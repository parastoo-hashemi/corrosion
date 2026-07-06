#!/usr/bin/env python3
"""Build a reproducible offline image-augmentation dataset.

This script only prepares images and provenance metadata. It does not train or
evaluate any classifier.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import logging
import os
import shutil
import sys
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from openpyxl import load_workbook
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE_DIR = PROJECT_ROOT / "Data" / "Images_dataset"
DEFAULT_WORKBOOK = PROJECT_ROOT / "Data" / "Images_Dataset_A-Z-1.xlsx"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "Data" / "Images_dataset_augmented"
DEFAULT_OUTPUT_CSV = PROJECT_ROOT / "Data" / "Images_Dataset_A-Z-1_augmented.csv"
DEFAULT_REPORT = PROJECT_ROOT / "Documentation" / "augmentation_dataset_report.md"
DEFAULT_CODEX_REPORT = (
    PROJECT_ROOT / "Documentation" / "codex" / "augmentation_dataset_report.md"
)
DEFAULT_CONTACT_SHEET = PROJECT_ROOT / "Documentation" / "augmentation_examples.png"

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}
RECIPE_NAMES = (
    "brightness_contrast",
    "saturation_colour_balance",
    "gaussian_blur_noise",
    "brightness_contrast_saturation",
    "horizontal_flip_brightness",
)


@dataclass(frozen=True)
class SourceRecord:
    excel_row: int
    values: dict[str, Any]
    source_path: Path
    original_image_name: str
    label: int
    specimen_id: str


@dataclass(frozen=True)
class AuditResult:
    valid_records: list[SourceRecord]
    missing_images: list[str]
    corrupted_images: list[tuple[str, str]]
    unmatched_files: list[str]
    readable_file_count: int
    source_file_count: int
    dimensions: Counter[tuple[int, int]]
    modes: Counter[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create an offline corrosion-classification dataset containing each "
            "readable original plus reproducible augmented copies."
        )
    )
    parser.add_argument("--image-dir", type=Path, default=DEFAULT_IMAGE_DIR)
    parser.add_argument("--workbook", type=Path, default=DEFAULT_WORKBOOK)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT_CSV)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--codex-report", type=Path, default=DEFAULT_CODEX_REPORT)
    parser.add_argument("--contact-sheet", type=Path, default=DEFAULT_CONTACT_SHEET)
    parser.add_argument(
        "--copies",
        type=int,
        default=4,
        help="Augmented copies per readable source image (default: 4; 5x total).",
    )
    parser.add_argument("--seed", type=int, default=20260630)
    parser.add_argument(
        "--workers",
        type=int,
        default=min(4, os.cpu_count() or 1),
        help="Parallel image workers (default: up to 4).",
    )
    parser.add_argument("--filename-column", default=None)
    parser.add_argument("--label-column", default=None)
    parser.add_argument("--specimen-column", default=None)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing generated outputs.",
    )
    return parser.parse_args()


def normalise_column_name(value: Any) -> str:
    text = str(value or "").strip().casefold()
    for character in (" ", "_", "-", "–", "—", "(", ")", "[", "]", "%", "/"):
        text = text.replace(character, "")
    return text


def select_column(
    headers: list[str],
    explicit: str | None,
    role: str,
    scorer: Any,
) -> str:
    if explicit:
        exact = [header for header in headers if header == explicit]
        normalised = [
            header
            for header in headers
            if normalise_column_name(header) == normalise_column_name(explicit)
        ]
        matches = exact or normalised
        if len(matches) != 1:
            raise ValueError(
                f"Could not uniquely resolve explicit {role} column {explicit!r}. "
                f"Available columns: {headers}"
            )
        return matches[0]

    scored = [(int(scorer(header)), header) for header in headers]
    best_score = max(score for score, _ in scored)
    best = [header for score, header in scored if score == best_score and score > 0]
    if len(best) != 1:
        candidates = [(header, score) for score, header in scored if score > 0]
        raise ValueError(
            f"Ambiguous {role} column. Candidates and scores: {candidates}. "
            f"Use --{role.replace(' ', '-')}-column to select one explicitly."
        )
    return best[0]


def filename_score(header: str) -> int:
    name = normalise_column_name(header)
    if name in {"samplename", "imagename", "imagefilename", "filename"}:
        return 100
    if "image" in name and ("name" in name or "file" in name):
        return 80
    if "sample" in name and "name" in name:
        return 70
    return 0


def label_score(header: str) -> int:
    name = normalise_column_name(header)
    if name in {
        "atotalrustcategory1–4",
        "atotalrustcategory14",
        "totalrustcategory",
        "totalrustcategory14",
    }:
        return 120
    if "totalrust" in name and "category" in name:
        return 110
    if "rust" in name and "category" in name and "peak" not in name:
        return 80
    if "peakrust" in name and "category" in name:
        return 30
    return 0


def specimen_score(header: str) -> int:
    name = normalise_column_name(header)
    if name in {"id", "specimenid", "sampleid"}:
        return 100
    if ("specimen" in name or "sample" in name) and "id" in name:
        return 80
    return 0


def read_workbook(
    workbook_path: Path,
    filename_column: str | None,
    label_column: str | None,
    specimen_column: str | None,
) -> tuple[list[str], list[dict[str, Any]], str, str, str, str]:
    if not workbook_path.is_file():
        raise FileNotFoundError(f"Workbook not found: {workbook_path}")

    workbook = load_workbook(workbook_path, read_only=True, data_only=True)
    worksheet = workbook.active
    raw_rows = list(worksheet.iter_rows(values_only=True))
    workbook.close()
    if len(raw_rows) < 3:
        raise ValueError("Workbook must contain group headers, column headers, and data.")

    header_row_index = None
    for index, row in enumerate(raw_rows[:10]):
        names = [str(value).strip() if value is not None else "" for value in row]
        if any(filename_score(name) for name in names) and any(
            label_score(name) for name in names
        ):
            header_row_index = index
            break
    if header_row_index is None:
        raise ValueError(
            "Could not identify the workbook header row from filename/label candidates."
        )

    headers = [
        str(value).strip() if value is not None else ""
        for value in raw_rows[header_row_index]
    ]
    if any(not header for header in headers):
        raise ValueError(f"Blank column header(s) found in workbook header row: {headers}")
    if len(set(headers)) != len(headers):
        duplicates = sorted(
            header for header, count in Counter(headers).items() if count > 1
        )
        raise ValueError(f"Duplicate workbook column headers: {duplicates}")

    selected_filename = select_column(
        headers, filename_column, "filename", filename_score
    )
    selected_label = select_column(headers, label_column, "label", label_score)
    selected_specimen = select_column(
        headers, specimen_column, "specimen", specimen_score
    )

    records: list[dict[str, Any]] = []
    for excel_row, row in enumerate(
        raw_rows[header_row_index + 1 :], start=header_row_index + 2
    ):
        if all(value is None or str(value).strip() == "" for value in row):
            continue
        padded = list(row) + [None] * (len(headers) - len(row))
        record = dict(zip(headers, padded[: len(headers)]))
        record["_excel_row"] = excel_row
        records.append(record)

    if not records:
        raise ValueError("No data records found below the workbook header.")
    return (
        headers,
        records,
        selected_filename,
        selected_label,
        selected_specimen,
        worksheet.title,
    )


def clean_source_name(value: Any) -> str:
    name = str(value or "").strip()
    if not name:
        raise ValueError("Encountered a blank image filename value.")
    if Path(name).name != name or name in {".", ".."}:
        raise ValueError(f"Unsafe image filename value: {name!r}")
    return name


def coerce_label(value: Any, excel_row: int, column: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"Invalid Boolean label at Excel row {excel_row}.")
    try:
        numeric = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Invalid label {value!r} at Excel row {excel_row}, column {column!r}."
        ) from error
    if not numeric.is_integer() or int(numeric) not in {1, 2, 3, 4}:
        raise ValueError(
            f"Label must be one of 1, 2, 3, 4; found {value!r} at Excel row "
            f"{excel_row}, column {column!r}."
        )
    return int(numeric)


def inspect_image(path: Path) -> tuple[tuple[int, int], str]:
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        image.load()
        return image.size, image.mode


def audit_sources(
    image_dir: Path,
    workbook_records: list[dict[str, Any]],
    filename_column: str,
    label_column: str,
    specimen_column: str,
) -> AuditResult:
    if not image_dir.is_dir():
        raise FileNotFoundError(f"Image directory not found: {image_dir}")

    all_files = sorted(path for path in image_dir.iterdir() if path.is_file())
    image_files = [
        path for path in all_files if path.suffix.casefold() in SUPPORTED_EXTENSIONS
    ]
    by_stem: dict[str, list[Path]] = defaultdict(list)
    for path in image_files:
        by_stem[path.stem.casefold()].append(path)

    dimensions: Counter[tuple[int, int]] = Counter()
    modes: Counter[str] = Counter()
    corrupted_images: list[tuple[str, str]] = []
    readable_paths: set[Path] = set()
    for index, path in enumerate(image_files, start=1):
        try:
            size, mode = inspect_image(path)
            dimensions[size] += 1
            modes[mode] += 1
            readable_paths.add(path)
        except Exception as error:  # Pillow exposes format-specific exception types.
            corrupted_images.append((path.name, f"{type(error).__name__}: {error}"))
        if index % 100 == 0 or index == len(image_files):
            logging.info("Source integrity audit: %d/%d files", index, len(image_files))

    valid_records: list[SourceRecord] = []
    missing_images: list[str] = []
    referenced_paths: set[Path] = set()
    for record in workbook_records:
        excel_row = int(record["_excel_row"])
        source_key = clean_source_name(record[filename_column])
        supplied_suffix = Path(source_key).suffix.casefold()
        if supplied_suffix in SUPPORTED_EXTENSIONS:
            candidates = [
                path
                for path in image_files
                if path.name.casefold() == source_key.casefold()
            ]
        else:
            candidates = by_stem.get(source_key.casefold(), [])

        if not candidates:
            missing_images.append(source_key)
            continue
        if len(candidates) > 1:
            raise ValueError(
                f"Multiple image files match workbook value {source_key!r}: "
                f"{[path.name for path in candidates]}"
            )
        source_path = candidates[0]
        referenced_paths.add(source_path)
        if source_path not in readable_paths:
            continue

        label = coerce_label(record[label_column], excel_row, label_column)
        specimen_id = str(record[specimen_column] or "").strip()
        if not specimen_id:
            raise ValueError(
                f"Blank specimen ID at Excel row {excel_row}, "
                f"column {specimen_column!r}."
            )
        valid_records.append(
            SourceRecord(
                excel_row=excel_row,
                values={key: value for key, value in record.items() if key != "_excel_row"},
                source_path=source_path,
                original_image_name=source_path.name,
                label=label,
                specimen_id=specimen_id,
            )
        )

    unmatched_files = sorted(
        path.name for path in image_files if path not in referenced_paths
    )
    return AuditResult(
        valid_records=valid_records,
        missing_images=sorted(missing_images),
        corrupted_images=sorted(corrupted_images),
        unmatched_files=unmatched_files,
        readable_file_count=len(readable_paths),
        source_file_count=len(image_files),
        dimensions=dimensions,
        modes=modes,
    )


def stable_rng(seed: int, image_name: str, augmentation_index: int) -> np.random.Generator:
    material = f"{seed}|{image_name}|{augmentation_index}".encode("utf-8")
    digest = hashlib.sha256(material).digest()
    derived_seed = int.from_bytes(digest[:8], byteorder="big", signed=False)
    return np.random.default_rng(derived_seed)


def adjust_colour_balance(
    image: Image.Image, rng: np.random.Generator
) -> tuple[Image.Image, dict[str, Any]]:
    array = np.asarray(image, dtype=np.float32)
    gains = rng.uniform(0.94, 1.06, size=3).astype(np.float32)
    gains /= float(np.mean(gains))
    balanced = np.clip(array * gains.reshape(1, 1, 3), 0, 255).astype(np.uint8)
    return Image.fromarray(balanced, mode="RGB"), {
        "rgb_gains": [round(float(value), 6) for value in gains]
    }


def add_gaussian_noise(
    image: Image.Image, sigma: float, rng: np.random.Generator
) -> Image.Image:
    array = np.asarray(image, dtype=np.float32) / 255.0
    noise = rng.normal(0.0, sigma, size=array.shape).astype(np.float32)
    noisy = np.clip(array + noise, 0.0, 1.0)
    return Image.fromarray(np.rint(noisy * 255.0).astype(np.uint8), mode="RGB")


def apply_recipe(
    source: Image.Image,
    recipe_name: str,
    rng: np.random.Generator,
) -> tuple[Image.Image, dict[str, Any]]:
    image = source.convert("RGB")
    parameters: dict[str, Any] = {}

    if recipe_name == "brightness_contrast":
        brightness = float(rng.uniform(0.75, 1.28))
        contrast = float(rng.uniform(0.78, 1.25))
        image = ImageEnhance.Brightness(image).enhance(brightness)
        image = ImageEnhance.Contrast(image).enhance(contrast)
        parameters.update(brightness=brightness, contrast=contrast)
    elif recipe_name == "saturation_colour_balance":
        saturation = float(rng.uniform(0.78, 1.28))
        image = ImageEnhance.Color(image).enhance(saturation)
        image, balance_parameters = adjust_colour_balance(image, rng)
        parameters.update(saturation=saturation, **balance_parameters)
    elif recipe_name == "gaussian_blur_noise":
        blur_sigma = float(rng.uniform(0.3, 1.5))
        noise_sigma = float(rng.uniform(0.005, 0.035))
        image = image.filter(ImageFilter.GaussianBlur(radius=blur_sigma))
        image = add_gaussian_noise(image, noise_sigma, rng)
        parameters.update(blur_sigma=blur_sigma, noise_sigma=noise_sigma)
    elif recipe_name == "brightness_contrast_saturation":
        brightness = float(rng.uniform(0.82, 1.18))
        contrast = float(rng.uniform(0.82, 1.18))
        saturation = float(rng.uniform(0.82, 1.18))
        image = ImageEnhance.Brightness(image).enhance(brightness)
        image = ImageEnhance.Contrast(image).enhance(contrast)
        image = ImageEnhance.Color(image).enhance(saturation)
        parameters.update(
            brightness=brightness,
            contrast=contrast,
            saturation=saturation,
        )
    elif recipe_name == "horizontal_flip_brightness":
        brightness = float(rng.uniform(0.85, 1.15))
        image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        image = ImageEnhance.Brightness(image).enhance(brightness)
        parameters.update(horizontal_flip=True, brightness=brightness)
    else:
        raise ValueError(f"Unknown augmentation recipe: {recipe_name}")

    rounded = {
        key: round(float(value), 6) if isinstance(value, float) else value
        for key, value in parameters.items()
    }
    return image, rounded


def process_source(
    record: SourceRecord,
    staging_dir: Path,
    copies: int,
    seed: int,
) -> list[dict[str, Any]]:
    original_destination = staging_dir / record.original_image_name
    shutil.copy2(record.source_path, original_destination)

    outputs: list[dict[str, Any]] = [
        {
            "augmented_image_name": record.original_image_name,
            "augmentation_id": "original",
            "augmentation_type": "original",
            "augmentation_parameters": "",
            "is_augmented": False,
        }
    ]

    with Image.open(record.source_path) as source:
        source.load()
        source_stem = Path(record.original_image_name).stem
        for copy_index in range(1, copies + 1):
            recipe_name = RECIPE_NAMES[(copy_index - 1) % len(RECIPE_NAMES)]
            rng = stable_rng(seed, record.original_image_name, copy_index)
            augmented, parameters = apply_recipe(source, recipe_name, rng)
            output_name = f"{source_stem}_aug{copy_index:02d}_{recipe_name}.png"
            output_path = staging_dir / output_name
            augmented.save(output_path, format="PNG", compress_level=6, optimize=False)
            outputs.append(
                {
                    "augmented_image_name": output_name,
                    "augmentation_id": f"aug{copy_index:02d}",
                    "augmentation_type": recipe_name,
                    "augmentation_parameters": serialise_parameters(parameters),
                    "is_augmented": True,
                }
            )
    return outputs


def serialise_parameters(parameters: dict[str, Any]) -> str:
    parts = []
    for key in sorted(parameters):
        value = parameters[key]
        if isinstance(value, list):
            text = "[" + ",".join(f"{float(item):.6f}" for item in value) + "]"
        elif isinstance(value, bool):
            text = "true" if value else "false"
        else:
            text = f"{float(value):.6f}"
        parts.append(f"{key}={text}")
    return ";".join(parts)


def path_for_metadata(path: Path) -> str:
    path = path.resolve()
    try:
        return path.relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def build_metadata_rows(
    records: list[SourceRecord],
    generated: dict[str, list[dict[str, Any]]],
    output_dir: Path,
    image_dir: Path,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in records:
        for output in generated[record.original_image_name]:
            metadata = {
                "original_image_name": record.original_image_name,
                "augmented_image_name": output["augmented_image_name"],
                "image_path": path_for_metadata(
                    output_dir / output["augmented_image_name"]
                ),
                "original_image_path": path_for_metadata(
                    image_dir / record.original_image_name
                ),
                "label": record.label,
                "augmentation_id": output["augmentation_id"],
                "augmentation_type": output["augmentation_type"],
                "augmentation_parameters": output["augmentation_parameters"],
                "is_augmented": output["is_augmented"],
                "specimen_id": record.specimen_id,
            }
            metadata.update(record.values)
            rows.append(metadata)
    return rows


def write_csv(
    output_csv: Path,
    rows: list[dict[str, Any]],
    original_headers: list[str],
    overwrite: bool,
) -> None:
    if output_csv.exists() and not overwrite:
        raise FileExistsError(
            f"Output CSV already exists: {output_csv}. Use --overwrite to replace it."
        )
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    provenance_headers = [
        "original_image_name",
        "augmented_image_name",
        "image_path",
        "original_image_path",
        "label",
        "augmentation_id",
        "augmentation_type",
        "augmentation_parameters",
        "is_augmented",
        "specimen_id",
    ]
    fieldnames = provenance_headers + [
        header for header in original_headers if header not in provenance_headers
    ]
    temporary = output_csv.with_suffix(output_csv.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output_csv)


def choose_contact_sheet_records(
    records: list[SourceRecord], seed: int
) -> list[SourceRecord]:
    by_class: dict[int, list[SourceRecord]] = defaultdict(list)
    for record in records:
        by_class[record.label].append(record)
    chosen: list[SourceRecord] = []
    for label in (1, 2, 3, 4):
        candidates = sorted(by_class[label], key=lambda item: item.original_image_name)
        rng = stable_rng(seed, f"contact-sheet-class-{label}", 0)
        chosen.append(candidates[int(rng.integers(0, len(candidates)))])
    return chosen


def create_contact_sheet(
    output_path: Path,
    output_dir: Path,
    records: list[SourceRecord],
    copies: int,
    seed: int,
    overwrite: bool,
) -> list[str]:
    if output_path.exists() and not overwrite:
        raise FileExistsError(
            f"Contact sheet already exists: {output_path}. Use --overwrite to replace it."
        )
    if copies == 0:
        columns = ["original"]
    else:
        columns = ["original"] + [
            f"aug{index:02d}" for index in range(1, min(copies, 5) + 1)
        ]

    chosen = choose_contact_sheet_records(records, seed)
    tile_width, tile_height = 560, 128
    left_margin, top_margin = 90, 52
    caption_height, gap = 34, 12
    canvas_width = left_margin + len(columns) * (tile_width + gap) + gap
    canvas_height = top_margin + len(chosen) * (tile_height + caption_height + gap) + gap
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()

    for column_index, column in enumerate(columns):
        x = left_margin + column_index * (tile_width + gap)
        draw.text((x + 4, 16), column, fill="black", font=font)

    selected_names: list[str] = []
    for row_index, record in enumerate(chosen):
        selected_names.append(record.original_image_name)
        y = top_margin + row_index * (tile_height + caption_height + gap)
        draw.text((12, y + tile_height // 2), f"class {record.label}", fill="black", font=font)
        stem = Path(record.original_image_name).stem
        names = [record.original_image_name]
        for copy_index in range(1, min(copies, 5) + 1):
            recipe = RECIPE_NAMES[(copy_index - 1) % len(RECIPE_NAMES)]
            names.append(f"{stem}_aug{copy_index:02d}_{recipe}.png")

        for column_index, name in enumerate(names):
            x = left_margin + column_index * (tile_width + gap)
            with Image.open(output_dir / name) as image:
                image = image.convert("RGB")
                image.thumbnail((tile_width, tile_height), Image.Resampling.LANCZOS)
                tile = Image.new("RGB", (tile_width, tile_height), "#eeeeee")
                tile.paste(
                    image,
                    ((tile_width - image.width) // 2, (tile_height - image.height) // 2),
                )
                canvas.paste(tile, (x, y))
            caption = name if len(name) <= 74 else name[:71] + "..."
            draw.text((x + 3, y + tile_height + 6), caption, fill="black", font=font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    canvas.save(temporary, format="PNG", compress_level=6)
    temporary.replace(output_path)
    return selected_names


def markdown_list(items: Iterable[str], empty_text: str = "None.") -> str:
    values = list(items)
    if not values:
        return empty_text
    return "\n".join(f"- `{value}`" for value in values)


def count_table(before: Counter[int], copies: int) -> str:
    lines = [
        "| Label | Original readable images | Augmented images | Total output images |",
        "|---:|---:|---:|---:|",
    ]
    for label in (1, 2, 3, 4):
        original = before[label]
        augmented = original * copies
        lines.append(f"| {label} | {original} | {augmented} | {original + augmented} |")
    return "\n".join(lines)


def create_report_text(
    *,
    args: argparse.Namespace,
    worksheet_name: str,
    filename_column: str,
    label_column: str,
    specimen_column: str,
    audit: AuditResult,
    metadata_rows: list[dict[str, Any]],
    contact_examples: list[str],
) -> str:
    before = Counter(record.label for record in audit.valid_records)
    original_count = len(audit.valid_records)
    augmented_count = original_count * args.copies
    output_count = len(metadata_rows)
    specimen_count = len({record.specimen_id for record in audit.valid_records})
    corrupted = [
        f"{name} — {reason}" for name, reason in audit.corrupted_images
    ]
    dimension_text = ", ".join(
        f"{width}x{height}: {count}"
        for (width, height), count in sorted(audit.dimensions.items())
    )
    mode_text = ", ".join(
        f"{mode}: {count}" for mode, count in sorted(audit.modes.items())
    )
    command = (
        "python augmentation/augment_dataset.py "
        f"--copies {args.copies} --seed {args.seed}"
    )
    if args.overwrite:
        command += " --overwrite"

    return f"""# Augmented Corrosion Image Dataset Report

## Completion status

**Completed successfully: Yes.**

The offline dataset was generated for four-class corrosion image classification only. No ResNet50, ViT, structural prediction, ultimate-load, wire-loss, or RUL model was trained or reproduced.

## Inputs and column mapping

- Source images: `{path_for_metadata(args.image_dir)}`
- Source workbook: `{path_for_metadata(args.workbook)}`
- Worksheet: `{worksheet_name}`
- Image filename column: `{filename_column}`; extension-free values were matched to image stems.
- Four-class label column: `{label_column}`; values were validated as integers in `{{1, 2, 3, 4}}`.
- Specimen/group column: `{specimen_column}`; preserved as `specimen_id` for leakage-safe downstream splitting.
- Workbook records inspected: {len(audit.valid_records) + len(audit.missing_images)}
- Distinct matched specimens: {specimen_count}

The workbook's `B_Peak_Rust_Category_(1–4)` column is preserved as original metadata but is not the classification target. The selected target is the surface-total rust category requested for this dataset.

## Source audit

- Files in the source image folder: {audit.source_file_count}
- Readable image files: {audit.readable_file_count}
- Workbook rows with readable matching images: {original_count}
- Workbook rows missing an image file: {len(audit.missing_images)}
- Corrupted/unreadable files: {len(audit.corrupted_images)}
- Image-folder files without a workbook row: {len(audit.unmatched_files)}
- Readable dimensions: {dimension_text}
- Readable colour modes: {mode_text}

### Missing image files

{markdown_list(audit.missing_images)}

### Corrupted/unreadable image files

{markdown_list(corrupted)}

### Image-folder files without a workbook row

{markdown_list(audit.unmatched_files)}

The known corrupted file `E01-20240508-17W.png` has no workbook row. It was recorded in the audit and excluded.

## Generated dataset

- Output image folder: `{path_for_metadata(args.output_dir)}`
- Output metadata: `{path_for_metadata(args.output_csv)}`
- Original images copied byte-for-byte: {original_count}
- Augmented images generated: {augmented_count}
- Total output images and metadata rows: {output_count}
- Expansion factor: {args.copies + 1}x (`1 original + {args.copies} augmented`)
- Random seed: `{args.seed}`

{count_table(before, args.copies)}

Every output row preserves all original workbook columns. Provenance fields include `original_image_name`, `augmented_image_name`, `image_path`, `original_image_path`, `label`, `augmentation_id`, `augmentation_type`, `augmentation_parameters`, `is_augmented`, and `specimen_id`.

## Augmentation recipes

The five augmentation recipes use label-preserving transforms. Parameter ranges are
calibrated to the measured inter-image luminance variation in the source dataset
(luminance range 98–255; 5th–95th percentile ratio 1.75x; real-world brightest-to-
darkest ratio 2.60x). The previous conservative [0.85, 1.15] range covered only 1.35x
of that variation and was widened accordingly.

1. `brightness_contrast`: brightness sampled from `[0.75, 1.28]`, contrast from `[0.78, 1.25]`. Calibrated to the real inter-image brightness distribution.
2. `saturation_colour_balance`: saturation from `[0.78, 1.28]`; normalized per-channel RGB gains from `[0.94, 1.06]`. Simulates camera white-balance and surface-wetness variation.
3. `gaussian_blur_noise`: Gaussian blur sigma from `[0.3, 1.5]` pixels; Gaussian noise sigma from `[0.005, 0.035]` in normalized `[0, 1]` RGB space. Simulates focus variation and sensor noise.
4. `brightness_contrast_saturation`: brightness, contrast, and saturation each independently sampled from `[0.82, 1.18]`. Represents compound photometric effects.
5. `horizontal_flip_brightness`: image mirrored left-to-right (label-safe for total-rust-category classification, which is position-invariant), combined with brightness from `[0.85, 1.15]`. First geometric augmentation; adds spatial diversity without altering rust-coverage class.

Excluded: MixUp, CutMix, GAN/diffusion synthesis, elastic deformation, random erasing,
vertical flip, large rotation (>10°), and heavy hue shifts (>0.1). These were excluded
because they corrupt label integrity, are physically implausible for this imaging setup,
or require infrastructure (generative models) outside the scope of this dataset.

## Quality and leakage controls

- Original source files and the workbook were opened read-only and were not modified.
- Output originals are byte-for-byte copies; augmented images are separate PNG files.
- Labels were copied exactly from `{label_column}` and validated before generation.
- `original_image_name` and `specimen_id` are present on every row.
- Future train/validation/test splitting must be performed by `specimen_id` before selecting augmented rows. All rows sharing an `original_image_name` must remain in the same split.
- The contact sheet is `{path_for_metadata(args.contact_sheet)}`. Its deterministic source examples are: {", ".join(f"`{name}`" for name in contact_examples)}.

## Reproduction

From the project root:

```bash
{command}
```

Use `--copies N` to change the number of augmented copies and `--seed N` to change the deterministic random stream. Existing generated outputs are protected unless `--overwrite` is supplied.
"""


def write_report(path: Path, text: str, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(
            f"Report already exists: {path}. Use --overwrite to replace it."
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def preflight_outputs(args: argparse.Namespace) -> None:
    outputs = [args.output_csv, args.report, args.codex_report, args.contact_sheet]
    existing = [path for path in outputs if path.exists()]
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        existing.append(args.output_dir)
    if existing and not args.overwrite:
        joined = "\n".join(f"- {path}" for path in existing)
        raise FileExistsError(
            "Generated output(s) already exist. Re-run with --overwrite to replace:\n"
            + joined
        )


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    if args.copies < 0:
        raise ValueError("--copies must be zero or greater.")
    if args.workers < 1:
        raise ValueError("--workers must be one or greater.")

    args.image_dir = args.image_dir.resolve()
    args.workbook = args.workbook.resolve()
    args.output_dir = args.output_dir.resolve()
    args.output_csv = args.output_csv.resolve()
    args.report = args.report.resolve()
    args.codex_report = args.codex_report.resolve()
    args.contact_sheet = args.contact_sheet.resolve()

    preflight_outputs(args)
    (
        headers,
        workbook_records,
        filename_column,
        label_column,
        specimen_column,
        worksheet_name,
    ) = read_workbook(
        args.workbook,
        args.filename_column,
        args.label_column,
        args.specimen_column,
    )
    logging.info("Selected filename column: %s", filename_column)
    logging.info("Selected label column: %s", label_column)
    logging.info("Selected specimen column: %s", specimen_column)
    logging.info("Workbook data rows: %d", len(workbook_records))

    audit = audit_sources(
        args.image_dir,
        workbook_records,
        filename_column,
        label_column,
        specimen_column,
    )
    if not audit.valid_records:
        raise ValueError("No readable workbook-linked images are available to augment.")
    observed_labels = {record.label for record in audit.valid_records}
    if observed_labels != {1, 2, 3, 4}:
        raise ValueError(
            f"Expected all four labels {{1,2,3,4}}, found {sorted(observed_labels)}."
        )
    logging.info(
        "Audit complete: %d valid, %d missing, %d corrupted, %d unmatched",
        len(audit.valid_records),
        len(audit.missing_images),
        len(audit.corrupted_images),
        len(audit.unmatched_files),
    )

    staging_dir = args.output_dir.with_name(args.output_dir.name + ".staging")
    if staging_dir.exists():
        if not args.overwrite:
            raise FileExistsError(
                f"Staging directory exists: {staging_dir}. Use --overwrite to replace it."
            )
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True)

    generated: dict[str, list[dict[str, Any]]] = {}
    try:
        logging.info(
            "Generating %d augmented images (%d copies x %d originals) with seed %d",
            len(audit.valid_records) * args.copies,
            args.copies,
            len(audit.valid_records),
            args.seed,
        )
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            future_to_record = {
                executor.submit(
                    process_source,
                    record,
                    staging_dir,
                    args.copies,
                    args.seed,
                ): record
                for record in audit.valid_records
            }
            for completed, future in enumerate(as_completed(future_to_record), start=1):
                record = future_to_record[future]
                generated[record.original_image_name] = future.result()
                if completed % 25 == 0 or completed == len(future_to_record):
                    logging.info(
                        "Image generation: %d/%d originals",
                        completed,
                        len(future_to_record),
                    )

        expected_files = len(audit.valid_records) * (args.copies + 1)
        actual_files = sum(1 for path in staging_dir.iterdir() if path.is_file())
        if actual_files != expected_files:
            raise RuntimeError(
                f"Output file-count check failed: expected {expected_files}, "
                f"found {actual_files}."
            )

        if args.output_dir.exists():
            shutil.rmtree(args.output_dir)
        staging_dir.replace(args.output_dir)

        metadata_rows = build_metadata_rows(
            audit.valid_records,
            generated,
            args.output_dir,
            args.image_dir,
        )
        if len(metadata_rows) != expected_files:
            raise RuntimeError(
                f"Metadata row-count check failed: expected {expected_files}, "
                f"found {len(metadata_rows)}."
            )
        write_csv(args.output_csv, metadata_rows, headers, args.overwrite)
        contact_examples = create_contact_sheet(
            args.contact_sheet,
            args.output_dir,
            audit.valid_records,
            args.copies,
            args.seed,
            args.overwrite,
        )
        report_text = create_report_text(
            args=args,
            worksheet_name=worksheet_name,
            filename_column=filename_column,
            label_column=label_column,
            specimen_column=specimen_column,
            audit=audit,
            metadata_rows=metadata_rows,
            contact_examples=contact_examples,
        )
        write_report(args.report, report_text, args.overwrite)
        write_report(args.codex_report, report_text, args.overwrite)
    except Exception:
        if staging_dir.exists():
            shutil.rmtree(staging_dir)
        raise

    logging.info("Completed successfully.")
    logging.info("Output image folder: %s", args.output_dir)
    logging.info("Output metadata CSV: %s", args.output_csv)
    logging.info("Reports: %s and %s", args.report, args.codex_report)
    logging.info("Contact sheet: %s", args.contact_sheet)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        logging.error("Interrupted by user.")
        raise SystemExit(130)
    except Exception as error:
        logging.error("%s: %s", type(error).__name__, error)
        raise SystemExit(1)

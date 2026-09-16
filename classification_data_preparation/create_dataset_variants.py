#!/usr/bin/env python3
"""Create controlled augmentation dataset variants without training models."""

from __future__ import annotations

import argparse
import csv
import hashlib
import logging
import math
import os
import shutil
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_CSV = PROJECT_ROOT / "Data" / "Images_Dataset_A-Z-1_augmented.csv"
DEFAULT_STATS_CSV = PROJECT_ROOT / "classification_data_preparation" / "tables" / "image_statistics_full.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "Data" / "augmentation_variants"
DEFAULT_REPORT = PROJECT_ROOT / "Documentation" / "codex" / "augmentation_variant_report.md"
DEFAULT_FIGURE_DIR = PROJECT_ROOT / "classification_data_preparation" / "figures" / "variants"

REQUIRED_COLUMNS = [
    "original_image_name",
    "augmented_image_name",
    "image_path",
    "original_image_path",
    "label",
    "specimen_id",
    "augmentation_id",
    "augmentation_type",
    "augmentation_parameters",
    "is_augmented",
    "A_Total_Rust_Category_(1–4)",
]

STATS_REQUIRED_COLUMNS = [
    "original_image_name",
    "mean_luminance_rec709_0_255",
]

VARIANT_COLUMNS = [
    "dataset_variant",
    "augmentation_strength",
    "sigma_type",
    "sigma_level",
    "selection_seed",
    "source_metadata_csv",
    "variant_generation_method",
]

SIZE_VARIANTS = {
    "size_plus50": 0.50,
    "size_plus100": 1.00,
    "size_plus150": 1.50,
}

BRIGHTNESS_VARIANTS = {
    "sigma2_brightness": 2,
    "sigma3_brightness": 3,
}

NOISE_VARIANTS = {
    "sigma2_noise": (2, 0.020),
    "sigma3_noise": (3, 0.035),
}

LABELS = (1, 2, 3, 4)
PNG_COMPRESS_LEVEL = 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create additional controlled corrosion augmentation variants in a "
            "separate output folder. This script prepares data only and does not "
            "train any model."
        )
    )
    parser.add_argument("--input-csv", type=Path, default=DEFAULT_INPUT_CSV)
    parser.add_argument("--stats-csv", type=Path, default=DEFAULT_STATS_CSV)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--seed", type=int, default=20260630)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace generated outputs under the augmentation variants folder.",
    )
    parser.add_argument(
        "--copy-images",
        action="store_true",
        help=(
            "Copy referenced images into size-variant folders. By default, size "
            "variants are manifest-only and reference Data/Images_dataset_augmented."
        ),
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=min(4, os.cpu_count() or 1),
        help="Parallel workers for sigma image generation and validation setup.",
    )
    return parser.parse_args()


def path_for_metadata(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def resolve_project_path(path_text: Any) -> Path:
    if pd.isna(path_text):
        raise ValueError("Encountered a blank path in metadata.")
    path = Path(str(path_text))
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def stable_hash_int(material: str) -> int:
    digest = hashlib.sha256(material.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


def stable_rng(seed: int, *parts: Any) -> np.random.Generator:
    material = "|".join([str(seed), *(str(part) for part in parts)])
    derived_seed = stable_hash_int(material)
    return np.random.default_rng(derived_seed)


def round_half_up(value: float) -> int:
    return int(value + 0.5)


def coerce_bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        raise ValueError("Blank is_augmented value found.")
    text = str(value).strip().casefold()
    if text in {"true", "1", "yes", "y"}:
        return True
    if text in {"false", "0", "no", "n"}:
        return False
    raise ValueError(f"Could not parse is_augmented value: {value!r}")


def coerce_bool_series(series: pd.Series) -> pd.Series:
    return series.map(coerce_bool_value).astype(bool)


def serialise_parameters(parameters: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in sorted(parameters):
        value = parameters[key]
        if isinstance(value, bool):
            text = "true" if value else "false"
        elif isinstance(value, int):
            text = str(value)
        elif isinstance(value, float):
            text = f"{value:.6f}"
        elif isinstance(value, (list, tuple)):
            text = "[" + ",".join(f"{float(item):.6f}" for item in value) + "]"
        else:
            text = str(value)
        parts.append(f"{key}={text}")
    return ";".join(parts)


def format_count_dict(values: dict[Any, int] | Counter[Any], keys: Iterable[Any]) -> str:
    return "{" + ", ".join(f"{key}: {int(values.get(key, 0))}" for key in keys) + "}"


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def validate_required_columns(df: pd.DataFrame, required: list[str], source: Path) -> None:
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"{source} is missing required column(s): {missing}")


def load_inputs(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, float, float]:
    if not args.input_csv.is_file():
        raise FileNotFoundError(f"Input metadata CSV not found: {args.input_csv}")
    if not args.stats_csv.is_file():
        raise FileNotFoundError(f"Image statistics CSV not found: {args.stats_csv}")

    metadata = pd.read_csv(args.input_csv)
    stats = pd.read_csv(args.stats_csv)
    validate_required_columns(metadata, REQUIRED_COLUMNS, args.input_csv)
    validate_required_columns(stats, STATS_REQUIRED_COLUMNS, args.stats_csv)

    metadata["is_augmented"] = coerce_bool_series(metadata["is_augmented"])
    metadata["label"] = pd.to_numeric(metadata["label"], errors="raise").astype(int)
    bad_labels = sorted(set(metadata["label"]) - set(LABELS))
    if bad_labels:
        raise ValueError(f"Labels must be only 1, 2, 3, 4; found {bad_labels}")

    if stats["original_image_name"].duplicated().any():
        duplicates = stats.loc[
            stats["original_image_name"].duplicated(), "original_image_name"
        ].tolist()
        raise ValueError(f"Duplicate statistics rows for original image(s): {duplicates}")
    stats["mean_luminance_rec709_0_255"] = pd.to_numeric(
        stats["mean_luminance_rec709_0_255"], errors="raise"
    )

    originals = metadata.loc[~metadata["is_augmented"]].copy()
    augmented = metadata.loc[metadata["is_augmented"]].copy()
    if originals.empty:
        raise ValueError("No original rows found where is_augmented == False.")
    if augmented.empty:
        raise ValueError("No augmented rows found where is_augmented == True.")
    if originals["original_image_name"].duplicated().any():
        raise ValueError("Original rows must be unique by original_image_name.")

    expected_original_names = set(originals["original_image_name"].astype(str))
    stats_original_names = set(stats["original_image_name"].astype(str))
    missing_stats = sorted(expected_original_names - stats_original_names)
    if missing_stats:
        raise ValueError(
            "Image statistics are missing original image(s): " + ", ".join(missing_stats[:10])
        )

    luminance_mean = float(stats["mean_luminance_rec709_0_255"].mean())
    luminance_std = float(stats["mean_luminance_rec709_0_255"].std(ddof=1))
    if not math.isfinite(luminance_std) or luminance_std <= 0:
        raise ValueError("Computed luminance standard deviation is not positive.")

    metadata["_source_order"] = range(len(metadata))
    originals = metadata.loc[~metadata["is_augmented"]].copy()
    augmented = metadata.loc[metadata["is_augmented"]].copy()
    return metadata, originals, augmented, luminance_mean, luminance_std


def allocate_proportional(
    weights: dict[Any, int],
    target: int,
    seed_material: str,
) -> dict[Any, int]:
    if target < 0:
        raise ValueError("Allocation target must be non-negative.")
    if not weights:
        if target == 0:
            return {}
        raise ValueError("Cannot allocate a positive target across no weights.")
    total_weight = sum(int(value) for value in weights.values())
    if total_weight <= 0:
        raise ValueError("Allocation weights must sum to a positive number.")

    exact = {
        key: (float(target) * float(weight) / float(total_weight))
        for key, weight in weights.items()
    }
    allocation = {key: int(math.floor(value)) for key, value in exact.items()}
    remainder = target - sum(allocation.values())
    order = sorted(
        weights,
        key=lambda key: (
            -(exact[key] - math.floor(exact[key])),
            stable_hash_int(f"{seed_material}|{key}"),
            str(key),
        ),
    )
    for key in order[:remainder]:
        allocation[key] += 1
    return allocation


def allocate_even_quota(
    keys: list[str],
    target: int,
    max_per_key: int,
    seed_material: str,
) -> dict[str, int]:
    if target > len(keys) * max_per_key:
        raise ValueError(
            f"Cannot allocate {target} selections across {len(keys)} keys with "
            f"capacity {max_per_key} each."
        )
    if not keys:
        if target == 0:
            return {}
        raise ValueError("Cannot allocate a positive target across no keys.")

    base = min(max_per_key, target // len(keys))
    allocation = {key: base for key in keys}
    remaining = target - base * len(keys)
    pass_index = 0
    while remaining > 0:
        candidates = [key for key in keys if allocation[key] < max_per_key]
        if not candidates:
            raise ValueError("Allocation capacity exhausted before target was reached.")
        candidates = sorted(
            candidates,
            key=lambda key: (
                stable_hash_int(f"{seed_material}|pass={pass_index}|{key}"),
                key,
            ),
        )
        for key in candidates:
            if remaining == 0:
                break
            allocation[key] += 1
            remaining -= 1
        pass_index += 1
    return allocation


def select_balanced_augmented_rows(
    originals: pd.DataFrame,
    augmented: pd.DataFrame,
    percentage: float,
    variant: str,
    seed: int,
) -> pd.DataFrame:
    target_augmented = round_half_up(len(originals) * percentage)
    label_weights = originals.groupby("label").size().astype(int).to_dict()
    label_targets = allocate_proportional(
        label_weights,
        target_augmented,
        f"{seed}|{variant}|label",
    )

    quotas: dict[str, int] = {}
    for label in LABELS:
        label_target = int(label_targets.get(label, 0))
        label_originals = originals.loc[originals["label"] == label]
        specimen_weights = (
            label_originals.groupby("specimen_id").size().astype(int).to_dict()
        )
        specimen_targets = allocate_proportional(
            specimen_weights,
            label_target,
            f"{seed}|{variant}|label={label}|specimen",
        )
        for specimen_id, specimen_target in specimen_targets.items():
            specimen_originals = label_originals.loc[
                label_originals["specimen_id"] == specimen_id
            ]
            original_names = sorted(
                specimen_originals["original_image_name"].astype(str).unique().tolist()
            )
            quotas.update(
                allocate_even_quota(
                    original_names,
                    int(specimen_target),
                    max_per_key=5,
                    seed_material=(
                        f"{seed}|{variant}|label={label}|"
                        f"specimen={specimen_id}|original"
                    ),
                )
            )

    if sum(quotas.values()) != target_augmented:
        raise RuntimeError(
            f"{variant}: quota total {sum(quotas.values())} does not match "
            f"target {target_augmented}."
        )

    rows_by_original_type: dict[str, dict[str, int]] = {}
    for index, row in augmented.iterrows():
        original_name = str(row["original_image_name"])
        augmentation_type = str(row["augmentation_type"])
        rows_by_original_type.setdefault(original_name, {})
        if augmentation_type in rows_by_original_type[original_name]:
            raise ValueError(
                f"Duplicate augmented row for {original_name} / {augmentation_type}."
            )
        rows_by_original_type[original_name][augmentation_type] = int(index)

    selected_indices: list[int] = []
    recipe_counts: Counter[str] = Counter()
    original_order = sorted(
        [name for name, quota in quotas.items() if quota > 0],
        key=lambda name: (
            stable_hash_int(f"{seed}|{variant}|selection-order|{name}"),
            name,
        ),
    )
    for original_name in original_order:
        available = rows_by_original_type.get(original_name, {})
        quota = quotas[original_name]
        if len(available) < quota:
            raise ValueError(
                f"{variant}: {original_name} has only {len(available)} augmented "
                f"rows but needs {quota}."
            )
        chosen_types: set[str] = set()
        for slot in range(quota):
            candidates = [
                recipe_name
                for recipe_name in available
                if recipe_name not in chosen_types
            ]
            candidates = sorted(
                candidates,
                key=lambda recipe_name: (
                    recipe_counts[recipe_name],
                    stable_hash_int(
                        f"{seed}|{variant}|{original_name}|slot={slot}|{recipe_name}"
                    ),
                    recipe_name,
                ),
            )
            chosen_recipe = candidates[0]
            chosen_types.add(chosen_recipe)
            recipe_counts[chosen_recipe] += 1
            selected_indices.append(available[chosen_recipe])

    if len(selected_indices) != target_augmented:
        raise RuntimeError(
            f"{variant}: selected {len(selected_indices)} rows, expected "
            f"{target_augmented}."
        )
    if len(set(selected_indices)) != len(selected_indices):
        raise RuntimeError(f"{variant}: duplicate augmented row selected.")

    return augmented.loc[selected_indices].sort_values("_source_order").copy()


def append_variant_columns(
    rows: pd.DataFrame,
    *,
    variant: str,
    augmentation_strength: str,
    sigma_type: str,
    sigma_level: str,
    seed: int,
    source_metadata_csv: Path,
    method: str,
) -> pd.DataFrame:
    output = rows.copy()
    output["dataset_variant"] = variant
    output["augmentation_strength"] = augmentation_strength
    output["sigma_type"] = sigma_type
    output["sigma_level"] = sigma_level
    output["selection_seed"] = seed
    output["source_metadata_csv"] = path_for_metadata(source_metadata_csv)
    output["variant_generation_method"] = method
    return output


def write_metadata(path: Path, rows: pd.DataFrame, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cleaned = rows.drop(columns=["_source_order"], errors="ignore").copy()
    cleaned = cleaned.reindex(columns=fieldnames)
    temporary = path.with_suffix(path.suffix + ".tmp")
    cleaned.to_csv(temporary, index=False)
    temporary.replace(path)


def copy_size_variant_images(rows: pd.DataFrame, variant_dir: Path) -> pd.DataFrame:
    output = rows.copy()
    image_dir = variant_dir / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    copied: dict[str, str] = {}
    for index, row in output.iterrows():
        source_path = resolve_project_path(row["image_path"])
        destination = image_dir / source_path.name
        if str(source_path) not in copied:
            shutil.copy2(source_path, destination)
            copied[str(source_path)] = path_for_metadata(destination)
        output.at[index, "image_path"] = copied[str(source_path)]
    return output


def adjust_brightness_by_luminance(
    image: Image.Image,
    source_luminance: float,
    luminance_std: float,
    sigma_level: int,
    direction: str,
) -> tuple[Image.Image, dict[str, Any]]:
    sign = -1.0 if direction == "minus" else 1.0
    requested_target = source_luminance + sign * sigma_level * luminance_std
    capped_target = min(255.0, max(0.0, requested_target))
    factor = capped_target / source_luminance if source_luminance > 0 else 1.0

    array = np.asarray(image.convert("RGB"), dtype=np.float32)
    scaled = array * factor
    high_clip_fraction = float(np.mean(scaled > 255.0))
    low_clip_fraction = float(np.mean(scaled < 0.0))
    adjusted = np.clip(scaled, 0.0, 255.0)
    output = Image.fromarray(np.rint(adjusted).astype(np.uint8), mode="RGB")
    parameters = {
        "brightness_factor": float(factor),
        "cap_lower_0_255": 0.0,
        "cap_upper_0_255": 255.0,
        "capped_target_luminance_0_255": float(capped_target),
        "direction": direction,
        "luminance_std_0_255": float(luminance_std),
        "requested_target_luminance_0_255": float(requested_target),
        "sigma_level": sigma_level,
        "source_mean_luminance_0_255": float(source_luminance),
        "pixel_fraction_clipped_high": high_clip_fraction,
        "pixel_fraction_clipped_low": low_clip_fraction,
    }
    return output, parameters


def add_gaussian_noise(
    image: Image.Image,
    noise_sigma: float,
    rng: np.random.Generator,
) -> tuple[Image.Image, dict[str, Any]]:
    array = np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0
    noisy = array + rng.normal(0.0, noise_sigma, size=array.shape).astype(np.float32)
    high_clip_fraction = float(np.mean(noisy > 1.0))
    low_clip_fraction = float(np.mean(noisy < 0.0))
    clipped = np.clip(noisy, 0.0, 1.0)
    output = Image.fromarray(np.rint(clipped * 255.0).astype(np.uint8), mode="RGB")
    parameters = {
        "existing_noise_range_normalized_rgb": "0.005-0.035",
        "noise_sigma_0_255": float(noise_sigma * 255.0),
        "noise_sigma_normalized_rgb": float(noise_sigma),
        "pixel_fraction_clipped_high": high_clip_fraction,
        "pixel_fraction_clipped_low": low_clip_fraction,
    }
    return output, parameters


def row_to_dict(row: pd.Series | dict[str, Any]) -> dict[str, Any]:
    if isinstance(row, pd.Series):
        return row.to_dict()
    return dict(row)


def generated_row_from_original(
    original_row: pd.Series | dict[str, Any],
    *,
    output_path: Path,
    output_name: str,
    augmentation_id: str,
    augmentation_type: str,
    augmentation_parameters: dict[str, Any],
    variant: str,
    augmentation_strength: str,
    sigma_type: str,
    sigma_level: int,
    seed: int,
    source_metadata_csv: Path,
    method: str,
) -> dict[str, Any]:
    row = row_to_dict(original_row)
    row["augmented_image_name"] = output_name
    row["image_path"] = path_for_metadata(output_path)
    row["augmentation_id"] = augmentation_id
    row["augmentation_type"] = augmentation_type
    row["augmentation_parameters"] = serialise_parameters(augmentation_parameters)
    row["is_augmented"] = True
    row["dataset_variant"] = variant
    row["augmentation_strength"] = augmentation_strength
    row["sigma_type"] = sigma_type
    row["sigma_level"] = sigma_level
    row["selection_seed"] = seed
    row["source_metadata_csv"] = path_for_metadata(source_metadata_csv)
    row["variant_generation_method"] = method
    return row


def generate_brightness_rows_for_original(
    original_row: dict[str, Any],
    *,
    images_dir: Path,
    variant: str,
    sigma_level: int,
    source_luminance: float,
    luminance_std: float,
    seed: int,
    input_csv: Path,
) -> list[dict[str, Any]]:
    original_name = str(original_row["original_image_name"])
    source_path = resolve_project_path(original_row["original_image_path"])
    stem = Path(original_name).stem
    generated_rows: list[dict[str, Any]] = []
    with Image.open(source_path) as image:
        image.load()
        for direction in ("minus", "plus"):
            output_name = f"{stem}_sigma{sigma_level}_brightness_{direction}.png"
            output_path = images_dir / output_name
            adjusted, parameters = adjust_brightness_by_luminance(
                image,
                source_luminance,
                luminance_std,
                sigma_level,
                direction,
            )
            adjusted.save(
                output_path,
                format="PNG",
                compress_level=PNG_COMPRESS_LEVEL,
                optimize=False,
            )
            generated_rows.append(
                generated_row_from_original(
                    original_row,
                    output_path=output_path,
                    output_name=output_name,
                    augmentation_id=f"sigma{sigma_level}_brightness_{direction}",
                    augmentation_type=f"brightness_{direction}_{sigma_level}sigma",
                    augmentation_parameters=parameters,
                    variant=variant,
                    augmentation_strength=f"brightness_{direction}_{sigma_level}sigma",
                    sigma_type="brightness",
                    sigma_level=sigma_level,
                    seed=seed,
                    source_metadata_csv=input_csv,
                    method="generated_from_original_luminance_capped_scaling",
                )
            )
    return generated_rows


def generate_noise_row_for_original(
    original_row: dict[str, Any],
    *,
    images_dir: Path,
    variant: str,
    sigma_level: int,
    noise_sigma: float,
    seed: int,
    input_csv: Path,
) -> dict[str, Any]:
    original_name = str(original_row["original_image_name"])
    source_path = resolve_project_path(original_row["original_image_path"])
    stem = Path(original_name).stem
    rng = stable_rng(seed, variant, original_name)
    output_name = f"{stem}_sigma{sigma_level}_noise.png"
    output_path = images_dir / output_name
    with Image.open(source_path) as image:
        image.load()
        noisy, parameters = add_gaussian_noise(image, noise_sigma, rng)
        parameters["sigma_level"] = sigma_level
        noisy.save(
            output_path,
            format="PNG",
            compress_level=PNG_COMPRESS_LEVEL,
            optimize=False,
        )
    return generated_row_from_original(
        original_row,
        output_path=output_path,
        output_name=output_name,
        augmentation_id=f"sigma{sigma_level}_noise",
        augmentation_type=f"gaussian_noise_{sigma_level}sigma",
        augmentation_parameters=parameters,
        variant=variant,
        augmentation_strength=f"noise_{sigma_level}sigma",
        sigma_type="noise",
        sigma_level=sigma_level,
        seed=seed,
        source_metadata_csv=input_csv,
        method="generated_gaussian_noise_existing_range",
    )


def create_size_variant(
    *,
    variant: str,
    percentage: float,
    originals: pd.DataFrame,
    augmented: pd.DataFrame,
    output_dir: Path,
    input_csv: Path,
    seed: int,
    copy_images: bool,
    fieldnames: list[str],
) -> pd.DataFrame:
    variant_dir = output_dir / variant
    variant_dir.mkdir(parents=True, exist_ok=True)
    selected_augmented = select_balanced_augmented_rows(
        originals,
        augmented,
        percentage,
        variant,
        seed,
    )
    rows = pd.concat(
        [
            originals.sort_values("_source_order"),
            selected_augmented.sort_values("_source_order"),
        ],
        ignore_index=True,
    )
    method = (
        "copied_existing_augmented_dataset"
        if copy_images
        else "manifest_only_existing_augmented_dataset"
    )
    rows = append_variant_columns(
        rows,
        variant=variant,
        augmentation_strength=f"+{round_half_up(percentage * 100)}%",
        sigma_type="",
        sigma_level="",
        seed=seed,
        source_metadata_csv=input_csv,
        method=method,
    )
    if copy_images:
        rows = copy_size_variant_images(rows, variant_dir)
    write_metadata(variant_dir / "metadata.csv", rows, fieldnames)
    return rows.drop(columns=["_source_order"], errors="ignore")


def create_brightness_variant(
    *,
    variant: str,
    sigma_level: int,
    originals: pd.DataFrame,
    stats: pd.DataFrame,
    output_dir: Path,
    input_csv: Path,
    seed: int,
    luminance_std: float,
    workers: int,
    fieldnames: list[str],
) -> pd.DataFrame:
    variant_dir = output_dir / variant
    images_dir = variant_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    stats_by_name = stats.set_index("original_image_name")

    generated_rows: list[dict[str, Any]] = []
    sorted_originals = originals.sort_values("_source_order")
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {}
        for _, original_row in sorted_originals.iterrows():
            original_name = str(original_row["original_image_name"])
            source_luminance = float(
                stats_by_name.loc[original_name, "mean_luminance_rec709_0_255"]
            )
            future = executor.submit(
                generate_brightness_rows_for_original,
                original_row.to_dict(),
                images_dir=images_dir,
                variant=variant,
                sigma_level=sigma_level,
                source_luminance=source_luminance,
                luminance_std=luminance_std,
                seed=seed,
                input_csv=input_csv,
            )
            futures[future] = original_name

        for completed, future in enumerate(as_completed(futures), start=1):
            generated_rows.extend(future.result())
            if completed % 50 == 0 or completed == len(futures):
                logging.info(
                    "%s image generation: %d/%d originals",
                    variant,
                    completed,
                    len(futures),
                )

    generated_part = pd.DataFrame(generated_rows).sort_values(
        ["_source_order", "augmented_image_name"]
    )

    original_part = append_variant_columns(
        originals.sort_values("_source_order"),
        variant=variant,
        augmentation_strength="original",
        sigma_type="",
        sigma_level="",
        seed=seed,
        source_metadata_csv=input_csv,
        method="original_row_from_existing_augmented_metadata",
    )
    rows = pd.concat([original_part, generated_part], ignore_index=True)
    write_metadata(variant_dir / "metadata.csv", rows, fieldnames)
    return rows.drop(columns=["_source_order"], errors="ignore")


def create_noise_variant(
    *,
    variant: str,
    sigma_level: int,
    noise_sigma: float,
    originals: pd.DataFrame,
    output_dir: Path,
    input_csv: Path,
    seed: int,
    workers: int,
    fieldnames: list[str],
) -> pd.DataFrame:
    variant_dir = output_dir / variant
    images_dir = variant_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    generated_rows: list[dict[str, Any]] = []
    sorted_originals = originals.sort_values("_source_order")
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(
                generate_noise_row_for_original,
                original_row.to_dict(),
                images_dir=images_dir,
                variant=variant,
                sigma_level=sigma_level,
                noise_sigma=noise_sigma,
                seed=seed,
                input_csv=input_csv,
            ): str(original_row["original_image_name"])
            for _, original_row in sorted_originals.iterrows()
        }
        for completed, future in enumerate(as_completed(futures), start=1):
            generated_rows.append(future.result())
            if completed % 50 == 0 or completed == len(futures):
                logging.info(
                    "%s image generation: %d/%d originals",
                    variant,
                    completed,
                    len(futures),
                )

    generated_part = pd.DataFrame(generated_rows).sort_values(
        ["_source_order", "augmented_image_name"]
    )

    original_part = append_variant_columns(
        originals.sort_values("_source_order"),
        variant=variant,
        augmentation_strength="original",
        sigma_type="",
        sigma_level="",
        seed=seed,
        source_metadata_csv=input_csv,
        method="original_row_from_existing_augmented_metadata",
    )
    rows = pd.concat([original_part, generated_part], ignore_index=True)
    write_metadata(variant_dir / "metadata.csv", rows, fieldnames)
    return rows.drop(columns=["_source_order"], errors="ignore")


def verify_image_readable(path: Path) -> None:
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        image.load()


def validate_variant(
    *,
    variant: str,
    rows: pd.DataFrame,
    originals: pd.DataFrame,
    expected_total_rows: int,
    expected_augmented_rows: int,
    output_dir: Path,
    manifest_only_size_variant: bool,
    sigma_variant: bool,
    verified_paths: set[Path],
) -> dict[str, Any]:
    is_augmented = coerce_bool_series(rows["is_augmented"])
    if len(rows) != expected_total_rows:
        raise RuntimeError(
            f"{variant}: expected {expected_total_rows} rows, found {len(rows)}."
        )
    if int(is_augmented.sum()) != expected_augmented_rows:
        raise RuntimeError(
            f"{variant}: expected {expected_augmented_rows} augmented rows, "
            f"found {int(is_augmented.sum())}."
        )

    labels = pd.to_numeric(rows["label"], errors="raise").astype(int)
    bad_labels = sorted(set(labels) - set(LABELS))
    if bad_labels:
        raise RuntimeError(f"{variant}: invalid labels found: {bad_labels}")
    if rows["original_image_name"].isna().any():
        raise RuntimeError(f"{variant}: original_image_name contains blank values.")
    if rows["specimen_id"].isna().any():
        raise RuntimeError(f"{variant}: specimen_id contains blank values.")

    original_names = set(originals["original_image_name"].astype(str))
    original_rows = rows.loc[~is_augmented]
    if len(original_rows) != len(originals):
        raise RuntimeError(
            f"{variant}: expected {len(originals)} original rows, found "
            f"{len(original_rows)}."
        )
    if set(original_rows["original_image_name"].astype(str)) != original_names:
        raise RuntimeError(f"{variant}: original image set is not preserved.")

    original_label_map = (
        originals.set_index("original_image_name")["label"].astype(int).to_dict()
    )
    original_specimen_map = (
        originals.set_index("original_image_name")["specimen_id"].astype(str).to_dict()
    )
    for _, row in rows.iterrows():
        original_name = str(row["original_image_name"])
        if original_name not in original_label_map:
            raise RuntimeError(
                f"{variant}: row references unknown original image {original_name}."
            )
        if int(row["label"]) != int(original_label_map[original_name]):
            raise RuntimeError(
                f"{variant}: label changed for generated row from {original_name}."
            )
        if str(row["specimen_id"]) != str(original_specimen_map[original_name]):
            raise RuntimeError(
                f"{variant}: specimen_id changed for row from {original_name}."
            )

    image_paths = rows["image_path"].astype(str).tolist()
    if manifest_only_size_variant:
        invalid_paths = [
            value
            for value in image_paths
            if not value.startswith("Data/Images_dataset_augmented/")
        ]
        if invalid_paths:
            raise RuntimeError(
                f"{variant}: manifest-only size variant has image paths outside "
                "Data/Images_dataset_augmented."
            )
    if sigma_variant:
        generated_rows = rows.loc[is_augmented]
        required_prefix = f"{path_for_metadata(output_dir / variant / 'images')}/"
        invalid_paths = [
            value
            for value in generated_rows["image_path"].astype(str)
            if not value.startswith(required_prefix)
        ]
        if invalid_paths:
            raise RuntimeError(
                f"{variant}: sigma-generated rows are not inside {required_prefix}."
            )

    for image_path_text in image_paths:
        path = resolve_project_path(image_path_text).resolve()
        if not path.is_file():
            raise RuntimeError(f"{variant}: image path does not exist: {path}")
        if path not in verified_paths:
            verify_image_readable(path)
            verified_paths.add(path)

    before_class_counts = (
        originals["label"].value_counts().reindex(LABELS, fill_value=0).astype(int).to_dict()
    )
    after_class_counts = labels.value_counts().reindex(LABELS, fill_value=0).astype(int).to_dict()
    specimen_counts = (
        rows["specimen_id"].astype(str).value_counts().sort_index().astype(int).to_dict()
    )
    original_augmented_counts = {
        "original": int((~is_augmented).sum()),
        "augmented": int(is_augmented.sum()),
    }

    print(f"\n[{variant}]")
    print(
        "class counts before augmentation: "
        + format_count_dict(before_class_counts, LABELS)
    )
    print(
        "class counts after augmentation: "
        + format_count_dict(after_class_counts, LABELS)
    )
    print(f"original vs augmented counts: {original_augmented_counts}")
    print(f"specimen counts: {specimen_counts}")

    return {
        "dataset_variant": variant,
        "total_rows": int(len(rows)),
        "original_rows": original_augmented_counts["original"],
        "augmented_rows": original_augmented_counts["augmented"],
        "class_counts": after_class_counts,
        "specimen_counts": specimen_counts,
        "metadata_path": path_for_metadata(output_dir / variant / "metadata.csv"),
        "readme_path": path_for_metadata(output_dir / variant / "README.md"),
    }


def create_contact_sheet(
    *,
    variant: str,
    rows: pd.DataFrame,
    originals: pd.DataFrame,
    figure_dir: Path,
    seed: int,
) -> str:
    figure_dir.mkdir(parents=True, exist_ok=True)
    selected_originals: list[str] = []
    for label in LABELS:
        candidates = (
            originals.loc[originals["label"] == label, "original_image_name"]
            .astype(str)
            .sort_values()
            .tolist()
        )
        if not candidates:
            continue
        ordered = sorted(
            candidates,
            key=lambda name: (
                stable_hash_int(f"{seed}|{variant}|contact-sheet|label={label}|{name}"),
                name,
            ),
        )
        selected_originals.append(ordered[0])

    tile_width, tile_height = 560, 128
    left_margin, top_margin = 96, 52
    caption_height, gap = 34, 12
    max_columns = 3 if "brightness" in variant else 2
    canvas_width = left_margin + max_columns * (tile_width + gap) + gap
    canvas_height = (
        top_margin
        + len(selected_originals) * (tile_height + caption_height + gap)
        + gap
    )
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    headers = ["original", "minus", "plus"] if "brightness" in variant else ["original", "noise"]
    for column_index, header in enumerate(headers):
        x = left_margin + column_index * (tile_width + gap)
        draw.text((x + 4, 16), header, fill="black", font=font)

    is_augmented = coerce_bool_series(rows["is_augmented"])
    for row_index, original_name in enumerate(selected_originals):
        row_y = top_margin + row_index * (tile_height + caption_height + gap)
        source_rows = rows.loc[rows["original_image_name"].astype(str) == original_name]
        label = int(source_rows.iloc[0]["label"])
        draw.text((12, row_y + tile_height // 2), f"class {label}", fill="black", font=font)
        original_meta = source_rows.loc[~coerce_bool_series(source_rows["is_augmented"])].iloc[0]
        image_items: list[tuple[str, str]] = [
            ("original", str(original_meta["image_path"])),
        ]
        augmented_rows = source_rows.loc[coerce_bool_series(source_rows["is_augmented"])]
        if "brightness" in variant:
            for direction in ("minus", "plus"):
                match = augmented_rows.loc[
                    augmented_rows["augmentation_type"].astype(str).str.contains(direction)
                ].iloc[0]
                image_items.append((direction, str(match["image_path"])))
        else:
            image_items.append(("noise", str(augmented_rows.iloc[0]["image_path"])))

        for column_index, (caption, image_path_text) in enumerate(image_items):
            x = left_margin + column_index * (tile_width + gap)
            with Image.open(resolve_project_path(image_path_text)) as image:
                image = image.convert("RGB")
                image.thumbnail((tile_width, tile_height), Image.Resampling.LANCZOS)
                tile = Image.new("RGB", (tile_width, tile_height), "#eeeeee")
                tile.paste(
                    image,
                    ((tile_width - image.width) // 2, (tile_height - image.height) // 2),
                )
                canvas.paste(tile, (x, row_y))
            caption_text = f"{caption}: {Path(image_path_text).name}"
            if len(caption_text) > 74:
                caption_text = caption_text[:71] + "..."
            draw.text((x + 3, row_y + tile_height + 6), caption_text, fill="black", font=font)

    output_path = figure_dir / f"{variant}_contact_sheet.png"
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    canvas.save(temporary, format="PNG", compress_level=6)
    temporary.replace(output_path)
    return path_for_metadata(output_path)


def write_variant_readme(
    *,
    variant: str,
    rows: pd.DataFrame,
    variant_dir: Path,
    summary: dict[str, Any],
    parameter_text: str,
    image_text: str,
    command: str,
) -> None:
    is_augmented = coerce_bool_series(rows["is_augmented"])
    class_counts = (
        rows["label"].astype(int).value_counts().reindex(LABELS, fill_value=0).astype(int).to_dict()
    )
    text = f"""# {variant}

This is one controlled augmentation variant for later corrosion-severity model comparisons. It is an additional dataset variant and does not replace the previously delivered augmented dataset.

- Metadata: `metadata.csv`
- Total rows: {len(rows)}
- Original rows: {int((~is_augmented).sum())}
- Augmented rows: {int(is_augmented.sum())}
- Class distribution: {format_count_dict(class_counts, LABELS)}
- Image handling: {image_text}
- Parameters: {parameter_text}
- Intended use: train/evaluate later models against this single controlled condition while preserving `specimen_id` and `original_image_name` for leakage-safe splitting.

Reproducibility command from the project root:

```bash
{command}
```
"""
    readme_path = variant_dir / "README.md"
    temporary = readme_path.with_suffix(readme_path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(readme_path)
    summary["readme_path"] = path_for_metadata(readme_path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_checksums(output_dir: Path) -> str:
    checksum_path = output_dir / "checksums_sha256.csv"
    rows: list[dict[str, str]] = []
    for path in sorted(output_dir.rglob("*")):
        if not path.is_file() or path == checksum_path:
            continue
        relative = path.relative_to(output_dir)
        dataset_variant = relative.parts[0] if relative.parts else ""
        rows.append(
            {
                "dataset_variant": dataset_variant,
                "file_path": path_for_metadata(path),
                "sha256": sha256_file(path),
            }
        )
    temporary = checksum_path.with_suffix(checksum_path.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["dataset_variant", "file_path", "sha256"],
        )
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(checksum_path)
    return path_for_metadata(checksum_path)


def create_report(
    *,
    summaries: list[dict[str, Any]],
    output_dir: Path,
    input_csv: Path,
    stats_csv: Path,
    report_path: Path,
    seed: int,
    copy_images: bool,
    original_count: int,
    luminance_mean: float,
    luminance_std: float,
    contact_sheets: dict[str, str],
    checksum_path: str,
) -> None:
    command = (
        "python classification_data_preparation/create_dataset_variants.py "
        f"--overwrite --seed {seed}"
    )
    if copy_images:
        command += " --copy-images"

    summary_rows = [
        [
            summary["dataset_variant"],
            summary["total_rows"],
            summary["original_rows"],
            summary["augmented_rows"],
            summary["metadata_path"],
        ]
        for summary in summaries
    ]
    class_rows = [
        [
            summary["dataset_variant"],
            summary["class_counts"].get(1, 0),
            summary["class_counts"].get(2, 0),
            summary["class_counts"].get(3, 0),
            summary["class_counts"].get(4, 0),
        ]
        for summary in summaries
    ]
    specimens = sorted(
        {
            specimen
            for summary in summaries
            for specimen in summary["specimen_counts"].keys()
        }
    )
    specimen_rows = [
        [
            specimen,
            *[
                summary["specimen_counts"].get(specimen, 0)
                for summary in summaries
            ],
        ]
        for specimen in specimens
    ]

    zip_commands = "\n".join(
        f"zip -r {summary['dataset_variant']}.zip {summary['dataset_variant']}"
        for summary in summaries
    )
    contact_sheet_lines = "\n".join(
        f"- `{variant}`: `{path}`" for variant, path in sorted(contact_sheets.items())
    )

    report = f"""# Controlled Augmentation Variant Report

## Scope

This is an additional augmentation package beyond the previously delivered augmented dataset. It does not replace or modify `Data/Images_dataset_augmented` or `Data/Images_Dataset_A-Z-1_augmented.csv`.

No model training was performed. No ResNet, ViT, Transformer, EfficientNet, hyperparameter tuning, or train/validation/test split generation was run.

## Inputs and protected files

- Source augmented metadata: `{path_for_metadata(input_csv)}`
- Source image statistics: `{path_for_metadata(stats_csv)}`
- Output parent folder: `{path_for_metadata(output_dir)}`
- Checksum manifest: `{checksum_path}`
- Selection seed: `{seed}`

The original images, original Excel workbook, existing delivered augmented dataset, existing split manifests, model code, and `classification_data_preparation/augment_dataset.py` were intentionally excluded from modification.

## Variants created

{markdown_table(["Variant", "Total rows", "Original rows", "Augmented rows", "Metadata"], summary_rows)}

## Class distribution per variant

{markdown_table(["Variant", "Label 1", "Label 2", "Label 3", "Label 4"], class_rows)}

## Specimen distribution per variant

The table shows total rows per specimen, including original and augmented rows.

{markdown_table(["Specimen", *[summary["dataset_variant"] for summary in summaries]], specimen_rows)}

## Dataset-size variants

The size variants are controlled selections from the existing delivered augmented CSV. Let `original_count` be the number of original rows where `is_augmented == False`. Here, `original_count = {original_count}`.

The augmented target is computed as `int(original_count * percentage + 0.5)`:

- `size_plus50`: `int(791 * 0.50 + 0.5) = 396` augmented rows, for `1187` total rows.
- `size_plus100`: `int(791 * 1.00 + 0.5) = 791` augmented rows, for `1582` total rows.
- `size_plus150`: `int(791 * 1.50 + 0.5) = 1187` augmented rows, for `1978` total rows.

By default these are manifest-only datasets. Their metadata points to existing files in `Data/Images_dataset_augmented`; images are not duplicated. The script supports `--copy-images` for size variants, but it was not used for this run.

Selection is deterministic and balanced as much as possible by `label`, `specimen_id`, `original_image_name`, and `augmentation_type`.

## Brightness sigma variants

Brightness sigma is based on measured source-image luminance from `mean_luminance_rec709_0_255` in `classification_data_preparation/tables/image_statistics_full.csv`.

- Global mean source luminance: `{luminance_mean:.6f}` on the 0-255 scale.
- Global source-luminance standard deviation: `{luminance_std:.6f}` on the 0-255 scale.
- `sigma2_brightness`: target luminance shift is `2 * {luminance_std:.6f} = {2 * luminance_std:.6f}`.
- `sigma3_brightness`: target luminance shift is `3 * {luminance_std:.6f} = {3 * luminance_std:.6f}`.

For each original image, the script creates both a darker and brighter variant:

`target_luminance = source_mean_luminance +/- sigma_level * luminance_std`

Targets are capped to `[0, 255]` before computing the brightness factor, and final RGB pixel values are clipped to `[0, 255]`. This avoids invalid values above 255 while making the cap explicit in `augmentation_parameters`.

## Noise sigma variants

The existing augmentation script uses Gaussian noise in normalized `[0, 1]` RGB space with `noise_sigma` sampled from `[0.005, 0.035]`.

The new controlled noise variants use fixed safe levels inside that existing envelope:

- `sigma2_noise`: `noise_sigma = 0.020` in normalized RGB space, equivalent to `5.100` on the 0-255 scale.
- `sigma3_noise`: `noise_sigma = 0.035` in normalized RGB space, equivalent to `8.925` on the 0-255 scale.

These values intentionally avoid literal `2` or `3` in normalized RGB space, which would destroy image content.

## Label preservation and leakage controls

All variants preserve the original `label`, `specimen_id`, `original_image_name`, and `is_augmented` fields. Brightness scaling and Gaussian sensor-noise stress tests do not alter the physical specimen identity or total-rust-category label, so the transformations are label-preserving for corrosion-severity classification.

No train/validation/test splits were created or modified. The metadata keeps `specimen_id` and `original_image_name` so later model-training work can perform specimen-level leakage-safe splitting.

The variants are separated into one folder per condition so model-performance changes can be attributed to one augmentation condition at a time rather than to a mixed uncontrolled dataset.

## Exclusions

Model training, model selection, hyperparameter tuning, ResNet, ViT, Transformer, EfficientNet, split-manifest updates, edits to original images, edits to the original Excel workbook, edits to the existing delivered augmented dataset, and edits to `classification_data_preparation/augment_dataset.py` were excluded because this task is limited to data augmentation and dataset preparation.

## Visual contact sheets

{contact_sheet_lines}

## Reproducibility

From the project root:

```bash
{command}
```

## Zip/share commands

Run these from `Data/augmentation_variants` if ZIP files are needed later:

```bash
{zip_commands}
```
"""

    report_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = report_path.with_suffix(report_path.suffix + ".tmp")
    temporary.write_text(report, encoding="utf-8")
    temporary.replace(report_path)


def preflight_outputs(args: argparse.Namespace) -> None:
    if args.output_dir.exists():
        if not args.overwrite:
            raise FileExistsError(
                f"Output directory already exists: {args.output_dir}. "
                "Use --overwrite to replace generated variant outputs."
            )
        shutil.rmtree(args.output_dir)
    if args.report.exists() and not args.overwrite:
        raise FileExistsError(
            f"Report already exists: {args.report}. Use --overwrite to replace it."
        )


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    args.input_csv = args.input_csv.resolve()
    args.stats_csv = args.stats_csv.resolve()
    args.output_dir = args.output_dir.resolve()
    args.report = args.report.resolve()
    if args.workers < 1:
        raise ValueError("--workers must be one or greater.")

    preflight_outputs(args)
    metadata, originals, augmented, luminance_mean, luminance_std = load_inputs(args)
    stats = pd.read_csv(args.stats_csv)
    stats["mean_luminance_rec709_0_255"] = pd.to_numeric(
        stats["mean_luminance_rec709_0_255"], errors="raise"
    )

    fieldnames = list(metadata.drop(columns=["_source_order"]).columns) + [
        column
        for column in VARIANT_COLUMNS
        if column not in metadata.columns
    ]

    original_count = len(originals)
    logging.info("Input metadata rows: %d", len(metadata))
    logging.info("Original rows: %d", original_count)
    logging.info("Existing augmented rows: %d", len(augmented))
    logging.info("Luminance mean/std: %.6f / %.6f", luminance_mean, luminance_std)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summaries: list[dict[str, Any]] = []
    contact_sheets: dict[str, str] = {}
    verified_paths: set[Path] = set()
    command = (
        "python classification_data_preparation/create_dataset_variants.py "
        f"--overwrite --seed {args.seed}"
    )
    if args.copy_images:
        command += " --copy-images"

    for variant, percentage in SIZE_VARIANTS.items():
        logging.info("Creating %s", variant)
        rows = create_size_variant(
            variant=variant,
            percentage=percentage,
            originals=originals,
            augmented=augmented,
            output_dir=args.output_dir,
            input_csv=args.input_csv,
            seed=args.seed,
            copy_images=args.copy_images,
            fieldnames=fieldnames,
        )
        expected_augmented = round_half_up(original_count * percentage)
        summary = validate_variant(
            variant=variant,
            rows=rows,
            originals=originals,
            expected_total_rows=original_count + expected_augmented,
            expected_augmented_rows=expected_augmented,
            output_dir=args.output_dir,
            manifest_only_size_variant=not args.copy_images,
            sigma_variant=False,
            verified_paths=verified_paths,
        )
        write_variant_readme(
            variant=variant,
            rows=rows,
            variant_dir=args.output_dir / variant,
            summary=summary,
            parameter_text=f"{percentage:.2f}x augmented rows selected with seed {args.seed}",
            image_text=(
                "referenced from Data/Images_dataset_augmented"
                if not args.copy_images
                else "copied into this variant's images folder"
            ),
            command=command,
        )
        summaries.append(summary)

    for variant, sigma_level in BRIGHTNESS_VARIANTS.items():
        logging.info("Creating %s", variant)
        rows = create_brightness_variant(
            variant=variant,
            sigma_level=sigma_level,
            originals=originals,
            stats=stats,
            output_dir=args.output_dir,
            input_csv=args.input_csv,
            seed=args.seed,
            luminance_std=luminance_std,
            workers=args.workers,
            fieldnames=fieldnames,
        )
        expected_augmented = original_count * 2
        summary = validate_variant(
            variant=variant,
            rows=rows,
            originals=originals,
            expected_total_rows=original_count + expected_augmented,
            expected_augmented_rows=expected_augmented,
            output_dir=args.output_dir,
            manifest_only_size_variant=False,
            sigma_variant=True,
            verified_paths=verified_paths,
        )
        contact_sheets[variant] = create_contact_sheet(
            variant=variant,
            rows=rows,
            originals=originals,
            figure_dir=DEFAULT_FIGURE_DIR,
            seed=args.seed,
        )
        write_variant_readme(
            variant=variant,
            rows=rows,
            variant_dir=args.output_dir / variant,
            summary=summary,
            parameter_text=(
                f"+/- {sigma_level} * luminance_std ({luminance_std:.6f}) "
                "with target luminance capped to [0, 255]"
            ),
            image_text="generated images stored in this variant's images folder",
            command=command,
        )
        summaries.append(summary)

    for variant, (sigma_level, noise_sigma) in NOISE_VARIANTS.items():
        logging.info("Creating %s", variant)
        rows = create_noise_variant(
            variant=variant,
            sigma_level=sigma_level,
            noise_sigma=noise_sigma,
            originals=originals,
            output_dir=args.output_dir,
            input_csv=args.input_csv,
            seed=args.seed,
            workers=args.workers,
            fieldnames=fieldnames,
        )
        expected_augmented = original_count
        summary = validate_variant(
            variant=variant,
            rows=rows,
            originals=originals,
            expected_total_rows=original_count + expected_augmented,
            expected_augmented_rows=expected_augmented,
            output_dir=args.output_dir,
            manifest_only_size_variant=False,
            sigma_variant=True,
            verified_paths=verified_paths,
        )
        contact_sheets[variant] = create_contact_sheet(
            variant=variant,
            rows=rows,
            originals=originals,
            figure_dir=DEFAULT_FIGURE_DIR,
            seed=args.seed,
        )
        write_variant_readme(
            variant=variant,
            rows=rows,
            variant_dir=args.output_dir / variant,
            summary=summary,
            parameter_text=(
                f"Gaussian noise sigma {noise_sigma:.3f} in normalized RGB "
                f"({noise_sigma * 255.0:.3f} on 0-255 scale)"
            ),
            image_text="generated images stored in this variant's images folder",
            command=command,
        )
        summaries.append(summary)

    checksum_path = write_checksums(args.output_dir)
    create_report(
        summaries=summaries,
        output_dir=args.output_dir,
        input_csv=args.input_csv,
        stats_csv=args.stats_csv,
        report_path=args.report,
        seed=args.seed,
        copy_images=args.copy_images,
        original_count=original_count,
        luminance_mean=luminance_mean,
        luminance_std=luminance_std,
        contact_sheets=contact_sheets,
        checksum_path=checksum_path,
    )

    logging.info("Completed successfully.")
    logging.info("Output parent folder: %s", args.output_dir)
    logging.info("Report: %s", args.report)
    logging.info("Checksums: %s", args.output_dir / "checksums_sha256.csv")
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

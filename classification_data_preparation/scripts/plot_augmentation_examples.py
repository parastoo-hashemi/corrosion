#!/usr/bin/env python3
"""Plot original-versus-augmented evidence panels for all five recipes."""

from __future__ import annotations

import argparse
import csv
import sys
import textwrap
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_METADATA = PROJECT_ROOT / "Data" / "Images_Dataset_A-Z-1_augmented.csv"
DEFAULT_TABLE = PROJECT_ROOT / "classification_data_preparation" / "tables" / "image_statistics_full.csv"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "classification_data_preparation" / "figures"
REGULAR_FONT = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
BOLD_FONT = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")

RECIPES = {
    "brightness_contrast": {
        "filename": "recipe1_brightness_contrast.png",
        "title": "Recipe 1 — Brightness and contrast",
        "range": "brightness [0.75, 1.28]  |  contrast [0.78, 1.25]",
        "purpose": "Evidence of controlled illumination and contrast variability.",
    },
    "saturation_colour_balance": {
        "filename": "recipe2_saturation_colour_balance.png",
        "title": "Recipe 2 — Saturation and colour balance",
        "range": "saturation [0.78, 1.28]  |  raw RGB gains [0.94, 1.06], mean-normalized",
        "purpose": "Evidence of camera white-balance and colour-intensity variability.",
    },
    "gaussian_blur_noise": {
        "filename": "recipe3_blur_noise.png",
        "title": "Recipe 3 — Gaussian blur and sensor noise",
        "range": "blur radius [0.3, 1.5] px  |  noise sigma [0.005, 0.035] on [0, 1]",
        "purpose": "Evidence of mild focus and pixel-noise variability.",
    },
    "brightness_contrast_saturation": {
        "filename": "recipe4_combined.png",
        "title": "Recipe 4 — Combined photometric variation",
        "range": "brightness, contrast, saturation independently sampled from [0.82, 1.18]",
        "purpose": "Evidence of compound but bounded acquisition effects.",
    },
    "horizontal_flip_brightness": {
        "filename": "recipe5_flip_brightness.png",
        "title": "Recipe 5 — Horizontal flip and brightness",
        "range": "left-right mirror  |  brightness [0.85, 1.15]",
        "purpose": "Evidence of position-invariant spatial diversity for total-rust classification.",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata-csv", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--statistics-csv", type=Path, default=DEFAULT_TABLE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    path = BOLD_FONT if bold else REGULAR_FONT
    try:
        return ImageFont.truetype(str(path), size=size)
    except OSError:
        return ImageFont.load_default()


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"CSV not found: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (PROJECT_ROOT / path).resolve()


def choose_examples(statistics: list[dict[str, str]]) -> list[dict[str, str]]:
    chosen: list[dict[str, str]] = []
    for label in ("1", "2", "3", "4"):
        candidates = [row for row in statistics if row["label"] == label]
        if not candidates:
            raise ValueError(f"No statistics rows found for label {label}.")
        luminance = np.asarray(
            [float(row["mean_luminance_rec709_0_255"]) for row in candidates]
        )
        lower, upper = np.percentile(luminance, [20, 80])
        central = [
            row
            for row in candidates
            if lower <= float(row["mean_luminance_rec709_0_255"]) <= upper
        ]
        central.sort(
            key=lambda row: (
                -float(row["mean_channel_std_0_255"]),
                row["original_image_name"],
            )
        )
        chosen.append(central[0])
    return chosen


def fit_on_tile(path: Path, size: tuple[int, int]) -> Image.Image:
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        rgb.thumbnail(size, Image.Resampling.LANCZOS)
        tile = Image.new("RGB", size, "#EEF2F5")
        tile.paste(rgb, ((size[0] - rgb.width) // 2, (size[1] - rgb.height) // 2))
        return tile


def centered_x(draw: ImageDraw.ImageDraw, text: str, selected_font: ImageFont.ImageFont, center: float) -> float:
    box = draw.textbbox((0, 0), text, font=selected_font)
    return center - (box[2] - box[0]) / 2


def find_augmented_row(
    metadata: list[dict[str, str]], source_name: str, recipe: str
) -> dict[str, str]:
    matches = [
        row
        for row in metadata
        if row["original_image_name"] == source_name
        and row["augmentation_type"] == recipe
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one {recipe!r} row for {source_name!r}; found {len(matches)}."
        )
    return matches[0]


def make_recipe_figure(
    recipe: str,
    configuration: dict[str, str],
    examples: list[dict[str, str]],
    metadata: list[dict[str, str]],
    output: Path,
) -> None:
    width, height = 2100, 1680
    margin, column_gap = 80, 55
    column_width = int((width - 2 * margin - column_gap) / 2)
    image_height = 235
    first_y, row_step = 285, 330

    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    navy, blue, orange = "#183153", "#2F6690", "#C76B29"

    title_font = font(42, True)
    draw.text(
        (centered_x(draw, configuration["title"], title_font, width / 2), 30),
        configuration["title"],
        font=title_font,
        fill=navy,
    )
    range_font = font(25, True)
    draw.text(
        (centered_x(draw, configuration["range"], range_font, width / 2), 91),
        configuration["range"],
        font=range_font,
        fill="#486581",
    )
    purpose_font = font(23)
    draw.text(
        (centered_x(draw, configuration["purpose"], purpose_font, width / 2), 137),
        configuration["purpose"],
        font=purpose_font,
        fill="#627D98",
    )
    draw.text((margin, 215), "Original", font=font(29, True), fill=blue)
    draw.text(
        (margin + column_width + column_gap, 215),
        "Augmented output",
        font=font(29, True),
        fill=orange,
    )

    for row_index, example in enumerate(examples):
        y = first_y + row_index * row_step
        augmented = find_augmented_row(
            metadata, example["original_image_name"], recipe
        )
        original_path = resolve_path(example["original_image_path"])
        augmented_path = resolve_path(augmented["image_path"])
        if not original_path.is_file() or not augmented_path.is_file():
            raise FileNotFoundError(
                f"Missing example image: {original_path} or {augmented_path}"
            )

        original_tile = fit_on_tile(original_path, (column_width, image_height))
        augmented_tile = fit_on_tile(augmented_path, (column_width, image_height))
        left_x = margin
        right_x = margin + column_width + column_gap
        canvas.paste(original_tile, (left_x, y))
        canvas.paste(augmented_tile, (right_x, y))
        draw.rectangle(
            (left_x, y, left_x + column_width, y + image_height),
            outline=blue,
            width=4,
        )
        draw.rectangle(
            (right_x, y, right_x + column_width, y + image_height),
            outline=orange,
            width=4,
        )

        source_caption = (
            f"Class {example['label']} | specimen {example['specimen_id']} | "
            f"{example['original_image_name']} | "
            f"mean Y={float(example['mean_luminance_rec709_0_255']):.2f}"
        )
        draw.text(
            (left_x + 5, y + image_height + 10),
            source_caption,
            font=font(19),
            fill=navy,
        )
        parameter_lines = textwrap.wrap(
            augmented["augmentation_parameters"], width=94
        )
        draw.text(
            (right_x + 5, y + image_height + 10),
            f"Parameters: {parameter_lines[0]}",
            font=font(19, True),
            fill="#7C3F18",
        )
        if len(parameter_lines) > 1:
            draw.text(
                (right_x + 5, y + image_height + 36),
                parameter_lines[1],
                font=font(19, True),
                fill="#7C3F18",
            )

    footer = (
        "Examples are existing offline files from the generated dataset; "
        "no recipe was recomputed or changed for this figure."
    )
    footer_font = font(22)
    draw.text(
        (centered_x(draw, footer, footer_font, width / 2), height - 48),
        footer,
        font=footer_font,
        fill="#627D98",
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    canvas.save(temporary, format="PNG", dpi=(300, 300), compress_level=6)
    temporary.replace(output)


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    outputs = {
        recipe: output_dir / configuration["filename"]
        for recipe, configuration in RECIPES.items()
    }
    existing = [path for path in outputs.values() if path.exists()]
    if existing and not args.overwrite:
        raise FileExistsError(
            "Output figure(s) exist; use --overwrite:\n"
            + "\n".join(str(path) for path in existing)
        )

    metadata = read_csv(args.metadata_csv.resolve())
    statistics = read_csv(args.statistics_csv.resolve())
    examples = choose_examples(statistics)
    for recipe, configuration in RECIPES.items():
        output = outputs[recipe]
        make_recipe_figure(
            recipe,
            configuration,
            examples,
            metadata,
            output,
        )
        print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERROR: {type(error).__name__}: {error}", file=sys.stderr)
        raise SystemExit(1)

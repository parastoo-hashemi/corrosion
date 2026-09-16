#!/usr/bin/env python3
"""Create a visual panel of the darkest and brightest original images."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TABLE = PROJECT_ROOT / "classification_data_preparation" / "tables" / "image_statistics_full.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "classification_data_preparation" / "figures" / "luminance_extremes.png"
REGULAR_FONT = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
BOLD_FONT = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--statistics-csv", type=Path, default=DEFAULT_TABLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--count", type=int, default=4)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    path = BOLD_FONT if bold else REGULAR_FONT
    try:
        return ImageFont.truetype(str(path), size=size)
    except OSError:
        return ImageFont.load_default()


def resolve_path(value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (PROJECT_ROOT / path).resolve()


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"Statistics table not found: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    required = {
        "original_image_name",
        "original_image_path",
        "specimen_id",
        "label",
        "mean_luminance_rec709_0_255",
    }
    if not rows or not required <= set(rows[0]):
        raise ValueError(f"Statistics table must contain {sorted(required)}.")
    return rows


def fit_on_tile(source_path: Path, size: tuple[int, int]) -> Image.Image:
    with Image.open(source_path) as image:
        rgb = image.convert("RGB")
        rgb.thumbnail(size, Image.Resampling.LANCZOS)
        tile = Image.new("RGB", size, "#EEF2F5")
        tile.paste(rgb, ((size[0] - rgb.width) // 2, (size[1] - rgb.height) // 2))
        return tile


def centered_x(draw: ImageDraw.ImageDraw, text: str, selected_font: ImageFont.ImageFont, center: float) -> float:
    box = draw.textbbox((0, 0), text, font=selected_font)
    return center - (box[2] - box[0]) / 2


def main() -> int:
    args = parse_args()
    if args.count < 1 or args.count > 8:
        raise ValueError("--count must be between 1 and 8.")
    output = args.output.resolve()
    if output.exists() and not args.overwrite:
        raise FileExistsError(f"Output exists: {output}. Use --overwrite.")

    rows = read_rows(args.statistics_csv.resolve())
    ordered = sorted(
        rows,
        key=lambda row: (
            float(row["mean_luminance_rec709_0_255"]),
            row["original_image_name"],
        ),
    )
    darkest = ordered[: args.count]
    brightest = list(reversed(ordered[-args.count :]))

    width, height = 2000, 1250
    outer, gap = 70, 24
    tile_width = int((width - 2 * outer - (args.count - 1) * gap) / args.count)
    image_height = 245
    row_height = 445
    first_y = 235

    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    navy = "#183153"
    title = "Observed luminance extremes in the original image dataset"
    title_font = font(40, True)
    draw.text(
        (centered_x(draw, title, title_font, width / 2), 34),
        title,
        font=title_font,
        fill=navy,
    )
    subtitle = (
        "Images ranked by mean Rec.709 luminance "
        "(Y = 0.2126R + 0.7152G + 0.0722B)"
    )
    subtitle_font = font(24)
    draw.text(
        (centered_x(draw, subtitle, subtitle_font, width / 2), 92),
        subtitle,
        font=subtitle_font,
        fill="#486581",
    )

    for row_index, (heading, selected, color) in enumerate(
        (
            (f"{args.count} darkest originals", darkest, "#A23B4A"),
            (f"{args.count} brightest originals", brightest, "#2F6690"),
        )
    ):
        y = first_y + row_index * row_height
        draw.text((outer, y - 57), heading, font=font(29, True), fill=color)
        for column, record in enumerate(selected):
            x = outer + column * (tile_width + gap)
            tile = fit_on_tile(
                resolve_path(record["original_image_path"]),
                (tile_width, image_height),
            )
            canvas.paste(tile, (x, y))
            draw.rectangle(
                (x, y, x + tile_width, y + image_height),
                outline=color,
                width=4,
            )
            luminance = float(record["mean_luminance_rec709_0_255"])
            lines = [
                record["original_image_name"],
                f"Y mean = {luminance:.2f}",
                f"specimen {record['specimen_id']} | label {record['label']}",
            ]
            for line_index, line in enumerate(lines):
                selected_font = font(19, bold=line_index == 1)
                draw.text(
                    (
                        centered_x(draw, line, selected_font, x + tile_width / 2),
                        y + image_height + 13 + line_index * 31,
                    ),
                    line,
                    font=selected_font,
                    fill=navy if line_index != 1 else color,
                )

    minimum = float(darkest[0]["mean_luminance_rec709_0_255"])
    maximum = float(brightest[0]["mean_luminance_rec709_0_255"])
    evidence = (
        f"Measured range: {minimum:.2f}–{maximum:.2f}; "
        f"brightest/darkest ratio = {maximum / minimum:.3f}x"
    )
    evidence_font = font(27, True)
    draw.rounded_rectangle(
        (390, height - 90, width - 390, height - 28),
        radius=12,
        fill="#F4F7FA",
        outline="#9FB3C8",
        width=2,
    )
    draw.text(
        (centered_x(draw, evidence, evidence_font, width / 2), height - 74),
        evidence,
        font=evidence_font,
        fill=navy,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    canvas.save(temporary, format="PNG", dpi=(300, 300), compress_level=6)
    temporary.replace(output)
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERROR: {type(error).__name__}: {error}", file=sys.stderr)
        raise SystemExit(1)

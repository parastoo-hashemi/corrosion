#!/usr/bin/env python3
"""Plot the distribution of image-level mean Rec.709 luminance."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TABLE = PROJECT_ROOT / "classification_data_preparation" / "tables" / "image_statistics_full.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "classification_data_preparation" / "figures" / "luminance_histogram.png"
REGULAR_FONT = Path("/System/Library/Fonts/Supplemental/Arial.ttf")
BOLD_FONT = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--statistics-csv", type=Path, default=DEFAULT_TABLE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--bins", type=int, default=30)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    path = BOLD_FONT if bold else REGULAR_FONT
    try:
        return ImageFont.truetype(str(path), size=size)
    except OSError:
        return ImageFont.load_default()


def read_values(path: Path) -> np.ndarray:
    if not path.is_file():
        raise FileNotFoundError(f"Statistics table not found: {path}")
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        field = "mean_luminance_rec709_0_255"
        if field not in (reader.fieldnames or []):
            raise ValueError(f"Statistics table is missing {field!r}.")
        values = [float(row[field]) for row in reader]
    if not values:
        raise ValueError("Statistics table contains no rows.")
    return np.asarray(values, dtype=np.float64)


def draw_centered(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    selected_font: ImageFont.ImageFont,
    fill: str,
) -> None:
    box = draw.textbbox((0, 0), text, font=selected_font)
    width = box[2] - box[0]
    draw.text((xy[0] - width / 2, xy[1]), text, font=selected_font, fill=fill)


def main() -> int:
    args = parse_args()
    if args.bins < 5:
        raise ValueError("--bins must be at least 5.")
    output = args.output.resolve()
    if output.exists() and not args.overwrite:
        raise FileExistsError(f"Output exists: {output}. Use --overwrite.")

    values = read_values(args.statistics_csv.resolve())
    minimum = float(values.min())
    p05, median, p95 = [float(value) for value in np.percentile(values, [5, 50, 95])]
    maximum = float(values.max())
    counts, edges = np.histogram(values, bins=args.bins, range=(0.0, 255.0))

    width, height = 1800, 1100
    left, right, top, bottom = 150, 90, 175, 165
    plot_left, plot_right = left, width - right
    plot_top, plot_bottom = top, height - bottom
    plot_width = plot_right - plot_left
    plot_height = plot_bottom - plot_top

    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    navy, blue, grid = "#183153", "#4C78A8", "#D9E2EC"

    draw_centered(
        draw,
        (width / 2, 35),
        f"Distribution of mean image luminance ({len(values)} original images)",
        font(38, bold=True),
        navy,
    )
    draw_centered(
        draw,
        (width / 2, 88),
        "Rec.709 definition: Y = 0.2126R + 0.7152G + 0.0722B; image-level mean on a 0–255 scale",
        font(23),
        "#334E68",
    )

    maximum_count = max(1, int(counts.max()))
    y_max = int(np.ceil(maximum_count / 20.0) * 20)
    y_max = max(20, y_max)
    for tick in np.linspace(0, y_max, 6):
        y = plot_bottom - float(tick) / y_max * plot_height
        draw.line((plot_left, y, plot_right, y), fill=grid, width=2)
        label = str(int(round(tick)))
        box = draw.textbbox((0, 0), label, font=font(20))
        draw.text(
            (plot_left - 18 - (box[2] - box[0]), y - 11),
            label,
            font=font(20),
            fill="#526D82",
        )

    bar_width = plot_width / len(counts)
    for index, count in enumerate(counts):
        x0 = plot_left + index * bar_width + 2
        x1 = plot_left + (index + 1) * bar_width - 2
        y0 = plot_bottom - float(count) / y_max * plot_height
        draw.rectangle((x0, y0, x1, plot_bottom), fill=blue, outline="#355C7D")

    for tick in (0, 50, 100, 150, 200, 255):
        x = plot_left + tick / 255.0 * plot_width
        draw.line((x, plot_bottom, x, plot_bottom + 10), fill=navy, width=2)
        draw_centered(draw, (x, plot_bottom + 18), str(tick), font(20), navy)

    draw.line((plot_left, plot_top, plot_left, plot_bottom), fill=navy, width=3)
    draw.line((plot_left, plot_bottom, plot_right, plot_bottom), fill=navy, width=3)
    draw_centered(
        draw,
        (width / 2, height - 85),
        "Mean image luminance (0–255)",
        font(25, bold=True),
        navy,
    )
    draw.text((22, plot_top + plot_height / 2 - 15), "Images", font=font(25, True), fill=navy)

    markers = [
        ("Min", minimum, "#B23A48"),
        ("P05", p05, "#E07A1F"),
        ("Median", median, "#6C757D"),
        ("P95", p95, "#2A9D5B"),
        ("Max", maximum, "#2F5597"),
    ]
    for marker_index, (name, value, color) in enumerate(markers):
        x = plot_left + value / 255.0 * plot_width
        draw.line((x, plot_top, x, plot_bottom), fill=color, width=4)
        label_y = plot_top + 10 + (marker_index % 2) * 42
        label = f"{name} {value:.2f}"
        box = draw.textbbox((0, 0), label, font=font(20, True))
        label_width = box[2] - box[0]
        label_x = min(max(plot_left + 5, x - label_width / 2), plot_right - label_width - 5)
        draw.rounded_rectangle(
            (label_x - 6, label_y - 3, label_x + label_width + 6, label_y + 29),
            radius=5,
            fill="white",
            outline=color,
            width=2,
        )
        draw.text((label_x, label_y), label, font=font(20, True), fill=color)

    summary = (
        f"Observed max/min ratio = {maximum / minimum:.3f}x     "
        f"P95/P05 ratio = {p95 / p05:.3f}x"
    )
    draw_centered(draw, (width / 2, height - 43), summary, font(23, True), "#334E68")

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

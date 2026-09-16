#!/usr/bin/env python3
"""Measure auditable image statistics for the original corrosion images only."""

from __future__ import annotations

import argparse
import csv
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageStat


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_METADATA = PROJECT_ROOT / "Data" / "Images_Dataset_A-Z-1_augmented.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "classification_data_preparation" / "tables" / "image_statistics_full.csv"
LUMINANCE_WEIGHTS = (0.2126, 0.7152, 0.0722)

INPUT_FIELDS = [
    "original_image_name",
    "original_image_path",
    "specimen_id",
    "label",
    "Sample Name",
    "ID",
    "Treatment",
    "Label_Treatment",
    "Ageing Days",
    "A_Surface_Total_Rust_Percentage[%]",
    "A_Total_Rust_Category_(1–4)",
]

STATISTIC_FIELDS = [
    "width_px",
    "height_px",
    "source_mode",
    "file_size_bytes",
    "mean_red_0_255",
    "mean_green_0_255",
    "mean_blue_0_255",
    "std_red_0_255",
    "std_green_0_255",
    "std_blue_0_255",
    "mean_rgb_intensity_0_255",
    "mean_channel_std_0_255",
    "mean_luminance_rec709_0_255",
    "mean_luminance_rec709_0_1",
    "luminance_rank_ascending",
    "luminance_percentile_rank",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Measure per-image RGB and Rec.709 luminance statistics for the "
            "original rows in the offline-augmented corrosion metadata."
        )
    )
    parser.add_argument("--metadata-csv", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--output-csv", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--workers",
        type=int,
        default=min(4, os.cpu_count() or 1),
        help="Parallel image readers (default: up to 4).",
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def resolve_project_path(value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (PROJECT_ROOT / path).resolve()


def is_original(value: str) -> bool:
    normalized = str(value).strip().casefold()
    if normalized not in {"true", "false"}:
        raise ValueError(f"Invalid is_augmented value: {value!r}")
    return normalized == "false"


def read_original_rows(metadata_csv: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not metadata_csv.is_file():
        raise FileNotFoundError(f"Metadata CSV not found: {metadata_csv}")
    with metadata_csv.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        required = {
            "original_image_name",
            "original_image_path",
            "specimen_id",
            "label",
            "is_augmented",
            "A_Total_Rust_Category_(1–4)",
        }
        missing = sorted(required - set(headers))
        if missing:
            raise ValueError(f"Metadata CSV is missing columns: {missing}")
        rows = [row for row in reader if is_original(row["is_augmented"])]

    if not rows:
        raise ValueError("No original-image rows were found.")
    names = [row["original_image_name"] for row in rows]
    if len(set(names)) != len(names):
        raise ValueError("Original-image rows contain duplicate original_image_name values.")
    return headers, rows


def measure_one(row: dict[str, str]) -> dict[str, Any]:
    path = resolve_project_path(row["original_image_path"])
    if not path.is_file():
        raise FileNotFoundError(f"Original image not found: {path}")

    with Image.open(path) as source:
        source.load()
        width, height = source.size
        source_mode = source.mode
        rgb = source.convert("RGB")
        statistics = ImageStat.Stat(rgb)
        means = [float(value) for value in statistics.mean]
        standard_deviations = [float(value) for value in statistics.stddev]

    mean_luminance = sum(
        weight * channel_mean
        for weight, channel_mean in zip(LUMINANCE_WEIGHTS, means)
    )
    result = {field: row.get(field, "") for field in INPUT_FIELDS}
    result.update(
        {
            "width_px": width,
            "height_px": height,
            "source_mode": source_mode,
            "file_size_bytes": path.stat().st_size,
            "mean_red_0_255": means[0],
            "mean_green_0_255": means[1],
            "mean_blue_0_255": means[2],
            "std_red_0_255": standard_deviations[0],
            "std_green_0_255": standard_deviations[1],
            "std_blue_0_255": standard_deviations[2],
            "mean_rgb_intensity_0_255": float(np.mean(means)),
            "mean_channel_std_0_255": float(np.mean(standard_deviations)),
            "mean_luminance_rec709_0_255": mean_luminance,
            "mean_luminance_rec709_0_1": mean_luminance / 255.0,
        }
    )
    return result


def add_luminance_ranks(rows: list[dict[str, Any]]) -> None:
    values = np.asarray(
        [row["mean_luminance_rec709_0_255"] for row in rows], dtype=np.float64
    )
    sorted_indices = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=np.int64)
    ranks[sorted_indices] = np.arange(1, len(values) + 1)
    denominator = max(1, len(values) - 1)
    for index, row in enumerate(rows):
        row["luminance_rank_ascending"] = int(ranks[index])
        row["luminance_percentile_rank"] = (
            float(ranks[index] - 1) / denominator * 100.0
        )


def format_for_csv(value: Any) -> Any:
    return f"{value:.6f}" if isinstance(value, float) else value


def write_table(output_csv: Path, rows: list[dict[str, Any]], overwrite: bool) -> None:
    if output_csv.exists() and not overwrite:
        raise FileExistsError(
            f"Output table exists: {output_csv}. Use --overwrite to replace it."
        )
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_csv.with_suffix(output_csv.suffix + ".tmp")
    fieldnames = INPUT_FIELDS + STATISTIC_FIELDS
    with temporary.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: format_for_csv(row.get(key, "")) for key in fieldnames})
    temporary.replace(output_csv)


def summarize(rows: list[dict[str, Any]]) -> dict[str, float]:
    values = np.asarray(
        [row["mean_luminance_rec709_0_255"] for row in rows], dtype=np.float64
    )
    p05, median, p95 = np.percentile(values, [5, 50, 95])
    minimum = float(values.min())
    maximum = float(values.max())
    return {
        "minimum": minimum,
        "p05": float(p05),
        "median": float(median),
        "p95": float(p95),
        "maximum": maximum,
        "max_min_ratio": maximum / minimum,
        "p95_p05_ratio": float(p95 / p05),
    }


def main() -> int:
    args = parse_args()
    if args.workers < 1:
        raise ValueError("--workers must be at least 1.")
    metadata_csv = args.metadata_csv.resolve()
    output_csv = args.output_csv.resolve()

    _, original_rows = read_original_rows(metadata_csv)
    print(f"Measuring {len(original_rows)} original images ...")
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        measured = list(executor.map(measure_one, original_rows, chunksize=8))
    add_luminance_ranks(measured)
    write_table(output_csv, measured, args.overwrite)

    summary = summarize(measured)
    print(f"Wrote {output_csv}")
    print(
        "Rec.709 mean luminance: "
        f"min={summary['minimum']:.3f}, P05={summary['p05']:.3f}, "
        f"median={summary['median']:.3f}, P95={summary['p95']:.3f}, "
        f"max={summary['maximum']:.3f}"
    )
    print(
        f"Ratios: max/min={summary['max_min_ratio']:.3f}x, "
        f"P95/P05={summary['p95_p05_ratio']:.3f}x"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("ERROR: interrupted.", file=sys.stderr)
        raise SystemExit(130)
    except Exception as error:
        print(f"ERROR: {type(error).__name__}: {error}", file=sys.stderr)
        raise SystemExit(1)

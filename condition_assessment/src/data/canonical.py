from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import Settings
from src.data.io import (
    discover_images,
    load_excel_table,
    prepare_canonical_frame,
    summarize_canonical_dataset,
    validate_canonical_dataset,
)
from src.logging_utils import get_logger


LOGGER = get_logger(__name__)


def build_canonical_dataset(settings: Settings) -> tuple[pd.DataFrame, dict[str, object], list[str]]:
    LOGGER.info("Loading spreadsheet: %s", settings.paths.excel_path)
    excel_df = load_excel_table(settings.paths.excel_path)
    LOGGER.info("Scanning image directory: %s", settings.paths.image_dir)
    image_df = discover_images(settings.paths.image_dir)
    canonical_df = prepare_canonical_frame(
        excel_df=excel_df,
        image_df=image_df,
        wire_loss_scale_threshold=settings.project.wire_loss_scale_to_percent_if_max_leq,
    )
    summary = summarize_canonical_dataset(canonical_df)
    issues = validate_canonical_dataset(canonical_df)
    return canonical_df, summary, issues


def export_canonical_dataset(df: pd.DataFrame, output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "canonical_dataset.csv"
    parquet_path = output_dir / "canonical_dataset.parquet"
    df.to_csv(csv_path, index=False)
    df.to_parquet(parquet_path, index=False)
    return {"csv": csv_path, "parquet": parquet_path}

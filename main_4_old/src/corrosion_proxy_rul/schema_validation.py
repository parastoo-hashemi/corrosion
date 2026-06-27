from __future__ import annotations

from typing import Sequence

import pandas as pd


REQUIRED_CANONICAL_COLUMNS = [
    "sample_name",
    "specimen_id",
    "n_steel_mesh_raw",
    "treatment_raw",
    "treatment_label_raw",
    "ageing_days",
    "surface_total_rust_pct",
    "surface_total_rust_category",
    "peak_rust_pct",
    "peak_rust_category",
    "peak_rust_location_cm",
    "cover_mm_raw",
    "wire_area_loss_raw",
    "ultimate_load_kn",
]


def validate_required_columns(df: pd.DataFrame) -> list[dict]:
    issues = []
    missing = [col for col in REQUIRED_CANONICAL_COLUMNS if col not in df.columns]
    if missing:
        issues.append(
            {
                "issue_type": "missing_required_columns",
                "severity": "error",
                "detail": ", ".join(missing),
            }
        )
    return issues


def validate_unique_rows(df: pd.DataFrame) -> list[dict]:
    issues = []
    duplicate_sample_name = int(df["sample_name"].duplicated().sum())
    duplicate_specimen_time = int(df[["specimen_id", "ageing_days"]].duplicated().sum())
    if duplicate_sample_name:
        issues.append(
            {
                "issue_type": "duplicate_sample_name",
                "severity": "error",
                "detail": str(duplicate_sample_name),
            }
        )
    if duplicate_specimen_time:
        issues.append(
            {
                "issue_type": "duplicate_specimen_time",
                "severity": "error",
                "detail": str(duplicate_specimen_time),
            }
        )
    return issues


def validate_constant_within_specimen(
    df: pd.DataFrame, columns: Sequence[str]
) -> list[dict]:
    issues = []
    for column in columns:
        offenders = (
            df.groupby("specimen_id")[column].nunique(dropna=False).gt(1)
        )
        offender_ids = sorted(offenders[offenders].index.tolist())
        if offender_ids:
            issues.append(
                {
                    "issue_type": "specimen_level_inconsistency",
                    "severity": "error",
                    "column": column,
                    "detail": ", ".join(offender_ids),
                }
            )
    return issues

from __future__ import annotations

from typing import Tuple

import pandas as pd

from .data_loading import parse_sample_name
from .schema_validation import (
    validate_constant_within_specimen,
    validate_required_columns,
    validate_unique_rows,
)
from .specimen_mapping import apply_mapping, mapping_to_dataframe


def _issue(issue_type: str, severity: str, detail: str, sample_name: str | None = None):
    return {
        "issue_type": issue_type,
        "severity": severity,
        "sample_name": sample_name,
        "detail": detail,
    }


def parse_metadata_fields(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    issues: list[dict] = []
    parsed_rows = []
    for sample_name in df["sample_name"]:
        try:
            parsed_rows.append(parse_sample_name(sample_name))
        except ValueError as exc:
            issues.append(_issue("sample_name_parse_error", "error", str(exc), sample_name))
            parsed_rows.append(
                {"specimen_id": None, "week": None, "calendar_date": pd.NaT}
            )
    parsed_df = pd.DataFrame(parsed_rows)
    parsed_df = parsed_df.rename(columns={"specimen_id": "specimen_id_from_name"})
    out = pd.concat([df.reset_index(drop=True), parsed_df], axis=1)
    specimen_mismatch = out["specimen_id"] != out["specimen_id_from_name"]
    for sample_name in out.loc[specimen_mismatch, "sample_name"]:
        issues.append(
            _issue(
                "specimen_id_mismatch",
                "error",
                "specimen_id column disagrees with sample_name",
                sample_name,
            )
        )
    out["week"] = out["week"].astype(int)
    out["calendar_date"] = pd.to_datetime(out["calendar_date"])
    day_mismatch = (out["week"] * 7) != out["ageing_days"]
    for sample_name in out.loc[day_mismatch, "sample_name"]:
        issues.append(
            _issue(
                "week_ageing_day_mismatch",
                "error",
                "week * 7 does not match ageing_days",
                sample_name,
            )
        )
    return out, pd.DataFrame(issues)


def build_master_table(
    metadata_df: pd.DataFrame, image_df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    issues: list[dict] = []

    issues.extend(validate_required_columns(metadata_df))
    metadata_df, parse_issues = parse_metadata_fields(metadata_df)
    if not parse_issues.empty:
        issues.extend(parse_issues.to_dict("records"))
    issues.extend(validate_unique_rows(metadata_df))
    issues.extend(
        validate_constant_within_specimen(
            metadata_df,
            ["treatment_raw", "treatment_label_raw", "n_steel_mesh_raw", "cover_mm_raw"],
        )
    )

    mapped_df = apply_mapping(metadata_df)

    image_workbook_merge = mapped_df.merge(
        image_df,
        on="sample_name",
        how="left",
        validate="one_to_one",
    )
    missing_images = image_workbook_merge["image_path"].isna()
    for sample_name in image_workbook_merge.loc[missing_images, "sample_name"]:
        issues.append(
            _issue("missing_image_for_workbook_row", "error", "No matching image file", sample_name)
        )

    unreadable_in_master = ~image_workbook_merge["image_readable"].fillna(False)
    for sample_name in image_workbook_merge.loc[unreadable_in_master, "sample_name"]:
        issues.append(
            _issue(
                "unreadable_image_for_workbook_row",
                "error",
                "Matching image exists but is unreadable",
                sample_name,
            )
        )

    workbook_names = set(mapped_df["sample_name"])
    orphan_images = image_df.loc[~image_df["sample_name"].isin(workbook_names)]
    for row in orphan_images.itertuples(index=False):
        issues.append(
            _issue(
                "orphan_image",
                "warning",
                f"image_readable={row.image_readable}; error={row.image_error}",
                row.sample_name,
            )
        )

    master_df = image_workbook_merge.loc[~missing_images & ~unreadable_in_master].copy()
    master_df["observation_id"] = master_df["sample_name"]
    master_df["wire_area_loss_frac"] = master_df["wire_area_loss_raw"]
    master_df["wire_area_loss_pct"] = master_df["wire_area_loss_raw"] * 100.0
    master_df["cover_mm"] = master_df["cover_mm_raw"]
    master_df["n_steel_mesh"] = master_df["n_steel_mesh_raw"].astype(int)
    master_df["has_structural_label"] = master_df[
        ["wire_area_loss_frac", "ultimate_load_kn"]
    ].notna().any(axis=1)
    master_df["is_terminal_structural_row"] = master_df["has_structural_label"]
    master_df = master_df.sort_values(["specimen_id", "ageing_days"]).reset_index(drop=True)

    specimen_mapping_df = mapping_to_dataframe()
    issues_df = pd.DataFrame(issues)
    if issues_df.empty:
        issues_df = pd.DataFrame(columns=["issue_type", "severity", "sample_name", "detail"])
    else:
        issues_df = issues_df.sort_values(
            ["severity", "issue_type", "sample_name"], na_position="last"
        )
    return master_df, specimen_mapping_df, issues_df


def build_terminal_structural_subset(master_df: pd.DataFrame) -> pd.DataFrame:
    subset = master_df.loc[master_df["has_structural_label"]].copy()
    return subset.sort_values(["specimen_id", "ageing_days"]).reset_index(drop=True)

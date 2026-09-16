from __future__ import annotations

from pathlib import Path
import re

import numpy as np
import pandas as pd


ID_PATTERN = re.compile(
    r"^(?P<specimen_id>[A-Za-z0-9]+)-(?P<capture_date>\d{8})-(?P<week>\d+)W$"
)

RAW_TO_CANONICAL = {
    "ID": "record_id",
    "N_Steel_Mesh": "n_steel_mesh",
    "Treatment": "treatment_code",
    "Ageing_Days": "ageing_days",
    "NaCl%": "nacl_pct",
    "A_Surface_Total_Rust_Percentage[%]": "surface_total_rust_pct",
    "A_Total_Rust_Category_(main_first–5)": "surface_total_rust_category",
    "B_Peak_Rust_Percentage_[%]": "peak_rust_pct",
    "B_Peak_Rust_Category_(main_first–5)": "peak_rust_category",
    "B_Location_of_Peak_Rus_ in_length_[cm]": "peak_rust_location_cm",
    "Cover_(Faliure_Surface)_[mm]": "cover_failure_surface_mm",
    "Last_Wire_Area_Loss_(Faliure_Surface)_%": "wire_area_loss_raw",
    "Ultimate_Load_[kN]": "ultimate_load_kn",
}

TREATMENT_NAME_MAP = {
    "NO": "No treatment",
    "MI": "Mixed-in inhibitor",
    "SA": "Surface-applied inhibitor",
    "PA": "Painted coating",
    "SA_PA": "Surface-applied + paint",
    "SA_VF": "Surface-applied + VF",
    "VF": "VF treatment",
}


def load_excel_table(excel_path: Path) -> pd.DataFrame:
    raw = pd.read_excel(excel_path)
    headers = [str(v).strip() for v in raw.iloc[0].tolist()]
    df = raw.iloc[1:].copy().reset_index(drop=True)
    df.columns = headers

    for column in df.columns:
        if column in {"ID", "Treatment"}:
            df[column] = df[column].astype(str).str.strip()
        else:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def discover_images(image_dir: Path) -> pd.DataFrame:
    rows = []
    for path in sorted(image_dir.glob("*.png")):
        rows.append(
            {
                "record_id": path.stem,
                "image_path": str(path.resolve()),
                "image_filename": path.name,
            }
        )
    return pd.DataFrame(rows)


def parse_record_ids(record_ids: pd.Series) -> pd.DataFrame:
    parts = record_ids.astype(str).str.extract(ID_PATTERN)
    out = pd.DataFrame(index=record_ids.index)
    out["specimen_id"] = parts["specimen_id"]
    out["capture_date"] = pd.to_datetime(
        parts["capture_date"], format="%Y%m%d", errors="coerce"
    )
    out["week"] = pd.to_numeric(parts["week"], errors="coerce")
    out["series_family"] = (
        out["specimen_id"].astype(str).str.extract(r"^([A-Za-z]+)")[0].fillna("UNK")
    )
    out["series_label"] = (
        out["specimen_id"].astype(str).str.extract(r"^(S\d|[A-Za-z])")[0].fillna("UNK")
    )
    out["record_id_valid"] = parts.notna().all(axis=1)
    return out


def wire_loss_to_percent(values: pd.Series, scale_threshold: float) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce")
    if numeric.dropna().empty:
        return numeric
    max_value = float(numeric.max())
    if max_value <= scale_threshold:
        return numeric * 100.0
    return numeric


def infer_campaign_id(df: pd.DataFrame) -> pd.Series:
    year = df["capture_date"].dt.year.fillna(0).astype(int).astype(str)
    mesh = df["n_steel_mesh"].fillna(-1).astype(int).astype(str)
    nacl = df["nacl_pct"].fillna(-1).map(lambda v: f"{float(v):.3f}" if v >= 0 else "nan")
    ageing = df["ageing_days"].fillna(-1).astype(int).astype(str)
    return "campaign_" + year + "_mesh" + mesh + "_nacl" + nacl + "_age" + ageing


def prepare_canonical_frame(
    excel_df: pd.DataFrame,
    image_df: pd.DataFrame,
    wire_loss_scale_threshold: float,
) -> pd.DataFrame:
    df = excel_df.rename(columns=RAW_TO_CANONICAL).copy()
    parsed = parse_record_ids(df["record_id"])
    df = pd.concat([df, parsed], axis=1)
    df = df.merge(image_df, on="record_id", how="outer", indicator="image_join_status")

    df["treatment_name"] = df["treatment_code"].map(TREATMENT_NAME_MAP).fillna(
        df["treatment_code"]
    )
    df["campaign_id"] = infer_campaign_id(df)
    df["capture_year"] = df["capture_date"].dt.year
    df["wire_area_loss_pct"] = wire_loss_to_percent(
        df["wire_area_loss_raw"], scale_threshold=wire_loss_scale_threshold
    )
    df["has_structural_labels"] = df[
        ["wire_area_loss_raw", "ultimate_load_kn"]
    ].notna().any(axis=1)
    df["sequence_order"] = (
        df.sort_values(["specimen_id", "week", "record_id"])
        .groupby("specimen_id")
        .cumcount()
        .reindex(df.index)
    )
    df["duplicate_record_id"] = df["record_id"].duplicated(keep=False)
    df["duplicate_specimen_week"] = df.duplicated(
        subset=["specimen_id", "week"], keep=False
    )
    df["image_exists"] = df["image_path"].notna()

    sort_cols = ["campaign_id", "specimen_id", "week", "record_id"]
    return df.sort_values(sort_cols, kind="stable").reset_index(drop=True)


def summarize_canonical_dataset(df: pd.DataFrame) -> dict[str, object]:
    structural_df = df[df["has_structural_labels"]].copy()
    return {
        "rows": int(len(df)),
        "image_rows": int(df["image_exists"].sum()),
        "unique_specimens": int(df["specimen_id"].nunique()),
        "campaigns": sorted(df["campaign_id"].dropna().unique().tolist()),
        "treatments": sorted(df["treatment_code"].dropna().unique().tolist()),
        "week_min": float(df["week"].min()),
        "week_max": float(df["week"].max()),
        "structural_rows": int(len(structural_df)),
        "structural_weeks": sorted(structural_df["week"].dropna().unique().tolist()),
        "duplicate_record_ids": int(df["duplicate_record_id"].sum()),
        "duplicate_specimen_week": int(df["duplicate_specimen_week"].sum()),
        "invalid_record_ids": int((~df["record_id_valid"]).sum()),
        "missing_images": int((~df["image_exists"]).sum()),
    }


def validate_canonical_dataset(df: pd.DataFrame) -> list[str]:
    issues: list[str] = []
    if df["record_id"].isna().any():
        issues.append("Canonical dataset contains rows without record_id.")
    if df["duplicate_record_id"].any():
        issues.append("Duplicate record_id values detected.")
    if df["duplicate_specimen_week"].any():
        issues.append("Duplicate specimen/week combinations detected.")
    if (~df["record_id_valid"]).any():
        issues.append("Some IDs do not match the expected specimen-date-week pattern.")
    if (~df["image_exists"]).any():
        issues.append("Some spreadsheet rows do not have matching images.")
    if df["week"].isna().any():
        issues.append("Some rows do not have valid week values.")
    if df["capture_date"].isna().any():
        issues.append("Some rows do not have valid capture dates.")
    return issues


def numeric_feature_columns(df: pd.DataFrame, exclude: set[str] | None = None) -> list[str]:
    exclude = exclude or set()
    cols = []
    for column in df.columns:
        if column in exclude:
            continue
        if pd.api.types.is_numeric_dtype(df[column]):
            cols.append(column)
    return cols

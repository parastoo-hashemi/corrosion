from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from PIL import Image


EXCEL_COLUMN_MAP = {
    ("Sample_level", "Sample Name"): "sample_name",
    ("Sample_level", "ID"): "specimen_id",
    ("Sample_level", "N_Steel_Mesh"): "n_steel_mesh_raw",
    ("Sample_level", "Treatment"): "treatment_raw",
    ("Sample_level", "Label_Treatment"): "treatment_label_raw",
    ("Sample_level", "Ageing Days"): "ageing_days",
    (
        "Corrosion_Progression_and_Quantification_Surface",
        "A_Surface_Total_Rust_Percentage[%]",
    ): "surface_total_rust_pct",
    (
        "Corrosion_Progression_and_Quantification_Surface",
        "A_Total_Rust_Category_(main_first–4)",
    ): "surface_total_rust_category",
    (
        "Corrosion_Progression_and_Quantification_Surface",
        "B_Peak_Rust_Percentage_[%]",
    ): "peak_rust_pct",
    (
        "Corrosion_Progression_and_Quantification_Surface",
        "B_Peak_Rust_Category_(main_first–4)",
    ): "peak_rust_category",
    (
        "Corrosion_Progression_and_Quantification_Surface",
        "B_Location_of_Peak_Rus_ in_length_[cm]",
    ): "peak_rust_location_cm",
    (
        "Corrosion_Progression_and_Quantification_Internal",
        "Cover_(Faliure_Surface)_[mm]",
    ): "cover_mm_raw",
    (
        "Corrosion_Progression_and_Quantification_Internal",
        "Last_Wire_Area_Loss_(Faliure_Surface)_%",
    ): "wire_area_loss_raw",
    (
        "Corrosion_Progression_and_Quantification_Internal",
        "Ultimate_Load_[kN]",
    ): "ultimate_load_kn",
}

SAMPLE_NAME_REGEX = re.compile(r"^(?P<specimen_id>.+)-(?P<date>\d{8})-(?P<week>\d+)W$")


def load_excel_metadata(excel_path: Path) -> pd.DataFrame:
    excel_path = Path(excel_path)
    df = pd.read_excel(excel_path, header=[0, 1])
    unknown = [col for col in df.columns if col not in EXCEL_COLUMN_MAP]
    if unknown:
        raise ValueError(f"Unexpected Excel columns: {unknown}")
    df = df.copy()
    df.columns = [EXCEL_COLUMN_MAP[col] for col in df.columns]
    return df


def parse_sample_name(sample_name: str) -> dict:
    match = SAMPLE_NAME_REGEX.match(sample_name)
    if not match:
        raise ValueError(f"Could not parse sample name: {sample_name}")
    payload = match.groupdict()
    payload["week"] = int(payload["week"])
    payload["calendar_date"] = pd.to_datetime(payload["date"], format="%Y%m%d")
    return payload


def scan_image_directory(images_dir: Path) -> pd.DataFrame:
    images_dir = Path(images_dir)
    rows = []
    for path in sorted(images_dir.glob("*.png")):
        record = {
            "image_filename": path.name,
            "sample_name": path.stem,
            "image_path": str(path),
            "image_readable": False,
            "image_width": None,
            "image_height": None,
            "image_error": None,
        }
        try:
            with Image.open(path) as image:
                record["image_width"], record["image_height"] = image.size
                record["image_readable"] = True
        except Exception as exc:  # pragma: no cover - exercised by corrupt file
            record["image_error"] = str(exc)
        rows.append(record)
    return pd.DataFrame(rows)

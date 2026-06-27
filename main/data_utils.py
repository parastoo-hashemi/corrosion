from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXCEL_PATH = REPO_ROOT / "Data" / "Images_Dataset_A-Z.xlsx"
DEFAULT_IMAGE_DIR = REPO_ROOT / "Data" / "Images_dataset"

COL_ID = "ID"
COL_TREATMENT = "Treatment"
COL_TARGET_PEAK = "B_Peak_Rust_Percentage_[%]"
COL_TARGET_PEAK_CAT = "B_Peak_Rust_Category_(main_first–5)"
COL_TARGET_AREA = "A_Surface_Total_Rust_Percentage[%]"
COL_N_MESH = "N_Steel_Mesh"
COL_AGEING_DAYS = "Ageing_Days"
COL_NACL = "NaCl%"
COL_COVER_MM = "Cover_(Faliure_Surface)_[mm]"

ID_PATTERN = re.compile(
    r"^(?P<specimen>[A-Za-z0-9]+)-(?P<date>\d{8})-(?P<week>\d+)W$"
)


@dataclass(frozen=True)
class DatasetSummary:
    n_rows: int
    n_specimens: int
    week_min: int
    week_max: int
    n_missing_images: int


def _safe_numeric_columns(df: pd.DataFrame, skip: Iterable[str]) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if col in skip:
            continue
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def load_corrosion_dataframe(
    excel_path: Path = DEFAULT_EXCEL_PATH, image_dir: Path = DEFAULT_IMAGE_DIR
) -> pd.DataFrame:
    """Load and clean the corrosion table from Excel.

    The main_first row in the provided file stores semantic column names, so this
    function promotes that row into headers and returns the cleaned data rows.
    """
    raw = pd.read_excel(excel_path)
    semantic_headers = [str(v).strip() for v in raw.iloc[0].tolist()]
    df = raw.iloc[1:].copy().reset_index(drop=True)
    df.columns = semantic_headers

    df = _safe_numeric_columns(df, skip={COL_ID, COL_TREATMENT})
    df[COL_ID] = df[COL_ID].astype(str)
    df[COL_TREATMENT] = df[COL_TREATMENT].astype(str)

    id_parts = df[COL_ID].str.extract(ID_PATTERN)
    df["specimen"] = id_parts["specimen"]
    df["capture_date"] = pd.to_datetime(
        id_parts["date"], format="%Y%m%d", errors="coerce"
    )
    df["week"] = pd.to_numeric(id_parts["week"], errors="coerce").astype("Int64")
    df["series"] = df["specimen"].str.extract(r"^([A-Za-z]+)")[0]
    df["specimen_number"] = pd.to_numeric(
        df["specimen"].str.extract(r"([0-9]+)$")[0], errors="coerce"
    )

    df["image_path"] = df[COL_ID].map(lambda x: str((image_dir / f"{x}.png").resolve()))
    df["image_exists"] = df["image_path"].map(lambda p: Path(p).exists())

    df = df.sort_values(["specimen", "week"], kind="stable").reset_index(drop=True)
    return df


def dataset_summary(df: pd.DataFrame) -> DatasetSummary:
    return DatasetSummary(
        n_rows=int(len(df)),
        n_specimens=int(df["specimen"].nunique()),
        week_min=int(df["week"].min()),
        week_max=int(df["week"].max()),
        n_missing_images=int((~df["image_exists"]).sum()),
    )


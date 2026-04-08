from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "Data"
EXCEL_PATH = DATA_DIR / "Images_Dataset_A-Z.xlsx"
IMAGE_DIR = DATA_DIR / "Images_dataset"

PHASE2_ROOT = Path(__file__).resolve().parent
ARTIFACTS_DIR = PHASE2_ROOT / "artifacts"
REPORTS_DIR = PHASE2_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
PER_MATERIAL_DIR = FIGURES_DIR / "per_material"

SEED = 42
TEST_SIZE = 0.2
VAL_SIZE_WITHIN_TRAIN = 0.2

TARGET_COL = "B_Peak_Rust_Percentage_[%]"
BASE_FEATURES = [
    "N_Steel_Mesh",
    "Treatment",
    "NaCl%",
    "Ageing_Days",
    "Cover_(Faliure_Surface)_[mm]",
    "week",
    "series",
]


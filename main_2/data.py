from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import torch
import torch.nn as nn
from torchvision.models import ResNet18_Weights, resnet18
from PIL import Image

ID_PATTERN = re.compile(
    r"^(?P<specimen>[A-Za-z0-9]+)-(?P<date>\d{8})-(?P<week>\d+)W$"
)


@dataclass
class SplitIndex:
    train_idx: np.ndarray
    val_idx: np.ndarray
    test_idx: np.ndarray


def load_dataframe(excel_path: Path, image_dir: Path) -> pd.DataFrame:
    raw = pd.read_excel(excel_path)
    headers = [str(v).strip() for v in raw.iloc[0].tolist()]
    df = raw.iloc[1:].copy().reset_index(drop=True)
    df.columns = headers

    for col in df.columns:
        if col in {"ID", "Treatment"}:
            continue
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["ID"] = df["ID"].astype(str)
    df["Treatment"] = df["Treatment"].astype(str)

    parts = df["ID"].str.extract(ID_PATTERN)
    df["specimen"] = parts["specimen"].astype(str)
    df["capture_date"] = pd.to_datetime(parts["date"], format="%Y%m%d", errors="coerce")
    df["week"] = pd.to_numeric(parts["week"], errors="coerce").astype(int)
    df["series"] = df["specimen"].str.extract(r"^([A-Za-z]+)")[0].fillna("UNK")
    df["image_path"] = df["ID"].map(lambda x: str((image_dir / f"{x}.png").resolve()))

    df = df.sort_values(["specimen", "week"], kind="stable").reset_index(drop=True)
    return df


def build_group_splits(
    df: pd.DataFrame,
    random_state: int = 42,
    test_size: float = 0.2,
    val_size_within_train: float = 0.2,
) -> SplitIndex:
    groups = df["specimen"].astype(str).values
    idx = np.arange(len(df))

    gss_outer = GroupShuffleSplit(
        n_splits=1, test_size=test_size, random_state=random_state
    )
    train_val_idx, test_idx = next(gss_outer.split(idx, groups=groups))

    groups_train_val = groups[train_val_idx]
    gss_inner = GroupShuffleSplit(
        n_splits=1, test_size=val_size_within_train, random_state=random_state
    )
    tr_local, va_local = next(
        gss_inner.split(train_val_idx, groups=groups_train_val)
    )
    train_idx = train_val_idx[tr_local]
    val_idx = train_val_idx[va_local]

    return SplitIndex(train_idx=train_idx, val_idx=val_idx, test_idx=test_idx)


def fit_tabular_preprocessor(
    df: pd.DataFrame, feature_cols: List[str], train_idx: np.ndarray
) -> ColumnTransformer:
    x_train = df.iloc[train_idx][feature_cols]
    cat_cols = [c for c in feature_cols if x_train[c].dtype == object]
    num_cols = [c for c in feature_cols if c not in cat_cols]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                num_cols,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        (
                            "onehot",
                            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                        ),
                    ]
                ),
                cat_cols,
            ),
        ]
    )
    preprocessor.fit(x_train)
    return preprocessor


def transform_tabular(
    df: pd.DataFrame, feature_cols: List[str], preprocessor: ColumnTransformer
) -> np.ndarray:
    arr = preprocessor.transform(df[feature_cols])
    if hasattr(arr, "toarray"):
        arr = arr.toarray()
    return np.asarray(arr, dtype=np.float32)


def _load_image_tensor(image_path: Path, transform, device: torch.device) -> torch.Tensor:
    with Image.open(image_path) as img:
        tensor = transform(img.convert("RGB")).unsqueeze(0).to(device)
    return tensor


def extract_resnet18_embeddings(
    df: pd.DataFrame,
    image_col: str = "image_path",
    device: torch.device | None = None,
) -> Tuple[np.ndarray, List[str]]:
    if device is None:
        if torch.backends.mps.is_available():
            device = torch.device("mps")
        elif torch.cuda.is_available():
            device = torch.device("cuda")
        else:
            device = torch.device("cpu")

    weights = ResNet18_Weights.IMAGENET1K_V1
    transform = weights.transforms()
    backbone = resnet18(weights=weights)
    backbone.fc = nn.Identity()
    backbone.to(device)
    backbone.eval()

    embs: List[np.ndarray] = []
    corrupted_ids: List[str] = []

    with torch.no_grad():
        for row in df.itertuples(index=False):
            image_path = Path(getattr(row, image_col))
            try:
                tensor = _load_image_tensor(image_path=image_path, transform=transform, device=device)
                emb = backbone(tensor).detach().cpu().numpy().reshape(-1)
            except Exception:
                emb = np.full((512,), np.nan, dtype=np.float32)
                corrupted_ids.append(str(row.ID))
            embs.append(emb.astype(np.float32))

    emb_arr = np.vstack(embs).astype(np.float32)
    col_medians = np.nanmedian(emb_arr, axis=0)
    nan_mask = np.isnan(emb_arr)
    emb_arr[nan_mask] = np.take(col_medians, np.where(nan_mask)[1])
    return emb_arr, corrupted_ids


def attach_split_labels(df: pd.DataFrame, split: SplitIndex) -> pd.DataFrame:
    out = df.copy()
    out["split"] = "train"
    out.loc[split.val_idx, "split"] = "val"
    out.loc[split.test_idx, "split"] = "test"
    return out


def summary_dict(df: pd.DataFrame) -> Dict[str, object]:
    return {
        "rows": int(len(df)),
        "specimens": int(df["specimen"].nunique()),
        "week_min": int(df["week"].min()),
        "week_max": int(df["week"].max()),
        "treatments": sorted(df["Treatment"].dropna().astype(str).unique().tolist()),
        "series": sorted(df["series"].dropna().astype(str).unique().tolist()),
    }


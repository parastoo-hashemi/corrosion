from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from PIL import Image

RUST_LOW = np.array([25, 0, 0], dtype=np.uint8)
RUST_HIGH = np.array([255, 100, 80], dtype=np.uint8)
BLACK_LOW = np.array([0, 0, 0], dtype=np.uint8)
BLACK_HIGH = np.array([5, 5, 0], dtype=np.uint8)
GRAY_LOW = np.array([60, 70, 35], dtype=np.uint8)
GRAY_HIGH = np.array([120, 105, 95], dtype=np.uint8)


def _mask_in_range(arr: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> np.ndarray:
    return np.all((arr >= lower) & (arr <= upper), axis=2)


def extract_image_features(image_path: Path) -> Tuple[Dict[str, float], bool, str]:
    """Extract compact, interpretable corrosion features from a single image."""
    features: Dict[str, float] = {}
    try:
        with Image.open(image_path) as img:
            rgb = np.array(img.convert("RGB"), dtype=np.uint8)
            hsv = np.array(img.convert("HSV"), dtype=np.uint8).astype(np.float32) / 255.0
    except Exception as exc:  # pragma: no cover - tested in training integration
        return (
            {
                "img_r_mean": np.nan,
                "img_g_mean": np.nan,
                "img_b_mean": np.nan,
                "img_r_std": np.nan,
                "img_g_std": np.nan,
                "img_b_std": np.nan,
                "img_h_mean": np.nan,
                "img_s_mean": np.nan,
                "img_v_mean": np.nan,
                "img_h_std": np.nan,
                "img_s_std": np.nan,
                "img_v_std": np.nan,
                "img_rg_diff_mean": np.nan,
                "img_red_dominance_pct": np.nan,
                "img_rust_mask_pct": np.nan,
                "img_black_mask_pct": np.nan,
                "img_gray_mask_pct": np.nan,
                "img_rust_to_black_ratio": np.nan,
            },
            True,
            str(exc),
        )

    rgbf = rgb.astype(np.float32) / 255.0
    r = rgbf[:, :, 0]
    g = rgbf[:, :, 1]
    b = rgbf[:, :, 2]

    rust_mask = _mask_in_range(rgb, RUST_LOW, RUST_HIGH)
    black_mask = _mask_in_range(rgb, BLACK_LOW, BLACK_HIGH)
    gray_mask = _mask_in_range(rgb, GRAY_LOW, GRAY_HIGH)
    rust_clean = rust_mask & (~black_mask) & (~gray_mask)

    features["img_r_mean"] = float(r.mean())
    features["img_g_mean"] = float(g.mean())
    features["img_b_mean"] = float(b.mean())
    features["img_r_std"] = float(r.std())
    features["img_g_std"] = float(g.std())
    features["img_b_std"] = float(b.std())

    features["img_h_mean"] = float(hsv[:, :, 0].mean())
    features["img_s_mean"] = float(hsv[:, :, 1].mean())
    features["img_v_mean"] = float(hsv[:, :, 2].mean())
    features["img_h_std"] = float(hsv[:, :, 0].std())
    features["img_s_std"] = float(hsv[:, :, 1].std())
    features["img_v_std"] = float(hsv[:, :, 2].std())

    features["img_rg_diff_mean"] = float((r - g).mean())
    features["img_red_dominance_pct"] = float((r > g + 0.05).mean())
    features["img_rust_mask_pct"] = float(rust_clean.mean())
    features["img_black_mask_pct"] = float(black_mask.mean())
    features["img_gray_mask_pct"] = float(gray_mask.mean())
    features["img_rust_to_black_ratio"] = float(
        features["img_rust_mask_pct"] / (features["img_black_mask_pct"] + 1e-6)
    )

    return features, False, ""


def build_image_feature_table(
    df: pd.DataFrame, cache_path: Path | None = None, force_recompute: bool = False
) -> Tuple[pd.DataFrame, List[str]]:
    """Build image features aligned with rows in the corrosion dataframe."""
    if cache_path and cache_path.exists() and not force_recompute:
        cached = pd.read_csv(cache_path)
        if {"ID", "image_corrupted"}.issubset(cached.columns):
            out = df[["ID"]].merge(cached, on="ID", how="left")
            corrupted_ids = (
                out.loc[out["image_corrupted"].fillna(False), "ID"].astype(str).tolist()
            )
            numeric_cols = [c for c in out.columns if c.startswith("img_")]
            out[numeric_cols] = out[numeric_cols].fillna(out[numeric_cols].median())
            return out, corrupted_ids

    rows = []
    corrupted_ids: List[str] = []
    for rec in df.itertuples(index=False):
        image_path = Path(rec.image_path)
        feats, corrupted, err = extract_image_features(image_path)
        row = {"ID": rec.ID, **feats, "image_corrupted": corrupted, "image_error": err}
        rows.append(row)
        if corrupted:
            corrupted_ids.append(str(rec.ID))

    feat_df = pd.DataFrame(rows)
    numeric_cols = [c for c in feat_df.columns if c.startswith("img_")]
    feat_df[numeric_cols] = feat_df[numeric_cols].fillna(feat_df[numeric_cols].median())

    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        feat_df.to_csv(cache_path, index=False)

    return feat_df, corrupted_ids


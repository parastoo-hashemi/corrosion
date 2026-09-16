from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

import joblib
import pandas as pd

from corrosion.classical_corrosion.data_utils import (
    COL_AGEING_DAYS,
    COL_COVER_MM,
    COL_N_MESH,
    COL_NACL,
    COL_TARGET_PEAK,
    COL_TREATMENT,
    DEFAULT_EXCEL_PATH,
    DEFAULT_IMAGE_DIR,
    dataset_summary,
    load_corrosion_dataframe,
)
from corrosion.classical_corrosion.image_features import build_image_feature_table
from corrosion.classical_corrosion.modeling import evaluate_models, get_feature_importance


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train corrosion ML models and save validated artifacts."
    )
    parser.add_argument(
        "--excel-path", type=Path, default=DEFAULT_EXCEL_PATH, help="Path to Excel file."
    )
    parser.add_argument(
        "--image-dir",
        type=Path,
        default=DEFAULT_IMAGE_DIR,
        help="Path to image dataset directory.",
    )
    parser.add_argument(
        "--artifacts-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "artifacts",
        help="Directory to save trained models and metadata.",
    )
    parser.add_argument(
        "--reports-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "reports",
        help="Directory to save benchmark tables and diagnostics.",
    )
    parser.add_argument(
        "--threshold-pct",
        type=float,
        default=20.0,
        help="Threshold percentage for severe corrosion timing target.",
    )
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument(
        "--force-image-recompute",
        action="store_true",
        help="Recompute all image features even if cache exists.",
    )
    return parser.parse_args()


def _create_time_to_threshold_dataset(
    df: pd.DataFrame, threshold_pct: float
) -> pd.DataFrame:
    rows: List[pd.DataFrame] = []
    for _, group in df.sort_values("week").groupby("specimen"):
        event = group.loc[group[COL_TARGET_PEAK] >= threshold_pct, "week"]
        if event.empty:
            continue
        event_week = float(event.iloc[0])
        local = group[group["week"] <= event_week].copy()
        local["remaining_weeks_to_threshold"] = event_week - local["week"].astype(float)
        rows.append(local)

    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def _save_task_outputs(
    task_name: str,
    benchmark,
    reports_dir: Path,
    artifacts_dir: Path,
    feature_columns: List[str],
) -> Dict[str, float | str]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    metrics_path = reports_dir / f"{task_name}_metrics.csv"
    benchmark.metrics.to_csv(metrics_path, index=False)

    model_path = artifacts_dir / f"{task_name}_model.joblib"
    joblib.dump(benchmark.best_pipeline, model_path)

    fi = get_feature_importance(
        benchmark.best_pipeline,
        benchmark.feature_names,
        top_k=35,
    )
    fi_path = reports_dir / f"{task_name}_feature_importance.csv"
    fi.to_csv(fi_path, index=False)

    return {
        "best_model": benchmark.best_model_name,
        "model_path": str(model_path.resolve()),
        "metrics_path": str(metrics_path.resolve()),
        "feature_importance_path": str(fi_path.resolve()),
        "n_features": len(feature_columns),
        "holdout_mae": benchmark.holdout_metrics["holdout_mae"],
        "holdout_rmse": benchmark.holdout_metrics["holdout_rmse"],
        "holdout_r2": benchmark.holdout_metrics["holdout_r2"],
    }


def main() -> None:
    args = parse_args()
    args.artifacts_dir.mkdir(parents=True, exist_ok=True)
    args.reports_dir.mkdir(parents=True, exist_ok=True)

    df = load_corrosion_dataframe(args.excel_path, args.image_dir)
    summary = dataset_summary(df)
    print(
        f"[INFO] Loaded data: rows={summary.n_rows}, specimens={summary.n_specimens}, "
        f"week_range={summary.week_min}-{summary.week_max}, "
        f"missing_images={summary.n_missing_images}"
    )

    image_cache_path = args.reports_dir / "image_features_cache.csv"
    image_feats, corrupted_ids = build_image_feature_table(
        df=df,
        cache_path=image_cache_path,
        force_recompute=args.force_image_recompute,
    )
    print(
        f"[INFO] Image features prepared. Corrupted images detected: {len(corrupted_ids)}"
    )

    full_df = df.merge(image_feats, on="ID", how="left")
    # In case cached rows miss these fields, enforce defaults.
    if "image_corrupted" not in full_df.columns:
        full_df["image_corrupted"] = False
    if "image_error" not in full_df.columns:
        full_df["image_error"] = ""

    base_features = [
        COL_N_MESH,
        COL_TREATMENT,
        COL_NACL,
        COL_AGEING_DAYS,
        COL_COVER_MM,
        "week",
        "series",
    ]
    image_feature_cols = [
        c for c in full_df.columns if c.startswith("img_") and c not in {"image_corrupted"}
    ]

    # Task main_first: Predict current corrosion amount using metadata + image features.
    current_features = base_features + image_feature_cols
    current_benchmark = evaluate_models(
        X=full_df[current_features],
        y=full_df[COL_TARGET_PEAK].astype(float),
        groups=full_df["specimen"].astype(str),
        random_state=args.random_state,
    )
    current_info = _save_task_outputs(
        task_name="current_corrosion",
        benchmark=current_benchmark,
        reports_dir=args.reports_dir,
        artifacts_dir=args.artifacts_dir,
        feature_columns=current_features,
    )
    print(
        "[INFO] current_corrosion -> "
        f"{current_info['best_model']} | MAE={current_info['holdout_mae']:.4f} | "
        f"R2={current_info['holdout_r2']:.4f}"
    )

    # Task 2: Predict corrosion progression by week using only metadata + week.
    progression_features = base_features
    progression_benchmark = evaluate_models(
        X=full_df[progression_features],
        y=full_df[COL_TARGET_PEAK].astype(float),
        groups=full_df["specimen"].astype(str),
        random_state=args.random_state,
    )
    progression_info = _save_task_outputs(
        task_name="progression",
        benchmark=progression_benchmark,
        reports_dir=args.reports_dir,
        artifacts_dir=args.artifacts_dir,
        feature_columns=progression_features,
    )
    print(
        "[INFO] progression -> "
        f"{progression_info['best_model']} | MAE={progression_info['holdout_mae']:.4f} | "
        f"R2={progression_info['holdout_r2']:.4f}"
    )

    # Task 3: Predict time-to-threshold using current corrosion state.
    time_df = _create_time_to_threshold_dataset(full_df, args.threshold_pct)
    if time_df.empty:
        raise RuntimeError(
            "No specimens reached the threshold; unable to train time-to-threshold model."
        )

    time_features = base_features + [COL_TARGET_PEAK]
    time_benchmark = evaluate_models(
        X=time_df[time_features],
        y=time_df["remaining_weeks_to_threshold"].astype(float),
        groups=time_df["specimen"].astype(str),
        random_state=args.random_state,
    )
    time_info = _save_task_outputs(
        task_name="time_to_threshold",
        benchmark=time_benchmark,
        reports_dir=args.reports_dir,
        artifacts_dir=args.artifacts_dir,
        feature_columns=time_features,
    )
    print(
        "[INFO] time_to_threshold -> "
        f"{time_info['best_model']} | MAE={time_info['holdout_mae']:.4f} | "
        f"R2={time_info['holdout_r2']:.4f}"
    )

    manifest = {
        "excel_path": str(args.excel_path.resolve()),
        "image_dir": str(args.image_dir.resolve()),
        "threshold_pct": args.threshold_pct,
        "random_state": args.random_state,
        "dataset": {
            "rows": summary.n_rows,
            "specimens": summary.n_specimens,
            "week_min": summary.week_min,
            "week_max": summary.week_max,
            "missing_images": summary.n_missing_images,
            "corrupted_image_ids": corrupted_ids,
        },
        "features": {
            "base_features": base_features,
            "image_features": image_feature_cols,
            "current_model_features": current_features,
            "progression_model_features": progression_features,
            "time_model_features": time_features,
        },
        "models": {
            "current_corrosion": current_info,
            "progression": progression_info,
            "time_to_threshold": time_info,
        },
    }
    manifest_path = args.artifacts_dir / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[INFO] Saved manifest: {manifest_path.resolve()}")


if __name__ == "__main__":
    main()

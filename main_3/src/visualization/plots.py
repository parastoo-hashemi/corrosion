from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.config import Settings
from src.features.image_processing import preprocess_image


sns.set_theme(style="whitegrid", context="talk")


def _save(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return path


def create_preprocessing_previews(
    canonical_df: pd.DataFrame,
    settings: Settings,
    output_dir: Path,
    limit: int,
) -> pd.DataFrame:
    output_dir.mkdir(parents=True, exist_ok=True)
    sample_idx = np.linspace(
        0, len(canonical_df) - 1, min(limit, len(canonical_df)), dtype=int
    )
    sample = canonical_df.iloc[sample_idx].copy()
    rows = []
    for row in sample.itertuples(index=False):
        processed = preprocess_image(Path(row.image_path), settings=settings)
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        axes[0].imshow(processed.roi_rgb)
        axes[0].set_title("ROI")
        axes[1].imshow(processed.normalized_rgb)
        axes[1].set_title("Normalized")
        axes[2].imshow(processed.normalized_rgb)
        axes[2].imshow(processed.rust_mask, cmap="Reds", alpha=0.35)
        axes[2].set_title("Rust mask")
        for axis in axes:
            axis.axis("off")
        out_path = _save(fig, output_dir / f"{row.record_id}.png")
        rows.append(
            {
                "record_id": row.record_id,
                "specimen_id": row.specimen_id,
                "week": row.week,
                "preview_path": str(out_path),
            }
        )
    return pd.DataFrame(rows)


def plot_regression_predictions(pred_df: pd.DataFrame, out_path: Path, title: str) -> Path:
    fig, ax = plt.subplots(figsize=(8, 8))
    sns.scatterplot(data=pred_df, x="y_true", y="y_pred", hue="model", ax=ax, s=60)
    lim = max(pred_df["y_true"].max(), pred_df["y_pred"].max()) * 1.05
    ax.plot([0, lim], [0, lim], "--", color="black", linewidth=1.0)
    ax.set_title(title)
    ax.set_xlabel("Observed")
    ax.set_ylabel("Predicted")
    return _save(fig, out_path)


def plot_metric_bars(metrics_df: pd.DataFrame, metric_col: str, out_path: Path, title: str) -> Path:
    grouped = (
        metrics_df.groupby(["model", "target"], as_index=False)[metric_col]
        .mean()
        .sort_values(metric_col, ascending=metric_col not in {"macro_f1", "accuracy"})
    )
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=grouped, x="model", y=metric_col, hue="target", ax=ax)
    ax.set_title(title)
    ax.set_ylabel(metric_col)
    ax.set_xlabel("Model")
    ax.tick_params(axis="x", rotation=15)
    return _save(fig, out_path)


def plot_risk_distribution(rul_df: pd.DataFrame, out_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.countplot(data=rul_df, x="risk_class", order=["Low", "Moderate", "High", "Critical"], ax=ax)
    ax.set_title("Specimen risk distribution")
    ax.set_xlabel("Risk class")
    ax.set_ylabel("Count")
    return _save(fig, out_path)


def plot_rul_histogram(rul_df: pd.DataFrame, out_path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(rul_df["estimated_rul_weeks"].dropna(), bins=20, kde=True, ax=ax)
    ax.set_title("Estimated proxy-RUL distribution")
    ax.set_xlabel("Weeks to threshold")
    return _save(fig, out_path)


def plot_trajectory_examples(
    trajectory_df: pd.DataFrame,
    out_path: Path,
    target: str,
    specimen_ids: list[str],
) -> Path:
    show = trajectory_df[
        (trajectory_df["target"] == target) & (trajectory_df["specimen_id"].isin(specimen_ids))
    ].copy()
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(
        data=show,
        x="week",
        y="forecast_value",
        hue="specimen_id",
        style="phase",
        ax=ax,
    )
    ax.set_title(f"Degradation trajectories: {target}")
    return _save(fig, out_path)

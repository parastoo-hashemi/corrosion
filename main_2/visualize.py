from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import confusion_matrix, mean_absolute_error

sns.set_theme(style="whitegrid", context="talk")


def _save(fig: plt.Figure, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return str(path.resolve())


def _class3(v: float) -> str:
    if v < 1.0:
        return "Low (<main_first%)"
    if v < 20.0:
        return "Medium (main_first-20%)"
    return "High (>=20%)"


def compute_group_metrics(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    rows = []
    for key, grp in df.groupby(group_col):
        mae = mean_absolute_error(grp["y_true"], grp["y_pred"])
        rmse = float(np.sqrt(np.mean((grp["y_true"] - grp["y_pred"]) ** 2)))
        rows.append(
            {
                group_col: key,
                "n": len(grp),
                "mae": mae,
                "rmse": rmse,
                "mean_true": float(grp["y_true"].mean()),
                "mean_pred": float(grp["y_pred"].mean()),
            }
        )
    return pd.DataFrame(rows).sort_values("mae")


def create_visualizations(
    pred_df: pd.DataFrame,
    figures_dir: Path,
    per_material_dir: Path,
    model_comparison: pd.DataFrame,
) -> Dict[str, str]:
    out: Dict[str, str] = {}
    figures_dir.mkdir(parents=True, exist_ok=True)
    per_material_dir.mkdir(parents=True, exist_ok=True)

    eval_df = pred_df[pred_df["split"] == "test"].copy()
    eval_df["residual"] = eval_df["y_pred"] - eval_df["y_true"]

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(pred_df["y_true"], bins=40, kde=True, ax=ax, color="#0c4a6e")
    ax.set_title("Target Distribution: Peak Rust Percentage")
    ax.set_xlabel("Peak rust percentage [%]")
    out["target_distribution"] = _save(fig, figures_dir / "01_target_distribution.png")

    fig, ax = plt.subplots(figsize=(8, 8))
    sns.scatterplot(data=eval_df, x="y_true", y="y_pred", hue="series", s=60, ax=ax)
    lim = max(eval_df["y_true"].max(), eval_df["y_pred"].max()) * 1.05
    ax.plot([0, lim], [0, lim], "--", color="black", linewidth=1.5)
    ax.set_title("Test Set: Predicted vs True")
    ax.set_xlabel("True peak rust [%]")
    ax.set_ylabel("Predicted peak rust [%]")
    out["pred_vs_true"] = _save(fig, figures_dir / "02_pred_vs_true_test.png")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(eval_df["residual"], bins=35, kde=True, ax=ax, color="#b45309")
    ax.axvline(0, color="black", linestyle="--")
    ax.set_title("Residual Distribution (Test)")
    ax.set_xlabel("Residual = prediction - true")
    out["residual_distribution"] = _save(fig, figures_dir / "03_residual_distribution.png")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=eval_df, x="week", y="residual", hue="series", s=55, ax=ax)
    ax.axhline(0, color="black", linestyle="--")
    ax.set_title("Residuals vs Week (Test)")
    out["residual_vs_week"] = _save(fig, figures_dir / "04_residual_vs_week.png")

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(data=model_comparison, x="model", y="test_mae", ax=ax, palette="crest")
    ax.set_title("Model Comparison (Test MAE)")
    ax.set_ylabel("MAE [%]")
    out["model_comparison"] = _save(fig, figures_dir / "05_model_comparison.png")

    by_treatment = compute_group_metrics(eval_df, "Treatment")
    by_series = compute_group_metrics(eval_df, "series")
    by_specimen = compute_group_metrics(eval_df, "specimen")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=by_treatment.sort_values("mae"), x="Treatment", y="mae", ax=ax, palette="mako")
    ax.set_title("Test MAE by Treatment")
    ax.set_ylabel("MAE [%]")
    out["mae_by_treatment"] = _save(fig, figures_dir / "06_mae_by_treatment.png")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=by_series.sort_values("mae"), x="series", y="mae", ax=ax, palette="viridis")
    ax.set_title("Test MAE by Series")
    ax.set_ylabel("MAE [%]")
    out["mae_by_series"] = _save(fig, figures_dir / "07_mae_by_series.png")

    agg_treat = (
        pred_df.groupby(["Treatment", "week"], as_index=False)[["y_true", "y_pred"]].mean()
    )
    fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)
    sns.lineplot(data=agg_treat, x="week", y="y_true", hue="Treatment", marker="o", ax=axes[0])
    axes[0].set_title("Average True Progression by Treatment")
    sns.lineplot(data=agg_treat, x="week", y="y_pred", hue="Treatment", marker="o", ax=axes[1])
    axes[1].set_title("Average Predicted Progression by Treatment")
    out["progression_by_treatment"] = _save(fig, figures_dir / "08_progression_by_treatment.png")

    agg_series = (
        pred_df.groupby(["series", "week"], as_index=False)[["y_true", "y_pred"]].mean()
    )
    fig, axes = plt.subplots(1, 2, figsize=(16, 6), sharey=True)
    sns.lineplot(data=agg_series, x="week", y="y_true", hue="series", marker="o", ax=axes[0])
    axes[0].set_title("Average True Progression by Series")
    sns.lineplot(data=agg_series, x="week", y="y_pred", hue="series", marker="o", ax=axes[1])
    axes[1].set_title("Average Predicted Progression by Series")
    out["progression_by_series"] = _save(fig, figures_dir / "09_progression_by_series.png")

    eval_df["class_true"] = eval_df["y_true"].map(_class3)
    eval_df["class_pred"] = eval_df["y_pred"].map(_class3)
    labels = ["Low (<main_first%)", "Medium (main_first-20%)", "High (>=20%)"]
    cm = confusion_matrix(eval_df["class_true"], eval_df["class_pred"], labels=labels)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels,
        ax=ax,
    )
    ax.set_title("Severity Confusion Matrix (3-level, Test)")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    out["severity_confusion"] = _save(fig, figures_dir / "10_severity_confusion_matrix.png")

    # One chart per material/specimen.
    material_paths: List[str] = []
    for specimen, grp in pred_df.groupby("specimen"):
        g = grp.sort_values("week")
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(g["week"], g["y_true"], marker="o", label="True", linewidth=2)
        ax.plot(g["week"], g["y_pred"], marker="x", label="Predicted", linewidth=2)
        ax.set_title(f"Material {specimen}: Corrosion Progression")
        ax.set_xlabel("Week")
        ax.set_ylabel("Peak rust [%]")
        ax.legend()
        material_paths.append(
            _save(fig, per_material_dir / f"{specimen}_progression.png")
        )
    out["per_material_count"] = str(len(material_paths))

    by_treatment.to_csv(figures_dir.parent / "metrics_by_treatment.csv", index=False)
    by_series.to_csv(figures_dir.parent / "metrics_by_series.csv", index=False)
    by_specimen.to_csv(figures_dir.parent / "metrics_by_specimen.csv", index=False)

    return out


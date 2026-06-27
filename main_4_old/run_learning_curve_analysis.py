from __future__ import annotations

import os
import sys

sys.path.insert(0, "src")

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from corrosion_proxy_rul.config import load_configs
from corrosion_proxy_rul.evaluation import (
    build_regression_models,
    fit_model_bundle,
    predict_model_bundle,
    regression_metrics,
)
from corrosion_proxy_rul.feature_engineering import get_model_feature_columns
from corrosion_proxy_rul.utils_paths import OUTPUT_DIR, configure_logging, ensure_dir, save_dataframe_csv

os.environ.setdefault("MPLCONFIGDIR", str(ensure_dir(OUTPUT_DIR / ".matplotlib")))

import matplotlib.pyplot as plt
import seaborn as sns


sns.set_theme(style="whitegrid")

LEARNING_FRACTIONS = [0.2, 0.4, 0.6, 0.8, 1.0]
FIGURE_ROOT = OUTPUT_DIR / "diagnostics" / "figures" / "learning_curves"
TABLE_ROOT = OUTPUT_DIR / "diagnostics" / "tables" / "learning_curves"

TARGET_LABELS = {
    "surface_total_rust_pct": "Surface total rust (%)",
    "peak_rust_pct": "Peak rust (%)",
    "wire_area_loss_frac": "Wire area loss fraction",
    "ultimate_load_kn": "Ultimate load (kN)",
}


@dataclass
class TargetSpec:
    stage: str
    target: str
    model_name: str
    target_transform: str
    feature_cols: list[str]
    feature_note: str
    df: pd.DataFrame
    manifest_df: pd.DataFrame


def _deterministic_group_sample(
    train_df: pd.DataFrame,
    group_col: str,
    fraction: float,
    random_seed: int,
) -> pd.DataFrame:
    groups = np.array(sorted(train_df[group_col].dropna().unique()))
    n_groups = len(groups)
    if n_groups == 0:
        return train_df.iloc[0:0].copy()
    n_select = min(n_groups, max(2, int(round(n_groups * fraction))))
    if n_select >= n_groups:
        return train_df.copy()
    rng = np.random.default_rng(random_seed)
    selected_groups = set(rng.choice(groups, size=n_select, replace=False).tolist())
    return train_df.loc[train_df[group_col].isin(selected_groups)].copy()


def _summarize_curve(raw_df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        raw_df.groupby(
            ["stage", "target", "model_name", "target_transform", "fraction"]
        )[
            [
                "n_train_rows",
                "n_train_groups",
                "train_mae",
                "test_mae",
                "train_rmse",
                "test_rmse",
                "train_r2",
                "test_r2",
                "train_spearman",
                "test_spearman",
            ]
        ]
        .agg(["mean", "std"])
        .reset_index()
    )
    summary.columns = [
        "_".join(column).strip("_") if isinstance(column, tuple) else column
        for column in summary.columns
    ]
    return summary


def _plot_target_curve(summary_df: pd.DataFrame, spec: TargetSpec, path: Path) -> None:
    ensure_dir(path.parent)
    plot_df = summary_df.copy()
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))

    metric_panels = [
        (
            axes[0],
            "mae",
            "Mean absolute error",
            "lower is better",
        ),
        (
            axes[1],
            "spearman",
            "Spearman correlation",
            "higher is better",
        ),
    ]

    for ax, metric_name, y_label, direction in metric_panels:
        for split_name, color in [("train", "#4C78A8"), ("test", "#E15759")]:
            mean_col = f"{split_name}_{metric_name}_mean"
            std_col = f"{split_name}_{metric_name}_std"
            metric_display = "MAE" if metric_name == "mae" else metric_name.capitalize()
            ax.plot(
                plot_df["fraction"],
                plot_df[mean_col],
                marker="o",
                linewidth=2.0,
                color=color,
                label=f"{split_name.title()} {metric_display}",
            )
            lower = plot_df[mean_col] - plot_df[std_col].fillna(0.0)
            upper = plot_df[mean_col] + plot_df[std_col].fillna(0.0)
            ax.fill_between(plot_df["fraction"], lower, upper, color=color, alpha=0.15)
        ax.set_xlabel("Fraction of available training specimens used")
        ax.set_ylabel(y_label)
        ax.set_title(f"{y_label} ({direction})")
        ax.set_xticks(LEARNING_FRACTIONS)
        ax.legend(loc="best")

    label = TARGET_LABELS.get(spec.target, spec.target)
    fig.suptitle(
        f"{label} learning curve\n{spec.stage.replace('_', ' ').title()} | {spec.model_name} | {spec.feature_note}",
        fontsize=13,
        y=1.03,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _plot_overview(summary_by_target: dict[str, pd.DataFrame], specs: list[TargetSpec], path: Path) -> None:
    ensure_dir(path.parent)
    n_rows = len(specs)
    fig, axes = plt.subplots(n_rows, 2, figsize=(13, 4.2 * n_rows), squeeze=False)

    for row_idx, spec in enumerate(specs):
        plot_df = summary_by_target[spec.target]
        for col_idx, (metric_name, y_label) in enumerate(
            [("mae", "MAE"), ("spearman", "Spearman")]
        ):
            ax = axes[row_idx, col_idx]
            for split_name, color in [("train", "#4C78A8"), ("test", "#E15759")]:
                mean_col = f"{split_name}_{metric_name}_mean"
                std_col = f"{split_name}_{metric_name}_std"
                ax.plot(
                    plot_df["fraction"],
                    plot_df[mean_col],
                    marker="o",
                    linewidth=1.8,
                    color=color,
                    label=split_name.title() if row_idx == 0 else None,
                )
                lower = plot_df[mean_col] - plot_df[std_col].fillna(0.0)
                upper = plot_df[mean_col] + plot_df[std_col].fillna(0.0)
                ax.fill_between(plot_df["fraction"], lower, upper, color=color, alpha=0.12)
            if row_idx == 0:
                ax.set_title(y_label)
            ax.set_xlabel("Training fraction")
            ax.set_ylabel(TARGET_LABELS.get(spec.target, spec.target))
            ax.set_xticks(LEARNING_FRACTIONS)
        axes[row_idx, 0].text(
            -0.35,
            0.5,
            f"{spec.stage.replace('_', ' ').title()}\n{spec.target}\n{spec.model_name}",
            transform=axes[row_idx, 0].transAxes,
            va="center",
            ha="left",
            fontsize=10,
        )

    handles, labels = axes[0, 0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.995), ncol=2, frameon=False)
    fig.suptitle("Learning curves for the repo's selected benchmark models", fontsize=14, y=1.035)
    fig.tight_layout(rect=[0.08, 0.02, 1, 0.98])
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _build_surface_specs(configs: dict) -> list[TargetSpec]:
    feature_df = pd.read_csv(OUTPUT_DIR / "models" / "surface" / "surface_feature_table.csv")
    manifest_df = pd.read_csv(OUTPUT_DIR / "models" / "surface" / "splits" / "group_shuffle.csv")
    best_df = pd.read_csv(OUTPUT_DIR / "models" / "surface" / "best_models.csv")

    specs: list[TargetSpec] = []
    for row in best_df.itertuples(index=False):
        target = row.target
        feature_cols = get_model_feature_columns(feature_df, target)
        specs.append(
            TargetSpec(
                stage="surface",
                target=target,
                model_name=row.best_model_name,
                target_transform="none",
                feature_cols=feature_cols,
                feature_note=row.benchmark_note,
                df=feature_df,
                manifest_df=manifest_df,
            )
        )
    return specs


def _build_hidden_specs(configs: dict) -> list[TargetSpec]:
    hidden_df = pd.read_csv(OUTPUT_DIR / "models" / "hidden_damage" / "hidden_damage_feature_table.csv")
    manifest_df = pd.read_csv(OUTPUT_DIR / "models" / "hidden_damage" / "splits" / "group_shuffle.csv")
    best_df = pd.read_csv(OUTPUT_DIR / "models" / "hidden_damage" / "best_models.csv")

    specs: list[TargetSpec] = []
    for row in best_df.itertuples(index=False):
        target = row.target
        features_path = OUTPUT_DIR / "models" / "hidden_damage" / target / f"{target}_selected_features.csv"
        feature_cols = pd.read_csv(features_path)["feature_name"].tolist()
        specs.append(
            TargetSpec(
                stage="hidden_damage",
                target=target,
                model_name=row.best_model_name,
                target_transform=row.target_transform,
                feature_cols=feature_cols,
                feature_note=row.feature_set_name,
                df=hidden_df,
                manifest_df=manifest_df,
            )
        )
    return specs


def _compute_learning_curve(spec: TargetSpec, modeling_cfg: dict, random_state: int) -> pd.DataFrame:
    model = build_regression_models(modeling_cfg)[spec.model_name]
    indexed = spec.df.set_index("sample_name", drop=False)
    rows: list[dict[str, object]] = []

    split_groups = list(spec.manifest_df.groupby("split_id"))
    for split_idx, (split_id, split_df) in enumerate(split_groups):
        train_names = split_df.loc[split_df["membership"] == "train", "sample_name"].tolist()
        test_names = split_df.loc[split_df["membership"] == "test", "sample_name"].tolist()
        train_full = indexed.loc[train_names].copy()
        test_df = indexed.loc[test_names].copy()

        for fraction_idx, fraction in enumerate(LEARNING_FRACTIONS):
            sampled_train = _deterministic_group_sample(
                train_full,
                group_col="specimen_id",
                fraction=fraction,
                random_seed=random_state + split_idx * 100 + fraction_idx,
            )
            bundle = fit_model_bundle(
                model,
                sampled_train[spec.feature_cols],
                sampled_train[spec.target],
                target_transform=spec.target_transform,
            )
            train_pred = predict_model_bundle(bundle, sampled_train[spec.feature_cols])
            test_pred = predict_model_bundle(bundle, test_df[spec.feature_cols])
            train_metrics = regression_metrics(sampled_train[spec.target], train_pred)
            test_metrics = regression_metrics(test_df[spec.target], test_pred)
            rows.append(
                {
                    "stage": spec.stage,
                    "target": spec.target,
                    "model_name": spec.model_name,
                    "target_transform": spec.target_transform,
                    "split_id": split_id,
                    "fraction": fraction,
                    "n_train_rows": int(len(sampled_train)),
                    "n_train_groups": int(sampled_train["specimen_id"].nunique()),
                    "train_mae": train_metrics["mae"],
                    "test_mae": test_metrics["mae"],
                    "train_rmse": train_metrics["rmse"],
                    "test_rmse": test_metrics["rmse"],
                    "train_r2": train_metrics["r2"],
                    "test_r2": test_metrics["r2"],
                    "train_spearman": train_metrics["spearman"],
                    "test_spearman": test_metrics["spearman"],
                }
            )

    return pd.DataFrame(rows)


def main() -> None:
    logger = configure_logging("run_learning_curve_analysis")
    configs = load_configs()
    modeling_cfg = configs["modeling"]
    random_state = int(modeling_cfg["random_state"])

    specs = _build_surface_specs(configs) + _build_hidden_specs(configs)
    all_raw_frames: list[pd.DataFrame] = []
    all_summary_frames: list[pd.DataFrame] = []
    summary_by_target: dict[str, pd.DataFrame] = {}

    for spec in specs:
        logger.info("Computing learning curve for %s / %s", spec.stage, spec.target)
        raw_df = _compute_learning_curve(spec, modeling_cfg, random_state)
        summary_df = _summarize_curve(raw_df)
        summary_by_target[spec.target] = summary_df

        target_table_dir = ensure_dir(TABLE_ROOT / spec.stage)
        target_figure_dir = ensure_dir(FIGURE_ROOT / spec.stage)
        raw_path = target_table_dir / f"{spec.target}_learning_curve_raw.csv"
        summary_path = target_table_dir / f"{spec.target}_learning_curve_summary.csv"
        figure_path = target_figure_dir / f"{spec.target}_learning_curve.png"

        save_dataframe_csv(raw_df, raw_path)
        save_dataframe_csv(summary_df, summary_path)
        _plot_target_curve(summary_df, spec, figure_path)

        logger.info("Saved %s", figure_path)
        all_raw_frames.append(raw_df)
        all_summary_frames.append(summary_df)

    combined_raw = pd.concat(all_raw_frames, ignore_index=True)
    combined_summary = pd.concat(all_summary_frames, ignore_index=True)
    save_dataframe_csv(combined_raw, TABLE_ROOT / "selected_models_learning_curve_raw.csv")
    save_dataframe_csv(combined_summary, TABLE_ROOT / "selected_models_learning_curve_summary.csv")

    overview_path = FIGURE_ROOT / "selected_models_learning_curves_overview.png"
    _plot_overview(summary_by_target, specs, overview_path)
    logger.info("Saved %s", overview_path)


if __name__ == "__main__":
    main()

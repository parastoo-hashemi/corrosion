from __future__ import annotations

import os
import sys

sys.path.insert(0, "src")

from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from corrosion_proxy_rul.config import load_configs
from corrosion_proxy_rul.utils_paths import OUTPUT_DIR, configure_logging, ensure_dir, save_dataframe_csv

os.environ.setdefault("MPLCONFIGDIR", str(ensure_dir(OUTPUT_DIR / ".matplotlib")))

import matplotlib.pyplot as plt
import seaborn as sns


sns.set_theme(style="whitegrid")

TARGET = "ultimate_load_kn"
STAGE = "hidden_damage"
MODEL_NAME = "RandomForest"

FIG_DIR = OUTPUT_DIR / "diagnostics" / "figures" / "model_diagnostics" / TARGET
TABLE_DIR = OUTPUT_DIR / "diagnostics" / "tables" / "model_diagnostics" / TARGET


def _encode_features(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    encoded = pd.get_dummies(df, dummy_na=False).astype(float)
    if columns is not None:
        encoded = encoded.reindex(columns=columns, fill_value=0.0)
    return encoded


def _fit_random_forest(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    random_state: int,
    model_cfg: dict,
) -> dict[str, object]:
    encoded_train = _encode_features(x_train)
    model = RandomForestRegressor(random_state=random_state, **model_cfg)
    model.fit(encoded_train, y_train.to_numpy(dtype=float))
    return {"model": model, "columns": list(encoded_train.columns)}


def _predict_with_uncertainty(bundle: dict[str, object], x_data: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    encoded = _encode_features(x_data, bundle["columns"])
    model: RandomForestRegressor = bundle["model"]  # type: ignore[assignment]
    encoded_values = encoded.to_numpy(dtype=float)
    tree_preds = np.column_stack([tree.predict(encoded_values) for tree in model.estimators_])
    mean_pred = tree_preds.mean(axis=1)
    std_pred = tree_preds.std(axis=1, ddof=1)
    return mean_pred, std_pred


def _regression_metrics(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, float]:
    spearman = spearmanr(y_true, y_pred).statistic
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)),
        "spearman": float(0.0 if np.isnan(spearman) else spearman),
    }


def _aggregate_encoded_importance(encoded_columns: list[str], values: np.ndarray, feature_cols: list[str]) -> pd.Series:
    rows = []
    for column, value in zip(encoded_columns, values):
        original_feature = column
        for feature in feature_cols:
            if column == feature or column.startswith(f"{feature}_"):
                original_feature = feature
                break
        rows.append({"feature_name": original_feature, "importance": float(value)})
    importance_df = pd.DataFrame(rows)
    aggregated = importance_df.groupby("feature_name", as_index=True)["importance"].sum()
    aggregated = aggregated.reindex(feature_cols, fill_value=0.0)
    return aggregated


def _load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, list[str], dict]:
    hidden_df = pd.read_csv(OUTPUT_DIR / "models" / "hidden_damage" / "hidden_damage_feature_table.csv")
    manifest_df = pd.read_csv(OUTPUT_DIR / "models" / "hidden_damage" / "splits" / "group_shuffle.csv")
    feature_cols = pd.read_csv(
        OUTPUT_DIR / "models" / "hidden_damage" / TARGET / f"{TARGET}_selected_features.csv"
    )["feature_name"].tolist()
    configs = load_configs()
    return hidden_df, manifest_df, feature_cols, configs


def _compute_cv_diagnostics(
    hidden_df: pd.DataFrame,
    manifest_df: pd.DataFrame,
    feature_cols: list[str],
    configs: dict,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    model_cfg = configs["modeling"]["models"]["random_forest"]
    random_state = int(configs["modeling"]["random_state"])
    indexed = hidden_df.set_index("sample_name", drop=False)

    prediction_rows: list[dict[str, object]] = []
    fold_metric_rows: list[dict[str, object]] = []
    importance_rows: list[dict[str, object]] = []

    for split_idx, (split_id, split_df) in enumerate(manifest_df.groupby("split_id")):
        train_names = split_df.loc[split_df["membership"] == "train", "sample_name"]
        test_names = split_df.loc[split_df["membership"] == "test", "sample_name"]
        train_df = indexed.loc[train_names].copy()
        test_df = indexed.loc[test_names].copy()

        bundle = _fit_random_forest(
            train_df[feature_cols],
            train_df[TARGET],
            random_state=random_state,
            model_cfg=model_cfg,
        )
        train_pred, train_std = _predict_with_uncertainty(bundle, train_df[feature_cols])
        test_pred, test_std = _predict_with_uncertainty(bundle, test_df[feature_cols])

        train_metrics = _regression_metrics(train_df[TARGET], train_pred)
        test_metrics = _regression_metrics(test_df[TARGET], test_pred)
        fold_metric_rows.append(
            {
                "split_id": split_id,
                "train_rows": int(len(train_df)),
                "test_rows": int(len(test_df)),
                "train_specimens": int(train_df["specimen_id"].nunique()),
                "test_specimens": int(test_df["specimen_id"].nunique()),
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

        interval_half_width = 1.96 * test_std
        lower = test_pred - interval_half_width
        upper = test_pred + interval_half_width
        for sample_name, specimen_id, y_true, y_pred, std_pred, low, high in zip(
            test_df["sample_name"],
            test_df["specimen_id"],
            test_df[TARGET],
            test_pred,
            test_std,
            lower,
            upper,
        ):
            residual = float(y_pred - y_true)
            prediction_rows.append(
                {
                    "split_id": split_id,
                    "sample_name": sample_name,
                    "specimen_id": specimen_id,
                    "y_true": float(y_true),
                    "y_pred": float(y_pred),
                    "residual": residual,
                    "abs_error": float(abs(residual)),
                    "pred_std": float(std_pred),
                    "pred_interval_low": float(low),
                    "pred_interval_high": float(high),
                    "covered_by_interval": bool(low <= y_true <= high),
                }
            )

        encoded_train = _encode_features(train_df[feature_cols], bundle["columns"])
        model: RandomForestRegressor = bundle["model"]  # type: ignore[assignment]
        fold_importance = _aggregate_encoded_importance(
            bundle["columns"],
            model.feature_importances_,
            feature_cols,
        )
        for feature_name, importance in fold_importance.items():
            importance_rows.append(
                {
                    "split_id": split_id,
                    "feature_name": feature_name,
                    "importance": float(importance),
                }
            )

    predictions_df = pd.DataFrame(prediction_rows)
    fold_metrics_df = pd.DataFrame(fold_metric_rows)
    importance_df = pd.DataFrame(importance_rows)
    return predictions_df, fold_metrics_df, importance_df


def _compute_feature_importance_summary(importance_df: pd.DataFrame) -> pd.DataFrame:
    return (
        importance_df.groupby("feature_name")
        .agg(
            importance_mean=("importance", "mean"),
            importance_std=("importance", "std"),
        )
        .reset_index()
        .sort_values("importance_mean", ascending=False)
        .reset_index(drop=True)
    )


def _compute_full_model_pdp(
    hidden_df: pd.DataFrame,
    feature_cols: list[str],
    configs: dict,
) -> pd.DataFrame:
    model_cfg = configs["modeling"]["models"]["random_forest"]
    random_state = int(configs["modeling"]["random_state"])
    bundle = _fit_random_forest(hidden_df[feature_cols], hidden_df[TARGET], random_state, model_cfg)

    rows: list[dict[str, object]] = []
    base_x = hidden_df[feature_cols].copy()
    for feature in feature_cols:
        series = base_x[feature]
        if pd.api.types.is_numeric_dtype(series):
            unique_values = np.sort(series.dropna().unique())
            if len(unique_values) <= 10:
                grid = unique_values.tolist()
            else:
                grid = np.quantile(series.dropna().to_numpy(dtype=float), np.linspace(0.05, 0.95, 12)).tolist()
                grid = sorted({float(value) for value in grid})
            for value in grid:
                varied = base_x.copy()
                varied[feature] = value
                preds, _std = _predict_with_uncertainty(bundle, varied)
                rows.append(
                    {
                        "feature_name": feature,
                        "feature_value": value,
                        "feature_value_label": str(round(float(value), 4)),
                        "prediction_mean": float(np.mean(preds)),
                        "feature_kind": "numeric",
                    }
                )
        else:
            categories = sorted(series.dropna().astype(str).unique().tolist())
            for category in categories:
                varied = base_x.copy()
                varied[feature] = category
                preds, _std = _predict_with_uncertainty(bundle, varied)
                rows.append(
                    {
                        "feature_name": feature,
                        "feature_value": category,
                        "feature_value_label": category,
                        "prediction_mean": float(np.mean(preds)),
                        "feature_kind": "categorical",
                    }
                )
    return pd.DataFrame(rows)


def _save_prediction_vs_truth(pred_df: pd.DataFrame, path: Path) -> None:
    ensure_dir(path.parent)
    fig, ax = plt.subplots(figsize=(7.5, 6))
    min_value = min(pred_df["y_true"].min(), pred_df["y_pred"].min())
    max_value = max(pred_df["y_true"].max(), pred_df["y_pred"].max())
    sns.scatterplot(data=pred_df, x="y_true", y="y_pred", hue="split_id", s=70, alpha=0.8, ax=ax)
    ax.plot([min_value, max_value], [min_value, max_value], linestyle="--", color="black", linewidth=1.3)
    mae = pred_df["abs_error"].mean()
    spearman = spearmanr(pred_df["y_true"], pred_df["y_pred"]).statistic
    ax.text(
        0.04,
        0.96,
        f"n = {len(pred_df)}\nMAE = {mae:.3f}\nSpearman = {spearman:.3f}",
        transform=ax.transAxes,
        va="top",
        ha="left",
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "edgecolor": "#CCCCCC"},
    )
    ax.set_title("Ultimate load: prediction vs ground truth\nGrouped CV test predictions")
    ax.set_xlabel("Observed ultimate load (kN)")
    ax.set_ylabel("Predicted ultimate load (kN)")
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _save_residual_analysis(pred_df: pd.DataFrame, path: Path) -> None:
    ensure_dir(path.parent)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    sns.scatterplot(
        data=pred_df,
        x="y_pred",
        y="residual",
        hue="split_id",
        s=65,
        alpha=0.75,
        ax=axes[0],
    )
    axes[0].axhline(0.0, linestyle="--", color="black", linewidth=1.2)
    axes[0].set_title("Residuals vs predicted")
    axes[0].set_xlabel("Predicted ultimate load (kN)")
    axes[0].set_ylabel("Predicted - observed (kN)")

    sns.boxplot(data=pred_df, x="split_id", y="residual", color="#F28E2B", ax=axes[1])
    sns.stripplot(data=pred_df, x="split_id", y="residual", color="black", alpha=0.45, size=3, ax=axes[1])
    axes[1].axhline(0.0, linestyle="--", color="black", linewidth=1.2)
    axes[1].set_title("Residual spread by grouped split")
    axes[1].set_xlabel("Split id")
    axes[1].set_ylabel("Predicted - observed (kN)")

    fig.suptitle("Ultimate load residual analysis", fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _save_error_histogram(pred_df: pd.DataFrame, path: Path) -> None:
    ensure_dir(path.parent)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    sns.histplot(pred_df["residual"], bins=16, kde=True, color="#4C78A8", ax=axes[0])
    axes[0].axvline(0.0, linestyle="--", color="black", linewidth=1.2)
    axes[0].set_title("Residual distribution")
    axes[0].set_xlabel("Predicted - observed (kN)")
    axes[0].set_ylabel("Count")

    sns.histplot(pred_df["abs_error"], bins=16, kde=True, color="#E15759", ax=axes[1])
    axes[1].set_title("Absolute error distribution")
    axes[1].set_xlabel("Absolute error (kN)")
    axes[1].set_ylabel("Count")

    fig.suptitle("Ultimate load error distribution", fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _save_partial_dependence(pdp_df: pd.DataFrame, path: Path, feature_cols: list[str]) -> None:
    ensure_dir(path.parent)
    n_features = len(feature_cols)
    n_cols = 4
    n_rows = int(np.ceil(n_features / n_cols))
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 4.2 * n_rows))
    axes = np.array(axes).reshape(n_rows, n_cols)

    for idx, feature in enumerate(feature_cols):
        ax = axes.flat[idx]
        sub = pdp_df.loc[pdp_df["feature_name"] == feature].copy()
        kind = sub["feature_kind"].iloc[0]
        if kind == "numeric":
            sub["feature_value_numeric"] = sub["feature_value"].astype(float)
            sns.lineplot(data=sub, x="feature_value_numeric", y="prediction_mean", marker="o", ax=ax, color="#4C78A8")
            ax.set_xlabel(feature)
        else:
            sns.barplot(data=sub, x="feature_value_label", y="prediction_mean", color="#F28E2B", ax=ax)
            ax.tick_params(axis="x", rotation=25)
            ax.set_xlabel(feature)
        ax.set_ylabel("Mean predicted ultimate load (kN)")
        ax.set_title(feature)

    for idx in range(n_features, n_rows * n_cols):
        axes.flat[idx].axis("off")

    fig.suptitle("Partial dependence plots for the selected ultimate-load model", fontsize=14, y=1.01)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _save_cv_stability(fold_df: pd.DataFrame, path: Path) -> None:
    ensure_dir(path.parent)
    order = sorted(fold_df["split_id"].tolist())
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    metrics = [
        ("test_mae", "Test MAE", "#4C78A8"),
        ("test_rmse", "Test RMSE", "#F28E2B"),
        ("test_r2", "Test R2", "#59A14F"),
        ("test_spearman", "Test Spearman", "#E15759"),
    ]
    for ax, (column, title, color) in zip(axes.flat, metrics):
        sns.lineplot(data=fold_df, x="split_id", y=column, marker="o", linewidth=2.0, color=color, sort=False, ax=ax)
        ax.set_title(title)
        ax.set_xlabel("Grouped split id")
        ax.set_ylabel(column.replace("test_", "").upper())
        ax.set_xticks(range(len(order)))
        ax.set_xticklabels(order, rotation=20)
    fig.suptitle("Cross-validation stability for the selected ultimate-load model", fontsize=14, y=1.01)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _save_feature_importance(importance_summary_df: pd.DataFrame, path: Path) -> None:
    ensure_dir(path.parent)
    plot_df = importance_summary_df.iloc[::-1].copy()
    fig, ax = plt.subplots(figsize=(9, max(4.5, len(plot_df) * 0.55)))
    sns.barplot(data=plot_df, x="importance_mean", y="feature_name", color="#4C78A8", ax=ax)
    ax.errorbar(
        x=plot_df["importance_mean"],
        y=np.arange(len(plot_df)),
        xerr=plot_df["importance_std"].fillna(0.0),
        fmt="none",
        ecolor="black",
        capsize=4,
    )
    ax.set_title("Feature importance for the selected ultimate-load model\n(mean +/- std across grouped CV folds)")
    ax.set_xlabel("Aggregated feature importance")
    ax.set_ylabel("Original feature")
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def _save_uncertainty_plot(pred_df: pd.DataFrame, path: Path) -> None:
    ensure_dir(path.parent)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    coverage = pred_df["covered_by_interval"].mean()
    interval = 1.96 * pred_df["pred_std"]
    axes[0].errorbar(
        pred_df["y_true"],
        pred_df["y_pred"],
        yerr=interval,
        fmt="o",
        ecolor="#9C755F",
        color="#4C78A8",
        alpha=0.65,
        elinewidth=1.0,
        capsize=2,
    )
    min_value = min(pred_df["y_true"].min(), pred_df["y_pred"].min())
    max_value = max(pred_df["y_true"].max(), pred_df["y_pred"].max())
    axes[0].plot([min_value, max_value], [min_value, max_value], linestyle="--", color="black", linewidth=1.2)
    axes[0].set_title(f"Prediction intervals from forest spread\nEmpirical coverage = {coverage:.2%}")
    axes[0].set_xlabel("Observed ultimate load (kN)")
    axes[0].set_ylabel("Predicted ultimate load (kN)")

    sns.regplot(
        data=pred_df,
        x="pred_std",
        y="abs_error",
        scatter_kws={"s": 60, "alpha": 0.7, "color": "#E15759"},
        line_kws={"color": "black", "linewidth": 1.3},
        ci=None,
        ax=axes[1],
    )
    axes[1].set_title("Model spread vs realized absolute error")
    axes[1].set_xlabel("Prediction std across trees")
    axes[1].set_ylabel("Absolute error (kN)")

    fig.suptitle("Ultimate-load uncertainty visualization", fontsize=14, y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    logger = configure_logging("run_ultimate_load_diagnostic_plots")
    hidden_df, manifest_df, feature_cols, configs = _load_inputs()
    predictions_df, fold_metrics_df, importance_df = _compute_cv_diagnostics(
        hidden_df, manifest_df, feature_cols, configs
    )
    importance_summary_df = _compute_feature_importance_summary(importance_df)
    pdp_df = _compute_full_model_pdp(hidden_df, feature_cols, configs)

    save_dataframe_csv(predictions_df, TABLE_DIR / "group_shuffle_predictions_with_uncertainty.csv")
    save_dataframe_csv(fold_metrics_df, TABLE_DIR / "group_shuffle_fold_metrics_selected_model.csv")
    save_dataframe_csv(importance_df, TABLE_DIR / "group_shuffle_feature_importance_by_fold.csv")
    save_dataframe_csv(importance_summary_df, TABLE_DIR / "group_shuffle_feature_importance_summary.csv")
    save_dataframe_csv(pdp_df, TABLE_DIR / "partial_dependence_values.csv")

    _save_prediction_vs_truth(predictions_df, FIG_DIR / "prediction_vs_ground_truth.png")
    _save_residual_analysis(predictions_df, FIG_DIR / "residual_analysis.png")
    _save_error_histogram(predictions_df, FIG_DIR / "error_distribution_histogram.png")
    _save_partial_dependence(pdp_df, FIG_DIR / "partial_dependence_plots.png", feature_cols)
    _save_cv_stability(fold_metrics_df, FIG_DIR / "cross_validation_stability.png")
    _save_feature_importance(importance_summary_df, FIG_DIR / "feature_importance.png")
    _save_uncertainty_plot(predictions_df, FIG_DIR / "uncertainty_visualization.png")

    logger.info("Saved diagnostic plots for %s to %s", TARGET, FIG_DIR)


if __name__ == "__main__":
    main()

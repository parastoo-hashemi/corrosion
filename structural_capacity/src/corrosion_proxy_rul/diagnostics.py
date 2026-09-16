from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

from .feature_engineering import EXCLUDE_FOR_MODELING, MODELING_QC_EXCLUSIONS, get_model_feature_columns
from .utils_paths import OUTPUT_DIR, ROOT_DIR, ensure_dir, save_dataframe_csv, write_text

os.environ.setdefault("MPLCONFIGDIR", str(ensure_dir(OUTPUT_DIR / ".matplotlib")))

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
import seaborn as sns


sns.set_theme(style="whitegrid")


DIAGNOSTICS_DIR = OUTPUT_DIR / "diagnostics"
DIAG_TABLE_DIR = DIAGNOSTICS_DIR / "tables"
DIAG_FIG_DIR = DIAGNOSTICS_DIR / "figures"

FEATURE_FIG_DIR = DIAG_FIG_DIR / "features"
DISTRIBUTION_FIG_DIR = DIAG_FIG_DIR / "distributions"
TEMPORAL_FIG_DIR = DIAG_FIG_DIR / "temporal"
BENCHMARK_FIG_DIR = DIAG_FIG_DIR / "benchmarks"
BENCHMARK_IMPORTANCE_FIG_DIR = BENCHMARK_FIG_DIR / "feature_importance"
BENCHMARK_PREDICTION_FIG_DIR = BENCHMARK_FIG_DIR / "predictions"
DEGRADATION_FIG_DIR = DIAG_FIG_DIR / "degradation"
PROXY_FIG_DIR = DIAG_FIG_DIR / "proxy"
INVENTORY_FIG_DIR = DIAG_FIG_DIR / "inventory"


SELECTED_DISTRIBUTION_VARIABLES = {
    "surface_total_rust_pct": "Surface total rust (%)",
    "peak_rust_pct": "Peak rust (%)",
    "peak_rust_location_cm": "Peak rust location (cm)",
    "wire_area_loss_frac": "Wire area loss (fraction)",
    "ultimate_load_kn": "Ultimate load (kN)",
    "img_rust_area_ratio_pct": "Image rust area ratio (%)",
    "img_strip_rust_max_pct": "Image peak strip rust (%)",
    "img_strip_peak_location_cm": "Image peak strip location (cm)",
    "img_brightness_mean": "Brightness mean",
    "img_rust_blob_count": "Rust blob count",
    "img_edge_to_center_rust_ratio": "Edge/center rust ratio",
    "predicted_wire_area_loss_frac": "Predicted hidden damage (fraction)",
}

SKEWED_READABILITY_VARIABLES = [
    "img_rust_blob_count",
    "img_edge_to_center_rust_ratio",
    "img_strip_rust_max_pct",
    "img_rust_area_ratio_pct",
    "predicted_wire_area_loss_frac",
]

IMAGE_HEATMAP_FEATURES = [
    "img_rust_area_ratio_pct",
    "img_black_mask_ratio_pct",
    "img_gray_mask_ratio_pct",
    "img_brightness_mean",
    "img_brightness_std",
    "img_gray_hist_bin_2",
    "img_glcm_contrast",
    "img_lbp_mean",
    "img_rust_blob_count",
    "img_rust_blob_largest_ratio_pct",
    "img_strip_rust_mean_pct",
    "img_strip_peak_location_cm",
]

TABULAR_HEATMAP_FEATURES = [
    "week",
    "ageing_days",
    "n_steel_mesh",
    "nacl_pct",
    "cover_mm",
    "terminal_week",
    "terminal_days",
]

TARGET_COLUMNS = [
    "surface_total_rust_pct",
    "peak_rust_pct",
    "wire_area_loss_frac",
    "ultimate_load_kn",
]


def dataframe_to_markdown(df: pd.DataFrame, index: bool = False) -> str:
    try:
        return df.to_markdown(index=index)
    except ImportError:
        return df.to_string(index=index)


def save_figure(path: Path, dpi: int = 180) -> None:
    ensure_dir(path.parent)
    plt.tight_layout()
    plt.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close()


def feature_family(column: str) -> str:
    if column.startswith("img_gray_hist_bin_"):
        return "image_histogram"
    if column.startswith("img_glcm_") or column.startswith("img_lbp_"):
        return "image_texture"
    if column.startswith("img_rust_blob_"):
        return "image_morphology"
    if column.startswith("img_strip_") or column.startswith("img_rust_center_of_mass") or column.startswith("img_edge_to_center"):
        return "image_spatial"
    if column.startswith("img_rust_area") or column.endswith("_mask_ratio_pct"):
        return "image_mask"
    if column.startswith("img_brightness") or column.startswith("img_contrast") or column.startswith("img_r_") or column.startswith("img_g_") or column.startswith("img_b_"):
        return "image_color"
    if column in {"week", "ageing_days", "terminal_week", "terminal_days"}:
        return "temporal"
    if column in {
        "campaign_id",
        "series_id",
        "split_group_treatment",
        "treatment_protocol",
        "treatment_coarse",
        "treatment_label_coarse",
        "n_steel_mesh",
        "nacl_pct",
        "cover_mm",
    }:
        return "tabular_metadata"
    if column.endswith("_raw"):
        return "raw_source"
    if column in TARGET_COLUMNS or column.endswith("_category"):
        return "target"
    if column in {
        "sample_name",
        "specimen_id",
        "image_filename",
        "image_path",
        "image_readable",
        "image_error",
        "image_width",
        "image_height",
        "specimen_id_from_name",
        "calendar_date",
        "date",
        "observation_id",
        "has_structural_label",
        "is_terminal_structural_row",
    }:
        return "identifier_or_flag"
    return "other"


def select_collinearity_pairs_for_plot(
    collinearity_df: pd.DataFrame,
    top_n: int = 15,
) -> tuple[pd.DataFrame, str]:
    if collinearity_df.empty:
        return collinearity_df.copy(), "Top high-collinearity feature pairs (|Spearman| >= 0.95)"

    ranked = collinearity_df.copy()
    if "left_family" not in ranked.columns:
        ranked["left_family"] = ranked["left_feature"].map(feature_family)
    if "right_family" not in ranked.columns:
        ranked["right_family"] = ranked["right_feature"].map(feature_family)

    ranked["is_image_pair"] = (
        ranked["left_family"].fillna("").str.startswith("image_")
        & ranked["right_family"].fillna("").str.startswith("image_")
    )
    ranked = ranked.sort_values(
        ["is_image_pair", "spearman_abs_corr", "left_feature", "right_feature"],
        ascending=[False, False, True, True],
    ).reset_index(drop=True)

    image_pairs = ranked.loc[ranked["is_image_pair"]].copy()
    if len(image_pairs) >= top_n:
        return (
            image_pairs.head(top_n).copy(),
            "Top image-feature collinearity pairs (|Spearman| >= 0.95)",
        )

    return (
        ranked.head(top_n).copy(),
        "Top high-collinearity feature pairs (image pairs prioritized; |Spearman| >= 0.95)",
    )


def exclusion_reason(column: str, target_col: str) -> str:
    if column == target_col:
        return "stage target"
    if column in MODELING_QC_EXCLUSIONS:
        return MODELING_QC_EXCLUSIONS[column]
    if column.endswith("_raw"):
        return "raw source column"
    if column in TARGET_COLUMNS:
        return "target column for another stage"
    if column.endswith("_category"):
        return "categorical target label"
    if column in {
        "sample_name",
        "specimen_id",
        "image_filename",
        "image_path",
        "image_readable",
        "image_error",
        "image_width",
        "image_height",
        "specimen_id_from_name",
        "calendar_date",
        "date",
        "observation_id",
    }:
        return "identifier or file metadata"
    if column in {"has_structural_label", "is_terminal_structural_row"}:
        return "label-availability flag"
    if column in {"terminal_week", "terminal_days"}:
        return "terminal-only metadata"
    if column in EXCLUDE_FOR_MODELING:
        return "excluded by modeling rules"
    return "not used in this stage"


def stage_feature_inventory(
    stage: str,
    df: pd.DataFrame,
    target_col: str,
    included_override: set[str] | None = None,
) -> pd.DataFrame:
    included = included_override if included_override is not None else set(get_model_feature_columns(df, target_col))
    rows = []
    for column in df.columns:
        series = df[column]
        numeric = pd.api.types.is_numeric_dtype(series)
        rows.append(
            {
                "stage": stage,
                "feature_name": column,
                "source_family": feature_family(column),
                "data_type": str(series.dtype),
                "missing_count": int(series.isna().sum()),
                "missing_fraction": float(series.isna().mean()),
                "nunique": int(series.nunique(dropna=True)),
                "variance": float(series.var(ddof=1)) if numeric else np.nan,
                "top_value_fraction": float(series.value_counts(dropna=False, normalize=True).iloc[0]),
                "included_in_stage": column in included,
                "exclusion_reason": "" if column in included else exclusion_reason(column, target_col),
            }
        )
    return pd.DataFrame(rows)


def build_feature_diagnostic_tables(full_feature_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    surface_inventory = stage_feature_inventory("surface", full_feature_df, "surface_total_rust_pct")
    hidden_selected_path = OUTPUT_DIR / "models" / "hidden_damage" / "hidden_damage_selected_feature_list.csv"
    hidden_selected = None
    if hidden_selected_path.exists():
        hidden_selected = set(pd.read_csv(hidden_selected_path)["feature_name"].tolist())
    hidden_inventory = stage_feature_inventory(
        "hidden_damage",
        full_feature_df.loc[full_feature_df["has_structural_label"]].copy(),
        "wire_area_loss_frac",
        included_override=hidden_selected,
    )
    inventory_df = pd.concat([surface_inventory, hidden_inventory], ignore_index=True)

    missingness_df = inventory_df[
        ["stage", "feature_name", "source_family", "missing_count", "missing_fraction"]
    ].copy()
    variance_df = inventory_df[
        [
            "stage",
            "feature_name",
            "source_family",
            "data_type",
            "variance",
            "nunique",
            "top_value_fraction",
            "included_in_stage",
        ]
    ].copy()
    near_constant_df = variance_df.loc[
        (variance_df["nunique"] <= 1) | (variance_df["top_value_fraction"] >= 0.95)
    ].sort_values(["stage", "top_value_fraction", "variance"], ascending=[True, False, True])

    duplicate_rows = []
    numeric_df = full_feature_df.select_dtypes(include="number")
    numeric_cols = [col for col in numeric_df.columns if feature_family(col).startswith(("image", "tabular", "temporal"))]
    for idx, left in enumerate(numeric_cols):
        for right in numeric_cols[idx + 1 :]:
            if numeric_df[left].equals(numeric_df[right]):
                duplicate_rows.append(
                    {
                        "left_feature": left,
                        "right_feature": right,
                        "duplicate_type": "exact_duplicate",
                    }
                )
    duplicate_df = pd.DataFrame(
        duplicate_rows,
        columns=["left_feature", "right_feature", "duplicate_type"],
    )

    collinearity_rows = []
    candidate_numeric = [
        col
        for col in numeric_cols
        if feature_family(col).startswith(("image", "tabular", "temporal"))
        and col not in TARGET_COLUMNS
    ]
    corr = full_feature_df[candidate_numeric].corr(method="spearman")
    for idx, left in enumerate(candidate_numeric):
        for right in candidate_numeric[idx + 1 :]:
            value = corr.loc[left, right]
            if np.isfinite(value) and abs(value) >= 0.95:
                collinearity_rows.append(
                    {
                        "left_feature": left,
                        "right_feature": right,
                        "left_family": feature_family(left),
                        "right_family": feature_family(right),
                        "spearman_abs_corr": float(abs(value)),
                        "spearman_corr": float(value),
                    }
                )
    collinearity_df = pd.DataFrame(
        collinearity_rows,
        columns=[
            "left_feature",
            "right_feature",
            "left_family",
            "right_family",
            "spearman_abs_corr",
            "spearman_corr",
        ],
    )
    if not collinearity_df.empty:
        collinearity_df = collinearity_df.sort_values(
            ["spearman_abs_corr", "left_feature", "right_feature"],
            ascending=[False, True, True],
        )

    corr_rows = []
    for target in TARGET_COLUMNS:
        valid_df = full_feature_df if target in {"surface_total_rust_pct", "peak_rust_pct"} else full_feature_df.loc[full_feature_df[target].notna()].copy()
        for feature in candidate_numeric:
            valid = valid_df[[feature, target]].dropna()
            if len(valid) < 5:
                corr_value = np.nan
            else:
                corr_value = valid[feature].corr(valid[target], method="spearman")
            corr_rows.append(
                {
                    "target": target,
                    "feature_name": feature,
                    "source_family": feature_family(feature),
                    "n_valid": int(len(valid)),
                    "spearman_corr": float(corr_value) if pd.notna(corr_value) else np.nan,
                    "spearman_abs_corr": float(abs(corr_value)) if pd.notna(corr_value) else np.nan,
                }
            )
    feature_target_corr_df = pd.DataFrame(corr_rows).sort_values(
        ["target", "spearman_abs_corr"], ascending=[True, False]
    )

    return {
        "feature_inventory_by_stage": inventory_df,
        "feature_missingness_summary": missingness_df,
        "feature_variance_summary": variance_df,
        "near_constant_features": near_constant_df,
        "duplicate_feature_pairs": duplicate_df,
        "high_collinearity_pairs": collinearity_df,
        "feature_target_correlation_summary": feature_target_corr_df,
    }


def build_distribution_tables(full_feature_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    rows = []
    pct_rows = []
    outlier_rows = []
    for column, label in SELECTED_DISTRIBUTION_VARIABLES.items():
        if column not in full_feature_df.columns:
            continue
        series = full_feature_df[column].dropna().astype(float)
        if series.empty:
            continue
        rows.append(
            {
                "variable": column,
                "label": label,
                "count": int(series.count()),
                "mean": float(series.mean()),
                "std": float(series.std()),
                "min": float(series.min()),
                "q25": float(series.quantile(0.25)),
                "median": float(series.median()),
                "q75": float(series.quantile(0.75)),
                "p95": float(series.quantile(0.95)),
                "p99": float(series.quantile(0.99)),
                "max": float(series.max()),
            }
        )
        for percentile in [0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]:
            pct_rows.append(
                {
                    "variable": column,
                    "label": label,
                    "percentile": percentile,
                    "value": float(series.quantile(percentile)),
                }
            )
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        upper_fence = q3 + 1.5 * iqr
        outlier_rows.append(
            {
                "variable": column,
                "label": label,
                "iqr_upper_fence": float(upper_fence),
                "n_iqr_outliers": int((series > upper_fence).sum()),
                "n_above_p99": int((series > series.quantile(0.99)).sum()),
                "p99_value": float(series.quantile(0.99)),
                "max_value": float(series.max()),
            }
        )
    return {
        "variable_distribution_summary": pd.DataFrame(rows),
        "variable_percentile_summary": pd.DataFrame(pct_rows),
        "outlier_summary": pd.DataFrame(outlier_rows),
    }


def representative_specimens(master_df: pd.DataFrame) -> list[str]:
    specimen_summary = (
        master_df.sort_values("ageing_days")
        .groupby(["campaign_id", "specimen_id"], as_index=False)
        .agg(final_surface_total_rust_pct=("surface_total_rust_pct", "last"))
    )
    selected = []
    for campaign_id, campaign_df in specimen_summary.groupby("campaign_id"):
        campaign_df = campaign_df.sort_values("final_surface_total_rust_pct").reset_index(drop=True)
        for idx in [0, len(campaign_df) // 2, len(campaign_df) - 1]:
            specimen_id = campaign_df.iloc[idx]["specimen_id"]
            if specimen_id not in selected:
                selected.append(specimen_id)
    return selected


def build_exposure_band_summary(master_df: pd.DataFrame) -> pd.DataFrame:
    bins = [-np.inf, master_df["ageing_days"].quantile(1 / 3), master_df["ageing_days"].quantile(2 / 3), np.inf]
    labels = ["early_exposure", "mid_exposure", "late_exposure"]
    working = master_df.copy()
    working["exposure_band"] = pd.cut(working["ageing_days"], bins=bins, labels=labels)
    summary = (
        working.groupby("exposure_band")[
            ["surface_total_rust_pct", "peak_rust_pct", "img_rust_area_ratio_pct"]
        ]
        .agg(["median", "mean", "count"])
        .reset_index()
    )
    summary.columns = [
        "_".join(col).strip("_") if isinstance(col, tuple) else col for col in summary.columns
    ]
    return working, summary


def load_summary_long() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summary_rows = []
    fold_rows = []
    split_rows = []

    for stage in ["surface", "hidden_damage"]:
        stage_dir = OUTPUT_DIR / "models" / stage
        for path in stage_dir.rglob("*_summary.csv"):
            rel = path.relative_to(stage_dir)
            if len(rel.parts) < 2:
                continue
            if "experiments" in rel.parts:
                continue
            df = pd.read_csv(path)
            if rel.parts[0] == "splits":
                temp = df.copy()
                temp["stage"] = stage
                split_rows.append(temp)
                continue
            target, strategy = rel.parts[0], rel.parts[1]
            temp = df.copy()
            temp["stage"] = stage
            temp["target"] = target
            temp["strategy"] = strategy
            summary_rows.append(temp)
        for path in stage_dir.rglob("*_fold_metrics.csv"):
            rel = path.relative_to(stage_dir)
            if len(rel.parts) < 2:
                continue
            if "experiments" in rel.parts:
                continue
            target, strategy = rel.parts[0], rel.parts[1]
            temp = pd.read_csv(path)
            temp["stage"] = stage
            temp["target"] = target
            temp["strategy"] = strategy
            fold_rows.append(temp)

    for path in OUTPUT_DIR.glob("splits/*_summary.csv"):
        temp = pd.read_csv(path)
        temp["stage"] = "master"
        split_rows.append(temp)

    summary_df = pd.concat(summary_rows, ignore_index=True).sort_values(
        ["stage", "target", "strategy", "mae_mean"]
    )
    fold_df = pd.concat(fold_rows, ignore_index=True).sort_values(
        ["stage", "target", "strategy", "model_name", "split_id"]
    )
    split_df = pd.concat(split_rows, ignore_index=True).sort_values(
        ["stage", "strategy", "split_id"]
    )
    return summary_df, fold_df, split_df


def build_best_model_robustness(summary_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for stage in ["surface", "hidden_damage"]:
        stage_summary = summary_df.loc[summary_df["stage"] == stage].copy()
        group_best = (
            stage_summary.loc[stage_summary["strategy"] == "group_shuffle"]
            .sort_values(["target", "mae_mean"])
            .groupby("target", as_index=False)
            .first()[["target", "model_name", "mae_mean", "spearman_mean"]]
            .rename(columns={"model_name": "best_model_name", "mae_mean": "group_shuffle_mae_mean"})
        )
        for row in group_best.itertuples(index=False):
            matching = stage_summary.loc[
                (stage_summary["target"] == row.target)
                & (stage_summary["model_name"] == row.best_model_name)
            ].copy()
            if matching.empty:
                continue
            base_mae = matching.loc[matching["strategy"] == "group_shuffle", "mae_mean"].iloc[0]
            for match in matching.itertuples(index=False):
                rows.append(
                    {
                        "stage": stage,
                        "target": match.target,
                        "best_model_name": row.best_model_name,
                        "strategy": match.strategy,
                        "mae_mean": match.mae_mean,
                        "mae_std": match.mae_std,
                        "spearman_mean": match.spearman_mean,
                        "spearman_std": match.spearman_std,
                        "relative_mae_vs_group_shuffle": float(match.mae_mean / base_mae)
                        if base_mae
                        else np.nan,
                    }
                )
    return pd.DataFrame(rows)


def build_degradation_tables() -> dict[str, pd.DataFrame]:
    working_df = pd.read_csv(OUTPUT_DIR / "models" / "degradation" / "full_feature_table_with_hidden_damage_proxy.csv")
    best_df = pd.read_csv(OUTPUT_DIR / "models" / "degradation" / "degradation_best_fits.csv")
    candidate_df = pd.read_csv(OUTPUT_DIR / "models" / "degradation" / "degradation_fit_candidates.csv")
    grid_df = pd.read_csv(OUTPUT_DIR / "models" / "degradation" / "degradation_trajectory_grid.csv")
    raw_monotone_path = OUTPUT_DIR / "models" / "degradation" / "degradation_raw_vs_monotone_proxy.csv"
    raw_monotone_df = pd.read_csv(raw_monotone_path) if raw_monotone_path.exists() else pd.DataFrame()

    observed_vs_fitted = (
        working_df[["sample_name", "specimen_id", "campaign_id", "split_group_treatment", "ageing_days", "predicted_wire_area_loss_frac"]]
        .merge(
            grid_df.rename(columns={"day": "ageing_days", "predicted_wire_area_loss_frac": "fitted_wire_area_loss_frac"}),
            on=["specimen_id", "ageing_days"],
            how="left",
            validate="many_to_one",
        )
    )
    observed_vs_fitted["residual"] = (
        observed_vs_fitted["predicted_wire_area_loss_frac"] - observed_vs_fitted["fitted_wire_area_loss_frac"]
    )

    fit_quality = (
        candidate_df.loc[candidate_df["fit_succeeded"]]
        .groupby("family", as_index=False)
        .agg(
            n_success=("fit_succeeded", "sum"),
            rmse_mean=("rmse", "mean"),
            rmse_median=("rmse", "median"),
            rmse_max=("rmse", "max"),
            criterion_mean=("criterion", "mean"),
        )
        .sort_values("rmse_mean")
    )

    mapping = working_df[["specimen_id", "campaign_id", "split_group_treatment"]].drop_duplicates()
    grouped_campaign = (
        grid_df.merge(mapping, on="specimen_id", how="left")
        .groupby(["campaign_id", "day"], as_index=False)["predicted_wire_area_loss_frac"]
        .median()
    )
    grouped_treatment = (
        grid_df.merge(mapping, on="specimen_id", how="left")
        .groupby(["split_group_treatment", "day"], as_index=False)["predicted_wire_area_loss_frac"]
        .median()
    )

    return {
        "degradation_observed_vs_fitted": observed_vs_fitted,
        "degradation_fit_quality_summary": fit_quality,
        "degradation_grouped_by_campaign": grouped_campaign,
        "degradation_grouped_by_treatment": grouped_treatment,
        "degradation_best_fits": best_df,
        "degradation_candidates": candidate_df,
        "degradation_grid": grid_df,
        "degradation_raw_vs_monotone_proxy": raw_monotone_df,
    }


def build_proxy_tables() -> dict[str, pd.DataFrame]:
    proxy_df = pd.read_csv(OUTPUT_DIR / "models" / "proxy_rul" / "proxy_rul_estimates.csv")
    summary_df = pd.read_csv(OUTPUT_DIR / "models" / "proxy_rul" / "proxy_rul_summary.csv")
    status_matrix = (
        proxy_df.pivot(index="specimen_id", columns="threshold_wire_area_loss_frac", values="threshold_status")
        .reset_index()
    )
    return {
        "proxy_estimates": proxy_df,
        "proxy_status_summary": summary_df,
        "proxy_status_matrix": status_matrix,
    }


def write_csv_bundle(bundle: dict[str, pd.DataFrame]) -> None:
    for name, df in bundle.items():
        save_dataframe_csv(df, DIAG_TABLE_DIR / f"{name}.csv")


def plot_feature_inventory(inventory_df: pd.DataFrame) -> list[str]:
    created = []
    counts = (
        inventory_df.groupby(["stage", "source_family", "included_in_stage"])
        .size()
        .reset_index(name="feature_count")
    )
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    sns.barplot(
        data=counts.loc[counts["included_in_stage"]],
        x="stage",
        y="feature_count",
        hue="source_family",
        ax=axes[0],
    )
    axes[0].set_title("Included feature counts by family and stage")
    axes[0].set_xlabel("Modeling stage")
    axes[0].set_ylabel("Included feature count")
    axes[0].legend(title="Feature family", bbox_to_anchor=(1.02, 1), loc="upper left")

    include_counts = (
        inventory_df.groupby(["stage", "included_in_stage"]).size().reset_index(name="feature_count")
    )
    include_counts["included_in_stage"] = include_counts["included_in_stage"].map(
        {True: "Included", False: "Excluded"}
    )
    sns.barplot(
        data=include_counts,
        x="stage",
        y="feature_count",
        hue="included_in_stage",
        ax=axes[1],
    )
    axes[1].set_title("Included vs excluded columns by stage")
    axes[1].set_xlabel("Modeling stage")
    axes[1].set_ylabel("Column count")
    axes[1].legend(title="")

    path = INVENTORY_FIG_DIR / "feature_inventory_stage_summary.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    family_missing = (
        inventory_df.groupby(["stage", "source_family"], as_index=False)["missing_fraction"].mean()
    )
    heatmap_df = family_missing.pivot(index="source_family", columns="stage", values="missing_fraction").fillna(0.0)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(heatmap_df, annot=True, fmt=".2f", cmap="YlOrRd", ax=ax)
    ax.set_title("Mean missingness by feature family and stage")
    ax.set_xlabel("Modeling stage")
    ax.set_ylabel("Feature family")
    path = INVENTORY_FIG_DIR / "missingness_by_family_stage_heatmap.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))
    return created


def plot_feature_quality(full_feature_df: pd.DataFrame, feature_tables: dict[str, pd.DataFrame]) -> list[str]:
    created = []
    missing_cols = [col for col in full_feature_df.columns if full_feature_df[col].isna().any()]
    if missing_cols:
        missing_summary = (
            pd.DataFrame(
                {
                    "column": missing_cols,
                    "missing_count": [int(full_feature_df[col].isna().sum()) for col in missing_cols],
                }
            )
            .sort_values("missing_count", ascending=False)
        )
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=missing_summary, x="column", y="missing_count", color="#E15759", ax=ax)
        ax.set_title("Columns with missing values in the full feature table")
        ax.set_xlabel("Column")
        ax.set_ylabel("Missing row count")
        ax.tick_params(axis="x", rotation=60)
        path = FEATURE_FIG_DIR / "full_feature_missingness_bar.png"
        save_figure(path)
        created.append(str(path.relative_to(ROOT_DIR)))

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(
            full_feature_df[missing_cols].isna().astype(int),
            cbar=False,
            cmap=ListedColormap(["#F5F5F5", "#D62728"]),
            ax=ax,
        )
        ax.set_title("Missingness heatmap for columns with any missing values")
        ax.set_xlabel("Columns with missingness")
        ax.set_ylabel("Observation index")
        path = FEATURE_FIG_DIR / "full_feature_missingness_heatmap.png"
        save_figure(path)
        created.append(str(path.relative_to(ROOT_DIR)))

    variance_df = feature_tables["feature_variance_summary"].copy()
    plot_df = variance_df.loc[variance_df["included_in_stage"] & variance_df["variance"].notna()].copy()
    plot_df["log10_variance_plus_1e_9"] = np.log10(plot_df["variance"] + 1e-9)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(data=plot_df, x="log10_variance_plus_1e_9", hue="stage", element="step", stat="count", common_norm=False, ax=ax)
    ax.set_title("Variance distribution for included numeric features by stage")
    ax.set_xlabel("log10(variance + 1e-9)")
    ax.set_ylabel("Feature count")
    path = FEATURE_FIG_DIR / "included_feature_variance_distribution.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    available_image_cols = [col for col in IMAGE_HEATMAP_FEATURES if col in full_feature_df.columns]
    if available_image_cols:
        image_corr = full_feature_df[available_image_cols].corr(method="spearman")
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(image_corr, cmap="coolwarm", center=0.0, ax=ax)
        ax.set_title("Focused image-feature Spearman correlation heatmap")
        path = FEATURE_FIG_DIR / "image_feature_correlation_heatmap.png"
        save_figure(path)
        created.append(str(path.relative_to(ROOT_DIR)))

    available_tabular_cols = [col for col in TABULAR_HEATMAP_FEATURES if col in full_feature_df.columns]
    if available_tabular_cols:
        tabular_corr = full_feature_df[available_tabular_cols].corr(method="spearman")
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(tabular_corr, cmap="coolwarm", center=0.0, annot=True, fmt=".2f", ax=ax)
        ax.set_title("Focused tabular-feature Spearman correlation heatmap")
        path = FEATURE_FIG_DIR / "tabular_feature_correlation_heatmap.png"
        save_figure(path)
        created.append(str(path.relative_to(ROOT_DIR)))

    feature_target_corr = feature_tables["feature_target_correlation_summary"].copy()
    focused_features = (
        feature_target_corr.groupby("target", as_index=False)
        .head(5)["feature_name"]
        .drop_duplicates()
        .tolist()
    )
    focused_heatmap = (
        feature_target_corr.loc[feature_target_corr["feature_name"].isin(focused_features)]
        .pivot(index="feature_name", columns="target", values="spearman_corr")
        .sort_index()
    )
    if not focused_heatmap.empty:
        fig, ax = plt.subplots(figsize=(8, max(4, len(focused_heatmap) * 0.35)))
        sns.heatmap(focused_heatmap, cmap="coolwarm", center=0.0, annot=True, fmt=".2f", ax=ax)
        ax.set_title("Focused feature-target Spearman correlation heatmap")
        path = FEATURE_FIG_DIR / "feature_target_correlation_heatmap.png"
        save_figure(path)
        created.append(str(path.relative_to(ROOT_DIR)))

    ranked = (
        feature_target_corr.groupby("target", as_index=False)
        .head(10)
        .copy()
    )
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    axes = axes.flatten()
    for ax, target in zip(axes, TARGET_COLUMNS):
        sub = ranked.loc[ranked["target"] == target].iloc[::-1]
        sns.barplot(data=sub, x="spearman_abs_corr", y="feature_name", hue="source_family", dodge=False, ax=ax)
        ax.set_title(f"Top absolute Spearman correlations with {target}")
        ax.set_xlabel("|Spearman correlation|")
        ax.set_ylabel("Feature")
        if ax is axes[0]:
            ax.legend(title="Family", bbox_to_anchor=(1.02, 1), loc="upper left")
        else:
            ax.legend_.remove()
    path = FEATURE_FIG_DIR / "ranked_feature_target_correlations.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    collinear, collinear_title = select_collinearity_pairs_for_plot(
        feature_tables["high_collinearity_pairs"],
        top_n=15,
    )
    if not collinear.empty:
        collinear["pair"] = collinear["left_feature"] + " vs " + collinear["right_feature"]
        plot_df = collinear.iloc[::-1].copy()
        fig, ax = plt.subplots(figsize=(10.5, max(4.5, len(plot_df) * 0.42)))
        sns.barplot(data=plot_df, x="spearman_abs_corr", y="pair", color="#F28E2B", ax=ax)
        ax.set_title(collinear_title)
        ax.set_xlabel("|Spearman correlation|")
        ax.set_ylabel("Feature pair")
        x_min = max(0.95, float(plot_df["spearman_abs_corr"].min()) - 0.0025)
        ax.set_xlim(x_min, 1.0025)
        for patch, value in zip(ax.patches, plot_df["spearman_abs_corr"]):
            ax.text(
                min(value + 0.0004, 1.0015),
                patch.get_y() + patch.get_height() / 2,
                f"{value:.4f}",
                va="center",
                ha="left",
                fontsize=8,
            )
        path = FEATURE_FIG_DIR / "high_collinearity_pairs.png"
        save_figure(path)
        created.append(str(path.relative_to(ROOT_DIR)))
    return created


def plot_prediction_and_importance_diagnostics() -> list[str]:
    created = []
    for stage in ["surface", "hidden_damage"]:
        stage_dir = OUTPUT_DIR / "models" / stage
        for importance_path in sorted(stage_dir.rglob("*_feature_importance.csv")):
            rel = importance_path.relative_to(stage_dir)
            if len(rel.parts) < 3:
                continue
            target, strategy = rel.parts[0], rel.parts[1]
            importance_df = pd.read_csv(importance_path).head(15).copy()
            if importance_df.empty or "feature" not in importance_df.columns:
                continue
            importance_df = importance_df.iloc[::-1]
            fig, ax = plt.subplots(figsize=(10, max(4, len(importance_df) * 0.35)))
            sns.barplot(data=importance_df, x="importance", y="feature", color="#4C78A8", ax=ax)
            ax.set_title(f"{stage} feature importance: {target} | {strategy}")
            ax.set_xlabel("Importance")
            ax.set_ylabel("Feature")
            output_path = (
                BENCHMARK_IMPORTANCE_FIG_DIR
                / stage
                / target
                / f"{target}_{strategy}_feature_importance_ranked.png"
            )
            save_figure(output_path)
            created.append(str(output_path.relative_to(ROOT_DIR)))

        for prediction_path in sorted(stage_dir.rglob("*_predictions.csv")):
            rel = prediction_path.relative_to(stage_dir)
            if len(rel.parts) < 3:
                continue
            target, strategy = rel.parts[0], rel.parts[1]
            pred_df = pd.read_csv(prediction_path)
            required_cols = {"y_true", "y_pred", "model_name"}
            if pred_df.empty or not required_cols.issubset(pred_df.columns):
                continue
            max_value = max(pred_df["y_true"].max(), pred_df["y_pred"].max())
            min_value = min(pred_df["y_true"].min(), pred_df["y_pred"].min())

            fig, axes = plt.subplots(1, 2, figsize=(12, 5))
            sns.scatterplot(
                data=pred_df,
                x="y_true",
                y="y_pred",
                hue="model_name",
                style="split_id" if "split_id" in pred_df.columns else None,
                alpha=0.6,
                ax=axes[0],
            )
            axes[0].plot([min_value, max_value], [min_value, max_value], linestyle="--", color="black")
            axes[0].set_title(f"Predictions vs truth: {stage} | {target} | {strategy}")
            axes[0].set_xlabel("Observed")
            axes[0].set_ylabel("Predicted")

            residual_df = pred_df.copy()
            residual_df["residual"] = residual_df["y_pred"] - residual_df["y_true"]
            sns.boxplot(data=residual_df, x="model_name", y="residual", color="#F28E2B", ax=axes[1])
            sns.stripplot(
                data=residual_df,
                x="model_name",
                y="residual",
                color="black",
                alpha=0.45,
                size=3,
                ax=axes[1],
            )
            axes[1].axhline(0.0, linestyle="--", color="black")
            axes[1].set_title(f"Residual spread: {stage} | {target} | {strategy}")
            axes[1].set_xlabel("Model")
            axes[1].set_ylabel("Predicted - observed")
            axes[1].tick_params(axis="x", rotation=20)

            output_path = (
                BENCHMARK_PREDICTION_FIG_DIR
                / stage
                / target
                / f"{target}_{strategy}_prediction_diagnostics.png"
            )
            save_figure(output_path)
            created.append(str(output_path.relative_to(ROOT_DIR)))
    return created


def plot_distribution_diagnostics(full_feature_df: pd.DataFrame, dist_tables: dict[str, pd.DataFrame]) -> list[str]:
    created = []
    target_cols = [
        "surface_total_rust_pct",
        "peak_rust_pct",
        "wire_area_loss_frac",
        "ultimate_load_kn",
    ]
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for ax, column in zip(axes.flatten(), target_cols):
        sns.histplot(full_feature_df[column].dropna(), bins=30, kde=True, ax=ax, color="#59A14F")
        ax.set_title(SELECTED_DISTRIBUTION_VARIABLES[column])
        ax.set_xlabel(column)
        ax.set_ylabel("Count")
    path = DISTRIBUTION_FIG_DIR / "target_histograms_full_range.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for ax, column in zip(axes.flatten(), target_cols):
        sns.boxplot(x=full_feature_df[column].dropna(), ax=ax, color="#76B7B2")
        ax.set_title(f"{SELECTED_DISTRIBUTION_VARIABLES[column]} boxplot")
        ax.set_xlabel(column)
    path = DISTRIBUTION_FIG_DIR / "target_boxplots_full_range.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    sns.violinplot(data=full_feature_df, x="campaign_id", y="surface_total_rust_pct", ax=axes[0], color="#4C78A8")
    axes[0].set_title("Surface total rust by campaign")
    axes[0].set_xlabel("Campaign")
    axes[0].set_ylabel("Surface total rust (%)")
    terminal_df = full_feature_df.loc[full_feature_df["wire_area_loss_frac"].notna()].copy()
    sns.violinplot(data=terminal_df, x="campaign_id", y="wire_area_loss_frac", ax=axes[1], color="#F28E2B")
    axes[1].set_title("Wire area loss by campaign (terminal rows)")
    axes[1].set_xlabel("Campaign")
    axes[1].set_ylabel("Wire area loss (fraction)")
    path = DISTRIBUTION_FIG_DIR / "campaign_violin_diagnostics.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    fig, axes = plt.subplots(len(SKEWED_READABILITY_VARIABLES), 1, figsize=(12, 4 * len(SKEWED_READABILITY_VARIABLES)))
    for ax, column in zip(axes, SKEWED_READABILITY_VARIABLES):
        series = full_feature_df[column].dropna()
        upper = float(series.quantile(0.99))
        sns.histplot(series.clip(upper=upper), bins=30, kde=False, ax=ax, color="#E15759")
        ax.set_title(
            f"{SELECTED_DISTRIBUTION_VARIABLES[column]} (visualized to 99th percentile for readability)"
        )
        ax.set_xlabel(column)
        ax.set_ylabel("Count")
    path = DISTRIBUTION_FIG_DIR / "skewed_variable_histograms_trimmed_p99.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    for ax, column in zip(axes.flatten(), SKEWED_READABILITY_VARIABLES[:4]):
        series = full_feature_df[column].dropna()
        upper = float(series.quantile(0.99))
        sns.boxplot(x=series.clip(upper=upper), ax=ax, color="#9C755F")
        ax.set_title(
            f"{SELECTED_DISTRIBUTION_VARIABLES[column]} (boxplot to 99th percentile)"
        )
        ax.set_xlabel(column)
    path = DISTRIBUTION_FIG_DIR / "skewed_variable_boxplots_trimmed_p99.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    percentile_df = dist_tables["variable_percentile_summary"].copy()
    selected = [
        "surface_total_rust_pct",
        "peak_rust_pct",
        "wire_area_loss_frac",
        "ultimate_load_kn",
        "img_rust_area_ratio_pct",
        "img_rust_blob_count",
        "img_edge_to_center_rust_ratio",
        "predicted_wire_area_loss_frac",
    ]
    fig, axes = plt.subplots(4, 2, figsize=(14, 14))
    for ax, column in zip(axes.flatten(), selected):
        sub = percentile_df.loc[percentile_df["variable"] == column]
        ax.plot(sub["percentile"] * 100.0, sub["value"], marker="o")
        ax.set_title(f"Percentile curve: {SELECTED_DISTRIBUTION_VARIABLES[column]}")
        ax.set_xlabel("Percentile")
        ax.set_ylabel("Value")
    path = DISTRIBUTION_FIG_DIR / "selected_variable_percentile_curves.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    outlier_df = dist_tables["outlier_summary"].copy().sort_values("n_iqr_outliers", ascending=False)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(data=outlier_df, x="variable", y="n_iqr_outliers", color="#B07AA1", ax=ax)
    ax.set_title("IQR-based outlier counts by selected variable")
    ax.set_xlabel("Variable")
    ax.set_ylabel("IQR outlier count")
    ax.tick_params(axis="x", rotation=60)
    path = DISTRIBUTION_FIG_DIR / "outlier_counts_by_variable.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))
    return created


def _median_iqr_summary(df: pd.DataFrame, group_col: str, value_col: str) -> pd.DataFrame:
    return (
        df.groupby([group_col, "week"], as_index=False)[value_col]
        .agg(median="median", q25=lambda s: s.quantile(0.25), q75=lambda s: s.quantile(0.75))
    )


def plot_temporal_diagnostics(master_df: pd.DataFrame, degradation_tables: dict[str, pd.DataFrame]) -> tuple[list[str], pd.DataFrame]:
    created = []
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.scatterplot(data=master_df, x="week", y="surface_total_rust_pct", hue="campaign_id", alpha=0.35, ax=axes[0])
    summary = master_df.groupby("week", as_index=False)["surface_total_rust_pct"].median()
    sns.lineplot(data=summary, x="week", y="surface_total_rust_pct", color="black", linewidth=2.0, ax=axes[0], legend=False)
    axes[0].set_title("Surface total rust vs week with overall median trend")
    axes[0].set_xlabel("Week")
    axes[0].set_ylabel("Surface total rust (%)")

    sns.scatterplot(data=master_df, x="week", y="peak_rust_pct", hue="campaign_id", alpha=0.35, ax=axes[1])
    peak_summary = master_df.groupby("week", as_index=False)["peak_rust_pct"].median()
    sns.lineplot(data=peak_summary, x="week", y="peak_rust_pct", color="black", linewidth=2.0, ax=axes[1], legend=False)
    axes[1].set_title("Peak rust vs week with overall median trend")
    axes[1].set_xlabel("Week")
    axes[1].set_ylabel("Peak rust (%)")
    path = TEMPORAL_FIG_DIR / "surface_progression_scatter_trends.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    campaign_summary = _median_iqr_summary(master_df, "campaign_id", "surface_total_rust_pct")
    fig, ax = plt.subplots(figsize=(10, 6))
    for campaign_id, sub in campaign_summary.groupby("campaign_id"):
        ax.plot(sub["week"], sub["median"], marker="o", label=campaign_id)
        ax.fill_between(sub["week"], sub["q25"], sub["q75"], alpha=0.18)
    ax.set_title("Campaign-wise surface progression (median with IQR band)")
    ax.set_xlabel("Week")
    ax.set_ylabel("Surface total rust (%)")
    ax.legend(title="Campaign")
    path = TEMPORAL_FIG_DIR / "campaign_surface_progression_median_iqr.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    treatment_summary = _median_iqr_summary(master_df, "split_group_treatment", "surface_total_rust_pct")
    fig, ax = plt.subplots(figsize=(12, 6))
    for treatment, sub in treatment_summary.groupby("split_group_treatment"):
        ax.plot(sub["week"], sub["median"], marker="o", linewidth=1.2, label=treatment)
    ax.set_title("Treatment-wise surface progression (median by week)")
    ax.set_xlabel("Week")
    ax.set_ylabel("Surface total rust (%)")
    ax.legend(title="Treatment", bbox_to_anchor=(1.02, 1), loc="upper left", ncol=1)
    path = TEMPORAL_FIG_DIR / "treatment_surface_progression_median.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    for ax, (campaign_id, sub) in zip(axes, master_df.groupby("campaign_id")):
        sns.lineplot(
            data=sub,
            x="week",
            y="surface_total_rust_pct",
            hue="specimen_id",
            legend=False,
            alpha=0.55,
            linewidth=1.0,
            ax=ax,
        )
        ax.set_title(f"Specimen-level surface trajectories: {campaign_id}")
        ax.set_xlabel("Week")
        ax.set_ylabel("Surface total rust (%)")
    path = TEMPORAL_FIG_DIR / "campaign_faceted_specimen_spaghetti.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    exposure_df, exposure_summary = build_exposure_band_summary(master_df)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    sns.boxplot(data=exposure_df, x="exposure_band", y="surface_total_rust_pct", ax=axes[0], color="#4C78A8")
    axes[0].set_title("Surface total rust by exposure band")
    axes[0].set_xlabel("Exposure band")
    axes[0].set_ylabel("Surface total rust (%)")
    sns.boxplot(data=exposure_df, x="exposure_band", y="peak_rust_pct", ax=axes[1], color="#F28E2B")
    axes[1].set_title("Peak rust by exposure band")
    axes[1].set_xlabel("Exposure band")
    axes[1].set_ylabel("Peak rust (%)")
    path = TEMPORAL_FIG_DIR / "exposure_band_target_boxplots.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    reps = representative_specimens(master_df)
    rep_df = master_df.loc[master_df["specimen_id"].isin(reps)].copy()
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=True, sharey=True)
    for ax, specimen_id in zip(axes.flatten(), reps):
        sub = rep_df.loc[rep_df["specimen_id"] == specimen_id].sort_values("week")
        ax.plot(sub["week"], sub["surface_total_rust_pct"], marker="o", color="#4C78A8")
        ax.set_title(specimen_id)
        ax.set_xlabel("Week")
        ax.set_ylabel("Surface total rust (%)")
    fig.suptitle("Representative specimen panels (lowest / median / highest final surface rust per campaign)")
    path = TEMPORAL_FIG_DIR / "representative_specimen_surface_panels.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    return created, exposure_summary


def plot_benchmark_diagnostics(summary_df: pd.DataFrame, fold_df: pd.DataFrame, split_df: pd.DataFrame) -> tuple[list[str], pd.DataFrame]:
    created = []
    best_robustness = build_best_model_robustness(summary_df)

    master_split = split_df.loc[split_df["stage"] == "master"].copy()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.boxplot(data=master_split, x="strategy", y="test_rows", ax=axes[0], color="#4C78A8")
    axes[0].set_title("Master split test-row counts by strategy")
    axes[0].set_xlabel("Strategy")
    axes[0].set_ylabel("Test rows")
    axes[0].tick_params(axis="x", rotation=20)
    sns.boxplot(data=master_split, x="strategy", y="test_specimens", ax=axes[1], color="#F28E2B")
    axes[1].set_title("Master split test-specimen counts by strategy")
    axes[1].set_xlabel("Strategy")
    axes[1].set_ylabel("Test specimens")
    axes[1].tick_params(axis="x", rotation=20)
    path = BENCHMARK_FIG_DIR / "split_strategy_overview.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    for stage in ["surface", "hidden_damage"]:
        stage_group = summary_df.loc[
            (summary_df["stage"] == stage) & (summary_df["strategy"] == "group_shuffle")
        ].copy()
        targets = stage_group["target"].unique().tolist()
        fig, axes = plt.subplots(1, len(targets), figsize=(7 * len(targets), 5), sharey=False)
        if len(targets) == 1:
            axes = [axes]
        for ax, target in zip(axes, targets):
            sub = stage_group.loc[stage_group["target"] == target].sort_values("mae_mean")
            sns.barplot(data=sub, x="model_name", y="mae_mean", ax=ax, color="#4C78A8")
            ax.errorbar(
                x=np.arange(len(sub)),
                y=sub["mae_mean"],
                yerr=sub["mae_std"],
                fmt="none",
                ecolor="black",
                capsize=4,
            )
            ax.set_title(f"{stage} group-shuffle MAE comparison: {target}")
            ax.set_xlabel("Model")
            ax.set_ylabel("MAE")
            ax.tick_params(axis="x", rotation=20)
        path = BENCHMARK_FIG_DIR / f"{stage}_group_shuffle_model_comparison_mae.png"
        save_figure(path)
        created.append(str(path.relative_to(ROOT_DIR)))

        fig, axes = plt.subplots(1, len(targets), figsize=(7 * len(targets), 5), sharey=False)
        if len(targets) == 1:
            axes = [axes]
        for ax, target in zip(axes, targets):
            sub = stage_group.loc[stage_group["target"] == target].sort_values("spearman_mean", ascending=False)
            sns.barplot(data=sub, x="model_name", y="spearman_mean", ax=ax, color="#59A14F")
            ax.errorbar(
                x=np.arange(len(sub)),
                y=sub["spearman_mean"],
                yerr=sub["spearman_std"],
                fmt="none",
                ecolor="black",
                capsize=4,
            )
            ax.set_title(f"{stage} group-shuffle Spearman comparison: {target}")
            ax.set_xlabel("Model")
            ax.set_ylabel("Spearman correlation")
            ax.tick_params(axis="x", rotation=20)
        path = BENCHMARK_FIG_DIR / f"{stage}_group_shuffle_model_comparison_spearman.png"
        save_figure(path)
        created.append(str(path.relative_to(ROOT_DIR)))

        stage_best = best_robustness.loc[best_robustness["stage"] == stage].copy()
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        sns.barplot(data=stage_best, x="strategy", y="mae_mean", hue="target", ax=axes[0])
        axes[0].set_title(f"{stage} best-model MAE across split strategies")
        axes[0].set_xlabel("Strategy")
        axes[0].set_ylabel("MAE")
        axes[0].tick_params(axis="x", rotation=20)
        sns.barplot(data=stage_best, x="strategy", y="spearman_mean", hue="target", ax=axes[1])
        axes[1].set_title(f"{stage} best-model Spearman across split strategies")
        axes[1].set_xlabel("Strategy")
        axes[1].set_ylabel("Spearman correlation")
        axes[1].tick_params(axis="x", rotation=20)
        path = BENCHMARK_FIG_DIR / f"{stage}_best_model_strategy_robustness.png"
        save_figure(path)
        created.append(str(path.relative_to(ROOT_DIR)))

        stage_fold = fold_df.loc[
            (fold_df["stage"] == stage) & (fold_df["strategy"] == "group_shuffle")
        ].copy()
        best_names = (
            stage_best[["target", "best_model_name"]]
            .drop_duplicates()
            .rename(columns={"best_model_name": "model_name"})
        )
        stage_fold = stage_fold.merge(best_names, on=["target", "model_name"], how="inner")
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        sns.lineplot(data=stage_fold, x="split_id", y="mae", hue="target", style="model_name", marker="o", ax=axes[0])
        axes[0].set_title(f"{stage} best-model fold-wise MAE")
        axes[0].set_xlabel("Grouped split id")
        axes[0].set_ylabel("MAE")
        axes[0].tick_params(axis="x", rotation=20)
        sns.lineplot(data=stage_fold, x="split_id", y="spearman", hue="target", style="model_name", marker="o", ax=axes[1])
        axes[1].set_title(f"{stage} best-model fold-wise Spearman")
        axes[1].set_xlabel("Grouped split id")
        axes[1].set_ylabel("Spearman correlation")
        axes[1].tick_params(axis="x", rotation=20)
        path = BENCHMARK_FIG_DIR / f"{stage}_best_model_fold_stability.png"
        save_figure(path)
        created.append(str(path.relative_to(ROOT_DIR)))

    heatmap_df = best_robustness.copy()
    heatmap_df["stage_target"] = heatmap_df["stage"] + " | " + heatmap_df["target"]
    heatmap = heatmap_df.pivot(index="stage_target", columns="strategy", values="relative_mae_vs_group_shuffle")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(heatmap, annot=True, fmt=".2f", cmap="YlOrRd", ax=ax)
    ax.set_title("Best-model relative MAE collapse vs group shuffle")
    ax.set_xlabel("Split strategy")
    ax.set_ylabel("Stage | target")
    path = BENCHMARK_FIG_DIR / "best_model_relative_mae_collapse_heatmap.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    rank_rows = []
    for (stage, target), sub in summary_df.loc[summary_df["strategy"] == "group_shuffle"].groupby(["stage", "target"]):
        ordered = sub.sort_values("mae_mean").reset_index(drop=True)
        for idx, row in ordered.iterrows():
            rank_rows.append(
                {
                    "stage_target": f"{stage} | {target}",
                    "model_name": row["model_name"],
                    "rank": idx + 1,
                }
            )
    rank_df = pd.DataFrame(rank_rows)
    rank_heatmap = rank_df.pivot(index="stage_target", columns="model_name", values="rank")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(rank_heatmap, annot=True, fmt=".0f", cmap="Blues_r", ax=ax)
    ax.set_title("Group-shuffle model rank by target")
    ax.set_xlabel("Model")
    ax.set_ylabel("Stage | target")
    path = BENCHMARK_FIG_DIR / "group_shuffle_model_rank_heatmap.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))
    return created, best_robustness


def plot_degradation_diagnostics(degradation_tables: dict[str, pd.DataFrame], master_df: pd.DataFrame) -> list[str]:
    created = []
    best_df = degradation_tables["degradation_best_fits"]
    candidate_df = degradation_tables["degradation_candidates"]
    observed_fitted_df = degradation_tables["degradation_observed_vs_fitted"]
    grouped_campaign = degradation_tables["degradation_grouped_by_campaign"]
    grouped_treatment = degradation_tables["degradation_grouped_by_treatment"]
    raw_monotone_df = degradation_tables.get("degradation_raw_vs_monotone_proxy", pd.DataFrame())

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.countplot(data=best_df, x="best_family", color="#4C78A8", ax=ax)
    ax.set_title("Selected degradation family counts")
    ax.set_xlabel("Best family")
    ax.set_ylabel("Specimen count")
    path = DEGRADATION_FIG_DIR / "degradation_best_family_counts.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    successful = candidate_df.loc[candidate_df["fit_succeeded"]].copy()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=successful, x="family", y="rmse", color="#F28E2B", ax=ax)
    sns.stripplot(data=successful, x="family", y="rmse", color="black", alpha=0.45, size=3, ax=ax)
    ax.set_title("Candidate degradation fit RMSE by family")
    ax.set_xlabel("Curve family")
    ax.set_ylabel("RMSE on monotone-smoothed proxy")
    path = DEGRADATION_FIG_DIR / "degradation_fit_rmse_by_family.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    fig, ax = plt.subplots(figsize=(6, 6))
    sns.scatterplot(
        data=observed_fitted_df,
        x="fitted_wire_area_loss_frac",
        y="predicted_wire_area_loss_frac",
        hue="campaign_id",
        alpha=0.55,
        ax=ax,
    )
    upper = max(
        observed_fitted_df["fitted_wire_area_loss_frac"].max(),
        observed_fitted_df["predicted_wire_area_loss_frac"].max(),
    )
    ax.plot([0, upper], [0, upper], linestyle="--", color="black")
    ax.set_title("Observed proxy vs fitted degradation curve at observed days")
    ax.set_xlabel("Fitted hidden-damage proxy")
    ax.set_ylabel("Observed hidden-damage proxy")
    path = DEGRADATION_FIG_DIR / "degradation_observed_vs_fitted_scatter.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    residual_family = observed_fitted_df.copy()
    if "best_family" not in residual_family.columns:
        residual_family = residual_family.merge(
            best_df[["specimen_id", "best_family"]],
            on="specimen_id",
            how="left",
        )
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=residual_family, x="best_family", y="residual", color="#76B7B2", ax=ax)
    ax.set_title("Observed-minus-fitted residuals by selected degradation family")
    ax.set_xlabel("Best family")
    ax.set_ylabel("Residual")
    path = DEGRADATION_FIG_DIR / "degradation_residuals_by_family.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=grouped_campaign, x="day", y="predicted_wire_area_loss_frac", hue="campaign_id", marker=None, ax=ax)
    ax.set_title("Grouped degradation summary by campaign")
    ax.set_xlabel("Ageing day")
    ax.set_ylabel("Median fitted hidden-damage proxy")
    path = DEGRADATION_FIG_DIR / "degradation_grouped_by_campaign.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(
        data=grouped_treatment,
        x="day",
        y="predicted_wire_area_loss_frac",
        hue="split_group_treatment",
        linewidth=1.4,
        ax=ax,
    )
    ax.set_title("Grouped degradation summary by treatment")
    ax.set_xlabel("Ageing day")
    ax.set_ylabel("Median fitted hidden-damage proxy")
    ax.legend(title="Treatment", bbox_to_anchor=(1.02, 1), loc="upper left")
    path = DEGRADATION_FIG_DIR / "degradation_grouped_by_treatment.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    reps = representative_specimens(master_df)
    rep_obs = observed_fitted_df.loc[observed_fitted_df["specimen_id"].isin(reps)].copy()
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=True, sharey=True)
    for ax, specimen_id in zip(axes.flatten(), reps):
        sub = rep_obs.loc[rep_obs["specimen_id"] == specimen_id].sort_values("ageing_days")
        ax.plot(sub["ageing_days"], sub["fitted_wire_area_loss_frac"], color="#4C78A8", linewidth=2.0)
        ax.scatter(sub["ageing_days"], sub["predicted_wire_area_loss_frac"], color="#E15759", s=20)
        ax.set_title(specimen_id)
        ax.set_xlabel("Ageing day")
        ax.set_ylabel("Hidden-damage proxy")
    fig.suptitle("Representative degradation trajectories: fitted curve with observed proxy points")
    path = DEGRADATION_FIG_DIR / "degradation_representative_specimens.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    if not raw_monotone_df.empty:
        reps = representative_specimens(master_df)
        rep_raw = raw_monotone_df.loc[raw_monotone_df["specimen_id"].isin(reps)].copy()
        fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=True, sharey=True)
        for ax, specimen_id in zip(axes.flatten(), reps):
            sub = rep_raw.loc[rep_raw["specimen_id"] == specimen_id].sort_values("ageing_days")
            ax.plot(
                sub["ageing_days"],
                sub["raw_predicted_wire_area_loss_frac"],
                marker="o",
                color="#E15759",
                label="raw proxy",
            )
            ax.plot(
                sub["ageing_days"],
                sub["monotone_proxy_wire_area_loss_frac"],
                marker="s",
                color="#4C78A8",
                label="monotone proxy",
            )
            ax.set_title(specimen_id)
            ax.set_xlabel("Ageing day")
            ax.set_ylabel("Wire area loss proxy")
        axes[0][0].legend(loc="upper left")
        fig.suptitle("Representative raw vs monotone hidden-damage proxy trajectories")
        path = DEGRADATION_FIG_DIR / "degradation_raw_vs_monotone_representative.png"
        save_figure(path)
        created.append(str(path.relative_to(ROOT_DIR)))
    return created


def plot_proxy_diagnostics(proxy_tables: dict[str, pd.DataFrame]) -> list[str]:
    created = []
    proxy_df = proxy_tables["proxy_estimates"]
    summary_df = proxy_tables["proxy_status_summary"]

    stacked = summary_df.melt(
        id_vars=["threshold_wire_area_loss_frac", "n_specimens"],
        value_vars=[
            "n_crossed_by_baseline",
            "n_crossed_during_observation",
            "n_future_crossings_within_horizon",
            "n_right_censored",
        ],
        var_name="status_component",
        value_name="count",
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    bottom = np.zeros(len(summary_df))
    color_map = {
        "n_crossed_by_baseline": "#E15759",
        "n_crossed_during_observation": "#F28E2B",
        "n_future_crossings_within_horizon": "#59A14F",
        "n_right_censored": "#4C78A8",
    }
    for component in [
        "n_crossed_by_baseline",
        "n_crossed_during_observation",
        "n_future_crossings_within_horizon",
        "n_right_censored",
    ]:
        sub = stacked.loc[stacked["status_component"] == component]
        ax.bar(
            sub["threshold_wire_area_loss_frac"].astype(str),
            sub["count"],
            bottom=bottom,
            label=component.replace("n_", "").replace("_", " "),
            color=color_map[component],
        )
        bottom += sub["count"].to_numpy(dtype=float)
    ax.set_title("Threshold-status counts by threshold")
    ax.set_xlabel("Wire area loss threshold")
    ax.set_ylabel("Specimen count")
    ax.legend(title="Status")
    path = PROXY_FIG_DIR / "proxy_threshold_status_counts.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    non_censored = proxy_df.loc[~proxy_df["right_censored"]].copy()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(
        data=non_censored,
        x="threshold_wire_area_loss_frac",
        y="estimated_crossing_day",
        color="#76B7B2",
        ax=ax,
    )
    sns.stripplot(
        data=non_censored,
        x="threshold_wire_area_loss_frac",
        y="estimated_crossing_day",
        hue="threshold_status",
        dodge=False,
        size=4,
        alpha=0.7,
        ax=ax,
    )
    ax.set_title("Estimated threshold-crossing day by threshold and status")
    ax.set_xlabel("Wire area loss threshold")
    ax.set_ylabel("Estimated crossing day")
    ax.legend(title="Status", bbox_to_anchor=(1.02, 1), loc="upper left")
    path = PROXY_FIG_DIR / "proxy_estimated_crossing_day_by_threshold.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    status_order = {
        "crossed_by_baseline": 0,
        "crossed_during_observation": 1,
        "future_crossing_within_horizon": 2,
        "not_crossed_within_horizon": 3,
    }
    heatmap_source = proxy_df.copy()
    specimen_order = (
        heatmap_source.groupby("specimen_id")["last_observed_predicted_wire_area_loss_frac"]
        .max()
        .sort_values(ascending=False)
        .index.tolist()
    )
    heatmap_source["status_code"] = heatmap_source["threshold_status"].map(status_order)
    heatmap = (
        heatmap_source.pivot(index="specimen_id", columns="threshold_wire_area_loss_frac", values="status_code")
        .reindex(specimen_order)
    )
    fig, ax = plt.subplots(figsize=(8, 12))
    cmap = ListedColormap(["#E15759", "#F28E2B", "#59A14F", "#4C78A8"])
    sns.heatmap(heatmap, cmap=cmap, cbar=False, ax=ax)
    ax.set_title("Specimen-level threshold-status heatmap\n(sorted by final predicted hidden-damage proxy)")
    ax.set_xlabel("Wire area loss threshold")
    ax.set_ylabel("Specimen")
    legend_elements = [
        Line2D([0], [0], marker="s", color="w", label=label.replace("_", " "), markerfacecolor=color, markersize=10)
        for label, color in zip(status_order.keys(), ["#E15759", "#F28E2B", "#59A14F", "#4C78A8"])
    ]
    ax.legend(handles=legend_elements, title="Status", bbox_to_anchor=(1.02, 1), loc="upper left")
    path = PROXY_FIG_DIR / "proxy_threshold_status_heatmap.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))

    future_counts = (
        proxy_df.groupby("threshold_wire_area_loss_frac")["proxy_rul_days"]
        .apply(lambda s: int(s.notna().sum()))
        .reset_index(name="n_future_proxy_rul_values")
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=future_counts, x="threshold_wire_area_loss_frac", y="n_future_proxy_rul_values", color="#59A14F", ax=ax)
    ax.set_title("Future proxy-RUL values available by threshold\n(current run: no future crossings)")
    ax.set_xlabel("Wire area loss threshold")
    ax.set_ylabel("Rows with non-null proxy_rul_days")
    path = PROXY_FIG_DIR / "proxy_future_rul_nonnull_counts.png"
    save_figure(path)
    created.append(str(path.relative_to(ROOT_DIR)))
    return created


def build_output_visualization_inventory() -> pd.DataFrame:
    rows = [
        {
            "file_path": "outputs/data/master_table.csv",
            "contains": "Aligned observation-level dataset with time, mapping, targets, and image linkage.",
            "plot_needed": "yes",
            "recommended_plot_type": "progression lines, distribution panels, missingness plot",
            "reason": "This is the main data table and needs temporal, structural, and outlier views.",
            "status_before": "existing plot weak",
            "companion_plots": "; ".join(
                [
                    "outputs/diagnostics/figures/temporal/surface_progression_scatter_trends.png",
                    "outputs/diagnostics/figures/temporal/campaign_surface_progression_median_iqr.png",
                    "outputs/diagnostics/figures/distributions/target_histograms_full_range.png",
                ]
            ),
        },
        {
            "file_path": "outputs/data/terminal_structural_table.csv",
            "contains": "Terminal structural subset with one labelled row per specimen.",
            "plot_needed": "yes",
            "recommended_plot_type": "campaign violin/boxplot, structural benchmark plots",
            "reason": "This table shows the sparsity and cross-campaign structural contrast.",
            "status_before": "new plot required",
            "companion_plots": "; ".join(
                [
                    "outputs/diagnostics/figures/distributions/campaign_violin_diagnostics.png",
                    "outputs/diagnostics/figures/benchmarks/hidden_damage_best_model_strategy_robustness.png",
                ]
            ),
        },
        {
            "file_path": "outputs/data/full_feature_table.csv",
            "contains": "Merged master table and interpretable image features.",
            "plot_needed": "yes",
            "recommended_plot_type": "missingness heatmap, feature correlation heatmaps",
            "reason": "This is the main modeling table and needs transparent feature diagnostics.",
            "status_before": "new plot required",
            "companion_plots": "; ".join(
                [
                    "outputs/diagnostics/figures/features/full_feature_missingness_heatmap.png",
                    "outputs/diagnostics/figures/features/image_feature_correlation_heatmap.png",
                    "outputs/diagnostics/figures/features/feature_target_correlation_heatmap.png",
                ]
            ),
        },
        {
            "file_path": "outputs/features/image_features.csv",
            "contains": "Raw interpretable image-feature table with identifiers.",
            "plot_needed": "yes",
            "recommended_plot_type": "feature correlation heatmap, skewed distribution plots",
            "reason": "Image features need outlier, duplicate, and collinearity diagnostics.",
            "status_before": "new plot required",
            "companion_plots": "; ".join(
                [
                    "outputs/diagnostics/figures/features/image_feature_correlation_heatmap.png",
                    "outputs/diagnostics/figures/distributions/skewed_variable_histograms_trimmed_p99.png",
                ]
            ),
        },
        {
            "file_path": "outputs/features/feature_dictionary.csv",
            "contains": "Textual feature definitions and extraction notes.",
            "plot_needed": "no",
            "recommended_plot_type": "none",
            "reason": "This is reference documentation rather than numeric output; a table is the right form.",
            "status_before": "existing plot sufficient",
            "companion_plots": "",
        },
        {
            "file_path": "outputs/features/image_feature_failures.csv",
            "contains": "Image-feature extraction failure log.",
            "plot_needed": "no",
            "recommended_plot_type": "none",
            "reason": "This is a sparse QA log; plotting it would not add clarity unless failures become numerous.",
            "status_before": "existing plot sufficient",
            "companion_plots": "",
        },
        {
            "file_path": "outputs/splits/*_summary.csv",
            "contains": "Grouped split summaries for the full aligned dataset.",
            "plot_needed": "yes",
            "recommended_plot_type": "split composition boxplots",
            "reason": "Split-size variation should be visible, not only tabulated.",
            "status_before": "new plot required",
            "companion_plots": "outputs/diagnostics/figures/benchmarks/split_strategy_overview.png",
        },
        {
            "file_path": "outputs/splits/*.csv",
            "contains": "Row-wise split membership manifests for the full aligned dataset.",
            "plot_needed": "no",
            "recommended_plot_type": "none",
            "reason": "These are transactional membership tables; the plot-worthy content is their derived composition, which is shown in the split overview figure.",
            "status_before": "existing plot sufficient",
            "companion_plots": "outputs/diagnostics/figures/benchmarks/split_strategy_overview.png",
        },
        {
            "file_path": "outputs/models/surface/*/*/*_summary.csv",
            "contains": "Surface benchmark summary metrics.",
            "plot_needed": "yes",
            "recommended_plot_type": "model-comparison bar plots and best-model robustness plots",
            "reason": "Model stability and strategy robustness matter more than the nominal winner.",
            "status_before": "existing plot weak",
            "companion_plots": "; ".join(
                [
                    "outputs/diagnostics/figures/benchmarks/surface_group_shuffle_model_comparison_mae.png",
                    "outputs/diagnostics/figures/benchmarks/surface_best_model_strategy_robustness.png",
                ]
            ),
        },
        {
            "file_path": "outputs/models/surface/best_models.csv",
            "contains": "Per-target surface-stage winner table with benchmark note.",
            "plot_needed": "yes",
            "recommended_plot_type": "strategy-robustness plot and rank heatmap",
            "reason": "The winner table alone hides whether the result is stable or scientifically meaningful.",
            "status_before": "existing plot weak",
            "companion_plots": "; ".join(
                [
                    "outputs/diagnostics/figures/benchmarks/surface_best_model_strategy_robustness.png",
                    "outputs/diagnostics/figures/benchmarks/group_shuffle_model_rank_heatmap.png",
                ]
            ),
        },
        {
            "file_path": "outputs/models/surface/*/*/*_fold_metrics.csv",
            "contains": "Fold-level surface benchmark metrics.",
            "plot_needed": "yes",
            "recommended_plot_type": "fold-wise stability lines",
            "reason": "Fold variability is critical for interpreting stability.",
            "status_before": "new plot required",
            "companion_plots": "outputs/diagnostics/figures/benchmarks/surface_best_model_fold_stability.png",
        },
        {
            "file_path": "outputs/models/surface/*/*/*_predictions.csv",
            "contains": "Surface-stage saved out-of-split predictions by model and split.",
            "plot_needed": "yes",
            "recommended_plot_type": "predicted-vs-observed scatter and residual boxplots",
            "reason": "Prediction tables are easier to interpret when error shape and dispersion are visible.",
            "status_before": "new plot required",
            "companion_plots": "outputs/diagnostics/figures/benchmarks/predictions/surface/..._prediction_diagnostics.png",
        },
        {
            "file_path": "outputs/models/surface/*/*/*_feature_importance.csv",
            "contains": "Surface-stage feature-importance tables.",
            "plot_needed": "yes",
            "recommended_plot_type": "ranked horizontal bar plots",
            "reason": "Importance CSVs should have an immediate visual ranking, even when interpretation remains conservative.",
            "status_before": "existing plot weak",
            "companion_plots": "outputs/diagnostics/figures/benchmarks/feature_importance/surface/..._feature_importance_ranked.png",
        },
        {
            "file_path": "outputs/models/hidden_damage/*/*/*_summary.csv",
            "contains": "Hidden-damage benchmark summary metrics.",
            "plot_needed": "yes",
            "recommended_plot_type": "grouped model-comparison bars and robustness plots",
            "reason": "These results are weak and need visual emphasis on collapse and instability.",
            "status_before": "new plot required",
            "companion_plots": "; ".join(
                [
                    "outputs/diagnostics/figures/benchmarks/hidden_damage_group_shuffle_model_comparison_mae.png",
                    "outputs/diagnostics/figures/benchmarks/hidden_damage_best_model_strategy_robustness.png",
                    "outputs/diagnostics/figures/benchmarks/best_model_relative_mae_collapse_heatmap.png",
                ]
            ),
        },
        {
            "file_path": "outputs/models/hidden_damage/best_models.csv",
            "contains": "Per-target hidden-damage winner table.",
            "plot_needed": "yes",
            "recommended_plot_type": "strategy-robustness plot and rank heatmap",
            "reason": "The winner table is not enough because this stage is small-sample and unstable across splits.",
            "status_before": "new plot required",
            "companion_plots": "; ".join(
                [
                    "outputs/diagnostics/figures/benchmarks/hidden_damage_best_model_strategy_robustness.png",
                    "outputs/diagnostics/figures/benchmarks/group_shuffle_model_rank_heatmap.png",
                ]
            ),
        },
        {
            "file_path": "outputs/models/hidden_damage/*/*/*_fold_metrics.csv",
            "contains": "Fold-level hidden-damage benchmark metrics.",
            "plot_needed": "yes",
            "recommended_plot_type": "fold-wise stability lines",
            "reason": "This stage is underpowered and needs explicit variance diagnostics.",
            "status_before": "new plot required",
            "companion_plots": "outputs/diagnostics/figures/benchmarks/hidden_damage_best_model_fold_stability.png",
        },
        {
            "file_path": "outputs/models/hidden_damage/*/*/*_predictions.csv",
            "contains": "Hidden-damage saved out-of-split predictions by model and split.",
            "plot_needed": "yes",
            "recommended_plot_type": "predicted-vs-observed scatter and residual boxplots",
            "reason": "The prediction spread is important for understanding how weak the structural stage is.",
            "status_before": "new plot required",
            "companion_plots": "outputs/diagnostics/figures/benchmarks/predictions/hidden_damage/..._prediction_diagnostics.png",
        },
        {
            "file_path": "outputs/models/hidden_damage/*/*/*_feature_importance.csv",
            "contains": "Hidden-damage feature-importance tables.",
            "plot_needed": "yes",
            "recommended_plot_type": "ranked horizontal bar plots",
            "reason": "Importance rankings are easier to review visually, but must be shown alongside weakness diagnostics.",
            "status_before": "existing plot weak",
            "companion_plots": "outputs/diagnostics/figures/benchmarks/feature_importance/hidden_damage/..._feature_importance_ranked.png",
        },
        {
            "file_path": "outputs/models/degradation/full_feature_table_with_hidden_damage_proxy.csv",
            "contains": "Longitudinal table augmented with hidden-damage proxy values used by degradation modelling.",
            "plot_needed": "yes",
            "recommended_plot_type": "distribution, temporal trend, and observed-vs-fitted plots",
            "reason": "This table links the prediction and trajectory stages and must be visually checked.",
            "status_before": "new plot required",
            "companion_plots": "; ".join(
                [
                    "outputs/diagnostics/figures/distributions/selected_variable_percentile_curves.png",
                    "outputs/diagnostics/figures/temporal/surface_progression_scatter_trends.png",
                    "outputs/diagnostics/figures/degradation/degradation_observed_vs_fitted_scatter.png",
                ]
            ),
        },
        {
            "file_path": "outputs/models/degradation/degradation_best_fits.csv",
            "contains": "Best degradation family per specimen.",
            "plot_needed": "yes",
            "recommended_plot_type": "family count bar chart",
            "reason": "Family selection should be visible and easy to discuss.",
            "status_before": "existing plot weak",
            "companion_plots": "outputs/diagnostics/figures/degradation/degradation_best_family_counts.png",
        },
        {
            "file_path": "outputs/models/degradation/degradation_fit_candidates.csv",
            "contains": "Candidate degradation fit metrics by family and specimen.",
            "plot_needed": "yes",
            "recommended_plot_type": "RMSE boxplot/strip plot by family",
            "reason": "Fit-quality dispersion matters more than only the selected family count.",
            "status_before": "new plot required",
            "companion_plots": "outputs/diagnostics/figures/degradation/degradation_fit_rmse_by_family.png",
        },
        {
            "file_path": "outputs/models/degradation/degradation_trajectory_grid.csv",
            "contains": "Dense day-level fitted degradation trajectories.",
            "plot_needed": "yes",
            "recommended_plot_type": "grouped trajectory lines and representative specimen panels",
            "reason": "Trajectory behavior is central to whether degradation modelling looks plausible.",
            "status_before": "existing plot weak",
            "companion_plots": "; ".join(
                [
                    "outputs/diagnostics/figures/degradation/degradation_grouped_by_campaign.png",
                    "outputs/diagnostics/figures/degradation/degradation_grouped_by_treatment.png",
                    "outputs/diagnostics/figures/degradation/degradation_representative_specimens.png",
                ]
            ),
        },
        {
            "file_path": "outputs/models/degradation/degradation_raw_vs_monotone_proxy.csv",
            "contains": "Observed raw hidden-damage proxy values and their monotone-smoothed versions at observed days.",
            "plot_needed": "yes",
            "recommended_plot_type": "raw-vs-monotone trajectory comparison panels",
            "reason": "This file makes the smoothing step visible instead of treating it as a hidden preprocessing detail.",
            "status_before": "new plot required",
            "companion_plots": "outputs/diagnostics/figures/degradation/degradation_raw_vs_monotone_representative.png",
        },
        {
            "file_path": "outputs/models/proxy_rul/proxy_rul_summary.csv",
            "contains": "Threshold-status summary by threshold.",
            "plot_needed": "yes",
            "recommended_plot_type": "stacked threshold-status count plot",
            "reason": "The summary is categorical and should show baseline, observed-window, future, and censored counts clearly.",
            "status_before": "existing plot weak",
            "companion_plots": "outputs/diagnostics/figures/proxy/proxy_threshold_status_counts.png",
        },
        {
            "file_path": "outputs/models/proxy_rul/proxy_rul_summary.json",
            "contains": "JSON serialization of the proxy threshold-status summary.",
            "plot_needed": "no",
            "recommended_plot_type": "none",
            "reason": "The CSV already holds the plotting-ready content; the JSON is only a machine-readable duplicate.",
            "status_before": "existing plot sufficient",
            "companion_plots": "",
        },
        {
            "file_path": "outputs/models/proxy_rul/proxy_rul_estimates.csv",
            "contains": "Specimen-level threshold-status records and crossing-day estimates.",
            "plot_needed": "yes",
            "recommended_plot_type": "status heatmap and crossing-day box/strip plot",
            "reason": "Specimen-level threshold behavior is easier to explain visually than row-wise CSV output.",
            "status_before": "new plot required",
            "companion_plots": "; ".join(
                [
                    "outputs/diagnostics/figures/proxy/proxy_threshold_status_heatmap.png",
                    "outputs/diagnostics/figures/proxy/proxy_estimated_crossing_day_by_threshold.png",
                ]
            ),
        },
        {
            "file_path": "outputs/logs/*.log",
            "contains": "Execution logs.",
            "plot_needed": "no",
            "recommended_plot_type": "none",
            "reason": "Logs are textual execution traces; summary tables and plots should be derived from structured outputs instead.",
            "status_before": "existing plot sufficient",
            "companion_plots": "",
        },
    ]
    return pd.DataFrame(rows)


def build_figure_inventory(new_figures: list[str]) -> pd.DataFrame:
    review_map = {
        "outputs/eda/figures/missingness.png": {
            "purpose": "Legacy missingness overview.",
            "quality_assessment": "strong and presentation-ready",
            "action": "keep",
            "reason": "Clear and directly useful.",
            "replacement_or_companion": "outputs/diagnostics/figures/features/full_feature_missingness_heatmap.png",
        },
        "outputs/eda/figures/structural_target_sparsity.png": {
            "purpose": "Legacy structural-label sparsity figure.",
            "quality_assessment": "strong and presentation-ready",
            "action": "keep",
            "reason": "Still one of the clearest summary figures in the project.",
            "replacement_or_companion": "",
        },
        "outputs/eda/figures/target_distributions.png": {
            "purpose": "Legacy target-distribution summary.",
            "quality_assessment": "useful but needs improvement",
            "action": "revise",
            "reason": "Helpful, but new diagnostics add separate outlier and percentile views.",
            "replacement_or_companion": "outputs/diagnostics/figures/distributions/target_histograms_full_range.png",
        },
        "outputs/eda/figures/within_specimen_surface_total_rust.png": {
            "purpose": "Legacy specimen-level surface trajectory overview.",
            "quality_assessment": "useful but needs improvement",
            "action": "revise",
            "reason": "Dense single-panel spaghetti view is hard to present cleanly.",
            "replacement_or_companion": "outputs/diagnostics/figures/temporal/campaign_faceted_specimen_spaghetti.png",
        },
        "outputs/eda/figures/cross_campaign_peak_rust.png": {
            "purpose": "Legacy peak-rust campaign comparison.",
            "quality_assessment": "strong and presentation-ready",
            "action": "keep",
            "reason": "Still useful as a quick campaign contrast figure.",
            "replacement_or_companion": "outputs/diagnostics/figures/temporal/campaign_surface_progression_median_iqr.png",
        },
        "outputs/eda/figures/surface_rust_by_campaign.png": {
            "purpose": "Legacy surface-rust campaign summary.",
            "quality_assessment": "useful but needs improvement",
            "action": "revise",
            "reason": "The new temporal campaign plot communicates progression more clearly than a static summary.",
            "replacement_or_companion": "outputs/diagnostics/figures/temporal/campaign_surface_progression_median_iqr.png",
        },
        "outputs/eda/figures/row_counts.png": {
            "purpose": "Legacy count summary.",
            "quality_assessment": "weak/redundant",
            "action": "discard",
            "reason": "The table already communicates this cleanly; not strong presentation material.",
            "replacement_or_companion": "",
        },
        "outputs/eda/figures/campaign_counts.png": {
            "purpose": "Legacy campaign counts.",
            "quality_assessment": "weak/redundant",
            "action": "discard",
            "reason": "Useful as a table, but low-value as a presentation figure.",
            "replacement_or_companion": "",
        },
        "outputs/eda/figures/treatment_counts.png": {
            "purpose": "Legacy treatment counts.",
            "quality_assessment": "weak/redundant",
            "action": "discard",
            "reason": "Counts are better handled in tables and the new stage-overview diagnostics.",
            "replacement_or_companion": "",
        },
        "outputs/eda/figures/week_distribution.png": {
            "purpose": "Legacy week distribution.",
            "quality_assessment": "weak/redundant",
            "action": "discard",
            "reason": "Helpful for audit, but not strong enough for a main explanation figure.",
            "replacement_or_companion": "outputs/diagnostics/figures/temporal/surface_progression_scatter_trends.png",
        },
        "outputs/models/degradation/degradation_subset_trajectories.png": {
            "purpose": "Legacy degradation subset figure.",
            "quality_assessment": "useful but needs improvement",
            "action": "revise",
            "reason": "A subset alone is not enough; grouped summaries and observed-vs-fitted views are clearer.",
            "replacement_or_companion": "outputs/diagnostics/figures/degradation/degradation_observed_vs_fitted_scatter.png",
        },
        "outputs/models/proxy_rul/proxy_rul_right_censored.png": {
            "purpose": "Legacy proxy censoring plot.",
            "quality_assessment": "useful but needs improvement",
            "action": "revise",
            "reason": "Status counts are more informative than censoring alone.",
            "replacement_or_companion": "outputs/diagnostics/figures/proxy/proxy_threshold_status_counts.png",
        },
        "outputs/models/surface/surface_total_rust_pct/group_shuffle/surface_total_rust_pct_feature_importance.png": {
            "purpose": "Surface benchmark feature importance.",
            "quality_assessment": "misleading",
            "action": "discard",
            "reason": "The target is a label-reconstruction sanity check, so this plot can be overread as model discovery.",
            "replacement_or_companion": "outputs/diagnostics/figures/features/feature_target_correlation_heatmap.png",
        },
        "outputs/models/surface/peak_rust_pct/group_shuffle/peak_rust_pct_feature_importance.png": {
            "purpose": "Peak-rust surface feature importance.",
            "quality_assessment": "useful but needs improvement",
            "action": "revise",
            "reason": "Keep only with the new ranked companion and strategy-robustness plots.",
            "replacement_or_companion": "outputs/diagnostics/figures/benchmarks/feature_importance/surface/peak_rust_pct/peak_rust_pct_group_shuffle_feature_importance_ranked.png",
        },
        "outputs/models/hidden_damage/wire_area_loss_frac/group_shuffle/wire_area_loss_frac_feature_importance.png": {
            "purpose": "Hidden-damage feature importance.",
            "quality_assessment": "useful but needs improvement",
            "action": "keep",
            "reason": "Keep as appendix only; pair it with stability and weakness diagnostics.",
            "replacement_or_companion": "outputs/diagnostics/figures/benchmarks/hidden_damage_best_model_strategy_robustness.png",
        },
        "outputs/models/hidden_damage/ultimate_load_kn/group_shuffle/ultimate_load_kn_feature_importance.png": {
            "purpose": "Ultimate-load feature importance.",
            "quality_assessment": "useful but needs improvement",
            "action": "revise",
            "reason": "The ranking is readable, but it needs the new residual and robustness context to avoid overclaiming.",
            "replacement_or_companion": "outputs/diagnostics/figures/benchmarks/predictions/hidden_damage/ultimate_load_kn/ultimate_load_kn_group_shuffle_prediction_diagnostics.png",
        },
    }
    rows = []
    all_figures = sorted(str(path.relative_to(ROOT_DIR)) for path in OUTPUT_DIR.rglob("*.png"))
    for figure_path in all_figures:
        if figure_path in review_map:
            rows.append({"figure_path": figure_path, **review_map[figure_path]})
        elif figure_path in new_figures:
            rows.append(
                {
                    "figure_path": figure_path,
                    "purpose": "New diagnostics figure.",
                    "quality_assessment": "new diagnostics figure",
                    "action": "keep",
                    "reason": "Generated to add a direct visual companion to an important output table or benchmark summary.",
                    "replacement_or_companion": "",
                }
            )
        else:
            rows.append(
                {
                    "figure_path": figure_path,
                    "purpose": "Existing figure not promoted during this diagnostics pass.",
                    "quality_assessment": "useful but needs improvement",
                    "action": "revise",
                    "reason": "Not selected as one of the strongest communication figures; keep only as appendix until reviewed more deeply.",
                    "replacement_or_companion": "",
                }
            )
    return pd.DataFrame(rows)


def write_markdown_reports(
    feature_tables: dict[str, pd.DataFrame],
    dist_tables: dict[str, pd.DataFrame],
    benchmark_tables: dict[str, pd.DataFrame],
    degradation_tables: dict[str, pd.DataFrame],
    proxy_tables: dict[str, pd.DataFrame],
    output_inventory_df: pd.DataFrame,
    figure_inventory_df: pd.DataFrame,
) -> None:
    feature_corr = feature_tables["feature_target_correlation_summary"]
    near_constant_df = feature_tables["near_constant_features"]
    duplicate_df = feature_tables["duplicate_feature_pairs"]
    collinear_df = feature_tables["high_collinearity_pairs"]
    best_robustness = benchmark_tables["benchmark_best_model_robustness"]
    surface_top = feature_corr.loc[feature_corr["target"] == "surface_total_rust_pct"].head(1)
    hidden_top = feature_corr.loc[feature_corr["target"] == "wire_area_loss_frac"].head(1)
    ultimate_campaign = best_robustness.loc[
        (best_robustness["target"] == "ultimate_load_kn")
        & (best_robustness["strategy"] == "leave_one_campaign_out")
    ].head(1)
    wire_group = best_robustness.loc[
        (best_robustness["target"] == "wire_area_loss_frac")
        & (best_robustness["strategy"] == "group_shuffle")
    ].head(1)

    output_lines = [
        "# Output Visualization Plan",
        "",
        "This plan maps each major existing output to either a matching figure or an explicit statement that a plot is not meaningful.",
        "",
        dataframe_to_markdown(output_inventory_df, index=False),
    ]
    write_text(ROOT_DIR / "outputs/diagnostics/OUTPUT_VISUALIZATION_PLAN.md", "\n".join(output_lines))

    feature_lines = [
        "# Feature Diagnostics",
        "",
        "## What Was Generated",
        "",
        "- feature inventory by stage",
        "- feature missingness and variance summaries",
        "- near-constant feature detection",
        "- duplicate and high-collinearity checks",
        "- focused feature-feature and feature-target correlation plots",
        "",
        "## Highest-Priority Findings",
        "",
        f"- Near-constant columns detected: {len(near_constant_df)} rows in `outputs/diagnostics/tables/near_constant_features.csv`.",
        f"- Exact duplicate feature pairs detected: {len(duplicate_df)}.",
        f"- High-collinearity pairs (|Spearman| >= 0.95): {len(collinear_df)}.",
        "- The collinearity figure prioritizes image-image pairs so the redundancy inside the image pipeline is visible at a glance; the CSV still keeps all pairs, including metadata and time variables.",
        f"- `surface_total_rust_pct` is almost numerically identical to `{surface_top.iloc[0]['feature_name']}` (Spearman {surface_top.iloc[0]['spearman_corr']:.4f}), which reinforces the existing label-reconstruction framing.",
        f"- The strongest univariate relationship with `wire_area_loss_frac` is only {hidden_top.iloc[0]['spearman_abs_corr']:.4f}, so the hidden-damage stage remains weak even before model fitting.",
        "- Focused heatmaps were used instead of one giant unreadable matrix.",
        "",
        "## Strongest Feature-Target Relationships",
        "",
        dataframe_to_markdown(feature_corr.groupby("target").head(5), index=False),
        "",
        "## Key Supporting Outputs",
        "",
        "- `outputs/diagnostics/tables/feature_inventory_by_stage.csv`",
        "- `outputs/diagnostics/tables/feature_missingness_summary.csv`",
        "- `outputs/diagnostics/tables/feature_variance_summary.csv`",
        "- `outputs/diagnostics/tables/near_constant_features.csv`",
        "- `outputs/diagnostics/tables/duplicate_feature_pairs.csv`",
        "- `outputs/diagnostics/tables/high_collinearity_pairs.csv`",
        "- `outputs/diagnostics/tables/feature_target_correlation_summary.csv`",
    ]
    write_text(ROOT_DIR / "outputs/diagnostics/FEATURE_DIAGNOSTICS.md", "\n".join(feature_lines))

    benchmark_lines = [
        "# Benchmark Diagnostics",
        "",
        "## What Was Generated",
        "",
        "- consolidated benchmark summary table across stages, targets, and strategies",
        "- consolidated fold-level benchmark table",
        "- split-composition diagnostics",
        "- group-shuffle model-comparison plots",
        "- best-model robustness plots across split strategies",
        "- fold-stability plots for the selected best models",
        "- a relative-MAE collapse heatmap",
        "- saved prediction diagnostics for every predictions CSV",
        "- saved ranked bar plots for every feature-importance CSV",
        "",
        "## Best-Model Robustness Snapshot",
        "",
        dataframe_to_markdown(best_robustness, index=False),
        "",
        "## Interpretation",
        "",
        "- These plots emphasize robustness and collapse, not only the lowest average MAE.",
        "- Leave-one-campaign-out is the clearest stress test for scientific generalization in this project.",
        "- Fold-stability plots should be consulted before claiming one model is meaningfully better than another.",
        f"- `ultimate_load_kn` degrades sharply under leave-one-campaign-out: relative MAE rises to {ultimate_campaign.iloc[0]['relative_mae_vs_group_shuffle']:.2f}x the group-shuffle baseline.",
        f"- `wire_area_loss_frac` remains weak even in the best grouped setting: best-model Spearman is only {wire_group.iloc[0]['spearman_mean']:.3f}.",
        "- Surface-stage prediction diagnostics are useful for communication, but `surface_total_rust_pct` should still be treated as a sanity-check target rather than a discovery result.",
        "",
        "## Key Supporting Outputs",
        "",
        "- `outputs/diagnostics/tables/benchmark_summary_long.csv`",
        "- `outputs/diagnostics/tables/benchmark_fold_metrics_long.csv`",
        "- `outputs/diagnostics/tables/benchmark_best_model_robustness.csv`",
        "- `outputs/diagnostics/tables/split_summary_long.csv`",
    ]
    write_text(ROOT_DIR / "outputs/diagnostics/BENCHMARK_DIAGNOSTICS.md", "\n".join(benchmark_lines))

    figure_lines = [
        "# Figure Review",
        "",
        "Existing figures were reviewed for presentation quality and whether a clearer replacement was needed.",
        "",
        dataframe_to_markdown(
            figure_inventory_df.loc[figure_inventory_df["figure_path"].str.startswith("outputs/")],
            index=False,
        ),
    ]
    write_text(ROOT_DIR / "outputs/diagnostics/FIGURE_REVIEW.md", "\n".join(figure_lines))


def run_diagnostics() -> dict[str, list[str]]:
    for path in [
        DIAG_TABLE_DIR,
        FEATURE_FIG_DIR,
        DISTRIBUTION_FIG_DIR,
        TEMPORAL_FIG_DIR,
        BENCHMARK_FIG_DIR,
        DEGRADATION_FIG_DIR,
        PROXY_FIG_DIR,
        INVENTORY_FIG_DIR,
    ]:
        ensure_dir(path)

    master_df = pd.read_csv(OUTPUT_DIR / "data" / "master_table.csv", parse_dates=["calendar_date"])
    image_feature_df = pd.read_csv(OUTPUT_DIR / "features" / "image_features.csv")
    full_feature_df = pd.read_csv(OUTPUT_DIR / "data" / "full_feature_table.csv")

    feature_tables = build_feature_diagnostic_tables(full_feature_df)
    if "img_rust_area_ratio_pct" not in full_feature_df.columns:
        full_feature_df = full_feature_df.merge(
            image_feature_df.drop(columns=["specimen_id", "image_path"], errors="ignore"),
            on="sample_name",
            how="left",
            validate="one_to_one",
        )
    distribution_tables = build_distribution_tables(
        pd.read_csv(OUTPUT_DIR / "models" / "degradation" / "full_feature_table_with_hidden_damage_proxy.csv")
    )
    summary_df, fold_df, split_df = load_summary_long()
    benchmark_tables = {
        "benchmark_summary_long": summary_df,
        "benchmark_fold_metrics_long": fold_df,
        "split_summary_long": split_df,
    }
    benchmark_figures, best_robustness = plot_benchmark_diagnostics(summary_df, fold_df, split_df)
    benchmark_tables["benchmark_best_model_robustness"] = best_robustness

    degradation_tables = build_degradation_tables()
    proxy_tables = build_proxy_tables()

    write_csv_bundle(feature_tables)
    write_csv_bundle(distribution_tables)
    write_csv_bundle(benchmark_tables)
    write_csv_bundle(degradation_tables)
    write_csv_bundle(proxy_tables)

    feature_figures = []
    feature_figures.extend(plot_feature_inventory(feature_tables["feature_inventory_by_stage"]))
    feature_figures.extend(plot_feature_quality(full_feature_df, feature_tables))

    distribution_figures = plot_distribution_diagnostics(
        pd.read_csv(OUTPUT_DIR / "models" / "degradation" / "full_feature_table_with_hidden_damage_proxy.csv"),
        distribution_tables,
    )
    temporal_figures, exposure_summary = plot_temporal_diagnostics(
        pd.read_csv(OUTPUT_DIR / "models" / "degradation" / "full_feature_table_with_hidden_damage_proxy.csv"),
        degradation_tables,
    )
    save_dataframe_csv(exposure_summary, DIAG_TABLE_DIR / "exposure_band_summary.csv")

    degradation_figures = plot_degradation_diagnostics(degradation_tables, master_df)
    proxy_figures = plot_proxy_diagnostics(proxy_tables)
    prediction_importance_figures = plot_prediction_and_importance_diagnostics()

    all_new_figures = (
        feature_figures
        + distribution_figures
        + temporal_figures
        + benchmark_figures
        + degradation_figures
        + proxy_figures
        + prediction_importance_figures
    )
    output_inventory_df = build_output_visualization_inventory()
    save_dataframe_csv(output_inventory_df, DIAG_TABLE_DIR / "output_visualization_inventory.csv")
    figure_inventory_df = build_figure_inventory(all_new_figures)
    save_dataframe_csv(figure_inventory_df, DIAG_TABLE_DIR / "figure_inventory.csv")

    write_markdown_reports(
        feature_tables,
        distribution_tables,
        benchmark_tables,
        degradation_tables,
        proxy_tables,
        output_inventory_df,
        figure_inventory_df,
    )

    return {
        "new_figures": all_new_figures,
        "new_tables": sorted(
            str(path.relative_to(ROOT_DIR))
            for path in DIAG_TABLE_DIR.glob("*.csv")
        ),
    }

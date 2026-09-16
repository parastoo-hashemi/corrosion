from __future__ import annotations

from pathlib import Path
import random

import numpy as np
import pandas as pd

from src.config import Settings, ensure_project_dirs
from src.data.canonical import build_canonical_dataset, export_canonical_dataset
from src.evaluation.reports import dataframe_to_markdown, write_markdown
from src.features.extractor import extract_image_features
from src.degradation.fitter import export_degradation_outputs, fit_degradation_curves
from src.logging_utils import get_logger
from src.models.common import evaluate_models, fit_full_pipeline, save_estimator, select_best_model
from src.models.corrosion import corrosion_classifier_factories, corrosion_regressor_factories
from src.models.damage import damage_regressor_factories
from src.rul.estimator import estimate_rul
from src.visualization.plots import (
    create_preprocessing_previews,
    plot_metric_bars,
    plot_regression_predictions,
    plot_risk_distribution,
    plot_rul_histogram,
    plot_trajectory_examples,
)


LOGGER = get_logger(__name__)
SPLIT_STRATEGIES = [
    "group_shuffle",
    "leave_one_treatment_out",
    "leave_one_campaign_out",
]


def set_global_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def load_canonical_dataset(settings: Settings) -> pd.DataFrame:
    path = settings.paths.outputs_dir / "canonical_dataset.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"Canonical dataset not found at {path}. Run scripts/02_build_metadata.py first."
        )
    return pd.read_parquet(path)


def load_feature_dataset(settings: Settings) -> pd.DataFrame:
    path = settings.paths.outputs_dir / "image_features.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"Image feature table not found at {path}. Run scripts/04_extract_features.py first."
        )
    return pd.read_parquet(path)


def inspection_markdown(summary: dict[str, object], issues: list[str]) -> str:
    issue_lines = "\n".join(f"- {issue}" for issue in issues) if issues else "- No structural dataset issues detected."
    campaigns = "\n".join(f"- `{campaign}`" for campaign in summary["campaigns"])
    return f"""# Dataset Inspection

## Summary
- Rows: **{summary['rows']}**
- Specimens: **{summary['unique_specimens']}**
- Treatments: **{', '.join(summary['treatments'])}**
- Campaigns: **{len(summary['campaigns'])}**
- Surface-labelled rows: **{summary['rows']}**
- Structural-labelled rows: **{summary['structural_rows']}**
- Structural label weeks: **{summary['structural_weeks']}**
- Week range: **{summary['week_min']} to {summary['week_max']}**

## Campaign IDs
{campaigns}

## Integrity Checks
{issue_lines}
"""


def run_dataset_inspection(settings: Settings) -> tuple[pd.DataFrame, dict[str, object], list[str]]:
    ensure_project_dirs(settings)
    set_global_seed(settings.project.seed)
    canonical_df, summary, issues = build_canonical_dataset(settings)
    report_path = settings.paths.reports_dir / "dataset_inspection.md"
    write_markdown(report_path, inspection_markdown(summary, issues))
    return canonical_df, summary, issues


def run_metadata_stage(settings: Settings) -> pd.DataFrame:
    canonical_df, summary, issues = run_dataset_inspection(settings)
    export_canonical_dataset(canonical_df, settings.paths.outputs_dir)
    summary_df = pd.DataFrame([summary])
    summary_df.to_csv(settings.paths.outputs_dir / "dataset_summary.csv", index=False)
    if issues:
        pd.DataFrame({"issue": issues}).to_csv(
            settings.paths.outputs_dir / "dataset_issues.csv", index=False
        )
    return canonical_df


def run_preprocessing_stage(settings: Settings) -> pd.DataFrame:
    canonical_df = load_canonical_dataset(settings)
    preview_dir = settings.paths.figures_dir / "preprocessing"
    preview_df = create_preprocessing_previews(
        canonical_df=canonical_df,
        settings=settings,
        output_dir=preview_dir,
        limit=settings.features.diagnostic_preview_limit,
    )
    preview_df.to_csv(settings.paths.outputs_dir / "preprocessing_previews.csv", index=False)
    return preview_df


def run_feature_stage(settings: Settings) -> pd.DataFrame:
    canonical_df = load_canonical_dataset(settings)
    feature_path = settings.paths.outputs_dir / "image_features.parquet"
    feature_df = extract_image_features(
        canonical_df=canonical_df,
        settings=settings,
        output_path=feature_path,
    )
    feature_df.to_csv(settings.paths.outputs_dir / "image_features.csv", index=False)
    return feature_df


def _feature_columns(feature_df: pd.DataFrame) -> list[str]:
    return [column for column in feature_df.columns if column != "record_id"]


def run_corrosion_stage(settings: Settings) -> dict[str, pd.DataFrame]:
    canonical_df = load_canonical_dataset(settings)
    feature_df = load_feature_dataset(settings)
    design_df = canonical_df.merge(feature_df, on="record_id", how="inner")
    feature_cols = _feature_columns(feature_df)

    regression_metrics_rows = []
    regression_prediction_rows = []
    classification_metrics_rows = []
    classification_prediction_rows = []
    state_estimates = design_df[["record_id"]].copy()

    for target in settings.targets.corrosion_regression:
        evaluation = evaluate_models(
            dataset=design_df,
            feature_cols=feature_cols,
            target_col=target,
            model_factories=corrosion_regressor_factories(),
            strategies=SPLIT_STRATEGIES,
            task="regression",
            random_state=settings.project.seed,
            test_size=settings.project.test_size,
        )
        regression_metrics_rows.append(evaluation.metrics)
        regression_prediction_rows.append(evaluation.predictions)
        best_model_name = select_best_model(evaluation.metrics, target_col=target, task="regression")
        final_estimator = fit_full_pipeline(
            dataset=design_df,
            feature_cols=feature_cols,
            target_col=target,
            model_factory=corrosion_regressor_factories()[best_model_name],
            random_state=settings.project.seed,
        )
        save_estimator(
            final_estimator,
            str(settings.paths.models_dir / f"corrosion_{target}_{best_model_name}.joblib"),
        )
        preds = np.asarray(final_estimator.predict(design_df[feature_cols]), dtype=float)
        state_estimates[f"pred_{target}"] = np.clip(preds, 0.0, 100.0)

    for target in settings.targets.corrosion_classification:
        evaluation = evaluate_models(
            dataset=design_df,
            feature_cols=feature_cols,
            target_col=target,
            model_factories=corrosion_classifier_factories(),
            strategies=SPLIT_STRATEGIES,
            task="classification",
            random_state=settings.project.seed,
            test_size=settings.project.test_size,
        )
        classification_metrics_rows.append(evaluation.metrics)
        classification_prediction_rows.append(evaluation.predictions)
        best_model_name = select_best_model(
            evaluation.metrics, target_col=target, task="classification"
        )
        final_estimator = fit_full_pipeline(
            dataset=design_df,
            feature_cols=feature_cols,
            target_col=target,
            model_factory=corrosion_classifier_factories()[best_model_name],
            random_state=settings.project.seed,
        )
        save_estimator(
            final_estimator,
            str(settings.paths.models_dir / f"corrosion_{target}_{best_model_name}.joblib"),
        )
        state_estimates[f"pred_{target}"] = (
            np.rint(final_estimator.predict(design_df[feature_cols])).astype(int)
        )

    regression_metrics = pd.concat(regression_metrics_rows, ignore_index=True)
    regression_predictions = pd.concat(regression_prediction_rows, ignore_index=True)
    classification_metrics = pd.concat(classification_metrics_rows, ignore_index=True)
    classification_predictions = pd.concat(classification_prediction_rows, ignore_index=True)
    state_estimates.to_parquet(settings.paths.outputs_dir / "corrosion_state_estimates.parquet", index=False)
    regression_metrics.to_csv(settings.paths.outputs_dir / "corrosion_regression_metrics.csv", index=False)
    regression_predictions.to_parquet(
        settings.paths.outputs_dir / "corrosion_regression_predictions.parquet",
        index=False,
    )
    classification_metrics.to_csv(
        settings.paths.outputs_dir / "corrosion_classification_metrics.csv", index=False
    )
    classification_predictions.to_parquet(
        settings.paths.outputs_dir / "corrosion_classification_predictions.parquet",
        index=False,
    )
    return {
        "regression_metrics": regression_metrics,
        "regression_predictions": regression_predictions,
        "classification_metrics": classification_metrics,
        "classification_predictions": classification_predictions,
        "state_estimates": state_estimates,
    }


def _damage_feature_columns(design_df: pd.DataFrame) -> list[str]:
    preferred = [
        "week",
        "n_steel_mesh",
        "ageing_days",
        "nacl_pct",
        "cover_failure_surface_mm",
        "treatment_code",
        "campaign_id",
        "series_label",
        "surface_total_rust_pct",
        "peak_rust_pct",
        "surface_total_rust_category",
        "peak_rust_category",
        "peak_rust_location_cm",
        "rust_area_pct_feature",
        "peak_rust_pct_feature",
        "peak_rust_location_cm_feature",
        "rust_distribution_std",
        "rust_component_count",
        "rust_component_largest_area_pct",
        "rust_score_mean",
        "rust_score_std",
        "edge_density",
        "texture_contrast_mean",
        "texture_homogeneity_mean",
        "texture_energy_mean",
        "lab_a_mean",
        "lab_b_mean",
        "hsv_s_mean",
        "hsv_v_mean",
    ]
    return [column for column in preferred if column in design_df.columns]


def run_damage_stage(settings: Settings) -> dict[str, pd.DataFrame]:
    canonical_df = load_canonical_dataset(settings)
    feature_df = load_feature_dataset(settings)
    corrosion_state = pd.read_parquet(
        settings.paths.outputs_dir / "corrosion_state_estimates.parquet"
    )
    design_df = canonical_df.merge(feature_df, on="record_id", how="inner").merge(
        corrosion_state, on="record_id", how="left"
    )
    structural_df = design_df[design_df["has_structural_labels"]].copy()
    feature_cols = _damage_feature_columns(structural_df)

    metrics_rows = []
    prediction_rows = []
    state_estimates = design_df[["record_id"]].copy()

    for target in settings.targets.damage_regression:
        evaluation = evaluate_models(
            dataset=structural_df,
            feature_cols=feature_cols,
            target_col=target,
            model_factories=damage_regressor_factories(),
            strategies=SPLIT_STRATEGIES,
            task="regression",
            random_state=settings.project.seed,
            test_size=settings.project.test_size,
        )
        metrics_rows.append(evaluation.metrics)
        prediction_rows.append(evaluation.predictions)
        best_model_name = select_best_model(evaluation.metrics, target_col=target, task="regression")
        final_estimator = fit_full_pipeline(
            dataset=structural_df,
            feature_cols=feature_cols,
            target_col=target,
            model_factory=damage_regressor_factories()[best_model_name],
            random_state=settings.project.seed,
        )
        save_estimator(
            final_estimator,
            str(settings.paths.models_dir / f"damage_{target}_{best_model_name}.joblib"),
        )
        pred_col = "estimated_wire_area_loss_pct" if target == "wire_area_loss_pct" else "estimated_ultimate_load_kn"
        preds = np.asarray(final_estimator.predict(design_df[feature_cols]), dtype=float)
        if pred_col == "estimated_wire_area_loss_pct":
            preds = np.clip(preds, 0.0, 100.0)
        else:
            preds = np.clip(preds, 0.0, None)
        state_estimates[pred_col] = preds

    metrics_df = pd.concat(metrics_rows, ignore_index=True)
    predictions_df = pd.concat(prediction_rows, ignore_index=True)
    state_estimates.to_parquet(settings.paths.outputs_dir / "damage_state_estimates.parquet", index=False)
    metrics_df.to_csv(settings.paths.outputs_dir / "damage_regression_metrics.csv", index=False)
    predictions_df.to_parquet(
        settings.paths.outputs_dir / "damage_regression_predictions.parquet",
        index=False,
    )
    return {
        "metrics": metrics_df,
        "predictions": predictions_df,
        "state_estimates": state_estimates,
    }


def run_degradation_stage(settings: Settings) -> dict[str, pd.DataFrame]:
    canonical_df = load_canonical_dataset(settings)
    damage_state = pd.read_parquet(settings.paths.outputs_dir / "damage_state_estimates.parquet")
    state_df = canonical_df.merge(damage_state, on="record_id", how="left")
    fits_df, forecasts_df = fit_degradation_curves(state_df=state_df, settings=settings)
    export_degradation_outputs(fits_df, forecasts_df, settings.paths.outputs_dir)
    return {"fits": fits_df, "forecasts": forecasts_df}


def run_rul_stage(settings: Settings) -> dict[str, pd.DataFrame]:
    canonical_df = load_canonical_dataset(settings)
    damage_state = pd.read_parquet(settings.paths.outputs_dir / "damage_state_estimates.parquet")
    forecast_df = pd.read_parquet(settings.paths.outputs_dir / "degradation_forecasts.parquet")
    state_df = canonical_df.merge(damage_state, on="record_id", how="left")
    estimates_df, trajectories_df = estimate_rul(
        state_df=state_df,
        forecast_df=forecast_df,
        settings=settings,
    )
    estimates_df.to_csv(settings.paths.outputs_dir / "rul_estimates.csv", index=False)
    estimates_df.to_parquet(settings.paths.outputs_dir / "rul_estimates.parquet", index=False)
    trajectories_df.to_parquet(settings.paths.outputs_dir / "rul_trajectories.parquet", index=False)
    return {"estimates": estimates_df, "trajectories": trajectories_df}


def run_report_stage(settings: Settings) -> dict[str, Path]:
    canonical_df = load_canonical_dataset(settings)
    regression_metrics = pd.read_csv(settings.paths.outputs_dir / "corrosion_regression_metrics.csv")
    classification_metrics = pd.read_csv(
        settings.paths.outputs_dir / "corrosion_classification_metrics.csv"
    )
    corrosion_predictions = pd.read_parquet(
        settings.paths.outputs_dir / "corrosion_regression_predictions.parquet"
    )
    damage_metrics = pd.read_csv(settings.paths.outputs_dir / "damage_regression_metrics.csv")
    damage_predictions = pd.read_parquet(
        settings.paths.outputs_dir / "damage_regression_predictions.parquet"
    )
    degradation_forecasts = pd.read_parquet(
        settings.paths.outputs_dir / "degradation_forecasts.parquet"
    )
    rul_df = pd.read_parquet(settings.paths.outputs_dir / "rul_estimates.parquet")

    figure_paths = {
        "corrosion_regression": plot_regression_predictions(
            corrosion_predictions[corrosion_predictions["strategy"] == "group_shuffle"],
            settings.paths.figures_dir / "corrosion_regression_parity.png",
            "Corrosion regression parity",
        ),
        "corrosion_metrics": plot_metric_bars(
            regression_metrics[regression_metrics["strategy"] == "group_shuffle"],
            metric_col="mae",
            out_path=settings.paths.figures_dir / "corrosion_model_mae.png",
            title="Corrosion model comparison",
        ),
        "corrosion_classification": plot_metric_bars(
            classification_metrics[classification_metrics["strategy"] == "group_shuffle"],
            metric_col="macro_f1",
            out_path=settings.paths.figures_dir / "corrosion_model_macro_f1.png",
            title="Corrosion classification comparison",
        ),
        "damage_regression": plot_regression_predictions(
            damage_predictions[damage_predictions["strategy"] == "group_shuffle"],
            settings.paths.figures_dir / "damage_regression_parity.png",
            "Damage regression parity",
        ),
        "damage_metrics": plot_metric_bars(
            damage_metrics[damage_metrics["strategy"] == "group_shuffle"],
            metric_col="mae",
            out_path=settings.paths.figures_dir / "damage_model_mae.png",
            title="Damage model comparison",
        ),
        "risk_distribution": plot_risk_distribution(
            rul_df, settings.paths.figures_dir / "risk_distribution.png"
        ),
        "rul_histogram": plot_rul_histogram(
            rul_df, settings.paths.figures_dir / "rul_histogram.png"
        ),
    }
    top_risk_specimens = rul_df.sort_values(
        ["failure_probability", "estimated_rul_weeks"], ascending=[False, True]
    )["specimen_id"].head(6).tolist()
    if top_risk_specimens:
        figure_paths["degradation_examples"] = plot_trajectory_examples(
            degradation_forecasts,
            settings.paths.figures_dir / "degradation_examples_peak_rust.png",
            target="peak_rust_pct",
            specimen_ids=top_risk_specimens,
        )

    summary_text = f"""# Pipeline Summary

## Dataset
- Canonical rows: **{len(canonical_df)}**
- Specimens: **{canonical_df['specimen_id'].nunique()}**
- Campaigns: **{canonical_df['campaign_id'].nunique()}**
- Structural rows: **{int(canonical_df['has_structural_labels'].sum())}**

## Corrosion Models
### Regression
{dataframe_to_markdown(regression_metrics[regression_metrics['strategy'] == 'group_shuffle'])}

### Classification
{dataframe_to_markdown(classification_metrics[classification_metrics['strategy'] == 'group_shuffle'])}

## Damage Models
{dataframe_to_markdown(damage_metrics[damage_metrics['strategy'] == 'group_shuffle'])}

## RUL Summary
- Low risk specimens: **{int((rul_df['risk_class'] == 'Low').sum())}**
- Moderate risk specimens: **{int((rul_df['risk_class'] == 'Moderate').sum())}**
- High risk specimens: **{int((rul_df['risk_class'] == 'High').sum())}**
- Critical specimens: **{int((rul_df['risk_class'] == 'Critical').sum())}**
- Median proxy-RUL (weeks): **{float(rul_df['estimated_rul_weeks'].dropna().median() if rul_df['estimated_rul_weeks'].dropna().size else float('nan')):.2f}**

## Figures
{chr(10).join(f"- `{name}`: `{path}`" for name, path in figure_paths.items())}
"""
    write_markdown(settings.paths.reports_dir / "pipeline_summary.md", summary_text)
    return figure_paths

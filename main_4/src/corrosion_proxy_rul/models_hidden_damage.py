from __future__ import annotations

from pathlib import Path

import pandas as pd

from .evaluation import benchmark_models
from .feature_engineering import (
    HIDDEN_DAMAGE_FEATURE_SETS,
    build_hidden_damage_feature_set,
    build_hidden_damage_feature_table,
)
from .splits import build_split_manifests, split_summary
from .utils_paths import ensure_dir, save_dataframe_csv
from .visualization import save_feature_importance_plot


STRUCTURAL_TARGETS = ["wire_area_loss_frac", "ultimate_load_kn"]


def _experiment_dir(target_dir: Path, feature_set_name: str, target_transform: str) -> Path:
    return ensure_dir(target_dir / "experiments" / f"{feature_set_name}__{target_transform}")


def _evaluate_hidden_damage_experiments(hidden_df, configs, manifests, output_dir: Path):
    modeling_cfg = configs["modeling"]
    cleanup_cfg = modeling_cfg["feature_cleanup"]
    hidden_cfg = modeling_cfg["hidden_damage"]
    near_constant_threshold = float(cleanup_cfg["near_constant_top_value_fraction"])
    correlation_threshold = float(cleanup_cfg["high_collinearity_threshold"])
    feature_sets = list(hidden_cfg["feature_sets"])
    selection_feature_sets = set(hidden_cfg["selection_feature_sets"])

    experiment_rows = []
    feature_inventory_rows = []

    for target in STRUCTURAL_TARGETS:
        target_dir = ensure_dir(output_dir / target)
        target_transforms = hidden_cfg["target_transforms"].get(target, ["none"])

        for feature_set_name in feature_sets:
            feature_cols, inventory_df = build_hidden_damage_feature_set(
                hidden_df,
                target,
                feature_set_name,
                near_constant_threshold=near_constant_threshold,
                correlation_threshold=correlation_threshold,
            )
            inventory_df = inventory_df.copy()
            inventory_df.insert(0, "target", target)
            inventory_df.insert(1, "n_selected_features", len(feature_cols))
            inventory_df.insert(
                2,
                "selection_candidate",
                feature_set_name in selection_feature_sets,
            )
            feature_inventory_rows.append(inventory_df)

            if not feature_cols:
                continue

            for target_transform in target_transforms:
                exp_dir = _experiment_dir(target_dir, feature_set_name, target_transform)
                for strategy, manifest_df in manifests.items():
                    result = benchmark_models(
                        hidden_df,
                        feature_cols,
                        target,
                        manifest_df,
                        modeling_cfg,
                        exp_dir / strategy,
                        target_transform=target_transform,
                    )
                    summary_df = result["summary"].copy()
                    summary_df["strategy"] = strategy
                    summary_df["feature_set_name"] = feature_set_name
                    summary_df["feature_set_description"] = HIDDEN_DAMAGE_FEATURE_SETS[feature_set_name]
                    summary_df["n_features"] = len(feature_cols)
                    summary_df["selection_candidate"] = feature_set_name in selection_feature_sets
                    experiment_rows.append(summary_df)

    experiment_df = pd.concat(experiment_rows, ignore_index=True).reset_index(drop=True)
    feature_inventory_df = pd.concat(feature_inventory_rows, ignore_index=True).reset_index(drop=True)
    return experiment_df, feature_inventory_df


def _select_robust_configs(experiment_df: pd.DataFrame, configs) -> pd.DataFrame:
    weights = configs["modeling"]["hidden_damage"]["robustness_weights"]
    rows = []
    for target in STRUCTURAL_TARGETS:
        target_df = experiment_df.loc[
            (experiment_df["target"] == target) & (experiment_df["selection_candidate"])
        ].copy()
        if target_df.empty:
            continue
        pivot = target_df.pivot_table(
            index=["target", "feature_set_name", "model_name", "target_transform", "n_features"],
            columns="strategy",
            values=["mae_mean", "rmse_mean", "r2_mean", "spearman_mean"],
            aggfunc="main_first",
        )
        pivot.columns = [f"{metric}_{strategy}" for metric, strategy in pivot.columns]
        pivot = pivot.reset_index()
        for strategy in ["group_shuffle", "leave_one_treatment_out", "leave_one_campaign_out"]:
            pivot[f"mae_rank_{strategy}"] = pivot[f"mae_mean_{strategy}"].rank(
                method="min",
                ascending=True,
                na_option="bottom",
            )
        pivot["spearman_rank_group_shuffle"] = pivot["spearman_mean_group_shuffle"].rank(
            method="min",
            ascending=False,
            na_option="bottom",
        )
        pivot["robustness_score"] = (
            weights["group_shuffle_mae_rank"] * pivot["mae_rank_group_shuffle"]
            + weights["leave_one_treatment_out_mae_rank"] * pivot["mae_rank_leave_one_treatment_out"]
            + weights["leave_one_campaign_out_mae_rank"] * pivot["mae_rank_leave_one_campaign_out"]
            + weights["group_shuffle_spearman_rank"] * pivot["spearman_rank_group_shuffle"]
        )
        pivot = pivot.sort_values(
            [
                "robustness_score",
                "mae_mean_leave_one_campaign_out",
                "mae_mean_leave_one_treatment_out",
                "mae_mean_group_shuffle",
                "spearman_mean_group_shuffle",
            ],
            ascending=[True, True, True, True, False],
        ).reset_index(drop=True)
        pivot["selected_for_deployment"] = False
        pivot.loc[0, "selected_for_deployment"] = True
        rows.append(pivot)
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def _build_feature_ablation_table(experiment_df: pd.DataFrame) -> pd.DataFrame:
    return (
        experiment_df.sort_values(
            ["target", "feature_set_name", "strategy", "mae_mean", "spearman_mean"],
            ascending=[True, True, True, True, False],
        )
        .groupby(["target", "feature_set_name", "strategy"], as_index=False)
        .first()
        .reset_index(drop=True)
    )


def _build_campaign_confounding_table(feature_ablation_df: pd.DataFrame) -> pd.DataFrame:
    baseline = (
        feature_ablation_df.loc[feature_ablation_df["feature_set_name"] == "all_cleaned"][
            ["target", "strategy", "mae_mean", "spearman_mean"]
        ]
        .rename(
            columns={
                "mae_mean": "all_cleaned_mae_mean",
                "spearman_mean": "all_cleaned_spearman_mean",
            }
        )
        .reset_index(drop=True)
    )
    comparison = feature_ablation_df.merge(baseline, on=["target", "strategy"], how="left")
    comparison["delta_mae_vs_all_cleaned"] = (
        comparison["mae_mean"] - comparison["all_cleaned_mae_mean"]
    )
    comparison["delta_spearman_vs_all_cleaned"] = (
        comparison["spearman_mean"] - comparison["all_cleaned_spearman_mean"]
    )
    return comparison.sort_values(["target", "strategy", "feature_set_name"]).reset_index(drop=True)


def _finalize_target_outputs(
    hidden_df: pd.DataFrame,
    target: str,
    selected_row: pd.Series,
    manifests: dict[str, pd.DataFrame],
    configs,
    output_dir: Path,
):
    modeling_cfg = configs["modeling"]
    cleanup_cfg = modeling_cfg["feature_cleanup"]
    feature_cols, inventory_df = build_hidden_damage_feature_set(
        hidden_df,
        target,
        selected_row["feature_set_name"],
        near_constant_threshold=float(cleanup_cfg["near_constant_top_value_fraction"]),
        correlation_threshold=float(cleanup_cfg["high_collinearity_threshold"]),
    )
    target_dir = ensure_dir(output_dir / target)
    save_dataframe_csv(
        inventory_df.assign(target=target),
        target_dir / f"{target}_feature_inventory.csv",
    )
    selected_features_df = pd.DataFrame(
        {
            "target": target,
            "feature_name": feature_cols,
            "feature_set_name": selected_row["feature_set_name"],
            "target_transform": selected_row["target_transform"],
            "source_family": pd.Series(feature_cols).map(
                lambda value: inventory_df.loc[
                    inventory_df["feature_name"] == value,
                    "source_family",
                ].iloc[0]
            ),
        }
    )
    save_dataframe_csv(selected_features_df, target_dir / f"{target}_selected_features.csv")

    group_result = benchmark_models(
        hidden_df,
        feature_cols,
        target,
        manifests["group_shuffle"],
        modeling_cfg,
        target_dir / "group_shuffle",
        target_transform=selected_row["target_transform"],
        selected_model_name=selected_row["model_name"],
    )
    if not group_result["importance"].empty:
        save_feature_importance_plot(
            group_result["importance"],
            (
                f"{target} feature importance "
                f"({selected_row['model_name']}, {selected_row['feature_set_name']}, {selected_row['target_transform']})"
            ),
            target_dir / "group_shuffle" / f"{target}_feature_importance.png",
        )

    for strategy in ["leave_one_treatment_out", "leave_one_campaign_out"]:
        benchmark_models(
            hidden_df,
            feature_cols,
            target,
            manifests[strategy],
            modeling_cfg,
            target_dir / strategy,
            target_transform=selected_row["target_transform"],
            selected_model_name=selected_row["model_name"],
        )
    return selected_features_df


def run_hidden_damage_models(feature_df, configs, output_dir: Path):
    ensure_dir(output_dir)
    outputs_root = output_dir.parent.parent
    improvements_table_dir = ensure_dir(outputs_root / "improvements" / "tables")

    hidden_df = build_hidden_damage_feature_table(feature_df)
    save_dataframe_csv(hidden_df, output_dir / "hidden_damage_feature_table.csv")

    split_cfg = configs["modeling"]["group_shuffle"]
    manifests = build_split_manifests(
        hidden_df,
        group_col="specimen_id",
        treatment_col="split_group_treatment",
        campaign_col="campaign_id",
        n_splits=split_cfg["n_splits"],
        test_size=split_cfg["test_size"],
        random_state=configs["modeling"]["random_state"],
    )
    split_output = ensure_dir(output_dir / "splits")
    for strategy, manifest_df in manifests.items():
        save_dataframe_csv(manifest_df, split_output / f"{strategy}.csv")
        save_dataframe_csv(split_summary(manifest_df), split_output / f"{strategy}_summary.csv")

    experiment_df, feature_inventory_df = _evaluate_hidden_damage_experiments(
        hidden_df,
        configs,
        manifests,
        output_dir,
    )
    save_dataframe_csv(experiment_df, output_dir / "hidden_damage_experiment_summary.csv")
    save_dataframe_csv(feature_inventory_df, output_dir / "hidden_damage_feature_inventory.csv")
    save_dataframe_csv(experiment_df, improvements_table_dir / "hidden_damage_experiment_summary.csv")
    save_dataframe_csv(feature_inventory_df, improvements_table_dir / "improved_hidden_damage_feature_inventory.csv")

    robustness_df = _select_robust_configs(experiment_df, configs)
    save_dataframe_csv(robustness_df, output_dir / "hidden_damage_robustness_selection.csv")
    save_dataframe_csv(robustness_df, improvements_table_dir / "hidden_damage_robustness_selection.csv")

    feature_ablation_df = _build_feature_ablation_table(experiment_df)
    campaign_confounding_df = _build_campaign_confounding_table(feature_ablation_df)
    save_dataframe_csv(feature_ablation_df, output_dir / "hidden_damage_feature_ablation_results.csv")
    save_dataframe_csv(campaign_confounding_df, output_dir / "hidden_damage_campaign_confounding.csv")
    save_dataframe_csv(feature_ablation_df, improvements_table_dir / "feature_ablation_results.csv")
    save_dataframe_csv(campaign_confounding_df, improvements_table_dir / "campaign_confounding_comparison.csv")

    best_rows = []
    selected_feature_rows = []
    for target in STRUCTURAL_TARGETS:
        selected_row = robustness_df.loc[
            (robustness_df["target"] == target) & (robustness_df["selected_for_deployment"])
        ].iloc[0]
        selected_features_df = _finalize_target_outputs(
            hidden_df,
            target,
            selected_row,
            manifests,
            configs,
            output_dir,
        )
        selected_feature_rows.append(selected_features_df)
        best_rows.append(
            {
                "target": target,
                "best_model_name": selected_row["model_name"],
                "feature_set_name": selected_row["feature_set_name"],
                "target_transform": selected_row["target_transform"],
                "n_features": int(selected_row["n_features"]),
                "robustness_score": float(selected_row["robustness_score"]),
                "group_shuffle_mae_mean": float(selected_row["mae_mean_group_shuffle"]),
                "leave_one_treatment_out_mae_mean": float(selected_row["mae_mean_leave_one_treatment_out"]),
                "leave_one_campaign_out_mae_mean": float(selected_row["mae_mean_leave_one_campaign_out"]),
                "group_shuffle_spearman_mean": float(selected_row["spearman_mean_group_shuffle"]),
            }
        )

    best_df = pd.DataFrame(best_rows)
    save_dataframe_csv(best_df, output_dir / "best_models.csv")
    save_dataframe_csv(best_df, improvements_table_dir / "improved_hidden_damage_selected_models.csv")
    save_dataframe_csv(
        pd.concat(selected_feature_rows, ignore_index=True),
        output_dir / "hidden_damage_selected_feature_list.csv",
    )
    return hidden_df, best_df

from __future__ import annotations

import json
import sys

import pandas as pd

sys.path.insert(0, "src")

from corrosion_proxy_rul.reporting import write_readme, write_scientific_report
from corrosion_proxy_rul.utils_paths import OUTPUT_DIR, ROOT_DIR, configure_logging, ensure_dir, save_dataframe_csv, write_text


STRATEGIES = ["group_shuffle", "leave_one_treatment_out", "leave_one_campaign_out"]
TARGETS = ["wire_area_loss_frac", "ultimate_load_kn"]


def _selected_row(model_dir, best_df: pd.DataFrame, target: str, strategy: str) -> dict:
    best_row = best_df.loc[best_df["target"] == target].iloc[0]
    summary_path = model_dir / target / strategy / f"{target}_summary.csv"
    summary_df = pd.read_csv(summary_path)
    model_name = best_row["best_model_name"]
    row = summary_df.loc[summary_df["model_name"] == model_name].iloc[0].to_dict()
    row["target"] = target
    row["strategy"] = strategy
    row["selected_model_name"] = model_name
    row["selected_feature_set_name"] = best_row.get("feature_set_name", "baseline_full_feature_space")
    row["selected_target_transform"] = best_row.get("target_transform", "none")
    row["selected_n_features"] = best_row.get("n_features", pd.NA)
    return row


def build_baseline_vs_improved_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    baseline_model_dir = OUTPUT_DIR / "improvements" / "baseline_snapshot" / "models" / "hidden_damage"
    current_model_dir = OUTPUT_DIR / "models" / "hidden_damage"

    baseline_best = pd.read_csv(baseline_model_dir / "best_models.csv")
    current_best = pd.read_csv(current_model_dir / "best_models.csv")

    comparison_rows = []
    for target in TARGETS:
        for strategy in STRATEGIES:
            baseline_row = _selected_row(baseline_model_dir, baseline_best, target, strategy)
            current_row = _selected_row(current_model_dir, current_best, target, strategy)
            comparison_rows.append(
                {
                    "target": target,
                    "strategy": strategy,
                    "baseline_model_name": baseline_row["selected_model_name"],
                    "baseline_feature_set_name": baseline_row["selected_feature_set_name"],
                    "baseline_target_transform": baseline_row["selected_target_transform"],
                    "baseline_n_features": baseline_row["selected_n_features"],
                    "baseline_mae_mean": baseline_row["mae_mean"],
                    "baseline_rmse_mean": baseline_row["rmse_mean"],
                    "baseline_r2_mean": baseline_row["r2_mean"],
                    "baseline_spearman_mean": baseline_row["spearman_mean"],
                    "improved_model_name": current_row["selected_model_name"],
                    "improved_feature_set_name": current_row["selected_feature_set_name"],
                    "improved_target_transform": current_row["selected_target_transform"],
                    "improved_n_features": current_row["selected_n_features"],
                    "improved_mae_mean": current_row["mae_mean"],
                    "improved_rmse_mean": current_row["rmse_mean"],
                    "improved_r2_mean": current_row["r2_mean"],
                    "improved_spearman_mean": current_row["spearman_mean"],
                    "delta_mae_mean": current_row["mae_mean"] - baseline_row["mae_mean"],
                    "delta_rmse_mean": current_row["rmse_mean"] - baseline_row["rmse_mean"],
                    "delta_r2_mean": current_row["r2_mean"] - baseline_row["r2_mean"],
                    "delta_spearman_mean": current_row["spearman_mean"] - baseline_row["spearman_mean"],
                }
            )
    comparison_df = pd.DataFrame(comparison_rows)

    robustness_rows = []
    for target in TARGETS:
        target_df = comparison_df.loc[comparison_df["target"] == target].copy()
        base_group = float(
            target_df.loc[target_df["strategy"] == "group_shuffle", "baseline_mae_mean"].iloc[0]
        )
        improved_group = float(
            target_df.loc[target_df["strategy"] == "group_shuffle", "improved_mae_mean"].iloc[0]
        )
        for row in target_df.itertuples(index=False):
            robustness_rows.append(
                {
                    "target": row.target,
                    "strategy": row.strategy,
                    "baseline_relative_mae_vs_group_shuffle": row.baseline_mae_mean / base_group,
                    "improved_relative_mae_vs_group_shuffle": row.improved_mae_mean / improved_group,
                    "delta_relative_mae_vs_group_shuffle": (row.improved_mae_mean / improved_group)
                    - (row.baseline_mae_mean / base_group),
                    "baseline_spearman_mean": row.baseline_spearman_mean,
                    "improved_spearman_mean": row.improved_spearman_mean,
                    "delta_spearman_mean": row.delta_spearman_mean,
                }
            )
    robustness_df = pd.DataFrame(robustness_rows)
    return comparison_df, robustness_df, current_best


def build_feature_inventory_comparison(current_best: pd.DataFrame) -> pd.DataFrame:
    baseline_inventory = pd.read_csv(
        OUTPUT_DIR / "improvements" / "baseline_snapshot" / "diagnostics" / "feature_inventory_by_stage.csv"
    )
    baseline_hidden = baseline_inventory.loc[
        (baseline_inventory["stage"] == "hidden_damage") & (baseline_inventory["included_in_stage"])
    ][["feature_name", "source_family"]].drop_duplicates()
    baseline_set = set(baseline_hidden["feature_name"].tolist())

    rows = []
    for target in TARGETS:
        current_inventory = pd.read_csv(
            OUTPUT_DIR / "models" / "hidden_damage" / target / f"{target}_feature_inventory.csv"
        )
        current_keep = current_inventory.loc[current_inventory["action"] == "keep"].copy()
        current_keep_set = set(current_keep["feature_name"].tolist())
        current_reason = (
            current_inventory.drop_duplicates("feature_name")
            .set_index("feature_name")["reason"]
            .to_dict()
        )
        current_family = (
            current_inventory.drop_duplicates("feature_name")
            .set_index("feature_name")["source_family"]
            .to_dict()
        )
        all_features = sorted(baseline_set | set(current_inventory["feature_name"].tolist()))
        for feature_name in all_features:
            baseline_included = feature_name in baseline_set
            improved_included = feature_name in current_keep_set
            if baseline_included and improved_included:
                change_type = "retained"
            elif baseline_included and not improved_included:
                change_type = "removed_in_improved"
            elif (not baseline_included) and improved_included:
                change_type = "new_in_improved"
            else:
                change_type = "not_selected_in_either"
            rows.append(
                {
                    "target": target,
                    "feature_name": feature_name,
                    "source_family": current_family.get(
                        feature_name,
                        baseline_hidden.loc[baseline_hidden["feature_name"] == feature_name, "source_family"].iloc[0]
                        if feature_name in baseline_set
                        else "unknown",
                    ),
                    "baseline_included": baseline_included,
                    "improved_included": improved_included,
                    "change_type": change_type,
                    "improved_reason": current_reason.get(feature_name, ""),
                    "improved_feature_set_name": current_best.loc[
                        current_best["target"] == target, "feature_set_name"
                    ].iloc[0],
                }
            )
    return pd.DataFrame(rows)


def build_degradation_proxy_summary() -> tuple[pd.DataFrame, pd.DataFrame]:
    baseline_deg = pd.read_csv(
        OUTPUT_DIR / "improvements" / "baseline_snapshot" / "models" / "degradation" / "degradation_best_fits.csv"
    )
    improved_deg = pd.read_csv(OUTPUT_DIR / "models" / "degradation" / "degradation_best_fits.csv")
    baseline_proxy = pd.read_csv(
        OUTPUT_DIR / "improvements" / "baseline_snapshot" / "models" / "proxy_rul" / "proxy_rul_summary.csv"
    )
    improved_proxy = pd.read_csv(OUTPUT_DIR / "models" / "proxy_rul" / "proxy_rul_summary.csv")

    deg_rows = []
    all_families = sorted(set(baseline_deg["best_family"]) | set(improved_deg["best_family"]))
    for family in all_families:
        deg_rows.append(
            {
                "best_family": family,
                "baseline_count": int((baseline_deg["best_family"] == family).sum()),
                "improved_count": int((improved_deg["best_family"] == family).sum()),
            }
        )
    deg_df = pd.DataFrame(deg_rows)

    proxy_df = baseline_proxy.merge(
        improved_proxy,
        on="threshold_wire_area_loss_frac",
        suffixes=("_baseline", "_improved"),
    )
    return deg_df, proxy_df


def write_improvement_docs(
    comparison_df: pd.DataFrame,
    robustness_df: pd.DataFrame,
    feature_compare_df: pd.DataFrame,
    degradation_df: pd.DataFrame,
    proxy_df: pd.DataFrame,
    current_best: pd.DataFrame,
) -> None:
    outputs_changed = [
        "outputs/models/hidden_damage/*",
        "outputs/models/degradation/*",
        "outputs/models/proxy_rul/*",
        "outputs/diagnostics/*",
        "outputs/improvements/tables/*",
        "SCIENTIFIC_REPORT.md",
    ]
    changed_files = [
        "MODEL_IMPROVEMENT_PLAN.md",
        "configs/modeling.yaml",
        "src/corrosion_proxy_rul/feature_engineering.py",
        "src/corrosion_proxy_rul/evaluation.py",
        "src/corrosion_proxy_rul/models_hidden_damage.py",
        "src/corrosion_proxy_rul/models_degradation.py",
        "src/corrosion_proxy_rul/models_rul_proxy.py",
        "src/corrosion_proxy_rul/reporting.py",
        "src/corrosion_proxy_rul/diagnostics.py",
        "run_model_improvement_analysis.py",
    ]

    applied_lines = [
        "# Model Improvements Applied",
        "",
        "## Changes Made",
        "",
        "- added hidden-damage feature-set cleanup with near-constant, duplicate, and high-collinearity filtering",
        "- added hidden-damage feature-family ablations and robustness-aware model selection across split strategies",
        "- allowed metadata-only hidden-damage models into final selection because they were more robust than image-heavy alternatives",
        "- regenerated degradation outputs from the improved hidden-damage stage",
        "- added raw-vs-monotone degradation trajectory artifacts and richer proxy threshold-status summaries",
        "",
        "## Files Changed",
        "",
    ]
    applied_lines.extend(f"- `{path}`" for path in changed_files)
    applied_lines.extend(
        [
            "",
            "## Stages Rerun",
            "",
            "- `conda run -n env python train_hidden_damage_models.py`",
            "- `conda run -n env python train_degradation_models.py`",
            "- `conda run -n env python train_rul_proxy_models.py`",
            "- `conda run -n env python run_diagnostics_visualizations.py`",
            "- `conda run -n env python run_model_improvement_analysis.py`",
            "",
            "## Outputs Regenerated",
            "",
        ]
    )
    applied_lines.extend(f"- `{path}`" for path in outputs_changed)
    applied_lines.extend(
        [
            "",
            "## Before vs After Snapshot",
            "",
            comparison_df.to_markdown(index=False),
            "",
            "## What Improved",
            "",
            "- `ultimate_load_kn` improved cleanly on absolute error across all three split strategies, with the largest gain under leave-one-campaign-out.",
            "- `wire_area_loss_frac` improved on leave-one-treatment-out and leave-one-campaign-out MAE, and grouped Spearman improved materially from a near-zero baseline.",
            "- both final hidden-damage models now use an explicit 8-feature metadata-only subset instead of the broader baseline feature space.",
            "",
            "## What Did Not Improve Cleanly",
            "",
            "- `wire_area_loss_frac` grouped MAE worsened after the robustness-oriented cleanup, so this should be treated as a trade-off rather than a net score win.",
            "- `wire_area_loss_frac` leave-one-campaign-out Spearman became more negative even though MAE improved, so ranking quality remains unreliable.",
            "- the stronger hidden-damage robustness comes from metadata-dominant models, not from stronger image-based structural inference.",
            "",
            "## Unresolved Weaknesses",
            "",
            "- `wire_area_loss_frac` remains weak in absolute predictive terms even though robustness improved",
            "- leave-one-campaign-out still fails badly enough that no deployment-grade hidden-damage claim is justified",
            "- the current best structural models rely on metadata-only feature sets, which shows that image features are not yet adding robust structural signal",
            "- degradation and proxy stages remain descriptive / exploratory downstream analyses",
        ]
    )
    write_text(ROOT_DIR / "MODEL_IMPROVEMENTS_APPLIED.md", "\n".join(applied_lines))

    results_lines = [
        "# Model Improvement Results",
        "",
        "## Hidden-Damage Benchmark Comparison Before vs After",
        "",
        comparison_df.to_markdown(index=False),
        "",
        "## Robustness Comparison Across Split Strategies",
        "",
        robustness_df.to_markdown(index=False),
        "",
        "## Feature-Space Reductions And Their Effects",
        "",
        f"- final selected feature counts: {current_best[['target', 'n_features', 'feature_set_name']].to_dict('records')}",
        f"- removed baseline broad hidden-damage feature space in favor of target-specific final selections documented in `outputs/models/hidden_damage/*/*_feature_inventory.csv`",
        "",
        "## Campaign-Confounding Findings",
        "",
        "- metadata-only feature sets were the most robust for both structural targets",
        "- this indicates that current robust structural signal comes mainly from exposure / treatment design metadata, not from engineered image features",
        "- image-heavy feature sets did not improve leave-one-campaign-out robustness",
        "",
        "## Degradation / Proxy Changes After Upstream Refinement",
        "",
        "Degradation family counts:",
        "",
        degradation_df.to_markdown(index=False),
        "",
        "Proxy threshold-status comparison:",
        "",
        proxy_df.to_markdown(index=False),
        "",
        "## Final Recommendation",
        "",
        (
            "The solution is genuinely better as a conservative structural baseline because the hidden-damage "
            "stage is now smaller, explicitly documented, and more robust on absolute error under the harder "
            "cross-campaign setting. That improvement is uneven: `ultimate_load_kn` improved cleanly, while "
            "`wire_area_loss_frac` traded better MAE for still-weak or worse ranking behavior. The improved "
            "models are metadata-dominant, so the project still does not support strong claims that surface "
            "image features robustly infer hidden damage."
        ),
    ]
    write_text(ROOT_DIR / "MODEL_IMPROVEMENT_RESULTS.md", "\n".join(results_lines))


def main() -> None:
    logger = configure_logging("run_model_improvement_analysis")
    tables_dir = ensure_dir(OUTPUT_DIR / "improvements" / "tables")

    comparison_df, robustness_df, current_best = build_baseline_vs_improved_tables()
    feature_compare_df = build_feature_inventory_comparison(current_best)
    degradation_df, proxy_df = build_degradation_proxy_summary()

    save_dataframe_csv(comparison_df, tables_dir / "baseline_vs_improved_benchmark_comparison.csv")
    save_dataframe_csv(feature_compare_df, tables_dir / "before_after_feature_inventory_comparison.csv")
    save_dataframe_csv(robustness_df, tables_dir / "split_strategy_robustness_comparison.csv")

    write_improvement_docs(
        comparison_df,
        robustness_df,
        feature_compare_df,
        degradation_df,
        proxy_df,
        current_best,
    )

    facts = json.loads((OUTPUT_DIR / "audit" / "verified_facts.json").read_text())
    surface_best = pd.read_csv(OUTPUT_DIR / "models" / "surface" / "best_models.csv")
    hidden_best = pd.read_csv(OUTPUT_DIR / "models" / "hidden_damage" / "best_models.csv")
    degradation_best = pd.read_csv(OUTPUT_DIR / "models" / "degradation" / "degradation_best_fits.csv")
    proxy_summary = pd.read_csv(OUTPUT_DIR / "models" / "proxy_rul" / "proxy_rul_summary.csv")
    write_scientific_report(
        ROOT_DIR,
        facts,
        surface_best,
        hidden_best,
        degradation_best,
        proxy_summary,
    )
    commands = [
        "conda run -n env python train_hidden_damage_models.py",
        "conda run -n env python train_degradation_models.py",
        "conda run -n env python train_rul_proxy_models.py",
        "conda run -n env python run_diagnostics_visualizations.py",
        "conda run -n env python run_model_improvement_analysis.py",
    ]
    write_readme(ROOT_DIR, commands)
    logger.info("Model improvement analysis artifacts generated successfully")


if __name__ == "__main__":
    main()

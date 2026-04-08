from __future__ import annotations

from pathlib import Path

import pandas as pd

from .evaluation import benchmark_models
from .feature_engineering import build_full_feature_table, get_model_feature_columns
from .splits import build_split_manifests, split_summary
from .utils_paths import ensure_dir, save_dataframe_csv
from .visualization import save_feature_importance_plot


SURFACE_TARGETS = ["surface_total_rust_pct", "peak_rust_pct"]
SURFACE_TARGET_NOTES = {
    "surface_total_rust_pct": "label_reconstruction_sanity_check",
    "peak_rust_pct": "surface_benchmark_with_related_strip_features",
}


def run_surface_models(master_df, image_feature_df, configs, output_dir: Path):
    ensure_dir(output_dir)
    feature_df = build_full_feature_table(master_df, image_feature_df)
    save_dataframe_csv(feature_df, output_dir / "surface_feature_table.csv")

    split_cfg = configs["modeling"]["group_shuffle"]
    manifests = build_split_manifests(
        feature_df,
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

    best_rows = []
    for target in SURFACE_TARGETS:
        target_dir = ensure_dir(output_dir / target)
        feature_cols = get_model_feature_columns(feature_df, target)
        group_shuffle_manifest = manifests["group_shuffle"]
        group_result = benchmark_models(
            feature_df,
            feature_cols,
            target,
            group_shuffle_manifest,
            configs["modeling"],
            target_dir / "group_shuffle",
        )
        best_model_name = group_result["best_model_name"]
        if not group_result["importance"].empty:
            if target == "surface_total_rust_pct":
                plot_title = (
                    f"{target} label-reconstruction sanity-check importance ({best_model_name})"
                )
            else:
                plot_title = f"{target} feature importance ({best_model_name})"
            save_feature_importance_plot(
                group_result["importance"],
                plot_title,
                target_dir / "group_shuffle" / f"{target}_feature_importance.png",
            )
        for strategy in ["leave_one_treatment_out", "leave_one_campaign_out"]:
            benchmark_models(
                feature_df,
                feature_cols,
                target,
                manifests[strategy],
                configs["modeling"],
                target_dir / strategy,
                model_names=[best_model_name],
            )
        best_rows.append(
            {
                "target": target,
                "best_model_name": best_model_name,
                "benchmark_note": SURFACE_TARGET_NOTES[target],
            }
        )

    best_df = pd.DataFrame(best_rows)
    save_dataframe_csv(best_df, output_dir / "best_models.csv")
    return feature_df, best_df

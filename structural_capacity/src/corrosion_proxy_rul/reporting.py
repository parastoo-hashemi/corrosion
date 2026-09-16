from __future__ import annotations

from pathlib import Path

import pandas as pd

from .feature_engineering import MODELING_QC_EXCLUSIONS
from .utils_paths import write_text


def write_readme(root_dir: Path, commands: list[str]) -> None:
    text = "# Corrosion Proxy-RUL Baseline\n\n"
    text += "This repository implements a leakage-safe, scientifically conservative baseline for:\n\n"
    text += (
        "surface corrosion progression -> hidden damage estimation -> "
        "degradation modelling -> exploratory threshold-status analysis (proxy-RUL).\n\n"
    )
    text += (
        "Important interpretation notes:\n\n"
        "- the `surface_total_rust_pct` benchmark is a label-reconstruction sanity check, not a "
        "standalone predictive success claim\n"
        "- the threshold stage is exploratory threshold-status analysis, not validated forward RUL\n\n"
    )
    text += "## Reproduction\n\n"
    text += "Use the existing conda environment and run:\n\n"
    for command in commands:
        text += f"- `{command}`\n"
    text += "\nAll generated artifacts are saved under `outputs/`.\n"
    write_text(root_dir / "outputs/reports/BASELINE_WORKFLOW.md", text)


def _load_summary(root_dir: Path, relative_path: str) -> pd.DataFrame:
    return pd.read_csv(root_dir / relative_path)


def _metric_line(summary_df: pd.DataFrame) -> str:
    row = summary_df.iloc[0]
    return (
        f"MAE={row['mae_mean']:.3f}, RMSE={row['rmse_mean']:.3f}, "
        f"Spearman={row['spearman_mean']:.3f}"
    )


def _metric_line_for_model(summary_df: pd.DataFrame, model_name: str) -> str:
    row = summary_df.loc[summary_df["model_name"] == model_name].iloc[0]
    return (
        f"MAE={row['mae_mean']:.3f}, RMSE={row['rmse_mean']:.3f}, "
        f"Spearman={row['spearman_mean']:.3f}"
    )


def write_scientific_report(
    root_dir: Path,
    facts: dict,
    surface_best: pd.DataFrame,
    hidden_best: pd.DataFrame,
    degradation_best: pd.DataFrame,
    proxy_summary: pd.DataFrame,
) -> None:
    outputs_dir = root_dir / "outputs"
    master_df = pd.read_csv(outputs_dir / "data" / "master_table.csv")
    image_feature_df = pd.read_csv(outputs_dir / "features" / "image_features.csv")
    proxy_estimates = pd.read_csv(outputs_dir / "models" / "proxy_rul" / "proxy_rul_estimates.csv")

    surface_rust_mae = (
        master_df["surface_total_rust_pct"] - image_feature_df["img_rust_area_ratio_pct"]
    ).abs().mean()
    surface_rust_max = (
        master_df["surface_total_rust_pct"] - image_feature_df["img_rust_area_ratio_pct"]
    ).abs().max()
    future_proxy_count = int(proxy_estimates["future_crossing_within_horizon"].sum())
    non_null_proxy_rul = int(proxy_estimates["proxy_rul_days"].notna().sum())
    baseline_proxy_crossings = int(proxy_estimates["threshold_reached_by_baseline"].sum())

    surface_total_group = _load_summary(
        root_dir,
        "outputs/models/surface/surface_total_rust_pct/group_shuffle/surface_total_rust_pct_summary.csv",
    )
    peak_group = _load_summary(
        root_dir,
        "outputs/models/surface/peak_rust_pct/group_shuffle/peak_rust_pct_summary.csv",
    )
    wire_group = _load_summary(
        root_dir,
        "outputs/models/hidden_damage/wire_area_loss_frac/group_shuffle/wire_area_loss_frac_summary.csv",
    )
    wire_loco = _load_summary(
        root_dir,
        "outputs/models/hidden_damage/wire_area_loss_frac/leave_one_campaign_out/wire_area_loss_frac_summary.csv",
    )
    load_group = _load_summary(
        root_dir,
        "outputs/models/hidden_damage/ultimate_load_kn/group_shuffle/ultimate_load_kn_summary.csv",
    )
    load_loco = _load_summary(
        root_dir,
        "outputs/models/hidden_damage/ultimate_load_kn/leave_one_campaign_out/ultimate_load_kn_summary.csv",
    )
    wire_best = hidden_best.loc[hidden_best["target"] == "wire_area_loss_frac"].iloc[0]
    load_best = hidden_best.loc[hidden_best["target"] == "ultimate_load_kn"].iloc[0]
    wire_loco_selected = _metric_line_for_model(wire_loco, wire_best["best_model_name"])
    load_loco_selected = _metric_line_for_model(load_loco, load_best["best_model_name"])

    qc_lines = [
        f"- `{feature}` excluded from modelling: {reason}"
        for feature, reason in MODELING_QC_EXCLUSIONS.items()
    ]

    lines = [
        "# Scientific Report",
        "",
        "## Problem formulation",
        "",
        "Direct supervised RUL is invalid for this dataset.",
        "",
        (
            "The current implementation should be interpreted conservatively as:"
        ),
        "",
        (
            "surface corrosion progression -> hidden damage estimation -> "
            "descriptive degradation smoothing -> exploratory threshold-status analysis"
        ),
        "",
        "## Verified dataset facts",
        "",
        f"- aligned usable rows: {facts['aligned_rows']}",
        f"- unique specimens: {facts['unique_specimens']}",
        f"- image files found: {facts['image_files']}",
        f"- orphan / corrupted image: {facts['orphan_images']}",
        f"- structural-label rows: {facts['structural_rows']}",
        f"- grouped split key: {facts['group_key']}",
        "",
        "## What Ran Successfully",
        "",
        "- audit and alignment validation",
        "- deterministic specimen mapping from `configs/specimen_mapping.yaml`",
        "- thesis-aligned interpretable image feature extraction",
        "- grouped surface and hidden-damage benchmarks",
        "- descriptive degradation fitting on model-based hidden-damage proxies",
        "- exploratory threshold-status output generation",
        "",
        "## What Is Scientifically Meaningful",
        "",
    ]
    lines.extend(
        [
            "- Data alignment and grouped split safety are credible.",
            (
                f"- The rust-mask feature reconstructs `surface_total_rust_pct` almost exactly "
                f"(MAE={surface_rust_mae:.6f}, max abs diff={surface_rust_max:.6f}); this is useful "
                "as a sanity check on the image-analysis pipeline."
            ),
            (
                f"- `peak_rust_pct` remains a meaningful auxiliary surface benchmark "
                f"({_metric_line(peak_group)}) under grouped splitting."
            ),
            (
                "- Leave-one-campaign-out structural failure remains the most informative negative result "
                "for the robustness-selected hidden-damage models: "
                f"`wire_area_loss_frac` {wire_loco_selected} and "
                f"`ultimate_load_kn` {load_loco_selected}."
            ),
            (
                f"- The current robust hidden-damage selections are "
                f"`{wire_best['feature_set_name']}` for `wire_area_loss_frac` and "
                f"`{load_best['feature_set_name']}` for `ultimate_load_kn`, which means the most stable "
                "structural signal in this round comes primarily from temporal / design metadata rather than "
                "from engineered image features."
            ),
        ]
    )
    lines.extend(
        [
            "",
            "## What Is Not A Valid Claim",
            "",
            (
                "- `surface_total_rust_pct` should not be presented as an independent predictive "
                "image-model result, because it is nearly equivalent to an engineered rust-area feature."
            ),
            (
                f"- `wire_area_loss_frac` is not a reliable hidden-damage predictor yet "
                f"({_metric_line(wire_group)}); ranking performance remains weak."
            ),
            (
                "- The degradation stage is descriptive smoothing of model-generated hidden-damage "
                "proxies, not validated physical degradation identification."
            ),
            (
                "- The threshold stage does not currently yield forward residual-life estimates; "
                "it is an exploratory threshold-status summary."
            ),
            "",
            "## Benchmark Snapshot",
            "",
            (
                f"- surface sanity check `surface_total_rust_pct`: "
                f"`{surface_best.loc[surface_best['target'] == 'surface_total_rust_pct', 'best_model_name'].iloc[0]}` "
                f"({_metric_line(surface_total_group)})"
            ),
            (
                f"- surface benchmark `peak_rust_pct`: "
                f"`{surface_best.loc[surface_best['target'] == 'peak_rust_pct', 'best_model_name'].iloc[0]}` "
                f"({_metric_line(peak_group)})"
            ),
            (
                f"- structural benchmark `wire_area_loss_frac`: "
                f"`{wire_best['best_model_name']}` "
                f"with `{wire_best['feature_set_name']}` "
                f"({_metric_line(wire_group)})"
            ),
            (
                f"- structural benchmark `ultimate_load_kn`: "
                f"`{load_best['best_model_name']}` "
                f"with `{load_best['feature_set_name']}` "
                f"({_metric_line(load_group)})"
            ),
            "",
            "## Feature Controls Applied",
            "",
        ]
    )
    lines.extend(qc_lines)
    lines.extend(
        [
            f"- `wire_area_loss_frac` final feature count: {int(wire_best.get('n_features', 0))}",
            f"- `ultimate_load_kn` final feature count: {int(load_best.get('n_features', 0))}",
            "",
            "## Degradation and Threshold-Status Outputs",
            "",
            f"- specimens fit successfully: {degradation_best['specimen_id'].nunique()}",
            f"- selected family counts: {degradation_best['best_family'].value_counts().to_dict()}",
            (
                f"- future threshold crossings within the projection horizon: {future_proxy_count}"
            ),
            (
                f"- rows with non-null `proxy_rul_days`: {non_null_proxy_rul} "
                "(only future crossings populate this column)"
            ),
            (
                f"- baseline threshold crossings across all specimen-threshold pairs: "
                f"{baseline_proxy_crossings}"
            ),
            "",
            "Threshold-status summary:",
            "",
            proxy_summary.to_markdown(index=False),
            "",
            "## Limitations",
            "",
            "- the aligned usable dataset is 791, not 792, because one PNG is orphaned and unreadable",
            "- structural supervision is limited to 48 terminal rows and remains too sparse for strong prognostic claims",
            "- campaign is confounded with mesh count, NaCl level, and terminal duration, so cross-campaign generalization remains weak",
            "- exact GIMP preprocessing steps from the thesis are not fully reproducible from the provided files",
            "- degradation and threshold-status outputs are downstream products of model-based hidden-damage proxies, not direct structural observations",
            "",
            "## Current Bottom Line",
            "",
            (
                "This codebase is currently strongest as an auditable baseline for data validation, "
                "surface-label reconstruction, leakage-safe evaluation, and honest negative findings "
                "about structural generalization."
            ),
            (
                "It is not yet strong enough to claim validated hidden-damage prognostics or "
                "decision-ready proxy-RUL."
            ),
        ]
    )
    write_text(root_dir / "outputs/reports/SCIENTIFIC_REPORT.md", "\n".join(lines))

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .utils_paths import ensure_dir, save_dataframe_csv
from .visualization import (
    save_barplot,
    save_boxplot,
    save_histograms,
    save_lineplot,
    save_missingness_plot,
)


def generate_eda(master_df: pd.DataFrame, output_dir: Path) -> dict:
    ensure_dir(output_dir)
    tables_dir = ensure_dir(output_dir / "tables")
    figures_dir = ensure_dir(output_dir / "figures")

    row_counts = pd.DataFrame(
        [
            {"entity": "rows", "count": len(master_df)},
            {"entity": "unique_specimens", "count": master_df["specimen_id"].nunique()},
            {"entity": "images_used", "count": master_df["image_path"].nunique()},
        ]
    )
    campaign_counts = (
        master_df.groupby("campaign_id")["sample_name"].count().reset_index(name="count")
    )
    treatment_counts = (
        master_df.groupby("split_group_treatment")["sample_name"]
        .count()
        .reset_index(name="count")
    )
    week_counts = master_df.groupby("week")["sample_name"].count().reset_index(name="count")
    missingness = (
        master_df.isna().sum().reset_index().rename(columns={"index": "column", 0: "missing_count"})
    )
    specimen_summary = (
        master_df.groupby("specimen_id")
        .agg(
            campaign_id=("campaign_id", "main_first"),
            split_group_treatment=("split_group_treatment", "main_first"),
            min_day=("ageing_days", "min"),
            max_day=("ageing_days", "max"),
            n_rows=("sample_name", "count"),
            has_structural_label=("has_structural_label", "max"),
            final_surface_total_rust_pct=("surface_total_rust_pct", "last"),
            final_peak_rust_pct=("peak_rust_pct", "last"),
        )
        .reset_index()
    )

    for name, frame in [
        ("row_counts.csv", row_counts),
        ("campaign_counts.csv", campaign_counts),
        ("treatment_counts.csv", treatment_counts),
        ("week_counts.csv", week_counts),
        ("missingness.csv", missingness),
        ("specimen_summary.csv", specimen_summary),
    ]:
        save_dataframe_csv(frame, tables_dir / name)

    save_barplot(row_counts, "entity", "count", "Dataset Counts", figures_dir / "row_counts.png")
    save_barplot(
        campaign_counts,
        "campaign_id",
        "count",
        "Campaign Counts",
        figures_dir / "campaign_counts.png",
    )
    save_barplot(
        treatment_counts,
        "split_group_treatment",
        "count",
        "Treatment Group Counts",
        figures_dir / "treatment_counts.png",
        rotation=45,
    )
    save_barplot(week_counts, "week", "count", "Week Distribution", figures_dir / "week_distribution.png")
    save_missingness_plot(missingness, figures_dir / "missingness.png")
    save_histograms(
        master_df,
        ["surface_total_rust_pct", "peak_rust_pct", "wire_area_loss_frac", "ultimate_load_kn"],
        figures_dir / "target_distributions.png",
    )
    sparsity = pd.DataFrame(
        [
            {"target": "wire_area_loss_frac", "non_null_rows": int(master_df["wire_area_loss_frac"].notna().sum())},
            {"target": "ultimate_load_kn", "non_null_rows": int(master_df["ultimate_load_kn"].notna().sum())},
        ]
    )
    save_dataframe_csv(sparsity, tables_dir / "structural_target_sparsity.csv")
    save_barplot(
        sparsity,
        "target",
        "non_null_rows",
        "Structural Target Sparsity",
        figures_dir / "structural_target_sparsity.png",
    )
    save_lineplot(
        master_df,
        x="ageing_days",
        y="surface_total_rust_pct",
        hue="specimen_id",
        title="Within-Specimen Surface Rust Trajectories",
        path=figures_dir / "within_specimen_surface_total_rust.png",
    )
    save_lineplot(
        master_df,
        x="ageing_days",
        y="peak_rust_pct",
        hue="campaign_id",
        title="Cross-Campaign Peak Rust Comparison",
        path=figures_dir / "cross_campaign_peak_rust.png",
    )
    save_boxplot(
        master_df,
        x="campaign_id",
        y="surface_total_rust_pct",
        title="Surface Rust by Campaign",
        path=figures_dir / "surface_rust_by_campaign.png",
    )

    return {
        "row_counts": row_counts,
        "campaign_counts": campaign_counts,
        "treatment_counts": treatment_counts,
        "week_counts": week_counts,
        "missingness": missingness,
        "specimen_summary": specimen_summary,
    }

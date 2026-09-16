from __future__ import annotations

import os
import sys

sys.path.insert(0, "src")

from pathlib import Path

import pandas as pd

from corrosion_proxy_rul.utils_paths import OUTPUT_DIR, ensure_dir

os.environ.setdefault("MPLCONFIGDIR", str(ensure_dir(OUTPUT_DIR / ".matplotlib")))

import matplotlib.pyplot as plt
import seaborn as sns


sns.set_theme(style="whitegrid")

FIGURE_PATH = OUTPUT_DIR / "diagnostics" / "figures" / "degradation" / "degradation_all_specimens_panel.png"


def main() -> None:
    grid_df = pd.read_csv(OUTPUT_DIR / "models" / "degradation" / "degradation_trajectory_grid.csv")
    proxy_df = pd.read_csv(OUTPUT_DIR / "models" / "degradation" / "full_feature_table_with_hidden_damage_proxy.csv")
    best_df = pd.read_csv(OUTPUT_DIR / "models" / "degradation" / "degradation_best_fits.csv")

    mapping = (
        proxy_df[["specimen_id", "campaign_id", "split_group_treatment"]]
        .drop_duplicates()
        .sort_values(["campaign_id", "specimen_id"])
        .reset_index(drop=True)
    )
    panel_order = mapping["specimen_id"].tolist()

    proxy_points = (
        proxy_df[["specimen_id", "ageing_days", "predicted_wire_area_loss_frac"]]
        .rename(columns={"ageing_days": "day"})
        .copy()
    )
    meta = mapping.merge(best_df[["specimen_id", "best_family"]], on="specimen_id", how="left")

    n_cols = 8
    n_rows = 6
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(24, 16), sharex=True, sharey=True)

    for ax, specimen_id in zip(axes.flatten(), panel_order):
        curve_sub = grid_df.loc[grid_df["specimen_id"] == specimen_id].sort_values("day")
        point_sub = proxy_points.loc[proxy_points["specimen_id"] == specimen_id].sort_values("day")
        meta_row = meta.loc[meta["specimen_id"] == specimen_id].iloc[0]

        ax.plot(
            curve_sub["day"],
            curve_sub["predicted_wire_area_loss_frac"],
            color="#4C78A8",
            linewidth=1.6,
        )
        ax.scatter(
            point_sub["day"],
            point_sub["predicted_wire_area_loss_frac"],
            color="#E15759",
            s=12,
            alpha=0.8,
        )
        ax.set_title(
            f"{specimen_id}\n{meta_row['campaign_id']} | {meta_row['best_family']}",
            fontsize=9,
        )
        ax.tick_params(labelsize=8)

    for ax in axes[-1, :]:
        ax.set_xlabel("Day", fontsize=10)
    for ax in axes[:, 0]:
        ax.set_ylabel("Proxy", fontsize=10)

    handles = [
        plt.Line2D([0], [0], color="#4C78A8", linewidth=2.0, label="fitted curve"),
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor="#E15759", markersize=6, label="observed proxy points"),
    ]
    fig.legend(handles=handles, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.5, 0.985))
    fig.suptitle(
        "Degradation curves for all specimens\nFitted hidden-damage proxy trajectories with observed proxy points",
        fontsize=16,
        y=1.01,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    ensure_dir(FIGURE_PATH.parent)
    fig.savefig(FIGURE_PATH, dpi=180, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()

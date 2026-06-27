from __future__ import annotations

import os
import sys

sys.path.insert(0, "src")

from pathlib import Path

import pandas as pd
from scipy.stats import pearsonr, spearmanr

from corrosion_proxy_rul.utils_paths import OUTPUT_DIR, configure_logging, ensure_dir, save_dataframe_csv

os.environ.setdefault("MPLCONFIGDIR", str(ensure_dir(OUTPUT_DIR / ".matplotlib")))

import matplotlib.pyplot as plt
import seaborn as sns


sns.set_theme(style="whitegrid")

FIGURE_DIR = OUTPUT_DIR / "diagnostics" / "figures" / "benchmarks" / "relationships"
TABLE_DIR = OUTPUT_DIR / "diagnostics" / "tables"
FIGURE_PATH = FIGURE_DIR / "ultimate_load_kn_vs_superficial_corrosion_by_mesh.png"
TABLE_PATH = TABLE_DIR / "ultimate_load_kn_vs_superficial_corrosion_by_mesh.csv"

CORROSION_COLUMNS = [
    ("surface_total_rust_pct", "Surface total rust (%)"),
    ("peak_rust_pct", "Peak rust (%)"),
]
MESH_GROUPS = [
    (4, "4 steel meshes", "#4C78A8"),
    (7, "7 steel meshes", "#F28E2B"),
]


def _safe_corr(series_x: pd.Series, series_y: pd.Series) -> tuple[float, float, float, float]:
    x = series_x.to_numpy(dtype=float)
    y = series_y.to_numpy(dtype=float)
    pearson_r, pearson_p = pearsonr(x, y)
    spearman_rho, spearman_p = spearmanr(x, y)
    return float(pearson_r), float(pearson_p), float(spearman_rho), float(spearman_p)


def _build_summary_rows(terminal_df: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for mesh_value, mesh_label, _color in MESH_GROUPS:
        subset = terminal_df.loc[terminal_df["n_steel_mesh"] == mesh_value].copy()
        for column, label in CORROSION_COLUMNS:
            pearson_r, pearson_p, spearman_rho, spearman_p = _safe_corr(
                subset[column], subset["ultimate_load_kn"]
            )
            rows.append(
                {
                    "n_steel_mesh": mesh_value,
                    "mesh_group_label": mesh_label,
                    "corrosion_column": column,
                    "corrosion_label": label,
                    "n_specimens": int(subset["specimen_id"].nunique()),
                    "ultimate_load_mean": float(subset["ultimate_load_kn"].mean()),
                    "ultimate_load_std": float(subset["ultimate_load_kn"].std(ddof=1)),
                    "corrosion_mean": float(subset[column].mean()),
                    "corrosion_std": float(subset[column].std(ddof=1)),
                    "pearson_r": pearson_r,
                    "pearson_pvalue": pearson_p,
                    "spearman_rho": spearman_rho,
                    "spearman_pvalue": spearman_p,
                }
            )
    return rows


def _add_panel(ax, subset: pd.DataFrame, x_col: str, x_label: str, mesh_label: str, color: str) -> None:
    pearson_r, _pearson_p, spearman_rho, _spearman_p = _safe_corr(
        subset[x_col], subset["ultimate_load_kn"]
    )
    sns.regplot(
        data=subset,
        x=x_col,
        y="ultimate_load_kn",
        ax=ax,
        ci=None,
        scatter_kws={"s": 65, "alpha": 0.85, "color": color, "edgecolor": "white", "linewidths": 0.5},
        line_kws={"color": "#222222", "linewidth": 1.8},
    )
    ax.set_title(f"{mesh_label}\n{ x_label } vs Ultimate load")
    ax.set_xlabel(x_label)
    ax.set_ylabel("Ultimate load (kN)")
    ax.text(
        0.03,
        0.97,
        "\n".join(
            [
                f"n = {subset['specimen_id'].nunique()}",
                f"Pearson r = {pearson_r:.3f}",
                f"Spearman rho = {spearman_rho:.3f}",
            ]
        ),
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "edgecolor": "#CCCCCC", "alpha": 0.95},
    )


def _save_figure(terminal_df: pd.DataFrame) -> None:
    ensure_dir(FIGURE_PATH.parent)
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharey=False)
    for row_idx, (x_col, x_label) in enumerate(CORROSION_COLUMNS):
        for col_idx, (mesh_value, mesh_label, color) in enumerate(MESH_GROUPS):
            ax = axes[row_idx, col_idx]
            subset = terminal_df.loc[terminal_df["n_steel_mesh"] == mesh_value].copy()
            _add_panel(ax, subset, x_col, x_label, mesh_label, color)
    fig.suptitle(
        "Ultimate load vs superficial corrosion, stratified by steel mesh count\n"
        "Terminal labeled specimens only",
        fontsize=14,
        y=1.02,
    )
    fig.tight_layout()
    fig.savefig(FIGURE_PATH, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    logger = configure_logging("run_ultimate_load_mesh_analysis")
    master_df = pd.read_csv(OUTPUT_DIR / "data" / "master_table.csv", parse_dates=["calendar_date"])
    terminal_df = (
        master_df.loc[master_df["ultimate_load_kn"].notna()]
        .copy()
        .sort_values(["n_steel_mesh", "specimen_id"])
        .reset_index(drop=True)
    )

    if terminal_df.empty:
        raise ValueError("No labeled rows found for ultimate_load_kn.")

    summary_df = pd.DataFrame(_build_summary_rows(terminal_df))
    save_dataframe_csv(summary_df, TABLE_PATH)
    _save_figure(terminal_df)
    logger.info("Saved mesh-stratified ultimate-load figure to %s", FIGURE_PATH)
    logger.info("Saved mesh-stratified correlation table to %s", TABLE_PATH)


if __name__ == "__main__":
    main()

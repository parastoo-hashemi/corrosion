"""
Generates Figure 4.6: terminal ultimate load vs. terminal surface total
rust percentage, stratified by steel-mesh family (mesh-4, mesh-7) and
pooled, with a fitted linear trend and Spearman rho/p per panel.

This is a focused, 3-panel reproduction of one row of the terminal-load
refocus phase's own saved 15-panel correlation figure
(main_4/outputs/ultimate_load_refocus/correlations/mesh_stratified_corrosion_vs_ultimate_load.png),
using only the single variable (surface_total_rust_pct) needed to make the
mesh-confounding point, computed directly from the phase's own saved
specimen-summary table (not hardcoded).

Reads:
  - main_4/outputs/ultimate_load_refocus/data/specimen_summary_table.csv

Run from the repository root:
    python activity_report/figures/generated_scripts/make_fig_4_6_mesh_stratified.py
"""
import pandas as pd
import numpy as np
from scipy.stats import spearmanr, pearsonr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = "."

df = pd.read_csv(f"{REPO_ROOT}/main_4/outputs/ultimate_load_refocus/data/specimen_summary_table.csv")
x_col = "surface_total_rust_pct_terminal"
y_col = "ultimate_load_kn"

groups = [
    (df[df["n_steel_mesh"] == 4], "4-mesh (Campaign 2)"),
    (df[df["n_steel_mesh"] == 7], "7-mesh (Campaign 1)"),
    (df, "Pooled (confounded)"),
]

fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.4), sharey=True)

for ax, (sub, title) in zip(axes, groups):
    x = sub[x_col].to_numpy(dtype=float)
    y = sub[y_col].to_numpy(dtype=float)
    ax.scatter(x, y, s=22, alpha=0.75, color="#4C72B0")
    if len(x) > 1:
        coeffs = np.polyfit(x, y, 1)
        xs = np.linspace(x.min(), x.max(), 50)
        ax.plot(xs, np.polyval(coeffs, xs), color="black", linewidth=1.2)
    rho, p = spearmanr(x, y)
    ax.set_title(f"{title}\nn={len(x)}, Spearman={rho:.2f} (p={p:.2g})", fontsize=9)
    ax.set_xlabel("Terminal total rust (%)")
    ax.grid(alpha=0.3)

axes[0].set_ylabel("Ultimate load (kN)")
fig.suptitle("Terminal surface corrosion vs. terminal ultimate load, by mesh family", fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.90])
fig.savefig(f"{REPO_ROOT}/activity_report/figures/fig_4_6_mesh_stratified_corrosion_vs_load.png", dpi=200)
print("wrote fig_4_6_mesh_stratified_corrosion_vs_load.png")
for sub, title in groups:
    rho, p = spearmanr(sub[x_col], sub[y_col])
    r, pp = pearsonr(sub[x_col], sub[y_col])
    print(title, "n=", len(sub), "pearson=", round(r, 3), "spearman=", round(rho, 3), "p=", round(p, 4))

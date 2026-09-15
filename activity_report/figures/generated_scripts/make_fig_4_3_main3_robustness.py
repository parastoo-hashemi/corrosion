"""
Generates Figure 4.3: R^2 by evaluation regime (grouped specimen holdout,
LOTO, LOCO) for the four continuous targets modelled in the interpretable
multi-family feature phase (main_3) -- two visible-corrosion targets and
two structural-condition targets. For each (target, regime) cell, the
model with the lowest mean MAE across folds of that regime is used (this
matches the selection rule used in the phase's own saved report).

Reads directly from the project's own saved metrics files:
  - main_3/outputs/corrosion_regression_metrics.csv
  - main_3/outputs/damage_regression_metrics.csv

Run from the repository root:
    python activity_report/figures/generated_scripts/make_fig_4_3_main3_robustness.py
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = "."

corr = pd.read_csv(f"{REPO_ROOT}/main_3/outputs/corrosion_regression_metrics.csv")
dmg = pd.read_csv(f"{REPO_ROOT}/main_3/outputs/damage_regression_metrics.csv")

regimes = ["group_shuffle", "leave_one_treatment_out", "leave_one_campaign_out"]
regime_labels = ["Grouped\nholdout", "LOTO", "LOCO"]
targets = [
    ("surface_total_rust_pct", corr, "Total rust\n(visible)"),
    ("peak_rust_pct", corr, "Peak rust\n(visible)"),
    ("wire_area_loss_pct", dmg, "Wire-area loss\n(structural)"),
    ("ultimate_load_kn", dmg, "Ultimate load\n(structural)"),
]


def best_mean_r2(df, target, regime):
    sub = df[(df["target"] == target) & (df["strategy"] == regime)]
    means = sub.groupby("model")["mae"].mean()
    best_model = means.idxmin()
    return sub[sub["model"] == best_model]["r2"].mean()


results = {t[0]: [best_mean_r2(t[1], t[0], r) for r in regimes] for t in targets}

fig, ax = plt.subplots(figsize=(7.5, 4.0))
x = range(len(regimes))
width = 0.19
colors = ["#4C72B0", "#64B5CD", "#C44E52", "#DD8452"]

for i, (target, _, label) in enumerate(targets):
    offs = [xi + (i - 1.5) * width for xi in x]
    vals = results[target]
    bars = ax.bar(offs, vals, width=width, label=label, color=colors[i])

ax.axhline(0, color="black", linewidth=0.8)
ax.set_xticks(list(x))
ax.set_xticklabels(regime_labels)
ax.set_ylabel("$R^2$ (best mean model per cell)")
ax.set_title("Visible-corrosion vs. structural-condition robustness\nacross evaluation regimes (interpretable multi-family feature phase)", fontsize=10)
ax.legend(loc="lower left", fontsize=8, ncol=2)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(f"{REPO_ROOT}/activity_report/figures/fig_4_3_main3_robustness_by_regime.png", dpi=200)
print("wrote fig_4_3_main3_robustness_by_regime.png")
for target, _, _ in targets:
    print(target, dict(zip(regimes, results[target])))

"""
Figure 5.1 (v2): cross-phase robustness synthesis using a FIXED model per
target within each phase (each phase's own grouped-holdout winner,
evaluated under every regime), not a best-available-model-per-regime
comparison. This corrects the v1 script, which sourced main_3's numbers
from Chapter 4 Table 3.2's "best mean model per (target, regime) cell",
which changes model identity across regimes for some targets (e.g. total
rust: RandomForest at grouped-holdout/LOCO but MLP at LOTO) and is
therefore not a same-model robustness ratio.

main_3 fixed-model source: main_3/outputs/corrosion_regression_metrics.csv,
main_3/outputs/damage_regression_metrics.csv (per-fold rows), aggregated by
(target, strategy, model), with the grouped-holdout-winning model selected
per target and its own rows read off under leave_one_treatment_out and
leave_one_campaign_out. Verified directly this session:
  surface_total_rust_pct : random_forest  (GH 1.381 / LOTO 1.649 / LOCO 2.096)
  peak_rust_pct           : mlp_regressor  (GH 4.209 / LOTO 4.744 / LOCO 7.435)
  wire_area_loss_pct      : random_forest  (GH 3.899 / LOTO 10.935 / LOCO 14.344)
  ultimate_load_kn        : random_forest  (GH 0.1207 / LOTO 0.1582 / LOCO 0.6487)

main_4 source: main_4/outputs/diagnostics/tables/benchmark_best_model_robustness.csv.
This table is ALREADY a fixed-model comparison by construction -- verified
directly against main_4/src/corrosion_proxy_rul/diagnostics.py's
build_best_model_robustness(): it selects each target's grouped-holdout
winner and reports that same model's rows under every strategy it has.
  surface_total_rust_pct : GradientBoosting (LOTO/GH=0.549, LOCO/GH=0.767)
  peak_rust_pct           : RandomForest     (LOTO/GH=0.758, LOCO/GH=0.964)
  wire_area_loss_frac     : RandomForest     (LOTO/GH=1.139, LOCO/GH=1.181)
  ultimate_load_kn        : RandomForest     (LOTO/GH=1.166, LOCO/GH=3.236)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

targets = ["Total/surface\nrust", "Peak\nrust", "Wire-area\nloss", "Ultimate\nload"]

# main_3, fixed model = grouped-holdout winner for that target
main3_gh   = [1.381353, 4.208694, 3.899300, 0.120685]
main3_loto = [1.648765, 4.743628, 10.934605, 0.158158]
main3_loco = [2.095868, 7.435230, 14.344338, 0.648721]
main3_loto_ratio = [b / a for a, b in zip(main3_gh, main3_loto)]
main3_loco_ratio = [b / a for a, b in zip(main3_gh, main3_loco)]

# main_4, already fixed-model (relative_mae_vs_group_shuffle column)
main4_loto_ratio = [0.549373, 0.758080, 1.138879, 1.166440]
main4_loco_ratio = [0.767472, 0.964394, 1.180697, 3.235727]

x = np.arange(len(targets))
width = 0.2

fig, ax = plt.subplots(figsize=(8.5, 4.4))
ax.bar(x - 1.5*width, main3_loto_ratio, width, label="main_3, LOTO/GH (fixed model)", color="#9ecae1")
ax.bar(x - 0.5*width, main3_loco_ratio, width, label="main_3, LOCO/GH (fixed model)", color="#3182bd")
ax.bar(x + 0.5*width, main4_loto_ratio, width, label="main_4, LOTO/GH (fixed model)", color="#fdae6b")
ax.bar(x + 1.5*width, main4_loco_ratio, width, label="main_4, LOCO/GH (fixed model)", color="#e6550d")

ax.axhline(1.0, color="black", linewidth=0.8, linestyle="--")
ax.set_xticks(x)
ax.set_xticklabels(targets)
ax.set_ylabel("Relative MAE\n(regime MAE / own grouped-holdout MAE,\nsame model in both)")
ax.set_title("Fixed-model robustness ratios: each phase's own grouped-holdout\nwinner, evaluated under every regime")
ax.legend(fontsize=7.5, ncol=2)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
out = "/Users/parastoo/All_projects/Proj_corrosion/corrosion/activity_report/figures/fig_5_1_robustness_synthesis.png"
fig.savefig(out, dpi=200)
print("wrote", out)
for t, a, b, c in zip(targets, main3_gh, main3_loto_ratio, main3_loco_ratio):
    print(t.replace(chr(10), " "), "main3 GH=", round(a,4), "LOTO/GH=", round(b,3), "LOCO/GH=", round(c,3))
for t, b, c in zip(targets, main4_loto_ratio, main4_loco_ratio):
    print(t.replace(chr(10), " "), "main4 LOTO/GH=", round(b,3), "LOCO/GH=", round(c,3))

"""
Generates Figure 4.1: main_2 image-only vs. multimodal MLP, validation MAE
vs. test MAE. Reads directly from the project's own saved artifacts (not
hardcoded), so the figure stays reproducible from source:

  - main_2/reports/training_history.csv  (validation MAE per epoch)
  - main_2/reports/model_comparison.csv  (final test MAE)

Run from the repository root:
    python activity_report/figures/generated_scripts/make_fig_4_1_main2_fusion.py
"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO_ROOT = "."

hist = pd.read_csv(f"{REPO_ROOT}/main_2/reports/training_history.csv")
comp = pd.read_csv(f"{REPO_ROOT}/main_2/reports/model_comparison.csv")

best_val_mae = hist.groupby("model")["val_mae"].min()
test_mae = comp.set_index("model")["test_mae"]

models = ["image_only_mlp", "multimodal_mlp"]
labels = ["Image-only", "Image + metadata\n(multimodal)"]
val_vals = [best_val_mae[m] for m in models]
test_vals = [test_mae[m] for m in models]

fig, axes = plt.subplots(1, 2, figsize=(7.5, 3.4), sharey=True)

colors = ["#4C72B0", "#DD8452"]
for ax, vals, title in zip(axes, [val_vals, test_vals], ["Best validation MAE", "Test MAE"]):
    bars = ax.bar(labels, vals, color=colors, width=0.55)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.08, f"{v:.2f}", ha="center", va="bottom", fontsize=9)
    ax.set_title(title, fontsize=10)
    ax.set_ylim(0, 6.5)
    ax.grid(axis="y", alpha=0.3)

axes[0].set_ylabel("MAE (peak rust %, current-week)")
fig.suptitle("Deep-embedding phase: image-only vs. multimodal regressor", fontsize=11)
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(f"{REPO_ROOT}/activity_report/figures/fig_4_1_main2_image_only_vs_multimodal.png", dpi=200)
print("wrote fig_4_1_main2_image_only_vs_multimodal.png")
print("validation MAE:", dict(zip(models, val_vals)))
print("test MAE:", dict(zip(models, test_vals)))

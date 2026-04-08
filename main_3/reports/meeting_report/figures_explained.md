# Figures Explained

Use these figures in roughly this order during the meeting.

## 1. Dataset overview

File:

- [/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/figures/dataset_overview.png](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/figures/dataset_overview.png)

What it shows:

- treatment imbalance
- week coverage
- where structural supervision exists
- corrosion-category balance

Insight:

- The project has dense surface labels but very sparse structural labels.
- That immediately explains why corrosion results are stronger than hidden-damage results.

Why it matters:

- This is the best figure for setting expectations before discussing any model metrics.

## 2. Representative corrosion images

File:

- [/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/figures/corrosion_examples.png](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/figures/corrosion_examples.png)

What it shows:

- low, medium, and high corrosion examples
- raw ROI plus normalized image with rust-mask overlay

Insight:

- Corrosion progression is visually meaningful, moving from clean or pale surfaces to localized streaks and bands, then to broad connected rust patches.

Why it matters:

- This is the easiest bridge from the physical specimens to the feature and model sections.

## 3. Corrosion label distributions

File:

- [/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/figures/corrosion_distributions.png](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/figures/corrosion_distributions.png)

What it shows:

- histogram of `surface_total_rust_pct`
- histogram of `peak_rust_pct`
- spatial distribution of peak-corrosion location

Insight:

- The label distributions are strongly skewed toward low corrosion.
- Peak corrosion is more spread than total surface corrosion.
- Corrosion hotspots are not uniform along the specimen length.

Why it matters:

- It explains why macro-F1 is lower than accuracy and why spatial features are useful.

## 4. Baseline parity plot from `main_2`

File:

- [/Users/parastoo/All_projects/Proj_corrosion/main_2/reports/figures/02_pred_vs_true_test.png](/Users/parastoo/All_projects/Proj_corrosion/main_2/reports/figures/02_pred_vs_true_test.png)

What it shows:

- the `main_2` test-set prediction vs truth relationship for the peak-corrosion baseline

Insight:

- The baseline already tracks the trend, but the spread around the diagonal is substantial.

Why it matters:

- It is the cleanest visual reminder of where the project started before `main_3`.

## 5. `main_3` corrosion regression parity

File:

- [/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/corrosion_regression_parity.png](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/corrosion_regression_parity.png)

What it shows:

- regression parity for the corrosion models in `main_3`

Insight:

- The grouped-specimen corrosion predictions are visibly tighter than the baseline story.
- Extreme values still show compression, especially at higher peak-rust severity.

Why it matters:

- This figure supports the claim that `main_3` materially improves the core corrosion task.

## 6. Hidden-damage relationships

File:

- [/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/figures/hidden_damage_relationships.png](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/figures/hidden_damage_relationships.png)

What it shows:

- visible peak rust vs wire loss
- surface rust vs ultimate load
- wire loss vs ultimate load

Insight:

- Visible corrosion is only weakly tied to internal damage in this dataset.
- The clearer structural relation is the negative trend between wire loss and ultimate load.

Why it matters:

- This figure is essential for an honest discussion of why the damage stage is harder than the corrosion stage.

## 7. Damage regression parity

File:

- [/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/damage_regression_parity.png](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/damage_regression_parity.png)

What it shows:

- prediction vs truth for the two damage regressions

Insight:

- The model is not random, but the scatter is clearly wider than the corrosion parity plot.

Why it matters:

- It visually justifies the statement that hidden-damage inference is promising but preliminary.

## 8. Degradation examples

File:

- [/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/figures/degradation_examples_panel.png](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/figures/degradation_examples_panel.png)

What it shows:

- average corrosion progression over week
- selected specimen-level peak-rust trajectories and forecasts

Insight:

- Corrosion generally increases over exposure time.
- Forecast shapes differ substantially between specimens, which justifies fitting degradation specimen by specimen instead of using one global trend.

Why it matters:

- This is the bridge from current-state prediction to future-state forecasting.

## 9. Risk distribution

File:

- [/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/risk_distribution.png](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/risk_distribution.png)

What it shows:

- count of specimens in Low, Moderate, High, and Critical proxy-risk classes

Insight:

- The outputs split the dataset into two large groups: Low and High.
- No specimen lands in the Critical category in this run.

Why it matters:

- This is the cleanest high-level view of what the proxy-RUL module is producing.

## 10. RUL histogram

File:

- [/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/rul_histogram.png](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/rul_histogram.png)

What it shows:

- distribution of `estimated_rul_weeks`

Insight:

- The median is zero because many specimens are already at a proxy threshold.
- A smaller subset has substantial remaining margin inside the forecast horizon.

Why it matters:

- It prevents overinterpreting the risk classes as smooth lifetime estimates.

## 11. Figure priority for the meeting

If time is short, prioritize these five:

1. `dataset_overview.png`
2. `corrosion_examples.png`
3. `corrosion_regression_parity.png`
4. `hidden_damage_relationships.png`
5. `risk_distribution.png`

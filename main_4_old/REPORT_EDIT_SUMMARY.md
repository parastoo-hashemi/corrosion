# Report Edit Summary

## 1. Final report structure

The rewritten `main.tex` now contains:

1. Title page
2. Abstract
3. Introduction
4. Project Objective and Scientific Motivation
5. Dataset and Documentation
6. Problem Formulation
7. Implemented Pipeline
8. Exploratory Analysis and Diagnostics
9. Model Benchmarking and Results
10. Important Figures and Their Interpretation
11. Limitations
12. Conclusion
13. Next Steps

## 2. Figures included

The report includes these figures:

1. `outputs/eda/figures/missingness.png`
2. `outputs/eda/figures/structural_target_sparsity.png`
3. `outputs/diagnostics/figures/distributions/skewed_variable_histograms_trimmed_p99.png`
4. `outputs/diagnostics/figures/temporal/campaign_surface_progression_median_iqr.png`
5. `outputs/diagnostics/figures/temporal/representative_specimen_surface_panels.png`
6. `outputs/diagnostics/figures/temporal/surface_progression_scatter_trends.png`
7. `outputs/diagnostics/figures/features/feature_target_correlation_heatmap.png`
8. `outputs/diagnostics/figures/features/image_feature_correlation_heatmap.png`
9. `outputs/diagnostics/figures/features/high_collinearity_pairs.png`
10. `outputs/diagnostics/figures/benchmarks/best_model_relative_mae_collapse_heatmap.png`
11. `outputs/diagnostics/figures/benchmarks/hidden_damage_best_model_strategy_robustness.png`
12. `outputs/diagnostics/figures/degradation/degradation_raw_vs_monotone_representative.png`
13. `outputs/diagnostics/figures/proxy/proxy_threshold_status_counts.png`

## 3. Figures excluded and why

The report intentionally excludes or de-emphasizes:

- `outputs/eda/figures/row_counts.png`
  - low information value compared with a small table
- `outputs/eda/figures/campaign_counts.png`
  - redundant once the dataset structure is explained in text
- `outputs/eda/figures/treatment_counts.png`
  - same reason as campaign counts
- `outputs/eda/figures/week_distribution.png`
  - weaker than the actual temporal progression figures
- `outputs/models/surface/surface_total_rust_pct/group_shuffle/surface_total_rust_pct_feature_importance.png`
  - too easy to over-interpret because the target is nearly identical to an engineered input feature
- `outputs/diagnostics/figures/benchmarks/predictions/surface/surface_total_rust_pct/surface_total_rust_pct_group_shuffle_prediction_diagnostics.png`
  - visually attractive but misleading for the same reason
- `outputs/models/proxy_rul/proxy_rul_right_censored.png`
  - less informative than the threshold-status summary figure
- `outputs/models/degradation/degradation_subset_trajectories.png`
  - weaker than the raw-vs-monotone degradation figure for an honest explanation
- most hidden-damage feature-importance figures
  - useful for appendix, but too weak and confounded to deserve main emphasis

## 4. Main storyline of the report

The report tells this story:

1. the dataset is longitudinal, grouped by specimen, and structurally sparse
2. therefore direct supervised RUL prediction is not valid
3. the project uses a staged, interpretable formulation instead
4. the data audit and mapping stages created a trustworthy canonical dataset
5. interpretable image features capture visible corrosion well
6. temporal corrosion progression is one of the strongest parts of the dataset
7. diagnostics show real redundancy and justify feature cleanup
8. benchmark robustness matters more than a single best grouped score
9. the hidden-damage stage remains weak and became more metadata-driven after robust selection
10. degradation and proxy-RUL remain exploratory and should not be overclaimed

## 5. Strongest conclusions highlighted

- The dataset audit and alignment are strong and trustworthy.
- Grouped splitting is necessary and was implemented consistently.
- Interpretable image features are scientifically useful for visible corrosion analysis.
- Temporal corrosion progression is clearly visible and presentation-worthy.
- The feature space is redundant, and the diagnostics made that problem explicit.
- The most important modelling lesson is about robustness: structural performance weakens sharply under harder splits.
- The final hidden-damage improvement is real but mostly metadata-driven.

## 6. Limitations explicitly stated

The report states clearly that:

- only 48 structural rows exist, one per specimen
- `surface_total_rust_pct` is mainly a sanity-check target
- cross-campaign hidden-damage generalization remains weak
- the improved structural models are metadata-only
- degradation modelling is descriptive smoothing, not strong predictive evidence
- proxy-RUL is exploratory threshold-status analysis, not decision-ready residual-life prediction
- the exact original image-preprocessing workflow from the thesis was not fully recoverable

## 7. Anything still missing or weak

- The report is intentionally conservative and does not try to make the structural stage look stronger than it is.
- Structural targets are still discussed, because they matter scientifically, but they are not allowed to dominate the storyline.
- If a later version of the report is needed for submission rather than presentation, the next likely improvement would be to add bibliography entries and a more formal references section.
- It would also be worth compiling the LaTeX once and checking figure sizing and page breaks manually, especially around the benchmark and diagnostics figures.

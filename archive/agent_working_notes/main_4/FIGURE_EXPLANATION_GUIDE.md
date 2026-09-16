# Figure Explanation Guide

## How To Use This Guide

This guide focuses on figures that help you explain the project clearly.

Evidence labels used here:

- **Strong**: solid, presentation-worthy evidence
- **Moderate**: useful with explanation and caveats
- **Weak**: appendix-only or easy to misinterpret

Recommendation labels:

- **Show**: good choice for main slides
- **Maybe**: useful for appendix or discussion
- **Avoid**: do not emphasize in the main presentation

## 1. Best Figures For Presentation

These are the clearest and most useful figures for explaining the project:

1. `outputs/eda/figures/missingness.png`
2. `outputs/eda/figures/structural_target_sparsity.png`
3. `outputs/diagnostics/figures/temporal/campaign_surface_progression_median_iqr.png`
4. `outputs/diagnostics/figures/temporal/representative_specimen_surface_panels.png`
5. `outputs/diagnostics/figures/temporal/surface_progression_scatter_trends.png`
6. `outputs/diagnostics/figures/features/feature_target_correlation_heatmap.png`
7. `outputs/diagnostics/figures/features/image_feature_correlation_heatmap.png`
8. `outputs/diagnostics/figures/features/high_collinearity_pairs.png`
9. `outputs/diagnostics/figures/benchmarks/best_model_relative_mae_collapse_heatmap.png`
10. `outputs/diagnostics/figures/proxy/proxy_threshold_status_counts.png`

## 2. Data Structure And Missingness Figures

| Figure path | What it shows | How to interpret it | Why it matters | Evidence strength | Show in presentation? |
| --- | --- | --- | --- | --- | --- |
| `outputs/eda/figures/missingness.png` | Missingness across major variables | Surface variables are dense; structural variables are sparse and mostly missing except at terminal rows | This is the quickest visual explanation of why direct RUL prediction is invalid | Strong | Show |
| `outputs/eda/figures/structural_target_sparsity.png` | Sparsity pattern of structural labels | Only one structural row per specimen is available | Directly supports the conservative problem formulation | Strong | Show |
| `outputs/eda/figures/target_distributions.png` | Combined target distributions | Gives a quick overview, but mixes dense and sparse targets in one view | Helpful early overview, but newer diagnostics are clearer | Moderate | Maybe |
| `outputs/eda/figures/cross_campaign_peak_rust.png` | Campaign comparison for peak rust | Shows that the two campaigns do not behave identically | Good early campaign-contrast figure | Moderate | Maybe |

## 3. Temporal Corrosion Progression Figures

| Figure path | What it shows | How to interpret it | Why it matters | Evidence strength | Show in presentation? |
| --- | --- | --- | --- | --- | --- |
| `outputs/diagnostics/figures/temporal/campaign_surface_progression_median_iqr.png` | Median surface corrosion progression with spread by campaign | Corrosion generally increases with exposure time, but campaigns differ in level and spread | Best high-level time-progress figure in the project | Strong | Show |
| `outputs/diagnostics/figures/temporal/representative_specimen_surface_panels.png` | Small panels of representative specimen trajectories | Shows that progression is real but not perfectly smooth specimen by specimen | Makes the longitudinal nature of the dataset easy to explain | Strong | Show |
| `outputs/diagnostics/figures/temporal/surface_progression_scatter_trends.png` | Scatter of corrosion against time with trend lines | Shows the global upward trend across the full dataset | Useful to communicate overall direction without focusing on single specimens | Strong | Show |
| `outputs/diagnostics/figures/temporal/campaign_faceted_specimen_spaghetti.png` | Many specimen-level trajectories separated by campaign | Shows within-campaign heterogeneity and overlap | Good appendix figure when asked about specimen variability | Moderate | Maybe |
| `outputs/diagnostics/figures/temporal/treatment_surface_progression_median.png` | Treatment-level median progression | Suggests treatment differences in visible corrosion, but still mixes campaign effects | Useful but should be explained carefully because treatment and campaign are related | Moderate | Maybe |
| `outputs/diagnostics/figures/temporal/exposure_band_target_boxplots.png` | Early, middle, late exposure comparisons | Summarizes how target values shift across exposure stages | Good support figure for the claim that corrosion increases over time | Moderate | Maybe |

## 4. Feature Understanding And Redundancy Figures

| Figure path | What it shows | How to interpret it | Why it matters | Evidence strength | Show in presentation? |
| --- | --- | --- | --- | --- | --- |
| `outputs/diagnostics/figures/features/feature_target_correlation_heatmap.png` | Focused correlations between key features and targets | Shows which feature families track visible corrosion strongly and how weak the structural relationships are | One of the best summary figures in the project | Strong | Show |
| `outputs/diagnostics/figures/features/ranked_feature_target_correlations.png` | Ranked feature-target correlations | Makes it easy to explain which engineered image features are most informative | Good companion to the heatmap | Strong | Maybe |
| `outputs/diagnostics/figures/features/image_feature_correlation_heatmap.png` | Correlation structure among key image features | Shows that many image features move together | Supports the claim that the feature space is redundant | Strong | Show |
| `outputs/diagnostics/figures/features/high_collinearity_pairs.png` | The strongest highly collinear feature pairs | Highlights duplicated or near-duplicated information | Important for explaining why feature cleanup was necessary | Strong | Show |
| `outputs/diagnostics/figures/features/full_feature_missingness_bar.png` | Missingness by feature | Mostly useful to show that image features are complete and structural outputs are sparse | Good if someone asks about data completeness | Moderate | Maybe |
| `outputs/diagnostics/figures/features/full_feature_missingness_heatmap.png` | Heatmap of missingness patterns | Makes the structural sparsity problem obvious | Useful, but more technical than the simpler EDA missingness plot | Moderate | Maybe |
| `outputs/diagnostics/figures/features/included_feature_variance_distribution.png` | Variance of included features | Shows that some features contribute much less information than others | Useful for technical discussion, less important for main slides | Moderate | Maybe |
| `outputs/diagnostics/figures/inventory/feature_inventory_stage_summary.png` | Counts of included and excluded features by stage/family | Shows how the modelling tables were simplified | Helpful when explaining feature cleanup and transparency | Moderate | Maybe |
| `outputs/diagnostics/figures/inventory/missingness_by_family_stage_heatmap.png` | Missingness by feature family and stage | Useful for technical appendix | More detailed than most presentations need | Weak to moderate | Maybe |

## 5. Distribution And Outlier Figures

| Figure path | What it shows | How to interpret it | Why it matters | Evidence strength | Show in presentation? |
| --- | --- | --- | --- | --- | --- |
| `outputs/diagnostics/figures/distributions/target_histograms_full_range.png` | Full-range target distributions | Shows the true spread, skew, and sparsity of the main variables | Good overview of what the models are trying to learn | Strong | Maybe |
| `outputs/diagnostics/figures/distributions/skewed_variable_histograms_trimmed_p99.png` | Readability-focused histograms for skewed variables | Lets you see the bulk of the data without hiding that outliers exist | Good way to discuss outliers honestly | Strong | Show |
| `outputs/diagnostics/figures/distributions/skewed_variable_boxplots_trimmed_p99.png` | Trimmed boxplots for skewed variables | Similar role to the trimmed histograms | Good appendix figure if asked about outliers | Moderate | Maybe |
| `outputs/diagnostics/figures/distributions/selected_variable_percentile_curves.png` | Percentile curves for selected variables | Shows how quickly tails grow, especially for unstable features | Useful for explaining why some features were excluded | Moderate | Maybe |
| `outputs/diagnostics/figures/distributions/outlier_counts_by_variable.png` | Outlier counts by variable | Summarizes where the heaviest tails are | Useful for discussion, but not essential in the main story | Moderate | Maybe |
| `outputs/diagnostics/figures/distributions/campaign_violin_diagnostics.png` | Campaign-wise variable distributions | Suggests campaign-level shifts | Good supporting evidence for campaign confounding | Moderate | Maybe |

## 6. Benchmark And Robustness Figures

| Figure path | What it shows | How to interpret it | Why it matters | Evidence strength | Show in presentation? |
| --- | --- | --- | --- | --- | --- |
| `outputs/diagnostics/figures/benchmarks/best_model_relative_mae_collapse_heatmap.png` | Relative error inflation across split strategies | Darker or larger ratios mean the benchmark breaks down when the split becomes harder | Best single benchmark figure for showing robustness vs collapse | Strong | Show |
| `outputs/diagnostics/figures/benchmarks/hidden_damage_best_model_strategy_robustness.png` | Structural best-model performance by strategy | Shows that structural modelling is fragile, especially across campaign | Good honest figure for the professor | Strong | Show |
| `outputs/diagnostics/figures/benchmarks/hidden_damage_best_model_fold_stability.png` | Fold-to-fold variability of structural performance | Shows that structural results are noisy and should be treated cautiously | Important if someone asks whether small metric differences matter | Strong | Maybe |
| `outputs/diagnostics/figures/benchmarks/group_shuffle_model_rank_heatmap.png` | Model ranking under grouped holdout | Shows the ordering of models in the easier grouped setting | Useful, but less important than the collapse heatmap | Moderate | Maybe |
| `outputs/diagnostics/figures/benchmarks/split_strategy_overview.png` | Split composition overview | Explains the three evaluation regimes | Good setup figure for the methods section | Moderate | Maybe |
| `outputs/diagnostics/figures/benchmarks/surface_best_model_strategy_robustness.png` | Surface-stage robustness by strategy | Surface results remain strong, but must be explained with the sanity-check caveat | Useful only if you explicitly state the caveat | Moderate | Maybe |
| `outputs/diagnostics/figures/benchmarks/surface_group_shuffle_model_comparison_mae.png` | Surface model comparison on grouped holdout | Shows model ranking for surface targets | Secondary because the surface stage is not the main scientific contribution | Moderate | Maybe |

## 7. Degradation And Proxy Figures

| Figure path | What it shows | How to interpret it | Why it matters | Evidence strength | Show in presentation? |
| --- | --- | --- | --- | --- | --- |
| `outputs/diagnostics/figures/degradation/degradation_observed_vs_fitted_scatter.png` | Observed proxy values vs fitted degradation values | Shows how closely the fitted curves follow the smoothed hidden-damage proxy | Good honesty figure: it supports descriptive smoothing, not strong prediction | Moderate | Maybe |
| `outputs/diagnostics/figures/degradation/degradation_raw_vs_monotone_representative.png` | Raw predicted hidden-damage trajectories vs monotone version | Shows why smoothing was applied | Very useful to explain that the degradation stage is a stabilizing descriptive layer | Moderate | Maybe |
| `outputs/diagnostics/figures/degradation/degradation_best_family_counts.png` | Counts of selected curve families | Shows which families were most often chosen | Useful as a summary, but not a headline figure | Weak to moderate | Maybe |
| `outputs/diagnostics/figures/proxy/proxy_threshold_status_counts.png` | Counts of threshold status outcomes | Shows that most thresholds are either already crossed or right-censored, with no future crossings within horizon | Best honest summary of the current proxy-RUL stage | Strong | Show |
| `outputs/diagnostics/figures/proxy/proxy_threshold_status_heatmap.png` | Threshold status by specimen and threshold | More detailed view of threshold outcomes | Good appendix figure if asked how specimens differ | Moderate | Maybe |
| `outputs/diagnostics/figures/proxy/proxy_future_rul_nonnull_counts.png` | Number of future residual-life estimates | Shows that there are essentially none | Supports the statement that proxy-RUL is still exploratory | Moderate | Maybe |

## 8. Figures To Avoid Or De-Emphasize

These figures are not wrong, but they are weak, redundant, or easy to overread.

| Figure path | Why to avoid or de-emphasize |
| --- | --- |
| `outputs/eda/figures/row_counts.png` | Useful as a table, not as a main presentation figure |
| `outputs/eda/figures/campaign_counts.png` | Redundant once the dataset is explained verbally or in a small table |
| `outputs/eda/figures/treatment_counts.png` | Same issue as campaign counts |
| `outputs/eda/figures/week_distribution.png` | Better replaced by a time-progression figure |
| `outputs/models/surface/surface_total_rust_pct/group_shuffle/surface_total_rust_pct_feature_importance.png` | Misleading because the target is almost the same as an input feature |
| `outputs/diagnostics/figures/benchmarks/predictions/surface/surface_total_rust_pct/surface_total_rust_pct_group_shuffle_prediction_diagnostics.png` | Easy to overclaim as predictive success even though it is mainly label reconstruction |
| `outputs/models/proxy_rul/proxy_rul_right_censored.png` | Less informative than the newer threshold-status plots |
| `outputs/models/degradation/degradation_subset_trajectories.png` | Weaker than the raw-vs-monotone and observed-vs-fitted degradation figures |
| `outputs/diagnostics/figures/benchmarks/feature_importance/hidden_damage/*` | Fine for appendix, but not strong headline evidence because structural signal remains weak and confounded |

## 9. Suggested Figure Set For Slides

If you need a compact presentation, use roughly this order:

1. `outputs/eda/figures/missingness.png`
2. `outputs/eda/figures/structural_target_sparsity.png`
3. `outputs/diagnostics/figures/temporal/campaign_surface_progression_median_iqr.png`
4. `outputs/diagnostics/figures/temporal/representative_specimen_surface_panels.png`
5. `outputs/diagnostics/figures/features/feature_target_correlation_heatmap.png`
6. `outputs/diagnostics/figures/features/image_feature_correlation_heatmap.png`
7. `outputs/diagnostics/figures/features/high_collinearity_pairs.png`
8. `outputs/diagnostics/figures/distributions/skewed_variable_histograms_trimmed_p99.png`
9. `outputs/diagnostics/figures/benchmarks/best_model_relative_mae_collapse_heatmap.png`
10. `outputs/diagnostics/figures/proxy/proxy_threshold_status_counts.png`

That set tells a coherent story:

- what data exists
- how corrosion progresses over time
- what the image features capture
- why feature cleanup was needed
- what benchmark robustness teaches us
- why the proxy-RUL stage is still exploratory

## 10. Bottom Line

The best figures in this project are not the ones with the biggest scores.

The best figures are the ones that make the scientific story clear:

- the dataset is longitudinal and structurally sparse
- visible corrosion progresses over time
- interpretable image features do capture visible corrosion
- the feature space is redundant and needed cleanup
- structural prediction remains weak and confounded
- proxy-RUL is exploratory, not decision-ready

Those are the figures worth showing.

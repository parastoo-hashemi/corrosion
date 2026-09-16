# Selected structural-capacity results

**14 preserved files: 13 figures and one paper.** Former location: `emiling/main_4/`.
Read the feature-set comparison and split diagrams first, then the Ridge diagnostics.
[Collection overview](../README.md).

These results concern terminal ultimate load from 48 specimens. Pooled grouped
cross-validation and campaign holdout answer different questions. Read the
[campaign comparison and scientific limits](../../docs/experiments.md#key-results-and-evidence)
alongside this selection. The eight figures in `metadata_only+Ridge/` all belong
to the pooled grouped-CV metadata-only Ridge experiment; they are not eight
independent studies.

| Selected file | What it shows and how to interpret it | Matching source copy |
|---|---|---|
| [feature_set_comparison_bars.png](feature_set_comparison_bars.png) | Start here: best model per feature set in pooled grouped cross-validation (CV). Metadata is a strong baseline; selection uses the evaluated folds. | [Source](../../structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/feature_set_comparison_bars.png) |
| [model_metric_heatmap.png](model_metric_heatmap.png) | Model/feature-set comparison using MAE, root mean squared error and Spearman correlation. Read each metric on its own scale. | [Source](../../structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/model_metric_heatmap.png) |
| [grouped_cv_balance.png](grouped_cv_balance.png) | Specimen and mesh balance for five grouped folds repeated twice; repeated folds are dependent. | [Source](../../structural_capacity/outputs/ultimate_load_refocus/splits/grouped_cv_balance.png) |
| [leave_one_campaign_out_balance.png](leave_one_campaign_out_balance.png) | Two campaign holdouts. Campaign, mesh and treatment composition are confounded; see campaign results in the experiment map. | [Source](../../structural_capacity/outputs/ultimate_load_refocus/splits/leave_one_campaign_out_balance.png) |
| [mesh_stratified_corrosion_vs_ultimate_load.png](mesh_stratified_corrosion_vs_ultimate_load.png) | Within-mesh corrosion/load associations; stratification does not establish a causal corrosion effect. | [Source](../../structural_capacity/outputs/ultimate_load_refocus/correlations/mesh_stratified_corrosion_vs_ultimate_load.png) |
| [metadata_only+Ridge/prediction_vs_ground_truth.png](metadata_only+Ridge/prediction_vs_ground_truth.png) | Terminal specimen predictions averaged over held-out repeats. Metrics on averaged predictions differ from means of fold metrics. | [Source](../../structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/prediction_vs_ground_truth.png) |
| [metadata_only+Ridge/error_distribution.png](metadata_only+Ridge/error_distribution.png) | Signed and absolute terminal prediction errors, in kN. | [Source](../../structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/error_distribution.png) |
| [metadata_only+Ridge/residual_analysis.png](metadata_only+Ridge/residual_analysis.png) | Signed residuals versus predicted load, with mesh groups. | [Source](../../structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/residual_analysis.png) |
| [metadata_only+Ridge/cv_stability.png](metadata_only+Ridge/cv_stability.png) | Fold-level metric distributions. Their spread is descriptive, not a confidence interval from independent replicates. | [Source](../../structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/cv_stability.png) |
| [metadata_only+Ridge/feature_importance.png](metadata_only+Ridge/feature_importance.png) | Full-fit Ridge coefficient magnitudes/aggregations. They describe the fitted model, not causal or independently validated importance. | [Source](../../structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/feature_importance.png) |
| [metadata_only+Ridge/learning_curve.png](metadata_only+Ridge/learning_curve.png) | Training-specimen fractions versus performance; subsampling also changes composition, so this is not a pure sample-count effect. | [Source](../../structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/learning_curve.png) |
| [metadata_only+Ridge/partial_dependence.png](metadata_only+Ridge/partial_dependence.png) | Fitted associations under feature variation. Correlated inputs may create unsupported combinations; this is not an intervention estimate. | [Source](../../structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/partial_dependence.png) |
| [metadata_only+Ridge/uncertainty.png](metadata_only+Ridge/uncertainty.png) | Variation across held-out repeats (two per specimen). Displayed uncertainty is descriptive, not a calibrated prediction interval. | [Source](../../structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/uncertainty.png) |
| [ultimate_load_refocus_ieee.pdf](ultimate_load_refocus_ieee.pdf) | Historical five-page terminal-load refocus paper. It differs from both the phase-local PDF build and the current v3 five-page article. | [Source](../../out/ultimate_load_refocus_ieee.pdf) |

## Evidence and continuation

Saved evidence: [feature-set comparison](../../structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/feature_set_comparison.csv)
and [model comparison](../../structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/model_comparison.csv).
For Ridge, the [experiment directory](../../structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/)
contains `fold_metrics.csv`, `terminal_oof_predictions.csv`,
`terminal_fold_predictions.csv`, `feature_importance_full_fit.csv`,
`learning_curve_raw.csv`, `learning_curve_summary.csv` and `partial_dependence.csv`.

The [refocus analysis code](../../structural_capacity/src/corrosion_proxy_rul/ultimate_load_refocus.py)
records the analysis workflow. Its current source has unresolved execution defects;
this selection preserves saved results, not a newly validated rerun. Start with
[known issues](../../docs/known_issues.md) and [reproduction instructions](../../docs/reproduction.md).

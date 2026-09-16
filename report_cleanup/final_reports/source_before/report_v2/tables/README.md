# Saved tables and numerical evidence

**20 CSV files and nine LaTeX files** support the reports. CSV files retain saved
numerical results or audit records; `.tex` files provide formatted tables or
reusable numbers for the manuscripts. A matching CSV and LaTeX file serve
different purposes and are both retained.

## CSV index

Compare results within the same target, units and evaluation regime. Some files
summarize selected models; selection and repeated-fold dependence limit inference.
See the [experiment map](../../docs/experiments.md) for the scientific context.

| File | Group | Contents |
|---|---|---|
| [campaign_design.csv](campaign_design.csv) | Dataset | Observed campaign-level specimen counts and exposure/design combinations. |
| [classification_splits.csv](classification_splits.csv) | Dataset | Four-class preparation counts by partition; not classifier performance. |
| [classical.csv](classical.csv) | Earlier modelling | Classical-model validation and holdout metrics. |
| [embedding.csv](embedding.csv) | Earlier modelling | Embedding-generation saved test metrics. |
| [interpretable_regime_winners.csv](interpretable_regime_winners.csv) | Earlier modelling | Historical interpretable-model results across evaluation strategies and targets. |
| [refined_robustness.csv](refined_robustness.csv) | Robustness | Refined-stage best-model metrics and relative errors across split regimes. |
| [robust_structural_selection.csv](robust_structural_selection.csv) | Robustness | Saved structural selection summary, feature choices and robustness metrics. |
| [robustness_ratios.csv](robustness_ratios.csv) | Robustness | Within-generation error ratios relative to grouped holdout. |
| [pooled_capacity.csv](pooled_capacity.csv) | Terminal capacity | Selected feature-family results under pooled grouped cross-validation. |
| [mesh_capacity.csv](mesh_capacity.csv) | Terminal capacity | Results within each mesh group. |
| [loco_capacity.csv](loco_capacity.csv) | Terminal capacity | Leave-one-campaign-out results; a confounded transfer stress test. |
| [post_onset_capacity.csv](post_onset_capacity.csv) | Terminal capacity | Post-onset sensitivity-analysis results. |
| [paired_specimen_errors.csv](paired_specimen_errors.csv) | Terminal capacity | Matched metadata-only and metadata+HSV Ridge errors and their differences, in kN. |
| [correlations_recomputed.csv](correlations_recomputed.csv) | Associations | Stored group-level correlation calculations; observational, not causal evidence. |
| [threshold_status.csv](threshold_status.csv) | Proxy thresholds | Counts of model-derived threshold statuses. |
| [threshold_summary.csv](threshold_summary.csv) | Proxy thresholds | Extended threshold summary; not observed failure times or validated remaining life. |
| [split_checks.csv](split_checks.csv) | Audit | Saved train/test specimen counts and overlap checks. |
| [source_hashes.csv](source_hashes.csv) | Audit | Hashes and timestamps of recorded source files. |
| [current_corruption_inventory.csv](current_corruption_inventory.csv) | Audit | Source-token corruption inventory at the earlier audit date; not a live scan. |
| [historical_artifact_timestamps.csv](historical_artifact_timestamps.csv) | Audit | Historical artifact hashes/timestamps used in the source-state investigation. |

## LaTeX files

| File | Role |
|---|---|
| [pooled_capacity.tex](pooled_capacity.tex) | Thesis pooled-capacity table; presentation of pooled_capacity.csv. |
| [pooled_capacity_article.tex](pooled_capacity_article.tex) | Compact article version of the pooled-capacity table. |
| [mesh_capacity.tex](mesh_capacity.tex) | Thesis appendix: within-mesh results. |
| [post_onset_capacity.tex](post_onset_capacity.tex) | Thesis appendix: post-onset results. |
| [classification_splits.tex](classification_splits.tex) | Thesis: classification-preparation partition counts. |
| [threshold_summary.tex](threshold_summary.tex) | Thesis appendix: exploratory threshold summary. |
| [paired_statistics.tex](paired_statistics.tex) | Macros used by both manuscripts for paired-error summary numbers; not a standalone table. |
| [loco_capacity.tex](loco_capacity.tex) | Retained formatted campaign-holdout table; not directly included by the current v3 masters/chapters. |
| [post_onset_capacity_article.tex](post_onset_capacity_article.tex) | Retained compact post-onset table; not directly included by the current v3 article. |

## Provenance and maintenance

The [script guide](../scripts/README.md) identifies the audit, paired-analysis and
formatting utilities. [Archived claims](../evidence/claims.json) record the saved
numerical audit. Historical source paths and timestamps describe that recorded
state; they are not fresh verification of the present environment.

All 29 existing files are preserved unchanged. Tables may be shared inputs to
both manuscripts, so changing a value or regenerating a presentation file can
change a future build. [Return to the report guide](../README.md).

# Selected condition-assessment results

**16 preserved files: 15 figures and one paper.** Former location: `emiling/main_3/`.
Read the dataset overview first, then surface prediction, terminal damage and the
exploratory degradation figures. [Collection overview](../README.md).

The work combines repeated image observations with only 48 terminal structural
outcomes. A large image-row count is not an equal number of independent structural
labels. The original figures are preserved; the notes below explain limits in
how they should be read.

| Selected file | What it shows and how to interpret it | Matching source copy |
|---|---|---|
| [dataset_overview.png](dataset_overview.png) | Start here: treatment, observation-time and label coverage; historical 792 surface records versus 48 structural outcomes. | [Source](../../condition_assessment/reports/meeting_report/figures/dataset_overview.png) |
| [corrosion_examples.png](corrosion_examples.png) | Illustrative low, medium and high corrosion examples with image/mask overlays; examples are not performance estimates. | [Source](../../condition_assessment/reports/meeting_report/figures/corrosion_examples.png) |
| [corrosion_distributions.png](corrosion_distributions.png) | Distributions of total and peak rust, and peak-location bands. | [Source](../../condition_assessment/reports/meeting_report/figures/corrosion_distributions.png) |
| [feature_alignment.png](feature_alignment.png) | Earlier condition-phase feature/label associations. These are distinct from the later structural-phase label-adjacency analysis. | [Source](../../condition_assessment/reports/meeting_report/figures/feature_alignment.png) |
| [grouped_regression_mae_summary.png](grouped_regression_mae_summary.png) | Grouped-holdout mean absolute error (MAE) summary. Surface percentages, wire-loss percentages and load in kN have different target scales. | [Source](../../condition_assessment/reports/figures/grouped_regression_mae_summary.png) |
| [corrosion_model_mae.png](corrosion_model_mae.png) | Surface-target MAE by model, in percentage points. | [Source](../../condition_assessment/reports/figures/corrosion_model_mae.png) |
| [corrosion_model_macro_f1.png](corrosion_model_macro_f1.png) | Historical five-class corrosion classification. This is a different task from the later four-class preparation, whose training is pending. | [Source](../../condition_assessment/reports/figures/corrosion_model_macro_f1.png) |
| [corrosion_regression_parity.png](corrosion_regression_parity.png) | Predicted versus observed surface values. The historical plot combines surface targets; inspect target-specific saved predictions for detailed comparisons. | [Source](../../condition_assessment/reports/figures/corrosion_regression_parity.png) |
| [hidden_damage_relationships.png](hidden_damage_relationships.png) | Surface indicators versus terminal wire loss and load. Associations may reflect treatment/campaign composition; they do not establish causality. | [Source](../../condition_assessment/reports/meeting_report/figures/hidden_damage_relationships.png) |
| [damage_model_mae.png](damage_model_mae.png) | Hidden-damage errors share an axis despite different units: ultimate load in kN and wire loss in percentage points. Do not compare their bar heights as equivalent errors. | [Source](../../condition_assessment/reports/figures/damage_model_mae.png) |
| [damage_regression_parity.png](damage_regression_parity.png) | Historical parity plot combines load in kN and wire-loss percentage points. Use target-specific predictions for quantitative interpretation. | [Source](../../condition_assessment/reports/figures/damage_regression_parity.png) |
| [degradation_examples_panel.png](degradation_examples_panel.png) | Cross-sectional peak rust over weeks and fitted/extrapolated specimen trajectories. Sample composition changes across observation times. | [Source](../../condition_assessment/reports/meeting_report/figures/degradation_examples_panel.png) |
| [degradation_examples_peak_rust.png](degradation_examples_peak_rust.png) | Illustrative specimen peak-rust fits and forecasts; exploratory extrapolation, not observed future outcomes. | [Source](../../condition_assessment/reports/figures/degradation_examples_peak_rust.png) |
| [risk_distribution.png](risk_distribution.png) | Model-assigned risk categories; these have not been validated as structural safety decisions. | [Source](../../condition_assessment/reports/figures/risk_distribution.png) |
| [rul_histogram.png](rul_histogram.png) | Estimated weeks to a chosen corrosion threshold, not observed lifetimes or validated remaining useful life (RUL). | [Source](../../condition_assessment/reports/figures/rul_histogram.png) |
| [corrosion_condition_pipeline_ieee.pdf](corrosion_condition_pipeline_ieee.pdf) | Historical eight-page condition-assessment paper. Its exact matching export is in out/; the phase-local PDF is a different build. | [Source](../../out/corrosion_condition_pipeline_ieee.pdf) |

## Evidence and continuation

Saved evidence: [surface regression metrics](../../condition_assessment/outputs/corrosion_regression_metrics.csv),
[five-class metrics](../../condition_assessment/outputs/corrosion_classification_metrics.csv),
[surface predictions](../../condition_assessment/outputs/corrosion_regression_predictions.parquet),
[damage metrics](../../condition_assessment/outputs/damage_regression_metrics.csv),
[damage predictions](../../condition_assessment/outputs/damage_regression_predictions.parquet),
[degradation forecasts](../../condition_assessment/outputs/degradation_forecasts.parquet) and
[threshold-time estimates](../../condition_assessment/outputs/rul_estimates.csv).

The [orchestration code](../../condition_assessment/src/orchestration.py) and
[plotting functions](../../condition_assessment/src/visualization/plots.py) explain
the metric/parity/degradation outputs. Meeting-report figures are linked to their
preserved source copies above. These links document provenance; regeneration has
not been certified. Read [reproduction instructions](../../docs/reproduction.md)
and [known issues](../../docs/known_issues.md) before running anything.

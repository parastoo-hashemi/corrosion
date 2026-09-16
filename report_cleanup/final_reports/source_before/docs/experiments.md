# Experiment map and saved evidence

Use this page to follow the research phases, find the evidence behind the main
findings, and choose an entry point for continuation. Paths are relative to the
repository root unless a working directory is stated.

**Reproduction status:** saved outputs establish what is available for review.
Historical modelling commands below are not certified runnable in the current
source state. Read [known issues](known_issues.md) before running them; training can
overwrite evidence. Use the separate working copy described in [reproduction](reproduction.md).

## Historical phases

Phase labels follow the project's research history. Phases 4a and 4b share the
`structural_capacity/` implementation; classification preparation is a separate,
later workstream.

| Phase and folder | Research question or contribution | Evidence to inspect | Status |
|---|---|---|---|
| 0. [Exploratory prototype](../exploratory_prototype/) | Initial handcrafted features, random forests and simulated trajectories | [Prototype artifacts](../exploratory_prototype/ressult/) | Exploratory; no defensible comparable held-out benchmark |
| 1. [Classical corrosion](../classical_corrosion/) | Estimate current peak corrosion, progression and threshold time | [Current-corrosion metrics](../classical_corrosion/reports/current_corrosion_metrics.csv), [progression metrics](../classical_corrosion/reports/progression_metrics.csv), [threshold-time metrics](../classical_corrosion/reports/time_to_threshold_metrics.csv) | Saved historical benchmarks; training rerun unverified; threshold time is not validated structural lifetime |
| 2. [Image embeddings](../image_embeddings/) | Compare frozen ResNet-18 image embeddings with added tabular context | [Model comparison](../image_embeddings/reports/model_comparison.csv), [saved predictions](../image_embeddings/reports/predictions_best_model.csv) | Saved historical results; embedding API blocked by saved-preprocessor compatibility |
| 3. [Condition assessment](../condition_assessment/) | Relate interpretable image features to surface corrosion, hidden damage and proxy-RUL | [Surface metrics](../condition_assessment/outputs/corrosion_regression_metrics.csv), [structural metrics](../condition_assessment/outputs/damage_regression_metrics.csv), [five-class metrics](../condition_assessment/outputs/corrosion_classification_metrics.csv) | Saved 792-row/five-class generation; current modelling source requires repair |
| 4a. [Structural robustness](../structural_capacity/) | Test sensitivity to specimen, treatment and campaign holdouts | [Robustness comparison](../structural_capacity/outputs/diagnostics/tables/benchmark_best_model_robustness.csv), [diagnostics](../structural_capacity/outputs/diagnostics/), [improvement analyses](../structural_capacity/outputs/improvements/) | Saved 791-row generation; structural transfer remains weak; rerun blocked by source/configuration defects |
| 4b. [Terminal-load refocus](../structural_capacity/outputs/ultimate_load_refocus/) | Do image descriptors add value beyond metadata for terminal ultimate load? | [Grouped feature comparison](../structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/feature_set_comparison.csv), [campaign holdout](../structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/leave_one_campaign_out/feature_set_comparison.csv) | Most mature saved structural study; present source is not a validated rerun baseline |
| 5. [Four-class preparation](../classification_data_preparation/) | Prepare augmented images and fixed specimen-disjoint partitions | [Split summary](../report_v2/tables/classification_splits.csv), [train](../Data/splits/train_manifest.csv), [validation](../Data/splits/val_manifest.csv), [test](../Data/splits/test_manifest.csv) manifests | Preparation complete; classifier training/evaluation not performed |

The [archived structural baseline](../archive/structural_baseline_snapshot/) is an
earlier saved state. [Selected results](../selected_results/README.md), formerly
`emiling/`, groups 28 figures and two historical papers with interpretation notes;
`out/` retains PDF exports. These collections are not additional independent
experiments. [Project history](project_history.md) explains
changes in direction and historical terminology.

## Key results and evidence

The numerical entries below are rounded from existing saved tables; they were not
produced by a new training run. MAE means mean absolute error; lower is better.
Ultimate-load errors are in kilonewtons (kN).

| Finding | Saved result and evaluation scope | Supporting evidence | Interpretation limit |
|---|---|---|---|
| Metadata is a strong pooled terminal-load baseline | Metadata-only Ridge: mean fold MAE **0.1727 kN**; metadata + HSV Ridge: **0.1730 kN**. Both use 10 fold evaluations (five grouped folds × two repeats) and 48 specimens. | [Feature comparison](../structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/feature_set_comparison.csv), [Ridge fold metrics](../structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/fold_metrics.csv), [comparison figure](../report_v2/figures/capacity_ablation.pdf) | This small difference does not establish an image benefit. These are terminal-image evaluations, not early-warning validation. |
| Campaign transfer is poor | The selected metadata-only GradientBoosting model has mean MAE **0.4650 kN** and mean R² **−4.6394** over two campaign holdouts. | [Campaign comparison](../structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/leave_one_campaign_out/feature_set_comparison.csv) | This is a different selected estimator from pooled Ridge. Campaign, mesh, chloride and exposure are confounded; do not attribute the gap to one causal factor. |
| Some surface accuracy reflects label reconstruction | Image-derived features can be closely related to the image-derived corrosion label, particularly total visible rust. | [Label-adjacency figure](../report_v2/figures/label_adjacency.pdf), [feature/target correlations](../structural_capacity/outputs/diagnostics/tables/feature_target_correlation_summary.csv) | Strong surface prediction does not establish hidden structural-damage prediction. |
| Threshold screening is exploratory | For model-derived wire-loss thresholds 0.20, 0.30 and 0.40, the saved summary reports **zero future crossings within the forecast horizon**, out of 48 specimens per threshold. | [Threshold summary](../report_v2/tables/threshold_summary.csv), [proxy outputs](../structural_capacity/outputs/models/proxy_rul/), [status figure](../report_v2/figures/threshold_status.pdf) | These are model-curve statuses, not observed lifetime events or validated remaining useful life. |
| Four-class preparation is ready for a training study | **38/5/5 specimens** in train/validation/test. Training: **3,846 rows** (641 originals + 3,205 augmentations); validation/test: **75 originals each**. | [Split summary](../report_v2/tables/classification_splits.csv), [fixed manifests](../Data/splits/) | Prepared data do not demonstrate classifier performance. Higher severity classes are scarce; keep all images and variants of a specimen in one partition. |

For the full interpretation, read the [current article](../report_v2/article/v3/article.pdf)
and [thesis](../report_v2/thesis/v3/thesis.pdf). The [data dictionary](data_dictionary.md)
defines targets, units and label versions.

## Inspect or reproduce a particular result

| Task | Inputs, settings and saved outputs | Entry point / current limitation |
|---|---|---|
| Inspect the pooled terminal-load benchmark | [Configuration](../structural_capacity/configs/ultimate_load_refocus.yaml), [specimen splits](../structural_capacity/outputs/ultimate_load_refocus/splits/grouped_cv_specimen_manifest.csv), [Ridge results](../structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/), [terminal OOF predictions](../structural_capacity/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/terminal_oof_predictions.csv) | [run_ultimate_load_refocus.py](../structural_capacity/run_ultimate_load_refocus.py), run from `structural_capacity/` only after source/configuration repair |
| Inspect sensitivity analyses | [Across-setting leaderboard](../structural_capacity/outputs/ultimate_load_refocus/comparisons/final_leaderboard.csv), [mesh-stratified results](../structural_capacity/outputs/ultimate_load_refocus/mesh_stratified/), [post-onset results](../structural_capacity/outputs/ultimate_load_refocus/pooled_post_onset/), [residual refinement](../structural_capacity/outputs/ultimate_load_refocus/residual_refinement/), [error audit](../structural_capacity/outputs/ultimate_load_refocus/error_audit/) | Saved analyses from the refocused workflow; subsets and estimators differ, so interpret each with its own split and cohort |
| Reproduce classification preparation | [Current workbook](../Data/Images_Dataset_A-Z-1.xlsx), [saved splits](../Data/splits/), five augmentations per original, seed `20260630` | [augment_dataset.py](../classification_data_preparation/augment_dataset.py) then [make_splits.py](../classification_data_preparation/make_splits.py); use the separate destinations in [reproduction](reproduction.md#3-classification-data-preparation-in-order) |
| Reproduce report tables/figures or compile the manuscripts | [Retained scientific tools](../report_v2/scripts/README.md), [tables](../report_v2/tables/), [figures](../report_v2/figures/) | Follow [report reproduction](reproduction.md#4-compile-a-report-without-fitting-a-model); tools can overwrite assets, so use a separate copy |

OOF means out-of-fold: a prediction made while that specimen is held out. The pooled
Ridge benchmark averages fold MAEs; a parity plot using mean OOF predictions uses a
different aggregation. Fold variation is descriptive, not an independent confidence
interval. Model selection used the reported evaluation folds.

The refocused workflow trains on historical image rows with repeated terminal
labels and evaluates terminal images. Both structural targets are measured only
once per specimen. Full-fit coefficients describe association, not causal effects
or held-out feature importance. Earlier robustness-selected models and later
refocused Ridge models are separate experiments; do not merge their metrics.

## Historical entry commands

These commands document execution order and working directories. Full generation
and training have not been rerun during cleanup; the known source/configuration
problems must be addressed before attempting them.

### Classical and embedding phases

From the parent of this checkout, keeping the package directory named `corrosion`:

```bash
python -m corrosion.classical_corrosion.train_models --help
python -m corrosion.image_embeddings.train_phase2 --help
```

Both help commands passed during folder migration. This verifies imports and
argument parsing only. The embedding API has a separate saved-preprocessor blocker.

### Condition-assessment phase

From the repository root, the intended sequence is:

```bash
python condition_assessment/scripts/01_inspect_dataset.py
python condition_assessment/scripts/02_build_metadata.py
python condition_assessment/scripts/03_preprocess_images.py
python condition_assessment/scripts/04_extract_features.py
python condition_assessment/scripts/05_train_corrosion_models.py
python condition_assessment/scripts/06_train_damage_models.py
python condition_assessment/scripts/07_fit_degradation_models.py
python condition_assessment/scripts/08_estimate_rul.py
python condition_assessment/scripts/09_generate_reports.py
```

### Structural robustness and terminal-load phases

From `structural_capacity/`, since these scripts add a relative `src` directory:

```bash
python run_audit_validation.py
python run_eda.py
python run_extract_image_features.py
python train_surface_models.py
python train_hidden_damage_models.py
python train_degradation_models.py
python train_rul_proxy_models.py
python run_diagnostics_visualizations.py
python run_model_improvement_analysis.py
```

The terminal-load refocus uses saved master data and configuration, with its own
entry point from the same working directory:

```bash
python run_ultimate_load_refocus.py
```

For every new run, preserve the delivered outputs and record the source state,
environment, configuration, input identities, specimen partitions and output
location. The [reproduction guide](reproduction.md) separates inspection from
commands that generate or replace files.

# Complete Project Report

## A. Project Overview

### Objective

The project aims to build a scientifically conservative baseline for:

surface corrosion analysis -> hidden damage estimation -> degradation modelling -> proxy-RUL

The emphasis is on interpretability, leakage-safe evaluation, and honest reporting of what the dataset can and cannot support.

### Scientific motivation

The research motivation is straightforward:

- corrosion is visible on the surface before deeper structural consequences are fully known
- images are abundant in this dataset
- structural measurements are sparse
- therefore, the project investigates whether visible surface patterns can act as a useful proxy for hidden degradation

### Dataset and documentation sources

Main sources:

- `Data/Images_Dataset_A-Z.xlsx`
- `Data/Images_dataset/`
- thesis PDF in `Documentation/Thesis/`
- conference paper PDF in `Documentation/Conferences/`

### Problem formulation

Direct supervised RUL prediction is not valid here because the dataset does not contain dense time-to-failure supervision.

The project therefore uses this formulation:

1. measure visible surface corrosion
2. estimate hidden damage on the small structural subset
3. smooth that hidden-damage signal over time
4. derive threshold-status or time-to-threshold style proxy outputs

This is the central scientific framing of the entire repository.

## B. Data Understanding

### Dataset composition

Verified facts:

- 792 image files were found
- 791 aligned workbook-image rows are usable
- 48 unique specimens are present
- one orphan/corrupted image exists: `E01-20240508-17W.png`

### Image and metadata structure

Each observation contains:

- a specimen image
- specimen ID
- ageing day and week
- surface corrosion measurements
- specimen metadata such as cover, treatment, campaign-related properties

The file `outputs/data/master_table.csv` is the canonical aligned dataset.

### Grouped longitudinal nature

This is a repeated-measures dataset:

- the same specimen is observed at multiple time points
- campaign 1 runs to week 28
- campaign 2 runs to week 36
- the grouped split key is `specimen_id`

This matters because train/test leakage would be easy if images from the same specimen were split incorrectly.

### Sparse structural labels

Structural labels are the main limitation:

- only 48 rows have structural labels
- this is exactly one structural row per specimen
- those labels occur at the terminal stage only

So the structural problem is underpowered compared with the dense surface problem.

### Why this matters for modelling

- dense surface labels support stable exploratory modelling
- sparse structural labels support only cautious baseline modelling
- grouped evaluation is mandatory
- leave-one-campaign-out becomes a particularly important stress test

## C. Pipeline Summary

### 1. Audit and validation

Implemented in:

- `run_audit_validation.py`
- `src/corrosion_proxy_rul/data_loading.py`
- `src/corrosion_proxy_rul/data_cleaning.py`
- `src/corrosion_proxy_rul/specimen_mapping.py`

Outputs:

- `outputs/audit/verified_facts.json`
- `outputs/audit/issues_log.csv`
- `outputs/data/master_table.csv`
- `outputs/data/terminal_structural_table.csv`

Purpose:

- align workbook rows with image files
- detect corrupt or missing files
- validate parsed sample names
- reconstruct deterministic campaign/treatment metadata

### 2. Preprocessing and image feature extraction

Implemented in:

- `run_extract_image_features.py`
- `src/corrosion_proxy_rul/image_features.py`
- `src/corrosion_proxy_rul/image_preprocessing.py`

Outputs:

- `outputs/features/image_features.csv`
- `outputs/features/feature_dictionary.csv`

Feature families:

- rust-mask ratios
- grayscale and color summaries
- histograms
- texture
- morphology
- strip-wise spatial corrosion summaries

### 3. Feature engineering

Implemented in:

- `src/corrosion_proxy_rul/feature_engineering.py`

Output:

- `outputs/data/full_feature_table.csv`

Purpose:

- merge metadata and image features
- define stage-specific modelling exclusions
- manage hidden-damage feature subsets

### 4. Split strategy

Implemented in:

- `src/corrosion_proxy_rul/splits.py`

Outputs:

- `outputs/splits/*`
- `outputs/models/*/splits/*`

Split strategies:

- grouped holdout by specimen
- leave-one-treatment-out
- leave-one-campaign-out

### 5. Surface modelling

Implemented in:

- `train_surface_models.py`
- `src/corrosion_proxy_rul/models_surface.py`

Outputs:

- `outputs/models/surface/*`

Role:

- mainly validates whether interpretable image features recover dense visible corrosion labels

### 6. Hidden-damage modelling

Implemented in:

- `train_hidden_damage_models.py`
- `src/corrosion_proxy_rul/models_hidden_damage.py`
- `src/corrosion_proxy_rul/evaluation.py`

Outputs:

- `outputs/models/hidden_damage/*`
- `outputs/improvements/tables/*`

Role:

- benchmark structural targets on the sparse labeled subset
- compare feature families and split strategies
- select models based on robustness, not only best grouped score

### 7. Degradation modelling

Implemented in:

- `train_degradation_models.py`
- `src/corrosion_proxy_rul/models_degradation.py`

Outputs:

- `outputs/models/degradation/*`

Role:

- extend hidden-damage estimates into specimen-level trajectories over time
- provide a smoothed degradation view for threshold analysis

### 8. Proxy-RUL logic

Implemented in:

- `train_rul_proxy_models.py`
- `src/corrosion_proxy_rul/models_rul_proxy.py`

Outputs:

- `outputs/models/proxy_rul/*`

Role:

- summarize threshold crossing status
- produce exploratory proxy-RUL fields where future crossings exist

### 9. Diagnostics and reporting

Implemented in:

- `run_diagnostics_visualizations.py`
- `src/corrosion_proxy_rul/diagnostics.py`
- `src/corrosion_proxy_rul/reporting.py`
- `run_model_improvement_analysis.py`

Outputs:

- `outputs/diagnostics/*`
- `FEATURE_DIAGNOSTICS.md`
- `BENCHMARK_DIAGNOSTICS.md`
- `FIGURE_REVIEW.md`
- `MODEL_IMPROVEMENT_RESULTS.md`

Role:

- convert raw outputs into interpretable plots
- explain redundancy, robustness, and weak points
- compare baseline vs improved structural stages

## D. Most Important Findings

### 1. The dataset and alignment are trustworthy

The project established a strong data foundation:

- 791 aligned rows
- 48 unique grouped specimens
- one explicit orphan/corrupt image
- leakage-safe split summaries reporting no specimen leakage

This is a solid finding.

### 2. Visible corrosion progression is real and explainable

The temporal plots show that surface corrosion generally increases with exposure time, although individual specimens and campaigns vary.

Most useful supporting figures:

- `outputs/diagnostics/figures/temporal/campaign_surface_progression_median_iqr.png`
- `outputs/diagnostics/figures/temporal/representative_specimen_surface_panels.png`
- `outputs/diagnostics/figures/temporal/surface_progression_scatter_trends.png`

This is a solid finding.

### 3. Interpretable image features capture visible corrosion well

The strongest image-feature finding is that the rust-mask area ratio tracks visible surface corrosion extremely closely.

Important nuance:

- this is scientifically useful as a validation of the image-analysis pipeline
- it is not strong evidence of hidden-damage inference

This is a solid finding, but only for the visible-corrosion stage.

### 4. The feature space is redundant and needed cleanup

Diagnostics found:

- near-constant features
- exact duplicates
- many highly collinear feature pairs

The cleanup was not cosmetic. It clarified that a large part of the feature space was repeating similar information.

This is a solid finding.

### 5. The benchmark story is about robustness, not just best score

The project learned more from robustness diagnostics than from headline MAE values.

Key lesson:

- surface benchmarks look strong, but the main surface target is largely a sanity-check target
- structural benchmarks weaken sharply under harder split regimes
- leave-one-campaign-out is the most informative stress test

This is a solid finding.

### 6. Hidden-damage generalization remains weak

The hidden-damage stage improved in a conservative sense after feature cleanup and robustness-aware selection, but the best structural models became metadata-only models.

This means:

- the current robust signal is dominated by time/design metadata
- image features are not yet providing strong robust structural inference

This is one of the most important project conclusions.

### 7. Degradation and proxy-RUL are still exploratory

The degradation stage is mainly descriptive smoothing of model-generated hidden-damage proxies.

The proxy-RUL stage currently produces threshold-status summaries rather than usable forward residual-life estimates.

This is a weak or exploratory result, not a strong predictive claim.

## E. Important Figures

### 1. `outputs/eda/figures/missingness.png`

Caption:

Missingness overview for the main dataset variables.

What it demonstrates:

- surface variables are dense
- structural variables are sparse

Why it is important:

- it immediately explains why direct RUL prediction is invalid

### 2. `outputs/eda/figures/structural_target_sparsity.png`

Caption:

Visual summary of structural-label sparsity.

What it demonstrates:

- structural supervision exists only at terminal rows

Why it is important:

- it supports the project's conservative formulation

### 3. `outputs/diagnostics/figures/temporal/campaign_surface_progression_median_iqr.png`

Caption:

Median visible corrosion progression over time by campaign.

What it demonstrates:

- corrosion progression is real
- campaigns differ in level and spread

Why it is important:

- it is the clearest high-level time-progress figure in the project

### 4. `outputs/diagnostics/figures/temporal/representative_specimen_surface_panels.png`

Caption:

Representative specimen trajectories across time.

What it demonstrates:

- the data are truly longitudinal
- progression is not perfectly smooth within each specimen

Why it is important:

- it helps explain the repeated-measures nature of the dataset

### 5. `outputs/diagnostics/figures/features/feature_target_correlation_heatmap.png`

Caption:

Focused feature-target correlation map.

What it demonstrates:

- which engineered image features strongly track visible corrosion
- how weak the structural relationships are by comparison

Why it is important:

- one of the best summary figures for explaining what the features really capture

### 6. `outputs/diagnostics/figures/features/image_feature_correlation_heatmap.png`

Caption:

Correlation structure among key image features.

What it demonstrates:

- many image features are highly related to each other

Why it is important:

- supports the feature-cleanup argument

### 7. `outputs/diagnostics/figures/features/high_collinearity_pairs.png`

Caption:

Highest-collinearity feature pairs in the modelling space.

What it demonstrates:

- why some features should be removed or down-weighted in interpretation

Why it is important:

- makes the redundancy issue concrete

### 8. `outputs/diagnostics/figures/distributions/skewed_variable_histograms_trimmed_p99.png`

Caption:

Readability-focused histograms for skewed variables, truncated at high percentiles for visualization only.

What it demonstrates:

- many variables are heavy-tailed
- some engineered features are unstable

Why it is important:

- supports honest outlier handling without hiding extreme values

### 9. `outputs/diagnostics/figures/benchmarks/best_model_relative_mae_collapse_heatmap.png`

Caption:

Relative error inflation across evaluation strategies.

What it demonstrates:

- where performance remains stable
- where it collapses under harder generalization tests

Why it is important:

- best single figure for explaining robustness

### 10. `outputs/diagnostics/figures/proxy/proxy_threshold_status_counts.png`

Caption:

Threshold-status counts for the proxy-RUL stage.

What it demonstrates:

- most cases are already crossed or right-censored
- no future threshold crossings are produced within the current horizon

Why it is important:

- communicates the honest status of the final stage

## F. Weak Or Limited Parts

### Sparse structural targets

The structural targets are present on only 48 rows, one per specimen.

Implication:

- the hidden-damage stage is structurally underpowered

### Weak hidden-damage generalization

Even after the improvement round:

- `ultimate_load_kn` improved, but still weakens strongly under leave-one-campaign-out
- `wire_area_loss_frac` remains weak and unstable

Implication:

- robust structural inference from images is not established

### Campaign confounding

The improvement round showed that metadata-only models were the most robust for structural targets.

Implication:

- the current structural signal is still tied strongly to campaign/time/design information

### Surface benchmark caveat

`surface_total_rust_pct` is almost numerically identical to an engineered rust-mask feature.

Implication:

- the surface stage is useful, but mainly as a label-reconstruction sanity check

### Degradation and proxy-RUL limitations

The degradation stage is a descriptive smoothing layer, and the proxy stage does not currently produce practical forward RUL estimates.

Implication:

- these outputs are exploratory and should not be overclaimed

## G. Final Conclusion

### What has been successfully achieved

The project has successfully produced:

- a verified aligned dataset
- a deterministic and reviewable specimen mapping
- an interpretable image-feature extraction pipeline
- leakage-safe split design
- clear temporal corrosion progression analysis
- strong feature diagnostics and redundancy analysis
- robustness-oriented benchmark reporting
- an honest improvement round with before/after evidence

### What remains exploratory

The following remain exploratory or limited:

- hidden-damage inference from images
- cross-campaign structural generalization
- degradation-as-prediction claims
- proxy-RUL as practical decision support

### What is ready to present now

Ready to present confidently:

- the data audit
- the longitudinal dataset structure
- the interpretable image features
- the temporal corrosion progression story
- the feature diagnostics
- the robustness-based benchmark interpretation
- the honest negative findings on structural generalization

### What should be improved next

The next scientifically useful improvement is not a new flashy model.

The next priority is to reduce campaign shortcut dependence and test how much structural signal remains once campaign-sensitive metadata are restricted more aggressively.

### Bottom line

This project is already presentation-worthy because it does something valuable and defensible:

it turns a raw corrosion-image dataset into an audited, interpretable, leakage-safe baseline, and it clearly shows both what the data supports and where the current scientific limits still are.

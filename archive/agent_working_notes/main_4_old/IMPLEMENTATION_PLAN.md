# Implementation Plan

## Goal

Create a research-grade baseline codebase for:

```text
surface corrosion analysis
-> hidden damage estimation
-> degradation modelling
-> proxy-RUL estimation
```

This plan intentionally avoids an initial end-to-end neural codebase.

## Proposed Codebase Structure

```text
main_4/
├── configs/
│   ├── dataset.yaml
│   ├── features.yaml
│   ├── modeling.yaml
│   └── thresholds.yaml
├── src/
│   └── corrosion_proxy_rul/
│       ├── __init__.py
│       ├── config.py
│       ├── constants.py
│       ├── io/
│       │   ├── __init__.py
│       │   ├── paths.py
│       │   ├── excel_loader.py
│       │   ├── image_index.py
│       │   └── thesis_lookup.py
│       ├── data/
│       │   ├── __init__.py
│       │   ├── schema.py
│       │   ├── harmonize.py
│       │   ├── alignment.py
│       │   ├── specimen_metadata.py
│       │   └── master_table.py
│       ├── features/
│       │   ├── __init__.py
│       │   ├── metadata_features.py
│       │   ├── image_preprocess.py
│       │   ├── rust_mask.py
│       │   ├── strip_features.py
│       │   ├── morphology_features.py
│       │   ├── texture_features.py
│       │   └── longitudinal_features.py
│       ├── splits/
│       │   ├── __init__.py
│       │   ├── grouped.py
│       │   ├── treatment_holdout.py
│       │   └── campaign_holdout.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── registry.py
│       │   ├── surface_regression.py
│       │   ├── hidden_damage.py
│       │   ├── ultimate_load.py
│       │   ├── degradation.py
│       │   └── proxy_rul.py
│       ├── evaluation/
│       │   ├── __init__.py
│       │   ├── metrics.py
│       │   ├── run_cv.py
│       │   ├── uncertainty.py
│       │   └── diagnostics.py
│       └── reporting/
│           ├── __init__.py
│           ├── figures.py
│           ├── tables.py
│           └── report_builder.py
├── scripts/
│   ├── 00_dataset_audit.py
│   ├── 01_build_master_table.py
│   ├── 02_extract_engineered_image_features.py
│   ├── 03_train_surface_models.py
│   ├── 04_train_hidden_damage_models.py
│   ├── 05_train_ultimate_load_models.py
│   ├── 06_fit_degradation_models.py
│   ├── 07_estimate_proxy_rul.py
│   └── 08_generate_report.py
├── tests/
│   ├── test_alignment.py
│   ├── test_schema.py
│   ├── test_unit_conversions.py
│   ├── test_grouped_splits.py
│   └── test_rust_features.py
├── artifacts/
│   ├── audit/
│   ├── data/
│   ├── features/
│   ├── models/
│   ├── predictions/
│   └── reports/
├── reports/
│   ├── figures/
│   └── tables/
├── PROJECT_AUDIT.md
├── SCIENTIFIC_SOLUTION_PLAN.md
└── IMPLEMENTATION_PLAN.md
```

## Package Responsibilities

### `io/`

Responsible for raw asset access only.

- load the Excel workbook with two-row header handling
- index readable images
- expose thesis-derived lookup tables for campaign and treatment reconstruction

### `data/`

Responsible for canonical tabular dataset creation.

- rename columns
- correct data types
- convert wire area loss fraction / percent units explicitly
- reconstruct:
  - `campaign_id`
  - `series_id`
  - `treatment_protocol`
  - `calendar_date`
  - `week`
  - `is_terminal_structural_row`
- build the aligned master table

### `features/`

Responsible for all inference-available features.

- metadata covariates
- RGB rust-mask features
- strip-wise corrosion descriptors
- morphology
- texture
- longitudinal summary features

### `splits/`

Responsible for leakage-safe split manifest creation.

- `GroupShuffleSplit`
- leave-one-treatment-out
- leave-one-campaign-out

### `models/`

Responsible for each modelling stage separately.

- surface corrosion models
- hidden damage models
- ultimate load models
- degradation models
- proxy-RUL estimators

### `evaluation/`

Responsible for:

- grouped CV execution
- metrics
- bootstrap intervals
- model comparison tables

### `reporting/`

Responsible for:

- figure generation
- summary tables
- markdown report assembly

## Canonical Master Table Design

The first executable artifact should be a master table with one row per aligned image observation.

Recommended columns:

- `observation_id`
- `sample_name`
- `specimen_id`
- `campaign_id`
- `series_id`
- `treatment_protocol`
- `treatment_coarse`
- `treatment_label_coarse`
- `calendar_date`
- `week`
- `ageing_days`
- `n_steel_mesh`
- `cover_mm`
- `image_path`
- `surface_total_rust_pct`
- `surface_total_rust_cat`
- `peak_rust_pct`
- `peak_rust_cat`
- `peak_rust_location_cm`
- `wire_area_loss_frac`
- `wire_area_loss_pct`
- `ultimate_load_kn`
- `has_structural_label`
- `is_terminal_structural_row`
- `split_group_specimen`
- `split_group_treatment`
- `split_group_campaign`

Rules:

- `wire_area_loss_frac` should keep the raw stored value in `[0, 1]`
- `wire_area_loss_pct` should be derived as `100 * wire_area_loss_frac`
- the orphan unreadable image must be excluded from this table

## Training Pipeline Stages

### Stage 0: dataset audit and split manifest generation

Script:

- `scripts/00_dataset_audit.py`

Outputs:

- `artifacts/audit/dataset_inventory.json`
- `artifacts/audit/alignment_report.csv`
- `artifacts/audit/missingness_summary.csv`
- `artifacts/audit/specimen_time_coverage.csv`
- `artifacts/audit/data_quality_flags.csv`
- `artifacts/data/splits_group_shuffle.json`
- `artifacts/data/splits_leave_one_treatment_out.json`
- `artifacts/data/splits_leave_one_campaign_out.json`

### Stage 1: master table build

Script:

- `scripts/01_build_master_table.py`

Outputs:

- `artifacts/data/master_table.parquet`
- `artifacts/data/master_table.csv`
- `artifacts/data/terminal_structural_table.parquet`

Checks:

- no duplicate `(specimen_id, ageing_days)`
- all aligned images readable
- terminal structural rows count equals `48`

### Stage 2: engineered image feature extraction

Script:

- `scripts/02_extract_engineered_image_features.py`

Feature families:

- rust-mask area fraction
- rust-color statistics
- strip summary features
- location features
- morphology features
- texture features
- image QA features

Outputs:

- `artifacts/features/image_features.parquet`
- `artifacts/features/image_features.csv`
- `artifacts/features/feature_dictionary.json`
- `artifacts/features/qa_image_failures.csv`

### Stage 3: surface model training

Script:

- `scripts/03_train_surface_models.py`

Targets:

- `surface_total_rust_pct`
- `peak_rust_pct`
- optional category targets

Model families:

- Random Forest
- Gradient Boosting
- XGBoost
- CatBoost

Feature ablations:

- metadata only
- image features only
- fused features

Outputs:

- `artifacts/models/surface/<target>/<model_name>/model.pkl`
- `artifacts/predictions/surface_cv_predictions.parquet`
- `artifacts/reports/surface_model_metrics.csv`
- `artifacts/reports/surface_feature_importance.csv`

### Stage 4: hidden-damage model training

Script:

- `scripts/04_train_hidden_damage_models.py`

Training table:

- only `48` terminal structural rows

Target:

- `wire_area_loss_frac`

Feature sets:

- metadata only
- image features only
- predicted / rederived surface metrics only
- fused features

Candidate models:

- Random Forest
- Gradient Boosting
- XGBoost
- CatBoost

Outputs:

- `artifacts/models/hidden_damage/<model_name>/model.pkl`
- `artifacts/predictions/hidden_damage_cv_predictions.parquet`
- `artifacts/reports/hidden_damage_metrics.csv`
- `artifacts/reports/hidden_damage_feature_importance.csv`

### Stage 5: ultimate-load model training

Script:

- `scripts/05_train_ultimate_load_models.py`

Training table:

- only `48` terminal structural rows

Target:

- `ultimate_load_kn`

Recommended features:

- predicted hidden damage
- metadata covariates
- engineered image features
- surface severity summaries

Outputs:

- `artifacts/models/ultimate_load/<model_name>/model.pkl`
- `artifacts/predictions/ultimate_load_cv_predictions.parquet`
- `artifacts/reports/ultimate_load_metrics.csv`

### Stage 6: degradation modelling

Script:

- `scripts/06_fit_degradation_models.py`

Input:

- full longitudinal master table
- selected hidden-damage model

Procedure:

1. predict hidden-damage proxy at every time point
2. smooth each specimen trajectory with monotone constraints
3. compare curve families:
   - linear in time
   - linear in log-time
   - monotone spline
   - Gompertz / logistic
4. estimate specimen-level and treatment-level trajectories

Outputs:

- `artifacts/models/degradation/degradation_fits.parquet`
- `artifacts/predictions/degradation_state_timeseries.parquet`
- `artifacts/reports/degradation_model_selection.csv`

### Stage 7: proxy-RUL estimation

Script:

- `scripts/07_estimate_proxy_rul.py`

Input thresholds from:

- `configs/thresholds.yaml`

Recommended threshold config entries:

- wire area loss fraction thresholds
- load-retention thresholds relative to campaign-specific untreated baselines
- uncertainty quantile settings

Outputs:

- `artifacts/predictions/proxy_rul_estimates.parquet`
- `artifacts/reports/proxy_rul_threshold_scenarios.csv`
- `artifacts/reports/proxy_rul_specimen_summary.csv`

### Stage 8: report generation

Script:

- `scripts/08_generate_report.py`

Outputs:

- `artifacts/reports/baseline_report.md`
- `artifacts/reports/baseline_report.html`
- figure and table bundles under `reports/`

## Mandatory Evaluation Design

Every training script must expose three evaluation regimes.

### Regime 1: GroupShuffleSplit

- primary model-selection regime
- `groups = specimen_id`

### Regime 2: leave-one-treatment-out

- treatment groups must come from reconstructed treatment protocol
- do not use workbook `Treatment` alone

Recommended treatment holdout groups:

- `S1_MI`
- `S2_SA`
- `S3_PA_SA`
- `S4_SA_VF`
- `S5_VF`
- `D_NO`
- `E_SA_SPRAY`
- `F_SA_BRUSH`
- `G_PAINT`

### Regime 3: leave-one-campaign-out

- `campaign_id` is the holdout group
- treat this as a stress test, not the only selection regime

## Figure And Report Outputs

The reporting layer should generate at minimum:

1. repository and dataset inventory table
2. missingness heatmap
3. specimen-by-timepoint coverage matrix
4. campaign / treatment timeline chart
5. image QA summary
6. surface corrosion trajectories by specimen
7. average surface trajectories by treatment
8. terminal scatter plots:
   - surface rust vs wire area loss
   - wire area loss vs ultimate load
   - cover vs wire area loss
9. grouped-CV model comparison table
10. feature importance / SHAP summary for the best baseline models
11. degradation trajectory plots with threshold lines
12. proxy-RUL sensitivity plots across thresholds

## Execution Order

Run the project in this order:

1. `00_dataset_audit.py`
2. `01_build_master_table.py`
3. `02_extract_engineered_image_features.py`
4. `03_train_surface_models.py`
5. `04_train_hidden_damage_models.py`
6. `05_train_ultimate_load_models.py`
7. `06_fit_degradation_models.py`
8. `07_estimate_proxy_rul.py`
9. `08_generate_report.py`

Dependencies by stage:

- Stages 4 and 5 depend on Stage 1 and Stage 2.
- Stage 6 depends on the selected Stage 4 hidden-damage model.
- Stage 7 depends on Stage 6 and the threshold configuration.
- Stage 8 depends on all previous stages.

## Baseline Package Choices

Recommended Python stack for the first implementation:

- `pandas`
- `numpy`
- `scikit-learn`
- `xgboost`
- `catboost`
- `scipy`
- `opencv-python` or `scikit-image`
- `Pillow`
- `matplotlib`
- `seaborn`
- `statsmodels` or `pygam` for interpretable smoothing
- `pyarrow`
- `pyyaml`

Optional later additions:

- `shap`
- `lightgbm`
- `torch` only for the advanced path

## Recommended Baseline Pipeline

The baseline codebase should implement:

1. a thesis-aligned data harmonization layer
2. interpretable corrosion feature extraction from images
3. grouped surface-regression baselines
4. terminal hidden-damage regression
5. terminal ultimate-load regression
6. monotone degradation modelling
7. threshold-based proxy-RUL reporting

## Recommended Advanced Pipeline

Reserve a later extension for:

- pretrained vision embeddings fused with engineered corrosion features
- hierarchical latent-state degradation modelling
- uncertainty-aware threshold crossing

That advanced path should extend the baseline package, not replace it.

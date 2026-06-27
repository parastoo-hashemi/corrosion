# Codebase Guide

## 1. How To Read This Repository

The project is organized like a pipeline:

1. validate the data
2. generate EDA
3. extract interpretable image features
4. build feature tables
5. train surface models
6. train hidden-damage models
7. build degradation trajectories
8. generate proxy-RUL threshold-status outputs
9. generate diagnostics, reports, and before/after improvement summaries

If you understand the entry scripts, the config files, and the main modules in `src/corrosion_proxy_rul/`, you understand most of the project.

## 2. Top-Level Scripts

| File | Role | Inputs | Outputs | What it does | Why it matters | Importance |
| --- | --- | --- | --- | --- | --- | --- |
| `run_audit_validation.py` | Data audit entry point | Excel workbook, image folder, specimen mapping | master table, audit tables, split manifests, verified facts | Loads raw metadata and image inventory, checks alignment, applies mapping, builds canonical data tables | Creates the trusted starting dataset | Core |
| `run_eda.py` | EDA entry point | `outputs/data/master_table.csv` | `outputs/eda/*` | Generates counts, missingness summaries, and early dataset figures | Best first script for understanding the dataset | Core |
| `run_extract_image_features.py` | Image-feature extraction entry point | `master_table.csv`, `configs/features.yaml` | `outputs/features/image_features.csv`, feature dictionary, failure log | Extracts deterministic interpretable features from each image | Connects images to modelling | Core |
| `train_surface_models.py` | Surface-model training entry point | master table, image features, configs | `outputs/models/surface/*` | Trains grouped baselines for visible corrosion targets | Validates the image-feature pipeline | Core |
| `train_hidden_damage_models.py` | Structural modelling entry point | full feature table, configs | `outputs/models/hidden_damage/*`, improvement tables | Trains and compares structural models with feature ablations and robustness-aware selection | Main place where hidden-damage learning is tested | Core |
| `train_degradation_models.py` | Degradation entry point | full feature table, hidden-damage model outputs | `outputs/models/degradation/*` | Converts hidden-damage predictions into specimen-level trajectories | Builds the bridge from structural estimation to threshold analysis | Core |
| `train_rul_proxy_models.py` | Proxy-RUL entry point | degradation fits, thresholds config | `outputs/models/proxy_rul/*` | Converts trajectories into threshold-status summaries | Produces the exploratory final stage | Core |
| `run_diagnostics_visualizations.py` | Diagnostics entry point | all major outputs | `outputs/diagnostics/*` plus diagnostics markdown files | Creates feature, benchmark, temporal, degradation, and proxy diagnostics | Best script for presentation support | Core |
| `run_model_improvement_analysis.py` | Improvement comparison entry point | baseline snapshot, current outputs | `outputs/improvements/tables/*`, improvement markdown files | Compares baseline and improved hidden-damage results | Important for understanding what changed and why | Support |
| `run_full_baseline.py` | Orchestration script | all raw inputs and configs | full baseline pipeline outputs | Runs the end-to-end baseline in sequence and refreshes README/report files | Useful if you want one command for the main pipeline | Support |

## 3. Core Python Modules

### 3.1 Configuration and file utilities

| File | Role | Inputs | Outputs | Why it matters | Importance |
| --- | --- | --- | --- | --- | --- |
| `src/corrosion_proxy_rul/config.py` | Config loader | YAML files in `configs/` | Python dictionaries | Central access point for all config values | Core |
| `src/corrosion_proxy_rul/utils_paths.py` | Path and I/O utilities | filesystem paths, dataframes, text/json payloads | saved files, configured loggers | Keeps file writing and logging consistent | Core |

### 3.2 Data loading and validation

| File | Role | Inputs | Outputs | What it actually does | Importance |
| --- | --- | --- | --- | --- | --- |
| `src/corrosion_proxy_rul/data_loading.py` | Raw data loader | workbook path, image folder | metadata dataframe, image scan dataframe | Normalizes workbook schema, parses sample names, scans image readability and dimensions | Core |
| `src/corrosion_proxy_rul/schema_validation.py` | Schema checks | raw metadata dataframe | issue records | Checks required columns, duplicates, and specimen-level consistency | Core |
| `src/corrosion_proxy_rul/specimen_mapping.py` | Mapping logic | canonical specimen mapping YAML | mapped dataframe, validated mapping table | Joins campaign and treatment metadata from the explicit YAML mapping | Core |
| `src/corrosion_proxy_rul/data_cleaning.py` | Canonical dataset builder | metadata dataframe, image scan dataframe | `master_df`, terminal subset, issues table | Parses metadata fields, checks mismatches, merges images, logs problems, derives canonical columns | Core |

### 3.3 Feature extraction and feature engineering

| File | Role | Inputs | Outputs | What it actually does | Importance |
| --- | --- | --- | --- | --- | --- |
| `src/corrosion_proxy_rul/image_preprocessing.py` | Low-level image preprocessing | image path | RGB and grayscale arrays | Loads PNGs and converts them to grayscale | Support |
| `src/corrosion_proxy_rul/image_features.py` | Main image-feature extractor | aligned master table, feature config | image feature table, feature dictionary, failures table | Extracts rust masks, histograms, texture, morphology, and strip features | Core |
| `src/corrosion_proxy_rul/feature_engineering.py` | Feature-table builder and feature-set selector | master table, image feature table | full feature table, hidden-damage feature subsets | Merges features and implements modelling exclusions, feature families, and hidden-damage feature-set cleanup | Core |

### 3.4 Splitting and evaluation

| File | Role | Inputs | Outputs | What it actually does | Importance |
| --- | --- | --- | --- | --- | --- |
| `src/corrosion_proxy_rul/splits.py` | Split generator | feature table and grouping columns | split manifests and split summaries | Builds grouped holdout, leave-one-treatment-out, and leave-one-campaign-out splits | Core |
| `src/corrosion_proxy_rul/evaluation.py` | Shared model evaluation engine | dataframe, feature list, target, split manifest, model config | fold metrics, predictions, summary tables, fitted bundles | Trains the four baseline regressor families and computes MAE, RMSE, R2, and Spearman | Core |

### 3.5 Modelling modules

| File | Role | Inputs | Outputs | What it actually does | Importance |
| --- | --- | --- | --- | --- | --- |
| `src/corrosion_proxy_rul/models_surface.py` | Surface-modelling stage | master table, image features, configs | `outputs/models/surface/*` | Builds the surface feature table, runs grouped surface benchmarks, saves summaries and feature importance | Core |
| `src/corrosion_proxy_rul/models_hidden_damage.py` | Hidden-damage modelling stage | full feature table, configs | `outputs/models/hidden_damage/*` and improvement tables | Runs feature-set ablations, robustness-aware selection, final structural benchmarks, and selected feature exports | Core |
| `src/corrosion_proxy_rul/models_degradation.py` | Degradation stage | full feature table, selected hidden-damage model, configs | `outputs/models/degradation/*` | Predicts hidden damage across time, enforces monotonicity, fits trajectory families, saves curves and summaries | Core |
| `src/corrosion_proxy_rul/models_rul_proxy.py` | Proxy-RUL stage | degradation best-fit table, trajectory grid, thresholds | `outputs/models/proxy_rul/*` | Computes threshold crossing status and simple proxy-RUL fields | Core |

### 3.6 Reporting and diagnostics

| File | Role | Inputs | Outputs | What it actually does | Importance |
| --- | --- | --- | --- | --- | --- |
| `src/corrosion_proxy_rul/eda.py` | Dataset exploration | master table | `outputs/eda/*` | Builds summary tables and early project figures | Core |
| `src/corrosion_proxy_rul/diagnostics.py` | Diagnostics layer | existing outputs across the project | `outputs/diagnostics/*`, diagnostics markdown summaries | Converts major CSV outputs into plot companions and diagnostic tables | Core |
| `src/corrosion_proxy_rul/visualization.py` | Shared plotting helpers | dataframes and plot parameters | PNG figures | Central plotting utilities used by multiple stages | Support |
| `src/corrosion_proxy_rul/reporting.py` | Text report writer | facts, benchmark tables, degradation/proxy summaries | README and scientific report markdown | Keeps top-level narrative files synchronized with outputs | Core |

## 4. YAML Config Files

| File | What it stores | Why it matters | Importance |
| --- | --- | --- | --- |
| `configs/dataset.yaml` | canonical paths, key columns, target lists, data policy | Documents what raw inputs are used and the rule that only aligned readable images are allowed | Core |
| `configs/features.yaml` | image-feature extraction settings, physical length, strip geometry, RGB thresholds | Defines how corrosion indicators are extracted from images | Core |
| `configs/modeling.yaml` | random seed, split settings, model hyperparameters, degradation settings, feature-cleanup rules, hidden-damage feature-set rules | Controls how models are trained and selected | Core |
| `configs/thresholds.yaml` | proxy-RUL thresholds and horizon | Defines the exploratory threshold-status logic | Core |
| `configs/specimen_mapping.yaml` | specimen-to-campaign and treatment mapping reconstructed from thesis evidence | Prevents hidden ad hoc mapping logic in code | Core |

## 5. Main Documentation And Review Files

| File | What it is for | Use it when | Importance |
| --- | --- | --- | --- |
| `PROJECT_AUDIT.md` | raw project and dataset audit | you want the origin story of the project and raw data facts | Core |
| `PROJECT_CONSTRAINTS.md` | canonical verified project facts | you need the final accepted dataset facts and scientific rules | Core |
| `SCIENTIFIC_SOLUTION_PLAN.md` | original scientific solution design | you want to see the intended modelling philosophy | Support |
| `IMPLEMENTATION_PLAN.md` | implementation contract | you want to see how the code structure was planned | Support |
| `SCIENTIFIC_REPORT.md` | current concise scientific summary | you need the current short summary of what the pipeline supports | Core |
| `OUTPUT_REVIEW.md` | strict review of generated outputs | you want an honest assessment of what is scientifically meaningful and what is weak | Core |
| `FEATURE_DIAGNOSTICS.md` | feature-space interpretation | you want a quick summary of redundancy, correlation, and feature quality | Core |
| `BENCHMARK_DIAGNOSTICS.md` | robustness-oriented benchmark summary | you want a quick summary of where models hold up and where they collapse | Core |
| `FIGURE_REVIEW.md` | figure quality assessment | you want to know which figures are strong, weak, redundant, or misleading | Core |
| `MODEL_IMPROVEMENT_PLAN.md` | focused improvement plan | you want to know what changes were justified before code edits | Support |
| `MODEL_IMPROVEMENTS_APPLIED.md` | change log for the improvement round | you want to know what was changed and rerun | Support |
| `MODEL_IMPROVEMENT_RESULTS.md` | before/after improvement comparison | you want to know whether the improvement round actually helped | Core |
| `OUTPUT_VISUALIZATION_PLAN.md` | mapping from outputs to visual companions | you want to see which CSVs have matching plots | Support |

## 6. Major Output Folders

| Folder | What is inside | Most important files | Why it matters |
| --- | --- | --- | --- |
| `outputs/audit/` | audit tables and verified facts | `verified_facts.json`, `issues_log.csv`, `image_scan.csv` | Best place to confirm the dataset is valid |
| `outputs/data/` | clean canonical data tables | `master_table.csv`, `terminal_structural_table.csv`, `full_feature_table.csv` | Main data products used by later stages |
| `outputs/features/` | extracted image features | `image_features.csv`, `feature_dictionary.csv` | Shows what the images were turned into |
| `outputs/eda/` | first-pass dataset exploration | `specimen_summary.csv`, `missingness.png`, `structural_target_sparsity.png` | Best place to understand the dataset at a glance |
| `outputs/splits/` | top-level split manifests | `master_group_shuffle_summary.csv`, `master_leave_one_campaign_out_summary.csv` | Confirms grouped splitting and leakage safety |
| `outputs/models/surface/` | surface-model outputs | `best_models.csv`, per-target summaries and predictions | Surface-label reconstruction and auxiliary surface benchmarks |
| `outputs/models/hidden_damage/` | structural-model outputs | `best_models.csv`, `hidden_damage_feature_ablation_results.csv`, `hidden_damage_campaign_confounding.csv` | Main evidence for or against hidden-damage inference |
| `outputs/models/degradation/` | trajectory outputs | `degradation_best_fits.csv`, `degradation_trajectory_grid.csv`, `degradation_raw_vs_monotone_proxy.csv` | Shows how hidden-damage predictions were smoothed over time |
| `outputs/models/proxy_rul/` | threshold-status outputs | `proxy_rul_summary.csv`, `proxy_rul_estimates.csv` | Final exploratory proxy-RUL stage |
| `outputs/diagnostics/` | diagnostics tables and figures | `feature_inventory_by_stage.csv`, `feature_target_correlation_summary.csv`, `benchmark_best_model_robustness.csv` plus all figure folders | Best folder for presentation preparation |
| `outputs/improvements/` | baseline-vs-improved comparison artifacts | `baseline_vs_improved_benchmark_comparison.csv`, `split_strategy_robustness_comparison.csv` | Best place to understand what changed in the improvement round |
| `outputs/logs/` | run logs | stage-specific `.log` files | Best place to check whether a stage ran successfully |

## 7. Most Important CSV And JSON Outputs

| File | What it contains | Why you should care |
| --- | --- | --- |
| `outputs/audit/verified_facts.json` | final verified dataset facts | Best single source for row counts, specimen counts, structural-row counts, and the grouped split key |
| `outputs/audit/issues_log.csv` | explicit audit issues | Shows whether any missing, unreadable, or orphan files were found |
| `outputs/data/master_table.csv` | canonical aligned observation table | Most important dataset file in the project |
| `outputs/data/terminal_structural_table.csv` | terminal structural subset | Shows exactly which rows support hidden-damage modelling |
| `outputs/data/full_feature_table.csv` | merged metadata and image-feature table | Starting point for most modelling and diagnostics |
| `outputs/features/image_features.csv` | interpretable per-image feature matrix | Best table for understanding what the images were converted into |
| `outputs/features/feature_dictionary.csv` | plain-language feature descriptions | Best reference when a feature name is unfamiliar |
| `outputs/eda/tables/specimen_summary.csv` | specimen-level trajectory summary | Useful for presentation and for understanding campaign/treatment structure |
| `outputs/diagnostics/tables/feature_inventory_by_stage.csv` | which features exist, their family, and whether they were included | Best transparency table for the modelling feature space |
| `outputs/diagnostics/tables/feature_target_correlation_summary.csv` | feature-target correlation summary | Best table for understanding what features are informative and which targets are weak |
| `outputs/diagnostics/tables/high_collinearity_pairs.csv` | strongest redundant feature pairs | Best table for explaining why feature cleanup was needed |
| `outputs/diagnostics/tables/benchmark_best_model_robustness.csv` | best-model benchmark summary across split strategies | Best table for explaining robustness vs collapse |
| `outputs/models/surface/best_models.csv` | selected surface models | Quick summary of which surface models were kept |
| `outputs/models/hidden_damage/best_models.csv` | selected hidden-damage models | Quick summary of which structural models were kept and what feature set they use |
| `outputs/models/hidden_damage/hidden_damage_feature_ablation_results.csv` | best result per feature set and split strategy | Best table for campaign-confounding and feature-family discussion |
| `outputs/models/hidden_damage/hidden_damage_campaign_confounding.csv` | comparison against the full feature space | Best table for showing whether performance depends on campaign-sensitive features |
| `outputs/models/hidden_damage/hidden_damage_selected_feature_list.csv` | final features actually used in the selected structural models | Best table for explaining the final structural feature space |
| `outputs/models/degradation/degradation_best_fits.csv` | best trajectory family per specimen | Main summary of the degradation stage |
| `outputs/models/degradation/degradation_raw_vs_monotone_proxy.csv` | raw vs monotone hidden-damage proxy trajectories | Best table for explaining why smoothing was needed |
| `outputs/models/proxy_rul/proxy_rul_summary.csv` | threshold-status summary by threshold | Best summary of the final exploratory proxy-RUL stage |
| `outputs/improvements/tables/baseline_vs_improved_benchmark_comparison.csv` | before/after structural benchmark comparison | Best table for explaining what improved and what did not |
| `outputs/improvements/tables/split_strategy_robustness_comparison.csv` | before/after robustness comparison | Best table for explaining whether robustness changed |

## 8. What You Need To Understand First

If you only want the shortest useful reading order:

1. `PROJECT_CONSTRAINTS.md`
2. `PROJECT_EXPLANATION_FOR_PRESENTATION.md`
3. `outputs/data/master_table.csv`
4. `outputs/features/image_features.csv`
5. `FEATURE_DIAGNOSTICS.md`
6. `BENCHMARK_DIAGNOSTICS.md`
7. `SCIENTIFIC_REPORT.md`

Then, if you want the code path:

1. `run_audit_validation.py`
2. `run_extract_image_features.py`
3. `train_hidden_damage_models.py`
4. `src/corrosion_proxy_rul/data_cleaning.py`
5. `src/corrosion_proxy_rul/image_features.py`
6. `src/corrosion_proxy_rul/feature_engineering.py`
7. `src/corrosion_proxy_rul/models_hidden_damage.py`
8. `src/corrosion_proxy_rul/diagnostics.py`

## 9. What Is Core vs Support vs Optional

### Core for understanding the scientific project

- `run_audit_validation.py`
- `run_extract_image_features.py`
- `train_hidden_damage_models.py`
- `src/corrosion_proxy_rul/data_cleaning.py`
- `src/corrosion_proxy_rul/image_features.py`
- `src/corrosion_proxy_rul/feature_engineering.py`
- `src/corrosion_proxy_rul/models_hidden_damage.py`
- `src/corrosion_proxy_rul/splits.py`
- `configs/specimen_mapping.yaml`
- `configs/modeling.yaml`

### Support for interpretation and presentation

- `run_eda.py`
- `run_diagnostics_visualizations.py`
- `src/corrosion_proxy_rul/eda.py`
- `src/corrosion_proxy_rul/diagnostics.py`
- `src/corrosion_proxy_rul/reporting.py`
- `run_model_improvement_analysis.py`

### Optional unless you are reproducing everything

- `run_full_baseline.py`
- `src/corrosion_proxy_rul/utils_paths.py`
- `src/corrosion_proxy_rul/visualization.py`
- `outputs/logs/*`
- `catboost_info/*`
- `__pycache__/*`

## 10. Bottom Line

You do not need to read every file line by line.

To understand the project well, focus on:

- how the master dataset is built
- how image features are extracted
- how grouped splits are enforced
- how the hidden-damage stage is benchmarked and selected
- how diagnostics explain what is meaningful and what is weak

Those five pieces explain most of the repository.

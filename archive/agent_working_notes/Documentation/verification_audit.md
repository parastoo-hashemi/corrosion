# Verification Audit
## Prior Recommendations vs. Actual Repository State

> **Scope:** Full search of source code (`main_4/src/`), entry scripts (`main_4/*.py`), config files (`main_4/configs/`), generated CSVs (`main_4/outputs/`), diagnostic markdown reports, and IEEE papers.
> **Date:** 2026-06-27
> **Method:** Keyword grep across all Python files, full reads of key modules (`ultimate_load_refocus.py`, `models_hidden_damage.py`, `models_degradation.py`, `models_rul_proxy.py`, `evaluation.py`, `splits.py`), direct reads of all referenced output CSVs.

---

## Executive Finding

**The repository is substantially more complete than the previous project review assumed.** Several analyses described as missing or recommended as future work are already fully or partially implemented — most of them concentrated in `ultimate_load_refocus.py`, a 3000+ line module that was reviewed only shallowly in the prior audit. The key gap is that these analyses exist in code and output files but are not surfaced in primary documentation or papers, making them invisible to surface-level review.

The genuinely missing items are a much shorter list than previously stated.

---

## Already Implemented

### Statistical Analysis

---

#### Campaign Confounding Analysis

**Status: Already implemented**
**Confidence: High**

A dedicated function `_build_campaign_confounding_table()` in `models_hidden_damage.py` (lines 151–171) computes per-target MAE and Spearman degradation across `group_shuffle`, `leave_one_treatment_out`, and `leave_one_campaign_out` strategies, then tabulates the delta versus the `all_cleaned` feature set baseline.

**Evidence:**
- Source: `main_4/src/corrosion_proxy_rul/models_hidden_damage.py`, function `_build_campaign_confounding_table()`
- Output CSV: `main_4/outputs/models/hidden_damage/hidden_damage_campaign_confounding.csv` — contains columns `all_cleaned_mae_mean`, `delta_mae_vs_all_cleaned`, `all_cleaned_spearman_mean`, `delta_spearman_vs_all_cleaned` per target and strategy

**Why it was missed in the prior review:** The CSV filename uses the word "confounding" but no primary markdown report or README section summarises this file as a confounding analysis. It is generated silently as part of the hidden-damage training stage and not referenced from `BENCHMARK_DIAGNOSTICS.md`.

---

#### Pooled vs. Within-Mesh Stratified Correlations (Simpson's Paradox)

**Status: Already implemented**
**Confidence: High**

The function `run_mesh_stratified_correlations()` in `ultimate_load_refocus.py` (lines 1739–1806) computes Pearson and Spearman correlations between each surface feature and `ultimate_load_kn` for three groups: pooled all specimens, 4-mesh specimens only, and 7-mesh specimens only. The docstring at line 1793 explicitly warns that pooled panels are "confounded references."

The output CSV shows the effect cleanly:

| Feature | Group | Spearman |
|---|---|---|
| `surface_total_rust_pct` | pooled | +0.462 |
| `surface_total_rust_pct` | 4-mesh | −0.046 |
| `surface_total_rust_pct` | 7-mesh | −0.401 |

This is a textbook Simpson's paradox: a pooled positive correlation that inverts to zero or negative within each homogeneous mesh group.

**Evidence:**
- Source: `main_4/src/corrosion_proxy_rul/ultimate_load_refocus.py`, function `run_mesh_stratified_correlations()`, lines 1739–1806
- Output CSV: `main_4/outputs/ultimate_load_refocus/correlations/mesh_stratified_corrosion_vs_ultimate_load.csv` — columns: `mesh_group`, `mesh_group_label` (4, 7, pooled), `pearson_r`, `spearman_rho`, `n_specimens`
- Output figure: `main_4/outputs/ultimate_load_refocus/correlations/mesh_stratified_corrosion_vs_ultimate_load.png`

**Why it was missed in the prior review:** The function and its output live inside the large `ultimate_load_refocus.py` module. The CSV exists in a subdirectory (`correlations/`) that was not listed in the prior audit. Neither the word "Simpson" nor "paradox" appears in any document or plot title — the inversion is present in the numbers but never named.

---

#### Leave-One-Campaign-Out Validation

**Status: Already implemented**
**Confidence: High**

Both the main pipeline (`splits.py`) and the ultimate-load refocus module (`ultimate_load_refocus.py`, lines 280–304, function `_build_leave_one_campaign_out_manifest()`) implement full leave-one-campaign-out grouped splitting keyed on `campaign_id`. The refocus module runs separate LOCO experiments for all-weeks and post-onset subsets.

**Evidence:**
- Source: `main_4/src/corrosion_proxy_rul/splits.py`, `LeaveOneGroupOut` on `campaign_id`
- Source: `main_4/src/corrosion_proxy_rul/ultimate_load_refocus.py`, lines 280–304
- Output manifests: `main_4/outputs/ultimate_load_refocus/splits/leave_one_campaign_out_specimen_manifest.csv`, `leave_one_campaign_out_row_manifest.csv`, `leave_one_campaign_out_balance_summary.csv`

---

#### Post-Onset Sensitivity (Threshold Filtering)

**Status: Already implemented**
**Confidence: High**

`ultimate_load_refocus.py` (lines 188–203) computes `visible_corrosion_onset_week` as the first week where `surface_total_rust_pct >= threshold_pct` (configured at 0.5% in `ultimate_load_refocus.yaml`). A boolean column `is_post_visible_corrosion_onset` is derived and a separate modeling table is built for post-onset specimens. Full grouped CV and LOCO runs are executed on this subset (lines 2791–2912).

**Evidence:**
- Source: `main_4/src/corrosion_proxy_rul/ultimate_load_refocus.py`, lines 188–203, 2791–2912
- Config: `main_4/configs/ultimate_load_refocus.yaml`, parameter `threshold_pct: 0.5`
- Output CSV: `main_4/outputs/ultimate_load_refocus/data/ultimate_load_modeling_table_post_onset.csv`

---

#### Specimen-Level Grouped Cross-Validation

**Status: Already implemented**
**Confidence: High**

`ultimate_load_refocus.py` (lines 232–277, function `_build_specimen_cv_manifest()`) builds a specimen-level stratified K-fold manifest using `group_col="specimen_id"`, ensuring no specimen appears in both train and test. Both the main pipeline (`splits.py`, `GroupShuffleSplit`) and the refocus module implement this constraint.

**Evidence:**
- Source: `main_4/src/corrosion_proxy_rul/ultimate_load_refocus.py`, lines 232–277
- Source: `main_4/src/corrosion_proxy_rul/splits.py`
- Output: `main_4/outputs/ultimate_load_refocus/splits/grouped_cv_specimen_manifest.csv`

---

### Validation

---

#### Robustness-Weighted Model Selection

**Status: Already implemented**
**Confidence: High**

`models_hidden_damage.py` (lines 87–127, function `_select_robust_configs()`) ranks models by a weighted combination of MAE ranks across strategies. Weights are configured in `modeling.yaml` and explicitly assign the highest weight (0.45) to `leave_one_campaign_out`. The output CSV records the weighted rank scores and the selection decision.

**Evidence:**
- Source: `main_4/src/corrosion_proxy_rul/models_hidden_damage.py`, lines 87–127
- Config: `main_4/configs/modeling.yaml`, `robustness_weights` section
- Output CSV: `main_4/outputs/models/hidden_damage/hidden_damage_robustness_selection.csv`

---

#### Learning Curves

**Status: Already implemented**
**Confidence: High**

`ultimate_load_refocus.py` (lines 1184–1266, function `compute_learning_curve()`) computes train and test MAE and Spearman as a function of training set fraction, producing raw and summary CSVs per experiment.

**Evidence:**
- Source: `main_4/src/corrosion_proxy_rul/ultimate_load_refocus.py`, lines 1184–1266
- Output CSVs per experiment: `learning_curve_raw.csv`, `learning_curve_summary.csv` (written to each experiment subdirectory under `outputs/ultimate_load_refocus/`)

---

#### Feature Ablation (Metadata-Only vs. Image-Only vs. Combined)

**Status: Already implemented**
**Confidence: High**

Two separate ablation systems exist. The main hidden-damage pipeline compares four feature sets (`all_cleaned`, `image_only`, `image_time_only`, `metadata_only`). The ultimate-load refocus module compares seven sets (`metadata_only`, `rgb_only`, `hsv_only`, `rgb_hsv`, `metadata_rgb`, `metadata_hsv`, `metadata_rgb_hsv`).

**Evidence:**
- Source: `main_4/src/corrosion_proxy_rul/feature_engineering.py`, `HIDDEN_DAMAGE_FEATURE_SETS`
- Source: `main_4/src/corrosion_proxy_rul/models_hidden_damage.py`, lines 284–289
- Source: `main_4/src/corrosion_proxy_rul/ultimate_load_refocus.py`, lines 31–52 and config
- Output CSVs: `main_4/outputs/models/hidden_damage/hidden_damage_feature_ablation_results.csv`
- Output CSVs: `main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/feature_set_comparison.csv`, `feature_set_delta_vs_metadata_only.csv`

---

#### Feature-Target Correlation Analysis

**Status: Already implemented**
**Confidence: High**

All-feature × all-target Spearman correlations are computed in the diagnostics stage and written to a dedicated summary CSV. Additionally, the refocus module computes within-mesh and pooled correlations specifically for `ultimate_load_kn`.

**Evidence:**
- Output CSV: `main_4/outputs/diagnostics/tables/feature_target_correlation_summary.csv` — columns: `target`, `feature_name`, `source_family`, `spearman_corr`, `spearman_abs_corr`
- Output CSV: `main_4/outputs/ultimate_load_refocus/correlations/mesh_stratified_corrosion_vs_ultimate_load.csv`

---

#### High-Collinearity Detection

**Status: Already implemented**
**Confidence: High**

Feature pairs with |Spearman| ≥ 0.98 are detected and reported. Near-constant features (top-value fraction > 0.95) are also flagged. Both are applied before modeling via `feature_engineering.py`.

**Evidence:**
- Source: `main_4/src/corrosion_proxy_rul/feature_engineering.py`
- Output CSV: `main_4/outputs/diagnostics/tables/high_collinearity_pairs.csv`
- Output CSV: `main_4/outputs/diagnostics/tables/near_constant_features.csv`

---

### Degradation Modeling

---

#### Isotonic Regression (Monotone Smoothing)

**Status: Already implemented**
**Confidence: High**

`models_degradation.py` (lines 53–74) imports `sklearn.isotonic.IsotonicRegression` and fits it as one of five degradation families. It dominates the best-family selection (21/48 specimens in the current run).

**Evidence:**
- Source: `main_4/src/corrosion_proxy_rul/models_degradation.py`, lines 53–74
- Output CSV: `main_4/outputs/models/degradation/degradation_best_fits.csv`, column `best_family` = `monotone_isotonic`

---

#### Gompertz and Logistic Degradation Curves

**Status: Already implemented**
**Confidence: High**

Both curves are defined as parametric functions in `models_degradation.py` and fit using `scipy.optimize.curve_fit` with AIC-based family selection.

**Evidence:**
- Source: `main_4/src/corrosion_proxy_rul/models_degradation.py`, lines 18 (`_logistic()`), 22 (`_gompertz()`), 43–51 (fitting), 75 (family list)
- Output CSV: `main_4/outputs/models/degradation/degradation_best_fits.csv`, `best_family` column includes values `logistic`, `gompertz`

---

#### AIC-Based Degradation Family Selection

**Status: Already implemented**
**Confidence: High**

For each specimen and target, all five families (linear, log_time, logistic, Gompertz, monotone_isotonic) are fit and ranked by AIC. The best family is recorded per specimen.

**Evidence:**
- Source: `main_4/src/corrosion_proxy_rul/models_degradation.py`, line 81 (AIC criterion)
- Output CSV: `main_4/outputs/models/degradation/degradation_best_fits.csv`, columns: `best_family`, `best_aic`

---

#### Proxy-RUL Threshold Sweep (3 Thresholds)

**Status: Already implemented**
**Confidence: High**

`models_rul_proxy.py` (lines 12–83) loops over thresholds `[0.2, 0.3, 0.4]` for `wire_area_loss_frac`, computes threshold-crossing day, and records censoring status for each specimen at each threshold.

**Evidence:**
- Source: `main_4/src/corrosion_proxy_rul/models_rul_proxy.py`, lines 12–83
- Config: `main_4/configs/thresholds.yaml`, `thresholds: [0.2, 0.3, 0.4]`
- Output CSV: `main_4/outputs/models/proxy_rul/proxy_rul_estimates.csv` — columns: `threshold_wire_area_loss_frac`, `proxy_rul_days`, `right_censored`, `threshold_status`
- Summary CSV: `main_4/outputs/models/proxy_rul/proxy_rul_summary.csv` — `n_crossed_by_baseline`, `n_future_crossings_within_horizon`, `n_right_censored`, `frac_right_censored` per threshold

---

#### Right-Censoring Handling

**Status: Already implemented**
**Confidence: High**

Each specimen's proxy-RUL calculation explicitly marks it as right-censored if the trajectory does not cross the threshold within the projection horizon (365 days from config). The logic is in `models_rul_proxy.py` (lines 24–31) and propagates to all output CSVs.

**Evidence:**
- Source: `main_4/src/corrosion_proxy_rul/models_rul_proxy.py`, lines 24–31
- Output CSV: `main_4/outputs/models/proxy_rul/proxy_rul_estimates.csv`, column `right_censored`

---

#### Approximate Prediction Uncertainty via CV Fold Variation

**Status: Already implemented**
**Confidence: High**

`ultimate_load_refocus.py` (lines 699–722, function `aggregate_prediction_rows()`) computes `predicted_ultimate_load_kn_std` as the standard deviation of out-of-fold predictions across the K folds. This provides specimen-level variation, not a formal bootstrap CI, but is an implemented uncertainty proxy.

**Evidence:**
- Source: `main_4/src/corrosion_proxy_rul/ultimate_load_refocus.py`, lines 699–722
- Output CSV: `main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/best_model_package/all_rows_oof_predictions.csv`, column `predicted_ultimate_load_kn_std`

---

#### Partial Dependence Analysis

**Status: Already implemented**
**Confidence: High**

`ultimate_load_refocus.py` computes and exports partial dependence curves for the best model, written per experiment directory.

**Evidence:**
- Source: `main_4/src/corrosion_proxy_rul/ultimate_load_refocus.py`
- Output CSV per experiment: `partial_dependence.csv`

---

#### Specimen Error Analysis and Hard-Specimen Diagnostics

**Status: Already implemented**
**Confidence: High**

`ultimate_load_refocus.py` identifies specimens with the largest prediction errors, ranks them, and produces an explicit "priority specimens" diagnostic table. This is effectively a residual analysis.

**Evidence:**
- Source: `main_4/src/corrosion_proxy_rul/ultimate_load_refocus.py`, lines 2738–2749
- Output CSVs: `best_feature_set_specimen_errors_long.csv`, `specimen_error_summary.csv`, `best_feature_set_specimen_errors_wide.csv`, `priority_specimens.csv`

---

#### Two-Stage Residual Refinement Model

**Status: Already implemented**
**Confidence: High**

A two-stage modeling approach exists in `ultimate_load_refocus.py`: a baseline metadata model is trained first, then its residuals are used to train a secondary model using additional image or mesh-stratified features. This is a form of boosted residual correction.

**Evidence:**
- Source: `main_4/src/corrosion_proxy_rul/ultimate_load_refocus.py`, lines ~2100–2400
- Output CSVs: `outputs/ultimate_load_refocus/*/baseline/terminal_oof_predictions.csv`, `residual_models/terminal_oof_predictions.csv`, `specimen_error_vs_baseline.csv`, `specimen_error_comparison_vs_baseline.csv`

---

## Partially Implemented

### Bootstrap Confidence Intervals

**Status: Partially implemented**
**Confidence: High**

Approximate uncertainty via CV fold standard deviation is implemented (`predicted_ultimate_load_kn_std` in the refocus outputs). However, this is not a bootstrap CI. It captures fold-to-fold variation in out-of-fold predictions, not the sampling uncertainty of the test-set metric. No percentile-based bootstrap resampling is present anywhere in the codebase.

**What exists:** `predicted_ultimate_load_kn_std` per specimen, error bar plots in `plot_uncertainty()` (lines 1488–1526)

**What is missing:** `scipy.stats.bootstrap` or equivalent; percentile CIs on MAE and Spearman at the fold or aggregate level

**Evidence for what exists:**
- Source: `main_4/src/corrosion_proxy_rul/ultimate_load_refocus.py`, lines 699–722, 1488–1526
- Output: `all_rows_oof_predictions.csv`, column `predicted_ultimate_load_kn_std`

---

### Proxy-RUL Uncertainty

**Status: Partially implemented**
**Confidence: High**

A censoring flag is computed for each specimen at each threshold (right-censoring analysis is complete). However, there is no uncertainty band around the degradation trajectory, no quantile-based estimate of the threshold-crossing time, and no sensitivity analysis showing how the crossing time would shift if the trajectory were shifted by ±1 standard error.

**What exists:** `right_censored` flag, `threshold_status` string, `proxy_rul_days` point estimate

**What is missing:** Confidence interval around `proxy_rul_days`, crossing-time sensitivity to trajectory uncertainty

---

### Sensitivity Analysis (Proxy-RUL Thresholds)

**Status: Partially implemented**
**Confidence: Medium**

Three thresholds are swept (0.2, 0.3, 0.4), and results are tabulated. This is a minimal sweep. The thresholds are arbitrary configuration values with no calibration to the observed structural measurements (ultimate_load_kn from bending tests), and the sweep does not extend below 0.2 or above 0.4, nor does it report sensitivity of specimen-level classification to ±0.05 perturbations. The post-onset threshold (0.5% surface_total_rust_pct) is configurable but tested only at one value.

**Evidence for what exists:**
- `main_4/src/corrosion_proxy_rul/models_rul_proxy.py`, lines 12–83
- `main_4/outputs/models/proxy_rul/proxy_rul_summary.csv`

---

## Missing

### Mixed-Effects / Hierarchical Models

**Status: Not implemented**
**Confidence: High**

No calls to `statsmodels.formula.api.mixedlm`, `sklearn`-based mixed-effect implementations, `lme4` (R), or PyMC hierarchical models anywhere in the codebase. Specimen-level grouping is handled by holdout (not by random-effects modeling), which prevents within-specimen correlation from being explicitly modeled.

**Search evidence:** `grep -r "mixedlm\|MixedLM\|mixed.effect\|hierarchical\|random.effect"` across all Python files returns zero results.

---

### Bayesian / Probabilistic Models

**Status: Not implemented**
**Confidence: High**

No PyMC, Stan, Pyro, NumPyro, BayesPy, or scikit-learn Bayesian regression usage. All models are frequentist point-estimate regressors (RandomForest, GradientBoosting, XGBoost, CatBoost).

**Search evidence:** `grep -r "pymc\|stan\|bayes\|posterior\|prior"` across all Python files returns zero results.

---

### Formal Bootstrap Confidence Intervals

**Status: Not implemented**
**Confidence: High**

CV fold standard deviation is present (see Partially Implemented), but no percentile-based bootstrap CI is computed on any reported metric. The distinction matters: fold std captures model variance under resampling of specimen groups, but does not give a valid 95% CI on the population metric.

---

### Conformal Prediction

**Status: Not implemented**
**Confidence: High**

No use of `nonconformist`, `mapie`, or manual split-conformal logic anywhere in the codebase.

---

### SHAP Values

**Status: Not implemented**
**Confidence: High**

No `shap` library import or usage in any module. Feature importance is computed using native tree-model `feature_importances_` (mean decrease in impurity), which is known to be biased toward high-cardinality features and does not provide additive feature attribution.

**Search evidence:** `grep -r "shap\|SHAP"` across all Python files returns zero results.

---

### Permutation Importance

**Status: Not implemented**
**Confidence: High**

`sklearn.inspection.permutation_importance` is not used. Only native `feature_importances_` from tree models is extracted.

---

### Power-Law and Exponential Degradation Curves

**Status: Not implemented**
**Confidence: High**

The five degradation families implemented are: `linear`, `log_time`, `logistic`, `gompertz`, `monotone_isotonic`. Power-law (`y = a * t^b`) and exponential (`y = a * exp(b * t)`) are not among them, despite being common in corrosion and fatigue literature.

**Evidence:** `models_degradation.py`, line 75 (family list); `grep -r "power.law\|exponential.*deg"` returns zero results.

---

### Calibration Analysis

**Status: Not implemented**
**Confidence: High**

No calibration plots (observed vs. predicted quantiles), reliability diagrams, or expected calibration error (ECE) calculations for any regression target. The difference between "model is accurate" and "model is calibrated" is not addressed.

---

### Explicit Simpson's Paradox Quantification

**Status: Not implemented as a formal test**
**Confidence: High**

The data demonstrating the paradox exists in `mesh_stratified_corrosion_vs_ultimate_load.csv` (pooled vs. within-mesh correlation reversal), but no function formally detects, names, or quantifies the paradox. The CSV must be read and the sign-flip observed manually. The word "Simpson" does not appear in any file in the repository.

---

### Full Threshold Sensitivity Sweep (Proxy-RUL)

**Status: Not implemented**
**Confidence: High**

Only three discrete threshold values (0.2, 0.3, 0.4) are evaluated. A continuous sweep from 0.05 to 0.60 with per-specimen classification stability analysis has not been run. Domain calibration of thresholds to observed terminal wire-area-loss values from the bending tests has not been attempted.

---

### Physics-Informed or Mechanistic Degradation Constraints

**Status: Not implemented**
**Confidence: High**

All degradation curve families are phenomenological (fitted to data without physical constraints). No electrochemical corrosion-rate model, Faraday-law penetration depth model, or diffusion-based chloride ingress model has been implemented or referenced.

---

## Recommendations Requiring No Additional Work

The following were recommended in `project_review.md` but already exist and can be used directly or reported from existing outputs.

| Recommendation | Location | Note |
|---|---|---|
| Simpson's paradox / pooled vs. within-mesh analysis | `outputs/ultimate_load_refocus/correlations/mesh_stratified_corrosion_vs_ultimate_load.csv` | Numbers are there; the finding just needs to be named and foregrounded in the paper |
| Campaign confounding analysis | `outputs/models/hidden_damage/hidden_damage_campaign_confounding.csv` | Fully computed; referenced only in BENCHMARK_DIAGNOSTICS.md |
| Feature ablation (metadata-only vs. image-only) | `outputs/models/hidden_damage/hidden_damage_feature_ablation_results.csv`, `outputs/ultimate_load_refocus/*/feature_set_comparison.csv` | Fully computed across seven feature families in the refocus module |
| Post-onset sensitivity analysis | `outputs/ultimate_load_refocus/data/ultimate_load_modeling_table_post_onset.csv` | Implemented and run; threshold configurable |
| Learning curves | `outputs/ultimate_load_refocus/*/learning_curve_raw.csv` | Implemented per experiment |
| Partial dependence analysis | `outputs/ultimate_load_refocus/*/partial_dependence.csv` | Implemented per experiment |
| Isotonic / Gompertz / logistic degradation comparison | `outputs/models/degradation/degradation_best_fits.csv` | Five families compared with AIC |
| Right-censoring analysis for proxy-RUL | `outputs/models/proxy_rul/proxy_rul_estimates.csv` | Fully implemented |
| Specimen-level error diagnostics | `outputs/ultimate_load_refocus/*/priority_specimens.csv` | Implemented as residual analysis |
| Two-stage residual refinement model | `outputs/ultimate_load_refocus/*/residual_models/` | Fully implemented as a leakage-safe two-stage pipeline |

**The primary work required is not implementation but visibility:** these results need to be surfaced in the main paper narrative, condensed into top-level summary tables, and given interpretive framing. The code already produces the evidence; what is missing is the argument built from it.

---

## Recommendations Still Worth Doing

These were recommended and are genuinely absent from the repository.

| Recommendation | Priority | Reason Still Valuable |
|---|---|---|
| **Formal bootstrap CIs on MAE and Spearman** | High | CV fold std is not a CI. Point-estimate tables without intervals will face reviewer objection. Implementation cost: 2–3 days. |
| **Mixed-effects linear baseline** (`statsmodels.mixedlm`) | High | Answers whether the ML pipeline adds anything over a 2-covariate linear model. If LME matches ML under LOCO, the paper's contribution to structural modeling is zero. Implementation cost: 2–3 days. |
| **Explicit proxy-RUL threshold sweep (0.05–0.60)** | Medium | Three thresholds is too sparse to characterize coverage sensitivity. Running a fine-grained sweep would definitively answer whether any threshold produces future residual-life predictions. Implementation cost: 1 day. |
| **SHAP values for best model** | Medium | Native tree feature importance (mean decrease impurity) is known to be biased. SHAP gives additive attribution and handles correlated features correctly. Implementation cost: 2 days. |
| **Formal naming and framing of Simpson's paradox finding** | Medium | The numbers exist but the finding is unnamed. A single paragraph in the paper naming the paradox, citing the CSV values, and explaining the implication for pooled ML models would significantly strengthen the contribution. Implementation cost: 0 days (writing only). |
| **Calibration analysis for ultimate_load_kn predictions** | Low | Accuracy and calibration are different. Even if MAE is acceptable, predictions may be systematically biased for certain mesh groups. A reliability diagram costs 1 day and is publication-standard for engineering prognostics. |
| **Threshold calibration against observed terminal wire-area-loss values** | Low | Current thresholds (0.2, 0.3, 0.4) are arbitrary. Examining the actual distribution of `wire_area_loss_frac` at termination (range, percentiles) and setting thresholds relative to observed severity would ground the proxy-RUL analysis scientifically. Cost: 0.5 days. |

---

## Why Key Findings Were Missed in the Prior Review

| Item | Reason Missed |
|---|---|
| Mesh-stratified correlation CSV (Simpson's paradox) | Located in `outputs/ultimate_load_refocus/correlations/` — a subdirectory not listed in the prior file inventory, and not referenced from any top-level markdown |
| Two-stage residual refinement | Implemented in `ultimate_load_refocus.py` (lines ~2100–2400) — the file is 3000+ lines and was only shallowly reviewed; not mentioned in README or any markdown report |
| Partial dependence outputs | Per-experiment output files in nested subdirectories; not listed in `OUTPUT_REVIEW.md` or `CODEBASE_GUIDE.md` |
| Post-onset sensitivity analysis | Config parameter `threshold_pct: 0.5` in `ultimate_load_refocus.yaml` is present but not highlighted in any top-level summary |
| Learning curves | Implemented and run but only referenced in individual experiment output subdirectories; not surfaced in `BENCHMARK_DIAGNOSTICS.md` |
| CV fold std as uncertainty proxy | Column `predicted_ultimate_load_kn_std` exists in the aggregated predictions CSV but is not mentioned in any diagnostic report |
| Feature set delta vs. metadata-only | `feature_set_delta_vs_metadata_only.csv` exists but was not in the prior list of output files inspected |

The root cause is a **documentation-to-output gap**: the `ultimate_load_refocus.py` module is a standalone, highly capable analysis pipeline that produces 40+ output files, but it is only briefly described in `CODEBASE_GUIDE.md` and is not reflected in any primary markdown report. The prior review audited documentation; this audit read the code and CSVs directly.

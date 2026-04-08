# Technical Report

This report translates the existing outputs of `main_2` and `main_3` into an evidence-based academic summary. All numbers and claims below come from saved artifacts, not from new training.

## 1. Scope and evidence base

Artifacts inspected:

- `main_2/README.md`
- `main_2/data.py`, `main_2/models.py`, `main_2/report_writer.py`, `main_2/build_pdf_report.py`
- `main_2/reports/*`
- `main_2/artifacts/run_info.json`
- `main_3/src/*`
- `main_3/outputs/*`
- `main_3/reports/*`
- `main_3/reports/figures/*`

## 2. What was implemented in `main_2`

`main_2` is the earlier Phase 2 baseline. It is a **multimodal deep regression pipeline** centered on a single continuous target:

- target: `B_Peak_Rust_Percentage_[%]` (`peak_rust_pct`)

Main implementation details verified from source:

- spreadsheet cleaning and ID parsing from `specimen-date-week`
- grouped train/validation/test splitting by specimen identity
- image encoding with pretrained **ResNet-18** embeddings (`512` dimensions)
- optional tabular context:
  - `N_Steel_Mesh`
  - `Treatment`
  - `NaCl%`
  - `Ageing_Days`
  - `Cover_(Faliure_Surface)_[mm]`
  - `week`
  - `series`
- shallow regression MLP head
- outputs:
  - predictions CSV
  - training history
  - by-treatment and by-series metrics
  - diagnostic plots
  - PDF scientific report

Observed result from `main_2/reports/model_comparison.csv`:

| Model | Test MAE | Test RMSE | Test R2 |
|---|---:|---:|---:|
| `image_only_mlp` | 5.6255 | 9.2639 | 0.5237 |
| `multimodal_mlp` | 5.7476 | 9.8652 | 0.4599 |

Important interpretation:

- The image-only model slightly outperformed the multimodal variant in this run.
- `main_2` already showed that visual information contains usable corrosion signal.
- However, the pipeline stops at **current corrosion regression**. It does not model hidden damage, degradation trajectories, or remaining life.

## 3. What improvements were implemented in `main_3`

`main_3` redesigns the project around an engineering pipeline rather than a single image-regression task.

### 3.1 Canonical data layer

From `main_3/src/data/io.py` and `canonical.py`, the pipeline:

- renames raw spreadsheet columns to a canonical schema
- parses `record_id` into:
  - `specimen_id`
  - `capture_date`
  - `week`
  - `series_family`
  - `series_label`
- infers `campaign_id`
- rescales wire-loss values to percent when raw values are fractional
- flags structural-label availability
- validates duplicates, invalid IDs, and image matching

### 3.2 Image preprocessing and feature extraction

From `main_3/src/features/image_processing.py` and `extractor.py`, the pipeline:

- crops a region of interest
- normalizes illumination
- computes a rust-likelihood map in RGB/HSV/Lab space
- thresholds that map into a rust mask
- extracts **91 image features**, including:
  - rust area percentage
  - peak segment rust percentage
  - peak rust location along the specimen
  - segment-wise rust distribution
  - connected-component geometry
  - RGB / HSV / Lab statistics
  - histogram features
  - texture features from GLCM and LBP

### 3.3 Multi-stage modeling

From `main_3/src/orchestration.py`:

- corrosion regression targets:
  - `surface_total_rust_pct`
  - `peak_rust_pct`
- corrosion classification targets:
  - `surface_total_rust_category`
  - `peak_rust_category`
- hidden-damage regression targets:
  - `wire_area_loss_pct`
  - `ultimate_load_kn`
- degradation fitting targets:
  - `surface_total_rust_pct`
  - `peak_rust_pct`
  - `estimated_wire_area_loss_pct`
  - `estimated_ultimate_load_kn`
- proxy-RUL estimation from limit-state crossing

### 3.4 Engineering interpretation layer

From `main_3/src/rul/estimator.py` and `health.py`, proxy-RUL is computed as the earliest finite crossing among:

- wire-loss threshold:
  - `20%`
  - `25%`
  - `30%`
- load threshold:
  - `0.8 x` campaign-specific reference load
- health-index threshold:
  - `health_index < 0.35`

This is explicitly a **proxy-RUL** formulation because the dataset does not contain true failure times.

## 4. Dataset analysis

### 4.1 Size and structure

From `main_3/outputs/canonical_dataset.csv` and `dataset_summary.csv`:

| Metric | Value |
|---|---:|
| Image records | 792 |
| Specimens | 48 |
| Campaigns | 2 |
| Surface-labelled rows | 792 |
| Structural-labelled rows | 48 |
| Structural label coverage | 6.06% |
| Week range | 0 to 36 |
| Unique observed week values | 25 |
| Mean images per specimen | 16.5 |
| Min / max images per specimen | 15 / 18 |

Campaign sizes:

| Campaign | Rows | Typical endpoint |
|---|---:|---:|
| `campaign_2022_mesh7_nacl0.035_age201` | 360 | week 28 |
| `campaign_2024_mesh4_nacl0.050_age260` | 432 | week 36 |

Treatment balance by image rows:

| Treatment | Rows |
|---|---:|
| `SA` | 306 |
| `NO` | 168 |
| `PA` | 123 |
| `MI` | 90 |
| `SA_PA` | 45 |
| `SA_VF` | 30 |
| `VF` | 30 |

### 4.2 Time progression structure

Key observations:

- Every specimen starts at **week 0**.
- The 2022 campaign follows a shorter schedule ending at **week 28**.
- The 2024 campaign extends to **week 36**.
- Cross-sectional weekly means are informative but not strictly monotonic because the two campaigns use different week grids and different specimen populations.
- Within-specimen progression is still positive overall:
  - mean `surface_total_rust_pct` increase from first to last observation: **+8.74 percentage points**
  - mean `peak_rust_pct` increase from first to last observation: **+24.99 percentage points**

Mean last-minus-first corrosion change by treatment:

| Treatment | Mean surface delta | Mean peak delta |
|---|---:|---:|
| `PA` | 1.20 | 4.27 |
| `SA_PA` | 5.74 | 24.32 |
| `SA` | 8.48 | 27.08 |
| `NO` | 8.71 | 25.16 |
| `VF` | 14.77 | 35.28 |
| `SA_VF` | 15.35 | 40.10 |
| `MI` | 15.68 | 34.46 |

This should be interpreted cautiously because treatment groups sit inside different campaigns and schedule patterns.

### 4.3 Corrosion labels and structural labels

Manual label summary:

| Variable | Count | Mean | Median | Min | Max |
|---|---:|---:|---:|---:|---:|
| `surface_total_rust_pct` | 792 | 2.850 | 0.347 | 0.000 | 53.412 |
| `peak_rust_pct` | 792 | 9.592 | 2.239 | 0.000 | 84.304 |
| `peak_rust_location_cm` | 792 | 9.535 | 6.500 | 0.510 | 23.480 |
| `wire_area_loss_pct` | 48 | 22.233 | 21.045 | 0.000 | 56.980 |
| `ultimate_load_kn` | 48 | 2.180 | 2.250 | 1.600 | 2.870 |

Category balance:

| Category | Surface rows | Peak rows |
|---|---:|---:|
| 1 | 493 | 304 |
| 2 | 51 | 159 |
| 3 | 38 | 72 |
| 4 | 77 | 122 |
| 5 | 133 | 135 |

Implications:

- Surface categories are heavily imbalanced toward category 1.
- Peak categories are broader but still imbalanced.
- Structural labels exist for **all 48 specimens**, but only once per specimen at late stage:
  - 24 rows at week 28
  - 24 rows at week 36

### 4.4 Missing values and integrity

Observed missingness:

- `wire_area_loss_raw`, `wire_area_loss_pct`, `ultimate_load_kn`: **744 missing rows each** by design
- all image rows, IDs, weeks, and image paths are present in the canonical dataset

Corrupted image handling:

- `main_2` recorded **1 corrupted image**: `E01-20240508-17W`
- `main_3` logged feature extraction failure on the same image and retained the row with `feature_extraction_failed = 1`
- feature columns were then median-imputed, so the sample remained in the downstream tables

Interpretation:

- The dataset is clean enough for surface corrosion modeling.
- The real bottleneck is **structural supervision sparsity**, not dataset integrity.

![Dataset Overview](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/figures/dataset_overview.png)

![Corrosion Distributions](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/figures/corrosion_distributions.png)

## 5. Image analysis results

Representative image examples were selected from the existing dataset:

- Low corrosion: `G01-20240221-6W`
- Medium corrosion: `F03-20240417-14W`
- High corrosion: `D05-20240807-30W`

Visual patterns that indicate corrosion:

- reddish-brown and dark-brown discoloration
- connected rust patches rather than isolated speckles
- widening of corroded bands along the lower specimen edge
- higher texture contrast and stronger saturation in severely corroded regions

Observed evolution across samples:

- low-corrosion samples are visually pale and sparse
- medium-corrosion samples show localized bands and edge streaks
- high-corrosion samples show broad connected patches and larger rust regions

Segmentation note:

- The rust-mask overlay is informative on medium and high examples.
- It is less reliable on very low-corrosion or acquisition-artifact-heavy images, which is consistent with the later finding that raw rust-area proxies alone are not calibrated labels.

![Representative Corrosion Examples](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/figures/corrosion_examples.png)

## 6. Extracted image features

### 6.1 Meaning of the main features

The exported feature dataset (`main_3/outputs/image_features.csv`) contains 792 rows and 92 columns including `record_id`.

Key feature groups:

- `rust_area_pct_feature`
  - fraction of the ROI above the rust-mask threshold
- `peak_rust_pct_feature`
  - highest rust fraction across 12 longitudinal segments
- `peak_rust_location_cm_feature`
  - center of the segment with highest rust fraction, mapped onto a 24 cm sample length
- `rust_distribution_*`
  - spread, range, and entropy of rust concentration across segments
- `rust_component_*`
  - number, size, and geometry of connected rust patches
- `texture_*`
  - contrast, homogeneity, energy, correlation, and LBP histograms
- `rgb_*`, `hsv_*`, `lab_*`
  - color intensity and variability

### 6.2 What the extracted features reveal

Important empirical result:

- The raw proxy percentages are **not** direct substitutes for the manual labels.

Direct feature-to-label alignment:

| Feature proxy vs label | Pearson r | MAE | Mean bias |
|---|---:|---:|---:|
| `rust_area_pct_feature` vs `surface_total_rust_pct` | 0.257 | 15.77 | +15.63 |
| `peak_rust_pct_feature` vs `peak_rust_pct` | 0.183 | 34.29 | +33.91 |
| `peak_rust_location_cm_feature` vs `peak_rust_location_cm` | 0.248 | 6.86 cm | +0.07 cm |

Interpretation:

- The raw rust mask tends to **overestimate absolute corrosion amount**.
- The useful signal is therefore not a single feature, but the combination of:
  - saturation histograms
  - blue-channel suppression
  - texture statistics
  - connected-component geometry
  - spatial segment distribution

Top univariate correlations with the manual corrosion labels:

| Target | Strongest feature cues |
|---|---|
| `surface_total_rust_pct` | `hist_s_bin_05`, `hist_s_bin_04`, `hsv_s_mean`, `texture_lbp_bin_04`, `rust_segmentation_threshold` |
| `peak_rust_pct` | `hsv_s_mean`, `hist_s_bin_05`, `hist_s_bin_07`, `hsv_s_std`, `rust_component_mean_area_pct` |
| `peak_rust_location_cm` | `peak_rust_location_cm_feature`, `rust_segment_00_pct`, `rust_distribution_entropy`, `rust_segment_10_pct`, `rust_segment_11_pct` |

This is consistent with corrosion being better captured by **color and texture pattern changes** than by a single hard-threshold area estimate.

Spatial corrosion distribution:

| Peak-location band | Rows |
|---|---:|
| 0-6 cm | 379 |
| 6-12 cm | 115 |
| 12-18 cm | 134 |
| 18-24 cm | 164 |

This suggests recurrent hotspot regions near the specimen ends, not uniform corrosion along the length.

![Feature Alignment](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/figures/feature_alignment.png)

## 7. Model performance analysis

### 7.1 Corrosion regression

Grouped-specimen holdout (`strategy = group_shuffle`) results:

| Target | Best model by MAE | MAE | RMSE | R2 |
|---|---|---:|---:|---:|
| `surface_total_rust_pct` | `random_forest` | 1.381 | 3.142 | 0.646 |
| `peak_rust_pct` | `mlp_regressor` | 4.209 | 6.234 | 0.784 |

Interpretation:

- `peak_rust_pct` is the stronger learned task in `main_3`.
- The shared target compared directly to `main_2` improved from **MAE 5.63 -> 4.21** and **R2 0.524 -> 0.784**.
- `surface_total_rust_pct` is also learnable, but with somewhat lower explained variance.

Error analysis for the best corrosion models:

| Target | Mean residual | Median abs error | 90th percentile abs error | Main failure mode |
|---|---:|---:|---:|---|
| `surface_total_rust_pct` | -0.18 | 0.41 | 3.35 | underprediction at moderate/high severity |
| `peak_rust_pct` | -0.26 | 2.46 | 11.26 | underprediction at moderate/high severity; some early-week overprediction |

Severity dependence for `peak_rust_pct` best model:

- trace rows: MAE **2.66**, positive bias **+2.10**
- low rows: MAE **2.31**, near-zero bias
- moderate rows: MAE **8.03**, bias **-2.83**
- high rows: MAE **8.03**, bias **-4.31**

This means the model is reliable for low-to-moderate screening, but it compresses extremes.

Notable outliers:

- `G02-20240724-28W`: underpredicted by **26.19**
- early `F01` samples: overpredicted by roughly **14-16**

These outliers show specimen-specific behavior that a generic feature model still misses.

### 7.2 Corrosion classification

Best grouped results:

| Target | Best model | Accuracy | Macro F1 |
|---|---|---:|---:|
| `surface_total_rust_category` | `logistic_regression` | 0.830 | 0.573 |
| `peak_rust_category` | `mlp_classifier` | 0.591 | 0.531 |

Important interpretation:

- Surface classification accuracy is high because categories 1 and 5 are easier and category 1 dominates.
- Macro F1 is much lower because middle classes remain difficult.

Per-class behavior from the saved predictions:

- `surface_total_rust_category`
  - class 1 F1: **0.932**
  - class 5 F1: **0.825**
  - class 3 F1: **0.222**
  - class 4 F1: **0.316**
- `peak_rust_category`
  - class 5 F1: **0.814**
  - class 1 F1: **0.652**
  - class 3 F1: **0.250**

This supports a practical interpretation:

- the model separates **clear low** and **clear high** corrosion
- it struggles in the ambiguous mid-severity region

### 7.3 What the models actually learned

Best-model feature evidence:

`surface_total_rust_pct` random forest top importances:

| Feature | Importance |
|---|---:|
| `rgb_b_mean` | 0.541 |
| `hist_s_bin_05` | 0.045 |
| `texture_homogeneity_std` | 0.044 |
| `hist_s_bin_06` | 0.042 |
| `rust_segment_08_pct` | 0.026 |

Interpretation:

- lower blue-channel intensity and stronger saturation distributions are consistent with rust-colored regions
- spatial segment features confirm that location matters, not only global color
- texture variability helps distinguish rough corroded regions from cleaner surfaces

### 7.4 Generalization limits

When evaluation is made stricter, performance drops sharply:

- leave-one-treatment-out corrosion regression:
  - all R2 values become negative
- leave-one-campaign-out corrosion regression:
  - still positive for most non-linear models, but worse than grouped shuffle

Interpretation:

- the model generalizes across unseen specimens reasonably well
- it is much less reliable on **unseen treatment domains**
- this is one of the central scientific limitations of the current dataset

![Corrosion Regression Parity](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/corrosion_regression_parity.png)

![Corrosion Model MAE](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/corrosion_model_mae.png)

## 8. Hidden damage estimation

### 8.1 Available supervision

The hidden-damage models train on only **48 structural rows**, with grouped evaluation typically using:

- `n_train = 38`
- `n_test = 10`

This is a very small supervision set.

### 8.2 Saved damage-model performance

Best grouped results:

| Target | Selected model | MAE | RMSE | R2 |
|---|---|---:|---:|---:|
| `wire_area_loss_pct` | `random_forest` | 3.899 | 4.995 | 0.310 |
| `ultimate_load_kn` | `random_forest` | 0.121 | 0.168 | 0.385 |

Interpretation:

- The damage models are **better than trivial guessing**, but clearly weaker than the corrosion models.
- They are usable as trend-level latent-state estimates, not as precise structural predictions.

### 8.3 Relationship between visible corrosion and hidden damage

Observed correlations on the 48 structural rows:

| Relationship | Correlation |
|---|---:|
| `surface_total_rust_pct` vs `wire_area_loss_pct` | 0.021 |
| `peak_rust_pct` vs `wire_area_loss_pct` | 0.011 |
| `surface_total_rust_pct` vs `ultimate_load_kn` | 0.261 |
| `peak_rust_pct` vs `ultimate_load_kn` | 0.387 |
| `wire_area_loss_pct` vs `ultimate_load_kn` | -0.387 |

Campaign-wise view:

- 2022 campaign:
  - visible corrosion has mild positive relation with wire loss
  - wire loss has clearer negative relation with ultimate load
- 2024 campaign:
  - visible corrosion vs wire loss is near zero
  - ultimate load is largely separated by campaign rather than by corrosion alone

Interpretation:

- Visible corrosion alone is a **weak direct proxy** for internal wire loss.
- The hidden-damage model is learning from a mixture of:
  - image texture/color cues
  - spatial corrosion descriptors
  - specimen metadata
  - campaign identity

### 8.4 What the damage models learned

Top importances for `wire_area_loss_pct` random forest:

| Feature | Importance |
|---|---:|
| `peak_rust_pct_feature` | 0.111 |
| `cover_failure_surface_mm` | 0.093 |
| `lab_a_mean` | 0.081 |
| `rust_component_count` | 0.076 |
| `peak_rust_location_cm` | 0.075 |

Top importances for `ultimate_load_kn` random forest:

| Feature | Importance |
|---|---:|
| `n_steel_mesh` | 0.172 |
| `campaign_id` (2022 indicator) | 0.128 |
| `campaign_id` (2024 indicator) | 0.105 |
| `week` | 0.101 |
| `ageing_days` | 0.095 |

Interpretation:

- Wire-loss estimation still uses image-derived corrosion patterns.
- Ultimate-load estimation leans heavily on **campaign and specimen metadata**, which means part of the apparent predictive power is experimental-context signal rather than purely visible corrosion.

### 8.5 Reliability assessment

The damage models become unstable under stricter generalization tests:

- leave-one-treatment-out: strongly negative R2 for both targets
- leave-one-campaign-out: strongly negative R2 for both targets

This is the clearest evidence that hidden-damage estimation is the current weak link of the pipeline.

![Damage Regression Parity](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/damage_regression_parity.png)

![Hidden Damage Relationships](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/figures/hidden_damage_relationships.png)

## 9. Degradation modeling

### 9.1 What was fitted

`main_3` fits degradation curves specimen by specimen for four targets:

- `surface_total_rust_pct`
- `peak_rust_pct`
- `estimated_wire_area_loss_pct`
- `estimated_ultimate_load_kn`

This produced:

- **192 curve fits** (`48 specimens x 4 targets`)
- **52,416 forecast rows**

### 9.2 Which curve families were selected

Model counts from `degradation_curves.parquet`:

| Target | Exponential | Piecewise linear |
|---|---:|---:|
| `surface_total_rust_pct` | 8 | 40 |
| `peak_rust_pct` | 4 | 44 |
| `estimated_wire_area_loss_pct` | 0 | 48 |
| `estimated_ultimate_load_kn` | 0 | 48 |

Interpretation:

- The dataset almost always favors **piecewise linear** fits.
- That is useful descriptively, but it is not a physics-based corrosion law.

### 9.3 Fit quality

Median fit statistics:

| Target | Median RMSE | Median R2 |
|---|---:|---:|
| `surface_total_rust_pct` | 0.424 | 0.903 |
| `peak_rust_pct` | 1.627 | 0.916 |
| `estimated_wire_area_loss_pct` | 1.894 | 0.636 |
| `estimated_ultimate_load_kn` | 0.035 | 0.601 |

Interpretation:

- Surface-corrosion histories are fitted well because they are directly observed repeatedly.
- Damage and capacity trajectories are less certain because they depend on model-estimated states rather than dense measured states.

### 9.4 What the degradation curves reveal

Evidence from the saved outputs:

- cross-sectional mean peak rust rises from **0.42% at week 0** to **29.26% at week 28**
- median peak rust rises from **0.42% at week 0** to **27.53% at week 28**
- later weeks show non-monotonic cross-sectional behavior because of campaign mixing and specimen heterogeneity

Interpretation:

- Corrosion progression is real and visible.
- The data support **specimen-level trend fitting** better than a single global degradation law.
- Some forecasted trajectories flatten or rise unrealistically, especially for damage and load. This is a sign that the chosen curve class is pragmatic rather than mechanistic.

![Degradation Panel](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/figures/degradation_examples_panel.png)

## 10. Proxy-RUL estimation

### 10.1 How RUL is computed

From the saved source:

1. take the latest state per specimen
2. forecast corrosion and estimated hidden damage forward in time
3. compute future health index using corrosion, wire loss, and ultimate load
4. compute threshold-crossing times
5. define:

`estimated_rul_weeks = min(rul_wire_25_weeks, rul_load_threshold_weeks, rul_health_threshold_weeks)` across finite values

### 10.2 RUL summary

From `main_3/outputs/rul_estimates.csv`:

| Metric | Value |
|---|---:|
| Specimens | 48 |
| Finite proxy-RUL values | 33 |
| No crossing inside forecast horizon | 15 |
| Zero-week proxy-RUL | 23 |
| Mean proxy-RUL | 5.42 weeks |
| Median proxy-RUL | 0.00 weeks |
| Max proxy-RUL | 55.5 weeks |

Risk classes:

| Risk class | Count |
|---|---:|
| Low | 20 |
| Moderate | 8 |
| High | 20 |
| Critical | 0 |

Governing limit states:

| Governing state | Count |
|---|---:|
| Load threshold | 16 |
| Wire-loss 25% | 10 |
| Load + wire-loss tie | 7 |
| No threshold crossing in horizon | 15 |
| Health threshold alone | 0 |

Interpretation:

- The health index contributes to risk scoring, but it does **not** become the earliest governing threshold in this run.
- Most urgent cases are driven by either predicted load degradation, predicted wire loss, or both.

### 10.3 Engineering meaning

What `estimated_rul_weeks = 0` means here:

- the specimen is already at or beyond at least one proxy threshold at the latest observed time
- it does **not** mean true immediate physical failure

Current condition summary:

| Current corrosion level | Count |
|---|---:|
| High | 17 |
| Moderate | 14 |
| Low | 6 |
| Severe | 6 |
| Trace | 5 |

Top-risk examples:

| Specimen | Current peak rust (%) | Predicted internal damage (%) | Predicted ultimate load (kN) | Health index | Proxy-RUL (weeks) | Risk |
|---|---:|---:|---:|---:|---:|---|
| `E04` | 11.737 | 39.369 | 1.726 | 0.488 | 0.0 | High |
| `F06` | 24.747 | 40.611 | 1.770 | 0.475 | 0.0 | High |
| `F02` | 32.664 | 38.152 | 1.830 | 0.465 | 0.0 | High |

Longest proxy-RUL examples:

| Specimen | Current peak rust (%) | Predicted internal damage (%) | Predicted ultimate load (kN) | Health index | Proxy-RUL (weeks) | Risk |
|---|---:|---:|---:|---:|---:|---|
| `G04` | 0.007 | 19.195 | 2.095 | 0.703 | 55.5 | Low |
| `S1MI01` | 14.561 | 20.136 | 2.358 | 0.656 | 31.5 | Low |
| `S3PA03` | 35.346 | 14.261 | 2.630 | 0.739 | 30.5 | Low |

Important interpretation:

- Proxy-RUL is already combining multiple modeled quantities.
- Some specimens with visible high corrosion still get longer proxy-RUL if the damage/load estimates remain relatively acceptable.
- That is useful for screening, but it also means RUL outcomes inherit the uncertainty of the damage models.

![Risk Distribution](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/risk_distribution.png)

![RUL Histogram](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/rul_histogram.png)

## 11. Overall conclusions

The most defensible conclusions are:

1. `main_2` demonstrated that image data alone can predict peak corrosion at a useful level.
2. `main_3` improves that corrosion modeling and makes it far more interpretable.
3. The dataset supports **surface corrosion progression modeling** convincingly.
4. The hidden-damage step is scientifically interesting but only moderately reliable because structural labels are sparse and late-stage only.
5. The RUL module should be presented as **proxy-RUL from threshold crossing**, not as direct supervised failure prediction.

For the compact comparison, see:

- [/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/main2_vs_main3.md](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/main2_vs_main3.md)

For a focused interpretation layer, see:

- [/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/results_analysis.md](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/results_analysis.md)

For limitations and follow-up recommendations, see:

- [/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/limitations_and_next_steps.md](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/limitations_and_next_steps.md)

# Data Augmentation Plan — Ferrocement Corrosion Project (`main_4`)

---

## Part 1: Diagnosis — Where Overfitting Actually Happens

The project has **two distinct overfitting problems with different causes**. They require separate strategies.

### Stage 1 — Surface corrosion (`surface_total_rust_pct`, `peak_rust_pct`)

**Status: Minimal overfitting, not the primary concern.**

| Split | MAE (total rust) | Spearman (peak rust) |
|---|---|---|
| GroupShuffleSplit | ~1.38 | 0.992 |
| LOCO | ~2.10 | 0.977 |

The degradation under campaign holdout is modest. The surface stage is working well. Adding augmentation here yields marginal benefit.

### Stage 2 — Hidden damage (`ultimate_load_kn`, `wire_area_loss_frac`)

**Status: Severe collapse under LOCO — this is the primary problem.**

| Target | GroupShuffle MAE | LOCO MAE | Ratio | LOCO Spearman |
|---|---|---|---|---|
| `ultimate_load_kn` | 0.174 kN | 0.564 kN | **3.24×** | 0.353 |
| `wire_area_loss_frac` | 0.105 | 0.124 | 1.18× | **−0.089** |

For `wire_area_loss_frac`, even in-distribution performance is weak (Spearman=0.280). Under LOCO, the model loses all ranking ability (negative Spearman). The root cause is **not sample count alone** — it is **campaign-level design confounding**: campaign, mesh count (`n_steel_mesh`), NaCl concentration, and ageing duration are co-linear. Campaign holdout is genuine extrapolation to a different design space, not just random unseen specimens.

**Critical constraint:** Augmenting the 791 surface images does **not** add any structural supervision. The 48 structural-label rows are terminal measurements, one per specimen, fixed by the physical experiment. Standard image augmentation cannot manufacture new structural labels. This is the binding constraint.

### Stage 3 — Degradation and proxy-RUL

**Status: Downstream of the structural stage failure.** If hidden damage predictions are poor under LOCO, trajectory fits and proxy-RUL estimates inherit that error. Not an independent overfitting problem.

---

## Part 2: Safe Augmentations (Label-Preserving)

These are transformations that keep the rust content, spatial distribution, and structural meaning of the image essentially intact.

### 2.1 Mild Gaussian Blur

- **What:** Apply a small Gaussian blur kernel (σ = 0.5–1.0 px, kernel 3×3) before feature extraction.
- **Why safe:** Blurring slightly smooths pixel noise without shifting color values enough to move pixels across the fixed RGB rust-mask thresholds (R∈[25,255], G∈[0,100], B∈[0,80]). Rust area ratios stay nearly identical. GLCM/LBP texture features change slightly — this is *desirable* as it tests feature stability.
- **Why useful:** Forces texture-based models (GLCM contrast, LBP) to rely on coarser structure rather than sensor noise. Reduces overfitting to fine-grained noise patterns.
- **Risk:** At σ > 1.5, rust-edge pixels near the G or B threshold can shift out of the rust mask. Keep σ ≤ 1.0.

### 2.2 Small Brightness/Contrast Variation (Grayscale only)

- **What:** Multiply grayscale channel by a factor in [0.90, 1.10] (±10%). Do **not** modify the RGB channels used for rust-mask computation.
- **Why safe:** Affects only grayscale-derived features (`img_brightness_mean`, `img_brightness_std`, percentiles, GLCM, LBP). Does not touch the RGB thresholds that define the rust mask.
- **Why useful:** The grayscale features add some signal (brightness is correlated with weathering stage). Small variation teaches the model that absolute brightness level is less important than the pattern.
- **Risk:** If applied to the RGB image before rust-mask computation, the G or B channels could drift outside the mask window. Keep it to grayscale-only paths.

### 2.3 Mild Additive Gaussian Noise (Grayscale only)

- **What:** Add N(0, σ=3–5 intensity units) noise to the grayscale array before texture/brightness feature extraction.
- **Why safe:** 3–5 units is well below the 25-unit lower threshold of the rust mask R channel and the 100-unit G upper threshold. Rust area ratios are unaffected.
- **Why useful:** Adds a small perturbation to texture features (GLCM contrast, LBP) without disturbing color-derived features. Works well together with blur.
- **Risk:** Noise + blur interact with LBP at fine scale. Test them separately first.

### 2.4 Horizontal Crop Variation (Center-Safe)

- **What:** Randomly crop ±3–5% from each side of the image (left, right) before feature extraction.
- **Why safe:** Strip features assume the image width corresponds to 24 cm physical specimen length, but crops of ±3–5% shift the cm calibration by only ±0.7–1.2 cm, which is within the strip step size (0.5 cm). Rust area ratios are affected only if cropped pixels have different rust density — for longitudinal corrosion, rust is typically distributed along the specimen, so marginal crops remove similar material.
- **Why useful:** Tests robustness to slight camera positioning variation, which is realistic given that the images were taken by different operators over 36 weeks.
- **Risk:** Aggressive crops (>10%) would invalidate strip-position features. Avoid vertical crops (would change the specimen-to-background ratio and affect mask areas). Do not combine with horizontal flip (specimen orientation matters).
- **Do NOT flip horizontally** — `img_strip_peak_location_cm` and `img_rust_center_of_mass_cm` encode left-to-right physical position.

### 2.5 Tabular SMOTE on the 48-Row Structural Table

- **What:** Apply SMOTE (Synthetic Minority Over-sampling Technique) or its regression variant (SMOTER) on the 48 terminal-stage rows in feature space, not image space. Generate synthetic specimens in the 8-feature metadata-only space or the full cleaned feature space, with interpolated `ultimate_load_kn` / `wire_area_loss_frac` targets.
- **Why safe:** The 48 rows represent real specimens with real structural measurements. SMOTE interpolates between nearby specimens — this is physically plausible because intermediate mesh counts and NaCl concentrations would produce intermediate structural outcomes.
- **Why useful:** The binding constraint is that only 38 training specimens are available in GroupShuffleSplit. SMOTE on tabular features can expand the effective training pool to 80–150 synthetic rows without inventing new images. Best models for structural targets already use `metadata_only` feature sets (8 features), so SMOTE in this 8-dimensional space is geometrically reasonable.
- **Risk:** SMOTE does not help LOCO failure — synthetic specimens will be interpolated within the training campaign's design space, not extrapolated to the holdout campaign. Set clear expectations: this is for GroupShuffleSplit/LOTO improvement, not LOCO.

---

## Part 3: Risky Augmentations (Avoid)

| Augmentation | Risk | Reason |
|---|---|---|
| **Horizontal flip** | High | Invalidates `img_strip_peak_location_cm`, `img_rust_center_of_mass_cm` — these encode physical position |
| **Rotation >5°** | High | Rotates specimen out of strip alignment; GLCM computed at horizontal angle only would misread texture |
| **RGB color jitter (hue/saturation shift)** | High | The rust mask uses fixed RGB thresholds. Shifting hue moves rust-colored pixels out of the [25–255]×[0–100]×[0–80] window, silently shrinking `img_rust_area_ratio_pct` |
| **Aggressive brightness change (>±15%)** | Medium | G channel upper threshold is 100; multiplying all channels by 1.15 can push G past 100 for rust pixels near the boundary |
| **Cutout / random erasing** | High | Removes physical corrosion from the image, reducing rust area features and misrepresenting the true corrosion level |
| **Elastic deformation / grid distortion** | High | Warps the spatial distribution of rust blobs; invalidates morphological and strip features |
| **GAN-based synthetic images** | Very High | Would require labeled synthetic images with known structural properties; not feasible at this dataset size |
| **Copy-paste corrosion patches** | High | Adds artificial rust pixels not present in the real specimen, inflating rust area ratios beyond the true label |
| **Vertical crop** | Medium | Changes specimen-to-background ratio; if background pixels are captured, they dilute the rust mask |

---

## Part 4: Leakage-Safe Implementation Strategy

The fundamental rule: **all augmented versions of a specimen's images must stay in the same split fold as the original**. Augmentation must happen *after* the specimen-level train/test split is computed, applied only to training specimens.

### Implementation approach: "augment-at-extraction" not "augment-at-storage"

The cleanest approach is to not pre-save augmented images. Instead, modify the feature extraction pipeline to apply augmentation transforms during training only:

```
Training pipeline:
  for each train specimen:
    load original image(s)
    → extract features normally              [original row]
    for n_aug in range(N_AUGMENTED_COPIES):
      apply random transform (blur / crop / brightness)
      → extract features from augmented image [augmented row, same specimen_id label]
    → append augmented rows to train feature table

Test pipeline:
  for each test specimen:
    load original image(s)
    → extract features normally (no augmentation)
```

This guarantees that no augmented test specimens appear in training and that the test evaluation is always on real, unmodified images.

### Key implementation points

- Augmented rows must carry the same `specimen_id`, `split_group`, `campaign_id`, and label values as the original row.
- The `specimen_id` grouping in `splits.py` must be applied **before** augmentation so that the split manifests remain based on the original 791 rows. Augmentation rows are added only to the training partition after splitting.
- All augmentation must use a fixed random seed per augmented copy (e.g., `seed = original_row_index * 1000 + aug_copy_idx`) for reproducibility.
- For SMOTE: generate synthetic structural rows only from train-fold specimens. Exclude SMOTE rows from any evaluation; use only as additional training signal.

---

## Part 5: Experiment Plan

### Baseline (already exists)

Current `main_4` outputs: `outputs/models/surface/best_models.csv`, `outputs/models/hidden_damage/best_models.csv`, benchmark robustness tables.

### Experiment A — Surface Stage: Image Augmentation

**Goal:** Test whether mild augmentation improves surface model generalization.

**Augmentations to test (each individually, then combined):**

| Variant | Description |
|---|---|
| A1 | Gaussian blur only (σ=0.7) |
| A2 | Grayscale brightness variation only (factor∈[0.90,1.10]) |
| A3 | Grayscale Gaussian noise only (σ=4) |
| A4 | Horizontal crop only (±4%) |
| A5 | A1+A2+A3+A4 combined (2 augmented copies per image = 3× dataset) |

**Split:** GroupShuffleSplit (5-fold) and LOCO. Report for both.

**Metrics:** MAE, RMSE, R², Spearman for `surface_total_rust_pct` and `peak_rust_pct`.

**Expected outcome:** Small improvement in GroupShuffleSplit, negligible or no improvement in LOCO (surface LOCO is already near-ceiling). If LOCO Spearman drops, the augmentation is hurting generalization.

**Pass/fail criterion:** Combined augmentation (A5) must not worsen LOCO Spearman by more than 0.02 vs baseline.

### Experiment B — Structural Stage: Tabular SMOTE

**Goal:** Test whether synthetic structural rows improve hidden-damage model performance within the same campaign.

**Approach:**

| Variant | Description |
|---|---|
| B1 | SMOTE on 48 terminal rows in `metadata_only` feature space (8 features), k=5 neighbors, generate 2× rows → 96 training rows |
| B2 | SMOTE in `all_cleaned` feature space (full feature table, 48 rows) |
| B3 | SMOTER (regression-aware SMOTE, from `imbalanced-learn`) on B1 feature space |

**Splits:** GroupShuffleSplit and LOTO. Do **not** evaluate SMOTE under LOCO (synthetic specimens cannot help campaign extrapolation — reporting LOCO improvement from SMOTE would be misleading).

**Metrics:** MAE, R², Spearman for `ultimate_load_kn` and `wire_area_loss_frac`.

**Expected outcome:** Moderate improvement in GroupShuffleSplit and LOTO for `ultimate_load_kn`. Uncertain for `wire_area_loss_frac` (already near-random).

**Pass/fail criterion:** SMOTE must not worsen LOTO Spearman for `ultimate_load_kn`. If it does, SMOTE is interpolating in a harmful direction.

### Experiment C — Test-Time Augmentation (TTA) for Uncertainty

**Goal:** Use augmentation at test time to generate uncertainty estimates on predictions, not to improve mean predictions.

**Approach:** For each test image, apply N=10 augmented copies → extract features → predict with best model → compute mean and std of predictions. Report prediction interval = mean ± 1.96×std.

**Metrics:** Coverage probability of 95% interval, sharpness (interval width), correlation of interval width with prediction error.

**Expected outcome:** Interval width should correlate with prediction error (wider intervals on harder specimens). Scientifically valuable for reporting proxy-RUL uncertainty.

### Validation Strategy (applies to all experiments)

- Always use the same pre-computed split manifests as the baseline.
- Augment only after splitting — never augment test specimens.
- Report all three split strategies (GroupShuffleSplit, LOTO, LOCO) for each experiment.
- Compare against the exact same model family and hyperparameters as the baseline — only the training data changes.
- Track training set size increase explicitly: original N vs augmented N.
- Report whether improvement is consistent across all 5 GroupShuffleSplit folds or only on some — inconsistency is a red flag.

### Expected Output Files

| File | Contents |
|---|---|
| `outputs/augmentation/surface_augmentation_results.csv` | Experiment A metrics per variant and split |
| `outputs/augmentation/smote_structural_results.csv` | Experiment B metrics per variant and split |
| `outputs/augmentation/tta_uncertainty_estimates.csv` | Experiment C uncertainty intervals per specimen |
| `outputs/augmentation/augmentation_comparison_summary.md` | Narrative before/after comparison |

---

## Part 6: Files to Edit or Create

### New files to create

| File | Purpose |
|---|---|
| `main_4/src/corrosion_proxy_rul/augmentation.py` | Augmentation functions: `apply_blur()`, `apply_grayscale_noise()`, `apply_grayscale_brightness()`, `apply_horizontal_crop()`, `build_augmented_feature_table()` |
| `main_4/src/corrosion_proxy_rul/smote_structural.py` | Tabular SMOTE logic for 48-row structural table: `smote_structural_features()`, `smoter_structural_features()` |
| `main_4/configs/augmentation.yaml` | Config: blur σ range, brightness range, noise σ, crop range, n_augmented_copies, random_seed, enabled flags per augmentation type |
| `main_4/run_augmentation_experiment.py` | Entry script: loads split manifests, applies augmentation, retrains models, writes comparison tables |

### Existing files to modify

| File | Change needed |
|---|---|
| `main_4/src/corrosion_proxy_rul/image_features.py` | Add optional `transform_fn` parameter to `extract_features_for_image()` so augmentation can be injected without changing the main extraction logic |
| `main_4/src/corrosion_proxy_rul/image_preprocessing.py` | Add `apply_augmentation(image_rgb, config)` that reads the augmentation config and returns a transformed image array (blur/noise/crop applied to grayscale path; crop applied to full array) |
| `main_4/src/corrosion_proxy_rul/config.py` | Register `augmentation` key in `load_configs()` to load `configs/augmentation.yaml` |

### Files that must NOT be changed

| File | Reason |
|---|---|
| `main_4/src/corrosion_proxy_rul/splits.py` | Split manifests must remain identical between baseline and augmentation experiments |
| `main_4/configs/modeling.yaml` | Keep model hyperparameters identical — only training data changes |
| `main_4/src/corrosion_proxy_rul/feature_engineering.py` | Exclusion logic, leakage guards, and feature family definitions must not change |

---

## Part 7: Summary of Recommendations (Priority Order)

### 1. Accept the LOCO limitation explicitly (no augmentation fix)

Campaign-level confounding is an experimental design constraint, not a solvable data problem. Document in the paper that LOCO is extrapolation, not generalization. No augmentation strategy will fix this — the two campaigns have different mesh counts and NaCl levels.

### 2. Tabular SMOTE on 48-row structural table (Experiment B) — highest implementation priority

This is the only lever that directly addresses the binding constraint (48 structural labels). Low implementation risk because it works entirely in feature space. Realistically expected to help GroupShuffleSplit and LOTO. Report honestly that it does not help LOCO.

### 3. Mild image augmentation for surface stage robustness (Experiment A, conservative)

Start with blur only (A1) and brightness variation (A2). Avoid crop initially. Validate that augmented features land within the same distribution as originals before adding to training. Useful for uncertainty estimation even if mean metrics don't improve.

### 4. Test-Time Augmentation for uncertainty (Experiment C)

Scientifically valuable regardless of whether augmentation improves mean predictions. Enables reporting confidence intervals on proxy-RUL estimates, which strengthens the paper's contribution.

### Do not pursue

Horizontal flip, rotation, hue jitter, cutout, or any augmentation that modifies the RGB content used for the rust mask threshold computation.

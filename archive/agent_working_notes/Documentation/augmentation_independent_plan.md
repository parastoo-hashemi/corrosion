# Augmentation Independent Plan
## Ferrocement Corrosion Image Dataset — Deep Learning Pipeline

> **Method:** Independent investigation of repository code, pixel statistics from actual images, label distributions, and literature. Nothing carried forward from prior plans.
> **Date:** 2026-06-27

---

## Executive Summary

The professor's request is achievable and scientifically well-posed. The core comparison is: **threshold red-color baseline vs. DL without augmentation vs. DL with augmentation**, targeting `peak_rust_pct` as the primary surface regression target.

The most important finding from this independent investigation is a **pixel-level empirical test** showing that brightness augmentation changes the threshold-derived rust percentage by 3–7× on the same image, while the DL model's label is anchored to the physical measurement and is therefore *not* corrupted by photometric augmentation. This distinction — safe for DL, harmful for the threshold pipeline — is the scientific justification for the comparison.

The second important finding is an **architectural blocking issue**: the current `main_2` pipeline pre-computes all ResNet18 embeddings in a single pass before training. Augmentation cannot be added by attaching transforms alone — the training loop must be restructured so images are processed per-batch during each epoch. This is a concrete implementation requirement, not a design preference.

The third finding is an **aspect ratio issue**: the images are 2835×650 pixels (4.36:1), and the default ResNet18 transform takes only the central ~22% of the specimen width as input. Random crop augmentation should be used to expose the model to different longitudinal sections of each specimen — this is more powerful for this specific geometry than generic random resized crops.

---

## Professor Request

From the email, four goals are stated:

1. Identify the most appropriate augmentation techniques for these images.
2. Understand how they can be implemented in Python.
3. Determine how much the dataset should reasonably be increased.
4. Implement the techniques.

The scientific context specified externally is:

- Augmentation targets the DL pipeline, not the threshold baseline.
- The comparison must include DL with and without augmentation versus the threshold baseline.
- Evaluation uses specimen-level grouped splits.
- Augmentation is applied only to training folds.
- The downstream goal includes whether augmented DL features can later support structural prediction.

---

## Repository Findings

### Image Dataset

**Source:** `Data/Images_dataset/`
**Count:** 792 PNG files; 791 usable (one corrupted: `E01-20240508-17W.png`)
**Resolution:** 2835 × 650 pixels, RGBA mode
**Alpha channel:** Constant 255 across all pixels (alpha carries no information; must convert to RGB before processing)
**Aspect ratio:** 4.36:1 — extremely wide. Specimen fills the full frame; corners are concrete-coloured (~R204, G183, B135), not white background.

**Implication for cropping:** The default ResNet18 inference transform (`weights.transforms()`) resizes the short side to 256 and center-crops to 224×224. On a 2835×650 image this creates a 256×1119 intermediate, then crops to 224×224 — capturing only the central ~20% of the specimen width. **The existing DL model sees less than one-fifth of each image.** Random crops expose the model to different longitudinal sections, which is scientifically appropriate for a specimen with spatially distributed rust.

### Label Distributions

Measured directly from `Data/Images_Dataset_A-Z-1.xlsx`:

| Target | N | Min | Max | Mean | Median | Zeros |
|---|---|---|---|---|---|---|
| `peak_rust_pct` | 792 | 0.000 | 84.304 | 9.592 | 2.239 | 8.5% |
| `surface_total_rust_pct` | 792 | 0.000 | 53.412 | 2.850 | — | — |
| `wire_area_loss_frac` | 48 | 0.000 | 0.570 | 0.222 | — | — |
| `ultimate_load_kn` | 48 | 1.600 | 2.870 | 2.180 | — | — |

`peak_rust_pct` has a right-skewed distribution (median 2.2% vs mean 9.6%) driven by specimens that develop high focal rust. The 8.5% zero fraction (no rust at early weeks) is a real phenomenon, not missing data.

### Pixel Statistics

Measured from actual images. Early-week images have mean R≈245, G≈240, B≈230 (near-white concrete). Late-week images have lower values as rust appears (D02-28W: R≈196, G≈176, B≈126).

**Critical empirical finding — brightness augmentation vs. rust threshold:**

| Image | Original rust% | ×0.8 (darker) | ×0.9 | ×1.1 | ×1.2 (brighter) |
|---|---|---|---|---|---|
| D01-20W | 0.68 | 1.37 (+101%) | 1.02 (+50%) | 0.41 (−40%) | 0.22 (−68%) |
| D02-20W | 1.49 | 4.83 (+224%) | 3.38 (+127%) | 0.59 (−60%) | 0.22 (−85%) |
| D02-28W | 5.42 | 7.53 (+39%) | 6.32 (+17%) | 4.87 (−10%) | 4.48 (−17%) |

**Interpretation:** Darkening an image by 20% can triple the threshold-detected rust percentage because dark pixels fall into the lower G and B threshold ranges, creating false positives. Brightening reduces detected rust because rust pixels exceed the G≤100 or B≤80 upper bound.

This is the empirical reason why brightness augmentation would corrupt the threshold baseline if applied there — but does **not** corrupt the DL pipeline, because the DL model's label is the physical measurement (a fixed number recorded in the workbook), not the threshold-computed value.

### Existing Deep Learning Code (`main_2`)

**Architecture:** Frozen ResNet18 (ImageNet weights, `ResNet18_Weights.IMAGENET1K_V1`) as backbone. Identity head replaces final FC layer → 512-dimensional embedding per image. `RegressionMLP` (512→256→128→64→1, BatchNorm, Dropout 0.2, SmoothL1 loss) trained on embeddings.

**Current target:** `B_Peak_Rust_Percentage_[%]` (`peak_rust_pct`). Confirmed in `main_2/config.py`, line 20.

**Tabular features used alongside embeddings:** N_Steel_Mesh, Treatment, NaCl%, Ageing_Days, Cover_[mm], week, series.

**Split logic:** `main_2/data.py` `build_group_splits()`, lines 57–81 — uses `GroupShuffleSplit` keyed on `specimen` column (not observation-level). Correct leakage prevention.

**Blocking architectural issue:** `extract_resnet18_embeddings()` (lines 137–175) runs in `backbone.eval()` with `torch.no_grad()`, processing all 791 images in a single pass before training. The resulting embeddings are stored in a numpy array. The MLP then trains on fixed pre-computed embeddings. **No augmented image can produce a new embedding from a frozen backbone unless the backbone is called again.** This means augmentation is impossible in the current architecture without restructuring the training loop.

**Transform used:** `weights.transforms()` — ImageNet standard inference preprocessing only. No augmentation.

### Existing Threshold Baseline (`main_4`)

**Location:** `main_4/src/corrosion_proxy_rul/image_features.py`, function `_threshold_mask()`

**Rust mask definition:** `main_4/configs/features.yaml`:
```
rust_lower: [25, 0, 0]
rust_upper: [255, 100, 80]
```
Any pixel with R∈[25,255] AND G∈[0,100] AND B∈[0,80] is classified as rust.

**Feature produced:** `img_rust_area_ratio_pct` — the fraction of such pixels × 100. This is the "quantification of the red color" the professor refers to.

**Relationship to label:** The workbook `surface_total_rust_pct` was computed from the original images using this or an equivalent threshold. The workbook `peak_rust_pct` is the maximum strip value from a similar threshold applied longitudinally. The DL label and the threshold label are computed from the same source images using similar logic — the DL model must learn to recover this signal from pixels without knowing the threshold.

### Existing Split Logic

`main_4/src/corrosion_proxy_rul/splits.py` produces three manifest types: `group_shuffle` (5 folds, test_size=0.2, keyed on `specimen_id`), `leave_one_treatment_out`, and `leave_one_campaign_out`. Pre-computed manifests saved as CSVs in `outputs/splits/`.

`main_2/data.py` uses an equivalent `GroupShuffleSplit` on the `specimen` column. The augmentation study should use the same split key.

---

## Literature Findings

### Augmentation techniques reported in corrosion and defect detection literature

| Study | Dataset size | Expansion | Techniques used | Notes |
|---|---|---|---|---|
| PMC11829104 (external corrosion, EfficientNetB0) | 800 images | **~6.25×** | Slight rotation, brightness, shear, zoom, channel/width/height shifts, horizontal flip, vertical flip | Used nearest-fill for rotation to avoid black corners confused with pitting corrosion |
| PMC11175235 (autonomous corrosion, steel) | 100 annotated | **20×** | Horizontal flip, vertical flip, translation, grid distortion | "Optimum number 20–40 augmentations per image"; visual changes undetectable beyond 40 |
| MDPI 2412-3811 (steel bridge, Mask RCNN + YOLOv8) | 812 images | **3×** | Augmentation mentioned, tripled dataset | Focus on segmentation, not regression |
| CMC/58635 (EfficientNetB0, industrial) | 1000 images | Unspecified | Flipping, rotating, shearing, scaling | Binary classification |

**Consistent findings across literature:**

1. Horizontal flip is universally used and considered safe for corrosion images that lack directional asymmetry.
2. Brightness and contrast variation are routinely applied and considered label-preserving for DL models.
3. Rotation up to ~15° is used, but fill mode must be chosen carefully — literature notes that black corners can be confused with pitting or void defects.
4. Expansion factors vary widely (3× to 20×) depending on original dataset size — smaller datasets use larger factors.
5. Online augmentation (per-batch, per-epoch) is preferred for datasets of this size when training from scratch or fine-tuning; offline augmentation is noted as viable for very small datasets (<500 images) where controlling exact training samples matters.

### Augmentation for regression vs. classification

The literature on augmentation for image regression (continuous label prediction) is thinner than for classification. The key principle that does apply: **label-preserving augmentations** are those where the augmented image could plausibly have been captured under different but realistic acquisition conditions, and where the physical quantity being measured (rust coverage) would have been the same. Brightness variation, small rotation, blur, and noise are standard label-preserving operations in image quality assessment and measurement tasks. Color jitter (moderate hue shifts) is less clearly label-preserving in classification tasks where colour is discriminative; for regression estimating rust coverage, it is acceptable at small ranges.

### Online vs. offline augmentation

The general position in the literature is:
- **Offline** is preferred for very small datasets (<300 training images) where controlling the exact set of training examples is important and computational resources are limited.
- **Online** is preferred for larger datasets and when using pre-trained backbones, because each epoch generates fresh variations and effective diversity grows with epochs.

At 630 training images with a frozen pretrained backbone, **online augmentation is the correct choice**. It provides effectively unlimited distinct training examples and requires no additional disk storage. The architectural restructuring it requires (per-batch backbone forward pass instead of pre-computed embeddings) is necessary regardless and is the more principled approach for transfer learning.

### Fine-tuning vs. frozen backbone in small datasets

Literature consistently recommends for datasets of ~500–1000 images: freeze the backbone initially, train only the head for ~20–50 epochs; then optionally unfreeze the final residual block(s) and fine-tune at a lower learning rate. Fine-tuning the full backbone on <1000 images without strong regularisation and augmentation risks catastrophic forgetting of useful ImageNet features. Augmentation becomes **more impactful** when the backbone is being fine-tuned, because the backbone weights need diverse inputs to avoid overfitting.

---

## Candidate Tasks

Three possible primary targets were considered:

| Target | N labeled | Task type | Threshold baseline exists? | Notes |
|---|---|---|---|---|
| `peak_rust_pct` | 792 | Regression | Yes (strip-based `img_strip_rust_max_pct`) | Already the main_2 target. Clear comparison possible. |
| `surface_total_rust_pct` | 792 | Regression | Yes (near-identical to `img_rust_area_ratio_pct`) | Near-tautology — threshold MAE ≈ 0.0002. DL cannot improve on a near-perfect baseline. |
| `ultimate_load_kn` | 48 | Regression | No direct image baseline | 48 labels insufficient for DL comparison; campaign confounding dominates. |
| `wire_area_loss_frac` | 48 | Regression | No | Same issue as ultimate_load. |

---

## Selected Task

**Primary target: `peak_rust_pct` (`B_Peak_Rust_Percentage_[%]`)**

**Repository evidence:** Already the configured target in `main_2/config.py` (line 20: `TARGET_COL = "B_Peak_Rust_Percentage_[%]"`).

**Reasoning:**
- `surface_total_rust_pct` is ruled out because it is nearly identical to `img_rust_area_ratio_pct` (threshold baseline MAE ≈ 0.0002). No DL model can improve meaningfully over a near-perfect baseline that was derived from the same images.
- `peak_rust_pct` is a spatially localised measurement — the maximum strip value across the specimen's length. A DL model processing the full image can potentially detect localised rust spots more robustly than the threshold strip analysis, especially under lighting variation.
- `peak_rust_pct` has high dynamic range (0 to 84.3%) and a skewed distribution (median 2.2%, mean 9.6%), making it a non-trivial regression target where augmentation-induced robustness could provide measurable benefit.
- Structural targets (`ultimate_load_kn`, `wire_area_loss_frac`) have only 48 labels and are dominated by campaign confounding. A DL comparison here would not produce interpretable conclusions from the augmentation study.

**Secondary downstream goal:** After the surface comparison is completed, aggregate augmented DL embeddings per specimen and test whether they improve structural target prediction in `main_4`. This is a downstream experiment, not the primary augmentation study.

---

## Candidate Implementation Paths

| Path | Description | Augmentation compatible? | Effort |
|---|---|---|---|
| **A** Current `main_2` — pre-computed embeddings | All embeddings extracted once before training; MLP trains on fixed vectors | **No** — augmented images produce the same embedding each epoch from a deterministic frozen backbone; restructuring required | n/a |
| **B** Restructured `main_2` — per-batch backbone call, frozen backbone | Training loop calls frozen ResNet18 per batch; augmented images produce different embeddings each epoch | **Yes** — correct approach for online augmentation with frozen backbone | Medium |
| **C** Restructured `main_2` — partial fine-tuning of backbone | Unfreeze last ResNet18 residual block (`layer4`), train at lower learning rate alongside head | **Yes** — augmentation is most impactful here; higher risk with 630 training images | Medium-High |
| **D** Separate new module | Build fresh DL pipeline independent of `main_2` | Yes, but duplicates infrastructure | High |

---

## Selected Implementation Path

**Path B** as the primary implementation, **Path C** as a secondary experiment for the journal paper.

**Repository evidence for Path B requirement:** `main_2/data.py`, `extract_resnet18_embeddings()` (lines 137–175) — single-pass pre-extraction makes augmentation structurally impossible without restructuring.

**Reasoning:** Path B is the minimum implementation that satisfies the professor's request without introducing the additional risk of fine-tuning instability on 630 images. Path C (partial fine-tuning) should be run as a secondary experiment because the literature shows augmentation has a larger effect on fine-tuned models, and this would strengthen the journal paper's contribution. Both experiments use the same augmentation transforms and the same split logic.

**Architecture decision for the frozen backbone (Path B):**

The change from pre-computed to per-batch embedding extraction does not alter the frozen backbone or the MLP architecture. It only changes *when* the backbone is called. In the training loop, each batch of images is augmented, passed through the frozen backbone, and the resulting embeddings are passed to the MLP. The MLP loss is backpropagated. The backbone weights do not update.

**Aspect ratio handling:** The default ResNet18 transform resizes the short side to 256 and center-crops to 224×224, capturing only the central 22% of specimen width. A better approach for this dataset is:

1. Resize height to 256, keeping aspect ratio → output 256×1119
2. RandomCrop(224×224) during training — samples random longitudinal sections
3. CenterCrop(224×224) during inference — always takes the specimen centre

This exposes the model to different spatial sections of each specimen during training, which is a powerful and domain-appropriate augmentation for the 4.36:1 aspect ratio of these images.

---

## Candidate Augmentations

Each augmentation was evaluated against three criteria: (1) does it change the label meaning? (2) is it used in corrosion/defect detection literature? (3) does it create visually implausible images for this dataset?

| Augmentation | Label safe? | Literature support | Plausible for this data? | Verdict |
|---|---|---|---|---|
| RandomCrop (longitudinal sections) | Yes | Yes (crop is universal) | **Strongly yes** — specimens are 4.36:1, cropping samples real rust patterns | **Select** |
| Horizontal flip | Yes | Universal, used in all reviewed corrosion studies | Yes — specimen has no physical left-right asymmetry affecting the label | **Select** |
| Brightness variation (±20%) | Yes for DL | PMC11829104, routine in all studies | Yes — lighting variation is real across 36 weeks | **Select** |
| Contrast variation (±20%) | Yes for DL | Routine in all studies | Yes — imaging conditions vary | **Select** |
| Gaussian blur (σ 0.5–1.5) | Yes | Routine | Yes — simulates focus variation | **Select** |
| Gaussian noise (σ 0.02–0.04) | Yes | Routine | Yes — simulates sensor noise | **Select** |
| Colour jitter — saturation (±20%) | Yes for DL | Used in PMC11829104 as "channel shifts" | Yes — saturation of concrete varies with wetness | **Select** |
| Small rotation (±5°) | Yes with reflect fill | PMC11829104 (slight rotation, nearest fill) | Yes with fill — camera tilt is plausible | **Select with condition** |
| Colour jitter — hue (±0.05) | Marginal | Less common in corrosion studies | Marginal — rust hue is characteristic; large shifts implausible | **Select at small range only** |
| Vertical flip | Borderline | Used in some corrosion studies (PMC11175235, PMC11829104) | Borderline — ferrocement slabs photographed horizontally; flipped image shows underside facing up, which is physically unusual | **Omit — low value, borderline plausibility** |
| Random erasing / Cutout | No | Not corrosion-specific | No — removes real rust from the image while keeping the label constant | **Reject** |
| Grid distortion | Borderline | PMC11175235 uses it for segmentation | Borderline — distortion is implausible for a flat-specimen photograph | **Omit for primary study** |
| Large rotation (>15°) | No | Avoided in specialist studies | No — produces background fill artefacts; specialist literature uses nearest fill to avoid confusion with corrosion pits | **Reject** |
| Hue shift >±0.1 | No | Not supported | No — moves rust pixels outside expected colour range; creates implausible images | **Reject** |
| Aggressive brightness (>±30%) | No for low-rust images | Outside typical range | No — at ×0.7 brightness, rust threshold percentage more than doubles; implausible for DL regression | **Reject at high levels** |
| Elastic deformation | No | Not used in photographic corrosion datasets | No — distorts specimen geometry | **Reject** |

---

## Selected Augmentations

Seven augmentations are selected. They are grouped into a **training transform pipeline** that applies them in sequence with independent random probabilities:

### S1 — Aspect-Ratio-Aware Random Crop

Resize the image so that height = 256 (preserving aspect ratio, giving ~1119 pixels wide). During training, apply `RandomCrop(224)` to sample a random 224×224 patch from different longitudinal positions. During inference, apply `CenterCrop(224)`.

- **Purpose:** Exposes the model to different sections of the 4.36:1 specimen in each epoch. This is the most important augmentation for this specific dataset and geometry.
- **Label safety:** `peak_rust_pct` is the maximum strip value across the full specimen. When a crop samples a low-rust region of a high-peak-rust specimen, the label is higher than the local content suggests — this teaches the model that not all crops show the peak. This is a valid challenge that improves generalisation.
- **Repository evidence:** Default transform crops to central 22% of width, losing 78% of specimen content.
- **Literature evidence:** Crop augmentation is universal in surface defect detection; this is a domain-adapted application of that principle.
- **Uncertainty:** Low — this is a clear gain for the 4.36:1 geometry.

### S2 — Random Horizontal Flip (p=0.5)

Mirrors the image left-right.

- **Purpose:** Doubles effective training diversity. The spatial location of peak rust on the specimen does not affect the `peak_rust_pct` value (it is a maximum, not a position). The flip is label-preserving.
- **Label safety:** `peak_rust_pct` = maximum strip percentage; location doesn't change the maximum value.
- **Repository evidence:** `B_Location_of_Peak_Rust_in_length_[cm]` is a separate column not used as a training target.
- **Literature evidence:** Used in all reviewed corrosion studies (PMC11829104, PMC11175235, MDPI bridge study).
- **Uncertainty:** Very low.

### S3 — Brightness and Contrast Jitter (±20%)

`torchvision.transforms.ColorJitter(brightness=0.2, contrast=0.2)`

- **Purpose:** Simulates real variation in ambient lighting, camera settings, and specimen surface wetness across 36 weeks of imaging.
- **Label safety:** The empirical pixel test confirms this changes threshold-derived rust% by up to 3×. For the DL model, the label is the fixed physical measurement — the model must learn invariance to lighting. This is the primary advantage of DL over the threshold baseline.
- **Repository evidence:** Pixel statistics show R/G/B means vary across early and late images (early R≈245, late R≈196–214), consistent with real lighting variation.
- **Literature evidence:** PMC11829104 uses brightness explicitly. Routine in all defect detection studies.
- **Uncertainty:** Low.

### S4 — Saturation Jitter (±20%)

`torchvision.transforms.ColorJitter(saturation=0.2)` — combined with S3 in the same `ColorJitter` call.

- **Purpose:** Simulates variation in camera saturation settings and concrete surface moisture content (wet concrete appears less saturated).
- **Label safety:** Saturation does not change `peak_rust_pct`.
- **Uncertainty:** Low.

### S5 — Small Hue Shift (±0.05)

`torchvision.transforms.ColorJitter(hue=0.05)` — combined in the same `ColorJitter` call.

- **Purpose:** Teaches the model that rust appearance is not defined by a fixed hue value alone — texture and spatial distribution also carry signal.
- **Label safety:** At ±0.05 hue shift, the change is subtle and rust pixels remain visually rust-coloured.
- **Risk:** If hue is shifted too far, rust pixels could exit the expected colour range. The ±0.05 limit (9° in hue circle) is conservative; literature uses 0.05–0.1 in similar contexts.
- **Literature evidence:** PMC11829104 uses "channel shifts". More conservative than common practice.
- **Uncertainty:** Medium — keep at ±0.05 and validate visually.

### S6 — Gaussian Blur (σ = 0.5–1.5, kernel=5)

`torchvision.transforms.GaussianBlur(kernel_size=5, sigma=(0.5, 1.5))`

- **Purpose:** Simulates camera defocus variation across different capture sessions. Regularises against fine-grained noise features.
- **Label safety:** Blur does not change rust coverage.
- **Literature evidence:** Routine in defect detection augmentation pipelines.
- **Uncertainty:** Low.

### S7 — Small Rotation (±5°, reflect fill, p=0.3)

`torchvision.transforms.RandomRotation(degrees=5, fill='reflect')` or using `interpolation=InterpolationMode.BILINEAR` with edge fill.

- **Purpose:** Simulates slight camera tilt variation across imaging sessions.
- **Condition:** Must use reflect (mirror) fill mode to avoid black corner artefacts. PMC11829104 explicitly notes that black corners from rotations can be confused with pitting corrosion. Reflect fill avoids this.
- **Applied at p=0.3** (not every image) to keep overall geometry stable.
- **Literature evidence:** PMC11829104 uses slight rotation with nearest fill.
- **Uncertainty:** Medium — keep degrees small (±5°), apply at low probability, validate no artefacts.

---

## Rejected Augmentations

| Augmentation | Reason for rejection |
|---|---|
| **Vertical flip** | Physically implausible for a horizontal slab photographed from above. Creates an image with the concrete's top face facing down. Adds minimal diversity at the cost of implausibility. Low benefit, some risk. |
| **Random erasing / Cutout** | Removes rust pixels from the image while the label stays at its measured maximum. When the erased patch contains the peak rust region, the visible image contradicts the label. Breaks label integrity. |
| **Large rotation (>15°)** | Produces large fill regions at image corners. Even with reflect fill, large rotations distort the specimen geometry significantly. Not seen at inference time. |
| **Hue shift >±0.1** | Pixel-level inspection confirms that rust pixels have characteristic brown-red hue. Shifting by 0.1+ moves them into orange or yellow range. At high corrosion levels this would create implausible images with rust-like colours where there is no rust. |
| **Grid/elastic distortion** | Distorts the flat specimen geometry. Not observed in real acquisition conditions. Used only in segmentation studies where mask labels deform with the image; for regression with fixed scalar labels, this creates images that do not correspond to the labelling condition. |
| **Aggressive brightness (>±30%)** | Pixel tests show that at ×0.7 (−30% brightness), threshold-detected rust approximately triples. Even though the DL label is fixed, an image that appears 3× more rusted than its label is genuinely misleading for a regression model. Keep within ±20%. |
| **Aggressive colour inversion, solarisation, posterisation** | Not realistic imaging variations. Create visually impossible images for this domain. |

---

## Dataset Expansion Strategy

### Online vs. offline

**Decision: Online augmentation.**

- **Repository evidence:** The training loop requires restructuring to support per-batch backbone calls (see Implementation Path B). Once restructured, online augmentation is the natural implementation — no pre-saved files needed.
- **Literature evidence:** Offline augmentation is recommended for datasets <300 training images (nanonets.com; viso.ai). At 630 training images, online is standard.
- **Practical advantage:** Each epoch generates a new random combination of augmentations for each image. Over 120 epochs, each training image produces 120 distinct augmented versions — effectively a very large expansion factor without disk overhead.

### Effective expansion factor

With online augmentation and 120 epochs:
- Training images: ~630
- Distinct augmented versions per image across training: ~120 (one per epoch, independent random state)
- Effective expansion: **~120×** (but with strong correlation across epochs; practically equivalent to ~5–10× of independent samples)

**Literature reference points:** PMC11829104 used 6.25× expansion (800→5000) with offline augmentation on a similar task. PMC11175235 used 20× on 100 images. For this dataset at 630 training images with online augmentation, the natural starting configuration is 120 epochs — this gives an effective diversity comparable to 5–8× offline expansion.

**Recommendation:** Do not artificially restrict epochs to simulate an expansion factor. Train for 120 epochs with early stopping (patience=18 as currently configured). The early stopping criterion governs effective exposure, not a manual expansion limit.

### Augmentation schedule

Apply all seven selected transforms in the following composition order:

```
RandomCrop-after-Resize      [always — step 1 before other transforms]
RandomHorizontalFlip p=0.5   [applied per-image]
ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05)   [p=0.8]
GaussianBlur(kernel=5, sigma=(0.5,1.5))   [p=0.3]
RandomRotation(degrees=5, fill='reflect')  [p=0.3]
ToTensor()
Normalize(ImageNet mean/std)
```

For inference (val and test): `Resize(256, keeping aspect ratio) → CenterCrop(224) → ToTensor() → Normalize()`

---

## Experimental Protocol

### Condition 1 — Threshold baseline (already implemented)

Source: `main_4`, `img_rust_area_ratio_pct` and `img_strip_rust_max_pct` features. These are computed deterministically from the same training images. For the comparison, use the `img_strip_rust_max_pct` feature as the threshold baseline for `peak_rust_pct` (the strip maximum is the threshold-based analog of the peak).

No additional work needed. Results already in `outputs/models/surface/best_models.csv`.

### Condition 2 — DL without augmentation

Source: Run restructured `main_2` with `augment=False`. The restructuring (Path B) changes the training loop to compute embeddings per batch, but with inference transforms only. This reproduces the current pipeline's intent with the corrected aspect-ratio handling.

**Why not just use the existing `main_2` output?** The existing pipeline uses a single-pass pre-extraction with the default ResNet18 transform, which captures only the central 22% of the specimen. The restructured pipeline with CenterCrop(224) is equivalent but within the new training loop. If the restructured no-augmentation run differs from the original, the difference is attributable to the improved aspect ratio handling, which is itself a contribution.

### Condition 3 — DL with augmentation

Source: Run restructured `main_2` with `augment=True`, applying all seven selected transforms to training images only.

### Metrics

For each condition, report under **all three split strategies** (GroupShuffleSplit 5-fold, Leave-One-Treatment-Out, Leave-One-Campaign-Out):

- MAE (primary, matches existing main_4 reporting)
- RMSE
- R²
- Spearman correlation

### Comparison format

A single table with rows for each condition and columns for each metric × split strategy. This matches the format already established in `outputs/models/surface/best_models.csv` and `outputs/diagnostics/tables/benchmark_best_model_robustness.csv`.

---

## Leakage Prevention

Three rules, all required:

**Rule 1 — Split before augment.** Split indices (train/val/test) must be computed from the original 791-row dataset using `specimen` as the grouping key, before any augmented image is seen by the model. The existing `main_2/data.py` `build_group_splits()` does this correctly. Do not modify the split logic.

**Rule 2 — Augment only training fold images.** The `CorrosionImageDataset` for the training fold receives the training transform pipeline (including all augmentations). The validation and test fold datasets receive only the inference transform (resize + center crop + normalise). Augmented images from training specimens must never appear in test or validation set.

**Rule 3 — Fixed labels.** Labels are loaded from the workbook, fixed per `sample_name`, and never modified by augmentation. The augmented image sees the same label as its source image. This is correct for label-preserving augmentations as selected above.

**Verification step:** After implementing, log the `sample_name` values for each fold partition and verify that the set of specimen IDs in train, val, and test are disjoint. `build_group_splits()` already provides this guarantee — confirm it is preserved after restructuring.

---

## Journal-Paper Considerations

### Minimum experiment (satisfies professor's request)

Run Conditions 1, 2, 3 above for `peak_rust_pct`. Report MAE and Spearman under GroupShuffleSplit (5-fold) and LOCO. One table, one figure (bar chart of MAE across conditions). This is the core contribution.

**Effort:** 3–4 days (1 day restructuring, 1 day augmentation pipeline, 1 day running experiments and generating table).

### Stronger experiment (journal paper)

In addition to the minimum:

1. **Ablation of individual augmentation components.** Run each augmentation type individually (crop only, flip only, brightness only, blur only) to identify which provide the most gain. This addresses "which augmentation techniques are most appropriate" with experimental evidence, not just literature reasoning.

2. **Augmentation strength comparison.** Run three strength levels (light: brightness=0.1, blur disabled; standard: as selected above; strong: brightness=0.3, hue=0.1, rotation=10°). Shows the sensitivity to augmentation aggressiveness and identifies the optimal operating point.

3. **Path C experiment (partial fine-tuning).** Unfreeze `ResNet18.layer4` (the last residual block, ~2M parameters) and fine-tune with a low learning rate (1e-4 for backbone vs 1e-3 for head). Literature supports this as more impactful than frozen backbone for small datasets with augmentation. Run with and without augmentation. This adds a clean 2×2 comparison (frozen/fine-tuned × no-aug/aug).

4. **Downstream structural experiment.** After training Condition 3, extract embeddings with inference transforms for all 48 terminal specimens. Apply PCA (fit on train-fold specimens only, retain top 10 components). Join to `main_4`'s terminal structural feature table. Run `train_hidden_damage_models.py` with a new feature set `dl_embedding_pca_metadata`. Report whether the augmented DL embedding improves `ultimate_load_kn` or `wire_area_loss_frac` under GroupShuffleSplit (not LOCO — campaign confounding dominates at LOCO level regardless of features).

5. **LOCO analysis with honest interpretation.** Report LOCO results for surface targets but explicitly note that LOCO failure for structural targets reflects campaign design confounding, not DL representation quality.

---

## Implementation Roadmap

### Files to create

| File | Purpose |
|---|---|
| `main_2/augmentation.py` | Training and inference transform definitions; `GaussianNoise` custom transform |
| `main_2/dataset.py` | `CorrosionImageDataset(Dataset)` — per-sample image loading and transform application |
| `main_2/configs/augmentation.yaml` | All augmentation hyperparameters (no hardcoded values in code) |

### Files to modify

| File | Change |
|---|---|
| `main_2/data.py` | Remove `extract_resnet18_embeddings()`. Add `build_backbone(device)` and `extract_embeddings_batch(backbone, batch, device)` for in-loop use. |
| `main_2/train_phase2.py` | Restructure training loop: instantiate separate train/val/test `CorrosionImageDataset`; call backbone per batch during training; add `--augment` / `--no-augment` flag; add LOCO evaluation. |
| `main_2/config.py` | Add path to `augmentation.yaml`; change `EXCEL_PATH` to use `-1.xlsx` (current config points to `Images_Dataset_A-Z.xlsx`, not the `-1` version). |

### Files NOT to modify

| File | Reason |
|---|---|
| `main_2/models.py` | `RegressionMLP` is unchanged — augmentation affects inputs, not the model architecture. |
| `main_4/*` | The threshold baseline and structural pipeline remain unchanged. Augmented DL embeddings are added as a new feature family, not a modification of existing code. |
| `main_4/src/corrosion_proxy_rul/splits.py` | Split manifests must remain identical for a fair comparison. |

### Execution order

```
1. Create main_2/augmentation.py and main_2/dataset.py
2. Modify main_2/data.py (remove pre-extraction, add backbone builder)
3. Modify main_2/train_phase2.py (restructure training loop)
4. Test: run --no-augment to verify restructured pipeline reproduces baseline metrics
5. Run --augment to produce augmented DL results
6. (Optional journal extension) Run ablation and strength experiments
7. (Optional downstream) Extract embeddings, run main_4 structural comparison
```

---

## Open Risks

**Risk 1 — Aspect-ratio crop may increase label noise for zero-rust images.**
At weeks 0–6, most images have near-zero rust. A random crop of a near-zero-rust image always produces a near-zero region, and the label is near-zero — no label conflict. But for a specimen at week 20–28 with localised peak rust, a crop that misses the rust spot will show near-zero pixels with a high label. The model sees a contradiction: blank concrete with a label of, say, 15% peak rust. This is technically acceptable (the model must learn that not all crops show the maximum), but may slow convergence or require more epochs for the model to learn the whole-specimen statistic from partial views.

**Mitigation:** If the crop approach causes training instability, fall back to resize-only (no crop, full specimen at lower resolution) for the no-augmentation baseline, and use only horizontal-flip + photometric augmentation without spatial crops.

**Uncertainty level:** Medium.

**Risk 2 — Per-batch backbone forward pass is slow on CPU.**
With the frozen ResNet18 called per training batch on a CPU, training time increases from minutes (pre-extracted embeddings) to potentially 2–4 hours per run. On MPS (Apple Silicon) or CUDA, ~30–60 minutes per run is realistic.

**Mitigation:** Add an embedding cache option — compute embeddings once per epoch with no augmentation (for a fast approximation), or accept the longer training time. On MPS (available on this Mac based on device detection in `train_phase2.py`), the frozen backbone forward pass is fast enough for this dataset.

**Uncertainty level:** Low for MPS hardware; medium for CPU-only.

**Risk 3 — Augmented DL may not outperform the threshold baseline.**
The threshold baseline for `peak_rust_pct` uses `img_strip_rust_max_pct` — the maximum strip percentage computed from the threshold mask across 47 longitudinal strips. This is a spatially-aware computation that knows the specimen's physical length. A ResNet18 crop of 224×224 from a 2835×650 image sees less context. The DL model may underperform the threshold baseline even with augmentation, because the threshold method explicitly uses the spatial structure that the DL model has to learn.

This is a scientifically valid outcome. The paper's contribution is the comparison and the evidence, not the demonstration that DL wins.

**Uncertainty level:** Medium — outcome uncertain, but finding is publishable either way.

**Risk 4 — Restructured pipeline introduces a bug that changes split semantics.**
The restructuring from pre-computed embeddings to per-batch processing touches the core training loop. A subtle indexing error could misalign images with labels or break the specimen-level split guarantee.

**Mitigation:** Add explicit assertions: (1) verify that `train_dataset[i].label == df.iloc[train_idx[i]][TARGET_COL]`; (2) verify no specimen appears in both train and test; (3) run the restructured `--no-augment` condition and compare metrics to the original pipeline to detect regressions.

**Uncertainty level:** Low if verified with assertions.

---

## Final Recommendation

**Do this, in this order:**

1. Restructure `main_2` to per-batch backbone processing. Verify with `--no-augment` that the restructured pipeline reproduces baseline performance (allowing for the improved aspect-ratio handling). This is the prerequisite for everything else.

2. Add the seven selected augmentations in `augmentation.py`. Apply to training fold only. Run with `--augment`. Report results for both grouped holdout and LOCO.

3. Run the ablation: individual augmentation types, then all combined. This satisfies the professor's goal to "understand which augmentation techniques are most appropriate" with experimental evidence from this specific dataset.

4. If results are strong enough for journal submission, add the partial fine-tuning experiment (Path C) and the downstream structural experiment. If augmented DL outperforms the threshold baseline under grouped holdout but not LOCO, frame the paper around the surface result and be explicit about the LOCO limitation.

**Do not:**
- Apply augmentation to the threshold pipeline — this would change the threshold-based labels.
- Use vertical flip, random erasing, grid distortion, or hue shifts larger than ±0.05 in the primary study.
- Pre-save augmented images to disk — online augmentation is correct for this dataset size and architecture.
- Treat the downstream structural experiment as the primary contribution — it is a downstream test, and campaign confounding will dominate at LOCO regardless of representation quality.

---

*Sources consulted:*
- *[A Deep Learning Approach to Industrial Corrosion Detection](https://www.techscience.com/cmc/v81n2/58635/html)*
- *[Deep neural networks for external corrosion classification in industrial above-ground storage tanks](https://pmc.ncbi.nlm.nih.gov/articles/PMC11829104/)*
- *[Autonomous Image-Based Corrosion Detection in Steel Structures Using Deep Learning](https://pmc.ncbi.nlm.nih.gov/articles/PMC11175235/)*
- *[A Systematic Review on Deep Learning with CNNs Applied to Surface Defect Detection](https://pmc.ncbi.nlm.nih.gov/articles/PMC10607335/)*
- *[Deep Learning-Based Steel Bridge Corrosion Segmentation and Condition Rating Using Mask RCNN and YOLOv8](https://www.mdpi.com/2412-3811/9/1/3)*
- *[Enhance Deep Learning with Data Augmentation Techniques](https://viso.ai/computer-vision/image-data-augmentation-for-computer-vision/)*
- *[Data Augmentation: How to Use Deep Learning with Limited Data](https://nanonets.com/blog/data-augmentation-how-to-use-deep-learning-when-you-have-limited-data-part-2/)*

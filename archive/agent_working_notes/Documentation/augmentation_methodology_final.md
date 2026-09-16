# Data Augmentation Methodology
## Four-Class Corrosion Severity Classification — Ferrocement Specimen Dataset

**Prepared by:** Parastoo Hashemi Alvar
**Supervised by:** Prof. Erica Lenticchia, Dr. Jonathan Noel, Dr. Gerardo
**Institution:** Politecnico di Torino
**Date:** 30 June 2026

---

## 1. What This Document Contains

This document records the complete augmentation methodology for the four-class corrosion severity classification study. For every numerical choice it states the origin of that number: whether it was measured directly from the 791 source images, taken from a published reference, or made as a conservative engineering judgement. Choices in the third category are labelled as such.

The augmented dataset is stored at `Data/Images_dataset_augmented/`. The provenance record is at `Data/Images_Dataset_A-Z-1_augmented.csv`. The five recipe figures are at `augmentation/figures/`. The per-image measurement table is at `augmentation/tables/image_statistics_full.csv` (791 rows, one per source image).

---

## 2. Dataset

**Table 1. Original dataset before augmentation.**

| Property | Value | Source |
|---|---|---|
| Total specimens | 48 | Dataset audit |
| Total usable images | 791 | Dataset audit; one corrupted file excluded |
| Images per specimen | 15 to 18 | Dataset audit |
| Image dimensions | 2835 × 650 pixels (predominant) | Dataset audit |
| Ageing period | 0 to 36 weeks per specimen | Excel workbook |
| Corrupted image excluded | `E01-20240508-17W.png` | Dataset audit |

**Table 2. Class distribution in the original 791 images.**

| Class | Description | Images | Percentage |
|---|---|---|---|
| 1 | No visible rust or negligible traces | 658 | 83.2% |
| 2 | Mild rust coverage | 99 | 12.5% |
| 3 | Moderate rust coverage | 20 | 2.5% |
| 4 | Severe rust coverage | 14 | 1.8% |
| **Total** | | **791** | **100%** |

The dataset is strongly imbalanced. This reflects the physical reality: each specimen spends more time in the early corrosion stages (class 1) than in the late stages (class 4). Augmentation expands all classes by the same factor and does not change this distribution. Class weighting within the model training is the appropriate mechanism for addressing the imbalance.

---

## 3. Why Augmentation Is Needed

Three facts make augmentation necessary for this study.

**The training set is small.** After specimen-level splitting, approximately 630 images are available for training. Published studies consistently show that ResNet50 requires at least 1,000 training images per class to generalise reliably; Vision Transformer requires more. Classes 3 and 4 contribute roughly 15 images each to the training partition. Without augmentation, the model cannot learn the visual variety these classes exhibit across different imaging sessions.

**Vision Transformers are more data-dependent than convolutional networks.** Convolutional networks (ResNet50) have structural assumptions that make them efficient on small datasets. Vision Transformers (ViT) do not: they must learn these spatial relationships entirely from data. On datasets of this size, ViTs trained without augmentation consistently underperform the corresponding convolutional model. The DeiT study (Touvron et al., 2021) demonstrated specifically that ViT reaches competitive accuracy with ResNet50 on moderate-scale data only when strong augmentation is applied during fine-tuning.

**The red-colour threshold classifier is sensitive to lighting.** The existing automatic classifier applies a fixed threshold: pixels with a specific range of red, green, and blue values are classified as rust. This threshold was calibrated to a particular lighting setup. When the overall image brightness changes — for example, because a specimen was photographed at a different time of day, under a different artificial light, or with different camera settings — the detected rust fraction can change substantially even though the actual rust coverage has not changed. The deep learning model, trained with brightness variation, learns to classify rust from spatial pattern and texture rather than from absolute pixel values, and is therefore more robust to this variation. Demonstrating this robustness advantage is the central argument of the planned journal paper.

---

## 4. Augmentation Pipeline Overview

Five transformation recipes were implemented. Each original image receives exactly one copy from each recipe, producing five augmented copies per source image. Together with the preserved original, every source image contributes six rows to the dataset.

**Table 3. Five augmentation recipes.**

| Recipe | What it changes | Parameter ranges | How parameters were chosen |
|---|---|---|---|
| 1 | Overall brightness and light-to-dark contrast | Brightness 0.75–1.28; contrast 0.78–1.25 | Brightness: measured from the dataset. Contrast: published literature range. |
| 2 | Colour intensity and small colour shifts | Colour intensity 0.78–1.28; per-channel shifts ±6% | Conservative heuristics, supported by within-class colour measurements. |
| 3 | Slight blur and camera noise | Blur radius 0.3–1.5 pixels; noise 0.005–0.035 | Published literature range. Effective values at training resolution are smaller — disclosed in Section 4.3. |
| 4 | Brightness, contrast, and colour intensity combined | Each parameter 0.82–1.18 | Narrower than Recipes 1–2 because three effects accumulate simultaneously. |
| 5 | Left-right mirror and brightness | Mirror (fixed); brightness 0.85–1.15 | Mirror: logically safe for a coverage-based label. Brightness: conservative sub-range of Recipe 1. |

---

## 4.1 Recipe 1 — Overall Brightness and Light-to-Dark Contrast

### What these operations do

**Brightness** multiplies every pixel value by a fixed number. A value below 1 makes the image darker, as if photographed in dimmer light. A value above 1 makes it brighter. A factor of 0.75 applied to a mid-brightness image produces a result roughly as dark as a specimen photographed in poor lighting conditions.

**Light-to-dark contrast** determines the difference between the brightest and darkest parts of an image. Reducing contrast brings all pixel values closer to a uniform mid-grey; increasing it pushes bright areas brighter and dark areas darker. Contrast changes simulate the difference between a crisp photograph taken in controlled lighting and a flat photograph taken on an overcast day.

### Evidence base for the brightness range [0.75, 1.28]

The brightness range is the only parameter in this pipeline derived entirely from direct measurement of the 791 source images. The derivation is as follows.

Overall brightness was measured for every source image using the standard photometric formula (a weighted average of the red, green, and blue pixel values that matches human perception of lightness). Results are shown in Figure 1 (luminance histogram) and Figure 2 (darkest and brightest specimens).

**Table 4. Measured overall brightness distribution across all 791 source images.**

| Statistic | Value | Image (where identified) |
|---|---|---|
| Minimum brightness | 98.1 | `D04-20240626-24W.png` |
| 5th percentile | 144.8 | — |
| Median | 197.7 | — |
| Mean | 199.1 | — |
| 95th percentile | 253.1 | — |
| Maximum brightness | 255.0 | `G01-20240110-0W.png` |
| Ratio of maximum to minimum | 2.60× | — |
| Ratio of 95th to 5th percentile | **1.75×** | — |

*Source: `augmentation/tables/image_statistics_full.csv`, column `mean_luminance_rec709_0_255`.*

The four darkest images (all of specimen D04, weeks 23–28) are photographs of heavily corroded concrete under dim conditions. The four brightest images (G-series specimens, week 0) are photographs of clean, pale concrete under good lighting. These are real images from the dataset, not outliers. A robust classifier must handle both.

The derivation of the augmentation range from these measurements:

- The 5th-percentile image is 1.37× darker than the mean (199.1 / 144.8 = 1.375). To allow augmented images to reach this darkness level, the lower brightness factor must be at most 1 / 1.375 = 0.727, rounded conservatively upward to **0.75**.
- The 95th-percentile image is 1.27× brighter than the mean (253.1 / 199.1 = 1.271). The upper factor is rounded to **1.28**.
- The range [0.75, 1.28] covers a brightness ratio of 1.28 / 0.75 = **1.71×**, closely matching the measured 5th-to-95th percentile ratio of 1.75×.

**Within-class verification.** The same measurement was performed separately for each severity class to confirm that the range is appropriate within individual classes rather than being driven purely by the difference between early (bright) and late (dark) time steps.

**Table 5. Brightness variation within each severity class.**

| Class | Images | Mean brightness | 5th percentile | 95th percentile | Within-class ratio |
|---|---|---|---|---|---|
| 1 (no rust) | 658 | 206.0 | 159.3 | 253.9 | 1.59× |
| 2 (mild rust) | 99 | 174.0 | 138.9 | 215.2 | 1.55× |
| 3 (moderate rust) | 20 | 149.8 | 129.0 | 172.1 | 1.33× |
| 4 (severe rust) | 14 | 120.2 | 99.8 | 145.0 | 1.45× |

*Source: computed from `augmentation/tables/image_statistics_full.csv`.*

The within-class brightness ratios range from 1.33× to 1.59×. The augmentation range covers 1.71×, which is slightly wider than any single class. This confirms the range is calibrated to real imaging variability rather than to the label-driven shift in brightness between early and late specimens.

A brightness factor of 0.75 applied to the class-1 mean brightness (206.0) produces an image at brightness 154.5 — darker than the typical class-4 image (mean 120.2) but within the class-4 minimum of 98.1. This is intentional: the model learns that overall brightness does not determine rust severity, only the rust pattern does.

**See:** Figure 1 (`augmentation/figures/luminance_histogram.png`) and Figure 2 (`augmentation/figures/luminance_extremes.png`) for the measured distribution and the visual appearance of the extreme cases.

### Justification for the contrast range [0.78, 1.25]

The contrast range is drawn from published literature. Industrial inspection and corrosion classification studies consistently apply contrast variation in the range ±15–25% from the neutral value. The chosen range [0.78, 1.25] represents approximately ±22%. No direct measurement was made to derive this specific interval from the dataset, because image contrast is dominated by content (rust-covered surfaces have more local variation than clean concrete) rather than by imaging conditions. A direct measurement would therefore confound physical content with camera effects.

**See:** Figure 3 (`augmentation/figures/recipe1_brightness_contrast.png`) for visual examples.

---

## 4.2 Recipe 2 — Colour Intensity and Small Colour Shifts

### What these operations do

**Colour intensity** (sometimes called saturation) describes how vivid or rich the colours in an image are. At full intensity, colours appear strong and distinct — rust looks strongly orange-red, concrete looks clearly grey or beige. At reduced intensity, colours become muted: rust looks brownish-grey, concrete looks almost white. Reducing colour intensity to zero produces a greyscale image with no colour information at all.

**Small colour shifts** adjust the relative strength of the red, green, and blue channels independently. A small increase in the red channel makes the image appear warmer (slightly more reddish); a small increase in the blue channel makes it appear cooler. These shifts simulate the variation in camera colour response between different imaging sessions, which depends on the colour temperature of the light source and the camera's automatic colour correction.

In this recipe, the three channel shifts are applied symmetrically around neutral: their average is always exactly 1.0, so they produce a colour tilt without changing the overall brightness. Brightness is handled separately by Recipe 1.

### Evidence base for the colour intensity range [0.78, 1.28]

No direct measurement of colour intensity variation is cited for this parameter, because colour intensity in these images is strongly correlated with the class label: heavily rusted specimens (class 4) have visibly more vivid rust colour than clean specimens (class 1). Calibrating the augmentation to the full dataset's colour intensity range would therefore calibrate it to the physical progression of corrosion — which is the label itself, not an imaging artefact.

The chosen range [0.78, 1.28] represents ±25% from the neutral value. This is consistent with published literature for industrial surface inspection (where ±20–30% is the standard range) and produces visually plausible results for both clean and corroded specimens, as visible in Figure 4. The range is treated as a conservative engineering choice supported by literature, not as a measured dataset statistic.

### Evidence base for the colour shift range [±6% per channel]

The three colour channel shifts are sampled independently in the range [0.94, 1.06], meaning each channel can change by at most 6% before the normalisation step.

To provide a measured basis for this choice, the ratio of the red channel mean to the green channel mean (R/G ratio) was computed for every source image. This ratio is a standard measure of colour tilt: an R/G ratio above 1.0 means the image is warmer (more red), and a lower ratio means it is cooler (more green-blue). Under controlled lighting, this ratio should remain constant; variation between sessions indicates real colour-response differences.

**Table 6. Within-class variation in the red-to-green channel ratio.**

| Class | 5th percentile R/G | 95th percentile R/G | Within-class range | Std deviation |
|---|---|---|---|---|
| 1 (no rust) | 1.000 | 1.107 | 10.6% | 0.031 |
| 2 (mild rust) | 1.080 | 1.215 | 13.5% | 0.044 |
| 3 (moderate rust) | 1.200 | 1.308 | 10.8% | 0.042 |
| 4 (severe rust) | 1.271 | 1.442 | 17.1% | 0.063 |

*Source: computed from `augmentation/tables/image_statistics_full.csv`.*

The within-class R/G range for class-1 images (clean concrete only) is 10.6%. This is the most direct estimate available of colour-balance variation due to imaging conditions, because class-1 specimens have minimal rust and the colour variation within this class is primarily caused by the camera and lighting rather than by rust colour. The chosen ±6% per-channel range covers about 57% of this within-class variation and is therefore conservative rather than aggressive.

The blue-to-green ratio (B/G) shows larger within-class variation (up to 34% for class-1 images), indicating that the blue channel is more sensitive to lighting conditions. This additional variation is partially addressed by the colour intensity component of this recipe, which shifts all colour channels together.

**See:** Figure 4 (`augmentation/figures/recipe2_saturation_colour_balance.png`) for visual examples.

---

## 4.3 Recipe 3 — Slight Blur and Camera Noise

### What these operations do

**Slight blur** reduces the sharpness of the image, as if the camera was slightly out of focus or the specimen moved slightly during the exposure. It works by averaging each pixel with its immediate neighbours, with closer neighbours weighted more heavily. The blur radius (sigma) controls how many pixels are averaged together; a larger radius produces stronger blur.

**Camera noise** adds small random variations to individual pixel values, simulating the electronic noise that all digital camera sensors produce. This noise is especially visible in images taken under low light, at high camera sensitivity settings, or with long exposure times. Adding controlled noise during training teaches the model not to rely on exact pixel values and to focus on larger patterns instead.

### Parameter ranges and their evidence basis

Both ranges in this recipe are drawn from published literature:

| Parameter | Range used | Literature norm | Source |
|---|---|---|---|
| Blur radius | 0.3–1.5 pixels | 0.1–2.0 pixels | Industrial inspection studies |
| Noise level | 0.005–0.035 (normalised 0–1 scale) | 0.01–0.05 | Surface defect classification studies |

The noise level of 0.035 in normalised space corresponds to a pixel-level standard deviation of 0.035 × 255 = **8.9 intensity units** on the standard 0–255 scale. This is comparable to the pixel noise observed in digital photographs taken at moderate to high camera sensitivity settings.

### Important disclosure: effective values at the training resolution

The blur and noise are applied to the source images at their full size of 2835 × 650 pixels. During model training, these images are resized to a smaller size for processing by ResNet50 and ViT (standard training crops to approximately 224 × 224 pixels). This resizing step reduces the effective blur and noise that the model actually receives.

The resize scale factor from source to training resolution is approximately 256 / 650 = 0.394. The effective parameter values at training resolution are:

**Table 7. Effective parameter values at training resolution (224 × 224 px) after downsampling.**

| Parameter | Applied at source | Effective at training | Perceptible at training? |
|---|---|---|---|
| Blur radius minimum | 0.3 pixels | 0.12 pixels | No — sub-pixel |
| Blur radius maximum | 1.5 pixels | 0.59 pixels | Marginally |
| Noise level minimum | 0.005 | ~0.003 | Minimal |
| Noise level maximum | 0.035 | ~0.022 (≈5.6 intensity units) | Moderate |

The blur effect is largely removed by downsampling. At the training resolution, even the maximum radius of 0.59 pixels introduces only marginal blurring. This does not invalidate the recipe: adding sub-pixel or very mild blur still teaches the model that fine pixel-level detail is unreliable as a classification cue. However, the physical argument that "blur simulates camera focus variation" applies accurately to the source-resolution images and must be understood as substantially attenuated in the images actually processed by the model. The noise, by contrast, retains about half its source-resolution level (approximately 5.6 intensity units at training resolution) and provides meaningful regularisation.

For a future implementation that maximises the blur and noise effect, these operations should be applied after the image has been resized to the training resolution (224 × 224 pixels), not at source resolution. This is a training-pipeline decision and does not affect the offline dataset as produced.

**See:** Figure 5 (`augmentation/figures/recipe3_blur_noise.png`) for visual examples. The examples confirm that even at the maximum values, the augmented images remain visually similar to the originals and all rust patterns are clearly preserved.

---

## 4.4 Recipe 4 — Combined Brightness, Contrast, and Colour Intensity

### What this recipe does

This recipe applies three separate changes to the same image: overall brightness, light-to-dark contrast, and colour intensity are each modified independently. The purpose is to simulate a photograph taken under conditions that differ from the reference in multiple respects simultaneously — for example, dimmer light, flatter contrast, and slightly desaturated colours all at once.

### Why the parameter range is narrower than in Recipes 1 and 2

When three adjustments are applied to the same image, their effects can add together. If brightness is reduced by 20%, contrast is reduced by 20%, and colour intensity is also reduced by 20%, the combined result is significantly different from any of these changes alone. At the extreme values of each parameter, the three effects would accumulate substantially.

To keep augmented images within realistic appearance limits even when all three adjustments coincide at their extremes, the individual range was reduced from [0.75, 1.28] to [0.82, 1.18] — approximately ±18% per adjustment. In the worst case of all three at 0.82 simultaneously, the combined effect reduces visual intensity by approximately 1 − 0.82³ = 45%. In practice, three independent random values all landing near their extreme is unlikely, and the typical combined effect is much smaller.

The range [0.82, 1.18] is a conservative engineering choice. No separate measurement was made to determine this specific boundary. The mathematical argument for narrowing relative to single-parameter recipes is sound; the precise value 0.82 is a judgement.

---

## 4.5 Recipe 5 — Left-Right Mirror and Brightness

### What this recipe does

The image is reflected left-to-right (a horizontal mirror), and a mild brightness adjustment is applied to ensure the copy is not a purely deterministic duplicate of the original.

### Why the mirror is safe for this classification label

The classification target, `A_Total_Rust_Category_(1–4)`, measures the total fraction of the specimen surface covered by rust. This is a scalar quantity — it answers the question "how much rust is present?" not "where on the specimen is the rust?" The total coverage does not change when the image is mirrored: a specimen showing 20% total rust coverage is still class 2 whether the rust patch appears on the left or the right.

This argument applies specifically to this label. It would not apply to the peak rust location column (`B_Location_of_Peak_Rust_in_length_[cm]`), which records a position. That column is preserved unchanged in the augmented CSV and must not be used as a spatial feature for mirrored copies.

### Why vertical mirror and large rotations were excluded

A vertical mirror would show the specimen photographed upside-down. The 48 specimens in this dataset were always photographed in the same fixed orientation; an upside-down image is not a physically possible acquisition condition for this setup.

Large rotations (more than approximately 10°) introduce empty corner regions that must be filled with an artificial value. Even with the best fill strategy (reflecting the edge pixels), these regions do not represent real specimen content and can be learned as spurious features. Rotations beyond 10° also do not correspond to plausible camera placement variability for a fixed imaging setup.

### Brightness range [0.85, 1.15]

The brightness component of this recipe uses a range of [0.85, 1.15]. This is narrower than the [0.75, 1.28] range of Recipe 1, for two reasons: the mirror already provides strong spatial diversity, so the brightness component is secondary; and a narrower range avoids creating copies that are both mirrored and extremely dark, which might degrade visual quality. The specific value 0.85 is a conservative engineering choice with no separate measurement basis.

**See:** Figure 6 (`augmentation/figures/recipe5_flip_brightness.png`) for visual examples.

---

## 5. Rejected Augmentation Techniques

**Table 8. Techniques considered and excluded.**

| Technique | Reason for exclusion |
|---|---|
| **MixUp** | Blends two images together and adjusts the class label proportionally. The result — for example, "60% class 2 and 40% class 3" — is not a physically meaningful rust severity. The four-class labels used in this study are discrete; they cannot be meaningfully interpolated. |
| **CutMix** | Pastes a rectangular patch from one image into another and adjusts the label proportionally to the pasted area. A patch of clean concrete pasted into a severe-rust image creates a contradictory training example: the label suggests moderate severity, but a region of the image shows no rust at all. For specimens in class 2 and class 3, where total rust coverage is already limited, this creates the largest risk of label corruption. |
| **Synthetic image generation (GAN, diffusion)** | Generating new corrosion images using a generative model would require training a separate model on fewer than 20 images per class for classes 3 and 4. Models trained on this few examples per class produce unstable or repetitive outputs. This technique is not among the professor's specified families and is outside the scope of this study. |
| **Elastic deformation** | Warps the image as if the surface were made of elastic material. This technique was developed for medical imaging (deformable tissue in histology slides and MRI scans). A flat ferrocement slab photographed perpendicular to its surface does not deform in this way; applying elastic deformation produces physically implausible specimen images. |
| **Random region removal (Cutout)** | Replaces a random rectangular region of the image with black or zero pixels. If the removed region contains the primary rust patch, the model receives an image labelled "moderate rust" that visually shows mostly clean concrete. For class 3 (20 images, limited rust coverage), this risk is highest. |
| **Heavy colour shift (>±10%)** | Shifting the hue of the image by more than approximately 10–18° on the colour circle can move rust pixels from their orange-red range into yellow, green, or magenta — colours that do not occur in corroded ferrocement. |
| **Vertical mirror** | Produces an upside-down photograph of the specimen. Not a plausible acquisition condition for this imaging setup. |
| **Large rotation (>±10°)** | Creates corner fill regions that are not representative of real specimen content. Imaging setup is fixed. |

---

## 6. Dataset Expansion Factor

### Resulting dataset

**Table 9. Dataset size before and after augmentation.**

| Class | Original images | Augmented copies | Total | Factor |
|---|---|---|---|---|
| 1 | 658 | 3,290 | 3,948 | 6× |
| 2 | 99 | 495 | 594 | 6× |
| 3 | 20 | 100 | 120 | 6× |
| 4 | 14 | 70 | 84 | 6× |
| **Total** | **791** | **3,955** | **4,746** | **6×** |

### Literature basis for the 6× factor

The expansion factor of 6× (one original plus five augmented copies) was chosen to match the range supported by published corrosion studies of comparable dataset size.

**Table 10. Expansion factors in comparable published studies.**

| Study | Architecture | Dataset size (pre-aug.) | Expansion | Result |
|---|---|---|---|---|
| PMC11829104 — tank corrosion | EfficientNetB0 | ~800 images | **6.25×** | 94% accuracy |
| PMC11175235 — steel corrosion | CNN | 100 images | 20× | — |
| arXiv 1906.11887 — general survey | Various | Various | **2–3× optimal** | diminishing returns above 3× |
| Steel defect detection studies | ResNet50, InceptionV3 | 800–2,400 | 3× | >90% accuracy |

The most directly comparable study (PMC11829104, approximately 800 images, corrosion classification, offline augmentation) used 6.25×. The general survey (arXiv 1906.11887) identifies 2–3× as optimal for larger datasets but acknowledges that corrosion-specific studies routinely use 3–6× on smaller collections. The chosen 6× sits at the upper boundary of this range.

### Why 6× was chosen over a higher factor

Using each of the five recipes exactly once per source image gives 6× and makes the composition of the training set transparent: every unique augmentation that the pipeline can produce appears exactly once. Generating more copies would require repeating recipes with different random parameters, introducing diminishing diversity per additional copy. No published corrosion study of comparable size justifies an expansion beyond 6–10×, and the general survey reports minimal accuracy improvement above 3×. Six copies from five distinct recipe families is the natural stopping point.

---

## 7. Reproducibility

### How the same augmented images are generated every time

Every augmented image is produced using a random number that depends on three inputs: the global seed, the source image filename, and the copy number. These three inputs are combined using a standard cryptographic hash function (SHA-256), and the result is used to initialise the random number generator independently for each image-copy pair. Changing any one of the three inputs produces a completely different sequence of random numbers.

This means the output of the script is fully deterministic. Running the script again with the same global seed produces byte-identical images. Running it on a different computer or with different numbers of parallel processes produces the same result. The order in which images happen to be processed does not affect the outcome.

### Global seed

The global seed used for all augmentation is **20260630**. This value was chosen to match the date of the dataset generation run and has no mathematical significance beyond uniqueness.

### Reproduction command

```bash
python augmentation/augment_dataset.py --copies 5 --seed 20260630 --overwrite
```

### Provenance fields in the CSV

Every row in `Data/Images_Dataset_A-Z-1_augmented.csv` contains:
- `original_image_name`: the source file this row was derived from
- `augmentation_type`: the recipe name applied
- `augmentation_parameters`: the exact numerical values used (for example, `brightness=0.874061;horizontal_flip=true`)
- `is_augmented`: whether this row is an original or an augmented copy
- `specimen_id`: the specimen identifier, required for leakage-safe train/test splitting

---

## 8. Splitting: Augmented Images Belong to the Training Partition Only

Augmented images must not appear in the validation or test sets. The rule is simple: the validation and test sets measure how well the model performs on images that look like real photographs. Augmented images do not look exactly like real photographs — they are intentionally altered. Including them in evaluation would measure performance on artificially varied images rather than on the real-world distribution.

More importantly, no augmented copy of a validation or test specimen may appear in the training set. Because augmented copies retain the visual identity of their source specimen (same rust pattern, same spatial layout, just with adjusted brightness or colour), placing a copy in training while the original is in the test set constitutes a data leak: the model has seen the specimen before, in a slightly different form.

The split manifests produced by `augmentation/make_splits.py` implement these rules:
- Training rows: all rows (original + augmented) for the 38 training specimens.
- Validation rows: original rows only for 5 validation specimens.
- Test rows: original rows only for 5 test specimens.
- The 750 augmented copies of validation and test specimens are excluded from all splits.

---

## 9. Evidence Status Summary

**Table 11. Evidence basis for every parameter choice.**

| Parameter | Value | Evidence basis | Confidence |
|---|---|---|---|
| Brightness lower bound | 0.75 | Measured: 1 / (mean/p5) = 1/1.375 = 0.727 → 0.75 | High |
| Brightness upper bound | 1.28 | Measured: p95/mean = 1.271 → 1.28 | High |
| Contrast lower bound | 0.78 | Literature: industrial inspection ±15–25% | Medium |
| Contrast upper bound | 1.25 | Literature: industrial inspection ±15–25% | Medium |
| Colour intensity lower | 0.78 | Conservative heuristic; literature ±20–30% | Medium |
| Colour intensity upper | 1.28 | Conservative heuristic; literature ±20–30% | Medium |
| Colour shift per channel | ±6% (0.94–1.06) | Measured: within-class R/G std ≈ 3%, range ≈ 11%; chosen range covers this conservatively | Medium–high |
| Blur radius at source | 0.3–1.5 pixels | Literature: industrial inspection 0.1–2.0 | Medium |
| *Blur at training resolution* | *0.12–0.59 pixels* | *Derived from resize scale 0.394* | *High (disclosure)* |
| Noise level at source | 0.005–0.035 | Literature: surface inspection 0.01–0.05 | Medium |
| *Noise at training resolution* | *~0.003–0.022* | *Derived from resize scale* | *High (disclosure)* |
| Combined recipe range | 0.82–1.18 | Engineering heuristic: 0.82³ = 0.551, keeps compound accumulation within ≈50% | Medium |
| Mirror flip | Fixed (no range) | Logical: total coverage is position-invariant | High |
| Flip brightness | 0.85–1.15 | Conservative sub-range of Recipe 1; heuristic | Low–medium |
| Expansion factor | 6× | Literature: PMC11829104 (6.25×); survey (2–3× optimal for larger sets) | High |

---

## 10. Limitations

**Contrast and colour intensity ranges are not measured from the dataset.** The parameter ranges for light-to-dark contrast (0.78–1.25) and colour intensity (0.78–1.28) are drawn from published literature and set conservatively. A more rigorous calibration would measure the within-class variation in these properties and derive the range from that measurement, as was done for brightness. This analysis requires separating variation due to imaging conditions from variation due to physical specimen state (which correlates with the class label), and was not performed.

**Blur is largely removed by downsampling.** The blur applied at source resolution (2835 × 650 pixels) is reduced to 0.12–0.59 effective pixels at training resolution (224 × 224 pixels) by the resize operation during model training. The blurring contribution to model regularisation is smaller than the stated source-resolution values suggest. Noise is similarly attenuated (to approximately 5.6 intensity units maximum at training resolution). Both effects are real and contribute to regularisation, but quantitatively less than the stated source-resolution values.

**The class imbalance is preserved.** Augmentation multiplies all classes by the same factor (6×). Class 1 remains 83.2% of the dataset. The model training must use class-weighted loss or an equivalent technique to address this imbalance.

**The augmented dataset is fixed.** Generating images offline means that only five specific random realisations of each recipe appear per source image. During model training, no new random variations are created per epoch. Online augmentation (applying transformations dynamically at training time) would produce greater variety at the cost of less convenient inspection and archiving. The offline approach was chosen for transparency and reproducibility.

---

## 11. Figures and Data Files

| File | Content |
|---|---|
| `augmentation/figures/luminance_histogram.png` | Distribution of overall image brightness across all 791 images, with 5th percentile (144.8), median (197.7), and 95th percentile (253.1) marked. Shows the 1.75× spread that motivates the brightness range. |
| `augmentation/figures/luminance_extremes.png` | Side-by-side comparison of the four darkest images (specimen D04, all class 4, brightness 98–113) and four brightest images (G-series, all class 1, brightness 255). Shows the full 2.60× real-world variation. |
| `augmentation/figures/recipe1_brightness_contrast.png` | One original image per class and its brightness-contrast augmented copy. |
| `augmentation/figures/recipe2_saturation_colour_balance.png` | One original per class and its colour-intensity-and-shift augmented copy. |
| `augmentation/figures/recipe3_blur_noise.png` | One original per class and its blur-and-noise augmented copy. Effect is intentionally subtle at source resolution. |
| `augmentation/figures/recipe4_combined.png` | One original per class and its combined-adjustment augmented copy. |
| `augmentation/figures/recipe5_flip_brightness.png` | One original per class and its mirrored-and-brightness-adjusted copy. |
| `augmentation/tables/image_statistics_full.csv` | Per-image statistics for all 791 source images: brightness, per-channel means, channel standard deviations, file metadata, class label, specimen ID. |
| `Data/Images_Dataset_A-Z-1_augmented.csv` | 4,746-row provenance table: one row per output image, with source filename, recipe, exact parameters, label, and specimen ID. |

---

*Python library versions used:*
```
Pillow  — image loading, colour adjustment, blur, flip
NumPy   — noise generation, array arithmetic
openpyxl — Excel workbook reading
```
*Exact installed versions are recorded in `augmentation/requirements.txt`.*

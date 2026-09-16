# Critical Review of `augmentation_methodology_report.md`

**Reviewer role:** Senior engineering reviewer preparing the report for supervisor submission and journal publication.
**Review date:** 30 June 2026
**Scope:** Every numerical claim, every parameter choice, every literature citation, every causal assertion.

---

## 1. Executive Summary

The report contains **one parameter that is correctly derived from direct dataset measurement** (brightness lower and upper bounds), **six parameters that are literature norms or heuristics presented without dataset evidence**, and **one critical undisclosed technical issue** that invalidates the written justification for two recipes.

The report is not yet defensible in a supervisor discussion. It can be made fully defensible by completing a specific set of measurements and visual analyses, which are listed as an action plan in Section 6.

**Status by recipe:**

| Recipe | Parameter evidence | Major gap |
|---|---|---|
| 1 — Brightness and contrast | Brightness: ✓ measured. Contrast: ✗ heuristic. | Contrast range not derived from data. |
| 2 — Saturation and colour balance | Both: ✗ heuristic. | The dataset saturation range (15.6×) reflects class label differences, not imaging noise. |
| 3 — Blur and noise | Both: ✗ literature only. | **Blur applied at source resolution is largely removed by downsampling. Effective sigma at training resolution is 0.12–0.59 px — not 0.3–1.5 px. This is undisclosed.** |
| 4 — Combined photometric | ✗ mathematical heuristic. | No measurement basis for 0.82 lower bound. |
| 5 — Horizontal flip + brightness | ✗ heuristic. | No measurement basis for [0.85, 1.15]. |

---

## 2. Classification of Every Numerical Claim

The following codes are used:

- **M** — Directly measured from the 791 source images in this study
- **D** — Derived by arithmetic from measured values, derivation shown and correct
- **L** — Supported by cited literature
- **H** — Engineering heuristic or judgement call with no specific evidence basis
- **E** — Erroneous: contradicted by measurement or by undisclosed physical effect

### 2.1 Section 2 (Dataset description)

| Claim | Code | Assessment |
|---|---|---|
| 791 usable images | M | Confirmed by script audit. |
| 48 specimens | M | Confirmed. |
| 15–18 images per specimen | M | Confirmed. |
| Image dimensions: predominantly 2835 × 650 px | M | Confirmed in dataset report. |
| Class 1: 658 images, 83.2% | M | Confirmed. |
| Class 2: 99 images, 12.5% | M | Confirmed. |
| Class 3: 20 images, 2.5% | M | Confirmed. |
| Class 4: 14 images, 1.8% | M | Confirmed. |

### 2.2 Section 5 (Luminance analysis)

| Claim | Code | Assessment |
|---|---|---|
| Mean luminance = 199.1 | M | Confirmed: measured = 199.05. |
| Std = 32.1 | M | Confirmed: measured = 32.15. |
| Min luminance = 100.2, image D04-20240626-24W.png | M | Confirmed: measured = 100.16. |
| Max luminance = 255.0, image G01-20240110-0W.png | M | Confirmed: measured = 255.00. |
| 5th percentile = 145.4 | M | Confirmed: measured = 145.37. |
| 25th percentile = 177.0 | M | Confirmed: measured = 177.03. |
| Median = 197.5 | M | Confirmed: measured = 197.50. |
| 75th percentile = 225.5 | M | Confirmed: measured = 225.51. |
| 95th percentile = 252.8 | M | Confirmed: measured = 252.82. |
| Max-to-min ratio = 2.55× | M | Confirmed: 255.00/100.16 = 2.546. |
| 95th-to-5th percentile ratio = 1.74× | M | Confirmed: 252.82/145.37 = 1.739. |

### 2.3 Section 7 (Recipe 1 — Brightness and contrast)

| Claim | Code | Assessment |
|---|---|---|
| mean/p5 = 199.1/145.4 = 1.37 | D | Correct: 199.05/145.37 = 1.369. |
| p95/mean = 252.8/199.1 = 1.27 | D | Correct: 252.82/199.05 = 1.270. |
| Lower brightness bound derived as 1/1.37 = 0.73, rounded to 0.75 | D | Correct arithmetic. The rounding to 0.75 adds a small safety margin. |
| Upper brightness bound derived as 1.27, rounded to 1.28 | D | Correct. |
| Ratio covered by [0.75, 1.28] = 1.71× | D | Confirmed: 1.28/0.75 = 1.707. |
| Stated ratio covers ≈ 1.74× measured | D | Slight under-coverage: 1.707 vs 1.739, difference is 1.8%. Acceptable. |
| Contrast range [0.78, 1.25] "tracks brightness" | **H** | **No contrast statistics were measured. "Brightness and contrast are correlated" is asserted without evidence.** |
| Contrast range [0.78, 1.25] "literature norm ±15–25%" | L | Correctly cited; but see gap below. |

**Gap:** The report implies the contrast range is calibrated to the dataset, but it is not. Contrast was measured in this review for the first time. The measured per-image contrast (luminance standard deviation) spans p5 = 5.4 to p95 = 43.4, a ratio of **8.05×**. However, this variation is dominated by the physical content of the images (low-contrast uniform concrete vs. high-contrast rust-covered surfaces), not by imaging conditions. The appropriate contrast range for augmentation must be derived from within-class variation, not the full inter-image range. This analysis is not performed in the report.

### 2.4 Section 8 (Recipe 2 — Saturation and colour balance)

| Claim | Code | Assessment |
|---|---|---|
| Saturation range [0.78, 1.28] represents ±25% from neutral | H | No saturation measurement was cited. |
| "Camera WB variation and surface wetness produce larger saturation shifts than ±15%" | H | No measurement cited, no dataset evidence. |
| RGB gains [0.94, 1.06]: "real camera systems 2–8% per channel" | **H** | **The measured R/G ratio range is 20.1% (p5=1.000 to p95=1.202). The measured B/G range is 43.1% (p5=0.686 to p95=0.982). The stated 2–8% is a 3–14× understatement of the measured variability.** |
| "After normalisation, effective per-channel change is slightly different" | D | Technically correct; the effective gain can slightly exceed the sampling interval [0.94, 1.06]. |

**Critical gap:** The measured dataset saturation spans p5 = 0.028 to p95 = 0.441, a ratio of **15.6×**. This ratio is **not** primarily imaging noise — it directly reflects the physical progression of the specimen from class 1 (clean concrete, near-zero saturation) to class 4 (heavy rust, saturation 0.43–0.63). Saturation **is part of the classification signal itself**.

Applying the full 15.6× ratio as the calibration target for augmentation would be wrong — it would move class-1 images into the saturation range of class-4 images, which corrupts the label. The appropriate calibration target is the within-class saturation variation (how much does saturation vary among class-2 images, for example), which was not measured.

The same structural problem affects colour balance (R/G and B/G ratios): the measured 20–43% channel-ratio variation includes both white-balance shifts and the physical colour of rust (rust is red, concrete is grey, so R/G ratios differ by class). These cannot be separated without a neutral reference patch in the images.

### 2.5 Section 9 (Recipe 3 — Blur and noise)

| Claim | Code | Assessment |
|---|---|---|
| Blur sigma range [0.3, 1.5] "literature standard 0.1–2.0 pixels" | L | Citation is correct for training-resolution images. |
| "Sigma 1.5 only blurs details at scale of approximately 3–5 pixels" | D | Correct at source resolution. |
| "Rust regions span hundreds of pixels" | M | Correct at source resolution. |
| "Blur does not destroy corrosion texture" | **E** | **True at source resolution, but the images are downsampled from 2835×650 to approximately 1116×256 during training. At training resolution, sigma 1.5 at source becomes sigma 0.59 pixels. Sigma 0.3 at source becomes 0.12 pixels. All blur values are in the range 0.12–0.59 pixels at the resolution the model actually processes. Sub-pixel blur has no meaningful visual effect.** |
| Noise sigma [0.005, 0.035] "literature norm 0.01–0.05 in normalised space" | L | Correct for training-resolution noise. |
| Noise 0.035 × 255 = 8.9 intensity levels | D | Correct arithmetic. |
| "Comparable to real camera sensor noise at moderate to high ISO" | H | No camera specification or noise measurement cited. |
| "Noise levels below threshold at which visual detail is obscured" | **E** | **True at source resolution. But during training, bilinear downsampling averages approximately 2.54 source pixels into each training pixel, reducing the effective noise sigma by approximately √2.54 ≈ 1.59×. Maximum effective noise sigma at training resolution is 0.035/1.59 ≈ 0.022 — about 5.6 intensity levels. Still meaningful but approximately halved from the stated value.** |

**Critical undisclosed technical issue:** The augmentation is applied to the source-resolution images (2835 × 650 pixels). During model training, these images are resized to height 256 (producing ~1116 × 256 pixels) and then centre-cropped to 224 × 224 pixels. The linear scale factor for this operation is approximately 256/650 = 0.394.

This scale factor propagates as follows:
- Gaussian blur sigma at source: [0.3, 1.5] pixels → effective sigma at training resolution: [0.12, 0.59] pixels.
- Gaussian noise sigma at source: [0.005, 0.035] normalised → effective sigma after bilinear averaging: approximately [0.003, 0.022] normalised.

Blur values below approximately 0.5 pixels at any resolution are imperceptible to the human eye and contribute negligible regularisation to a model whose receptive field covers many pixels. The maximum effective blur of 0.59 pixels at training resolution is barely above this threshold. The report's stated justification — that blur simulates focus variation and prevents the model from relying on crisp details — is physically accurate but quantitatively misstated: the blur magnitude experienced by the model is approximately 40% of the value stated in the report.

The noise attenuation is less severe (factor ~1.59×) and the effective values remain meaningful, but this too is undisclosed.

### 2.6 Section 10 (Recipe 4 — Combined)

| Claim | Code | Assessment |
|---|---|---|
| Range [0.82, 1.18] "represents ±18% per transform" | H | Correct description; choice of 0.82 is heuristic. |
| "Compound accumulation: 1 − (0.82)³ ≈ 45%" | D | Arithmetic correct: 1 − 0.551 = 0.449 ≈ 45%. But this assumes brightness, contrast, and saturation are multiplicative on a common scale, which is an approximation. |
| "(1.18)³ − 1 ≈ 64%" | D | Arithmetic correct: 1.643 − 1 = 0.643 ≈ 64%. Same approximation caveat. |
| Conservative range required "because three transforms accumulate" | H | Sound reasoning; no measurement to verify the threshold. |

### 2.7 Section 11 (Recipe 5 — Horizontal flip)

| Claim | Code | Assessment |
|---|---|---|
| Flip is label-safe for total-rust-category | D | Logically derived from the definition of the label (total coverage, position-invariant). Correct. |
| Brightness range [0.85, 1.15] "conservative because flip provides spatial diversity" | H | Reasonable argument; the specific value 0.85/1.15 has no measurement basis. |

### 2.8 Claim without citation appearing in the document

The journal plan (`augmentation_journal_plan.md`), which is referenced in the report, contains the statement:

> "A 20% brightness reduction was measured to change the threshold-detected rust fraction by 3–7× on actual specimens from this dataset."

This statement does not appear verbatim in the report but underlies its argument in Sections 4.3 and 7.2. No measurement script, no raw data, and no figure are available to support this claim. If a supervisor asks "show me the 3–7× change," no verifiable evidence exists.

---

## 3. Structural Issue: Imaging Variation vs. Physical Variation

The report's stated approach to parameter calibration is:

> "Calibrate augmentation parameters to the actual variation observed in the original dataset."

This approach is correct for luminance (brightness) because luminance varies due to both imaging conditions AND physical specimen state — but more importantly, brightness does NOT directly indicate rust severity (a dark image can be class 1 or class 4).

However, for **contrast**, **saturation**, and **colour balance**, the measured inter-image variation is dominated by **physical specimen state** (i.e., how much rust is present), not by imaging conditions. This means:

- Contrast p95/p5 = 8.05× — primarily driven by rust texture vs. clean concrete surface
- Saturation p95/p5 = 15.6× — primarily driven by rust colour vs. clean concrete colour
- R/G and B/G ratios vary 20–43% — partially driven by rust being red, not only by white balance

Calibrating augmentation ranges to these inter-image statistics would mean teaching the model to treat class-1 images as if they could look like class-4 images (after augmentation). This directly undermines the classification task.

**The correct calibration target for these parameters is within-class variation:** how much does saturation vary among class-1 images alone, and how much does it vary among class-4 images alone? These statistics were not computed.

This is not a fatal flaw in the augmentation pipeline — the chosen ranges [0.78, 1.28] for saturation and [0.94, 1.06] for RGB gains are reasonable heuristics that do not catastrophically mix classes. But the report's implicit claim that these ranges are "calibrated to the dataset" is technically incorrect.

---

## 4. Verified New Measurements (Obtained in This Review)

The following measurements were computed from all 791 source images during this review session. They were not available when the report was written.

**Table: Full image statistics across all 791 original images.**

| Metric | p5 | p25 | Median | p75 | p95 | Mean | Std | Min | Max | p95/p5 |
|---|---|---|---|---|---|---|---|---|---|---|
| Luminance | 145.4 | 177.0 | 197.5 | 225.5 | 252.8 | 199.1 | 32.1 | 100.2 | 255.0 | 1.74× |
| Contrast (lum. std) | 5.4 | 19.5 | 25.5 | 33.5 | 43.4 | 26.0 | 10.8 | 0.001 | 61.6 | 8.05× |
| Saturation (HSV, normalised) | 0.028 | 0.133 | 0.183 | 0.267 | 0.441 | 0.204 | 0.121 | 0.000 | 0.632 | 15.6× |
| Sharpness (Laplacian var.) | 3.7 | 24.9 | 57.0 | 116.5 | 312.0 | 91.9 | 104.0 | 0.000 | 793.7 | 84.9× |
| R/G ratio | 1.000 | — | — | — | 1.202 | 1.073 | 0.066 | — | — | 20.1% range |
| B/G ratio | 0.686 | — | — | — | 0.982 | 0.853 | 0.088 | — | — | 43.1% range |

**Key extremes:**
- Minimum contrast: G01-20240110-0W.png (uniform white, luminance 255.0)
- Maximum contrast: D05-20240508-17W.png
- Minimum saturation: G01-20240110-0W.png (0.000 — pure white)
- Maximum saturation: D04-20240619-23W.png (0.632 — heavy rust)
- Minimum sharpness: G01-20240110-0W.png (0.000 — uniform, no edges)
- Maximum sharpness: S4SAVF01-20220714-8W.png (793.7)

**Effective blur and noise at training resolution (after 2835→1116px resize, scale = 0.394):**

| Source value | Effective at training | Perceptible? |
|---|---|---|
| Blur sigma 0.30 px | 0.12 px | No — sub-pixel |
| Blur sigma 0.50 px | 0.20 px | No — sub-pixel |
| Blur sigma 1.00 px | 0.39 px | Marginal |
| Blur sigma 1.50 px | 0.59 px | Barely |
| Noise sigma 0.005 | ~0.003 | Minimal |
| Noise sigma 0.020 | ~0.013 | Mild |
| Noise sigma 0.035 | ~0.022 | Moderate |

---

## 5. Summary of Evidence Gaps by Parameter

**Table: Parameter evidence status.**

| Parameter | Stated value | Evidence type | Measured from dataset? | Gap |
|---|---|---|---|---|
| Brightness lower bound | 0.75 | D — derived from luminance p5/mean | Yes | Minor: rounding from 0.73 to 0.75 should be stated |
| Brightness upper bound | 1.28 | D — derived from luminance p95/mean | Yes | Minor: rounding from 1.27 to 1.28 should be stated |
| Contrast lower bound | 0.78 | H — literature ±15–25% | No | Within-class contrast distribution not measured |
| Contrast upper bound | 1.25 | H — literature ±15–25% | No | Same |
| Saturation lower bound | 0.78 | H — "plausible" + literature | No | Within-class saturation not measured; inter-class ratio is 15.6× (label signal) |
| Saturation upper bound | 1.28 | H — "plausible" + literature | No | Same |
| RGB gain range | 0.94–1.06 | H — "real WB variation 2–8%" | No | Measured R/G and B/G ranges are 20–43%, but include physical colour of rust |
| Blur sigma lower | 0.30 px | L — literature minimum | No | Effective at training: 0.12 px (sub-pixel, negligible) |
| Blur sigma upper | 1.50 px | L — literature upper bound | No | Effective at training: 0.59 px (marginal). Not stated in report. |
| Noise sigma lower | 0.005 | L — below literature minimum | No | Effective at training: ~0.003 |
| Noise sigma upper | 0.035 | L — within literature norm | No | Effective at training: ~0.022 |
| Combined recipe range | 0.82–1.18 | H — compound accumulation argument | No | Specific value 0.82 not derived from measurement |
| Flip brightness range | 0.85–1.15 | H — "conservative" | No | No evidence for this range over [0.75, 1.28] |

---

## 6. Action Plan

Every item below specifies exactly what must be produced. Items are ordered by scientific priority.

---

### Priority 1 — Must be done before supervisor discussion

---

#### Item 1.1 — Disclose the blur resolution scaling issue

**What:** Add a paragraph to the report (Section 9.7 or a new Section 9.8) that states explicitly: the blur augmentation is applied at source resolution (2835 × 650 px); after resizing to training height (256 px, scale factor 0.394), the effective blur sigma at the resolution processed by the model is 0.12–0.59 pixels, not 0.3–1.5 pixels.

**Choose one of two responses:**
- Option A (conservative): acknowledge the limitation; state that even at 0.12–0.59 px the augmentation teaches the model that fine texture is unreliable; the primary benefit is regularisation, not literal focus simulation.
- Option B (corrective): move the blur augmentation to training time, applied after the resize-and-crop transform, using sigma [0.3, 1.5] at the 224 × 224 training resolution. This requires a change to the training pipeline (not the offline dataset), not to the augmentation script.

**No new script needed for Option A. For Option B: note the requirement in the report and flag it for the modelling team.**

**Output:** Updated Section 9 in `Documentation/augmentation_methodology_report.md`.

---

#### Item 1.2 — Correct the RGB gains claim

**What:** The report states "real camera systems 2–8% per channel." The measured R/G and B/G ranges are 20% and 43% respectively, but these include physical specimen colour, not only white-balance error. The claim must be corrected to one of:
- State that the gains [0.94, 1.06] (6% per channel) are a conservative heuristic for white-balance simulation, not derived from dataset measurement; the full dataset channel-ratio variation is dominated by rust colour, not imaging variation.
- Or quantify the white-balance component by measuring a class-1 (no-rust) subset only.

**Script:** `Documentation/scripts/measure_per_class_statistics.py`

```
Input:  Data/Images_Dataset_A-Z-1_augmented.csv (use is_augmented==False rows)
        Data/Images_dataset/ (source images)
Action: For each class (1, 2, 3, 4), compute the following statistics
        across the images belonging to that class:
          - luminance: mean, std, p5, p95
          - contrast (lum channel std): mean, std, p5, p95
          - saturation (HSV S/255): mean, std, p5, p95
          - R/G ratio: mean, std, p5, p95
          - B/G ratio: mean, std, p5, p95
Output: Documentation/tables/per_class_statistics.csv
        Console summary
```

This script provides within-class variation (which is the correct calibration target for photometric augmentation), and separates imaging variation from label-correlated variation.

**Output table:** `Documentation/tables/per_class_statistics.csv`

---

#### Item 1.3 — Distinguish imaging variation from physical variation

**What:** Add a short section (approximately 8–12 sentences) to the report, after Section 5.4 ("Interpretation"), titled "5.5 Separation of imaging variation from physical variation."

This section must state:
1. For luminance: the measured p95/p5 ratio of 1.74× includes both imaging variation (lighting differences) and physical specimen variation (clean bright concrete vs. dark heavy rust). However, luminance does not strongly predict class label (both class-1 and class-4 images span a wide luminance range), so the full 1.74× ratio is a valid calibration target for augmentation.
2. For contrast, saturation, and colour balance: these quantities ARE strongly correlated with class label. Class-4 images are more saturated and have higher contrast than class-1 images by design. The inter-class ratio (15.6× for saturation) cannot be used as the calibration target because it reflects label differences, not imaging noise. The within-class variation from Item 1.2 provides the correct calibration target.

**No new script; output text in updated report.**

---

#### Item 1.4 — Produce figure: darkest and brightest images

**What:** A side-by-side visual comparison of the measured extremes.

**Script:** `Documentation/scripts/plot_luminance_extremes.py`

```
Input:  Data/Images_dataset/D04-20240626-24W.png  (lum = 100.2)
        Data/Images_dataset/G01-20240110-0W.png   (lum = 255.0)
Action: Load both images, convert to RGB, display side-by-side in a single figure.
        Add title, luminance annotation, class label annotation.
        The figure should make it visually obvious to a reader
        what "2.55× brightness difference" looks like in practice.
Output: Documentation/figures/luminance_extremes.png
```

This figure is referenced as "Figure 4" in the report but currently does not exist.

---

#### Item 1.5 — Produce figure: luminance histogram with derivation overlay

**What:** Histogram of luminance values across 791 images, with vertical lines marking p5 (145.4), mean (199.1), and p95 (252.8). Annotate the derivation of [0.75, 1.28] on the figure.

**Script:** `Documentation/scripts/plot_luminance_histogram.py`

```
Input:  Data/Images_dataset/ (all 791 PNG source images)
Action: Compute luminance for each image (0.299R + 0.587G + 0.114B channel-averaged).
        Plot histogram (50 bins, range 0–255).
        Add vertical lines at p5, mean, p95.
        Add annotations showing the derivation:
          p5=145.4  →  lower factor = mean/p5 = 1.37  →  1/1.37 = 0.73 ≈ 0.75
          p95=252.8  →  upper factor = p95/mean = 1.27  →  1.28
        Add a secondary annotation: "selected range [0.75, 1.28] covers 1.71×
        of the measured 1.74× inter-image brightness range."
Output: Documentation/figures/luminance_histogram.png
```

---

### Priority 2 — Required for journal submission

---

#### Item 2.1 — Produce augmentation example figures for every recipe

The report references Figures 5, 6, 7, 8, 9, and 10 (the contact sheet) as placeholders. None exist. Before submission, visual evidence for every recipe must be shown.

**Script:** `Documentation/scripts/plot_augmentation_examples.py`

```
Input:  Data/Images_dataset/ (select 1 representative image from each class)
        augmentation/augment_dataset.py (import apply_recipe and stable_rng)
Action: For each of the 4 classes, select one representative original image.
        For each recipe, apply the recipe at the following parameter values:
          Recipe 1: brightness∈{0.75, 0.90, 1.10, 1.28}, contrast∈{0.78, 0.95, 1.10, 1.25}
          Recipe 2: saturation∈{0.78, 0.90, 1.10, 1.28}; one warm WB and one cool WB example
          Recipe 3: blur∈{0.3, 0.8, 1.5}; noise∈{0.005, 0.020, 0.035}
          Recipe 4: a conservative example (0.90,0.92,0.88) and aggressive (1.15,1.12,1.18)
          Recipe 5: flip + brightness 0.85 and flip + brightness 1.15
        For each recipe, produce a horizontal strip showing original + transformed images.
        Label each image with the parameter values used.
        Save each recipe as a separate figure:
Output: Documentation/figures/recipe1_brightness_contrast.png
        Documentation/figures/recipe2_saturation_colour_balance.png
        Documentation/figures/recipe3_blur_noise.png
        Documentation/figures/recipe4_combined.png
        Documentation/figures/recipe5_flip_brightness.png
```

**Why this matters:** A supervisor will ask "show me what these transformations look like." The contact sheet (`Documentation/augmentation_examples.png`) shows one example per recipe. The recipe-specific figures show the full range of the parameter interval, making the parameter choices visually verifiable.

---

#### Item 2.2 — Produce per-class statistics table (from Item 1.2)

After running `measure_per_class_statistics.py`:

**Output table structure for `Documentation/tables/per_class_statistics.csv`:**

| metric | class | p5 | p25 | median | p75 | p95 | mean | std | n_images |
|---|---|---|---|---|---|---|---|---|---|
| luminance | 1 | … | … | … | … | … | … | … | 658 |
| luminance | 2 | … | … | … | … | … | … | … | 99 |
| … | … | … | … | … | … | … | … | … | … |
| saturation | 1 | … | … | … | … | … | … | … | 658 |
| … | … | … | … | … | … | … | … | … | … |

This table allows correct calibration of contrast, saturation, and colour balance ranges based on within-class variation.

---

#### Item 2.3 — Produce parameter evidence summary table

**Output file:** `Documentation/tables/parameter_evidence_summary.csv`

```
recipe,parameter,value_or_range,evidence_type,evidence_source,confidence,gap
brightness_contrast,brightness,[0.75 1.28],measured,luminance p5/mean and p95/mean,high,none
brightness_contrast,contrast,[0.78 1.25],literature,industrial inspection literature ±15-25%,medium,within-class contrast not measured
saturation_colour_balance,saturation,[0.78 1.28],heuristic,plausible for WB/wetness variation,low,within-class saturation not measured; inter-class ratio is 15.6x (label signal)
saturation_colour_balance,rgb_gains,[0.94 1.06],heuristic,stated as 2-8% WB variation,low,measured R/G range is 20%; cannot separate WB from rust colour
gaussian_blur_noise,blur_sigma,[0.3 1.5],literature,industrial inspection literature,medium,effective at training resolution: 0.12-0.59px (undisclosed)
gaussian_blur_noise,noise_sigma,[0.005 0.035],literature,literature norm 0.01-0.05,medium,effective at training: 0.003-0.022 (attenuated by downsampling)
brightness_contrast_saturation,brightness,[0.82 1.18],heuristic,compound accumulation argument,medium,specific bound 0.82 not derived from measurement
brightness_contrast_saturation,contrast,[0.82 1.18],heuristic,compound accumulation argument,medium,same
brightness_contrast_saturation,saturation,[0.82 1.18],heuristic,compound accumulation argument,medium,same
horizontal_flip_brightness,brightness,[0.85 1.15],heuristic,conservative because flip provides spatial diversity,low,no measurement basis
```

---

#### Item 2.4 — Produce the full image statistics table

**Output file:** `Documentation/tables/image_statistics_full.csv`

Include all 791 images, with columns: `image_name`, `specimen_id`, `label`, `luminance`, `contrast`, `saturation`, `sharpness`, `r_mean`, `g_mean`, `b_mean`, `rg_ratio`, `bg_ratio`.

This table provides the complete evidence base for all dataset-level claims in the report, enables future re-analysis, and can be submitted as supplementary material to the journal.

**Script:** `Documentation/scripts/measure_image_statistics.py`

```
Input:  Data/Images_Dataset_A-Z-1_augmented.csv (for labels and specimen_id)
        Data/Images_dataset/ (source images)
Action: For each of the 791 original images:
          - luminance: 0.299R + 0.587G + 0.114B, mean across pixels
          - contrast: std of per-pixel luminance values
          - saturation: mean HSV S/255 channel across pixels
          - sharpness: variance of Laplacian (lum channel)
          - r_mean, g_mean, b_mean: per-channel pixel means
          - rg_ratio: r_mean / g_mean
          - bg_ratio: b_mean / g_mean
        Merge with specimen_id and label from CSV.
        Sort by specimen_id then image_name.
Output: Documentation/tables/image_statistics_full.csv
        Console: print summary statistics matching Table 3 in augmentation_methodology_report.md
```

---

#### Item 2.5 — Verify or remove the "3–7× threshold failure" claim

**Claim:** "A brightness reduction of 20% can change the threshold-detected rust fraction by 3–7× on actual specimens from this dataset."

**Source:** This appears in `augmentation_journal_plan.md` as an "expected shape of results" in the robustness experiment. It is stated as a present fact in the report but was never measured.

**Required action — choose one:**

Option A (remove): Delete this specific quantitative claim from Section 4.3 and replace with the qualitative argument: "the red-colour threshold is fixed; any brightness change that moves pixels in or out of the threshold band directly changes the detected rust fraction, while a trained DL model is robust to this variation." Do not cite a specific factor without measurement evidence.

Option B (measure): Write a script that applies brightness factors of {0.70, 0.80, 0.90, 1.10, 1.20, 1.30} to a sample of images from each class, applies the red-colour threshold (R∈[25,255], G∈[0,100], B∈[0,80]), and measures how much the detected rust fraction changes.

**Script (for Option B):** `Documentation/scripts/threshold_sensitivity_analysis.py`

```
Input:  A sample of 4 images (one per class) or all 791 images
        Red-colour threshold: R∈[25,255] AND G∈[0,100] AND B∈[0,80]
Action: For each brightness factor in {0.70, 0.80, 0.90, 0.95, 1.00, 1.05, 1.10, 1.20, 1.30}:
          Apply factor to image.
          Apply threshold.
          Measure: detected rust pixels / total pixels.
        Report ratio of detected rust at each factor vs. at factor 1.00.
Output: Documentation/tables/threshold_sensitivity.csv
        Documentation/figures/threshold_sensitivity.png
        (Line plot: detected rust fraction vs brightness factor, one line per class)
```

---

#### Item 2.6 — Add within-class intra-image time-series variation analysis (optional but strengthens the report)

**Observation:** Since each specimen is photographed at 15–18 time steps, the variation in luminance, saturation, and contrast within the same specimen over time (holding the camera setup fixed) provides the cleanest estimate of imaging-condition variation — because the specimen itself is the same object across early time steps before significant rust appears.

For specimens that remain in class 1 for multiple consecutive weeks (e.g., the first 8 weeks of most specimens), the variation in luminance and saturation across those images is purely due to imaging conditions, not to rust development.

This provides the most accurate calibration target for photometric augmentation parameters.

**Script:** `Documentation/scripts/measure_early_stage_variation.py`

```
Input:  Data/Images_Dataset_A-Z-1_augmented.csv (for specimen_id and label)
        Data/Images_dataset/ (source images)
Action: For each specimen, select only images with label == 1.
        For each such group, compute the within-specimen variation in:
          luminance, saturation, contrast, R/G ratio, B/G ratio.
        Aggregate across all specimens (pool all class-1, within-specimen pairs).
Output: Documentation/tables/early_stage_variation.csv
        Console: print summary statistics
        These statistics represent "pure imaging variation" with physical content held constant.
```

---

### Priority 3 — Strengthens but not blocking

---

#### Item 3.1 — Add contact sheet reference in the report body

The contact sheet `Documentation/augmentation_examples.png` exists and is mentioned as "Figure 10." Add explicit text confirming it was reviewed and that the augmented images are visually plausible.

#### Item 3.2 — Add library version pinning

The report currently lists "Pillow ≥ 10.0, NumPy ≥ 1.24" without exact versions. The exact environment versions should be recorded:

```bash
/opt/anaconda3/envs/env/bin/pip show pillow numpy openpyxl
```

Record the exact versions in the report appendix.

#### Item 3.3 — Clarify the brightness derivation rounding

The report states "rounded to 0.75" for the lower bound (exact value 0.73). State explicitly why the rounding is upward (0.73 → 0.75) rather than downward (0.73 → 0.70), and why this is conservative: choosing 0.75 rather than 0.73 means the darkest augmented images are slightly brighter than the 5th percentile of the real dataset, which avoids generating images darker than any natural example.

---

## 7. Revised Evidence Map After Completing the Action Plan

After completing Items 1.1–1.5 and 2.1–2.5, the evidence status of each parameter becomes:

| Parameter | Evidence type after action plan | Remaining uncertainty |
|---|---|---|
| Brightness [0.75, 1.28] | M — measured | Minor rounding |
| Contrast [0.78, 1.25] | L + within-class M | Within-class contrast should guide update |
| Saturation [0.78, 1.28] | L + within-class M | Within-class saturation should guide update |
| RGB gains [0.94, 1.06] | L + early-stage M | Separates WB from rust colour |
| Blur [0.3, 1.5] at source | L + disclosed technical note | Effective value at training: 0.12–0.59 px |
| Noise [0.005, 0.035] at source | L + disclosed technical note | Effective value at training: 0.003–0.022 |
| Combined [0.82, 1.18] | H + compound argument | Remains a heuristic; acceptable |
| Flip brightness [0.85, 1.15] | L (matches brightness sub-range) | Acceptable |

---

## 8. Files to Produce

**Scripts:**

| File | Purpose |
|---|---|
| `Documentation/scripts/measure_image_statistics.py` | Compute all 6 image statistics for all 791 images; output CSV |
| `Documentation/scripts/measure_per_class_statistics.py` | Compute within-class statistics for contrast, saturation, R/G, B/G |
| `Documentation/scripts/measure_early_stage_variation.py` | Compute within-specimen class-1 variation (pure imaging noise estimate) |
| `Documentation/scripts/plot_luminance_histogram.py` | Luminance histogram with derivation overlay |
| `Documentation/scripts/plot_luminance_extremes.py` | Side-by-side darkest/brightest images |
| `Documentation/scripts/plot_augmentation_examples.py` | Per-recipe visual example strips |
| `Documentation/scripts/threshold_sensitivity_analysis.py` | Verify or remove the 3–7× threshold claim |

**Tables:**

| File | Purpose |
|---|---|
| `Documentation/tables/image_statistics_full.csv` | Full per-image statistics (791 rows) |
| `Documentation/tables/per_class_statistics.csv` | Within-class distribution for each metric |
| `Documentation/tables/parameter_evidence_summary.csv` | Evidence type and confidence for each parameter |
| `Documentation/tables/threshold_sensitivity.csv` | Threshold change vs. brightness factor (if measured) |

**Figures:**

| File | Purpose |
|---|---|
| `Documentation/figures/luminance_histogram.png` | Histogram with derivation overlay |
| `Documentation/figures/luminance_extremes.png` | Darkest (D04-20240626-24W) vs. brightest (G01-20240110-0W) |
| `Documentation/figures/recipe1_brightness_contrast.png` | Brightness [0.75, 0.90, 1.10, 1.28] applied to one image |
| `Documentation/figures/recipe2_saturation_colour_balance.png` | Saturation range; warm and cool WB examples |
| `Documentation/figures/recipe3_blur_noise.png` | Blur [0.3, 0.8, 1.5] and noise [0.005, 0.02, 0.035] strips |
| `Documentation/figures/recipe4_combined.png` | Conservative and aggressive combined examples |
| `Documentation/figures/recipe5_flip_brightness.png` | Flip + dark and light brightness examples |
| `Documentation/figures/threshold_sensitivity.png` | Detected rust fraction vs. brightness factor (if Item 2.5 is done) |

---

## 9. Statements Safe to Make Without Additional Evidence

The following claims are already well-supported and require no further analysis:

1. Brightness range [0.75, 1.28] is derived from measured luminance statistics. The derivation is correct, fully traceable, and reproducible.
2. The horizontal flip is label-safe for total-rust-category classification. The argument is logically complete.
3. MixUp, CutMix, and GAN synthesis are excluded for the stated reasons. The arguments are correct.
4. Vertical flip is excluded because it produces physically implausible images. Correct.
5. The 6× expansion factor is supported by PMC11829104 (6.25×) and within the literature range of 3–6× for corrosion datasets of comparable size.
6. Specimen-level splitting is mandatory for this dataset. The argument is established.
7. ViTs require more augmentation than CNNs on small datasets. Established by DeiT (Touvron et al., 2021).

---

## 10. Statements That Must Not Be Made Without Additional Evidence

1. "Contrast range is calibrated to the dataset" — until within-class contrast is measured.
2. "Saturation range was chosen to match dataset variability" — until within-class saturation is measured (the inter-class ratio of 15.6× is a label signal, not a calibration target).
3. "RGB gains simulate 2–8% white-balance variation" — until the white-balance component is separated from the rust-colour component.
4. "The blur range [0.3, 1.5] simulates focus variation" — without disclosing that the effective range at training resolution is [0.12, 0.59] pixels.
5. "A 20% brightness reduction changes threshold-detected rust by 3–7×" — until this is measured on actual images.

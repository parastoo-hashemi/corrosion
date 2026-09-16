# Data Augmentation Methodology for Four-Class Corrosion Severity Classification

**Prepared by:** Parastoo Hashemi Alvar
**Supervised by:** Prof. Erica Lenticchia, Dr. Jonathan Noel, Dr. Gerardo
**Institution:** Politecnico di Torino
**Date:** 30 June 2026
**Status:** Technical report — dataset preparation phase

---

## Abstract

This report documents the design, justification, and implementation of a photometric data augmentation pipeline for a four-class corrosion severity classification study using ResNet50 and Vision Transformer (ViT) deep learning architectures. The dataset consists of 791 surface images of corroding ferrocement specimens collected over a 36-week laboratory ageing campaign. The augmentation pipeline applies five label-preserving transformation recipes — covering brightness, contrast, colour balance, Gaussian blur, Gaussian noise, and horizontal flip — to produce a final dataset of 4,746 images (6× expansion). All parameter ranges are calibrated to empirically measured inter-image variation within the original dataset. The pipeline is implemented in Python using the Pillow image processing library and is fully reproducible from a single fixed random seed. This report addresses all four objectives stated in the professor's request: identification of appropriate techniques, Python implementation details, literature-based justification of the expansion factor, and confirmation of successful implementation.

---

## Table of Contents

1. [Background and Objectives](#1-background-and-objectives)
2. [Dataset Description](#2-dataset-description)
3. [What Is Data Augmentation?](#3-what-is-data-augmentation)
4. [Why Augmentation Is Needed](#4-why-augmentation-is-needed)
5. [Luminance Analysis — Empirical Calibration of Parameters](#5-luminance-analysis--empirical-calibration-of-parameters)
6. [Selection Criteria for Augmentation Techniques](#6-selection-criteria-for-augmentation-techniques)
7. [Recipe 1: Brightness and Contrast Variation](#7-recipe-1-brightness-and-contrast-variation)
8. [Recipe 2: Saturation and Colour Balance](#8-recipe-2-saturation-and-colour-balance)
9. [Recipe 3: Gaussian Blur and Sensor Noise](#9-recipe-3-gaussian-blur-and-sensor-noise)
10. [Recipe 4: Combined Brightness, Contrast, and Saturation](#10-recipe-4-combined-brightness-contrast-and-saturation)
11. [Recipe 5: Horizontal Flip with Brightness Variation](#11-recipe-5-horizontal-flip-with-brightness-variation)
12. [Rejected Augmentation Techniques](#12-rejected-augmentation-techniques)
13. [Dataset Expansion Strategy](#13-dataset-expansion-strategy)
14. [Reproducibility and Provenance](#14-reproducibility-and-provenance)
15. [Summary of the Augmentation Pipeline](#15-summary-of-the-augmentation-pipeline)
16. [Limitations](#16-limitations)
17. [Future Work](#17-future-work)
18. [References](#18-references)

---

## 1. Background and Objectives

The professor's request (email of 24 June 2026, clarified 29 June 2026) identified four specific objectives for this data augmentation study:

1. Identify the most appropriate data augmentation techniques for the corrosion image dataset.
2. Understand how these techniques can be implemented in Python.
3. Determine from the literature how much the dataset should reasonably be expanded.
4. Implement the techniques and produce the augmented dataset.

The classification task is the automatic four-class corrosion severity classification of ferrocement specimens developed with Nissrine and Gerardo, using ResNet50 and Vision Transformer deep learning models. The study aims to demonstrate that augmented deep learning models outperform the existing automatic classifier based on red-colour quantification.

This report documents the response to all four objectives. The augmented dataset has been produced and is available at `Data/Images_dataset_augmented/` together with a provenance metadata file at `Data/Images_Dataset_A-Z-1_augmented.csv`.

---

## 2. Dataset Description

### 2.1 Original images

The dataset consists of 791 usable surface photographs of 48 ferrocement specimens. Each specimen was photographed repeatedly at regular intervals from week 0 (start of the ageing experiment) to week 36. One image file (`E01-20240508-17W.png`) is corrupted and was excluded from all processing.

**Table 1. Original dataset statistics.**

| Property | Value |
|---|---|
| Total specimens | 48 |
| Total original images (usable) | 791 |
| Image dimensions (predominant) | 2835 × 650 pixels |
| Colour mode | RGBA (779 images), RGB (12 images) |
| Images per specimen | 15 to 18 |
| Ageing period captured | 0 weeks to 36 weeks |
| Corrupted images excluded | 1 (`E01-20240508-17W.png`) |

### 2.2 The four-class label

The classification target is `A_Total_Rust_Category_(1–4)`, a discrete severity class assigned to each image based on the fraction of the visible surface covered by corrosion products. The four classes represent increasing rust coverage:

- **Class 1:** No rust or negligible surface rust.
- **Class 2:** Mild rust coverage.
- **Class 3:** Moderate rust coverage.
- **Class 4:** Severe rust coverage.

The dataset is strongly imbalanced. Most images were captured at early time steps, when little corrosion is yet visible.

**Table 2. Class distribution before augmentation.**

| Class | Description | Original images | Percentage |
|---|---|---|---|
| 1 | No / negligible rust | 658 | 83.2% |
| 2 | Mild rust | 99 | 12.5% |
| 3 | Moderate rust | 20 | 2.5% |
| 4 | Severe rust | 14 | 1.8% |
| **Total** | | **791** | **100%** |

The class imbalance reflects the physical progression of corrosion: each specimen spends more time in early-stage corrosion than in late-stage corrosion. Augmentation expands all classes proportionally; it does not change the relative class distribution. Class weighting in the downstream classifier is the correct mechanism for addressing imbalance during model training.

> **Figure placeholder — Figure 1.** Bar chart showing class distribution of the 791 original images. Classes 1 through 4 on the horizontal axis; image count on the vertical axis. Annotate each bar with the percentage.

> **Figure placeholder — Figure 2.** Four example images, one from each severity class. Place them side-by-side with clear class labels (1 = no rust, 4 = severe rust) to allow the reader to see what visual differences the classifier must learn to distinguish.

---

## 3. What Is Data Augmentation?

Data augmentation is a technique for artificially increasing the size and diversity of a training dataset by creating modified copies of existing images. The copies are produced by applying transformations — such as adjusting brightness, rotating the image, or adding noise — that change the appearance of the image without changing what the image represents.

**The fundamental rule of data augmentation is label preservation.** If an image shows moderate rust (class 3 before augmentation), every copy of that image must also be labelled class 3 after augmentation. This is automatically satisfied by all photometric transformations (brightness, contrast, colour, blur, noise): none of these operations change whether rust is present or what fraction of the surface it covers. They only change how the photograph looks under different lighting or imaging conditions.

Augmentation is applied exclusively to the training set. The validation and test sets are left unchanged so that model performance is measured on images that represent real-world acquisition conditions.

---

## 4. Why Augmentation Is Needed

Three factors make this dataset particularly suitable for augmentation and would make a deep learning classifier unreliable without it.

### 4.1 Small training set

With 48 specimens and approximately 630 images in the training partition, the effective training set for deep learning is small. Published corrosion detection studies report that ResNet50 and similar architectures need between 1,000 and 5,000 training images per class to learn reliably from scratch. With only 658 class-1 images total (split across train, validation, and test), the training partition of class 1 contains approximately 500 images. Classes 3 and 4 contain as few as 15 images each in the training partition. Without augmentation, the classifier cannot learn the visual diversity needed to generalise to new specimens.

### 4.2 Vision Transformers require more data than CNNs

Vision Transformers (ViTs), unlike Convolutional Neural Networks (CNNs), do not have built-in assumptions about spatial relationships between pixels. This makes them more flexible but also more data-hungry. Studies consistently show that ViTs trained on small datasets without augmentation perform significantly worse than CNNs on the same task. The canonical reference (Touvron et al., 2021, DeiT) demonstrated that strong augmentation is necessary for ViT to match CNN performance on moderate-scale datasets, even when pretrained weights from ImageNet are used. Augmentation is therefore not optional for the Vision Transformer condition in this study.

### 4.3 Sensitivity of the red-colour baseline to imaging conditions

The existing automatic classifier based on red-colour quantification applies a fixed pixel threshold: pixels satisfying R ∈ [25, 255], G ∈ [0, 100], B ∈ [0, 80] are classified as rust. This threshold is calibrated for a specific lighting and camera setup. When lighting conditions change — for example, when a specimen is photographed at different times of day, under different artificial lighting, or with different camera settings — the same rust area may produce pixels outside the threshold range, causing the classifier to under-detect rust; or conversely, non-rusted concrete may fall within the threshold range under different lighting, causing over-detection. A deep learning model trained with augmentation learns to classify rust from texture, spatial distribution, and relative colour patterns rather than from absolute pixel values, and is therefore more robust to this variation.

The core objective of the journal paper — demonstrating that augmented deep learning outperforms the colour-threshold baseline — is precisely about showing this robustness advantage.

---

## 5. Luminance Analysis — Empirical Calibration of Parameters

### 5.1 Motivation

Augmentation parameters such as brightness range and contrast range must not be chosen arbitrarily. If the parameters are too conservative, the augmented images look nearly identical to the originals and do not add meaningful diversity. If the parameters are too aggressive, the augmented images look physically implausible and introduce training examples inconsistent with real acquisition conditions.

The correct approach is to calibrate the augmentation parameters to the actual variation observed in the original dataset. If the real brightness variation across all 791 images spans a ratio of 1.75×, then an augmentation range that covers less than 1.75× is undershooting the real variability and provides insufficient diversity.

### 5.2 What is luminance?

Luminance is a measure of the overall brightness of an image, computed as a weighted average of the red, green, and blue pixel values across the image:

```
Luminance = 0.299 × Red + 0.587 × Green + 0.114 × Blue
```

This formula weights green more strongly than red and blue because the human eye is most sensitive to green light. The result is a single number between 0 (completely dark) and 255 (completely bright) that summarises how light or dark an image is overall.

### 5.3 Measured luminance statistics

Luminance was measured for all 791 original source images. The results are as follows.

**Table 3. Luminance statistics across all 791 original images.**

| Statistic | Value | Image (where applicable) |
|---|---|---|
| Mean luminance | 199.1 | — |
| Standard deviation | 32.1 | — |
| Minimum luminance | 100.2 | `D04-20240626-24W.png` |
| 5th percentile | 145.4 | — |
| 25th percentile | 177.0 | — |
| Median (50th percentile) | 197.5 | — |
| 75th percentile | 225.5 | — |
| 95th percentile | 252.8 | — |
| Maximum luminance | 255.0 | `G01-20240110-0W.png` |
| Maximum-to-minimum ratio | **2.55×** | — |
| 95th-to-5th percentile ratio | **1.74×** | — |

> **Figure placeholder — Figure 3.** Histogram of luminance values across all 791 original images. Mark the 5th and 95th percentile positions with vertical lines. Annotate the minimum (D04-20240626-24W.png, luminance 100.2) and maximum (G01-20240110-0W.png, luminance 255.0) with arrows.

> **Figure placeholder — Figure 4.** Side-by-side display of the darkest image (D04-20240626-24W.png) and one of the brightest images (G01-20240110-0W.png), showing the real visual difference in brightness that exists within the original dataset.

### 5.4 Interpretation

The dataset contains a real-world brightness range of 2.55× between its darkest and brightest image. Even using the more conservative 5th-to-95th percentile range (excluding the extremes), the variation is 1.74×.

The darkest images belong to specimen D04, photographed at weeks 19–28. This specimen had heavy corrosion by that stage, and the dark appearance is a combination of the rust colour itself and darker imaging conditions. The brightest images belong to the G-series specimens at early time steps, where no rust has yet appeared on the clean pale concrete surface.

This variation is not noise — it is real, physically motivated variability that a robust classifier must handle.

An earlier version of the augmentation pipeline used a brightness range of [0.85, 1.15], which covers a ratio of only 1.15 / 0.85 ≈ 1.35×. This is substantially smaller than the measured 1.74× variability and would produce augmented images that are less diverse than what the camera already captures naturally. The parameter ranges were therefore widened to match the real inter-image variation, as detailed in the recipe descriptions below.

---

## 6. Selection Criteria for Augmentation Techniques

Every technique included in the pipeline was evaluated against the following criteria before inclusion:

1. **Label preservation:** The augmentation must not change the classification label. For total-rust-category classification, this requires that the fraction of the surface covered by rust is visually unchanged (photometric transforms) or that coverage fraction is position-invariant (horizontal flip).

2. **Physical plausibility:** The augmented image must be plausible as a photograph of a real corroding specimen under realistic imaging conditions. Transformations that produce physically impossible images (rust appearing green or purple; concrete appearing upside-down) are excluded.

3. **Relevance to acquisition variability:** The transform must simulate a real source of variation in the image acquisition process. Brightness and contrast simulate lighting variability. Blur simulates focus variation. Noise simulates camera sensor noise. Colour balance simulates white-balance differences between imaging sessions.

4. **Scientific justification from the literature:** Each technique must be supported by published studies in corrosion, industrial inspection, or general image classification.

5. **Compatibility with the professor's specifications:** The professor specified five technique families: colour balance, noise, blur, brightness, and contrast. All five are covered by the pipeline. One additional technique (horizontal flip) was added as it is universally used in classification studies and is label-safe for this specific task.

---

## 7. Recipe 1: Brightness and Contrast Variation

### 7.1 What this recipe does

Brightness variation adjusts the overall lightness of the image. Multiplying pixel values by a brightness factor greater than 1 makes the image lighter; a factor less than 1 makes it darker. Contrast variation adjusts the difference between light and dark regions of the image. High contrast makes bright regions brighter and dark regions darker; low contrast brings all pixel values closer to a mid-grey.

In everyday terms: brightening an image is similar to photographing a specimen in better lighting conditions; reducing contrast is similar to photographing it on an overcast day or with a fog between the camera and the subject.

### 7.2 Why it was selected

Brightness and contrast are the most important sources of variability in the corrosion image dataset. The 791 source images were collected over 36 weeks under laboratory conditions, but the lighting was not perfectly controlled across sessions. The measured luminance statistics in Section 5 confirm that real brightness differences of up to 2.55× exist in the original dataset. A classifier trained only on the original images has already seen this variation, but only from 48 specimens. Augmentation exposes the model to this variation across all specimens, including those that happen to appear in a narrow brightness range in the original data.

This technique is used in every published corrosion augmentation pipeline reviewed for this study, including PMC11829104 (EfficientNetB0 on tank corrosion) and PMC11175235 (CNN for steel corrosion detection).

### 7.3 Why it is label-preserving

Adjusting brightness or contrast does not change whether rust is present or how much of the surface it covers. The category of "moderate rust" is defined by the area of rust visible on the specimen, not by the absolute pixel brightness at which that rust is photographed. The class label is unchanged by this recipe.

### 7.4 Why it is appropriate for corrosion classification

The most important consequence of this recipe for this specific study is the following: the existing red-colour threshold classifier fails when lighting changes because the threshold is fixed. A brightness reduction of 20% can move pixels that should trigger the threshold outside the detection range. A brightness increase can cause non-rust concrete pixels to enter the range. The deep learning classifier trained with brightness augmentation learns to classify rust from texture, pattern, and relative colour, not from absolute brightness — which is the fundamental advantage that the journal paper must demonstrate.

### 7.5 Python implementation

The implementation uses two operations from the Pillow image processing library:

```python
brightness = float(rng.uniform(0.75, 1.28))
contrast   = float(rng.uniform(0.78, 1.25))

image = ImageEnhance.Brightness(image).enhance(brightness)
image = ImageEnhance.Contrast(image).enhance(contrast)
```

`ImageEnhance.Brightness` scales every pixel value by the brightness factor relative to a mid-grey reference, using Pillow's built-in implementation. `ImageEnhance.Contrast` blends the image with a greyscale copy of itself using the contrast factor as the blend weight. Both operations produce a result in valid 8-bit pixel range (0–255). The random number generator `rng` is seeded uniquely for each image and copy index, so the same parameters are reproduced exactly when the script is run again with the same seed.

### 7.6 Parameter range and justification

**Brightness range: [0.75, 1.28]**

This range was derived from the luminance measurements in Section 5. The calculation is as follows:

- The mean luminance of the dataset is 199.1.
- The 5th percentile is 145.4. The ratio of mean to 5th percentile is 199.1 / 145.4 = 1.37, meaning the average image is 37% brighter than the darkest 5% of images.
- The 95th percentile is 252.8. The ratio of 95th percentile to mean is 252.8 / 199.1 = 1.27, meaning the brightest 5% of images are 27% brighter than the average.

To simulate the same brightness range that already exists in the dataset, the augmentation must cover a factor of at least [1/1.37, 1.27] = [0.73, 1.27]. The chosen range [0.75, 1.28] matches this empirically derived requirement closely, rounding to two decimal places and slightly widening the lower bound to cover the extremes.

The ratio covered by this range is 1.28 / 0.75 = 1.71×, which is close to the measured 5th-to-95th percentile ratio of 1.74× and avoids the extreme minimum and maximum of the dataset (which may be atypical imaging conditions rather than typical variability).

The previous range of [0.85, 1.15] covered only 1.15 / 0.85 = 1.35×, which is substantially less than the real inter-image variability. This was identified as a calibration error and corrected.

**Contrast range: [0.78, 1.25]**

Contrast and brightness are correlated: images taken in low-light conditions tend to have lower contrast as well as lower overall brightness. The contrast range is set slightly narrower than the brightness range because aggressive contrast reduction (factor < 0.75) makes the image appear uniformly grey and destroys visual detail, while aggressive contrast increase (factor > 1.30) produces unnatural, over-sharpened results. The range [0.78, 1.25] represents a change of approximately ±22% from the neutral value of 1.0, which matches the literature norm of ±15–25% for contrast augmentation in industrial inspection studies.

> **Figure placeholder — Figure 5.** Strip showing one original corrosion image beside four augmented versions produced by this recipe with different brightness and contrast factors (e.g., 0.75, 0.90, 1.10, 1.28). Label each image with its factor values.

---

## 8. Recipe 2: Saturation and Colour Balance

### 8.1 What saturation means

Saturation describes how vivid or rich the colours in an image are. A fully saturated image has pure, intense colours. A fully desaturated image is greyscale — all colour information has been removed, and only light-and-dark differences remain.

In everyday terms: a photograph taken in bright sunlight tends to look more saturated (vivid colours); a photograph taken on an overcast day or under artificial lighting may look more desaturated (muted, washed-out colours). Rust is naturally an orange-red colour. Fresh rust tends to look vivid; old, dried rust tends to look brown and desaturated.

### 8.2 What colour balance means

Colour balance refers to the relative proportions of red, green, and blue light in an image. A camera's automatic white-balance system tries to make neutral surfaces (white concrete, for example) appear white regardless of the light source. However, different light sources have different colour temperatures, and white-balance algorithms are imperfect. This means the same specimen photographed under different lighting may appear slightly warmer (more red-yellow) or cooler (more blue) depending on the camera and conditions. Colour balance variation simulates this acquisition-to-acquisition variability.

### 8.3 What RGB gains mean

In this recipe, colour balance is adjusted by multiplying the red, green, and blue channels independently by small numerical factors called gains. A red gain of 1.03 increases the red channel by 3%; a green gain of 0.97 decreases the green channel by 3%. The three gains together shift the overall colour tint of the image.

Importantly, the three gains are normalised so that their average is exactly 1.0. This means the overall brightness of the image does not change when colour balance is adjusted — only the colour tint changes. Without normalisation, colour balance adjustment would also change brightness, which is handled separately by Recipe 1.

### 8.4 Why these techniques were selected

Camera white-balance differences across imaging sessions produce real colour shifts in the dataset. Saturation changes are motivated by two physical phenomena: (1) surface wetness, which can occur when specimens are sprayed during the corrosion acceleration experiment and which desaturates the rust colour temporarily; and (2) the natural colour evolution of rust from vivid orange-red (iron oxide formed recently) to dull brown (older, drier corrosion product). The classifier must learn to categorise rust by its coverage and distribution, not by whether it is fresh-vivid or aged-dull.

This technique family is used in PMC11829104 under the name "channel shift augmentation," which is equivalent to per-channel gain adjustment.

### 8.5 Why it is label-preserving

Neither saturation nor colour balance changes the area of rust visible on the surface. A specimen with 15% rust coverage in class 3 remains class 3 whether the rust looks orange-vivid or brown-muted. The label is unchanged.

### 8.6 Python implementation

```python
saturation = float(rng.uniform(0.78, 1.28))
image = ImageEnhance.Color(image).enhance(saturation)

# Colour balance: multiply each channel by a normalised gain
array = np.asarray(image, dtype=np.float32)
gains = rng.uniform(0.94, 1.06, size=3).astype(np.float32)
gains /= float(np.mean(gains))   # normalise: mean gain becomes exactly 1.0
balanced = np.clip(array * gains.reshape(1, 1, 3), 0, 255).astype(np.uint8)
image = Image.fromarray(balanced, mode="RGB")
```

`ImageEnhance.Color` is Pillow's saturation control. A value of 0 produces a greyscale image; a value of 1 leaves the image unchanged; values above 1 increase colour vividness. The per-channel gains are applied to a NumPy array representation of the image and clipped to the valid 8-bit range [0, 255].

### 8.7 Parameter range and justification

**Saturation range: [0.78, 1.28]**

A saturation factor of 0.78 reduces colour vividness by 22%, producing a noticeably desaturated but still clearly coloured image. A factor of 1.28 increases vividness by 28%, producing a somewhat richer-looking but physically plausible image. This range covers the typical variation introduced by white-balance differences, wetness effects, and the natural colour progression of rust, without producing unrealistically desaturated (near-greyscale) or unrealistically vivid images. The literature norm for saturation augmentation is ±20–30%, and the range [0.78, 1.28] corresponds to approximately ±25% relative to the neutral value of 1.0.

**RGB channel gains: [0.94, 1.06]**

The individual channel gains are sampled from [0.94, 1.06], representing a maximum per-channel change of 6% before normalisation. After normalisation, the effective per-channel change is slightly different (because one channel may go up while another goes down relative to their mean), but the range remains modest. This is intentionally much smaller than the brightness range because colour-balance variation in real camera systems is typically in the range of 2–8% per channel, and larger shifts produce unrealistic colour casts that are not representative of the imaging setup.

> **Figure placeholder — Figure 6.** Strip showing the effect of saturation variation (values 0.78, 0.90, 1.10, 1.28) on a single corrosion image. Also show one example with the colour balance shifted warm and one shifted cool.

---

## 9. Recipe 3: Gaussian Blur and Sensor Noise

### 9.1 What Gaussian blur is

Blur is the loss of sharpness in an image. A blurred image looks as if the camera was slightly out of focus, or as if the specimen was moving slightly during exposure. "Gaussian blur" is the most common type of blur used in image processing. The word "Gaussian" refers to the mathematical function that describes how much each pixel is averaged with its neighbours: pixels very close to the centre of a small region contribute more, while pixels at the edge contribute less, following the bell-shaped (Gaussian) curve.

The parameter sigma (σ) controls how strong the blur is. A sigma of 0.3 pixels is almost invisible — it just slightly softens sharp edges. A sigma of 1.5 pixels is noticeable: fine details become less crisp, but the overall image content remains clearly recognisable.

### 9.2 What Gaussian noise is

Noise in a digital image is a random variation in pixel values that does not represent real visual information. Camera sensors are not perfect: even photographing a flat white surface under constant lighting produces slightly different pixel values from one capture to the next because of thermal fluctuations in the sensor electronics. This is called sensor noise.

"Gaussian noise" means that the random fluctuation at each pixel follows a Gaussian (bell-shaped) distribution. Most pixels change only slightly, but a small number change more. The sigma parameter controls the typical size of the noise: a smaller sigma means most pixels change by only a few intensity values; a larger sigma means larger random variations.

### 9.3 Why these techniques were selected

Blur simulates focus variation and slight motion in the imaging setup. Different imaging sessions may have slightly different focus settings, slightly different distances between camera and specimen, or small vibrations during exposure. A classifier trained only on perfectly sharp images may fail on slightly blurred inputs. Adding mild blur during training teaches the model to identify rust patterns from the spatial structure of the colour distribution rather than from perfectly crisp edge details.

Noise simulates camera sensor variation. Images collected across 36 weeks of an experiment may use different camera sensitivity settings (ISO), different exposure times, or experience variation in sensor temperature. These all introduce slightly different noise levels in different imaging sessions. Noise augmentation teaches the model not to rely on fine-grained individual pixel values, which are unreliable, but on broader colour regions and pattern structures.

### 9.4 Why it is label-preserving

Blur and noise do not add, remove, or relocate rust on the specimen surface. They only change how the image looks at the pixel level, not what visual content it shows. A specimen showing 30% rust coverage before this recipe is applied shows 30% rust coverage after — it just looks slightly softer and slightly noisier. The class label is unchanged.

### 9.5 Why it does not destroy corrosion texture

The selected blur range (sigma 0.3 to 1.5 pixels) is very mild relative to the image size (2835 × 650 pixels). Even the maximum blur (sigma = 1.5) only blurs details at a scale of approximately 3–5 pixels, while the rust regions visible in these images span hundreds of pixels. The overall rust pattern remains clearly visible. Similarly, the noise levels selected are well below the threshold at which visual detail is obscured.

To illustrate: the darkest specimens in the dataset (D04 series, luminance 100.2) already exhibit significant pixel-level variability due to the dark rust colour and imaging conditions. The noise added by augmentation is comparable to this natural variation.

### 9.6 Python implementation

```python
blur_sigma  = float(rng.uniform(0.3, 1.5))
noise_sigma = float(rng.uniform(0.005, 0.035))

# Apply Gaussian blur
image = image.filter(ImageFilter.GaussianBlur(radius=blur_sigma))

# Apply Gaussian noise
array = np.asarray(image, dtype=np.float32) / 255.0   # normalise to [0, 1]
noise = rng.normal(0.0, noise_sigma, size=array.shape).astype(np.float32)
noisy = np.clip(array + noise, 0.0, 1.0)
image = Image.fromarray(np.rint(noisy * 255.0).astype(np.uint8), mode="RGB")
```

`ImageFilter.GaussianBlur(radius=blur_sigma)` applies Pillow's built-in Gaussian blur. The noise is added in the normalised [0, 1] colour space (where 0 is black and 1 is white) so that the sigma value has a consistent interpretation regardless of pixel value range. The `np.clip` operation ensures that no pixel value falls outside the valid range after noise is added.

### 9.7 Parameter range and justification

**Blur sigma range: [0.3, 1.5] pixels**

The literature standard for Gaussian blur augmentation in industrial inspection is sigma 0.1 to 2.0 pixels with a 5-pixel kernel. The chosen range [0.3, 1.5] covers the mild-to-moderate portion of this standard range, avoiding very strong blur (sigma > 2.0) that would make rust texture recognition difficult. The lower bound of 0.3 is barely perceptible but ensures some blur is always applied in this recipe. The upper bound of 1.5 is noticeable under close inspection but does not obscure the rust pattern.

**Noise sigma range: [0.005, 0.035] in normalised [0, 1] pixel space**

Converted to 8-bit pixel intensity values (multiplying by 255):

| Normalised sigma | Approximate 8-bit equivalent | Effect |
|---|---|---|
| 0.005 | 1.3 intensity levels | Nearly imperceptible |
| 0.020 | 5.1 intensity levels | Subtle grain, typical of moderate ISO |
| 0.035 | 8.9 intensity levels | Visible grain, similar to high ISO |

The chosen range (0.005–0.035) corresponds to a maximum random pixel variation of approximately 9 intensity levels (out of 255), which is comparable to real camera sensor noise at moderate to high ISO settings. The literature norm for Gaussian noise in normalised space is sigma 0.01–0.05. The chosen range [0.005, 0.035] is within this norm and avoids the highest reported values (0.04–0.05), which produce visually obvious grain.

> **Figure placeholder — Figure 7.** Strip showing the effect of blur (sigma 0.3, 0.8, 1.5) and noise (sigma 0.005, 0.02, 0.035) on a single corrosion image. The reader should see that even at maximum blur and noise, the rust pattern remains clearly identifiable.

---

## 10. Recipe 4: Combined Brightness, Contrast, and Saturation

### 10.1 What this recipe does

This recipe applies three separate photometric adjustments to the same image: brightness, contrast, and saturation are each modified independently. Unlike Recipes 1 and 2, which apply one or two transforms, this recipe deliberately combines all three to simulate compound photometric variation — for example, a session that is both darker than average and has lower contrast and desaturated colours.

### 10.2 Why the parameter range is narrower than in Recipes 1 and 2

When multiple augmentations are applied to the same image, their individual effects accumulate. If brightness is reduced by 25% and saturation is also reduced by 25%, the combined visual change is larger than either alone. With three independent transforms each at ±25%, the worst-case combination could produce a very dark, low-contrast, near-greyscale image that no longer resembles a realistic corrosion photograph.

To keep the augmented images within a realistic appearance range even when all three transforms coincide at their extremes, the parameter range for each individual transform is reduced. The chosen range [0.82, 1.18] represents a change of ±18% per transform, so the maximum compound effect is moderate.

The mathematical argument: three transforms each at a factor of 0.82 reduce the overall visual intensity by approximately 1 − (0.82)³ = 45%. Three transforms at 1.18 increase it by (1.18)³ − 1 = 64%. While these extremes can occur, they occur only when all three random samples happen to be near their respective extremes simultaneously, which is unlikely. In practice, the typical combined effect is much more moderate.

### 10.3 Why it is label-preserving

The same argument applies as for Recipes 1 and 2: photometric transforms do not change rust coverage. The classification label is unchanged.

### 10.4 Python implementation

```python
brightness = float(rng.uniform(0.82, 1.18))
contrast   = float(rng.uniform(0.82, 1.18))
saturation = float(rng.uniform(0.82, 1.18))

image = ImageEnhance.Brightness(image).enhance(brightness)
image = ImageEnhance.Contrast(image).enhance(contrast)
image = ImageEnhance.Color(image).enhance(saturation)
```

Each of the three factors is sampled independently from the same range. The operations are applied sequentially. This recipe represents "compound photometric effects" — situations where multiple sources of imaging variation coincide.

### 10.5 Parameter range summary

**Combined recipe range: [0.82, 1.18]**

This is narrower than the individual ranges in Recipes 1 and 2 (which go as low as 0.75 for brightness and 0.78 for contrast and saturation). The reduction is intentional: applying three transforms simultaneously requires more conservative individual ranges to keep the combined output within plausible visual limits.

> **Figure placeholder — Figure 8.** Strip showing four examples from this recipe, illustrating the range from a dark-low-contrast-desaturated result to a bright-high-contrast-vivid result, alongside the original image.

---

## 11. Recipe 5: Horizontal Flip with Brightness Variation

### 11.1 What horizontal flip does

A horizontal flip mirrors the image left-to-right. A rust patch that was on the left side of the specimen appears on the right side in the flipped image; a patch on the right appears on the left.

### 11.2 Why horizontal flip is label-preserving for this task

The classification target is `A_Total_Rust_Category_(1–4)`, which measures the **total fraction** of the visible surface covered by rust. This is a scalar quantity — it answers the question "how much rust?" not "where is the rust?" Whether a rust patch occupies the left half or the right half of the specimen does not change how much rust is present in total.

Therefore, horizontal flip does not change the class label. A specimen showing 20% total rust coverage is class 2 whether the rust is on the left or the right.

### 11.3 Why vertical flip was excluded

A vertical flip would show the specimen upside-down. The specimens in this dataset are ferrocement panels photographed horizontally in a fixed setup, with the specimen oriented consistently across all 791 images. An upside-down photograph is not a plausible imaging condition for this setup. Including it would add images that look unlike any image the classifier would encounter in real use, which could confuse the model rather than help it generalise.

### 11.4 Why large rotations were excluded

A rotation of more than approximately 10° would place empty space (or fill artefacts) in the corners of the image that do not represent real specimen content. For the long, narrow images in this dataset (2835 × 650 pixels), even a 5° rotation creates substantial areas at the image edges that must be filled with an artificial value. These fill artefacts can be learned as spurious classification signals. Large rotations also do not simulate plausible camera variability for a mounted, fixed imaging setup.

### 11.5 Why brightness variation is combined with the flip

A deterministic flip without any additional variation would produce a copy that is always identically mirror-symmetric to the original. Adding a small brightness variation [0.85, 1.15] ensures that each horizontal-flip copy is also slightly different in intensity from the original, increasing the diversity of the training set. The brightness range for this recipe is conservative (±15%) because the flip already provides strong spatial diversity; the brightness component is secondary.

### 11.6 Why it is appropriate for corrosion classification

Horizontal flip is the most universally used geometric augmentation in image classification. It is used in every major deep learning benchmark (ImageNet, CIFAR-10, CIFAR-100) and in virtually all published corrosion and defect detection studies, including PMC11829104 and PMC11175235. For this specific task, it is safe because the classification label is position-invariant.

### 11.7 Python implementation

```python
brightness = float(rng.uniform(0.85, 1.15))

image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
image = ImageEnhance.Brightness(image).enhance(brightness)

parameters.update(horizontal_flip=True, brightness=brightness)
```

`Image.Transpose.FLIP_LEFT_RIGHT` is Pillow's built-in horizontal flip operation. It is lossless: no interpolation is applied. The flip is always applied (not randomly); the brightness factor provides randomness. The CSV record stores `horizontal_flip=true` together with the sampled brightness value, so the augmentation is fully auditable.

> **Figure placeholder — Figure 9.** An original image shown beside its horizontally flipped version with two different brightness factors. The reader should see that rust coverage appears the same on both sides.

---

## 12. Rejected Augmentation Techniques

Several techniques commonly used in image classification were considered and excluded. The reasons for exclusion are given below.

**Table 4. Rejected augmentation techniques and reasons for exclusion.**

| Technique | Reason for exclusion |
|---|---|
| **MixUp** | Creates interpolated images between two training examples. The resulting label is also interpolated (e.g., 60% class 2 + 40% class 3). Discrete four-class severity labels cannot be meaningfully interpolated. The technique requires modifying the classifier's loss function to handle fractional labels, which is not part of the standard classification pipeline for this study. |
| **CutMix** | Pastes a rectangular region from one image into another and adjusts the label in proportion to the pasted area. A patch of rust-free concrete pasted into a severe-rust image produces a physically meaningless training example: the image shows mixed content, and the adjusted label is a fraction with no physical interpretation. |
| **GAN synthesis** | A Generative Adversarial Network could be trained to generate new synthetic corrosion images. However, classes 3 and 4 have only 20 and 14 training images respectively, which is far too few to train a stable generative model. GAN training on small datasets produces mode collapse (generating only a few similar images) or unstable outputs. The technique also requires weeks of additional implementation and training effort. |
| **Diffusion models** | Same argument as GAN: generating photorealistic corrosion images from fewer than 20 training examples per class is not currently feasible with standard diffusion models without a much larger base dataset for pre-training. |
| **Elastic deformation** | Warps the image as if the surface were made of elastic material. This technique was developed for medical image augmentation (histology slides, MRI scans), where tissue deformation is a real source of variability. A flat concrete slab photographed perpendicular to its surface does not deform. Elastic deformation is physically implausible for this dataset. |
| **Vertical flip** | Produces a photograph of the specimen upside-down. Not a plausible imaging condition for a fixed horizontal imaging setup. |
| **Large rotation (>±10°)** | Creates fill artefacts at image corners that do not represent real specimen content. The imaging setup is fixed; camera tilt beyond a few degrees is not a realistic source of variation. |
| **Heavy hue shift (>±10% on the hue circle)** | Hue is the colour direction (red, green, blue, yellow, etc.) independent of brightness. Moving rust from its orange-red hue by more than 10–18° on the hue circle produces yellow-rust or magenta-rust, which are not physically possible colours for corroded iron in concrete. |
| **Random erasing / Cutout** | Randomly blacks out a rectangular region of the image. If the erased region contains the primary rust pattern, the model receives an image labelled "moderate rust" that shows only concrete — a direct contradiction in the training data. This risk is highest for classes 3 and 4, which have limited rust coverage. |

---

## 13. Dataset Expansion Strategy

### 13.1 Original and augmented counts

**Table 5. Class distribution before and after augmentation.**

| Class | Original | Augmented copies | Total | Expansion |
|---|---|---|---|---|
| 1 (no/minimal rust) | 658 | 3,290 | 3,948 | 6× |
| 2 (mild rust) | 99 | 495 | 594 | 6× |
| 3 (moderate rust) | 20 | 100 | 120 | 6× |
| 4 (severe rust) | 14 | 70 | 84 | 6× |
| **Total** | **791** | **3,955** | **4,746** | **6×** |

Each original image receives exactly five augmented copies, one from each recipe. Together with the original, every source image contributes six rows to the dataset (6× expansion).

### 13.2 Literature evidence for the expansion factor

The choice of expansion factor was informed by the following published studies.

**Table 6. Literature evidence for expansion factors in comparable studies.**

| Study | Architecture | Original training size | Expansion factor | Augmentation method |
|---|---|---|---|---|
| PMC11829104 — Storage tank corrosion | EfficientNetB0 | ~800 images | **6.25×** | Offline |
| PMC11175235 — Steel corrosion detection | CNN | 100 images | **20×** | Offline |
| arXiv 1906.11887 — General classification survey | Various | Various | **2–3× recommended optimum** | Both |
| Steel defect detection studies | ResNet50, InceptionV3 | 800–2,400 | **3×** | Offline |
| DeiT (Touvron et al., 2021) — ImageNet | ViT | 1.2M | Online (very high) | Online |

The most directly comparable study is PMC11829104, which applies a 6.25× expansion to a corrosion dataset of similar size (approximately 800 images) and achieves 94% accuracy. The chosen expansion factor of 6× is consistent with this reference.

The general classification survey (arXiv 1906.11887) reports that the optimal augmentation rate for most classification tasks is 2–3×, with diminishing returns beyond this range. However, this recommendation is derived from studies with larger training sets. For datasets in the 100–1,000 image range — which matches this study's training partition — corrosion-specific studies consistently use 3–6×.

### 13.3 Why unlimited augmentation was avoided

The professor's email correctly notes that by combining transformations, the number of augmented images could be made arbitrarily large. The 6× factor was chosen for the following reasons:

1. **Diminishing returns.** The general survey (arXiv 1906.11887) and practical experience with corrosion studies both indicate that augmentation beyond 6–10× provides minimal additional accuracy benefit while increasing training time proportionally. There is no scientific justification for generating 50× or 100× expansion when 6× captures the essential diversity of the available transformation families.

2. **Interpretability.** A 6× expansion means that each of the five recipes is applied exactly once per source image, producing one augmented copy per recipe. This is easy to explain and audit: the dataset contains exactly the augmented diversity provided by the five chosen recipes, with no recipe repeated.

3. **Offline storage.** The five augmented copies of 791 images already produce 3,955 augmented files. Storing 10× or 20× would require proportionally more disk space without proportional scientific benefit.

4. **Consistency with the best available comparable study.** PMC11829104 uses 6.25× on a dataset of comparable size. Matching this reference provides a strong literature basis for the chosen factor.

### 13.4 Splitting: augmented images stay in the training partition only

A critical rule for correct use of the augmented dataset is that augmented images must only appear in the training partition. The validation and test partitions must contain only original, unaugmented images. This ensures that model performance is evaluated on images that look exactly like real-world acquisition conditions.

Furthermore, all images from the same specimen (original and augmented) must remain in the same partition. This prevents the model from learning to recognise individual specimens by their characteristic rust patterns, rather than learning to classify rust severity in general.

These rules are enforced by the split manifests produced by `augmentation/make_splits.py`. The augmented CSV contains a `specimen_id` column and an `is_augmented` column on every row to facilitate this split construction.

---

## 14. Reproducibility and Provenance

### 14.1 Deterministic random seed

Every augmented image is generated using a reproducible random number derived from three inputs: (1) the global seed (20260630), (2) the source image filename, and (3) the copy index. The derivation uses the SHA-256 cryptographic hash function:

```python
material = f"{seed}|{image_name}|{augmentation_index}".encode("utf-8")
digest   = hashlib.sha256(material).digest()
derived_seed = int.from_bytes(digest[:8], byteorder="big", signed=False)
rng = np.random.default_rng(derived_seed)
```

This means that running the script again with the same global seed always produces the same augmented images. The order in which images are processed (which may vary due to parallel execution) does not affect the result, because each image has its own independent random stream.

### 14.2 Provenance metadata

Every row in the augmented CSV records:

- `original_image_name`: the filename of the source image
- `augmented_image_name`: the filename of the augmented image
- `augmentation_type`: the name of the recipe applied
- `augmentation_parameters`: the exact numerical values sampled for this copy
- `is_augmented`: whether the row is an original or an augmented copy
- `specimen_id`: the specimen identifier (used for split construction)
- `label`: the validated classification label (preserved unchanged from the source)

**Example provenance record for a flip augmentation:**

```
original_image_name:       D01-20240110-0W.png
augmented_image_name:      D01-20240110-0W_aug05_horizontal_flip_brightness.png
augmentation_type:         horizontal_flip_brightness
augmentation_parameters:   brightness=0.874061;horizontal_flip=true
is_augmented:              True
specimen_id:               D01
label:                     1
```

### 14.3 Reproduction command

The complete augmented dataset can be regenerated from scratch with the following command, executed from the repository root:

```bash
python augmentation/augment_dataset.py --copies 5 --seed 20260630 --overwrite
```

---

## 15. Summary of the Augmentation Pipeline

### 15.1 Complete recipe table

**Table 7. All five augmentation recipes with parameters and justification.**

| Recipe | Transforms applied | Parameter range | Literature basis | Expected effect |
|---|---|---|---|---|
| 1. Brightness and contrast | Brightness, contrast | Brightness [0.75, 1.28], contrast [0.78, 1.25] | PMC11829104; measured dataset luminance range (ratio 1.74×) | Simulates lighting variation across imaging sessions; calibrated to measured dataset variability |
| 2. Saturation and colour balance | Saturation, per-channel RGB gains | Saturation [0.78, 1.28], gains [0.94, 1.06] | PMC11829104 channel shifts; camera white-balance literature | Simulates white-balance differences and surface-wetness effects |
| 3. Blur and noise | Gaussian blur, Gaussian noise | Blur sigma [0.3, 1.5] px, noise sigma [0.005, 0.035] | Industrial inspection literature; DeiT protocol | Simulates focus variation and camera sensor noise |
| 4. Combined photometric | Brightness + contrast + saturation | Each [0.82, 1.18] | General augmentation literature; conservative range for compound effects | Simulates simultaneous multi-factor photometric variability |
| 5. Horizontal flip + brightness | Flip left-right, brightness | Brightness [0.85, 1.15] | Universal in classification literature; PMC11829104; PMC11175235 | Adds spatial diversity; label-safe because total rust coverage is position-invariant |

### 15.2 Dataset size summary

**Table 8. Final augmented dataset statistics.**

| Quantity | Value |
|---|---|
| Source images | 791 |
| Augmented copies per source image | 5 (one per recipe) |
| Total images in the augmented dataset | 4,746 |
| Total expansion factor | 6× |
| Training partition (approx.) | 3,846 rows (38 specimens: originals + 5 augmented copies) |
| Validation partition (approx.) | 75 rows (5 specimens, originals only) |
| Test partition (approx.) | 75 rows (5 specimens, originals only) |
| Augmented rows excluded from val/test | 750 rows |
| Random seed | 20260630 |

### 15.3 Technique families covered

**Table 9. Correspondence between professor's specified technique families and implemented recipes.**

| Professor's specified family | Recipe that covers it |
|---|---|
| Brightness | Recipes 1, 4, and 5 |
| Contrast | Recipes 1 and 4 |
| Colour balance | Recipe 2 (channel gains) |
| Blur | Recipe 3 |
| Noise | Recipe 3 |
| "Other similar variations" | Recipe 4 (compound combination), Recipe 5 (geometric + photometric) |

All five families specified by the professor are covered. Recipe 5 (horizontal flip) was added as it is universally established for classification tasks and is label-safe for this specific target variable.

> **Figure placeholder — Figure 10.** Contact sheet showing one example from each of the four severity classes (rows), with the original image and all five augmented copies (columns). This is the main visual summary of the augmentation pipeline. The contact sheet is automatically generated and saved to `Documentation/augmentation_examples.png`.

---

## 16. Limitations

### 16.1 Offline augmentation fixes the diversity at 5 copies per source image

The current pipeline applies each recipe exactly once per source image, producing five fixed augmented copies. Online augmentation (generating new random parameters at each training epoch) would provide far more variety: across 100 training epochs, an online pipeline would produce 100 different random combinations per source image rather than 5. The offline approach was chosen because it produces a stable, auditable, reproducible dataset that can be inspected, shared, and archived; but it provides less diversity per recipe than online augmentation would.

### 16.2 Class imbalance is preserved

The 6× expansion multiplies all classes equally. Class 1 remains the dominant class (83.2% of images). Augmentation does not correct the class imbalance; it only preserves it at a larger scale. The downstream classifier must use class-weighted loss functions, oversampling, or other imbalance-correction techniques during training. This is standard practice and not specific to augmentation, but it must be noted.

### 16.3 Augmentation parameters are not optimised by experiment

The parameter ranges are calibrated to empirically measured dataset statistics (for brightness and contrast) and to literature norms (for all recipes). However, the optimal ranges for this specific dataset and task have not been determined by ablation experiments. It is possible that different ranges would produce better or worse results. The ablation study described in the journal research plan will quantify the sensitivity of model performance to parameter range choice.

### 16.4 Geometric diversity is limited

The pipeline includes only one geometric augmentation: horizontal flip. Small rotations, random crops, and perspective distortions are in principle applicable and could add geometric diversity that photometric transforms cannot provide. These were deferred to ablation experiments rather than included in the primary pipeline, because the training-time crop from 2835×650 pixels to 224×224 pixels already introduces a form of spatial diversity (different crop positions expose different sections of the specimen), and because adding more geometric transforms at the dataset-preparation stage would increase complexity.

### 16.5 No augmentation of class-specific visual features

All recipes apply the same augmentation regardless of which class the image belongs to. In principle, class-specific augmentation could be designed: for example, brightening could be applied more aggressively to dark images (which tend to be in the later rust stages) and less aggressively to already-bright images (which tend to be in the early, low-rust stage). This level of class-adaptive augmentation is beyond the scope of the dataset-preparation phase.

---

## 17. Future Work

### 17.1 Online augmentation study

The augmented dataset in its current form is an offline deliverable: augmented images are pre-generated and saved as files. An alternative and potentially more powerful approach is online augmentation, where random transformations are applied to each training image at every epoch during model training. Online augmentation produces far more diverse training examples because the random parameters change at every epoch. A comparison study between the offline (5 fixed copies) and online (unlimited) augmentation approaches would quantify whether the additional diversity from online augmentation produces measurable improvements in classification accuracy for this dataset.

### 17.2 Ablation studies

The journal research plan includes three ablation studies:

- **Ablation 1 — individual transform contribution:** Remove one recipe at a time and measure the resulting change in balanced accuracy. This will identify which of the five recipes contributes most to model performance and allow informed decisions about simplifying the pipeline if needed.
- **Ablation 2 — parameter range intensity:** Compare three intensity levels (conservative, standard, aggressive) for the photometric recipes. This will answer the question of whether the calibrated parameter ranges are approximately correct or whether the model benefits from wider or narrower ranges.
- **Ablation 3 — fine-tuning depth:** Compare training only the classification head versus full model fine-tuning for both ResNet50 and ViT. This will quantify how much of the improvement from augmentation comes from better representation learning versus better classifier calibration.

### 17.3 ResNet50 and Vision Transformer comparison

The complete experimental protocol compares five conditions: the red-colour baseline (C1), ResNet50 without augmentation (C2), ResNet50 with augmentation (C3), ViT without augmentation (C4), and ViT with augmentation (C5). The primary expected findings are that both augmented models (C3, C5) outperform the baseline (C1), and that the ViT benefits more from augmentation than ResNet50 because it lacks the spatial inductive biases of convolutional architectures. The augmented dataset prepared in this phase is the training resource for all five conditions.

### 17.4 Robustness experiment

A planned experiment will evaluate all five conditions on artificially brightness-perturbed test sets (±10%, ±20%, ±30%). The expected result is that the red-colour baseline degrades sharply under brightness perturbation while the augmented deep learning models maintain stable accuracy. This experiment is the strongest single demonstration of the advantage of augmentation for this specific dataset and classification task.

### 17.5 Advanced generative augmentation

For classes 3 and 4 (20 and 14 original images respectively), more aggressive expansion might be warranted. Once the journal paper experiments are complete and the moderate-severity specimens are better understood, a generative approach (diffusion model fine-tuned on a larger corrosion dataset, or style transfer) could be explored as a supplementary expansion for the rarest classes. This is outside the current scope and requires careful label validation to ensure that synthetic images are consistent with the severity class boundaries.

---

## 18. References

1. **PMC11829104** — Deep neural networks for external corrosion classification on above-ground storage tanks. EfficientNetB0; ~800 images augmented to ~5,000 (6.25×); offline augmentation; 94% accuracy. PubMed Central, 2025.

2. **PMC11175235** — Autonomous detection of corrosion in steel structures. CNN; 100 training images expanded 20× using horizontal flip, vertical flip, translation, and grid distortion. PubMed Central, 2024.

3. **Touvron et al., 2021 (DeiT)** — Training data-efficient image transformers and distillation through attention. Meta AI, arXiv 2012.12877. Establishes that Vision Transformers require strong augmentation to reach CNN-level performance on moderate-scale datasets.

4. **arXiv 1906.11887** — A preliminary study on data augmentation for image classification. Reports that 2–3× is the optimal augmentation rate for typical classification benchmarks; higher rates provide diminishing accuracy returns.

5. **MDPI Electronics 2024 (Hybrid-DC)** — Hybrid ResNet50 and Vision Transformer architecture for steel surface defect classification; 0.9944 validation accuracy. Direct precedent for using both architectures together.

6. **MDPI Applied Sciences 2022** — Vision Transformer in industrial visual inspection. Confirms that "CNNs are often safer in smaller or medium-sized data settings because their inductive bias helps them learn useful structure more efficiently" and that ViTs require augmentation on small datasets.

7. **arXiv 2302.03751** — Understanding why ViT trains badly on small datasets. Documents the structural reasons for ViT's small-dataset limitation and the role of augmentation in addressing it.

8. **YOLOv8n-cls for four-class corrosion severity** — Applied to hydraulic steel structures; confirms that four-class severity classification is an established and achievable task with transfer learning.

---

*End of report.*

*Python library versions used for dataset generation:*
- Python ≥ 3.10
- Pillow ≥ 10.0
- NumPy ≥ 1.24
- openpyxl ≥ 3.1

*Full reproduction command:*
```bash
python augmentation/augment_dataset.py --copies 5 --seed 20260630 --overwrite
```

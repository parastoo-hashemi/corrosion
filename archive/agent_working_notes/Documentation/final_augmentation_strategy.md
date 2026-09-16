# Final Augmentation Strategy
## Four-Class Corrosion Severity Classification Dataset

> **Scope:** Offline dataset preparation for the corrosion classification study (Nissrine, Gerardo, Parastoo).
> **Responsibility:** Parastoo's task — prepare the augmented dataset only. No model training here.
> **Based on:** `Documentation/augmentation_journal_plan.md`, `Documentation/codex/augmentation_dataset_report.md`, `augmentation/augment_dataset.py`, pixel statistics measured from actual images.
> **Date:** 2026-06-30

---

## What Exists Now

The current pipeline (`augmentation/augment_dataset.py`) produced:

| Item | Value |
|---|---|
| Original images | 791 (1 corrupted excluded) |
| Augmented copies per original | 4 |
| Total images | 3,955 (5× expansion) |
| Recipes | `brightness_contrast`, `saturation_colour_balance`, `gaussian_blur_noise`, `brightness_contrast_saturation` |
| Brightness/contrast/saturation range | ±15% (factor 0.85–1.15) |
| Blur sigma | 0.3–1.2 |
| Noise sigma | 0.005–0.02 |
| Geometric augmentation | None |

---

## Empirical Calibration — Measured Dataset Variation

The parameter ranges must be calibrated against the actual brightness variation in the 791 source images. Measured from all 791 images:

| Metric | Value |
|---|---|
| Mean luminance | 199.1 |
| Min luminance (darkest image) | 98.1 |
| Max luminance (brightest image) | 255.0 |
| Real-world brightness ratio (max/min) | **2.60×** |
| 5th percentile luminance | 144.8 |
| 95th percentile luminance | 253.1 |
| 5th–95th percentile ratio | **1.75×** |
| Mean/5th percentile ratio | 199.1/144.8 = **0.73** (27% below mean) |
| 95th percentile/mean ratio | 253.1/199.1 = **1.27** (27% above mean) |

**Critical finding:** The real inter-image brightness variation spans a 5th–95th percentile ratio of **1.75×**. The current augmentation covers only **1.35×** (0.85–1.15). The current parameters are substantially undershooting the actual acquisition variation present in the dataset. A range of [0.75, 1.28] is needed to cover the realistic 5th–95th percentile span of the dataset's own brightness distribution.

This is the primary empirical justification for widening the brightness and contrast parameter ranges. It is not an aggressive choice — it is calibration to reality.

---

## Decision 1 — What Is Already Sufficiently Justified

The four existing recipes cover all five of the professor's specified technique families:

| Professor's family | Covered by recipe |
|---|---|
| Brightness | `brightness_contrast` (recipe 1), `brightness_contrast_saturation` (recipe 4) |
| Contrast | `brightness_contrast` (recipe 1), `brightness_contrast_saturation` (recipe 4) |
| Colour balance | `saturation_colour_balance` (recipe 2, channel gains) |
| Blur | `gaussian_blur_noise` (recipe 3) |
| Noise | `gaussian_blur_noise` (recipe 3) |

**The technique families are fully covered. No new family is strictly required.**

However, the parameter ranges for brightness, contrast, and saturation are calibrated too conservatively relative to the real dataset variation. This is a calibration problem, not a technique-selection problem.

---

## Decision 2 — What Is Optional But Scientifically Defensible

### 2a — Widen parameter ranges (recommended)

| Transform | Current range | Proposed range | Justification |
|---|---|---|---|
| Brightness | [0.85, 1.15] | **[0.75, 1.28]** | Covers actual 5th–95th percentile inter-image variation (luminance ratio 1.75×); current ±15% covers only 1.35× |
| Contrast | [0.85, 1.15] | **[0.78, 1.25]** | Real contrast variation tracks luminance variation; ±22% more representative |
| Saturation | [0.85, 1.15] | **[0.78, 1.28]** | Camera WB variation and surface wetness produce larger saturation shifts than ±15% |
| RGB channel gains | [0.97, 1.03] | **[0.94, 1.06]** | Per-channel WB shifts; slightly larger range represents real sensor variation |
| Blur sigma | [0.3, 1.2] | **[0.3, 1.5]** | Literature standard is 0.5–1.5; extending upper bound modestly |
| Noise sigma | [0.005, 0.02] | **[0.005, 0.035]** | Literature norm for Gaussian noise on normalised images is 0.01–0.05; current is at lower end |
| Combined recipe | [0.90, 1.10] | **[0.82, 1.18]** | Mild joint variation; wider to match individual recipe expansions |

### 2b — Horizontal flip (recommended)

**What it does:** Mirrors the image left-to-right.

**Why it is label-safe:** The classification target is `A_Total_Rust_Category_(1–4)` — total rust coverage fraction converted to a severity class. Total coverage is invariant to left-right reflection. The class of a specimen with 12% total rust coverage is "mild" (class 2) regardless of which side the rust appears on.

**Why it adds value:** Horizontal flip effectively doubles training variety for any spatial feature that is not position-dependent. This is well-established in corrosion and defect detection literature (used in PMC11829104, PMC11175235, and essentially all general-purpose classification pipelines).

**Why the original pipeline excluded it:** The dataset report states the initial run omitted geometric transforms "without introducing location or border-fill questions." For total-rust-category classification, the location question does not apply. The flip is safe.

**Implementation note:** Combine the flip with a mild photometric variation so that each copy remains randomly distinct (a bare deterministic flip of the same image is not a randomly augmented sample; it is a fixed copy).

---

## Decision 3 — What Is Too Risky

These are excluded from the final dataset and from any ablation study at the dataset-preparation stage.

| Transform | Reason |
|---|---|
| **Random erasing / Cutout** | Removes real rust pixels while the class label stays unchanged. For specimens in class 2 (mild rust, ~3–8% coverage), erasing the rust region produces a blank concrete image labelled "mild" — a direct contradiction that corrupts the training signal. |
| **MixUp / CutMix** | Produces fractional class labels (e.g., 60% class-1 + 40% class-2). Categorical four-class labels cannot be interpolated meaningfully. Requires soft label training, which is not part of the standard classification pipeline for this study. |
| **GAN / diffusion synthesis** | Requires a separate generative model trained on <800 images per class. With 14–20 images in classes 3 and 4, GAN training will collapse. Not among the professor's techniques. Future work only. |
| **Vertical flip** | Produces an upside-down concrete slab. Not a physically plausible acquisition condition for specimens photographed horizontally in a fixed setup. Zero scientific justification for this dataset. |
| **Large rotation (>±10°)** | Creates large fill regions at image corners. At large angles, fill artefacts occupy a significant fraction of the resized 224×224 crop used during training. Not a plausible camera variation for a mounted imaging system. |
| **Hue shift > ±0.1** | Moves rust-coloured pixels outside their plausible hue range (rust appears green or purple at large shifts). Not a realistic acquisition variation. |
| **Elastic deformation** | Physically implausible for a flat concrete surface photographed perpendicularly. Domain: medical histology and MRI. Not applicable here. |

---

## Decision 4 — What Should Be in the Final Deliverable

### Final recipe set — 5 recipes, 6× expansion

| Recipe name | Transforms | Parameter ranges | Justification |
|---|---|---|---|
| `brightness_contrast` | Brightness + contrast | Brightness [0.75, 1.28], contrast [0.78, 1.25] | Core professor-specified families; widened to cover real dataset luminance variation |
| `saturation_colour_balance` | Saturation + per-channel gains | Saturation [0.78, 1.28], gains [0.94, 1.06] | Covers colour balance family; wider range reflects real WB and wetness variation |
| `gaussian_blur_noise` | Gaussian blur + Gaussian noise | Blur sigma [0.3, 1.5], noise sigma [0.005, 0.035] | Covers blur and noise families; upper bounds extended to literature norms |
| `brightness_contrast_saturation` | Brightness + contrast + saturation combined | Each [0.82, 1.18] | Joint photometric variation; represents compound acquisition effects |
| `horizontal_flip_brightness` | Horizontal flip + brightness | Flip (deterministic) + brightness [0.85, 1.15] | First geometric augmentation; label-safe for total-rust-category; adds spatial diversity; combined with brightness to ensure each copy is randomly distinct |

**Dataset output:**

| Quantity | Value |
|---|---|
| Original images (preserved) | 791 |
| Augmented copies per original | 5 |
| Total images | **4,746** |
| Expansion factor | **6×** |
| Command | `python augmentation/augment_dataset.py --copies 5 --overwrite --seed 20260630` |

**Class distribution after expansion:**

| Label | Original | Augmented | Total |
|---|---|---|---|
| 1 (no/minimal rust) | 658 | 3,290 | 3,948 |
| 2 (mild rust) | 99 | 495 | 594 |
| 3 (moderate rust) | 20 | 100 | 120 |
| 4 (severe rust) | 14 | 70 | 84 |
| **Total** | **791** | **3,955** | **4,746** |

Note: augmentation preserves the class imbalance present in the original dataset. Class weighting in the downstream classifier (not the dataset) is the correct way to address imbalance.

---

## Decision 5 — What Should Be Left for Ablation Studies

These transforms are scientifically defensible but are not included in the primary deliverable because they introduce additional complexity without a clear gain for the dataset-preparation stage. They belong in the training-time ablation experiments described in `augmentation_journal_plan.md`.

| Transform | Why deferred |
|---|---|
| **Small rotation (±5°, reflect fill)** | Plausible camera variation; label-safe; but requires careful fill-mode implementation to avoid black corners. Adds code complexity for modest diversity gain given that flip is already included. Best tested at training time using torchvision RandomRotation. |
| **Hue shift (±0.05)** | Small hue shifts are scientifically defensible; but rust hue is a key discriminant for the red-color baseline. Including hue variation in the ablation will reveal whether the DL model is relying on hue; valuable as a diagnostic, not as a standard recipe. |
| **Online augmentation** | More diverse than offline; produces a new random combination per training epoch. The offline dataset is the deliverable here; online augmentation is a training-time choice for the downstream classifier team. |
| **Wider brightness (>±30%)** | At >30%, darkening can make class-1 images appear rust-coloured to the red-color threshold. Safe for DL label but could create misleading visuals. Leave for ablation to verify the boundary. |

---

## Final Augmentation Recipe — Summary

```
FINAL RECIPE SET (5 recipes, --copies 5, 6x expansion)

Recipe 1: brightness_contrast
  brightness:  U[0.75, 1.28]   ← widened from [0.85, 1.15]
  contrast:    U[0.78, 1.25]   ← widened from [0.85, 1.15]

Recipe 2: saturation_colour_balance
  saturation:  U[0.78, 1.28]   ← widened from [0.85, 1.15]
  rgb_gains:   U[0.94, 1.06]   ← widened from [0.97, 1.03], mean-normalised

Recipe 3: gaussian_blur_noise
  blur_sigma:  U[0.30, 1.50]   ← extended upper bound from 1.2
  noise_sigma: U[0.005, 0.035] ← extended upper bound from 0.02

Recipe 4: brightness_contrast_saturation
  brightness:  U[0.82, 1.18]   ← widened from [0.90, 1.10]
  contrast:    U[0.82, 1.18]   ← widened from [0.90, 1.10]
  saturation:  U[0.82, 1.18]   ← widened from [0.90, 1.10]

Recipe 5: horizontal_flip_brightness  ← NEW
  flip:        FLIP_LEFT_RIGHT (deterministic)
  brightness:  U[0.85, 1.15]
```

**Command to regenerate:**
```bash
python augmentation/augment_dataset.py --copies 5 --seed 20260630 --overwrite
```

---

## Codex Prompt

Copy everything below the horizontal rule and paste it into Codex as the complete task specification.

---

```
TASK: Extend the corrosion image augmentation pipeline.

FILE TO MODIFY: augmentation/augment_dataset.py
DO NOT MODIFY: Data/Images_dataset (source images)
DO NOT MODIFY: Data/Images_Dataset_A-Z-1.xlsx (source workbook)
OUTPUT: Data/Images_dataset_augmented (will be regenerated with --overwrite)
OUTPUT: Data/Images_Dataset_A-Z-1_augmented.csv
OUTPUT: Documentation/augmentation_dataset_report.md
OUTPUT: Documentation/codex/augmentation_dataset_report.md
OUTPUT: Documentation/augmentation_examples.png

---

BACKGROUND

The existing script produces a 5x offline augmentation dataset (4 copies per original image)
using four photometric recipes. The task is to:

1. Add a fifth recipe: horizontal_flip_brightness
2. Widen the parameter ranges for the four existing recipes to better represent the actual
   inter-image brightness variation measured in the dataset (real range: luminance 98–255,
   ratio 2.60x; the current +/-15% covers only 1.35x of that range)
3. Update RECIPE_NAMES to include the new recipe
4. Update the report template text to describe all five recipes accurately
5. Update the contact sheet column count so it shows up to 5 augmented columns

Running the modified script with --copies 5 --overwrite --seed 20260630 must produce a
6x dataset (1 original + 5 augmented copies per image = 4746 total images from 791 originals).

Do not change: the audit logic, the CSV structure, the provenance fields, the label
validation, the specimen_id handling, the staging-directory pattern, the report structure,
or the argument parser defaults (keep --copies default at 4 so the existing 4-recipe
invocation still works correctly for users who do not pass --copies).

---

CHANGE 1: Update RECIPE_NAMES

Current:
    RECIPE_NAMES = (
        "brightness_contrast",
        "saturation_colour_balance",
        "gaussian_blur_noise",
        "brightness_contrast_saturation",
    )

Replace with:
    RECIPE_NAMES = (
        "brightness_contrast",
        "saturation_colour_balance",
        "gaussian_blur_noise",
        "brightness_contrast_saturation",
        "horizontal_flip_brightness",
    )

---

CHANGE 2: Update apply_recipe — widen existing parameter ranges and add new recipe

In the apply_recipe function, make the following changes to each branch:

Branch "brightness_contrast":
    Change: rng.uniform(0.85, 1.15) for both brightness and contrast
    To:     brightness = float(rng.uniform(0.75, 1.28))
            contrast   = float(rng.uniform(0.78, 1.25))

Branch "saturation_colour_balance":
    Change: rng.uniform(0.85, 1.15) for saturation
    To:     saturation = float(rng.uniform(0.78, 1.28))

    Change: rng.uniform(0.97, 1.03, size=3) for channel gains in adjust_colour_balance
    But adjust_colour_balance is a separate function — do NOT modify it from within
    apply_recipe. Instead, modify the default gain range inside adjust_colour_balance:
    Change: gains = rng.uniform(0.97, 1.03, size=3)
    To:     gains = rng.uniform(0.94, 1.06, size=3)

Branch "gaussian_blur_noise":
    Change: blur_sigma  = float(rng.uniform(0.3, 1.2))
    To:     blur_sigma  = float(rng.uniform(0.3, 1.5))

    Change: noise_sigma = float(rng.uniform(0.005, 0.02))
    To:     noise_sigma = float(rng.uniform(0.005, 0.035))

Branch "brightness_contrast_saturation":
    Change: rng.uniform(0.90, 1.10) for all three factors
    To:     brightness = float(rng.uniform(0.82, 1.18))
            contrast   = float(rng.uniform(0.82, 1.18))
            saturation = float(rng.uniform(0.82, 1.18))

Add new branch "horizontal_flip_brightness" BEFORE the final else clause:
    elif recipe_name == "horizontal_flip_brightness":
        brightness = float(rng.uniform(0.85, 1.15))
        image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        image = ImageEnhance.Brightness(image).enhance(brightness)
        parameters.update(horizontal_flip=True, brightness=brightness)

For the serialise_parameters function: the value horizontal_flip=True is a bool, not a
float. Serialise it as the string "true" rather than attempting float conversion.
Update serialise_parameters so that bool values are serialised as "true"/"false" strings
instead of going through float():

    def serialise_parameters(parameters: dict[str, Any]) -> str:
        parts = []
        for key in sorted(parameters):
            value = parameters[key]
            if isinstance(value, list):
                text = "[" + ",".join(f"{float(item):.6f}" for item in value) + "]"
            elif isinstance(value, bool):
                text = "true" if value else "false"
            else:
                text = f"{float(value):.6f}"
            parts.append(f"{key}={text}")
        return ";".join(parts)

---

CHANGE 3: Update contact sheet column count

Current:
    columns = ["original"] + [
        f"aug{index:02d}" for index in range(1, min(copies, 4) + 1)
    ]

Replace with:
    columns = ["original"] + [
        f"aug{index:02d}" for index in range(1, min(copies, 5) + 1)
    ]

The corresponding loop that reads image names uses the same variable `columns` and works
correctly because `names` is built from the same range. No further change needed there.

---

CHANGE 4: Update create_report_text — recipe description block

Find the section of the report template that reads:

    The default four copies use conservative, label-preserving recipes:

    1. `brightness_contrast`: brightness and contrast factors independently sampled from `[0.85, 1.15]`.
    2. `saturation_colour_balance`: saturation factor from `[0.85, 1.15]`; small normalized RGB channel gains from `[0.97, 1.03]`.
    3. `gaussian_blur_noise`: Gaussian blur sigma from `[0.3, 1.2]` pixels and Gaussian noise sigma from `[0.005, 0.02]` in normalized `[0, 1]` RGB space.
    4. `brightness_contrast_saturation`: combined mild factors independently sampled from `[0.90, 1.10]`.

    No MixUp, CutMix, GAN/diffusion, elastic deformation, random erasing/cutout, large rotation, heavy hue shift, horizontal flip, or rotation was applied. The optional geometric transformations were omitted because the requested photometric set already supplies a conservative 5x offline dataset without introducing location or border-fill questions.

Replace with:

    The five augmentation recipes use label-preserving transforms. Parameter ranges are
    calibrated to the measured inter-image luminance variation in the source dataset
    (luminance range 98–255; 5th–95th percentile ratio 1.75x; real-world brightest-to-
    darkest ratio 2.60x). The previous conservative [0.85, 1.15] range covered only 1.35x
    of that variation and was widened accordingly.

    1. `brightness_contrast`: brightness sampled from `[0.75, 1.28]`, contrast from `[0.78, 1.25]`. Calibrated to the real inter-image brightness distribution.
    2. `saturation_colour_balance`: saturation from `[0.78, 1.28]`; normalized per-channel RGB gains from `[0.94, 1.06]`. Simulates camera white-balance and surface-wetness variation.
    3. `gaussian_blur_noise`: Gaussian blur sigma from `[0.3, 1.5]` pixels; Gaussian noise sigma from `[0.005, 0.035]` in normalized `[0, 1]` RGB space. Simulates focus variation and sensor noise.
    4. `brightness_contrast_saturation`: brightness, contrast, and saturation each independently sampled from `[0.82, 1.18]`. Represents compound photometric effects.
    5. `horizontal_flip_brightness`: image mirrored left-to-right (label-safe for total-rust-category classification, which is position-invariant), combined with brightness from `[0.85, 1.15]`. First geometric augmentation; adds spatial diversity without altering rust-coverage class.

    Excluded: MixUp, CutMix, GAN/diffusion synthesis, elastic deformation, random erasing,
    vertical flip, large rotation (>10°), and heavy hue shifts (>0.1). These were excluded
    because they corrupt label integrity, are physically implausible for this imaging setup,
    or require infrastructure (generative models) outside the scope of this dataset.

---

VERIFICATION

After making the changes, confirm the following without running the script:

1. RECIPE_NAMES has exactly 5 entries.
2. apply_recipe handles all 5 recipe names and raises ValueError for unknown names.
3. serialise_parameters handles bool values without calling float() on them.
4. adjust_colour_balance uses gains from [0.94, 1.06] not [0.97, 1.03].
5. The report template describes exactly 5 recipes with the new parameter ranges.
6. The contact sheet shows min(copies, 5) augmented columns, not min(copies, 4).

To regenerate the final augmented dataset, run from the project root:

    python augmentation/augment_dataset.py --copies 5 --seed 20260630 --overwrite

Expected output:
    Original images:    791
    Augmented copies:   3955 (5 per original)
    Total images:       4746
    Expansion factor:   6x
```

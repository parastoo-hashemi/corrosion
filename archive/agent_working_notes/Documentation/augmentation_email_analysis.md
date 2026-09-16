# Professor Email Analysis — Data Augmentation
## Ambiguities, Critical Questions, and Task-Dependent Strategy

> **Based on:** Professor's email (received 2026-06-29), `Documentation/augmentation_objective_decision.md`
> **Date:** 2026-06-29

---

## 1. Precise Reading of the Email

Before identifying ambiguities, every sentence must be read as written — not as assumed.

**Sentence 1:**
> *"We would like to work on data augmentation for the image dataset."*

"We" is the research group, not Parastoo alone. "The image dataset" refers to the corrosion specimen image collection (`Data/Images_dataset/`). The work is collaborative in scope, even if the implementation assignment falls on Parastoo.

**Sentence 2:**
> *"The idea is to use the images we already have and apply standard augmentation techniques to increase the size and variability of the dataset."*

Two goals are stated: (a) increase dataset **size** (more training samples), and (b) increase **variability** (more diverse training inputs). These are distinct. "Standard augmentation techniques" signals that the professor expects well-established, literature-supported methods, not experimental ones.

**Sentence 3 — The load-bearing sentence:**
> *"This would be useful not only to improve the robustness of the deep learning model, but also to show the advantage of using deep learning methods compared to a more automatic classification approach based only on the quantification of the red color."*

This sentence contains the two stated purposes:
- Purpose A: **Improve robustness** of "the deep learning model"
- Purpose B: **Show DL advantage** over "a more automatic classification approach based only on the quantification of the red color"

"The deep learning model" — definite article. The professor has a specific model in mind. **This model is not named.**

"A more automatic classification approach based only on the quantification of the red color" — this is the baseline. It describes exactly what the RGB threshold pipeline in `main_4` does (R∈[25,255], G∈[0,100], B∈[0,80] → rust mask → percentage). But it could also describe Nisrine's automatic classification work if that work uses a red-color threshold as its core mechanism.

**Sentence 4:**
> *"In particular, we could apply transformations that modify the color balance, introduce noise, add blurring, change brightness or contrast, and other similar variations."*

The techniques listed are **exclusively photometric**: colour balance, noise, blur, brightness, contrast. No geometric transforms are mentioned. "Other similar variations" extends the list to analogous photometric operations. This is consistent with the professor's intent to simulate real-world acquisition variation — lighting, camera settings, sensor noise.

**Sentence 5:**
> *"These are standard techniques that are commonly used in the literature and can probably be implemented directly using common Python libraries for machine learning and image processing."*

"Probably" signals the professor is not certain of the technical specifics. They expect the student to verify this from literature. The phrase "common Python libraries" points to `torchvision.transforms`, `albumentations`, `PIL`, or `scikit-image` — not custom implementations.

**Sentence 6:**
> *"...we need to define a reasonable augmentation strategy based on our specific problem, rather than increasing the dataset arbitrarily."*

This is a constraint on scope. The professor is explicitly asking for a **principled, bounded** expansion — not "as many augmentations as possible." The augmentation factor must be justified from the literature and the specific problem, not chosen arbitrarily.

**The four goals — read precisely:**

The email says "identify," "understand," "check from the literature," and "implement." Goal 1 is research (which techniques?). Goal 2 is technical (how to implement?). Goal 3 is empirical (what expansion factor does literature support?). Goal 4 is engineering (build it). The email does not mention running the comparison experiment or writing up results — those are implied as later steps toward the journal paper.

---

## 2. Critical Ambiguities

### Ambiguity 1 (Critical) — Which deep learning model?

The email says "the deep learning model." It does not name it. Given that the research group includes:

- **Nisrine** — automatic classification work
- **Gerardo** — corrosion estimation model
- **Parastoo** — ultimate load prediction model

Three interpretations are possible, and they produce three completely different augmentation pipelines. This is not a minor detail — as shown in `augmentation_objective_decision.md`, the prediction target determines which augmentations are label-safe, which baseline is appropriate, and what success means.

### Ambiguity 2 (Critical) — What is "the automatic classification approach based on the red color"?

Two interpretations:

**Interpretation A:** The "red color" baseline is the threshold pipeline in `main_4` (or the equivalent from `main_3`). This is the fixed RGB threshold that computes rust pixel fraction. In this case, the baseline is the existing engineering pipeline — not any person's work.

**Interpretation B:** Nisrine's automatic classification work IS the "automatic classification approach based on the red color." In this case, Nisrine's method is the baseline to be beaten, not a DL model to be improved. The DL model to improve would then be Gerardo's or Parastoo's.

These two interpretations are mutually exclusive and change the entire experimental design.

### Ambiguity 3 (Important) — What is the prediction target?

The email uses "classification" loosely. It could mean:
- Categorical classification: does this image have rust? (binary); what severity? (multi-class)
- Continuous estimation: what percentage of the surface is covered by rust?
- Localised estimation: what is the maximum rust concentration in any section?

As established in `augmentation_objective_decision.md`, the choice of target determines whether the comparison is even possible:
- `surface_total_rust_pct`: tautological — the workbook label was derived from the same RGB threshold; the DL model cannot outperform the threshold's own label.
- `peak_rust_pct`: non-tautological — spatially localised; DL can potentially improve.
- Categorical labels: do not currently exist in the dataset; would require a design decision about severity boundaries.

### Ambiguity 4 (Important) — Who is responsible for which part of the paper?

"We would like to work on data augmentation" and "to complete a journal paper with these analyses" — this implies a collaborative paper. But the augmentation task is assigned to Parastoo. Is the augmentation study:
- Parastoo's standalone contribution to the paper?
- Infrastructure that Nisrine and Gerardo will also use for their models?
- A methodological section shared across all three researchers' results?

The answer determines whether augmentation must be implemented in a way that works for multiple model architectures and multiple prediction targets.

### Ambiguity 5 (Moderate) — What constitutes "showing DL advantage"?

No metric is specified. No performance threshold is named. "Show the advantage" could mean:
- Lower MAE on a test set
- Better generalisation under acquisition condition variation
- Higher Spearman correlation to the physical measurement
- A combination of accuracy and robustness

Without defining this upfront, the comparison study has no clear success criterion.

### Ambiguity 6 (Moderate) — Offline or online augmentation?

The professor says "increase the size of the dataset" — this sounds like offline augmentation (pre-generating and storing augmented images). But the professor also says "implement the techniques" using Python libraries — which is compatible with online augmentation (applied during training, no files saved). These are architecturally different choices with different implications for storage, the Excel file, and reproducibility.

---

## 3. Why the Identity of the Target DL Model is Critical

`augmentation_objective_decision.md` establishes that augmentation interacts with three things: the label, the baseline, and the evaluation. When the DL model is unknown, all three are unknown.

### The label question

If the DL model is Nisrine's classifier, the label is categorical (rust present/absent, or severity class). Augmentation is straightforwardly label-preserving for categorical labels: no transformation changes which category a specimen belongs to. All photometric transforms are safe; boundary cases at severity thresholds need care, but the risk is manageable.

If the DL model is Gerardo's estimator, the label is a continuous percentage. The choice between `surface_total_rust_pct` and `peak_rust_pct` then becomes decisive:
- `surface_total_rust_pct`: the label was derived from the same RGB threshold as the baseline. Augmentation cannot create a fair comparison because the baseline is essentially the oracle for its own label.
- `peak_rust_pct`: the label is a fixed physical measurement. Photometric augmentation is label-safe — darkening the image does not change the measured peak rust percentage from the original acquisition.

If the DL model is Parastoo's structural predictor (ultimate load), there are only 48 data points — one per specimen at terminal stage. No DL model can be trained directly on 48 samples. Augmentation must be applied to a surface proxy model first, whose embeddings are then used for structural regression. This is a two-stage pipeline requiring a separate architectural decision.

### The baseline question

`augmentation_objective_decision.md` established that the "red color quantification" approach changes the threshold-detected rust percentage by 3–7× under a 20% brightness change (measured empirically from actual images in this dataset). This fragility is the scientific argument for DL: a model trained with brightness augmentation learns invariance that the threshold cannot provide.

But this argument only works if the DL model's label is NOT itself derived from the threshold. If the target is `surface_total_rust_pct` (derived from the same threshold), the argument collapses: the DL model learns to predict a label that is the threshold's own output, and the comparison becomes circular.

The model identity determines whether the baseline is the threshold pipeline (Goal 5 in the decision memo — achievable) or Nisrine's work (a different comparison with different success criteria).

### The evaluation question

The specimen-level split requirement (no observation from the same specimen in both train and test) is already implemented in `main_2` and `main_4`. But if the augmented study is for Gerardo's model or a new joint pipeline, the same split logic must be enforced for that model. Without knowing which model is in scope, the correct split implementation cannot be designed.

---

## 4. Augmentation Strategy by Task

### Task A — Image Classification (categorical output)

This task applies if the "DL model" is a classifier (Nisrine's work) and the goal is to outperform a binary or multi-class threshold-based classifier.

**Augmentation suitable:** All photometric transforms (brightness ±20%, contrast ±20%, saturation ±20%, hue ±0.05, blur, noise). Geometric transforms (horizontal flip, small rotation ±5°). Labels do not change under any of these — a specimen with moderate rust remains moderate-rust regardless of image brightness.

**What becomes risky:** Aggressive brightness or contrast shifts at category boundaries. A specimen with 4.9% rust (just below a moderate-rust threshold) darkened by 30% might look identical to an 8% rust specimen. The visual appearance contradicts the label near boundaries. Keep photometric augmentation within ±20%.

**Augmentation factor:** Literature for classification tasks typically supports 5–20×. For 791 images, 5× gives ~3955; 10× gives ~7910. The lower bound is appropriate for photometric-only augmentation of a moderately sized dataset.

**Success:** Augmented DL classifier accuracy/F1 > threshold-based classifier under specimen-grouped holdout.

**Excel implications:** Categorical labels are fully invariant to augmentation. All original metadata columns copy unchanged. Add provenance columns: `is_augmented`, `source_image_id`, `augmentation_type`.

**Location column issue:** `B_Location_of_Peak_Rust_in_length_[cm]` would change under horizontal flip (reflected location = specimen_length − original_location). If this column is not used as an input feature for the classifier, this is harmless. If it is used, the reflected value must be computed.

### Task B — Corrosion Estimation by Regression (continuous output)

This task applies if the "DL model" is Gerardo's estimator producing a continuous rust percentage.

**This task has two sub-cases depending on the target:**

**Sub-case B1 — Target: `surface_total_rust_pct`**

Do not proceed with this target. As established in `augmentation_objective_decision.md`, the workbook label `surface_total_rust_pct` was derived from the same RGB threshold as the baseline. The threshold achieves MAE ≈ 0.0002 against this label (essentially zero error). No DL model, augmented or not, can outperform the method that generated the label. Augmentation cannot fix a structurally unfair comparison.

**Sub-case B2 — Target: `peak_rust_pct`**

This is the correct target. `peak_rust_pct` is the maximum rust concentration along any longitudinal strip — spatially localised, non-tautological, and already the target in the `main_2` pipeline.

**Augmentation suitable:** All photometric transforms (brightness ±20%, contrast ±20%, saturation ±20%, hue ±0.05, blur, noise). Horizontal flip (peak rust value is the maximum across all strips; the maximum does not depend on which side of the specimen it is located). Aspect-ratio-aware random crop (exposes the model to different longitudinal sections of the 4.36:1 specimen, which is the most important augmentation for this specific geometry).

**What becomes risky:** Very heavy brightness darkening on low-rust images (creating false visual rust) beyond the ±20–25% range. Random crop at specimens where the peak rust is highly localised — the crop may sample a zero-rust region while the label is, say, 40% — this is a valid learning challenge but requires sufficient epochs to converge.

**Success:** Augmented DL MAE and Spearman for `peak_rust_pct` < threshold baseline (`img_strip_rust_max_pct`) under specimen-grouped holdout.

**Excel implications:** `B_Peak_Rust_Percentage_[%]` copies unchanged for all photometric augmentations. `B_Location_of_Peak_Rust_in_length_[cm]` changes under horizontal flip. If the location column is not used as a feature, copy unchanged; if it is used, compute the reflected value.

### Task C — Corrosion Segmentation (pixel-level mask output)

This task applies if Gerardo's model produces a pixel-level rust segmentation mask as output (rather than a scalar percentage).

**This task requires a fundamentally different augmentation strategy.** The ground-truth label for segmentation is a pixel mask — and if the mask was derived from the same RGB threshold, it is not fixed like a scalar measurement. It changes when the image is augmented.

**Augmentation suitable:** Geometric transforms (horizontal flip, small rotation, translation) — IF the label mask is transformed identically to the image. This is the standard approach in segmentation: augment image and mask together with identical spatial transforms.

**What becomes risky:** Photometric transforms (brightness, contrast, colour shifts). When the image is brightened, pixels that were previously classified as rust (falling within R∈[25,255], G∈[0,100], B∈[0,80]) may no longer meet the threshold. If the label mask was derived from the original image, the augmented image and the mask are now inconsistent — some pixels appear rust-free in the brightened image but are labelled as rust in the mask.

This is the opposite of the regression case:
- For regression: photometric augmentation is safe (scalar label is fixed); geometric augmentation has nuances.
- For segmentation (with threshold-derived masks): photometric augmentation corrupts label consistency; geometric augmentation is safe if mask is co-transformed.

**If segmentation is in scope, the professor's listed techniques (brightness, contrast, colour balance) are the most dangerous ones for this specific task.**

This is a critical clarification question to bring back to the professor.

**Success:** Augmented DL segmentation IoU/Dice > threshold-derived mask under specimen-grouped holdout.

**Excel implications:** Scalar columns copy unchanged. Location columns follow the same rules as Task B. The mask labels themselves must be co-transformed with the image — they should not appear in the Excel at all (they are image-derived, not scalar measurements).

### Task D — Ultimate Load Prediction (Parastoo's structural model)

This task applies if the "DL model" refers to the structural prediction pipeline in `main_4`.

**The fundamental constraint:** `ultimate_load_kn` and `wire_area_loss_frac` have only 48 data points — one per specimen at terminal stage. No DL model can be trained directly on 48 samples. Augmentation of the structural labels themselves is not meaningful.

**The only viable path:** Augmentation is applied to the surface corrosion training (791 samples) to produce a more robust backbone. The backbone's learned representations are then extracted per specimen and used as features for the structural regression. This is an indirect, two-stage benefit from augmentation.

**Augmentation suitable:** Same photometric transforms as Task B — but applied to the surface model's training phase, not to the structural regression. The structural model sees only 48 aggregated embeddings (one per specimen), not augmented images.

**What becomes risky:** Treating structural prediction improvement as the primary success criterion for augmentation. As `augmentation_objective_decision.md` establishes, the LOCO collapse (grouped MAE 0.174 → LOCO MAE 0.564, 3.24×) is driven by campaign confounding — Campaign 1 uses 7 steel mesh + 3.5% NaCl, Campaign 2 uses 4 steel mesh + 5% NaCl. The Spearman correlation of wire area loss under LOCO is −0.089. Campaign confounding is a data design problem, not a representation learning problem. No augmentation strategy can fix it.

**Success:** Under grouped 5-fold CV (not LOCO), augmented backbone embeddings improve structural prediction relative to unaugmented embeddings. LOCO failure is expected and should be reported with its correct explanation (campaign confounding, not model failure).

**Excel implications:** The structural prediction study does not require augmented rows in the Excel file. The Excel tracking issue is a surface-model concern only.

---

## 5. Augmentation Safety by Technique and Task

| Technique | Classification (A) | Regression (B2) | Segmentation (C) | Structural (D) |
|---|---|---|---|---|
| **Brightness ±20%** | Safe | Safe — label fixed | **Risky** — mask derived from pixels | Safe for backbone |
| **Contrast ±20%** | Safe | Safe | **Risky** | Safe |
| **Colour balance / saturation ±20%** | Safe | Safe | **Risky** | Safe |
| **Hue shift ±0.05** | Safe | Safe at small range | **Risky** | Safe at small range |
| **Gaussian blur** | Safe | Safe | Safe — mask from original | Safe |
| **Gaussian noise (σ=0.02)** | Safe | Safe | Safe | Safe |
| **Horizontal flip** | Safe | Safe — peak value position-invariant | Safe if mask co-flipped | Safe |
| **Vertical flip** | Borderline | Borderline | Safe if mask co-flipped | Borderline |
| **Rotation ±5° (reflect fill)** | Safe | Safe | Safe if mask co-rotated | Safe |
| **Random crop (longitudinal)** | Safe | Safe — teaches location invariance | Safe if mask co-cropped | Safe |
| **Cutout / random erasing** | Risky near boundaries | Risky — hides real rust | Risky — mask-image mismatch | Risky |
| **Heavy brightness (>±30%)** | Risky near boundaries | Risky — creates false rust visually | **Very Risky** | Risky |
| **Large hue shift (>±0.1)** | Risky — rust changes apparent colour | Risky | **Very Risky** | Risky |

**Key asymmetry to communicate clearly:**

The professor's listed techniques — brightness, contrast, colour balance — are safe for Task A (classification) and Task B (regression), but are the **riskiest** techniques for Task C (segmentation with threshold-derived masks). For segmentation, geometric transforms (flip, rotation) are safe, and photometric transforms introduce label inconsistency. This asymmetry is not obvious and should be discussed with the professor if Gerardo's model is a segmentation model.

---

## 6. Additional Questions to Ask the Professor

Ranked by criticality:

### Q1 — Which deep learning model? (Critical)

> "You mention 'the deep learning model' — could you clarify which model this refers to? Is it Nisrine's classification model, Gerardo's corrosion estimation model, or the deep learning component of my structural prediction work? This determines the prediction target, the appropriate augmentation strategy, and how the baseline comparison is set up."

**Why critical:** As shown in `augmentation_objective_decision.md`, the prediction target determines which augmentations are label-preserving and whether the comparison against the red-color baseline is even fair (see the tautology issue for `surface_total_rust_pct`).

### Q2 — What is the red-color baseline? (Critical)

> "You describe 'a more automatic classification approach based only on the quantification of the red color.' Is this the RGB threshold pipeline already implemented in the project (which computes a rust mask from fixed pixel ranges), or is this specifically Nisrine's work? Understanding whether Nisrine's work is the baseline to be beaten or the DL model to be improved is essential for designing the comparison."

**Why critical:** If Nisrine's work is the baseline, then neither Nisrine's model nor Nisrine's pipeline receives augmentation — the augmented DL model (Gerardo's or Parastoo's) is what Nisrine's method is compared against. If the threshold pipeline is the baseline, augmentation goes into whichever DL model is in scope.

### Q3 — What is the prediction target? (Critical)

> "For the comparison study, what specific output should the DL model produce? Binary rust presence/absence (classification), a continuous rust coverage percentage (regression), a pixel-level segmentation mask, or the peak rust concentration? The answer changes both the augmentation strategy and the success criterion."

**Why critical:** From `augmentation_objective_decision.md`: `surface_total_rust_pct` is near-tautological (derived from the same threshold), so DL cannot outperform the threshold on this target. `peak_rust_pct` is non-tautological and the correct target for a fair comparison. Categorical labels don't currently exist and would need to be constructed.

### Q4 — Is Gerardo's model doing regression or segmentation? (Important if Gerardo)

> "Does Gerardo's corrosion estimation model produce a scalar rust percentage per image, or a pixel-level segmentation mask? The augmentation strategy is fundamentally different: for regression, brightness and colour augmentation are safe; for segmentation with threshold-derived masks, brightness augmentation can cause label inconsistency because the mask was computed from the original image's pixel values."

**Why important:** If segmentation, the professor's listed techniques (brightness, contrast, colour balance) are the most risky ones, and this needs to be addressed before implementation.

### Q5 — Evaluation protocol: specimen-grouped splits or image-level splits? (Important)

> "For evaluating the comparison between DL and the red-color approach, should we use specimen-level grouped splits (so that all images from the same specimen appear in either train or test, never both), or a simpler image-level random split? Specimen-grouped splits are stricter and more honest for this dataset — augmented images from a training specimen must not appear in the test set."

**Why important:** Without specimen-level grouping, augmented images from the same specimen as test images could appear in training, inflating DL performance and failing peer review.

### Q6 — Offline or online augmentation? (Moderate)

> "Should augmented images be generated in advance and saved to disk (offline augmentation), or generated dynamically during each training epoch (online augmentation)? Online augmentation provides greater diversity and avoids disk overhead, but does not produce a physically larger dataset. Offline augmentation produces additional files that might need to be tracked in the Excel metadata. Which approach do you have in mind?"

**Why moderate:** This changes whether the Excel file needs to be modified and whether augmented images need to be stored and tracked as separate files.

### Q7 — Is structural prediction in scope for this augmentation study? (Moderate)

> "Should the augmentation study aim to improve the ultimate load prediction, or is the scope limited to the surface corrosion comparison (DL vs. red-color threshold)? The structural prediction has only 48 data points, so augmentation would need to act indirectly through better backbone representations — it is a separate downstream experiment, not part of the primary augmentation study."

**Why moderate:** Avoids scope creep. The email does not mention ultimate load or structural prediction; clarifying that it is out of scope for this study prevents effort being directed at a problem that augmentation cannot directly solve.

### Q8 — What does "showing DL advantage" mean quantitatively? (Moderate)

> "For the comparison study, what metric and what threshold of improvement would constitute a demonstrated DL advantage? For example, is it lower MAE on a held-out test set, better performance under varied lighting conditions, or a combination?"

**Why moderate:** Without a clear success criterion, the study has no stopping condition.

---

## 7. Excel Metadata Implications

### Current Excel structure

`Data/Images_Dataset_A-Z-1.xlsx` contains one row per image (791 usable rows). Relevant columns:

| Column | Type | Changes with augmentation? |
|---|---|---|
| `specimen_id` / specimen name | Physical property | **No** |
| `week`, `ageing_days` | Temporal property | **No** |
| `N_Steel_Mesh`, `Treatment`, `NaCl%` | Design properties | **No** |
| `Cover_(Failure_Surface)_[mm]` | Physical property | **No** |
| `B_Peak_Rust_Percentage_[%]` | Physical measurement | **No** (for all photometric augmentations) |
| `B_Location_of_Peak_Rust_in_length_[cm]` | Spatial measurement | **Yes — under horizontal flip** |
| `C_surface_total_rust_pct` | Physical measurement | **No** |
| `wire_area_loss_frac`, `ultimate_load_kn` | Structural measurements | **No** (only 48 rows, terminal stage) |
| `image_filename` | File identifier | **Yes — new filename for each augmented image** |

### Columns to duplicate unchanged

For any augmentation type: `specimen_id`, `week`, `ageing_days`, `N_Steel_Mesh`, `Treatment`, `NaCl%`, `Cover`, `B_Peak_Rust_Percentage_[%]`, `C_surface_total_rust_pct`, `wire_area_loss_frac`, `ultimate_load_kn`.

### Columns that must be modified

| Column | Condition | Required modification |
|---|---|---|
| `image_filename` | Always (new file must have a new name) | New filename encoding augmentation type and source ID (e.g., `D02-20240529-20W_aug_hflip_b120.png`) |
| `B_Location_of_Peak_Rust_in_length_[cm]` | Only under horizontal flip | Reflected location = `specimen_length_cm − original_location_cm` |

### New columns to add (augmentation provenance)

If offline augmentation is chosen (pre-generated files):

| New column | Purpose | Example value |
|---|---|---|
| `is_augmented` | Boolean flag | `TRUE` / `FALSE` |
| `source_image_id` | Original image filename | `D02-20240529-20W.png` |
| `augmentation_type` | Human-readable transform name | `brightness_+20pct`, `horizontal_flip`, `blur_sigma1.2` |
| `augmentation_seed` | Random seed for reproducibility | `42` |
| `augmentation_intensity` | Numeric parameter | `1.20` (brightness factor), `0.5` (blur sigma) |

If online augmentation is chosen (no pre-generated files, transforms applied during training):

**No Excel modification is needed.** Online augmentation operates entirely within the training loop. The augmented tensors are never written to disk. The Excel file tracks the physical measurements from the original images only. This is the cleaner solution.

### Task-dependent label consistency considerations

**For classification (Task A):** All categorical labels copy unchanged. No location adjustment needed unless location is used as a feature.

**For regression (Task B — `peak_rust_pct`):** The scalar label copies unchanged for all photometric augmentations. Under horizontal flip, `B_Location_of_Peak_Rust_in_length_[cm]` must be reflected if it is included as a feature. `B_Peak_Rust_Percentage_[%]` (the value, not the location) is invariant to flip.

**For segmentation (Task C):** The scalar columns copy unchanged. The pixel mask is NOT stored in the Excel — it is an image-level annotation. For geometric augmentations, the mask must be co-transformed with the image; the Excel row does not need updating for the mask. For photometric augmentations, the mask is no longer accurate (see Section 4, Task C). If segmentation is in scope, the augmentation-mask consistency problem should be raised explicitly with the professor.

**For structural prediction (Task D):** Augmentation is applied only to the surface training phase (791 rows). The 48 structural rows never receive augmented data — they represent terminal-stage measurements, not training inputs for the backbone. No Excel modification is needed for structural rows.

---

## 8. Does the Email Implicitly Assume Excel Modifications?

No. The professor does not mention the Excel file. The email discusses images and augmentation techniques. The implicit assumption is:

1. Augmented images carry the same labels as their source images — which is true for photometric transforms and mostly true for geometric transforms (with the location column exception).
2. The augmented images integrate into the existing training pipeline without restructuring the label tracking system.

The professor likely envisions offline augmentation (generating a physically larger image collection) without realising that this creates a tracking obligation: augmented images need labels, and those labels must be consistent and provenance-tracked.

However, from the repository's architecture, **online augmentation is the correct implementation** for this dataset. Online augmentation generates augmented tensors during training and never writes files to disk. The Excel file remains unchanged. No provenance tracking is needed because augmented images are ephemeral — they exist only within a training batch.

The one case where Excel modification becomes necessary is if the study compares augmented DL models built by different researchers (Nisrine, Gerardo, Parastoo) using different augmented subsets of the same dataset. In that case, a shared augmentation specification (a config file, not an Excel column) is the right solution — not expanding the Excel file.

**Recommendation:** Use online augmentation. Keep the Excel file as-is. Define augmentation parameters in `main_2/configs/augmentation.yaml` (as planned in `augmentation_independent_plan.md`). This is reproducible, clean, and requires no data file restructuring.

---

## Summary of Open Questions (Priority Order)

| # | Question | Blocking? | Who can answer |
|---|---|---|---|
| 1 | Which DL model — Nisrine's, Gerardo's, or Parastoo's? | **Yes** | Professor |
| 2 | Is the "red color approach" the threshold pipeline, or Nisrine's specific work? | **Yes** | Professor |
| 3 | What is the prediction target — classification, rust %, peak rust, or segmentation? | **Yes** | Professor |
| 4 | Is Gerardo's model regression or pixel-level segmentation? | Yes (if Gerardo) | Gerardo / Professor |
| 5 | Evaluation protocol — specimen-grouped splits or image-level? | Yes | Professor |
| 6 | Offline or online augmentation? | Moderate | Professor / implementation decision |
| 7 | Is structural prediction (ultimate load) in scope? | Moderate | Professor |
| 8 | What metric and threshold defines "DL advantage"? | Moderate | Professor |

**Until Questions 1, 2, and 3 are answered, the augmentation implementation should not begin.** The literature review (Goals 1 and 3 in the professor's email) can proceed in parallel because technique candidates and expansion factor ranges are task-agnostic. Implementation (Goal 4) requires the answers.

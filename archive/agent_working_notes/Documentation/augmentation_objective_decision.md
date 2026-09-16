# Augmentation Objective Decision Memo
## Why the Purpose Changes the Correct Strategy

> **Question:** My professor asked for data augmentation. Why does the *objective* change the correct strategy?
> **Date:** 2026-06-27

---

## Framing the Problem

Augmentation is not a fixed procedure. Each transformation interacts with three things:

1. **The label** — what are you trying to predict, and how was that label generated?
2. **The baseline** — what method are you trying to outperform?
3. **The evaluation** — under what conditions must the model succeed?

Apply the wrong augmentation for the wrong goal and you can corrupt labels, create unfalsifiable baselines, or produce a comparison that looks right but measures the wrong thing. The seven goals below are all plausible interpretations of your professor's email — but they are not equivalent, and they call for different strategies.

---

## Key Evidence That Shapes Every Goal

### From the Professor's Email

> *"...show the advantage of using deep learning methods compared to a more automatic classification approach based only on the quantification of the red color."*

This is the load-bearing phrase. The professor is asking for a **comparison** between DL and threshold-based red-color quantification. Augmentation is the enabling mechanism, not the endpoint.

The professor also names specific techniques: colour balance, noise, blur, brightness, contrast. These are all **photometric** (pixel-value) transforms. No spatial distortions, no object removal, no structural changes to the image.

### From the Dataset

- 791 usable images, 48 specimens, time-series 0W–36W.
- `surface_total_rust_pct` (workbook label): **near-tautological** with the threshold feature `img_rust_area_ratio_pct`. Measured MAE between them ≈ 0.0002. The workbook label was derived from the same RGB threshold on the same images.
- `peak_rust_pct` (workbook label): the **maximum** longitudinal strip value. Spatially localised. Range 0–84.3%, median 2.24%, mean 9.59%, 8.5% zeros. Non-tautological — the DL model must learn spatial localisation to predict it.
- Structural labels (`ultimate_load_kn`, `wire_area_loss_frac`): only 48 rows (one per specimen, terminal stage only).
- Campaign confounding: Campaign 1 = 7 steel mesh + 3.5% NaCl; Campaign 2 = 4 steel mesh + 5% NaCl. Spearman of `n_steel_mesh` vs `ultimate_load_kn` = 0.827. LOCO collapse: grouped MAE 0.174 → LOCO MAE 0.564 (3.24×).

### From the Threshold Baseline (main_4)

RGB rust threshold: R∈[25,255] AND G∈[0,100] AND B∈[0,80].

Empirical pixel test on actual images: **brightness augmentation changes the threshold-detected rust percentage by 3–7×** on the same image. Darkening by 20% can more than double the detected rust area. The threshold has no mechanism for invariance — it reads whatever pixel values are present.

The DL model's label is fixed in the workbook. Darkening the image does not change the workbook label. This asymmetry is the core scientific argument for augmentation.

### From the DL Pipeline (main_2)

- Frozen ResNet18 backbone (ImageNet weights). Target: `B_Peak_Rust_Percentage_[%]` (`peak_rust_pct`).
- Architecture issue: all embeddings are pre-computed in a single pass before training. The MLP trains on fixed vectors. Online augmentation requires restructuring the training loop so the backbone is called per-batch during training.
- Images are 2835×650 (4.36:1 aspect ratio). The default transform center-crops to 224×224, capturing only the central ~22% of specimen width.

### From the Split Requirement

Splits are keyed on `specimen_id` (main_4) / `specimen` (main_2). No observation from the same specimen may appear in both train and test. Augmented images from a training specimen must never appear in the test fold.

---

## Goal 1 — Corrosion Classification (Categorical)

**What this means:** Predict a categorical label — rust present/absent, or severity class (none/mild/moderate/severe).

**What augmentation is suitable:** All standard transforms. Flips, rotation, brightness, contrast, blur, noise. Labels are categories; none of these transforms change which category the image belongs to.

**What becomes risky:** Very aggressive brightness or hue shifts that move a near-boundary image across the category threshold (e.g., a specimen with 1% rust becomes visually indistinguishable from 0% rust after heavy brightening). Risk is manageable at moderate augmentation levels.

**What success means:** Augmented DL classifier outperforms threshold-based binary detection (rust vs. no-rust) on a specimen-held-out test set.

**What experiment is required:** Build rust category labels from the workbook (e.g., 0%=none, 0–5%=mild, 5%+=moderate). Train DL classifier with and without augmentation. Compare to threshold binary detection (any pixel above threshold = rust present).

**Does it match the professor's email?** Partially. The email uses the word "classification," but the current targets are continuous percentages, not categories. The professor may be using "classification" loosely to mean "measurement." No categorical labels currently exist in the dataset or main_2 pipeline. Building them would require a design decision about thresholds that is not in the workbook.

**Verdict:** Plausible but requires a label engineering step not currently in the pipeline. Not the path of least resistance.

---

## Goal 2 — Rust Percentage Regression (`surface_total_rust_pct`)

**What this means:** Predict the total rust area as a percentage of the specimen surface. The workbook column is `C_surface_total_rust_pct`.

**What augmentation is suitable:** Technically, photometric augmentation is label-preserving (the label is a fixed number). But see below.

**What becomes risky:** **The comparison is unfalsifiable.** The workbook label `surface_total_rust_pct` was derived from the same RGB threshold on the same images. The existing threshold feature `img_rust_area_ratio_pct` predicts it with MAE ≈ 0.0002. No DL model — regardless of augmentation — can outperform a baseline that is essentially the oracle for its own label.

Augmentation on this target does not make the comparison impossible; it makes the comparison meaningless. The DL model will always lose to a method that was used to generate the label.

**What success means:** Augmented DL MAE < threshold MAE on `surface_total_rust_pct`. In practice, this can only happen if the DL learns the threshold almost exactly — which would make it a slow, expensive replica of the threshold, not an improvement.

**What experiment is required:** Run Condition 1 (threshold) vs Condition 2 (DL no-aug) vs Condition 3 (DL with-aug) for `surface_total_rust_pct`. The experiment will show the threshold nearly perfect and DL behind.

**Does it match the professor's email?** The phrase "quantification of the red color" points directly to `surface_total_rust_pct`. But this is the tautological target. If the professor intends a comparison on this specific target, the comparison is structurally biased against DL — and augmentation cannot fix this.

**Verdict:** Wrong target for the comparison the professor wants to demonstrate. Using this target undermines the study.

---

## Goal 3 — Peak Rust Prediction (`peak_rust_pct`)

**What this means:** Predict the maximum longitudinal strip percentage — the worst rust concentration anywhere along the specimen length. Column: `B_Peak_Rust_Percentage_[%]`. This is the current `main_2` target.

**What augmentation is suitable:** All seven selected transforms. Photometric augmentation (brightness, contrast, saturation, hue) is label-safe because `peak_rust_pct` is a fixed physical measurement. Random crop augmentation samples different longitudinal sections, teaching the model that the peak may be anywhere along the specimen's 4.36:1 length.

**What becomes risky:** Heavy brightness augmentation at images with very low or zero rust, where the model must learn to produce near-zero predictions from uniformly dark or bright pixels. At moderate levels this is fine. Random crop combined with high-peak-rust images: the crop may show a zero-rust section while the label is high (e.g., 30%). This is a valid learning signal (the model must integrate information across the full specimen) but requires more epochs to converge.

**What success means:** Augmented DL MAE and Spearman correlation for `peak_rust_pct` outperform the threshold strip baseline (`img_strip_rust_max_pct`) under specimen-grouped holdout.

**What experiment is required:** Three conditions (threshold, DL no-aug, DL with-aug) targeting `peak_rust_pct`, evaluated under GroupShuffleSplit (5-fold, keyed on `specimen`) and LOCO. The threshold baseline uses `img_strip_rust_max_pct` from `main_4` outputs.

**Does it match the professor's email?** Yes, better than Goal 2. `peak_rust_pct` is non-tautological (the threshold strip analysis computes a similar thing but the DL model can improve on the spatial localisation). The professor's stated goal of "showing DL advantage" is achievable here in a way it is not for `surface_total_rust_pct`.

**Verdict:** Correct target. The existing `main_2` pipeline already targets this. The comparison is fair, falsifiable, and achievable.

---

## Goal 4 — Robustness to Image Acquisition Conditions

**What this means:** The 48 specimens were imaged over 36 weeks in potentially varying ambient lighting, camera calibration, and surface wetness conditions. The goal is to train a model that produces consistent predictions regardless of these variations — where the threshold baseline would not.

**What augmentation is suitable:** Brightness and contrast jitter are the *primary* augmentations for this goal — directly simulating the lighting variations the model must be invariant to. Blur simulates focus variation. Noise simulates sensor variation. These are the transforms the professor explicitly lists.

**What becomes risky:** Augmentations that are not plausible acquisition variations — heavy hue shifts, vertical flips, large rotations — do not simulate real lighting conditions. Applying them dilutes the training signal with implausible examples.

**What success means:** Under brightness-perturbed test images, the DL model's metrics degrade gracefully while the threshold baseline's metrics degrade severely. The empirical pixel test already demonstrates the threshold is fragile: a 20% brightness reduction can triple detected rust area. The DL model trained with brightness augmentation should be invariant to this.

**What experiment is required:** Perturb the test set images with ±20% brightness changes. Evaluate threshold baseline, DL no-aug, and DL with-aug under these perturbations. This produces a direct demonstration of the acquisition-robustness advantage.

**Does it match the professor's email?** Directly. The professor lists "colour balance, noise, blur, brightness, contrast" — these are all acquisition-condition variations. This framing makes the professor's specific list of transforms scientifically motivated rather than arbitrary.

**Verdict:** This is the scientific *reason* why photometric augmentation is appropriate for this dataset. Goals 3 and 4 are complementary: Goal 3 defines the metric (peak rust regression), Goal 4 explains why augmentation helps (threshold is fragile to the same conditions augmentation simulates).

---

## Goal 5 — Showing DL Advantage Over Red-Color Thresholding

**What this means:** The professor's stated goal. Produce experimental evidence that a DL model outperforms a fixed threshold approach for corrosion surface quantification.

**What augmentation is suitable:** Photometric augmentation — specifically brightness and contrast jitter — because it directly demonstrates the threshold's core weakness. The threshold reads pixel values literally; the DL model trained on augmented data learns invariance to photometric variation. This makes the comparison meaningful beyond just prediction accuracy: it shows the DL model is more robust to the conditions under which real corrosion images are acquired.

**What becomes risky:**
- Choosing `surface_total_rust_pct` as the target (Goal 2 issue: tautological, DL loses).
- Applying augmentation that the threshold baseline cannot replicate — this is actually *good* for the comparison, but must be clearly presented so it is not perceived as cherry-picking conditions where DL wins.
- Running the comparison only under simple random splits (no specimen grouping), which would overstate DL performance and fail peer review.

**What success means:** On `peak_rust_pct` under specimen-grouped evaluation: augmented DL MAE and Spearman outperform the threshold strip baseline. Even if only the acquisition-robustness comparison (perturbed test set) shows DL advantage, this is a publishable finding.

**What experiment is required:** Exactly Goal 3's experiment, framed as a comparison study. Add the brightness-perturbation test from Goal 4 as the robustness comparison. Present three conditions (threshold, DL no-aug, DL with-aug) with the perturbation test as a subsection.

**Does it match the professor's email?** Yes — this is the professor's literal stated objective. All other goals are either subsumed here or are separate problems.

**Verdict:** This is the unifying goal. Goals 3 and 4 are the mechanism. This is what the comparison study should be framed around.

---

## Goal 6 — Learning Embeddings for Later Structural Prediction

**What this means:** Train the DL model on surface corrosion (791 samples), then extract per-specimen embeddings and use them as features for structural prediction (`ultimate_load_kn`, `wire_area_loss_frac`) alongside or instead of the classical handcrafted features.

**What augmentation is suitable:** Augmentation that makes embeddings more specimen-discriminative — that is, the frozen ResNet18 backbone should learn (through its fine-tuned head, or through selecting which backbone features to rely on) to distinguish specimens by their rust severity and spatial pattern, not by lighting artefacts. Photometric augmentation forces the model to learn specimen-discriminative features that are invariant to lighting — which is exactly what is needed for an embedding that generalises across specimens at structural-prediction time.

**What becomes risky:** Augmentations that destroy specimen identity — very large hue shifts, heavy distortion, cutout over rust spots. The embedding needs to represent *this specimen's* corrosion pattern, not an idealised or corrupted version of it. At inference time, embeddings are always extracted without augmentation; training augmentation only teaches the model to be invariant to acquisition variation, which is desirable.

**What success means:** Augmented-backbone embeddings (aggregated per specimen over all time points, or at terminal time point) produce better structural prediction metrics under specimen-grouped splits than unaugmented embeddings or classical features alone.

**What experiment is required:** Train surface model → extract terminal-stage embeddings per specimen (inference transforms, no augmentation) → run structural regression with grouped 5-fold CV → compare to classical feature set. This is a downstream experiment, separated from the primary augmentation study.

**Does it match the professor's email?** Not explicitly. The professor's email focuses on the surface comparison ("classification approach based only on the quantification of the red color"). Structural prediction is a downstream research question not mentioned in the email. Pursuing this in parallel would be scope expansion.

**Verdict:** Valid scientific goal, but not what the professor is asking for in this assignment. Should be framed as an extension, not the primary deliverable.

---

## Goal 7 — Improving Ultimate Load / Wire Loss Prediction

**What this means:** Use augmentation-improved DL representations to directly improve prediction of `ultimate_load_kn` or `wire_area_loss_frac`.

**What augmentation is suitable:** Same as Goal 6 — photometric augmentation on the surface model is the only available path, since structural labels exist for only 48 specimens (one per specimen, terminal only).

**What becomes risky:** Treating this as the primary evaluation of augmentation success. The structural prediction problem has an architectural constraint that augmentation cannot fix: LOCO collapse (grouped MAE 0.174 → LOCO 0.564, 3.24×) is driven by campaign confounding — the two campaigns differ in steel mesh count, NaCl concentration, and structural load range simultaneously. No amount of augmentation changes the fact that the model must generalise across campaigns that differ on multiple axes.

The Spearman correlation of `wire_area_loss_frac` LOCO is −0.089 — effectively zero predictive signal under the harshest but most honest split. This is not an augmentation problem; it is a structural confounding problem.

**What success means:** An augmented DL embedding improves `ultimate_load_kn` prediction under **grouped 5-fold CV** (not LOCO). Success under LOCO would require the corrosion signal to transfer across campaign boundaries, which the existing evidence suggests it does not.

**What experiment is required:** Goal 6's experiment, plus a clear reporting protocol that separates grouped CV results (potentially positive) from LOCO results (likely negative due to confounding) and explains the difference honestly.

**Does it match the professor's email?** No. The email does not mention ultimate load, wire area loss, or structural prediction. This goal is not part of the current assignment.

**Verdict:** Real scientific problem, important for the thesis, but outside the scope of what the professor is asking for. Do not introduce it into the first augmentation study.

---

## Comparison Summary Table

| Goal | Right Target | Threshold Wins Unfairly? | Augmentation Helps? | In Professor's Email? |
|---|---|---|---|---|
| 1. Categorical classification | Built-from-scratch labels | Possible | Yes | Loosely (word "classification") |
| 2. `surface_total_rust_pct` regression | No — tautological | **Yes — always** | Cannot fix tautology | Implied, but wrong |
| 3. `peak_rust_pct` regression | **Yes** | No | **Yes — primary path** | Yes (most defensible) |
| 4. Acquisition robustness | `peak_rust_pct` | N/A (different evaluation) | **Yes — core argument** | **Yes — directly** |
| 5. DL vs. threshold comparison | `peak_rust_pct` | No (with right target) | **Yes — enables it** | **Yes — explicitly** |
| 6. Embeddings for structural | `peak_rust_pct` → embeddings | N/A | Yes, indirectly | No |
| 7. Ultimate load improvement | `ultimate_load_kn` (48 rows) | N/A | Cannot fix confounding | No |

---

## What the Professor Most Likely Wants

The professor's explicit request is a comparison study: **DL model vs. threshold red-color quantification**, with augmentation as the mechanism that makes DL viable on this small dataset.

The scientifically correct vehicle for this comparison is `peak_rust_pct` regression, not `surface_total_rust_pct`. The reason: `surface_total_rust_pct` was derived from the same threshold applied to the same images; DL cannot outperform a method that generated the label. `peak_rust_pct` is spatially localised, non-tautological, and the current target in `main_2` — the comparison is fair and falsifiable.

The professor's specific list of techniques (colour balance, noise, blur, brightness, contrast) is not arbitrary; it corresponds exactly to the acquisition conditions that vary across 36 weeks of imaging, and these are the conditions under which the threshold baseline is fragile (empirically: 3–7× change in detected rust under 20% brightness variation) while the DL model can learn invariance.

The professor is also not asking for structural prediction improvement, categorical classification, or LOCO analysis of ultimate load. These are separate problems.

---

## What I Should Do First

**Single objective:** Implement a three-condition comparison for `peak_rust_pct` regression, with photometric augmentation applied to the DL training fold only.

1. Restructure `main_2` so the backbone is called per-batch during training (required for online augmentation — pre-computed embeddings make augmentation structurally impossible).
2. Implement the training transform pipeline: aspect-ratio-aware random crop + horizontal flip + brightness/contrast/saturation jitter + blur + noise.
3. Run three conditions under specimen-grouped 5-fold CV:
   - Condition 1: Threshold baseline (`img_strip_rust_max_pct` from `main_4`)
   - Condition 2: DL without augmentation (inference transforms only)
   - Condition 3: DL with augmentation (training transforms as above)
4. Report MAE and Spearman for all three conditions.
5. Add a secondary evaluation: apply ±20% brightness perturbation to the test set and compare all three conditions — this directly demonstrates acquisition robustness and is the clearest argument for DL.

---

## What I Should Not Mix Into This First Study

| Item | Why it should stay out |
|---|---|
| `surface_total_rust_pct` as a comparison target | Near-tautological label; threshold will always win; comparison is not informative |
| Structural prediction (Goals 6, 7) | Separate problem with 48 labels; campaign confounding dominates; out of scope for this assignment |
| LOCO evaluation as a primary metric | LOCO failure for structural targets reflects design confounding, not augmentation quality; including it without explanation creates misleading conclusions |
| Categorical classification | No categorical labels exist; building them requires a separate design decision; not in the professor's request |
| Offline augmentation (pre-saved images) | Online augmentation is standard for this dataset size and architecture; offline adds disk overhead without benefit |
| Aggressive hue shifts, vertical flips, random erasing | Not in the professor's list; not plausible acquisition variations; no literature support for their benefit here |

---

## Recommended Immediate Augmentation Objective

**Augmentation for `peak_rust_pct` regression in the DL pipeline (main_2), using photometric transforms only, compared against the threshold strip baseline, evaluated under specimen-level grouped holdout.**

This single objective:
- Directly answers the professor's request (DL vs. threshold comparison)
- Uses the correct non-tautological target (peak_rust_pct, not surface_total_rust_pct)
- Applies exactly the transforms the professor listed (brightness, contrast, colour balance, noise, blur)
- Demonstrates why augmentation helps DL but cannot help the threshold (the threshold reads raw pixels; the DL model learns invariance)
- Is achievable with the existing main_2 codebase after restructuring the training loop
- Does not require additional data, new labels, or structural experiments
- Produces a result that can be extended to structural prediction later, without contaminating the primary study

---

*Evidence sources: `main_2/config.py`, `main_2/data.py`, `main_2/train_phase2.py`, `main_4/configs/features.yaml`, `main_4/src/corrosion_proxy_rul/image_features.py`, `outputs/models/surface/`, `outputs/diagnostics/tables/benchmark_best_model_robustness.csv`, pixel statistics measured from actual images, professor's email as interpreted in `Documentation/augmentation_phase1_intent.md`.*

# Augmentation Phase 1 — Advisor Intent Analysis

> **Purpose:** Interpret the advisor's email before designing any augmentation study.
> **Method:** Close reading of email language, cross-referenced against known project state.
> **Date:** 2026-06-27

---

## Advisor Intent

The advisor is not primarily asking for augmentation as a technique. They are asking for augmentation as an enabling step toward a specific comparison: **a deep learning model vs. the threshold-based red-color classification approach**. The core goal is to produce evidence that a learned representation (DL) outperforms a rule-based one (color thresholding), and augmentation is the mechanism proposed to make the DL model viable on a small dataset.

The four stated goals — identify techniques, understand Python implementation, determine how much to augment, implement — are framed as a sequential research task, not as a design question. The advisor expects this to be treated as a literature-driven, principled engineering exercise rather than an open-ended experiment.

The phrase "show the advantage of using deep learning methods" is the load-bearing phrase. The advisor believes that such an advantage exists and that augmentation is what is needed to demonstrate it.

---

## Hidden Assumptions

**Assumption 1: A deep learning model exists or is planned.**
The email refers to "the deep learning model" (definite article), implying a specific model is in scope. This most likely refers to the ResNet18-based pipeline from `main_2`, which used frozen pretrained embeddings as features. Whether the advisor means fine-tuning this model, training a new one, or extending the existing one is not stated.

**Assumption 2: The current baseline is purely threshold-based red-color classification.**
The phrase "automatic classification approach based only on the quantification of the red color" describes the threshold-based pipeline in `main_4`/`main_3`, which computes `img_rust_area_ratio_pct` from a fixed RGB threshold (R∈[25,255], G∈[0,100], B∈[0,80]). The advisor is aware of this approach and treats it as the baseline to beat.

**Assumption 3: The DL model underperforms or is untested because the dataset is too small.**
The advisor implicitly attributes any gap between DL and the threshold baseline to data scarcity, not to a fundamental limitation of the image-to-target relationship. Augmentation is proposed as the fix for this specific cause.

**Assumption 4: The comparison will be on surface-visible corrosion, not structural targets.**
The email refers to "classification" and "quantification of the red color." Both point to surface corrosion targets (`surface_total_rust_pct`, `peak_rust_pct`, rust category labels). Structural targets (`ultimate_load_kn`, `wire_area_loss_frac`) are not mentioned, which suggests the advisor is scoping this to the surface/appearance layer of the problem.

**Assumption 5: Standard augmentation techniques are appropriate and sufficient.**
The advisor lists specific transformations — color balance, noise, blur, brightness, contrast — and describes these as "standard techniques... commonly used in the literature." The implicit assumption is that these are safe to apply without detailed analysis of their interaction with the corrosion measurement labels.

**Assumption 6: Dataset size is the binding constraint.**
The advisor frames the question as "how many augmented images we should generate," treating the problem as one of volume. The possibility that the binding constraint is label quality, campaign confounding, or the structural label bottleneck is not raised.

---

## Hypotheses

The advisor is implicitly proposing two hypotheses, one primary and one secondary.

**Primary hypothesis:** A deep learning model trained with data augmentation will outperform the threshold-based red-color quantification approach for surface corrosion estimation.

**Secondary hypothesis:** The gap between DL and the threshold baseline — if it currently exists — is attributable to insufficient training data, and augmentation will close or reverse it.

Both are testable. Neither is stated explicitly, but both are required for the advisor's framing to be coherent.

---

## Expected Deliverables

Based on the four stated goals, the advisor expects:

1. **A literature-grounded list of augmentation techniques** appropriate for corrosion images, with rationale for why each is suitable or unsuitable.

2. **Python implementation of the selected augmentation methods,** most likely using `torchvision.transforms`, `albumentations`, `PIL`, or `scikit-image`. The advisor expects working code, not pseudocode.

3. **A principled decision on augmentation volume** — specifically, a justified multiplier or total count (e.g., 5× or 10× the original dataset) grounded in literature norms and the specific dataset size.

4. **An augmented dataset or an augmentation pipeline** that produces augmented images on demand during training, integrated with the deep learning training workflow.

The email does not ask for evaluation results, comparison tables, or a paper contribution. It asks for the augmentation infrastructure to be in place. Evaluation is an implied next step, not part of the current assignment.

---

## Success Criteria

The advisor would consider the outcome successful if:

- A DL model trained on augmented data demonstrates measurably better performance than the threshold-based red-color approach on at least one surface corrosion target.
- The augmentation strategy is documented and reproducible (specific transformations, ranges, multipliers, random seeds).
- The augmentation rationale is grounded in literature (precedent for the chosen technique types and dataset expansion ratios).
- The implementation is cleanly integrated with the existing training pipeline.

A weaker form of success — which the advisor would likely still accept — is a demonstration that augmentation improves DL model performance relative to the unaugmented DL baseline, even if the augmented DL does not yet exceed the threshold baseline. This would validate the augmentation direction and set up the next step.

---

## Failure Criteria

The outcome would be considered a failure if:

- The augmented DL model performs worse than or equal to the threshold-based classification on all surface corrosion targets, with no credible path to improvement.
- The augmentation pipeline is implemented but cannot be connected to the DL training workflow without redesigning the architecture.
- The augmented images are unrealistic (e.g., hue-shifted images where rust pixels are no longer visually identifiable as rust), undermining the assumption that augmented labels remain valid.
- The literature review reveals that the chosen transformations are known to harm performance on similar corrosion or material-appearance datasets, making the augmentation strategy scientifically indefensible.

---

## Open Questions

These are questions the email leaves unresolved and that must be answered before any design work begins.

1. **Which deep learning model specifically?** Is the reference to `main_2`'s ResNet18 frozen-feature extractor, a fine-tuned ResNet, a model trained from scratch on corrosion images, or something else? The answer determines what augmentation is applied to (training images in a fine-tuning loop vs. images used to build a feature database).

2. **What is the specific task and target variable?** Is the comparison on `surface_total_rust_pct` (continuous regression), rust category (classification), `peak_rust_pct`, or all three? The task type determines whether augmentation affects only the input (always) or also the label (e.g., for spatial targets like peak rust location).

3. **What is the evaluation protocol?** Does the advisor expect the same specimen-level grouped splits used in the current pipeline, or a simpler random train/test split? The answer determines whether augmented images from the same specimen can appear in the test set — a critical leakage question.

4. **Is the advisor aware that `surface_total_rust_pct` is near-identical to the red-color threshold feature?** The existing pipeline already computes a feature (`img_rust_area_ratio_pct`) with MAE = 0.0002 against the workbook label. If the DL model is benchmarked against the workbook label, the threshold method will be nearly impossible to beat on this specific target because it is the source of the label.

5. **Is the comparison a binary classification, a regression, or both?** The email uses the word "classification" but the current targets are continuous percentages. Clarifying whether the advisor wants categorical outputs (rust category labels) or continuous estimates would change the model architecture and the choice of DL approach.

6. **What counts as "the DL model"?** Is it sufficient to use frozen pretrained features (as in `main_2`), or does the advisor expect end-to-end fine-tuning or training from scratch? Augmentation is much more critical for training-from-scratch than for frozen feature extraction.

7. **What is the intended audience for this comparison?** Is it for the existing paper, a new paper, a thesis chapter, or an internal report? The answer determines the level of rigor required for the comparison (reproducibility, statistical testing, cross-validation vs. single split).

---

## Confidence Level

**On the primary intent:** High. The advisor wants a DL-vs-threshold comparison, with augmentation as the enabling condition. This reading is strongly supported by the phrase "show the advantage of using deep learning methods compared to a more automatic classification approach based only on the quantification of the red color."

**On which target and task:** Medium. Surface corrosion is strongly implied; the specific target variable and whether it is classification or regression is not stated.

**On which DL model:** Low. The email does not name a model or reference `main_2`. The choice of DL architecture is a critical open question.

**On the leakage question:** Low. The advisor does not mention grouped splits or specimen-level evaluation. Whether they are aware of the leakage risk from placing augmented images of the same specimen in both train and test is unknown.

---

## What Information Do I Still Need Before Designing an Augmentation Study?

1. **Confirmation of which deep learning model is in scope** — specifically, whether fine-tuning of a pretrained network (e.g., ResNet18) or training from scratch is intended, and whether the `main_2` architecture is the starting point.

2. **Confirmation of the target variable and task type** — regression on `surface_total_rust_pct` or `peak_rust_pct`, binary/multi-class rust category classification, or all of the above.

3. **Clarification of the evaluation protocol** — in particular, whether the advisor expects specimen-level grouped splits (which prevents augmented test-set leakage) or a simpler image-level random split.

4. **Clarification of what "outperforming the red-color baseline" means** in quantitative terms — which metric (MAE, accuracy, AUC), on which split, at which threshold of improvement.

5. **Whether the advisor is aware that the workbook label `surface_total_rust_pct` was itself derived from threshold-based color analysis** on the same images, which constrains how much any method can outperform the baseline on this specific target.

6. **Whether the comparison is intended for publication** and, if so, which venue — because a reviewer familiar with structural health monitoring will ask about leakage-safe evaluation and about the tautology of using a DL model to predict a label derived from the same images.

# Augmentation Readiness Assessment
## Is The Problem Sufficiently Defined To Begin?

> **Source:** Email exchange between Prof. Erica Lenticchia and Parastoo Hashemi Alvar, June 24–29, 2026.
> **Assessment role:** Senior researcher auditing problem definition before work begins.
> **Date:** 2026-06-29

---

## What the Email Exchange Actually Says

The original email (June 24) and the professor's clarifying reply (June 29) establish the following facts. Only statements explicitly made in the emails are listed here — not inferences, not repository knowledge.

**Stated by the professor, explicitly:**

1. The work is data augmentation for "the image dataset."
2. The purpose is twofold: improve robustness of "the deep learning model," and show DL advantage over automatic classification based on red-color quantification.
3. The augmentation techniques of interest are: colour balance, noise, blur, brightness, contrast, and "other similar variations."
4. The four goals are: identify techniques, understand Python implementation, determine expansion factor from literature, implement.
5. The output is a journal paper.
6. Nissrine is to continue with attention maps — she is not assigned to augmentation.
7. The email is signed by "Erica, Jonathan, Gerardo" — three supervisors or co-supervisors are involved.
8. The DL models are ResNet50 and the Vision Transformer, applied to automatic classification.
9. The automatic classification approach based on the red color was developed with Nissrine and Gerardo.

**That is the complete explicitly stated specification.**

---

## What Is Already Well Defined

### 1. The augmentation task is assigned to Parastoo

**Why it matters:** Assigns responsibility unambiguously. Nissrine is explicitly redirected to attention maps.
**Affects implementation?** Yes — Parastoo builds the augmentation pipeline, not Gerardo or Nissrine.
**Uncertainty level:** None.

### 2. The DL model types are ResNet50 and Vision Transformer

**Why it matters:** These are specific architecture families with different training dynamics, data requirements, and known responses to augmentation. The choice of architecture affects augmentation magnitude (ViTs are more data-hungry than ResNets on small datasets) and training protocol.
**Why it might matter less than expected:** If the models already exist with pre-trained weights, augmentation is added to the fine-tuning step regardless of whether the backbone is ResNet50 or ViT. The insertion point is the same.
**Affects augmentation selection?** Marginally — the magnitude and necessity of augmentation differ between the two architectures, but the technique families themselves are similar.
**Affects experimental design?** Yes — two models means the comparison has at least four conditions (each model, with and without augmentation).
**Uncertainty level:** Architecture family is clear. Specific variant (which ViT?) is not.

### 3. The task is classification

**Why it matters:** Classification requires discrete class labels as training targets. This is fundamentally different from regression. The augmentation pipeline must preserve label validity for categorical outputs. All photometric transforms (brightness, contrast, colour, noise, blur) are label-preserving for classification — the class of a specimen does not change because the image was brightened.
**Affects augmentation selection?** Yes — removes concerns about label corruption from photometric transforms. Geometric transforms (flip, rotation) are also generally label-safe for classification.
**Uncertainty level:** Task type is clear. Class definitions are not.

### 4. The goal is a journal paper

**Why it matters:** This sets the quality bar for reproducibility, statistical rigor, and completeness. It means results must be reported with confidence intervals, splits must be principled, and the study must be defensible to peer reviewers.
**Affects experimental design?** Yes — cannot use a single random train/test split; must use cross-validation or equivalent.
**Uncertainty level:** None.

### 5. The augmentation technique families

The professor named five families: colour balance, noise, blur, brightness, contrast.

**Why it matters:** These are all photometric transforms. They are label-preserving for classification and well-supported in the literature. The professor's list is a reasonable prior for what to include.
**Why it partially constrains the design:** The professor did not exclude other transforms (rotation, flip, crop). The phrase "and other similar variations" explicitly leaves the door open. But the professor did not ask for geometric transforms, GAN synthesis, or MixUp — those require justification if included.
**Affects augmentation selection?** Yes — the professor's list is the expected core; anything beyond it requires explicit justification.
**Uncertainty level:** Low. The exact parameters (brightness range, noise sigma) are open, but that is for the literature review and implementation phase.

---

## What Is Implicitly Defined

### 6. The existing classification work is the baseline

The professor's answer to "what is the automatic classification approach based on red color?" was: "the classification that was developed with Nissrine and Gerardo."

This implicitly defines:
- The baseline is an existing system, not something to be constructed for this study.
- The baseline uses red-color quantification (RGB thresholding or equivalent).
- It was developed jointly — results presumably exist.

**Why it matters:** If the baseline results already exist (accuracy, confusion matrix, etc.), the study does not need to recompute them. If they do not exist in a reproducible form, the baseline must be reconstructed, which is additional work not discussed in the email.
**Affects experimental design?** Yes — the comparison can use existing baseline results if they are available on the same dataset and the same split.
**Uncertainty level:** The fact that a baseline exists is clear. Whether its results are accessible in a form that can be used for the paper comparison is unknown.

### 7. The DL models may already exist

"Improve the robustness" implies the models already have some implementation or trained state. If they were to be built from scratch, the professor would more likely say "train" or "build."

**Why it matters:** If the models already exist and were trained without augmentation, the study adds augmentation to the retraining phase. If the models do not exist in a trainable form, Parastoo must build them from scratch.
**Affects implementation?** Yes — the scope of implementation is fundamentally different depending on whether a codebase already exists.
**Uncertainty level:** Moderate. The professor's language suggests existing work, but does not confirm it.

### 8. Nissrine is working on attention maps of the existing DL model

The professor explicitly redirected Nissrine to attention maps in the same email. This means:
- The DL model being studied with attention maps is likely the same ResNet50 or ViT that will be augmented.
- If Parastoo's augmentation study produces a new version of that model (retrained with augmentation), the attention maps Nissrine is generating may become outdated.

**Why it matters:** This is a coordination dependency, not a technical blocker.
**Affects implementation?** Potentially — if Nissrine's attention maps are on the existing model weights, augmentation-induced retraining changes those weights and the attention maps become inconsistent.
**Affects publication quality?** Yes — a journal paper that shows attention maps from a different model version than the one evaluated in the comparison table contains an inconsistency that reviewers will flag.
**This item requires clarification before the final paper is written, not before augmentation begins.**

---

## What Remains Uncertain

### U1 — The class label definition (critical)

**What is unknown:** What are the categories? How many classes? What are the class boundaries? Who generated the ground-truth labels, and how?

**Why it matters:** No classifier — ResNet50, ViT, or anything else — can be trained without knowing what it is supposed to predict. The class label definition is the foundation of the entire study. If the labels are {no rust / mild rust / severe rust}, the model architecture, class weighting, and evaluation metrics differ from a binary {rust present / rust absent} setup.

**Whether it affects:**
- Augmentation selection? Marginally. Photometric transforms are safe for any categorical classification task. But near-boundary class cases (e.g., a specimen with borderline rust) become more sensitive to aggressive brightness augmentation — more relevant to know if class boundaries are tight.
- Implementation? Yes — the number of output neurons in the classification head, the loss function, and any class weighting strategy depend on this.
- Experimental design? Yes — metrics (accuracy, F1, kappa) are sensitive to class count and distribution.
- Publication quality? Significantly — a paper that does not clearly define its classes is not publishable.

**Can it be assumed?** No. This cannot be inferred from the email exchange.

### U2 — Whether the DL models have an accessible codebase

**What is unknown:** Does Gerardo's ResNet50/ViT implementation exist in a form Parastoo can access and modify? Is it in this repository, a separate repository, or undocumented?

**Why it matters:** If the code exists, Parastoo adds an augmentation pipeline to it. If it does not exist or is inaccessible, Parastoo builds from scratch — a much larger task.
**Can it be assumed?** No. Must be confirmed by checking with Gerardo or finding the codebase.

### U3 — Whether baseline results are accessible

**What is unknown:** Do usable, documented results exist for the red-color classification baseline on the same dataset with the same split?

**Why it matters:** The entire comparison is between the augmented DL model and the baseline. If baseline results are not available in reproducible form, the baseline must be reconstructed — adding significant work not mentioned in the email.
**Can it be assumed?** No. Must be confirmed.

### U4 — The specific ViT variant

**What is unknown:** "Vision Transformer" covers ViT-B/16, ViT-L/32, DeiT-Small, DeiT-Base, Swin-T, and others. The training dynamics, parameter count, and data requirements differ significantly.

**Why it matters:** DeiT-Small (22M parameters) was designed for small-dataset training with augmentation. ViT-B/16 (86M parameters) has a stronger reliance on large-scale pretraining. The choice changes training time, memory requirements, and expected performance without augmentation.
**Affects augmentation selection?** Marginally. Augmentation is more impactful for ViTs in general; which ViT variant has second-order effects.
**Affects experimental design?** Yes — training compute budget differs.
**Can it be assumed?** For now, yes — DeiT-Small is a defensible choice for this dataset size and can be stated as the implementation decision subject to review.

### U5 — The dataset split strategy

**What is unknown:** No split has been specified. Are train/val/test folds agreed? Are the same splits used for the DL models and the baseline?

**Why it matters:** The comparison is only valid if all conditions use identical test specimens. If the DL model and the baseline were evaluated on different test sets, the comparison is meaningless.
**Affects experimental design?** Yes — this must be resolved before any training begins.
**Can it be assumed?** Partially. Specimen-level grouped splits are the only scientifically defensible choice for this dataset (as documented in the existing repository analysis). Whether this is what Nissrine and Gerardo used for the baseline is unknown.

---

## What Information Is Genuinely Necessary

These are blocking. Without them, the study cannot begin in a technically correct way.

| Item | Why it is blocking |
|---|---|
| Class label definitions | Cannot train any classifier without knowing the output categories and their source |
| Access to existing DL codebase | Cannot add augmentation to a model that cannot be found |
| Confirmation that baseline results exist and are accessible | The comparison is the study; no comparison means no paper |
| Whether the existing DL models used specimen-level splits | Must be confirmed to ensure the comparison is conducted on identical evaluation conditions |

---

## What Information Is Helpful But Not Required

These are useful but do not block the study from starting.

| Item | Why it helps without blocking |
|---|---|
| Specific ViT variant | Can be decided from literature; DeiT-Small is a reasonable default |
| Class distribution (how many samples per class) | Helps choose evaluation metrics and class weighting, but these decisions can be made after seeing the data |
| Exact augmentation parameters (brightness range, noise sigma) | Determined from literature review, which is Goal 1 of the professor's assignment |
| Whether augmented images should be stored offline or generated online | Implementation choice; can be decided during implementation phase |

---

## What Information Is Probably Irrelevant

These are facts that exist in the repository or in context but do not affect this specific study.

| Item | Why it is irrelevant |
|---|---|
| Structural prediction (ultimate load, wire loss, RUL) | Explicitly ruled out by the professor: "we will avoid it for now" |
| Specimen mapping and campaign confounding analysis | Relevant to structural prediction; not relevant to surface classification |
| The tautology issue with `surface_total_rust_pct` | Relevant to regression; this study is classification |
| LOCO collapse (MAE=0.174 vs 0.564) | Structural prediction result; not relevant to classification |
| The main_4 pipeline and proxy-RUL | Out of scope |
| Parastoo's existing ultimate load model | Explicitly ruled out |

---

## Current Understanding

After reading the email exchange precisely and applying no assumptions beyond what is stated:

The professor has assigned Parastoo to apply data augmentation to a corrosion severity classification task, using ResNet50 and a Vision Transformer as the DL models, in order to show that these augmented DL models outperform an existing automatic classifier based on red-color quantification. The classifier to be beaten was developed collaboratively with Nissrine and Gerardo. Nissrine is separately working on attention maps of the existing DL model. The output is a journal paper. The augmentation technique families of interest are photometric: colour balance, noise, blur, brightness, contrast.

---

## Assumptions I Can Safely Make

1. The task is image classification with discrete severity categories — not regression, not segmentation.
2. All five photometric transform families listed by the professor are applicable and label-safe for classification.
3. ImageNet pretrained weights are the starting point for both ResNet50 and ViT.
4. The study requires a hold-out test set that is identical for all conditions (including the baseline).
5. The dataset is the 791-image corrosion specimen image collection in this repository.
6. The paper will report accuracy-based metrics and some form of cross-validation.

---

## Assumptions I Should Not Make

1. **That the class labels are defined.** This is the most dangerous assumption to make. Do not assume binary rust/no-rust, do not assume four severity classes, do not assume anything. The class definition controls the entire study.
2. **That the existing baseline results can be used directly.** The baseline may have been evaluated on a different split or with a different evaluation protocol.
3. **That the DL codebase is accessible.** "Developed with Gerardo" does not mean "available in this repository."
4. **That Nissrine's attention maps were generated from the model that augmentation will modify.** If augmentation produces a new model, the attention maps may become stale.
5. **That the dataset split used by Nissrine and Gerardo matches what is appropriate for the journal paper.** The existing repository uses specimen-level grouped splits; whether their work used the same protocol is unknown.
6. **That "other similar variations" in the professor's email invites geometric transforms.** It may — or it may mean other photometric operations. Do not add flips and rotations to the "confirmed" list until clarified or until literature review justifies them.

---

## Information That Is Essential

Three items. In priority order.

**1. Class label definitions.** What categories exist? How many? How are they named? What are the boundaries (if derived from continuous measurements)? Who generated the training labels, and how? This is the single most important missing piece.

**2. The existing DL codebase.** Where is it? Is it in this repository (main_2?), Gerardo's repository, or undocumented? What training protocol was used? What pretrained weights?

**3. Whether the baseline evaluation is reusable.** Do Nissrine and Gerardo's existing results include a confusion matrix or accuracy figure on a reproducible, documented test set? If yes, what split was used?

---

## Information That Is Helpful But Not Required

- The specific ViT variant.
- The class distribution (how many images per class).
- Whether offline or online augmentation is preferred.
- Augmentation parameter ranges (determined during literature review).
- The target journal.

---

## Information That Is Probably Irrelevant

Everything outside the classification task: structural prediction, RUL, wire loss, campaign confounding at the structural level, and any analysis from main_4 that was developed for regression targets.

---

## Minimum Knowledge Needed To Start The Augmentation Study

Two things only:

1. **The class label definitions** — without these, no training can begin.
2. **The location of the existing DL codebase** — to know whether the augmentation pipeline is built alongside existing code or from scratch.

Everything else — augmentation parameters, expansion factor, ViT variant, statistical tests — can be determined during the study. But these two items cannot be inferred, assumed, or deferred.

---

## Suggested Next Step

A single conversation with Gerardo, specifically asking:

1. What are the class categories for the corrosion classification task?
2. Where is the existing ResNet50/ViT codebase?
3. What split was used for the existing baseline results (and can those results be used directly in the journal paper comparison)?

This conversation takes fifteen minutes and unblocks the entire study. The literature review (Goals 1 and 3 in the professor's email) can proceed in parallel, since it does not depend on the class labels.

---

## If I Were Your Co-Supervisor, What Would I Investigate Next?

The question I would prioritise before anything else is not about augmentation — it is about the baseline.

The professor says the comparison is between augmented DL and "the classification that was developed with Nissrine and Gerardo." That classification is described as based on the quantification of the red color. If that classification was built by applying the RGB threshold and then assigning categories based on threshold-derived percentages, then the class labels in the training set were generated by the same method that defines the baseline.

This creates a risk that is not stated anywhere in the email exchange: **if the DL model is trained on labels derived from the threshold, it learns to replicate the threshold, not to exceed it.** In that case, augmentation cannot produce a DL model that outperforms the baseline, because the baseline is the oracle for its own labels.

This is not certain — it depends on how the class labels were generated. But it is the first thing I would check before writing a single line of code. The scientific validity of the entire comparison depends on the answer.

If the labels were generated by manual annotation of rust severity (independently of the threshold), the comparison is clean and the study can proceed. If the labels were generated by thresholding the RGB measurement and then assigning severity categories, the study needs either a different label source or a different framing of the scientific question.

This is the question I would bring to Gerardo, before the augmentation technique selection, before the literature review, and before any code is written.

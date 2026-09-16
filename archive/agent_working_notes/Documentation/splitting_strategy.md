# Splitting Strategy for the Augmented Corrosion Image Dataset

> **Scope:** Journal-quality four-class corrosion severity classification using ResNet50 and ViT.
> **Dataset:** 48 specimens, 791 original images, 4,746 rows after 5× offline augmentation.
> **Target:** `A_Total_Rust_Category_(1–4)`

---

## 1. The Apparent Conflict and Its Resolution

The three requirements stated in the problem are:

1. Augmented copies must stay with their original specimen.
2. Validation and test must contain original images only.
3. Every augmented row must appear in exactly one split.

Requirements 1 and 2 are scientifically valid and non-negotiable. Requirement 3 is not valid. It is the source of the apparent conflict, and it should be dropped.

The correct formulation of requirement 3 is:

> **Every original image must appear in exactly one split. Augmented copies that belong to non-training specimens are excluded from all splits.**

Once requirement 3 is restated correctly, the conflict disappears. Option A is the correct protocol.

---

## 2. Why Augmented Copies Are Not Part of the Evaluation Dataset

Augmentation is a training-time operation. Its purpose is to regularise the training set by showing the model photometric variants of training specimens. It has no role in evaluation.

The offline augmented dataset in `Data/Images_dataset_augmented/` was generated for convenience — it applies the five recipes to all 791 source images so that the output is stable and reproducible before the split is decided. This does not mean the augmented copies are equal members of the dataset. They are derivative artifacts of the training set. Their logical scope is: **the training specimens, only**.

An analogy: if you augment a training set online (at training time), augmented images of val/test specimens are never generated at all. Offline augmentation should replicate exactly the same behavior. The fact that augmented copies of val/test specimens happen to exist in the CSV is an implementation detail of the offline approach, not a scientific claim that those copies should be used.

---

## 3. Analysis of Each Option

### Option A — Exclude augmented copies of val/test specimens

**Procedure:** Assign specimens to train/val/test. For training specimens, use all rows (`is_augmented == True` and `is_augmented == False`). For val/test specimens, use only `is_augmented == False` rows. Augmented rows from val/test specimens are excluded entirely.

**Leakage:** None. The model never sees any image — original or augmented — from a val/test specimen during training.

**Literature convention:** Universal. Every benchmark that uses offline augmentation (ImageNet training, CIFAR, medical imaging datasets) follows this protocol. Augmented images never appear in val or test sets.

**Fairness:** Complete. Val and test reflect the real-world distribution: unaugmented, natural images. The evaluation measures performance on images that look exactly like images the model will encounter in deployment.

**Reproducibility:** Clean and unambiguous. The split manifest states: train rows are all rows for train specimens; val/test rows are original rows only for the respective specimens; excluded rows are identified by specimen_id and listed in the split report.

**Downstream training:** No practical disadvantage. With 48 specimens split approximately 38/5/5, approximately 627 original training images remain. With augmentation, the training set expands to approximately 627 + (627 × 5) = 3,762 rows. This is the expansion that matters.

**Verdict: Correct. This is the only scientifically valid option.**

---

### Option B — Assign augmented copies of val/test specimens to train

**Procedure:** Val/test specimens' augmented copies are moved into the training split.

**Leakage analysis:** This option causes leakage. The model trains on augmented versions of the same physical specimens it is evaluated on during validation and testing.

The leakage operates through specimen-specific visual features. A corroding ferrocement specimen has a characteristic rust pattern — location, texture, spatial distribution — that persists across time-steps and across photometric augmentations. Brightness-adjusted, blur-filtered, or flipped copies of a val/test specimen's images still contain this specimen's visual signature. A model trained on these copies learns specimen-specific features. When evaluated on the original images of the same specimen, it benefits from having seen that specimen's rust pattern during training.

This is not a hypothetical concern. Specimen-level leakage is exactly why grouped specimen-level splits are mandatory for this dataset (and explicitly documented in `CLAUDE.md`). Option B reintroduces the leakage through the back door of augmentation.

**Verdict: Invalid. Cannot be used in a journal paper.**

---

### Option C — Include augmented images in val/test

**Procedure:** Val/test splits contain both original and augmented images of val/test specimens.

**Problems:**

1. **Evaluation validity:** Val/test must measure performance on the real-world distribution. Augmented images are artificial variants; they are not drawn from the deployment distribution. Including them inflates or distorts the measured performance on easy photometric variants.

2. **Double evaluation:** Each specimen's rust progression would be evaluated multiple times with photometric variants, giving some specimens disproportionate weight in the evaluation.

3. **Universal convention:** No published classification benchmark includes augmented images in the test set. This would be flagged immediately in peer review.

**Verdict: Invalid. Contradicts the purpose of held-out evaluation.**

---

### Option D — Handle differently

The only scientifically meaningful "different" approach is to redesign the augmentation pipeline to augment training specimens only, after the split is determined. In that design, augmented copies of val/test specimens would simply not be generated.

The current offline design pre-generates augmented copies of all 791 source images for reproducibility. Option A replicates the logical outcome of a training-only augmentation pipeline within the offline framework. It is equivalent to Option D in all scientifically relevant respects.

**Verdict: Option A is the correct implementation of Option D for an offline pipeline.**

---

## 4. Exact Numbers for the Recommended Protocol

Based on the measured dataset (48 specimens, 791 originals, 15–18 images per specimen):

| Specimen allocation | Specimens | Original images | Augmented rows | Split rows |
|---|---|---|---|---|
| Train | 38 | ~627 | ~3,135 | ~3,762 |
| Validation | 5 | ~82 | excluded (410 rows discarded) | ~82 |
| Test | 5 | ~82 | excluded (410 rows discarded) | ~82 |
| **Total** | **48** | **791** | **3,955** | **3,926** |

Rows excluded: approximately 820 (augmented copies of val/test specimens). These 820 rows are not assigned to any split. They exist in the CSV and are skipped during split construction.

The training set still achieves a 6× expansion over the training originals (3,762 / 627 ≈ 6.0×). The excluded rows do not reduce the training augmentation ratio; they simply confirm that augmentation was applied to training specimens only.

---

## 5. The Class Imbalance Complication

The split cannot be constructed by random specimen allocation. The class distribution at the specimen level is severely imbalanced:

| Maximum label reached by specimen | Specimens | Images |
|---|---|---|
| 1 only | 16 | ~256 |
| 2 (reached at least once) | 22 | ~363 |
| 3 (reached at least once) | 5 | ~82 |
| 4 (reached at least once) | 5 | ~82 |

With only 5 specimens that ever reach label 3 and 5 that ever reach label 4, a random split at the specimen level can easily produce a test set with zero label-3 or label-4 examples. A model that predicts label 1 for every image would achieve 83.2% accuracy on such a test set, which is scientifically uninformative.

**Required protocol: stratified specimen-level splitting.**

Stratify by the maximum label reached by each specimen. Allocate specimens so that each split contains at least one specimen from each rare class:

| Label stratum | Train | Val | Test |
|---|---|---|---|
| Max = 1 (16 specimens) | 14 | 1 | 1 |
| Max = 2 (22 specimens) | 18 | 2 | 2 |
| Max = 3 (5 specimens) | 3 | 1 | 1 |
| Max = 4 (5 specimens) | 3 | 1 | 1 |
| **Total** | **38** | **5** | **5** |

This allocation ensures:
- Every split contains specimens that progress through labels 3 and 4
- No split is trivially dominated by label-1 specimens
- The rare class specimens are represented in evaluation
- The train/val/test ratio is 79% / 10% / 10% at the specimen level

This also means the test set will contain label-3 and label-4 images, making the evaluation metrics (balanced accuracy, macro F1) informative rather than trivially dominated by the majority class.

**Important:** Within each stratum, the assignment of specific specimens to train/val/test must be deterministic (fixed seed) and documented. The paper must report exactly which specimens are in each split so that the results are reproducible and other researchers can use the same evaluation protocol.

---

## 6. Implementation Guidance for `make_splits.py`

The split script must implement the following logic:

```
1. Load the augmented CSV.

2. Compute each specimen's max_label (maximum A_Total_Rust_Category_(1–4) observed
   across all its original rows).

3. Stratify specimens by max_label into four strata.

4. Within each stratum, sort specimens deterministically (alphabetical by specimen_id)
   and allocate to train/val/test according to the table in Section 5.
   Use the fixed seed only if random allocation within stratum is needed.

5. For each split:
   - Train: all rows (is_augmented == True and False) for train specimens
   - Val: only is_augmented == False rows for val specimens
   - Test: only is_augmented == False rows for test specimens

6. Augmented rows from val/test specimens: not assigned to any split.
   Record them in the split report as "excluded_augmented_rows".

7. Validate:
   - No specimen_id appears in more than one split.
   - No augmented image appears in val or test.
   - All 791 original rows appear in exactly one split.
   - The sum of train + val + test rows + excluded rows equals 4,746.
   - Each split contains at least one specimen per label stratum.

8. Write:
   - Data/splits/train_manifest.csv
   - Data/splits/val_manifest.csv
   - Data/splits/test_manifest.csv
   - Documentation/codex/split_report.md
```

The split report must state: which specimens are in each split, how many original and augmented rows per split, how many augmented rows were excluded and why, and the stratification rationale.

---

## 7. Evaluation Protocol Implications

**Metrics:** Because the test set remains highly imbalanced (label-1 images outnumber label-4 images even after stratified specimen allocation), standard accuracy is uninformative. Use:
- Balanced accuracy (arithmetic mean of per-class recall)
- Macro F1 (unweighted mean of per-class F1)
- Cohen's Kappa (chance-corrected agreement)
- Per-class confusion matrix

**Baseline comparison:** The red-color threshold baseline must be evaluated on the exact same test set. If Gerardo's baseline results were computed on a different split, the comparison requires rerunning the baseline on the new test set. A comparison between a model evaluated on test set A and a baseline evaluated on test set B is not scientifically valid and will be rejected in peer review.

**Augmentation ablation:** The augmentation effect is measured by comparing condition C2 (ResNet50, no augmentation) and condition C3 (ResNet50, with augmentation) on the same test set. Because the test set uses only original images, the evaluation is fair: the model with augmentation is measured on natural images, not on augmented ones. This is the correct experimental design for showing that augmentation improves generalisation.

---

## 8. Summary

| Requirement | Status | Action |
|---|---|---|
| Augmented copies stay with their specimen | Met | Augmented rows follow their specimen_id |
| Val and test contain originals only | Met | Filter to is_augmented == False for val/test |
| No leakage | Met | No train/val/test overlap at specimen level |
| Augmented copies of val/test specimens | **Excluded** | Not assigned to any split |
| Stratified by specimen severity | Required | Stratify by max_label before allocation |
| Reproducible | Required | Deterministic allocation, document specimen list |

**The answer to the question is Option A.** Augmented images from val/test specimens are excluded entirely. This is not a compromise — it is the only protocol consistent with standard machine learning practice, specimen-level leakage prevention, and the requirements of a journal-quality comparative study.

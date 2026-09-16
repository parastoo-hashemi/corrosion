# Augmentation Research Plan
## Four-Class Corrosion Severity Classification — ResNet50 and Vision Transformer

> **Task:** Data augmentation study for the automatic corrosion classification developed with Nissrine and Gerardo.
> **Models:** ResNet50, Vision Transformer (ViT / DeiT).
> **Baseline:** Automatic four-class classification based on red-color quantification.
> **Goal:** Journal-quality comparison study.
> **Date updated:** 2026-06-30
> **Literature evidence:** Web search conducted 2026-06-30. Sources marked as *Established*, *Emerging*, or *Speculative* per evidence strength.

---

## Scientific Question

> **Does photometric data augmentation — specifically colour balance, brightness, contrast, blur, and noise — enable ResNet50 and Vision Transformer classifiers to outperform a red-color quantification baseline for four-class corrosion severity classification on a small ferrocement specimen image dataset?**

A secondary question is embedded in the study design:

> **Between ResNet50 and Vision Transformer, which architecture benefits more from augmentation when trained on a small corrosion image dataset, and does the benefit of augmentation differ between them in a measurable and explainable way?**

Both questions are answerable with the available data, require no new specimens, and produce results that are relevant to the broader domain of DL-based structural inspection.

---

## Hypothesis

### Primary Hypothesis

ResNet50 and Vision Transformer classifiers trained with photometric augmentation achieve higher four-class balanced accuracy than the red-color quantification baseline on held-out specimens not seen during training, under a specimen-level grouped evaluation protocol.

### Secondary Hypothesis

The Vision Transformer benefits more from augmentation (in absolute accuracy gain) than ResNet50, because ViTs lack the local inductive biases of CNNs and are more reliant on data diversity to learn discriminative texture features on small datasets.

*Literature basis:* Confirmed as established practice — ViTs are documented to underperform CNNs on small datasets without augmentation, and DeiT (Touvron et al., 2021) was specifically designed around the finding that strong augmentation closes this gap. The MDPI Applied Sciences study on ViT for industrial inspection confirms that "vision transformers can be more reliant on data augmentation with smaller training datasets."

### Null Hypotheses (for statistical testing)

- H₀₁: Augmentation does not significantly improve ResNet50 accuracy over the unaugmented ResNet50 baseline.
- H₀₂: Augmentation does not significantly improve ViT accuracy over the unaugmented ViT baseline.
- H₀₃: Neither augmented model significantly outperforms the red-color classification baseline.

---

## Literature Review

### Relevance Ranking

| Rank | Domain | Relevance to This Study |
|---|---|---|
| 1 | Corrosion classification with DL | Direct domain match |
| 2 | Surface defect detection — CNN and ViT | Same task structure, comparable dataset sizes |
| 3 | Augmentation for Vision Transformers | Architecture-specific, directly relevant to ViT conditions |
| 4 | Industrial inspection — small datasets | Dataset size regime matches |
| 5 | Augmentation for CNNs — general | Provides parameter norms |
| 6 | Multi-class severity classification | Task structure match |
| 7 | Hybrid CNN+ViT approaches | Context for interpreting results |

---

### Domain 1 — Corrosion Classification with Deep Learning

**What to extract:** Which architectures achieve what accuracy on multi-class corrosion tasks? What augmentation was used, and at what expansion factor?

**Established findings from literature:**

- *PMC11829104* (EfficientNetB0, above-ground storage tank corrosion): original ~800 images augmented to ~5,000 (6.25×); augmentation included rotation, brightness, shear, zoom, channel shifts, flips; final accuracy 94%. Augmentation applied offline.
- *PMC11175235* (autonomous steel corrosion detection): 100 images expanded 20× using horizontal flip, vertical flip, translation, grid distortion; demonstrates feasibility of aggressive expansion on very small datasets.
- *Hybrid-DC (MDPI Electronics, 2024)*: ResNet50 + ViT hybrid for steel surface defect classification achieved 0.9944 validation accuracy; direct precedent for using both architectures together.
- *ResNet50 binary corrosion classification*: 96.58% accuracy with augmentation. VGG16 + ResNet50 on 900 corrosion images achieved 98% recall.
- *YOLOv8n-cls for four-class corrosion severity*: directly applied to hydraulic steel structures; four-class severity assessment using transfer learning; confirms that four-class corrosion severity is an established task.
- *Inception-v3 for corrosion severity on steel*: >95% accuracy; confirms multi-class corrosion severity is feasible with pretrained CNNs.

**Evidence quality:** Established.

---

### Domain 2 — Surface Defect Detection — CNN and ViT

**What to extract:** How does augmentation affect CNN vs. ViT performance when dataset size is below 5,000 images?

**Established findings:**

- *Hybrid CNN+Transformer for strip steel (ResearchGate, 2022)*: hybrid architecture combining local CNN features with global ViT attention improves upon either alone.
- *LMViT for steel defect detection (CMC, 2025)*: Learnable Memory ViT; augmentation plus t-SNE analysis; confirms that augmentation mitigates overfitting and stabilises ViT training on small industrial datasets.
- *MDPI Applied Sciences, ViT for industrial inspection (2022)*: "CNNs are often safer in smaller or medium-sized data settings because their inductive bias helps them learn useful structure more efficiently." ViTs tend to require large-scale pre-training, strong augmentation, or architectural modification to match CNNs on small datasets.

**Evidence quality:** Established for CNNs; Established but context-dependent for ViTs.

---

### Domain 3 — Augmentation for Vision Transformers

**What to extract:** What augmentation strategy is recommended specifically for ViTs? How does it differ from CNN augmentation?

**Established findings:**

- *DeiT (Touvron et al., 2021)*: ViT trained data-efficiently on ImageNet-1K using: RandAugment, random erasing, Mixup, CutMix, repeated augmentation, stochastic depth. Achieved 84.2% top-1 accuracy without external data on a single 8-GPU server. This is the canonical reference for "augmentation is necessary for ViT on moderate-scale data."
- *Compact Transformers (arXiv 2104.05704)*: sequence pooling and other tricks allow ViT variants to train from scratch on small datasets without extensive augmentation, at the cost of model capacity.
- *ViT for Small-Size Datasets (arXiv 2112.13492)*: structural modifications (shifted patch tokenisation, locality self-attention) allow ViTs to learn effectively from small datasets.

**Relevance to this study:** ViT will be used with ImageNet pretrained weights (transfer learning), which partially alleviates the small-dataset limitation. However, augmentation during fine-tuning remains important for ViT to generalise to the corrosion domain. The DeiT training recipe (minus CutMix and Mixup, which are complex for classification) provides the reference augmentation protocol.

**Evidence quality:** Established.

---

### Domain 4 — Industrial Inspection on Small Datasets

**What to extract:** What is the practical range of training set sizes in comparable studies, and what augmentation achieves acceptable performance?

**Established findings:**

- Multiple studies achieve >90% accuracy on surface defect classification with 1,000–5,000 training images using pretrained CNNs with photometric augmentation.
- Transfer learning from ImageNet is the dominant strategy; fine-tuning the full model or the last block(s) is standard.
- Dataset sizes below 1,000 training images (before augmentation) are common in specialist inspection tasks and are considered addressable with augmentation + transfer learning.

**Evidence quality:** Established.

---

### Domain 5 — Augmentation for CNNs — Parameter Norms

**What to extract:** What parameter ranges are used in practice?

| Transform | Reported range | Source type |
|---|---|---|
| Brightness | ±20–30% (factor 0.7–1.3) | Established |
| Contrast | ±15–25% (factor 0.75–1.25) | Established |
| Saturation | ±20% | Established |
| Gaussian blur | σ 0.1–2.0, kernel 3–5 px | Established |
| Gaussian noise | σ 0.01–0.05 normalised | Established |
| Horizontal flip | p=0.5 | Established |
| Rotation | ±5–15° | Established |

**Evidence quality:** Established.

---

### Domain 6 — Multi-Class Severity Classification

**What to extract:** How is four-class severity defined and evaluated in comparable studies?

**Established findings:**

- Four-class severity (none / mild / moderate / severe) is a common scheme in corrosion and structural damage assessment.
- Class boundaries are typically defined by rust coverage percentage or ASTM D610 rust grade standards.
- Balanced accuracy and macro F1 are the appropriate primary metrics when class imbalance is expected (early-stage specimens dominate in time-series datasets).
- Cohen's Kappa is reported in studies where ordinal agreement is scientifically relevant.

**Evidence quality:** Established.

---

## Augmentation Strategy

All augmentations are evaluated for a **four-class corrosion severity classification** task. Labels are discrete categories. All photometric transforms are inherently label-preserving for categorical classification — the severity class of a specimen does not change because the image is brightened or blurred.

---

### Recommended

These five augmentations directly correspond to the professor's specified technique families. All are established practice for corrosion and industrial inspection classification.

---

**1. Brightness variation**

| Property | Detail |
|---|---|
| Scientific rationale | Outdoor and semi-outdoor corrosion imaging produces lighting variation across sessions, seasons, and time of day. A model that classifies by absolute pixel intensity rather than by texture and colour pattern will fail under natural lighting change. |
| Literature prevalence | Universal — present in PMC11829104, PMC11175235, DeiT training protocol, and virtually all surveyed industrial inspection studies. *Established.* |
| Expected benefit | Teaches the model to classify rust severity from texture and relative colour rather than from absolute pixel brightness. The red-color baseline is empirically fragile to this variation: a 20% brightness reduction was measured to change the threshold-detected rust fraction by 3–7× on actual specimens from this dataset. Augmented DL models learn invariance the baseline cannot provide. |
| Risk | Extreme darkening (>40%) can make a non-corroded concrete surface appear rust-coloured by pushing pixels toward the lower end of the red-color range. Keep within ±30%. |
| Implementation complexity | Trivial. |
| Parameter range | Factor ∈ [0.70, 1.30]; apply independently per image. |

---

**2. Contrast variation**

| Property | Detail |
|---|---|
| Scientific rationale | Camera sensor response, image compression, and surface reflectance variation produce contrast differences across imaging sessions. Contrast variation teaches the model to be robust to edge-sharpness differences that do not reflect rust severity. |
| Literature prevalence | High — standard companion to brightness in all reviewed augmentation pipelines. *Established.* |
| Expected benefit | Regularises against contrast-specific overfitting; improves performance on low-contrast images at early corrosion stages. |
| Risk | Very low contrast merges rust and concrete visual boundaries; high contrast exaggerates texture differences artificially. Moderate ranges are safe. |
| Implementation complexity | Trivial. |
| Parameter range | Factor ∈ [0.75, 1.25]. |

---

**3. Colour balance / Saturation**

| Property | Detail |
|---|---|
| Scientific rationale | Camera white balance and surface wetness change colour saturation. Rust colour shifts from vivid orange-red (fresh) to desaturated brown (aged). Saturation variation teaches the model to classify rust severity from spatial distribution and morphology, not only from colour vividness. |
| Literature prevalence | High — PMC11829104 uses channel shift augmentation (equivalent); standard in corrosion DL literature. *Established.* |
| Expected benefit | Robustness to saturation-based visual variation across the 36-week imaging timeline; particularly useful for distinguishing mild vs. moderate rust where both have reddish hue but different coverage patterns. |
| Risk | Heavy desaturation causes rust to appear identical to concrete at severe desaturation levels; heavy oversaturation creates unrealistic images. Moderate range is safe. |
| Implementation complexity | Trivial. |
| Parameter range | Factor ∈ [0.70, 1.30]. |

---

**4. Gaussian blur**

| Property | Detail |
|---|---|
| Scientific rationale | Camera focus variation, different capture distances, and motion in the imaging setup produce blur variation in real images. Blur augmentation teaches multi-scale feature representation and prevents the model from relying on high-frequency texture details that vary with capture conditions. |
| Literature prevalence | High — used in DeiT protocol, industrial inspection studies. *Established.* |
| Expected benefit | Regularisation; improved generalisation to images captured under non-ideal focus conditions; particularly useful for ViT, which processes image patches and may otherwise over-rely on fine-grained patch-level texture. |
| Risk | Strong blur removes discriminative rust texture. Keep blur mild. |
| Implementation complexity | Trivial. |
| Parameter range | σ ∈ [0.1, 1.5], kernel 5×5; apply at p = 0.5. |

---

**5. Gaussian noise**

| Property | Detail |
|---|---|
| Scientific rationale | Camera sensor noise, especially at lower ISO settings or in uncontrolled lighting, introduces pixel-level noise that varies across imaging sessions. Noise augmentation teaches the model that fine-grained pixel values carry noise and that classification should rely on higher-level features. |
| Literature prevalence | High — standard in all small-dataset augmentation surveys. *Established.* |
| Expected benefit | Regularisation effect; reduces sensitivity to imaging session–specific pixel artefacts; particularly useful for ViT, whose patch-level input is directly affected by pixel noise. |
| Risk | High noise obscures rust texture at early-stage specimens where rust coverage is low; keep sigma small. |
| Implementation complexity | Low — requires a custom `GaussianNoise` transform (not built into torchvision; one-line implementation with `torch.randn_like`). |
| Parameter range | σ ∈ [0.01, 0.04] in normalised [0,1] pixel space. |

---

### Potentially Useful

These are label-safe for classification and appear in related literature, but carry a secondary risk or have lower expected benefit for this specific dataset.

---

**6. Horizontal flip**

| Property | Detail |
|---|---|
| Scientific rationale | The ferrocement specimen has no left-right semantic asymmetry relevant to rust severity classification. Flip effectively doubles training set size at no cost. |
| Literature prevalence | Universal. *Established.* |
| Expected benefit | Highest diversity gain per transform; the easiest augmentation to justify. |
| Risk | None for classification. The peak rust location column (`B_Location_of_Peak_Rust_in_length_[cm]`) would need to be reflected if used as an input feature — but classification does not use this column. |
| Implementation complexity | Trivial. |
| Parameter range | p = 0.5. |
| Note | Not in the professor's explicitly listed families; include in ablation to quantify contribution. |

---

**7. Small rotation**

| Property | Detail |
|---|---|
| Scientific rationale | Camera tilt variation during specimen imaging introduces slight rotational differences across sessions. |
| Literature prevalence | Moderate — used in PMC11829104, standard in defect detection. *Established.* |
| Expected benefit | Rotational robustness; slightly improves generalisation. |
| Risk | Corner fill artefacts at larger angles. **Must use reflect or replicate fill mode — not zero fill (black corners)**. Black corners have been documented to be confused with dark corrosion regions in corner-sensitive models. |
| Implementation complexity | Low. |
| Parameter range | ±5–10°, fill = `reflect`, p = 0.3. |

---

**8. Random crop (aspect-ratio-aware)**

| Property | Detail |
|---|---|
| Scientific rationale | The specimen images are 2835×650 pixels (4.36:1). Standard ResNet50 and ViT transforms center-crop to 224×224, using only the central ~22% of specimen width. Random crops expose the model to rust patterns at different longitudinal positions along the specimen. |
| Literature prevalence | Universal for classification. *Established.* |
| Expected benefit | Largest domain-specific benefit of any geometric transform for this dataset — effectively multiplies the number of distinct training views per image. |
| Risk | A crop may sample a low-rust region of a specimen classified as "severe," creating an apparent mismatch between visible content and class label. This is a valid learning challenge, not a label error — severity is a specimen-level property. Convergence may require more epochs. |
| Implementation complexity | Low — resize height to 256 (preserving aspect ratio), apply `RandomCrop(224)` during training; `CenterCrop(224)` at inference. |
| Parameter range | Crop size: 224×224 from resized 256-height image. |

---

**9. Hue shift (small)**

| Property | Detail |
|---|---|
| Scientific rationale | Rust oxidation state shifts hue from orange-red (fresh) toward reddish-brown (aged). Small hue variation teaches the model not to classify rust severity purely by hue. |
| Literature prevalence | Moderate. *Established at small ranges.* |
| Expected benefit | Mild — most discrimination between severity classes comes from coverage area, not hue. |
| Risk | Hue shift >±0.1 (18° on the hue circle) can move rust pixels outside their plausible colour range (rust appears yellow or purple). Keep conservative. |
| Parameter range | ±0.05 (9°); apply at p = 0.3. |

---

### Risky

Include only in the ablation study to measure whether they help or hurt. Do not include in the primary recommended pipeline.

---

**10. Random erasing / Cutout**

| Property | Detail |
|---|---|
| Scientific rationale | None specific to this task. |
| Risk | Removes real rust pixels from the image while the class label (e.g., "moderate rust") stays unchanged. If the erased region contains the primary visual evidence for the class, the model sees contradictory training data. The risk is highest for specimens in the mild and moderate severity classes, which have limited rust coverage. |
| Verdict | Ablation only. Literature for defect detection occasionally uses it, but the label integrity risk is non-trivial when classes are defined by rust coverage. |

---

**11. Vertical flip**

| Property | Detail |
|---|---|
| Scientific rationale | None for a horizontal concrete slab photographed from above. |
| Risk | Produces images with the specimen appearing upside-down. Not a plausible acquisition condition. Adds diversity without adding physically relevant variation. |
| Verdict | Low benefit, low risk, low scientific justification. Include in ablation to confirm marginal or zero benefit. |

---

**12. Large rotation (>±15°)**

| Property | Detail |
|---|---|
| Risk | Creates large fill regions at image corners. Even with reflect fill, angles >15° distort the specimen geometry significantly. Not a plausible camera variation for a mounted imaging setup. |
| Verdict | Do not use. |

---

### Unsuitable

These are not appropriate for the study scope. Briefly explained.

| Transform | Reason |
|---|---|
| **MixUp** | Interpolates between class labels — creates fractional class labels (60% "mild" + 40% "moderate") that are meaningless for discrete severity categories. Requires soft label training. Not appropriate for this task. |
| **CutMix** | Same fundamental label problem as MixUp. A patch of "no rust" concrete pasted into a "severe rust" image with a proportional label is physically meaningless. |
| **GAN / Diffusion synthesis** | Requires training a generative model on <800 images — unstable and prone to mode collapse. Adds weeks of effort with uncertain gain. Not among the professor's techniques. Suitable only as a future work mention. |
| **Elastic deformation** | Physically implausible for a flat concrete slab photographed perpendicular to its surface. Domain: medical imaging (histology, MRI). Not applicable here. |
| **Heavy hue shift (>±0.1)** | Rust-coloured specimens appear yellow, magenta, or green — physically impossible for corroded ferrocement. |

---

## Dataset Expansion Strategy

### The Professor's Observation

The professor correctly identifies that by combining transforms, augmented images are potentially unlimited. The question is what is scientifically reasonable and practically justified.

### Literature Evidence

| Study | Domain | Original training size | Expansion | Method |
|---|---|---|---|---|
| PMC11829104 | Corrosion (EfficientNetB0) | ~800 | **6.25×** | Offline |
| PMC11175235 | Steel corrosion (CNN) | 100 | **20×** | Offline |
| arXiv 1906.11887 | General image classification survey | Various | **2–3× recommended** | Both |
| Steel defect studies | Industrial inspection | 800–2,400 | **3×** | Offline |
| DeiT (Touvron 2021) | ImageNet classification | 1.2M | Online + repeated | Online |

**The survey result (arXiv 1906.11887) is the most directly applicable:** it found that 2–3× is the optimal augmentation rate for image classification — higher rates show diminishing accuracy returns while cost increases linearly. However, corrosion-specific studies use 3–6× with clear benefit.

### Recommendation: Online Augmentation as Primary Strategy

**Decision: online augmentation.** *Evidence quality: Established practice for pretrained model fine-tuning.*

Online augmentation applies a new random combination of transforms to each training image at every epoch. With 120 training epochs:
- Training images: approximately 630 (80% of 791, specimen-grouped)
- Distinct augmented views per image across training: ~120
- Effective diversity: comparable to a 5–10× offline expansion, but with maximum randomness (no repeated combination occurs twice unless by chance)

**Why online over offline for this study:**

1. The training set of ~630 images is well within the regime where online augmentation provides meaningful diversity per epoch.
2. No disk storage required for augmented files.
3. Augmentation parameters can be adjusted without regenerating a dataset.
4. Both ResNet50 and ViT fine-tuning are compatible with online augmentation — the backbone is called per-batch during training.
5. Reproducibility is achieved through fixed random seeds in the training script.

**If the professor or journal requires offline augmentation** (for example, for explicit reporting of training set size):

Generate a fixed 5× offline expansion for the training fold only. Do not augment the validation or test folds. This gives approximately 3,150 training images from the original 630, consistent with the middle of the literature-supported range (2–6×).

| Factor | Training images (approx.) | Justification |
|---|---|---|
| 2× | 1,260 | Minimum meaningful expansion; below literature midpoint |
| **3× (minimum recommended)** | **1,890** | Lower bound of corrosion literature practice |
| **5× (recommended for offline)** | **3,150** | Centre of corrosion literature practice; consistent with PMC11829104 range |
| 10× | 6,300 | Above literature midpoint for this size; diminishing returns expected |
| Online | Equivalent to ~5–10× | Preferred; maximum diversity at zero storage cost |

---

## Experimental Protocol

### Conditions

| ID | Model | Augmentation | Purpose |
|---|---|---|---|
| C1 | RGB / red-color classifier (Nissrine + Gerardo) | None | Comparison baseline |
| C2 | ResNet50 | None (inference transforms only) | CNN control |
| C3 | ResNet50 | Recommended pipeline | CNN + augmentation |
| C4 | Vision Transformer (DeiT-Small) | None | ViT control |
| C5 | Vision Transformer (DeiT-Small) | Recommended pipeline | ViT + augmentation |

**Architecture note on ViT variant:** DeiT-Small (22M parameters, ImageNet pretrained) is recommended over ViT-B/16 (86M parameters) because DeiT was designed for data-efficient training with augmentation. For a dataset of ~630 training images, DeiT-Small provides a better compute-to-performance trade-off. Subject to confirmation with the professor.

### Validation Protocol

**Specimen-level grouped splits are mandatory.** All 791 images come from 48 specimens imaged over time (0W–36W). A naive random split would allow training on week-4 images of Specimen X and testing on week-20 images of the same specimen — this inflates accuracy by leaking temporal identity information.

Recommended: **5-fold GroupShuffleSplit** keyed on `specimen_id`, test_size = 0.2 (~10 specimens held out per fold), inner validation from training fold (~20% of remaining specimens). Report mean ± standard deviation across 5 folds as the primary performance estimate.

All five conditions (C1–C5) must be evaluated on **identical test sets**. The comparison is invalid if conditions use different splits.

### Evaluation Metrics

| Metric | Primary? | Rationale |
|---|---|---|
| **Balanced accuracy** | ✓ | Corrects for class imbalance — early specimens (weeks 0–6) will produce many "no rust" or "mild" cases |
| **Macro F1-score** | ✓ | Treats all four severity classes equally; does not reward correct majority-class prediction |
| Overall accuracy | Secondary | Report for completeness; misleading if class distribution is uneven |
| Weighted F1-score | Secondary | Useful for absolute performance comparison |
| Per-class precision / recall | Diagnostic | Shows which severity class is hardest to classify |
| **Cohen's Kappa** | ✓ | Measures inter-rater agreement; particularly appropriate for ordinal severity categories |
| Confusion matrix | Required | Full four-class confusion matrix for every condition |

*Report balanced accuracy and macro F1 as primary metrics in the abstract and summary table.*

### Ablation Studies

#### Ablation 1 — Individual Transform Contribution

Remove one transform at a time from the recommended pipeline. Measures the contribution of each transform independently.

| Pipeline variant | What is removed |
|---|---|
| Full pipeline (reference) | Nothing |
| No brightness | Brightness variation |
| No contrast | Contrast variation |
| No saturation | Saturation variation |
| No blur | Gaussian blur |
| No noise | Gaussian noise |
| No flip | Horizontal flip |
| No crop | Random crop (centre crop only) |

#### Ablation 2 — Augmentation Intensity

Three intensity levels for the five core recommended transforms:

| Level | Brightness | Contrast | Saturation | Noise σ | Blur σ |
|---|---|---|---|---|---|
| Light | ±10% | ±10% | ±10% | 0.01 | 0.3 |
| **Standard (recommended)** | **±25%** | **±20%** | **±20%** | **0.03** | **0.8** |
| Strong | ±35% | ±30% | ±30% | 0.05 | 1.5 |

This directly answers the professor's question about how many augmented images to generate — by demonstrating that parameter intensity matters more than volume at this dataset size.

#### Ablation 3 — Fine-Tuning Depth

| Variant | Layers trained |
|---|---|
| Head only | Classification head only (backbone fully frozen) |
| Last block | Head + last residual block (ResNet50: layer4; ViT: last 2 transformer blocks) |
| Full fine-tuning | All layers |

This ablation is especially important for the ViT, which may need deeper fine-tuning to adapt its attention patterns from ImageNet features to corrosion texture features.

### Robustness Experiment

**Purpose:** Demonstrate that augmented DL models maintain accuracy under imaging condition variation, while the red-color baseline degrades severely.

**Protocol:**
- Apply systematic brightness perturbations to the test set: −30%, −20%, −10%, 0% (original), +10%, +20%, +30%.
- Evaluate all five conditions on each perturbed test set.
- Plot balanced accuracy as a function of perturbation level.

**Expected shape of results:** The C1 baseline accuracy will drop sharply under both brightening and darkening (threshold-detected rust fraction changes 3–7× with 20% brightness variation on actual images from this dataset). C3 (ResNet50 + aug) and C5 (ViT + aug) will show flatter curves. C2 and C4 (unaugmented DL) will show intermediate degradation.

This experiment is the strongest single argument for why augmentation matters for this specific dataset and is directly publishable as a standalone finding.

### Statistical Tests

| Test | Purpose | When applied |
|---|---|---|
| **McNemar's test** | Pairwise comparison of two classifiers on the same test set | All pairs: C1 vs C3, C1 vs C5, C2 vs C3, C4 vs C5 |
| **Wilcoxon signed-rank test** | Paired comparison across 5 CV folds | C2 vs C3, C4 vs C5 |
| **Bootstrap 95% CI** | Confidence interval for each accuracy estimate | All conditions; 1,000 bootstrap iterations |

Report p-values and effect sizes. For a journal paper, both statistical significance (p < 0.05) and practical significance (effect size in percentage points) must be discussed.

### Expected Outcomes

**Expected positive outcomes (high confidence):**

1. C3 > C2: ResNet50 with augmentation outperforms ResNet50 without augmentation. Effect size: 3–8% balanced accuracy, based on corrosion literature.
2. C5 > C4: ViT with augmentation outperforms ViT without augmentation. Effect size: 5–15%, larger than for ResNet50, confirming the secondary hypothesis.
3. C3 > C1 and C5 > C1: Both augmented DL models outperform the red-color baseline, particularly on the boundary severity classes (mild vs. moderate), where the threshold classifier is most ambiguous.
4. Robustness: C3 and C5 maintain accuracy better than C1 under brightness perturbation.
5. Ablation: brightness and contrast contribute most; this is consistent with the core argument that these transforms simulate the exact condition under which the baseline fails.

**Expected negative outcomes (handle honestly, do not suppress):**

1. C4 < C2: ViT without augmentation underperforms ResNet50 without augmentation on this small dataset. *This is the expected result and is the scientific motivation for augmentation — report it prominently.*
2. Augmented conditions may not reach statistical significance at α=0.05 on individual folds given the 48-specimen constraint. Report with confidence intervals and acknowledge the power limitation explicitly.
3. The C1 baseline may outperform unaugmented DL (C2, C4) on certain severity classes, especially if class labels were derived from the red-color threshold. Report honestly — this strengthens the argument for augmentation, not against it.
4. LOCO cross-validation (leave-one-specimen-out) will show lower absolute accuracy for all DL models due to specimen-level variation. This is expected and should be reported alongside 5-fold grouped CV.

---

## Journal Paper Structure

### Suggested Title

*"Photometric data augmentation for deep learning-based corrosion severity classification: a comparative study of ResNet50 and Vision Transformer on a limited ferrocement dataset"*

### Sections

| Section | Key content |
|---|---|
| Abstract | Scientific question, dataset, four-class task, five conditions, primary metric results, key finding |
| 1. Introduction | Corrosion monitoring; limitations of rule-based colour classification; DL promise; data scarcity challenge; augmentation as solution; paper contributions (3 bullet points) |
| 2. Related Work | (a) Corrosion and defect detection with DL; (b) CNN vs. ViT for industrial inspection on small datasets; (c) Augmentation strategies for limited training data |
| 3. Dataset and Classification Task | 48 specimens, 791 images, four-class severity definition; class distribution; specimen-level split rationale |
| 4. Augmentation Pipeline | Table of all transforms with parameters, rationale, and classification; excluded transforms with reasons |
| 5. Deep Learning Models | ResNet50 architecture and fine-tuning; DeiT-Small architecture and fine-tuning; training hyperparameters |
| 6. Experimental Design | Five conditions; specimen-grouped validation; metrics; ablation design; robustness experiment |
| 7. Results | Main comparison table; confusion matrices (selected); ablation results; robustness analysis |
| 8. Discussion | Primary and secondary hypothesis results; which augmentations contribute most; ResNet50 vs. ViT comparison; limitations; practical implications |
| 9. Conclusions | Summary; augmentation recommendations for small corrosion datasets; future work |
| References | — |

### Figures

| Figure | Content |
|---|---|
| Fig. 1 | Dataset overview: four specimen images at different severity levels; severity class distribution bar chart |
| Fig. 2 | Augmentation examples: one original specimen image shown with all five recommended transforms applied (one panel each) |
| Fig. 3 | Main results: grouped bar chart — balanced accuracy and macro F1 across all five conditions; error bars = 95% CI |
| Fig. 4 | Confusion matrices: 2×3 grid — C1, C3, C5 (baseline, ResNet50+aug, ViT+aug) as columns; four-class matrices as rows |
| Fig. 5 | Robustness analysis: line plot — balanced accuracy vs. brightness perturbation (−30% to +30%) for all five conditions; shows C1 collapse and C3/C5 stability |
| Fig. 6 | Ablation heatmap: balanced accuracy change when each transform is removed; rows = transforms, columns = ResNet50 / ViT |
| Fig. 7 | Learning curves: training and validation loss over epochs for C2 vs. C3 (ResNet50) and C4 vs. C5 (ViT); shows effect of augmentation on overfitting reduction |

### Tables

| Table | Content |
|---|---|
| Table 1 | Dataset statistics: specimens per class, images per class, weeks in time series |
| Table 2 | Augmentation pipeline: transform, parameter range, probability, classification (recommended / potentially useful / risky), literature support |
| Table 3 | **Main results table:** all five conditions × all metrics (balanced accuracy, macro F1, Cohen's Kappa, overall accuracy); mean ± std over 5 folds |
| Table 4 | Ablation 1 — individual transform contribution: balanced accuracy for each transform-removed variant |
| Table 5 | Ablation 2 — intensity levels: light / standard / strong results for C3 and C5 |
| Table 6 | Robustness: balanced accuracy under each perturbation level for all conditions |
| Table 7 | Statistical test summary: McNemar p-values and Wilcoxon p-values for key pairwise comparisons |

### Appendices

| Appendix | Content |
|---|---|
| A | Full augmentation implementation specification: library versions, exact parameter values, random seeds |
| B | Per-class precision, recall, F1 for all five conditions |
| C | Full 4×4 confusion matrices for conditions not shown in main figures |
| D | Ablation 3 — fine-tuning depth results |

---

## Timeline — Four Weeks

### Week 1 — Setup and Baseline

| Task | Output |
|---|---|
| Confirm class label definitions and class boundaries with Nissrine/Gerardo | Confirmed class schema |
| Confirm specimen-level split manifest (which specimens in train/val/test) | Fixed split file |
| Implement RGB threshold baseline (C1) and reproduce Nissrine/Gerardo's results | C1 metrics; confirm reproducibility |
| Implement augmentation pipeline (all recommended transforms with configurable parameters) | Augmentation module |
| Generate Figure 2 (augmentation examples) to visually verify pipeline | Augmentation figure |

**End-of-week gate:** C1 baseline metrics confirmed; augmentation pipeline visually verified.

### Week 2 — ResNet50 Experiments

| Task | Output |
|---|---|
| Implement ResNet50 fine-tuning pipeline (head only, then full) | ResNet50 training script |
| Train and evaluate C2 (ResNet50, no augmentation) | C2 metrics |
| Train and evaluate C3 (ResNet50 + augmentation) | C3 metrics |
| Run Ablation 1 (individual transform removal) for ResNet50 | Ablation 1 results, ResNet50 |
| Run Ablation 2 (intensity levels) for ResNet50 | Ablation 2 results, ResNet50 |

**End-of-week gate:** C2 and C3 metrics recorded; primary ResNet50 ablation complete.

### Week 3 — Vision Transformer Experiments and Robustness

| Task | Output |
|---|---|
| Implement DeiT-Small fine-tuning pipeline | ViT training script |
| Train and evaluate C4 (ViT, no augmentation) | C4 metrics |
| Train and evaluate C5 (ViT + augmentation) | C5 metrics |
| Run Ablation 1 and 2 for ViT | Ablation results, ViT |
| Run robustness experiment (brightness-perturbed test set for all conditions) | Robustness table |
| Run statistical tests (McNemar, Wilcoxon, bootstrap CI) | Statistical test results |

**End-of-week gate:** All five conditions evaluated; full results table assembled; statistical tests complete.

### Week 4 — Figures, Tables, and Writing

| Task | Output |
|---|---|
| Generate all publication-quality figures (300 dpi, consistent style and font) | Figs 1–7 |
| Finalize all tables | Tables 1–7 |
| Write Methods sections (Sections 3, 4, 5, 6) | Draft sections |
| Write Results and Discussion (Sections 7, 8) | Draft sections |
| Write Introduction, Related Work, Conclusions (Sections 1, 2, 9) | Draft sections |
| Write abstract | Abstract |
| Internal review with Nissrine, Gerardo, and professor | Feedback |

**End-of-week gate:** Complete first-draft manuscript ready for supervisor review.

---

## What Would Make My Professor Say: "Yes, This Is Exactly What I Asked For"

Four things, in order of importance:

**1. A table showing augmented DL beats the red-color baseline.**
The professor's core request is to "show the advantage of using deep learning methods compared to the automatic classification approach based only on the quantification of the red color." The primary deliverable is Table 3 — a clean comparison showing C3 and/or C5 outperforming C1 on balanced accuracy and macro F1, with confidence intervals.

**2. A visual demonstration of why augmentation helps.**
The robustness experiment (Figure 5) provides the clearest intuitive argument: the red-color baseline degrades under brightness variation, while augmented DL models do not. This is one figure that communicates the core scientific point without requiring the reader to parse a statistics table.

**3. An answer to "how much augmentation is enough."**
The professor explicitly asked for this. The Ablation 2 intensity experiment answers it directly: light, standard, and strong augmentation levels are compared, and the standard level is recommended based on results and literature.

**4. The ViT vs. ResNet50 finding.**
Whether the result is that ResNet50 is better, ViT is better, or augmentation helps both equally, the comparison is a novel and concrete finding for this specific domain and dataset size. The professor named both architectures — both must appear in the results, and the comparison between them is itself a contribution.

---

## Actionable Checklist

### Before Any Code Is Written
- [ ] Confirm four-class label definitions (category names and boundaries) with Nissrine/Gerardo
- [ ] Confirm whether existing baseline (C1) results are reproducible and on which split
- [ ] Confirm specimen-level split (which of the 48 specimens are train/val/test)
- [ ] Confirm DeiT-Small as the ViT variant (or obtain professor preference)
- [ ] Confirm access to Gerardo's ResNet50/ViT codebase, if it exists

### Week 1 Gates
- [ ] C1 baseline metrics match Nissrine/Gerardo's documented results
- [ ] Augmentation pipeline generates visually plausible examples for all five transforms
- [ ] No augmentation is applied to validation or test folds (verified by inspection)

### Week 2 Gates
- [ ] C2 (ResNet50 no-aug) metrics recorded under 5-fold grouped CV
- [ ] C3 (ResNet50 + aug) metrics recorded; C3 > C2 confirmed or not
- [ ] Ablation 1 complete for ResNet50

### Week 3 Gates
- [ ] C4 (ViT no-aug) metrics recorded; C4 vs. C2 comparison documented
- [ ] C5 (ViT + aug) metrics recorded; C5 > C4 confirmed or not
- [ ] Robustness experiment complete (brightness perturbation on full test set)
- [ ] All statistical tests computed

### Week 4 Gates
- [ ] All 7 figures at 300 dpi with consistent style
- [ ] All 7 tables with correct decimal places and units
- [ ] Complete manuscript draft submitted to supervisor

---

*Literature sources used in this plan:*
- [Deep neural networks for external corrosion classification — PMC11829104](https://pmc.ncbi.nlm.nih.gov/articles/PMC11829104/)
- [Autonomous corrosion detection in steel structures — PMC11175235](https://pmc.ncbi.nlm.nih.gov/articles/PMC11175235/)
- [A Deep Learning Approach to Industrial Corrosion Detection — CMC/58635](https://www.techscience.com/cmc/v81n2/58635/html)
- [Hybrid-DC: ResNet-50 and Vision Transformer for Steel Surface Defect Classification — MDPI Electronics 2024](https://www.mdpi.com/2079-9292/13/22/4467)
- [Vision Transformer in Industrial Visual Inspection — MDPI Applied Sciences 2022](https://mdpi.com/2076-3417/12/23/11981/htm)
- [Understanding Why ViT Trains Badly on Small Datasets — arXiv 2302.03751](https://arxiv.org/pdf/2302.03751)
- [Data-efficient Image Transformers (DeiT) — Meta AI Blog](https://ai.meta.com/blog/data-efficient-image-transformers-a-promising-new-technique-for-image-classification/)
- [A Preliminary Study on Data Augmentation for Image Classification — arXiv 1906.11887](https://arxiv.org/pdf/1906.11887)
- [Deep learning in corrosion assessment and control — De Gruyter 2024](https://www.degruyterbrill.com/document/doi/10.1515/corrrev-2024-0060/html)
- [Portable deep learning system for corrosion segmentation and grading — ScienceDirect 2026](https://www.sciencedirect.com/science/article/abs/pii/S1568494626007052)
- [Explainable DL for binary corrosion classification using Grad-CAM — PMC 2025](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12656319/)

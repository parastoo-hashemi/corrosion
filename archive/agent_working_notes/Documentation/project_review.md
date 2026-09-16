# Independent Project Review and Completion Strategy
## Ferrocement Corrosion ML Research — `main_4`

> **Prepared after full audit of:** codebase, configs, generated outputs (791-row master table, 329 CSVs, 430 figures), diagnostic markdown reports, IEEE papers, and thesis documentation.
> **Date of review:** 2026-06-27

---

## Executive Summary

This project is a well-engineered feasibility study on predicting structural hidden damage in ferrocement specimens from repeated surface images. The pipeline is complete end-to-end and the data audit is rigorous. However, the scientific output is substantially weaker than the engineering effort suggests.

**The strongest result** — image-based visible corrosion tracking — is partly tautological: the primary surface metric (`surface_total_rust_pct`) is numerically equivalent to an extracted image feature by construction (MAE = 0.0002 between label and feature). **The most important result** is a negative one: image features add no measurable value over specimen metadata alone for structural target estimation, and the hidden-damage models collapse by 3.24× in MAE when held out by campaign. The proxy-RUL layer produces zero future residual-life predictions at any configured threshold.

The project is **not publication-ready as a predictive system**. It is, however, well-positioned as an **honest methodological case study on the limits of surface-image-based structural assessment under sparse supervision and campaign confounding** — a contribution with real scientific value if framed correctly.

---

## 1. Current State of the Repository

### 1.1 Pipeline Completeness

All eight pipeline stages have been executed and their outputs are present:

| Stage | Entry Script | Key Output | Status |
|---|---|---|---|
| Data audit | `run_audit_validation.py` | `outputs/audit/verified_facts.json` | Complete |
| EDA | `run_eda.py` | `outputs/eda/` | Complete |
| Image feature extraction | `run_extract_image_features.py` | `outputs/features/image_features.csv` (791 rows, 77 features) | Complete |
| Surface modeling | `train_surface_models.py` | `outputs/models/surface/best_models.csv` | Complete |
| Hidden-damage modeling | `train_hidden_damage_models.py` | `outputs/models/hidden_damage/best_models.csv` | Complete |
| Degradation modeling | `train_degradation_models.py` | `outputs/models/degradation/degradation_best_fits.csv` | Complete |
| Proxy-RUL | `train_rul_proxy_models.py` | `outputs/models/proxy_rul/proxy_rul_summary.csv` | Complete |
| Diagnostics | `run_diagnostics_visualizations.py` | 430 PNG figures, 14 subdirectories | Complete |

### 1.2 Artifact Inventory

- **329 CSV files** across all output stages
- **430 PNG figures** (feature importance, residuals, degradation curves, diagnostics)
- **2 IEEE conference papers** drafted and present in `emiling/`
- **1 thesis** from the original experimenter (209 pages)
- **10+ markdown diagnostic reports** (`BENCHMARK_DIAGNOSTICS.md`, `FEATURE_DIAGNOSTICS.md`, `OUTPUT_REVIEW.md`, etc.)

### 1.3 What the Pipeline Does Not Include

No uncertainty quantification (point estimates only), no mechanistic or physics-informed degradation model, no multi-task learning across structural targets, no Bayesian treatment, no ablation of proxy-RUL threshold choices against failure evidence, no mixed-effects model for specimen-level random variation, no cross-specimen temporal modeling.

---

## 2. Scientific Assessment

### 2.1 What Is Well-Supported by Evidence

**Finding 1: Image-based surface rust quantification is reproducible and consistent.**

The extracted feature `img_rust_area_ratio_pct` achieves MAE = 0.0002 against the workbook label `surface_total_rust_pct`. This is not a predictive achievement — it is verification that the feature extraction pipeline faithfully reproduces the original MATLAB-derived workbook values. The label is essentially the feature, computed from the same images using equivalent thresholds.

The non-trivial surface result is `peak_rust_pct` prediction (MAE = 1.097, Spearman = 0.992 under grouped holdout; MAE = 1.058, Spearman = 0.977 under leave-one-campaign-out). This is a genuine result: peak rust location and intensity is recoverable from images and generalises across campaigns.

**Finding 2: Campaign confounding is the dominant structure in the data, not corrosion.**

The Spearman correlation between `n_steel_mesh` and `ultimate_load_kn` is 0.827. The Spearman between `ageing_days` and `ultimate_load_kn` is −0.827. Both reflect campaign identity (7-mesh/3.5%NaCl vs 4-mesh/5%NaCl). The two campaigns differ simultaneously in mesh count, salt concentration, specimen age at termination, and calendar year. There is no way to isolate any single factor from the observed structural outcome. This is an experimental design limitation, not a modeling problem.

**Finding 3: Image features do not add value over metadata for structural targets.**

The best hidden-damage models selected `metadata_only` (8 features: mesh count, NaCl concentration, ageing days, week, etc.) over all image-inclusive feature sets in the robustness-weighted selection. This was found after systematic comparison across four feature-set families (`all_cleaned`, `image_time_only`, `image_only`, `metadata_only`). The image features added noise, not signal, for structural prediction under leakage-safe evaluation.

This is a **substantive negative finding** with scientific value.

### 2.2 What Is Weakly Supported

**Hidden-damage ranking.**

`wire_area_loss_frac`: grouped Spearman = 0.280; leave-one-campaign-out Spearman = −0.089 (negative ranking ability). The best single predictor (`img_rust_blob_eccentricity_mean`) has univariate Spearman = 0.382. Models trained on 38 specimens and evaluated on 10 do not demonstrably outperform simple rank-based baselines.

`ultimate_load_kn`: grouped Spearman = 0.778, leave-one-campaign-out Spearman = 0.353. The within-campaign apparent performance (grouped holdout, MAE = 0.174 kN) is entirely consistent with the model learning campaign identity (n_steel_mesh alone explains 68% of variance in ultimate_load). Under true cross-campaign holdout, MAE rises to 0.564 kN — 3.24× the within-campaign value — and R² = −6.826, meaning the model performs worse than the campaign-mean baseline.

**Degradation modelling.**

The monotone isotonic family dominates (21/48 specimens), achieving near-zero RMSE through interpolation. This is arithmetically correct but scientifically uninformative: isotonic regression is not a degradation model, it is a piecewise monotone interpolant with no extrapolation capability. The selected "degradation model" cannot predict future states.

### 2.3 What Is Unsupported

**Proxy-RUL as a residual-life estimate.**

At all three configured thresholds (0.2, 0.3, 0.4 wire-area-loss-frac), the number of future residual-life predictions within a 365-day projection horizon is **zero**. All `proxy_rul_days` values are NULL. The proxy-RUL layer is a threshold-crossing-status summary, not a remaining-useful-life estimate. The thresholds themselves are arbitrary configurations with no calibration to observed failure events from the bending tests.

| Threshold | Specimens crossed by final observation | Future crossings (365-day horizon) | Right-censored |
|---|---|---|---|
| 0.20 | 33 / 48 (68.8%) | **0** | 15 (31.3%) |
| 0.30 | 9 / 48 (18.8%) | **0** | 39 (81.3%) |
| 0.40 | 5 / 48 (10.4%) | **0** | 43 (89.6%) |

**Any claim that this system estimates remaining service life is unsupported.**

---

## 3. Bottlenecks

### 3.1 Structural Label Sparsity (Fundamental — Cannot Be Fixed)

- 48 structural-labeled rows out of 791 (6.1%)
- One measurement per specimen, at experiment termination only
- No intermediate structural observations; no failure-time data
- This limits structural models to 38 training samples at best under any grouped split

This is a **physical constraint** of the experiment, not a modeling problem. Additional processing, augmentation, or model sophistication cannot manufacture new structural labels. Any proposed improvement that does not acknowledge this as a hard ceiling is scientifically misleading.

### 3.2 Campaign Confounding (Fundamental — Cannot Be Fixed With This Data)

The two campaigns differ across at least four dimensions simultaneously (mesh, NaCl, duration, year). There is no within-campaign variation in mesh count or NaCl concentration. Cross-campaign prediction requires extrapolating from one design point (7 mesh, 3.5% NaCl) to another (4 mesh, 5% NaCl) with no intermediate specimens.

No machine learning method can reliably extrapolate in this setting. Leave-one-campaign-out is not a generalization test — it is an extrapolation test. The 3.24× MAE collapse is expected and unresolvable with the current dataset.

### 3.3 Surface Label Validity (Methodological)

`surface_total_rust_pct` in the workbook is numerically computed from images using the same RGB threshold used by the current pipeline. The "prediction" of this label from image features is circular: the model is predicting the output of a deterministic function from its inputs. This result must not be presented as evidence that corrosion can be estimated from images.

`peak_rust_pct` does not have this problem — its spatial strip-based measurement introduces some non-trivial information — but it is still heavily driven by image strip features (Spearman ≈ 0.99 with `img_strip_rust_max_pct`).

### 3.4 Image Preprocessing Non-Reproducibility (Technical)

The original thesis images were processed with GIMP white-balance correction and custom MATLAB thresholds. The exact GIMP parameters are not fully recovered. The pipeline is forced to use the provided PNGs, which may already contain preprocessing bias. Features derived from these images carry an unquantified measurement-protocol dependency.

### 3.5 Monotone Degradation Without Physical Grounding (Scientific)

The degradation stage enforces monotone increase (via isotonic regression) as a post-hoc correction on non-monotone hidden-damage predictions. This monotone smoothing:
- Cannot extrapolate beyond the last observation
- Produces near-zero RMSE through interpolation, not because the model is learning
- Has no mechanistic basis for selecting among linear, logistic, Gompertz, or isotonic families

The degradation stage is descriptive, not prognostic.

---

## 4. Critical Review (Reviewer Perspective)

### 4.1 Novelty

**Moderate.** The end-to-end pipeline from repeated images to proxy-RUL is not unprecedented; similar workflows exist in corrosion monitoring literature. The specific contribution — explicit demonstration of campaign confounding and metadata-only selection for structural targets — is honest and has methodological novelty. The negative finding (image features do not help) is undervalued in the current framing.

### 4.2 Scientific Contribution

**Mixed.** The project's strongest contribution is methodological transparency: the multi-stage pipeline with leakage-safe grouped splits, treatment reconstruction from mapping files, and an honest assessment of what each stage can and cannot do. The scientific contribution would be stronger if the negative finding (image features ≠ structural signal) were positioned as the central result rather than a secondary caveat.

The proxy-RUL contribution is currently **not a contribution** — it is an empty result. Removing it from the paper scope and being explicit about why would be stronger than including it with heavy caveats.

### 4.3 Robustness

**Weak for structural targets; moderate for surface targets.** Leave-one-campaign-out is the only scientifically meaningful generalization test for this dataset (since campaign is the main source of variation). Surface models hold under this test (Spearman ≥ 0.977). Structural models do not (Spearman 0.353 for load, negative for wire loss).

The robustness scoring system (which weights LOCO at 0.45) is well-designed and honest. However, reporting grouped-holdout metrics alongside LOCO without clear visual separation risks misleading readers who may anchor on the more impressive numbers.

### 4.4 Reproducibility

**High.** The pipeline is fully scripted, YAML-configured, seed-controlled, and documented. Splits are pre-computed and saved. All artifacts are versioned via the output directory structure. This is a genuine strength.

### 4.5 Validity of Claims

The project's internal documentation (`OUTPUT_REVIEW.md`, `BENCHMARK_DIAGNOSTICS.md`) is admirably honest about limitations. However, the IEEE papers (particularly if they present grouped-holdout numbers as primary results) risk overstating generalization. A reviewer will immediately check whether cross-campaign performance is reported and will flag the 3.24× MAE collapse as the decisive result.

### 4.6 Publication Readiness

**Not ready for a predictive-system paper. Ready for a methods/case-study paper with reframing.**

The pipeline and negative findings constitute a publishable contribution if positioned as: *"We demonstrate that, under experimentally realistic evaluation with campaign holdout, interpretable image features from repeated surface photographs do not add structural prognostic value beyond specimen design metadata in a ferrocement corrosion study."*

---

## 5. Improvement Options

The following options are ranked by scientific value, implementation effort, probability of success, and risk of misleading conclusions.

### 5.1 Explicitly Model and Report Campaign Confounding (HIGH VALUE, LOW EFFORT)

**What:** Add a Simpson's paradox analysis — compute corrosion-vs-load correlations within each campaign separately, then compare to the pooled correlation. Show that the pooled positive relationship inverts or disappears within homogeneous groups.

**Why:** This is already implied by the data but not explicitly demonstrated. It is the clearest explanation for why image features cannot rescue structural prediction. A single table (within-campaign vs. pooled Spearman for key features vs. ultimate_load_kn) would make this argument concrete.

**Effort:** 1 day. **Scientific value:** High. **Publication impact:** Strong — this is the key diagnostic that the paper currently underreports.

### 5.2 Bootstrap Confidence Intervals on All Key Metrics (HIGH VALUE, LOW-MEDIUM EFFORT)

**What:** For each fold's MAE and Spearman, compute bootstrap confidence intervals (1000 resamples at the observation level within each fold). Report means ± 95% CI instead of point estimates only.

**Why:** With 10 test specimens per fold in grouped holdout and 24 per fold in LOCO, point estimates have wide sampling variance. Presenting only point estimates without confidence intervals makes the results appear more precise than they are. A reviewer will ask for this.

**Effort:** 2–3 days. **Scientific value:** High. **Risk:** Low (CIs will likely widen, making weak results look weaker — this is honest, not harmful).

### 5.3 Mixed-Effects Baseline for Structural Targets (HIGH VALUE, MEDIUM EFFORT)

**What:** Fit a linear mixed-effects model for `ultimate_load_kn` with `n_steel_mesh` and `nacl_pct` as fixed effects (specimen-design covariates) and a specimen-level random intercept. Compare its leave-one-campaign-out MAE to the current best ML model.

**Why:** If a simple linear mixed-effects model with two design covariates achieves comparable or better campaign-holdout performance than RandomForest with 8 features, the conclusion is clear: this is fundamentally a linear covariate problem, not a complex ML problem. This comparison either validates or deflates the ML pipeline's structural contribution.

**Effort:** 2–3 days (statsmodels or R lme4). **Scientific value:** Very high. **Risk:** Low — it may show the ML models are not needed for structural targets, which is the honest result.

### 5.4 Explicit Uncertainty Quantification via Conformal Prediction (MEDIUM VALUE, MEDIUM EFFORT)

**What:** Apply split conformal prediction on the surface models to produce marginal coverage guarantees. For the hidden-damage stage, use jackknife+ with the grouped split structure to produce specimen-level prediction intervals.

**Why:** Point estimates without uncertainty are inadequate for a structural health monitoring paper. Conformal prediction is assumption-free and integrates cleanly with the existing grouped split framework.

**Effort:** 3–5 days. **Scientific value:** Medium. **Publication impact:** Moderate — adds methodological depth without overstating results. Risk: Low.

### 5.5 Threshold Sensitivity Analysis for Proxy-RUL (MEDIUM VALUE, LOW EFFORT)

**What:** Sweep wire-area-loss thresholds from 0.05 to 0.60 in steps of 0.05. For each threshold, report: fraction crossed by observation end, fraction with future crossings within 365 days, and sensitivity of the "already degraded" classification to ±10% threshold variation.

**Why:** The current three thresholds (0.20, 0.30, 0.40) are arbitrary. If no threshold produces future residual-life predictions, this should be stated explicitly with quantitative support. If some thresholds do, the paper should report which and why they might be domain-relevant.

**Effort:** 1 day. **Scientific value:** Medium. **Risk:** May show that the proxy-RUL layer is entirely vacuous, which is an honest and publishable result.

### 5.6 Physics-Informed Degradation Constraint (MEDIUM VALUE, HIGH EFFORT)

**What:** Replace isotonic regression post-smoothing with a parametric degradation model from the corrosion kinetics literature (e.g., power-law corrosion rate, Faraday-based electrochemical model). Constrain the hidden-damage trajectory to monotone increase with physically meaningful acceleration parameters.

**Why:** A mechanistic degradation model — even a simple one — provides extrapolation capability (unlike isotonic regression) and produces parameters with physical meaning (corrosion rate, induction period).

**Effort:** 1–2 weeks. **Scientific value:** High if a mechanistic model fits well; low if it fits as poorly as phenomenological models. **Risk:** Medium — the data may not have enough resolution (16–17 time points per specimen) to distinguish between mechanistic families.

### 5.7 Self-Supervised Representation Learning (LOW PROBABILITY, VERY HIGH EFFORT)

**What:** Train a contrastive or masked-image model (SimCLR, DINO) on the 791 images to produce specimen-level embeddings, then evaluate whether these embeddings correlate with structural targets.

**Why proposed:** Dense image information may contain structural signals not captured by hand-engineered features.

**Why it is likely to fail:** (1) 791 images across 48 specimens is too small for self-supervised visual representation learning to produce useful embeddings. (2) The structural label bottleneck (48 rows) means any learned representation has only 48 supervision signals to calibrate against. (3) The existing finding that image features do not outperform metadata in a well-regularized 8-feature model is strong evidence against richer image representations helping structural targets.

**Effort:** 1–2 weeks. **Probability of success:** Low. **Risk:** High (could produce misleading results if evaluated only on grouped holdout without campaign separation).

### 5.8 Data Augmentation for Image Features (LOW VALUE FOR STRUCTURAL, MODERATE FOR SURFACE)

**What:** Apply conservative image augmentation (Gaussian blur, ±10% grayscale brightness, ±4% horizontal crop) before feature extraction, using only training-fold images.

**Why limited value:** Augmenting 791 surface images does not create new structural labels. The 48 structural rows are terminal measurements — augmenting their corresponding images produces more rows with the same 48 distinct structural label values. Under grouped specimen splitting, no augmented row introduces information about new specimens. Augmentation therefore cannot reduce the core structural label bottleneck.

For the surface stage (where it is most applicable), surface models already generalise well (Spearman ≥ 0.977 under LOCO). Augmentation would be optimising a non-bottleneck.

**Conclusion:** Do not prioritise augmentation. If pursued, confine it to the surface stage only, and set the expectation that gains will be marginal.

---

## 6. Things Not to Do

| Action | Reason |
|---|---|
| Present grouped-holdout structural metrics as primary results | Campaign-holdout is the only scientifically valid test; grouped numbers mislead about generalization |
| Augment images expecting structural improvement | Does not create new structural labels; does not resolve the 48-sample ceiling |
| Train deep or self-supervised models without campaign-holdout evaluation | Small dataset + high model capacity = inflated within-campaign metrics with no generalization |
| Frame proxy-RUL as a residual-life prediction system | Zero future crossings at any threshold; thresholds are uncalibrated to failure events |
| Report `surface_total_rust_pct` model performance as a predictive achievement | It is label reconstruction from the source of truth image features |
| Use isotonic regression degradation as evidence of learned degradation dynamics | It is monotone interpolation, not a physical model; it cannot extrapolate |
| Chase metric improvements on the same data | The bottlenecks are structural label sparsity and campaign confounding — both are fixed by experimental design, not by algorithm choice |
| Add more ML models to the structural comparison | Five model families have already been compared; the problem is data, not algorithm |

---

## 7. Completion Roadmap (2–4 Weeks)

Priority objective: produce a rigorous, honest paper that reports what the data actually supports.

---

### Week 1 — Strengthen What Is Already True

**Task 1.1: Simpson's paradox analysis** (2 days)
- For each image feature family (rust area, texture, morphology, strip), compute Spearman correlation with `ultimate_load_kn` both pooled and within each campaign separately.
- Produce a 3-column table: Feature | Pooled Spearman | Campaign-1 Spearman | Campaign-2 Spearman.
- Expected finding: pooled correlations appear meaningful; within-campaign correlations near zero or inverted.
- *Effort: low. Gain: high. Scientific value: this is the central explanatory finding.*

**Task 1.2: Bootstrap CIs on all reported metrics** (2 days)
- Add bootstrap resampling (1000 resamples, observation level within fold) to the evaluation engine.
- Re-report all primary metrics with 95% CIs.
- *Effort: low-medium. Gain: high credibility. Risk: none.*

**Task 1.3: Reframe surface_total_rust_pct explicitly** (0.5 days)
- In the paper and in code comments, label surface_total_rust_pct modeling as "label reconstruction verification," not "surface prediction."
- Report it in a single sentence with the tautology caveat, not as a benchmark.
- *Effort: very low. Scientific value: prevents a reviewer objection that would otherwise sink the paper.*

---

### Week 2 — Address the Structural Target Properly

**Task 2.1: Mixed-effects linear baseline** (3 days)
- Fit `ultimate_load_kn ~ n_steel_mesh + nacl_pct + (1|specimen_id)` using `statsmodels` or `scipy`.
- Evaluate under leave-one-campaign-out (exclude the random intercepts for the holdout campaign).
- Compare LOCO MAE against the current RandomForest best (MAE = 0.564 kN).
- *Effort: medium. Gain: resolves whether ML is actually needed for structural targets. Scientific value: high.*

**Task 2.2: Threshold sensitivity sweep for proxy-RUL** (1 day)
- Sweep thresholds 0.05–0.60 in steps of 0.05.
- Report coverage (fraction crossed), future crossings, and sensitivity to ±0.05 threshold shift.
- If zero future crossings persist across the full sweep, state this explicitly in the paper.
- *Effort: low. Gain: provides honest quantitative support for the proxy-RUL limitation claim.*

**Task 2.3: Produce the final figure set** (2 days)
- Campaign confounding figure (pooled vs. within-campaign correlation scatter)
- Grouped vs. campaign holdout performance comparison bar chart for all four targets
- Feature ablation table (all_cleaned vs. image_time_only vs. metadata_only under LOCO)
- Proxy-RUL threshold sensitivity curve
- *Effort: medium. Publication value: high — these are the 4–5 figures that carry the paper.*

---

### Week 3 — Decide on Depth vs. Polish

**Task 3.1 (if mechanistic degradation is pursued):** Fit power-law or Boltzmann S-curve degradation models using `scipy.optimize.curve_fit` with physical constraints (monotone, non-negative rate, bounded asymptote). Compare AIC to isotonic and polynomial families per specimen. *Effort: 3–4 days.*

**Task 3.1 (if mechanistic degradation is not pursued):** Drop the degradation and proxy-RUL stages from the primary paper scope. Retain them as an appendix or supplementary section with explicit caveats. This simplifies the paper and focuses on the defensible results. *Effort: 1 day.*

**Recommendation:** Drop degradation/proxy-RUL from primary scope unless the mechanistic model is implemented. The empty proxy-RUL result (zero future crossings) weakens the paper if presented alongside incomplete methodological treatment.

**Task 3.2: Paper writing — core results section** (3 days)
- Methods: specimen design, imaging protocol, feature extraction, leakage-safe grouped splits.
- Results: surface tracking (genuine), hidden-damage modeling (negative finding, positive for methodology), campaign confounding analysis (new).
- Discussion: why image features cannot rescue structural prediction given experimental design; what additional data would be needed.

---

### Week 4 — Paper Completion and Review

**Task 4.1: Uncertainty section** (2 days)
- Add bootstrap CIs to all tables.
- If time allows, add conformal prediction intervals for the surface stage.

**Task 4.2: Literature positioning** (2 days)
- Locate 3–5 papers on image-based corrosion assessment with structural outcome prediction.
- Position this work as a rigorous negative result with important methodological lessons.

**Task 4.3: Final review and submission** (1 day)
- Confirm all results match pipeline outputs exactly.
- Confirm all LOCO results are reported alongside grouped holdout with clear labeling.
- Remove or footnote any proxy-RUL claims not supported by the data.

---

## 8. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Mixed-effects baseline outperforms ML models for `ultimate_load_kn` | High | Medium | Frame as a positive finding — simplicity wins; validates honest ML comparison |
| Reviewer rejects `surface_total_rust_pct` result as tautological | High | High | Preemptively reframe as label-reconstruction verification in the paper |
| Bootstrap CIs reveal that grouped-holdout Spearman for structural targets is not significantly above zero | Medium | High | This is the honest result; adjust paper claims accordingly |
| Mechanistic degradation models fail to converge or fit poorly | Medium | Low | Fall back to phenomenological families; keep degradation as secondary scope |
| Campaign confounding cannot be disentangled from surface texture trends | High | Low | The inability to disentangle is itself the finding |
| Augmentation experiment (if pursued) produces inflation on grouped holdout but not LOCO | Medium | High | Always evaluate augmented models under LOCO; do not report grouped-only augmentation results |

---

## 9. Publication Positioning

### Strongest Publishable Contribution

The project's most defensible and novel contribution is a **rigorous negative result with methodological transparency**:

> Image features extracted from repeated surface photographs of corroding ferrocement specimens do not add structural prognostic value beyond specimen design metadata, when evaluated under experimentally realistic campaign holdout. The primary limitation is structural label sparsity (48 terminal measurements) combined with inherent campaign confounding that prevents cross-design-space generalization with available data.

This is a publishable finding. Negative results with rigorous evaluation frameworks are published in structural health monitoring, non-destructive testing, and prognostics & health management venues.

A secondary contribution is the interpretable image feature pipeline itself (77 features, fully reproducible, threshold-explicit), which provides a baseline for future work with larger or better-controlled datasets.

### Suggested Paper Framing

**Primary frame:** Methodological study — *what can and cannot be learned from repeated surface images for ferrocement structural assessment, and why.*

**Avoid:** Framing as a predictive system, RUL estimator, or deployed health monitoring tool. None of these are supported by the results.

**Narrative arc:**
1. Surface corrosion is trackable from images (established, strong result — but reframe the tautology)
2. Structural damage is not recoverable from surface images alone with this dataset (central negative finding)
3. Campaign confounding is the mechanistic explanation (Simpson's paradox analysis)
4. The methodology demonstrates best-practice evaluation for small-dataset structural health monitoring studies

### Not Recommended Paper Framing

- "AI-based remaining useful life prediction for ferrocement" — proxy-RUL produces zero future predictions; not supported
- "Deep learning corrosion assessment" — no deep learning in the pipeline; main_2 deep learning phase was superseded
- "Image-based structural health monitoring system" — structural results do not generalize across campaigns

---

## 10. Final Recommendation

### Recommended direction

Reframe the project as a **methodological case study on the limits of surface imaging for structural prognosis**. Implement the Simpson's paradox analysis (Task 1.1) and mixed-effects baseline (Task 2.1) in Week 1–2. These two additions cost 4–5 total days of work and transform a paper that looks like it overpromises on a weak result into a paper that clearly demonstrates an important finding about experimental design requirements for image-based structural prognostics.

Add bootstrap confidence intervals to all metrics (Task 1.2). Drop proxy-RUL from the primary scope unless mechanistic degradation modeling is added. Polish the figure set (Task 2.3) to lead visually with the campaign confounding story.

### Not recommended direction

Do not invest significant effort in augmentation, deep learning, GAN-based synthesis, or self-supervised learning on this dataset. These approaches cannot resolve the binding constraint (48 structural labels, two-campaign experimental design). They risk producing inflated within-campaign metrics that a careful reviewer will correctly identify as campaign-confounded, and they would cost 2–4 weeks for a low probability of publishable gain.

Do not attempt to optimize models further to improve LOCO performance on structural targets. The performance ceiling under genuine cross-campaign holdout is set by the experimental design, not the algorithm.

### Main limitations (for explicit disclosure in any publication)

1. Structural labels: 48 terminal measurements, one per specimen, no intermediate or repeat structural observations
2. Campaign confounding: mesh count, NaCl concentration, ageing duration, and calendar year are simultaneously different between campaigns; cross-campaign prediction is extrapolation, not interpolation
3. Image preprocessing: exact GIMP white-balance parameters not fully recovered; features may carry hidden preprocessing dependence
4. Proxy-RUL: thresholds are uncalibrated to observed failure events; zero future residual-life predictions produced
5. No measurement uncertainty: single terminal structural measurements per specimen, no uncertainty about the measured wire loss or ultimate load values

### Suggested final title

> **"Surface Imaging Cannot Substitute for Structural Testing in Ferrocement Corrosion Prognosis: A Leakage-Safe Evaluation Under Campaign Holdout"**

Or, if the surface tracking contribution is foregrounded:

> **"Limits of Repeated-Image Surface Corrosion Tracking for Structural Prognosis: A Campaign-Confounding Case Study in Ferrocement Specimens"**

---

*This review is based on a full audit of the codebase (`main_4/`), all 329 CSV outputs, diagnostic markdown reports, IEEE conference papers, and the source thesis. All metrics cited are taken directly from generated output files or markdown diagnostic reports and cross-checked against source code.*

# Final Strategy Decision
## Ferrocement Corrosion Project — Given Fixed Dataset and Mature Codebase

> **Basis:** Full audit of codebase, 329 CSVs, 430 figures, IEEE papers, and diagnostic reports documented in `verification_audit.md` and `project_review.md`.
> **Constraint:** No new experiments. No new specimens. No new structural labels. Dataset is fixed.
> **Date:** 2026-06-27

---

## The Real Situation

The project has already computed everything a reviewer would ask for. The gap is not in the analysis — it is in the argument. Sophisticated outputs exist in nested subdirectories without being assembled into a coherent scientific narrative. The paper reads as a pipeline description when its most valuable content is a set of precise, honest negative findings backed by rigorous evaluation.

The bottleneck is now entirely about framing, assembly, and selective emphasis. The code is done. The story has not been told yet.

---

## Recommendations

---

### R1 — Name and formally present the Simpson's paradox finding

**Recommendation:** Extract the numbers from `outputs/ultimate_load_refocus/correlations/mesh_stratified_corrosion_vs_ultimate_load.csv` and present the within-mesh vs. pooled correlation reversal as a named, foregrounded finding with a dedicated figure and a one-paragraph mechanistic explanation.

**Why it is valuable:** This is the single result that explains everything else in the paper. Pooled Spearman = +0.46 between surface rust and ultimate load; within 4-mesh: −0.05; within 7-mesh: −0.40. The reversal is complete and unambiguous. Without naming this, readers see a confusing pattern of results (ML models that appear to work in grouped holdout, then collapse under LOCO) and cannot understand why. With naming it, the entire paper becomes legible: the pooled correlation is an artefact of campaign structure, image features inherit this artefact, and LOCO correctly destroys any model that learned it.

**Scientific problem it addresses:** Why do image features not improve over metadata for structural targets? The answer is that the apparent image-structure relationship in pooled data is entirely driven by the mesh-count separation between campaigns, not by corrosion physics.

**Expected implementation effort:** Zero code. The CSV exists. Two hours of writing and one figure (scatter plot with mesh-coloured points and pooled regression line vs. within-mesh regression lines). The figure could be assembled from existing `partial_dependence.csv` and `mesh_stratified_corrosion_vs_ultimate_load.csv` outputs.

**Probability of improving the paper:** Very high. This finding is currently buried in a CSV without interpretive framing.

**Publication impact:** High. Explicit demonstration of a confounding structure that invalidates pooled analysis is a methodological contribution independently of the ML results.

**Reviewer impact:** High. A reviewer who reaches the LOCO collapse numbers without this explanation will ask "why does the model fail so completely?" This figure answers the question before it is asked.

**Priority: HIGH**

---

### R2 — Reframe the paper's primary contribution as a negative finding

**Recommendation:** Restructure the paper abstract and introduction so that the central claim is: *"We demonstrate, under experimentally realistic campaign holdout, that interpretable image features from repeated surface photographs do not contribute structural prognostic value beyond specimen design metadata in ferrocement corrosion assessment."* Every subsequent section should be positioned as evidence for or context around this claim.

**Why it is valuable:** The current framing leads with the pipeline and ends with weak results. A reviewer reading in this order experiences disappointment. Reversing the order — leading with the finding, then showing the evidence — produces a coherent argument. Negative results with rigorous evaluation and a clear mechanistic explanation are publishable and citable. A pipeline paper with ambiguous results is neither.

**Scientific problem it addresses:** The paper currently lacks a falsifiable central claim. "We built a pipeline" is not a scientific claim. "Image features do not predict structural damage under campaign holdout, because campaign is confounded with mesh design" is a falsifiable claim with strong evidence.

**Expected implementation effort:** One to two days of writing. No code changes.

**Probability of improving the paper:** High. This change propagates to the abstract, introduction, results framing, and discussion — all without touching a single line of code.

**Publication impact:** High. Negative findings in structural health monitoring are underrepresented and explicitly sought by journals such as *Structural Health Monitoring*, *Engineering Structures*, and *NDT & E International*.

**Reviewer impact:** Very high. A clearly stated negative finding with rigorous evidence is far easier to accept than a positive claim with weak evidence.

**Priority: HIGH**

---

### R3 — Add bootstrap confidence intervals to all primary metric tables

**Recommendation:** For each primary reported metric (MAE and Spearman under grouped holdout and LOCO), compute percentile bootstrap CIs by resampling at the specimen level (not the observation level) within each fold, 1000 resamples. Report as `mean [95% CI: lower, upper]` in all tables.

**Why it is valuable:** With 10 test specimens per grouped-holdout fold and 24 per LOCO fold, point estimates have wide sampling variance. A reviewer who computes the standard error of a Spearman correlation based on n=10 will immediately note that the current confidence is low. Reporting CIs preemptively demonstrates statistical rigour and prevents the paper from being rejected for incomplete uncertainty reporting.

**Scientific problem it addresses:** Whether the observed metric differences (e.g., Spearman = 0.778 under grouped holdout vs. 0.353 under LOCO for `ultimate_load_kn`) are statistically distinguishable from each other and from a null (Spearman = 0) baseline.

**Expected implementation effort:** Two to three days. Add a `bootstrap_metric_ci()` function to `evaluation.py` using `scipy.stats.bootstrap` or a manual percentile loop. Rerun the evaluation stage. All existing downstream CSV consumers are unaffected.

**Probability of improving the paper:** Very high. CIs are expected in any quantitative ML paper. Their absence is a gap that reviewers will flag.

**Publication impact:** Medium — CIs do not change the findings, but they prevent a rejection on statistical grounds.

**Reviewer impact:** High. A table with `0.353 [0.12, 0.57]` is defensible. A table with `0.353` alone invites the question "is this distinguishable from zero?"

**Priority: HIGH**

---

### R4 — Add a mixed-effects linear baseline for `ultimate_load_kn`

**Recommendation:** Fit `ultimate_load_kn ~ n_steel_mesh + nacl_pct + (1|specimen_id)` using `statsmodels.formula.api.mixedlm` with campaign excluded from the test fold's random effects. Compare its LOCO MAE and Spearman against the current RandomForest best (MAE = 0.564 kN, Spearman = 0.353).

**Why it is valuable:** There are two possible outcomes, both valuable. If the mixed-effects model matches or outperforms RandomForest under LOCO, the paper's honest conclusion is that a two-covariate linear model is sufficient and that ML adds no structural value — this is a clean, strong, publishable negative result. If RandomForest outperforms the mixed-effects model under LOCO, then ML has demonstrated incremental value and the paper has a stronger positive claim than it currently makes.

Either outcome resolves the most important open question: is the ML pipeline doing anything that a simple design-covariate model cannot?

**Scientific problem it addresses:** Whether the structural modeling contribution of the ML pipeline exceeds what a simple linear model with known design covariates can achieve.

**Expected implementation effort:** Two to three days. `statsmodels` is likely already in the environment (it is a scipy-ecosystem package). No change to the existing pipeline structure required.

**Probability of improving the paper:** Very high regardless of outcome.

**Publication impact:** High. Including this comparison is now standard practice in applied ML papers in engineering domains. Its absence will be noted.

**Reviewer impact:** Very high. A reviewer who asks "did you compare against a simple linear baseline?" will receive a complete answer rather than a gap.

**Priority: HIGH**

---

### R5 — Calibrate proxy-RUL thresholds against observed terminal measurements

**Recommendation:** Compute the empirical distribution of `wire_area_loss_frac` values at termination across all 48 specimens (mean, median, 10th/25th/75th/90th percentiles). Set at least one threshold at a data-grounded level (e.g., the 25th percentile of observed terminal wire loss) in addition to the current arbitrary [0.2, 0.3, 0.4] values. Describe threshold rationale in the paper.

**Why it is valuable:** The current thresholds are arbitrary configuration values with no stated connection to the physical measurements taken at termination. A reviewer will ask: what is the engineering basis for 0.2 as a threshold? If the answer is "it is arbitrary," the proxy-RUL section has no scientific standing. If the answer is "it corresponds to the 25th percentile of observed terminal wire loss," it has domain grounding.

**Scientific problem it addresses:** Whether the proxy-RUL threshold choices have any connection to observed structural severity in this dataset.

**Expected implementation effort:** Half a day. Read `terminal_structural_table.csv`, compute percentiles of `wire_area_loss_frac`, select a justified threshold, add a sentence to the paper.

**Probability of improving the paper:** High. This is a low-effort change with high credibility impact.

**Publication impact:** Medium. Improves the proxy-RUL section from "arbitrary configuration" to "data-grounded exploration."

**Reviewer impact:** High. This specific question is very likely to appear in a review.

**Priority: HIGH**

---

### R6 — Remove or demote the proxy-RUL section

**Recommendation:** Either remove the proxy-RUL section from the primary paper and retain it as supplementary material, or reduce it to a single paragraph acknowledging that no future residual-life predictions were produced within a 365-day horizon at any threshold, and explaining why this outcome is expected given the structural label constraints.

**Why it is valuable:** The proxy-RUL layer currently produces zero future crossings at all three thresholds. Presenting this as a "system component" implies a capability that does not exist. A reviewer will immediately ask: "what is the RUL estimate for specimen X?" The honest answer is "right-censored at all thresholds." Removing or shrinking this section focuses the paper on its genuine contributions and prevents a misleading impression of predictive capability.

**Scientific problem it addresses:** Misrepresentation of what the system can do in the current state.

**Expected implementation effort:** Writing only. One to two hours to condense the section, move detailed tables to supplementary material.

**Probability of improving the paper:** High. Removing a weak section that invites scepticism is always beneficial.

**Publication impact:** Medium — the proxy-RUL concept is interesting conceptually; the issue is that it has not produced results with this dataset. Framing it explicitly as a "what would be needed" discussion is more valuable than presenting empty results.

**Reviewer impact:** High. An honest acknowledgement that the method produced no positive RUL estimates is more credible than tables of NULLs presented without comment.

**Priority: HIGH**

---

### R7 — Reframe `surface_total_rust_pct` modeling as verification, not prediction

**Recommendation:** Relabel the `surface_total_rust_pct` benchmark in all tables and text as "label reconstruction verification" rather than a model result. Add a single sentence explaining that the workbook label and the image feature `img_rust_area_ratio_pct` are computed from the same images by equivalent threshold operations (MAE = 0.0002), and that this confirms pipeline consistency rather than demonstrating predictive capability.

**Why it is valuable:** Leaving it presented as a predictive result invites the criticism that the best result in the paper is circular. Preemptively acknowledging it prevents this objection and demonstrates self-awareness that reviewers appreciate.

**Scientific problem it addresses:** The validity of the surface_total_rust_pct result as a scientific claim.

**Expected implementation effort:** Thirty minutes of writing.

**Probability of improving the paper:** High.

**Reviewer impact:** High. A reviewer who spots the near-identity between the feature and the label and finds no disclosure will interpret it as an oversight.

**Priority: HIGH**

---

### R8 — Produce the core diagnostic figure set

**Recommendation:** Assemble five publication-quality figures from existing output CSVs. These are the figures that carry the paper's argument. No new computation is required.

**Figure 1 — Campaign confounding structure:** Scatter plot of `surface_total_rust_pct` vs. `ultimate_load_kn`, points coloured by `n_steel_mesh` (4 vs. 7), with three regression lines: pooled, 4-mesh, 7-mesh. This makes the Simpson's paradox visible at a glance. Data: `mesh_stratified_corrosion_vs_ultimate_load.csv`, `ultimate_load_modeling_table_all_weeks.csv`.

**Figure 2 — Grouped holdout vs. LOCO performance comparison:** Bar chart of MAE and Spearman for all four targets under all three split strategies (grouped, LOTO, LOCO), with error bars from CV fold std. This is the paper's primary results figure. Data: `hidden_damage_feature_ablation_results.csv`, `benchmark_best_model_robustness.csv`.

**Figure 3 — Feature set ablation for `ultimate_load_kn`:** Bar chart comparing MAE under LOCO across the seven feature sets (metadata_only, rgb_only, hsv_only, rgb_hsv, metadata_rgb, metadata_hsv, metadata_rgb_hsv). Shows that adding image features does not improve and may worsen campaign-holdout performance. Data: `feature_set_comparison.csv`, `feature_set_delta_vs_metadata_only.csv`.

**Figure 4 — Surface tracking quality (the positive result):** Scatter of predicted vs. actual `peak_rust_pct` under LOCO, one point per specimen, with Spearman annotation. This is the strongest genuine predictive result and should be given prominent visual treatment. Data: per-fold prediction CSVs from the surface model outputs.

**Figure 5 — Degradation curves for representative specimens:** Four to six representative specimen degradation trajectories with best-fit curves (isotonic, logistic, Gompertz), showing the range of behaviour and the limitation of extrapolation. Data: `degradation_trajectory_grid.csv`, `degradation_best_fits.csv`.

**Expected implementation effort:** Two to three days for figure-quality polish. Raw plots may already exist among the 430 PNGs; the task is selecting and reformatting to publication quality.

**Priority: HIGH** (Figures 1–3); **MEDIUM** (Figures 4–5)

---

### R9 — Add a "what data would be needed" discussion section

**Recommendation:** Add a brief, direct discussion section answering: what experimental design would be required to validly test whether image features predict structural damage? Specifically: (a) multiple campaigns with overlapping mesh counts and NaCl levels; (b) intermediate structural measurements (not just terminal); (c) a minimum specimen count per treatment group for grouped CV to be well-powered.

**Why it is valuable:** This reframes the negative result as a methodological lesson rather than a failure. It tells future researchers precisely what is missing and what the study contributes by identifying the gap. This type of discussion is highly valued by reviewers in engineering journals.

**Expected implementation effort:** One day of writing.

**Probability of improving the paper:** High.

**Publication impact:** High. Papers that clearly define their own limitations and state what would be needed to address them are read more generously by reviewers.

**Priority: MEDIUM**

---

### R10 — SHAP values for the surface model

**Recommendation:** Add SHAP attribution for the `peak_rust_pct` RandomForest model (the strongest genuine result). This replaces mean-decrease-impurity feature importance with additive, interaction-aware attribution.

**Why it is valuable:** `peak_rust_pct` is the paper's positive result. It should be presented with the best available interpretability tools. SHAP beeswarm plots are now standard in applied ML papers and are visually compelling.

**Expected implementation effort:** One to two days. Add `shap` to requirements, run `shap.TreeExplainer` on the fitted model, produce beeswarm and waterfall plots.

**Probability of improving the paper:** Medium. Feature importance from trees is already computed; SHAP adds interpretability depth but does not change the finding.

**Publication impact:** Medium.

**Priority: MEDIUM**

---

## What I Would Do If This Were My Paper

Two weeks. Ranked from highest return on investment to lowest.

---

### Days 1–2: Write the argument, not the methods

**Task:** Draft or rewrite the abstract and introduction around the central negative finding. Write the two-paragraph core argument: (1) the pooled image-structure correlation appears positive but reverses within homogeneous mesh groups; (2) LOCO correctly destroys any model that learned this campaign artefact; (3) therefore image features do not add structural prognostic value in this dataset.

Do this first because every other decision — which sections to cut, which figures to include, what to emphasise — follows from having a clear central claim.

**Effort:** 2 days
**Scientific gain:** High (clarity of contribution)
**Publication gain:** Very high (abstract is what reviewers read first)
**Probability of success:** Very high (no new analysis required)

---

### Day 3: Produce Figure 1 (the Simpson's paradox figure)

**Task:** From `mesh_stratified_corrosion_vs_ultimate_load.csv` and `ultimate_load_modeling_table_all_weeks.csv`, produce a scatter plot of surface rust vs. ultimate load, with points coloured by mesh group and three regression lines drawn (pooled in grey, 4-mesh and 7-mesh in separate colours). Annotate with Spearman values from the CSV (pooled: +0.46; 4-mesh: −0.05; 7-mesh: −0.40).

This figure requires no new computation. It is a one-page assembly task using existing CSV outputs.

**Effort:** 0.5 days
**Scientific gain:** Very high (makes the central mechanism visible)
**Publication gain:** High (a single compelling figure is more persuasive than three pages of text)
**Probability of success:** Very high

---

### Days 3–4: Add mixed-effects linear baseline

**Task:** `pip install statsmodels`. Write a 50-line script that reads `terminal_structural_table.csv`, fits `ultimate_load_kn ~ C(n_steel_mesh) + nacl_pct` (fixed effects only, since LME cannot generalize to a held-out campaign's random intercept under LOCO), evaluates under leave-one-campaign-out by refitting on campaign 1 and predicting campaign 2 (and vice versa), and reports MAE and Spearman. Compare to RandomForest LOCO (MAE = 0.564, Spearman = 0.353).

If the linear model matches or beats RandomForest: the paper's conclusion is strengthened — ML adds nothing over a two-covariate linear model. If the linear model is worse: the paper has a new piece of evidence that the tree-based model does capture some non-linear structure even under LOCO.

**Effort:** 2 days
**Scientific gain:** Very high (resolves the most important open question)
**Publication gain:** High (this comparison will be requested by reviewers)
**Probability of success:** Very high (the comparison is straightforward)

---

### Days 4–5: Bootstrap CIs

**Task:** Add `bootstrap_metric_ci()` to `evaluation.py`. Resample at the specimen level (not observation) within each fold, 1000 resamples, compute 5th/95th percentiles of MAE and Spearman. Update all primary result tables with `mean [CI]` format.

**Effort:** 2 days (1 for code, 1 for rerunning evaluation and updating tables)
**Scientific gain:** Medium (does not change findings, adds precision)
**Publication gain:** High (avoids a certain reviewer comment)
**Probability of success:** Very high

---

### Days 5–6: Produce Figures 2–3 (results and ablation)

**Task:** From `benchmark_best_model_robustness.csv` and `feature_set_comparison.csv` / `feature_set_delta_vs_metadata_only.csv`, produce (a) the grouped vs. LOCO comparison bar chart for all targets, and (b) the feature-set ablation bar chart for `ultimate_load_kn`. Both datasets exist; this is a formatting task.

**Effort:** 1 day
**Scientific gain:** Medium
**Publication gain:** High (these are the core results figures)
**Probability of success:** Very high

---

### Day 6: Fix the surface_total_rust_pct labeling and calibrate proxy-RUL thresholds

**Task A:** Add one sentence to the paper acknowledging the tautology. Relabel in all tables.

**Task B:** Compute percentiles of `wire_area_loss_frac` from `terminal_structural_table.csv`. Write one sentence justifying threshold choices by reference to the data distribution.

**Effort:** 0.5 days total
**Scientific gain:** Medium
**Publication gain:** High (pre-empts two likely reviewer comments)
**Probability of success:** Very high

---

### Days 7–8: Shrink or remove proxy-RUL section

**Task:** Reduce the proxy-RUL section to a focused two-paragraph discussion: (1) what the method computes and why it was attempted; (2) what result was obtained (zero future crossings at all thresholds); (3) what data would be required to produce valid residual-life estimates. Move all tables to supplementary.

**Effort:** 1 day
**Scientific gain:** High (removes a section that undermines the paper's credibility)
**Publication gain:** High
**Probability of success:** Very high

---

### Days 8–9: Write discussion and limitations section

**Task:** Write a direct limitations section covering: (a) one structural measurement per specimen; (b) campaign-design confounding; (c) image preprocessing dependence on provided PNGs; (d) no true failure times; (e) what experimental design would be needed to resolve these limitations. This section converts weaknesses into a constructive methodological contribution.

**Effort:** 1.5 days
**Scientific gain:** High
**Publication gain:** High
**Probability of success:** Very high

---

### Days 9–10: SHAP for `peak_rust_pct`

**Task:** Run `shap.TreeExplainer` on the fitted `peak_rust_pct` RandomForest. Produce a beeswarm plot of SHAP values for the top 10 features. This replaces the existing mean-decrease-impurity importance plot with a more defensible and visually compelling alternative.

**Effort:** 1.5 days
**Scientific gain:** Low (finding does not change)
**Publication gain:** Medium (SHAP plots are now standard and reviewers expect them)
**Probability of success:** High

---

### Days 10–14: Final paper assembly, revision, and submission preparation

**Task:** Integrate all new material, enforce consistent terminology, verify all cited numbers against output CSVs, write acknowledgements and data availability statement, format to target journal style.

**Effort:** 4 days
**Scientific gain:** None (assembly only)
**Publication gain:** Very high
**Probability of success:** Certain

---

## What I Would Stop Working On

---

**Image augmentation.** The verification audit confirmed this was already considered and correctly deprioritised. Augmenting the 791 surface images cannot create new structural labels. The 48 structural rows are fixed. Under grouped specimen splitting, augmented versions of the same specimen always remain in the same fold — they cannot introduce information about unseen specimens. For the surface stage (where augmentation could apply), the models already achieve Spearman > 0.97 under LOCO. There is no performance ceiling to push against. Stop.

**Deeper or richer image models (CNN, ViT, ResNet fine-tuning).** The verification audit confirmed that `main_2` already explored deep image embeddings (ResNet18 frozen features) and the approach was superseded by interpretable classical features. More importantly: the fundamental finding is that image features — regardless of how they are extracted — do not outperform metadata-only models under LOCO for structural targets. This is a dataset-structure problem, not a representation-quality problem. A better image model will learn the same campaign artefact more efficiently, not avoid it. Stop.

**Self-supervised learning or contrastive pretraining.** 791 images is below the minimum practical size for self-supervised visual representation learning. Even if a useful embedding were learned, it would still face the same 48-sample structural-label ceiling and the same campaign confounding under LOCO. The verification audit shows no evidence that richer representations have been tried and failed, but the structural argument is clear: the limit is the experimental design, not the image representation. Stop.

**GAN-based synthetic image generation.** No labeled synthetic images can be generated without knowing their structural properties (`wire_area_loss_frac`, `ultimate_load_kn`). A GAN can produce visually plausible corrosion images but cannot assign physically meaningful structural labels to them. The output would be unlabeled synthetic data, which does not address the binding constraint. Stop.

**Additional feature engineering.** The current pipeline extracts 77 interpretable features covering rust mask area, color histograms (RGB and HSV), GLCM texture, LBP texture, rust blob morphology, and longitudinal strip statistics. The verification audit found 36 high-collinearity feature pairs already pruned and 13 near-constant features excluded. The feature space is mature. The finding that `metadata_only` outperforms `all_cleaned` and `image_time_only` under LOCO is strong evidence that the problem is not feature richness. Additional features will add noise, not signal. Stop.

**Additional ML model families.** Four families (RandomForest, GradientBoosting, XGBoost, CatBoost) have been trained with systematic hyperparameter configurations. The robustness selection framework already identifies the best-performing model per target per split strategy. A fifth or sixth model family is unlikely to change the conclusion that metadata-only models dominate under LOCO for structural targets. The verification audit confirmed this is already exhaustive relative to the dataset size. Stop.

**Optimising LOCO performance for structural targets.** The 3.24× MAE collapse under LOCO for `ultimate_load_kn` is not an optimisation problem. It is the correct answer to the question: "does this model generalise across campaigns?" The answer is no, because the campaigns differ in mesh count and NaCl concentration, and no model trained on one campaign's design space can interpolate to the other. Optimising the model is attempting to change the answer to this question — but the answer is determined by the data, not the model. Stop.

---

## Suggested Final Narrative

### What the paper should actually say

The study set out to test a practical question in structural health monitoring: can repeated surface photographs of corroding specimens support estimation of hidden internal structural damage (wire loss, ultimate load capacity)?

The answer — established with rigorous leakage-safe evaluation — is no, not with this dataset. Surface corrosion can be accurately tracked from images (Spearman > 0.97 for `peak_rust_pct` under campaign holdout). But interpretable image features extracted from those photographs add no measurable value over specimen design metadata alone when predicting internal structural damage under genuine cross-campaign evaluation. The reason is specific and instructive: pooled correlations between surface rust and structural load appear positive but reverse sign within each homogeneous specimen group (4-mesh and 7-mesh), because campaign identity — not corrosion — drives the pooled relationship. Any model trained on this pooled signal learns an artefact, which LOCO correctly destroys.

This is a methodological contribution. It demonstrates precisely why image-based structural prognosis requires controlled experimental designs with overlapping design parameters across validation partitions — something that cannot be retrofitted into an existing single-experiment dataset.

The positive contribution is the surface tracking result and the interpretable feature pipeline: an explicit, threshold-based, fully reproducible feature extraction system that achieves strong cross-campaign consistency for surface corrosion quantification.

### What should be removed

- The proxy-RUL section as a primary result (retain as a brief exploratory note or supplementary material)
- The `surface_total_rust_pct` model as a predictive claim (retain as verification)
- The degradation section as a prognostic claim (retain as descriptive trajectory analysis)
- All performance numbers reported without their LOCO counterpart

### What should be emphasised

- The pooled vs. within-mesh correlation reversal (Figure 1, with explicit numbers)
- The LOCO collapse and its mechanistic explanation (not a failure of the model — a success of the evaluation)
- The metadata-only model selection result (image features add nothing under rigorous evaluation)
- The surface tracking quality (Spearman 0.977 for `peak_rust_pct` under campaign holdout — a genuine result)
- The reproducible interpretable feature pipeline (a usable artefact for the community)

### What title would maximise scientific credibility

**Primary recommendation:**

> Surface Imaging Cannot Substitute for Structural Testing in Ferrocement Corrosion Assessment: Evidence from a Campaign-Confounded Dataset with Rigorous Cross-Campaign Evaluation

**Alternative (if the journal prefers a positive framing):**

> Limits and Opportunities of Repeated-Image Corrosion Tracking for Structural Prognosis: A Leakage-Safe Study in Ferrocement Specimens

**Short form for conference proceedings:**

> Image-Based Corrosion Features Do Not Improve Structural Load Prediction Under Campaign Holdout: A Ferrocement Case Study

The word "rigorous" in the primary title signals honest evaluation rather than optimistic ML benchmarking. The phrase "campaign-confounded dataset" tells a reviewer immediately that the authors understand their own experimental limitation — which is the fastest path to acceptance for a negative-result paper.

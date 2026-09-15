# Chapter 4, Batch B (Sections 4.5–4.8) — Evidence Selection Plan

Internal planning document, written before drafting. All numbers below were
freshly verified against saved repository artifacts in this session.

## 4.5 — Degradation modelling and proxy-RUL feasibility (`main_3`, continued)

- **Research question:** can a specimen-level degradation trajectory, fitted
  from repeated estimates of condition over time, be extrapolated forward to
  a screening estimate of remaining service life?
- **What was implemented:** for each of 48 specimens and 4 targets (2
  directly observed visible-corrosion series, 2 model-estimated structural
  series), a curve is fit to the available per-week values and used to
  forecast forward. A composite "health index" combining all four series is
  also computed. Threshold-crossing times are read off the fitted/forecast
  curves for three wire-loss thresholds (20/25/30%), a load threshold (80%
  of a campaign reference load), and the health-index threshold (0.35); the
  final reported proxy-RUL is the *earliest* of the 25%-wire, load, and
  health-index crossings, extrapolated up to a 104-week horizon beyond the
  last observation.
- **Verified quantities** (`main_3/outputs/degradation_curves.parquet`,
  192 rows = 48 specimens × 4 targets): curve family counts —
  `surface_total_rust_pct` 40 piecewise-linear/8 exponential (median R²
  0.903); `peak_rust_pct` 44/4 (median R² 0.916); both structural series 48
  piecewise-linear each (median R² 0.636 wire-loss, 0.601 load). All four
  series are fit on 15–18 points per specimen — for the structural series,
  these are the same per-week model-estimated values introduced in
  Section~4.4.3, not repeated physical measurements.
- **Verified proxy-RUL outcome** (`main_3/outputs/rul_estimates.csv`, 48
  rows): 33 specimens receive a finite estimate within the 104-week
  horizon; of those, 23 (70%) are exactly zero weeks — meaning the relevant
  threshold was already crossed at the specimen's last observation, not
  projected into the future. 15 specimens never cross within the horizon
  (right-censored). Risk classes: 20 Low, 8 Moderate, 20 High, 0 Critical.
- **Most important limitation:** the majority of "finite" proxy-RUL values
  are degenerate (zero weeks), so the screening tool's practical
  forward-looking content is smaller than the raw finite-count suggests;
  only 10 specimens (33 finite − 23 zero) have a proxy-RUL that is both
  finite and genuinely in the future.
- **Diagnostic that changed interpretation:** because the structural series
  feeding the curve fit are themselves weak under distribution shift
  (Section~4.4.3), uncertainty compounds through the pipeline — a
  degradation curve fit to a noisy estimated series inherits that noise,
  and a threshold-crossing time read off an extrapolated curve inherits the
  curve-fitting uncertainty on top of that.
- **Figure:** `main_3/reports/figures/rul_histogram.png` — real, already
  clearly shows the concentration of finite estimates near zero weeks.
  **ESSENTIAL, reuse as-is** (copy with provenance-preserving name; caption
  must state the 15 censored specimens are not shown in the histogram).
- **Omit:** `risk_distribution.png` (redundant with the risk-class counts,
  which are one sentence of prose) — **OMIT**. Per-specimen degradation
  panels (`degradation_examples_peak_rust.png`,
  `degradation_examples_panel.png`) — illustrative but not necessary given
  the quantitative summary already conveys the finding — **OPTIONAL/OMIT**
  for the main body (candidate for an appendix).
- **Table:** not needed — the handful of summary numbers are more
  proportionate as prose than as a table for this shorter subsection.

## 4.6 — Robustness and diagnostic refinement (`main_4`, pre-refocus)

- **Framing check (important):** `main_3`'s own report already names
  campaign confounding, sparse structural supervision, and the
  "downstream label shortcut" risk (Section~4.4.4). This section is
  written as main_4 **quantifying and acting on** those already-identified
  problems, not discovering them.
- **Feature-redundancy audit, verified against `main_4/FEATURE_DIAGNOSTICS.md`:**
  13 near-constant columns, 1 exact-duplicate pair, 36 high-collinearity
  pairs (|Spearman| ≥ 0.95); `surface_total_rust_pct` vs.
  `img_rust_area_ratio_pct` Spearman = 0.9996 (near-tautological, already
  established qualitatively in Section~4.4.1 for a different feature pair —
  this is the main_4-native, quantified version). Strongest univariate
  correlate of `wire_area_loss_frac` is only 0.382 (an image morphology
  feature); the top-5 univariate correlates of `ultimate_load_kn` are all
  metadata/temporal variables at an *identical* |r|=0.827 (ageing_days,
  week, n_steel_mesh, nacl_pct, terminal_week) — because these variables
  are perfectly campaign-linked on the 48-row structural subset, they are
  numerically indistinguishable predictors. **This directly answers "where
  is the apparently predictive signal actually coming from" for ultimate
  load: campaign-linked metadata, not image content.**
- **Robustness quantification, verified against
  `main_4/outputs/diagnostics/tables/benchmark_best_model_robustness.csv`:**
  see table below. Visible-corrosion targets: relative MAE under LOCO stays
  at or below 1.0× the grouped-holdout MAE (surface total rust actually
  improves, 0.77×; peak rust roughly flat, 0.96×), and Spearman stays above
  0.97 in both cases. Structural targets: `ultimate_load_kn` LOCO MAE is
  3.24× the grouped-holdout value and Spearman falls to 0.35;
  `wire_area_loss_frac` LOCO Spearman turns *negative* (−0.089). **This is
  the section's central diagnostic figure/table** — it must show both
  target families side by side so the contrast, not just the structural
  collapse in isolation, is visible.
- **Model-selection methodology change, verified against
  `main_4/configs/modeling.yaml`:** structural-target model selection is
  now a weighted combination across regimes (`leave_one_campaign_out`
  weighted 0.45, `leave_one_treatment_out` 0.25, `group_shuffle` MAE 0.20,
  `group_shuffle` Spearman 0.10) rather than a single-split "best mean
  model" as in `main_3`, or a test-metric selection as in Phases 1–2. A
  genuine methodological improvement, stated as such.
- **Degradation-curve refinement, verified against
  `main_4/MODEL_IMPROVEMENT_RESULTS.md`:** family selection shifted from a
  baseline dominated by the flexible non-parametric fit (44 of 48
  specimens `monotone_isotonic`, 3 `linear`, 1 `gompertz`) to a more even
  split after revision (21 `monotone_isotonic`, 27 `linear`) — responding
  to the project's own documented concern that the flexible fit can reach
  near-zero training error by interpolation rather than by capturing a
  genuine mechanistic trend.
- **Threshold-status reframing:** rather than collapsing degradation status
  to a single ambiguous "weeks remaining" number as in `main_3`, this phase
  reports explicit status categories (already crossed by the last
  observation / crossed during the observed period / projected to cross
  within the horizon / right-censored) with their fractions, which is a
  more transparent way of communicating the same underlying uncertainty.
- **Project's own stated conclusion, quoted from `main_4/MODEL_IMPROVEMENT_RESULTS.md`:**
  "The improved models are metadata-dominant, so the project still does
  not support strong claims that surface image features robustly infer
  hidden damage." Worth citing close to verbatim as the phase's own
  self-assessment.
- **Figure:** `main_4/outputs/diagnostics/figures/benchmarks/best_model_relative_mae_collapse_heatmap.png`
  — real, already-generated, exactly shows the four targets × three
  regimes relative-MAE contrast. **ESSENTIAL, reuse as-is.**
- **Table:** new compact table with absolute MAE and Spearman (not just the
  heatmap's ratios) for the four targets × three regimes, from the same
  verified CSV — **ESSENTIAL**, complements the figure with the absolute
  numbers the ratios are computed from.
- **Omit:** per-fold stability plots (`hidden_damage_best_model_fold_stability.png`,
  `surface_best_model_fold_stability.png`), full collinearity heatmap
  (`high_collinearity_pairs.png`, 36 pairs — too dense for the main
  narrative), temporal/inventory diagnostic figures (overlap with Chapter
  2's dataset description) — all **OMIT** from the main body.

## 4.7 — Refocused terminal ultimate-load study (`main_4`)

This is the largest subsection, per instructions.

- **Research question, verified against `main_4/README.md` and
  `configs/ultimate_load_refocus.yaml`:** after controlling for specimen
  design, does superficial corrosion add predictive value for terminal
  ultimate load?
- **Why a refocusing, not just another experiment:** the target changes
  from a proxy/derived quantity chain (corrosion → estimated damage →
  degradation curve → threshold crossing) to the one directly measured
  terminal endpoint in the dataset, evaluated with an explicit feature-family
  ablation design from the outset, rather than as an afterthought.
- **Feature-set comparison, verified against
  `main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/feature_set_comparison.csv`
  (48 specimens, 10 grouped-CV splits):** metadata-only (Ridge, 11
  features) achieves MAE 0.173, R²=0.645, Spearman=0.758. Adding HSV
  descriptors leaves MAE essentially unchanged (0.173) and slightly
  improves Spearman (0.771); adding RGB descriptors *worsens* both MAE
  (0.184) and R² (0.584); RGB-only or HSV-only alone are both clearly worse
  than metadata-only (RGB-only MAE 0.253, R²=0.269). **Core finding:
  metadata is the strongest pooled predictor family, and image descriptors
  do not provide a meaningful pooled improvement over it — confirmed
  directly from the saved comparison table, not asserted.**
- **Post-onset subset nuance, verified against the same phase's
  `pooled_post_onset/grouped_cv/feature_set_comparison.csv` (43 specimens,
  excluding nine near-zero-corrosion rows):** here `metadata_rgb_hsv`
  (MAE 0.163, R²=0.660) edges out `metadata_only` (MAE 0.173, R²=0.633) on
  MAE and R², though `metadata_only`'s Spearman (0.803) is still slightly
  higher than the combined set's (0.791). This is a modest, subgroup-specific
  observation — stated as such, not as a reversal of the pooled conclusion.
- **Mesh-stratified robustness, verified against the same
  `final_leaderboard.csv` rows for `mesh_4` and `mesh_7` (24 specimens
  each):** every feature set, including the best-MAE one, has a
  **negative mean R²** within each mesh group (mesh_4: −0.81 to −3.56;
  mesh_7: −0.30 to −4.65), even though raw MAE numbers look superficially
  reasonable (0.14–0.26 kN). **This is the guardrail case explicitly
  flagged in the brief: subgroup MAE alone would misleadingly suggest a
  working model; R² and Spearman (mesh_4 best Spearman ≈0.10; mesh_7 best
  Spearman ≈0.46) show the within-group relationship is weak to
  essentially absent.** Must be stated prominently, not glossed over.
- **Mesh-stratified correlation diagnostic, verified against
  `main_4/outputs/ultimate_load_refocus/correlations/mesh_stratified_corrosion_vs_ultimate_load.csv`
  and cross-checked by direct recomputation from `specimen_summary_table.csv`
  (`surface_total_rust_pct_terminal` vs. `ultimate_load_kn`):** pooled
  Spearman ρ=0.462 (p=0.0009, n=48); mesh_4 ρ=−0.046 (p=0.83, n=24); mesh_7
  ρ=−0.401 (p=0.052, n=24, opposite sign to the pooled estimate). The
  saved output table itself labels the pooled row `"Pooled (confounded)"`.
  **Interpretation, per guardrails: this is evidence of confounding by
  mesh/campaign group structure, not proof that no corrosion-capacity
  relationship exists under any condition — worded accordingly.**
- **Campaign holdout, verified against the same leaderboard's
  `leave_one_campaign_out` rows:** every feature set collapses to strongly
  negative R² (metadata-only: MAE 0.465, R²=−4.64), consistent with
  campaign holdout being a severe extrapolation stress test
  (Section~2.3.3/2.6), not evidence against the in-distribution finding.
- **Residual-refinement experiment, verified against the same leaderboard's
  `specimen_summary_residual_refinement` rows:** attempting a mesh-aware
  residual-correction second stage on top of the metadata-only baseline
  *worsened* MAE, RMSE, and Spearman relative to the baseline (explicitly
  labelled `"worsened"` in the saved table) — a negative result kept
  visible, not hidden.
- **Models actually compared:** Ridge (metadata-heavy feature sets) and
  CatBoost (feature sets including RGB/HSV) are the models that win most
  feature-set cells in the saved leaderboard; XGBoost and GradientBoosting
  appear as the winning model only under `leave_one_campaign_out` cells
  where every feature set is failing regardless of model choice. Reported
  at the level of "which family tends to win," not exhaustively.
- **Figure:** new, focused 3-panel figure (mesh_4 / mesh_7 / pooled) for
  `surface_total_rust_pct` vs. `ultimate_load_kn`, generated directly from
  `specimen_summary_table.csv` — **ESSENTIAL**. The existing project
  figure (`mesh_stratified_corrosion_vs_ultimate_load.png`) is real and
  correct but shows 5 corrosion variables × 3 groupings (15 panels); four
  of the five variables are highly correlated with each other or with
  `surface_total_rust_pct` (already established), so a focused 3-panel
  reproduction of the same underlying data communicates the one point that
  matters without the redundant panels. Documented as reproducible from a
  saved table in evidence_log.md.
- **Table:** new compact table, pooled grouped-CV feature-set comparison
  (7 rows, MAE/R²/Spearman) — **ESSENTIAL**, this is the table the core
  conclusion rests on.
- **Omit:** the full 15-panel existing correlation figure (superseded by
  the focused version above for the main body, though still available in
  the repository); per-specimen trajectory figures in
  `best_model_package/` (better suited to an appendix); the residual /
  uncertainty diagnostic plots under `residual_refinement/` (the negative
  finding is fully captured by one sentence plus the leaderboard row) —
  all **OMIT** from the main body.

## 4.8 — Four-class corrosion classification and augmentation

- **How this differs from Section 4.4's classification work:** `main_3`
  modelled a **five**-category historical schema on the 792-row basis
  (Section~2.5, Table 1.6); this later effort targets the **current**
  four-category schema (`A_Total_Rust_Category_(1-4)`) on the 791-row
  aligned basis, with its own dataset preparation and augmentation
  pipeline, entirely independent of `main_3`'s or `main_4`'s code.
- **Class distribution, verified against `Documentation/augmentation_methodology_final.md`
  Table 9 (cross-checked against Chapter 2's Table 1.2):** 658/99/20/14
  images across classes 1–4 (83.2%/12.5%/2.5%/1.8%) — severely imbalanced.
- **Augmentation methodology:** five recipe families (brightness/contrast,
  saturation/colour-balance, blur/noise, a compound recipe, and a
  mirror-flip+brightness recipe), each applied at a fixed 6× expansion
  factor (one original + five augmented copies) **uniformly across all
  four classes** — verified in the same Table 9: every class expands by
  exactly 6×, so the post-augmentation class proportions are numerically
  identical to the pre-augmentation ones (3948/594/120/84 → same 83.2%
  majority share). **Augmentation increases the absolute number of
  training images but does not itself rebalance the classes**; the
  project's own documentation states that class-weighting or an
  equivalent technique remains a requirement for the (not yet written)
  training script.
- **Why mirror flip is acceptable here but was banned for the regression
  work in `AUGMENTATION_PLAN.md` (Section~3.10 contradiction register,
  already noted in Chapter 2/3):** verified directly in
  `augmentation_methodology_final.md`'s parameter-justification table —
  mirror flip is justified specifically because "total coverage is
  position-invariant" for a whole-image severity label, unlike the
  strip-position and rust-location features used elsewhere in the project,
  for which left-right position is part of the signal.
- **Rejected augmentations, verified against the same document:** MixUp
  and CutMix (rejected because severity classes are discrete and cannot be
  meaningfully interpolated or partially blended); GAN/diffusion synthesis
  (rejected as infeasible with fewer than 20 training images in the
  smallest classes, and out of scope); elastic deformation and cutout
  (rejected as physically implausible or label-corrupting for a flat,
  perpendicular-photographed specimen); heavy hue shift, vertical flip,
  and large rotation (rejected as producing colours or orientations that
  do not occur in the real acquisition setup). Summarised as a short list
  of reasons, not reproduced verbatim.
- **Leakage-safety, verified directly against `augmentation/make_splits.py`:**
  a runtime check (`raise RuntimeError` if any augmented row appears in the
  validation or test manifest) enforces that augmentation is applied to
  training specimens only — not merely documented intent.
- **Resulting dataset size, verified against `Data/splits/*.csv` row
  counts:** train 3,846 rows (includes augmented copies), validation 75,
  test 75 — all real, unaugmented images.
- **Explicit status (verified: no training code exists anywhere in
  `augmentation/`, confirmed by the folder's own `README.md` and by a
  fresh listing of the directory in this session):** dataset preparation,
  class-distribution analysis, specimen-level splitting, and the
  augmentation pipeline are complete; no classifier (ResNet-50, ViT, or
  otherwise) has been trained, compared, or evaluated. This is stated as
  the section's closing sentence, not qualified or hedged further.
- **Figure:** candidate — one of the project's own recipe example panels
  (`augmentation/figures/recipe4_combined.png` or similar) showing
  before/after examples. **OPTIONAL** — decided to include one small
  reused example panel only if it fits the length budget without pushing
  the subsection into a full methodology write-up; otherwise **OMIT** and
  rely on the prose description plus one compact table.
- **Table:** compact class-distribution-before/after-augmentation table
  (4 rows) — **ESSENTIAL**, the clearest way to show the imbalance and the
  uniform 6× expansion in one place without prose repetition.

## Overall figure/table budget, Batch B

- Figures: 1 reused (`rul_histogram.png`, §4.5), 1 reused
  (`best_model_relative_mae_collapse_heatmap.png`, §4.6), 1 new
  (mesh-stratified 3-panel, §4.7). Possibly 1 optional reused augmentation
  example panel (§4.8), included only if length permits.
- Tables: 1 new (§4.6 robustness numbers), 1 new (§4.7 feature-set
  comparison), 1 new (§4.8 class distribution).
- This keeps Batch B at 3–4 figures and 3 tables across four subsections,
  consistent with "selective scientific storytelling" rather than
  exhaustive documentation.

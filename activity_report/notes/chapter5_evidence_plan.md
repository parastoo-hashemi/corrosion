# Chapter 5 — Integrated Results and Comparative Analysis: Synthesis Evidence Plan

Internal planning document. Not part of the final report. Written before
drafting, per instructions. Organised by scientific question, not by
repository phase. All facts below are either already verified in
`evidence_log.md` (Chapters 2–4 passes; cited by section number below) or
newly verified in this session (cited with source path and marked **NEW**).

Chapter 5's job is synthesis: it must not re-narrate Chapter 4's chronology.
Every row below states what Chapter 5 is allowed to *conclude*, not what
Chapter 4 already *reported* — the distinction the chapter itself must
observe.

---

## Q1. How reliably can visible surface corrosion be estimated from images?

- **Strongest supporting evidence:** main_3 interpretable-feature models
  reach useful grouped-holdout accuracy for both continuous visible-corrosion
  targets (total rust MAE 1.38/R²=0.646; peak rust MAE 4.21/R²=0.784;
  Chapter 4 §4.4.1) and **remain positive under LOCO** (R²=0.582, 0.595).
  main_4's independently re-audited robustness benchmark reinforces this at
  a different feature/dataset vintage: surface targets' LOCO MAE is *at or
  below* their own grouped-holdout MAE (0.77× and 0.96×), with Spearman
  ≥0.97 under LOCO (Chapter 4 §4.6).
- **Strongest contradicting/limiting evidence:** (a) both visible-corrosion
  targets go **negative** under LOTO in main_3 (total rust R²=−0.677, peak
  rust R²=−0.077; Chapter 4 §4.4.1) — treatment-level transfer is markedly
  less stable than campaign-level transfer, and this must not be smoothed
  over by only citing LOCO. (b) The Phase-1 classical baseline's strongest
  number (MAE 2.38, R²=0.900) is substantially a restatement of the
  colour-threshold rule used to build its own label (one feature = 91.5% of
  importance; Chapter 4 §4.2) — not independent evidence of a learned visual
  concept. (c) main_4's own feature-redundancy audit found
  `surface_total_rust_pct` correlated with a single image feature
  (`img_rust_area_ratio_pct`) at Spearman 0.9996 (Chapter 4 §4.6) — the
  **total-rust** benchmark in particular is close to label reconstruction,
  not an independent predictive test, and must not be cited as a headline
  success on its own. **Peak rust is the more meaningful test** because no
  comparably near-tautological feature pairing was found for it.
- **Contributing phases:** Phase 1 (`main`, tautology caveat), Phase 2
  (`main_2`, ResNet-18 embedding), Phase 3 (`main_3`, interpretable
  features, all three regimes), Phase 4a (`main_4`, robustness
  requantification).
- **Directly comparable?** Only *within* a phase (e.g. main_3's own
  GH/LOTO/LOCO numbers for the same target, same feature set, same
  dataset basis). **Not** directly comparable *across* phases: main_3 is
  792-row/91-feature; main_4 is 791-row/reduced-and-audited feature set;
  main_2 uses a ResNet-18 embedding on a different target family
  definition entirely (peak rust only, no total-rust equivalent tested).
  Chapter 5 compares these at the level of *robustness pattern*
  (LOCO-robust/LOTO-fragile in both main_3 and main_4) and *evidential
  status* (tautology risk), not at the level of raw MAE ranking.
- **Final bounded conclusion:** Visible surface corrosion is the project's
  most reliably estimated quantity from images, but "reliable" must be
  qualified twice: it holds for peak rust more than for total rust (label-
  reconstruction risk), and it holds under campaign-level transfer more
  than under treatment-level transfer. It is not universally robust.
- **Candidate table/figure:** Table 5.1 (comparability matrix) row;
  contributes to optional Figure 5.1 (relative-robustness comparison).
- **Should NOT be compared:** main_3's total-rust MAE (1.38, 792-row,
  91-feature) against main_4's total-rust MAE (0.177, 791-row, redundancy-
  audited feature set) as if one phase is "better" — different feature
  sets, different dataset bases, and the main_4 number is itself flagged as
  a near-tautological reconstruction benchmark, not a headline result.

## Q2. How reliably can hidden structural condition be inferred?

- **Strongest supporting evidence:** main_3's grouped-holdout results show a
  "modest but non-trivial" relationship (wire-area loss R²=0.310; ultimate
  load R²=0.385; Chapter 4 §4.4.2) — not zero, and not dismissible outright
  under the most favourable (least demanding) evaluation regime.
- **Strongest contradicting/limiting evidence:** every structural result
  collapses under both stricter regimes, in both main_3 and main_4:
  main_3 LOCO R² = −0.39 (wire) / −8.36 (load); LOTO R² = −5.48 (wire) /
  −4.57 (load). main_4's independently re-audited robustness benchmark
  shows the same pattern on a different feature set: ultimate-load LOCO
  MAE is 3.24× its own grouped-holdout MAE (Spearman falling to 0.35), and
  wire-area-loss LOCO Spearman turns **negative** (−0.089) — worse than no
  rank information at all. Feature-importance/correlation diagnostics in
  both phases point to the same root cause: main_3's full-data ultimate-
  load model is dominated by steel-mesh and campaign indicators, not image
  descriptors (§4.4.2); main_4's redundancy audit finds the top five
  univariate correlates of ultimate load are five metadata/temporal
  variables tied at exactly |r|=0.827 (§4.6) — a direct numerical signature
  of campaign confounding on the 48-row structural subset.
- **What sparse 48-row supervision implies:** every structural number in
  the project rests on exactly 48 labelled specimens, one observation per
  specimen (Chapter 2 §1.4/1.7). This bounds statistical power well below
  what the dense visible-corrosion labels support, and is the single most
  important reason structural inference is systematically weaker and less
  stable than visible-corrosion inference — not a difference in modelling
  effort between the two lines of work.
- **Contributing phases:** Phase 3 (`main_3`, mixed-input, all regimes),
  Phase 4a (`main_4`, feature audit + robustness-weighted refinement),
  Phase 4b (`main_4`, terminal-load refocus — treated separately under Q3
  because it reframes the question rather than repeating this one).
- **Directly comparable?** main_3's structural numbers (792-row basis,
  mixed-input feature set including manually assigned corrosion labels)
  and main_4's (791-row basis, redundancy-audited feature set, robustness-
  weighted model selection) are **not** numerically comparable as a
  leaderboard. They are comparable as two independent tests of the same
  underlying finding (sparse-and-confounded structural signal), which is
  the comparison Chapter 5 makes.
- **Important distinction to state explicitly:** main_3's structural models
  are mixed-input (metadata + manual corrosion labels + image features,
  §4.4.2); main_4's *final* robustness-weighted structural models are
  **metadata-only** (`best_models.csv`: wire-area-loss → CatBoost,
  metadata_only; ultimate load → RandomForest, metadata_only — Chapter 4
  §4.6 QC-correction row). The project's own best structural models,
  after the robustness-weighting refinement, use no image input at all.
  This is a stronger and more specific statement than "structural
  inference is weak" — it is evidence about *where* whatever structural
  signal exists actually comes from.
- **Final bounded conclusion:** The available evidence supports
  substantially weaker and less stable structural inference than visible-
  corrosion inference, driven by sparse supervision (48 rows) and campaign-
  linked confounding, and the project's own final best structural models
  do not use image input at all. This does not establish that structural
  prediction from corrosion images is impossible in principle — only that
  it is not established by the evidence gathered here.
- **Candidate table/figure:** Table 5.1 row; contributes to optional
  Figure 5.1.
- **Should NOT be compared:** main_3's ultimate-load MAE (0.121 kN, 38/10
  split, mixed-input, 792-row basis) against main_4's ultimate-load MAE
  (0.174 kN pooled grouped-CV, metadata-only, 791-row basis, 10 repeated
  splits) as a direct leaderboard — different feature sets, different
  splits, different dataset bases, already flagged in Chapter 4 §4.4.2 and
  repeated here because Chapter 5 is exactly where the temptation to make
  this comparison numerically would arise.

## Q3. What information do images contribute beyond metadata?

This is the "images contain signal" vs. "images add incremental value"
distinction the brief singles out — the two are logically independent and
Chapter 5 must keep them so.

- **Strongest supporting evidence for "images add incremental value":** the
  post-onset subset analysis (43 of 48 specimens with measurable terminal
  corrosion) shows `metadata+RGB+HSV` edging ahead of `metadata_only` on
  MAE (0.163 vs. 0.173 kN) and R² (0.660 vs. 0.633) — Chapter 4 §4.7.1.
  This is real, verified evidence, not fabricated to make the section
  balanced.
- **Strongest contradicting/limiting evidence:** the pooled, full-sample
  comparison (all 48 specimens, the primary analysis) shows metadata-only
  Ridge as the strongest configuration by MAE (0.173 kN) and second-
  strongest by Spearman (0.758); adding RGB descriptors *worsens* both MAE
  and R² (Chapter 4 §4.7.1). The post-onset subset result does not overturn
  this — it is explicitly a narrower, subset-specific observation
  (metadata_only still has marginally higher Spearman even in that
  subset, 0.803 vs. 0.791), and the pooled analysis, not the subset one, is
  the phase's primary comparison.
- **Historical two-way comparisons are weaker evidence than the three-way
  one:** main_2's image-only-vs-multimodal comparison (Chapter 4 §4.3)
  never included a metadata-only baseline (Chapter 3 §3.5 already states
  this explicitly), so it cannot answer "do images add value beyond
  metadata" at all — it can only speak to "does adding metadata to an
  image model help," which is a different and weaker question. Chapter 5
  must not retroactively treat main_2 as if it had run the full ablation.
  The terminal-load-focused phase (`main_4`, Chapter 4 §4.7) is the
  **only** phase that ran the complete image-only / metadata-only /
  combined three-way comparison as a designed, central part of its
  methodology (Chapter 3 §3.5).
- **Contributing phases:** Phase 2 (`main_2`, partial two-way comparison,
  explicitly flagged as incomplete), Phase 4b (`main_4`, complete three-way
  comparison, pooled and post-onset subset).
- **Directly comparable?** main_2's numbers and main_4's numbers are not
  comparable to each other at all (different targets — current-week peak
  rust vs. terminal ultimate load; different representations — ResNet-18
  embedding vs. RGB/HSV summary statistics; different dataset bases).
  Chapter 5 does not attempt a numeric comparison between them; it uses
  main_2 only to establish that the *ablation itself* was incomplete
  historically, and main_4 as the phase where the ablation was done
  properly.
- **Final bounded conclusion:** For terminal ultimate load — the only
  target with a complete three-way ablation — metadata is the strongest
  pooled predictor, and images do not provide a reliable pooled
  improvement over it, with a narrow, non-overturning exception once
  corrosion has visibly onset. "Images contain some signal" (true, in the
  post-onset subset and in the general visible-corrosion estimation task
  of Q1) is not equivalent to "images add incremental value beyond
  metadata for structural prediction" (not established, and contradicted
  by the primary pooled analysis).
- **Candidate table/figure:** Table 5.2 row ("Incremental image value").
  No new figure needed — Chapter 4's Table 3.4 already carries the numbers;
  Chapter 5 states the conclusion in prose, citing it by reference.
- **Should NOT be compared:** main_2's image-only/multimodal MAE reversal
  (peak rust, current-week) against main_4's feature-set comparison
  (ultimate load, terminal) as if they were two data points on the same
  question — they answer different, only superficially similar, questions.

## Q4. How sensitive are conclusions to evaluation regime and domain shift?

- **What changed when evaluation became harder, by target family:**
  - *Visible-corrosion targets:* robust under LOCO (both main_3 and main_4
    show R² staying positive / MAE ratio ≤1.2× grouped-holdout), but
    **not** robust under LOTO (both main_3 visible-corrosion targets go
    negative; Chapter 4 §4.4.1). Treatment-level shift, not campaign-level
    shift, is the visible-corrosion layer's weak point — the opposite
    pattern from the structural layer (below).
  - *Structural targets:* fragile under both stricter regimes in both
    phases, with LOCO consistently the more damaging of the two for
    ultimate load specifically (main_3 LOCO R²=−8.36 vs. LOTO R²=−4.57;
    main_4 LOCO MAE ratio 3.24× vs. LOTO ratio 1.17×, computed directly
    **NEW** from `benchmark_best_model_robustness.csv`: LOTO MAE 0.2034 /
    GH MAE 0.1744 = 1.166×). For wire-area loss, LOCO Spearman actually
    turns negative while LOTO Spearman stays weakly positive (0.275) —
    **NEW**, same source file — so for this specific target LOCO is the
    more damaging regime by rank-correlation too.
- **Why LOCO and LOTO are not "two versions of the same test":** LOCO
  holds out an entire campaign, and campaign identity is perfectly
  entangled with steel-mesh configuration, chloride concentration, and
  ageing duration (Chapter 2 §1.6). LOTO holds out a treatment protocol
  within otherwise-similar specimens. This is why the two regimes damage
  the two target families asymmetrically: campaign holdout is an
  extrapolation test across the design space (relevant to whatever in a
  model's signal is design-linked — which Q2 established is most of the
  structural signal), while treatment holdout is a test within a single
  design point, more relevant to whatever in a model's signal is treatment-
  specific (which affects the smaller, uneven treatment groups underlying
  the visible-corrosion LOTO instability, §4.4.1).
- **Contributing phases:** Phase 3 (`main_3`, first phase to test all three
  regimes systematically), Phase 4a (`main_4`, requantification with an
  audited feature set), Phase 4b (`main_4`, LOCO tested for terminal load
  specifically, plus the mesh-stratified within-group analysis which is a
  third, complementary way of exposing the same design confounding without
  invoking either LOTO or LOCO).
- **Directly comparable?** The *ratios* (regime MAE ÷ own grouped-holdout
  MAE; regime R² or Spearman directly, since these are already scale-free)
  are comparable across main_3 and main_4 in the qualitative sense of "did
  this target family's robustness pattern replicate" — even though the
  underlying absolute MAEs are not comparable (different feature sets,
  different dataset bases). This is the basis for the optional synthesis
  figure below.
- **Optional synthesis figure — Figure 5.1 (tentative):** a compact bar
  chart of relative MAE (regime MAE ÷ own grouped-holdout MAE) for the two
  visible-corrosion targets and the two structural targets, computed
  separately for main_3 and main_4, under LOTO and LOCO. All quantities are
  ratios to each model's own baseline, so no raw MAE from different phases
  is placed on a shared axis. **Verified inputs (NEW, computed directly
  this session from already-logged source CSVs):**
  - main_4 (`benchmark_best_model_robustness.csv`): surface_total_rust_pct
    LOCO/GH=0.767, LOTO/GH=0.549; peak_rust_pct LOCO/GH=0.964, LOTO/GH=0.758;
    wire_area_loss_frac (diagnostic RF row) LOCO/GH=1.181, LOTO/GH=1.139;
    ultimate_load_kn LOCO/GH=3.236, LOTO/GH=1.166.
  - main_3 (Chapter 4 Table 3.2, already-verified numbers): total rust
    LOCO/GH=2.10/1.38=1.522, LOTO/GH=1.53/1.38=1.109; peak rust
    LOCO/GH=6.21/4.21=1.475, LOTO/GH=4.74/4.21=1.126; wire-area loss
    LOCO/GH=12.28/3.90=3.149, LOTO/GH=10.76/3.90=2.759; ultimate load
    LOCO/GH=0.624/0.121=5.157, LOTO/GH=0.158/0.121=1.306.
  - **Decision:** include this figure only if it renders cleanly as a
    single compact panel (8 bar-groups) without needing extensive caption
    caveats beyond stating the ratio definition and the two phases' feature-
    set/dataset differences once. If it becomes visually cluttered, fall
    back to folding the same ratios into Table 5.1 instead and drop the
    figure, per the "very few figures" instruction.
- **Final bounded conclusion:** Model robustness is target-family-specific
  and regime-specific, not phase-specific: the same qualitative pattern
  (visible-corrosion sturdier than structural; LOTO the visible-corrosion
  layer's weak point; LOCO the structural layer's most damaging regime)
  replicates independently in main_3 and main_4 despite their different
  feature sets and dataset bases, which is itself evidence that the
  pattern reflects the data's design structure rather than an artifact of
  one phase's modelling choices.
- **Should NOT be compared:** raw MAE values across main_3 and main_4 on a
  shared axis — only the ratios, and only for the qualitative
  robustness-pattern conclusion above, not for ranking one phase's models
  against the other's.

## Q5. What can and cannot be concluded about degradation and remaining life?

- **main_3 (first-generation proxy-RUL, Chapter 4 §4.5):** composite
  derivation across four series (two observed, two model-estimated),
  three threshold types, 104-week (728-day) horizon. Of 48 specimens, 33
  finite estimates, 23 of those exactly zero weeks, 15 right-censored —
  only 10 specimens carry a genuinely forward-looking finite estimate.
- **main_4 (refined threshold-status framing) — NEW verification this
  session:** `main_4/configs/thresholds.yaml` shows a narrower,
  single-target derivation (`predicted_wire_area_loss_frac` only, three
  thresholds 0.20/0.30/0.40, horizon **365 days**, i.e. ≈52 weeks — not
  104 weeks/728 days as in main_3; this horizon difference is itself a
  protocol change that must be stated, not silently treated as the "same"
  horizon). Directly verified from
  `main_4/outputs/models/proxy_rul/proxy_rul_summary.json` and
  `proxy_rul_estimates.csv` (144 rows = 48 specimens × 3 thresholds):
  **`n_future_crossings_within_horizon` is exactly 0 at all three
  thresholds** — every one of the 144 specimen/threshold combinations is
  classified as either `crossed_by_baseline` (already past threshold at
  the specimen's first observation — 32/48 at the 0.20 threshold),
  `crossed_during_observation` (2 cases total), or
  `not_crossed_within_horizon` (right-censored — 97/144). There is
  **no genuinely forward-looking finite crossing anywhere in the refined
  pipeline's output**, a stronger and more conservative outcome than
  main_3's ten forward-looking cases.
  - **Open concern surfaced by the project's own documentation (NEW,
    `main_4/NEXT_STEPS_PLAN.md` §2.3, already read in the prior QC pass):**
    the same document flags, as an unresolved validation check, that "at
    week 0, many specimens already have predicted wire-area-loss fractions
    near or above 0.2, even when visible rust is essentially zero" — which
    is directly consistent with the 32/48 `crossed_by_baseline` figure just
    verified. This is stated in Chapter 5 as an **open, project-flagged
    plausibility concern**, not a confirmed modelling error, since the
    project's own documentation frames it as a validation check still
    needed rather than a resolved finding.
- **What this evolution means scientifically:** the refined pipeline did
  not "improve" the RUL estimates in the sense of producing more
  confident forward-looking numbers — it became more conservative and, if
  anything, more sceptical of its own baseline predictions, while
  simultaneously surfacing (via its own next-steps documentation) a
  concrete physical-plausibility question about those same baseline
  predictions. Read together, both generations of the pipeline demonstrate
  that the four-step derivation (Chapter 3 §2.8) can be executed end to
  end, and both generations' own outputs argue against treating the
  resulting numbers as validated remaining-life estimates.
- **Contributing phases:** Phase 3 (`main_3`, composite/104-week),
  Phase 4a (`main_4`, single-target/365-day, threshold-status framing).
- **Directly comparable?** No — different target composition (composite
  four-series vs. single wire-loss series), different threshold definitions,
  and a different horizon (104 vs. ~52 weeks). Chapter 5 compares them only
  at the level of "does either generation produce validated forward-looking
  estimates" (no, in both cases, for different but reinforcing reasons),
  not at the level of specimen-by-specimen or count-by-count agreement.
- **Final bounded conclusion:** The project's degradation/proxy-RUL work
  is a genuine, reproducible feasibility demonstration of the derivation
  chain, evaluated twice under two different (and non-comparable)
  configurations, both of which reinforce the same conclusion: this is an
  exploratory degradation/threshold-screening framework, not a validated
  remaining-life prediction method. True RUL remains unavailable in this
  dataset (Chapter 3 §2.8).
- **Candidate table/figure:** Table 5.2 row ("Proxy-RUL"). No new figure —
  Chapter 4 already carries `fig_4_4_main3_proxy_rul_histogram.png`; a
  visual for main_4's all-zero-crossings result would be a single flat bar
  and adds nothing beyond the sentence already given above.
- **Should NOT be compared:** main_3's "33 finite / 23 zero / 10 forward-
  looking" breakdown against main_4's "0 forward-looking" result as though
  computed under the same protocol — the horizon, target, and threshold
  definitions all differ, as stated above.

## Q6. What is the current status of the four-class classification branch?

- **Completed, verified (Chapter 4 §4.8, all already logged):** current
  four-class schema definition (Chapter 2 Table 1.6); class-distribution
  characterisation (658/99/20/14, 83.2%/12.5%/2.5%/1.8%); specimen-level
  grouped train/val/test split with an enforced leakage-safety runtime
  check; five-recipe, uniform 6× augmentation; the corrected split/
  inventory accounting from the Chapter 4 QC pass (global inventory 4,746
  vs. actually-used manifests 3,846/75/75 = 3,996).
- **Not yet available:** any trained classifier, any ResNet-50/ViT
  comparison, any accuracy/macro-F1/confusion-matrix result. Verified by a
  fresh directory listing showing no training code exists anywhere under
  `augmentation/` (Chapter 4 §4.8 evidence-log row, already logged).
- **Contributing phases:** the classification/augmentation effort only —
  this branch has no code dependency on any earlier phase (Chapter 4 §4.8)
  and no phase-comparison question arises for it.
- **Directly comparable?** Not applicable — there is no performance number
  to compare against anything else in the project.
- **Final bounded conclusion:** this branch currently contributes
  methodology and data-preparation evidence (a leakage-safe, class-
  distribution-aware, reproducible pipeline) to the report, not model-
  performance evidence. It cannot yet be used to support or contradict any
  claim about classification accuracy.
- **Candidate table/figure:** Table 5.2 row only ("Four-class
  classification" — evidence level "exploratory" or "not yet evaluated").
  No figure — nothing quantitative to plot.
- **Should NOT be compared:** this branch against main_3's five-category
  classification results (§4.4.1) as though they were two data points on
  the same four-vs-five-class question — the schemas differ (Chapter 2
  Table 1.6) and, more importantly, the current branch has no trained-model
  result to compare at all.

---

## Cross-cutting comparability rules for the chapter (restated for drafting discipline)

1. No MAE/R² value from one phase is placed in the same table row or the
   same sentence as a value from another phase unless the row/sentence
   also states the differing dataset basis, feature set, and evaluation
   regime, or the comparison is explicitly a ratio-to-own-baseline (as in
   the Q4 figure).
2. "Images contain signal" (supported for peak-rust visible-corrosion
   estimation, Q1) and "images add incremental value beyond metadata"
   (not supported for terminal ultimate load, Q3) are different claims and
   must never be conflated into one sentence without the distinguishing
   clause.
3. Every mention of LOCO must either state or clearly presuppose (via
   back-reference to Chapter 2 §1.6/Chapter 3 §2.3.3) that it is an
   extrapolation stress test in this dataset, not an estimate of expected
   future performance.
4. Diagnostic per-strategy winners (Chapter 4 Table 3.3) and final
   robustness-weighted selections (`best_models.csv`) remain distinguished
   wherever Chapter 5 cites main_4's structural models (Q2).
5. "Proxy-RUL" is never shortened to "RUL" anywhere in Chapter 5.
6. main_3's five-class categorical results and the current four-class
   classification branch are never placed in the same comparative sentence
   without stating the schema difference (Chapter 2 Table 1.6).

## Planned chapter structure (adopting the suggested structure; no changes needed)

5.1 Scope and Rules for Cross-Phase Comparison (very short, ~0.3 page)
5.2 Visible-Corrosion Estimation (Q1) — subsections: current estimation,
    robustness, interpretability/tautology
5.3 Structural-Condition Prediction (Q2)
5.4 Incremental Value of Image Information (Q3)
5.5 Robustness and Distribution Shift (Q4) — optional Figure 5.1
5.6 Degradation and Proxy-RUL Evidence (Q5)
5.7 Current Four-Class Classification Branch (Q6, short)
5.8 Integrated Findings — Table 5.1 (comparability matrix) + Table 5.2
    (integrated scientific-findings table, qualitative evidence-level terms
    only: well supported / conditionally supported / exploratory / not yet
    evaluated, each defined in the surrounding prose)

Target length: 4–6 pages (hard ceiling before compression: ~7). Tables: 2
(5.1, 5.2). Figures: 0–1 (5.1, optional, decided at drafting time per the
rendering-clarity criterion stated under Q4).

---

## QC correction pass (post-draft, targeted scientific review)

Six issues were identified in a review of the drafted chapter and resolved
by direct re-verification against repository outputs. The Q1/Q4 sections
above are the *original* pre-drafting plan and are left as historical
record; the corrections below are what actually governs the compiled
chapter text. Where the two disagree, this section is authoritative.

**1. Visible-corrosion LOTO synthesis was wrong for main\_4.** The
original plan (Q1, item (a) above) asserted that main\_4 "reinforces" or
replicates main\_3's treatment-level fragility for visible-corrosion
targets. Directly re-inspecting
`main_4/outputs/diagnostics/tables/benchmark_best_model_robustness.csv`
shows the opposite: for both `surface_total_rust_pct` (GradientBoosting)
and `peak_rust_pct` (RandomForest), leave-one-treatment-out MAE is *below*
grouped-holdout MAE (ratios 0.549 and 0.758) and Spearman stays above
0.97. R² is not reported in that summary table; recomputed directly this
session from the phase's own per-fold files
(`main_4/outputs/models/surface/{surface_total_rust_pct,peak_rust_pct}/leave_one_treatment_out/*_fold_metrics.csv`,
9 folds each), mean R² is **0.9948** (total rust) and **0.9574** (peak
rust) — near-perfect, not negative. Leave-one-treatment-out in main\_4
uses 9 finer-grained treatment splits (`split_group_treatment` in
`main_4/src/corrosion_proxy_rul/models_surface.py`) rather than main\_3's
7 coarse treatment protocols; this may partly explain the divergence, but
the evidence establishes only the outcome, not the mechanism. **Treatment-
level fragility for visible-corrosion targets is a main\_3-specific
finding and does not replicate in main\_4.** Corrected in
Section~5.2 (Robustness), Section~5.5, and Table 5.2 (both the "Visible
surface corrosion" and "Cross-regime / cross-campaign robustness" rows).

**2. Figure 5.1's ratio was not a same-model comparison for main\_3.**
Chapter 4's Table 3.2 reports the *best-available* model per (target,
regime) cell, and the winning model changes across regimes for some
targets (e.g. total rust: RandomForest at grouped-holdout/LOCO, MLP at
LOTO). The original Figure 5.1 sourced main\_3's ratios directly from
Table 3.2, so its "ratio to that phase's own baseline" claim was not
actually a same-model ratio for main\_3. **Fix:** regenerated using a
fixed-model rule — for each target, select that phase's own
grouped-holdout-winning model (recomputed directly this session from
`main_3/outputs/corrosion_regression_metrics.csv` and
`damage_regression_metrics.csv`, aggregating per-fold rows by
`(target, strategy, model)`), then read that *same* model's rows under
leave-one-treatment-out and leave-one-campaign-out. Verified fixed models
and ratios:

  | Target | main\_3 fixed model | GH MAE | LOTO/GH | LOCO/GH |
  |---|---|---|---|---|
  | surface/total rust | random\_forest | 1.3814 | 1.194 | 1.517 |
  | peak rust | mlp\_regressor | 4.2087 | 1.127 | 1.767 |
  | wire-area loss | random\_forest | 3.8993 | 2.804 | 3.679 |
  | ultimate load | random\_forest | 0.1207 | 1.311 | 5.375 |

  main\_4's `benchmark_best_model_robustness.csv` was independently
  confirmed (by reading `build_best_model_robustness()` in
  `main_4/src/corrosion_proxy_rul/diagnostics.py`) to *already* be
  constructed this way — it selects each target's grouped-holdout winner
  and reports that model's own rows under every strategy — so main\_4's
  previously-used ratios (surface 0.549/0.767, peak 0.758/0.964,
  wire-loss 1.139/1.181, load 1.166/3.236) required no change. Figure 5.1
  was regenerated (not dropped) with the corrected main\_3 values; caption
  rewritten to name the fixed model per target/phase and state the
  selection rule explicitly.

**3. Tautology-risk synthesis conflated two different targets.** The
original text said the Phase-1 and main\_4 findings "implicate the same
target." They do not: Phase 1's near-tautological result concerns
peak-rust (current-corrosion) prediction; main\_4's near-identity finding
concerns `surface_total_rust_pct`. Also, re-checked
`main/image_features.py` directly: `img_rust_mask_pct` is computed by this
project's own fixed-threshold colour-mask code, independently of the
label. Chapter 2 states the visible-corrosion labels are *manually
assigned* (Section~1.2, modality C). The repository does **not** establish
that `img_rust_mask_pct` is computed by "the same rule" used to assign the
manual label — only that the two are closely aligned. Corrected wording
now separates the two findings (Phase-1 shortcut/tautology risk for
peak-rust vs. main\_4's directly-quantified near-label-reconstruction for
total/surface rust, Spearman 0.9996) and removes the unverified
same-rule provenance claim, using "closely aligned with the target" rather
than "the same colour-threshold rule used to construct its own label."

**4. Horizon unit error in Table 5.1.** "104 vs. 365 days" was wrong —
main\_3's horizon is 104 *weeks* (~728 days), not 104 days. Corrected to
"104 weeks ≈ 728 days versus 365 days ≈ 52 weeks." The main chapter prose
(Section~5.6) already correctly said "104-week" throughout; only the
compressed Table 5.1 parenthetical had the error. Checked the whole
chapter source and both notes files for any other "104-day" wording: none
found.

**5. Closing paragraph over-generalised "independently reproduced."**
Re-checked each of the three negative findings individually:
campaign-confounded structural inference — genuinely named early and
reinforced by later, independent requantification (main\_3's own report,
then main\_4's feature audit); proxy-RUL's non-validated status —
genuinely reinforced by two independently configured pipeline generations;
but the lack of reliable incremental image value for terminal ultimate
load is established by *one* phase's own designed three-way ablation
(main\_4's terminal-load refocus), not corroborated by a second,
independent experiment. The closing paragraph is rewritten to state this
distinction explicitly rather than describing all three as "independently
reproduced."

**6. Table 5.2 rows updated for consistency with (1).** "Visible surface
corrosion" and "Cross-regime / cross-campaign robustness" rows revised so
neither states treatment-level fragility as a project-wide, replicated
conclusion; both now state campaign-level robustness and structural
fragility as replicated, and treatment-level visible-corrosion behaviour
as phase-dependent/diverging.

**No change was required** to the Structural-Condition Prediction (Q2),
Incremental Value (Q3, aside from wording in the closing paragraph), or
Four-Class Classification (Q6) sections — targeted re-verification of
their key numbers during this pass did not surface any error.

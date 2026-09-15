# Chapter 6 — Scientific Interpretation and Research Decisions: Interpretation Plan

Internal planning document. Not part of the final report. Written before
drafting. Organised by interpretive question, per instructions. Chapters
2–5 are frozen; this plan draws on their already-verified facts (cited by
section) and on `evidence_log.md` / `chapter5_evidence_plan.md`, adding new
repository verification only where a specific interpretive claim requires
it (marked **NEW**).

For each question: empirical observations it rests on; what may safely be
inferred; what must not be inferred; the resulting research decision; and
a category label — **evidence-backed interpretation**, **methodological
lesson**, **project decision**, or **future hypothesis** — kept distinct
per instruction.

---

## Q1. Why is visible surface corrosion comparatively learnable?

- **Empirical observations:** dense, image-level supervision (791 of 792
  observations, Chapter 2 §1.2/1.7) vs. sparse structural supervision (48
  of 791, one per specimen); useful grouped-holdout accuracy across three
  independent phases with different representations (classical threshold,
  ResNet-18 embedding, interpretable multi-family features; Chapter 5
  §4.2.1); campaign-level robustness replicated across two phases (Chapter
  5 §4.2.3); two independent, target-specific label-adjacency findings
  (Phase-1 peak-rust shortcut risk, main_4 total-rust near-identity;
  Chapter 5 §4.2.2).
- **Safe inference:** visible corrosion is directly manifested in surface
  appearance and is densely, repeatedly labelled, which together plausibly
  explain why it is the project's most consistently learnable image-based
  quantity — an inference from supervision structure and cross-phase
  replication, not a claim about which specific visual cues a model uses.
- **Must not infer:** that every visible-corrosion benchmark reported is
  equally trustworthy (the total-rust/peak-rust distinction, Chapter 5
  §4.2.2, blocks this); that treatment-level robustness is settled (it is
  phase-dependent, Chapter 5 §4.2.3/§4.5); that high accuracy alone
  validates a genuinely learned visual concept independent of label
  construction.
- **Resulting research decision:** none new here — this section interprets
  a pattern already established across Phases 1–4a; the decision it
  motivates (moving to interpretable, non-tautological descriptors) is
  Phase 3's own, already reported in Chapter 4 §3.3's closing paragraph.
- **Category:** evidence-backed interpretation (the "why," not new
  evidence), with one embedded methodological lesson (accuracy is not
  sufficient if the feature reconstructs the label).

## Q2. Why is hidden structural condition much harder to recover?

- **Empirical observations:** 48 structural rows total, one terminal
  measurement per specimen, no repeated or intermediate structural
  measurement for any specimen (Chapter 2 §1.4); campaign identity
  perfectly co-varies with mesh/NaCl/duration (Chapter 2 §1.6); structural
  models collapse under both stricter regimes in two independent phases
  (Chapter 5 §4.3); mesh-stratified within-group R² is negative for every
  feature-set configuration tested (Chapter 4 §3.7.2); main_3's structural
  models are mixed-input, main_4's final robustness-weighted selections are
  metadata-only (Chapter 5 §4.3).
- **Safe inference:** the combination of sparse, single-timepoint
  supervision and near-perfect design confounding is sufficient on its own
  to explain weak and unstable structural signal, independent of any
  claim about image quality or model capability — supervision scarcity is
  a data-availability constraint, not a modelling failure.
- **Must not infer:** "surface corrosion does not affect structural
  capacity" — this is explicitly the wrong conclusion (physical claim not
  tested). The correct, narrower conclusion: this dataset and experimental
  design do not isolate a robust incremental image-based relationship to
  hidden structural capacity. The distinction between a *physical*
  relationship (which the data cannot rule out) and *predictive
  identifiability from this dataset* (which is what was actually tested)
  must be explicit and is one of the chapter's required distinctions.
- **Resulting research decision:** motivated the shift from hidden-damage
  estimation to the terminal-load refocus (Q5) and the audit-and-
  robustness-weighting refinement in Phase 4a (already described in
  Chapter 4 §3.6, not repeated here).
- **Category:** evidence-backed interpretation, with the
  physical-vs-identifiability distinction flagged as a methodological
  lesson.

## Q3. What does metadata dominance mean scientifically?

- **Empirical observations:** metadata-only Ridge is the strongest pooled
  predictor for terminal ultimate load (Chapter 4 §3.7.1); the five
  strongest univariate correlates of ultimate load are metadata/temporal
  variables tied at exactly $|r|=0.827$, a numerical signature of
  campaign alignment (Chapter 4 §3.6); mesh-stratified and LOCO evaluation
  both show the pooled metadata-driven relationship does not hold up
  within a design-homogeneous subgroup or under campaign extrapolation
  (Chapter 4 §3.7.2–3.7.4, Chapter 5 §4.3).
- **Safe inference:** metadata dominance is genuinely double-edged and
  both readings are simultaneously true, not competing: (1) mesh
  configuration, chloride exposure, ageing duration, and treatment are
  real design/exposure variables with a plausible physical relationship to
  structural response, so metadata carrying predictive information is not
  inherently suspicious; and (2) because these same variables are almost
  perfectly aligned with campaign identity in this specific sample
  (Chapter 2 §1.6), metadata's pooled predictive strength cannot be
  distinguished, from the pooled evidence alone, from a shortcut that
  merely recovers which campaign a specimen belongs to.
- **Must not infer:** that metadata is "invalid" or "not real signal" —
  this must be explicitly avoided per instruction. Also must not infer
  that pooled predictive success demonstrates transferable structural
  inference: the within-mesh and LOCO evidence specifically shows pooled
  performance does not transfer to a design-homogeneous subgroup or a new
  campaign.
- **Resulting research decision:** motivated designing the explicit
  image-only/metadata-only/combined ablation (Phase 4b) and the
  mesh-stratified and campaign-holdout robustness checks as necessary
  companions to any pooled result, rather than treating a pooled metadata
  benchmark as sufficient on its own (Chapter 4 §3.7, already reported).
- **Category:** evidence-backed interpretation; the "pooled performance
  can be useful yet insufficient" point is also a methodological lesson
  (feeds Q9/§6.9).

## Q4. Why did stricter validation change the interpretation of early results?

- **Empirical observations:** Phase 1's headline current-corrosion result
  (MAE 2.38, $R^2=0.900$) used only a grouped holdout with no stricter
  regime tested, and its own model-selection practice used the holdout
  metric for both selection and reporting (Chapter 4 §3.2); Phase 3 was
  "the first phase in the project" to test all three regimes systematically
  (Chapter 4 §3.4); once tested, visible-corrosion and structural targets
  both showed regime-dependent collapse under at least one stricter regime
  (Chapter 5 §4.2.3/§4.3); main_4's own review explicitly reframed
  grouped-holdout-only evaluation as "an unreliable guide to structural
  robustness" (Chapter 4 §3.6, already quoted there).
- **Safe inference:** a grouped holdout alone answers a narrower question
  (generalisation to unseen specimens within the observed design mixture)
  than a project needs answered to support claims about transfer to new
  treatments or campaigns; the project's own successive phases treated
  this as a reason to add, not replace, evaluation regimes.
- **Must not infer:** that grouped-holdout results are worthless — they
  remain the correct regime for the question they answer (Chapter 3 §2.3.1)
  — or that every early-phase result was invalidated; some (e.g.
  visible-corrosion campaign-level robustness) were reinforced, not
  overturned, by stricter testing.
- **Resulting research decision:** adoption of the three-regime
  methodology as a standing principle (Chapter 3 §2.9, already frozen) and
  the robustness-weighted model-selection procedure in Phase 4a (Chapter 4
  §3.6).
- **Category:** methodological lesson, grounded in evidence-backed
  interpretation of the Phase 1 → Phase 3 → Phase 4a progression.

## Q5. Why was the terminal ultimate-load refocus justified?

- **Empirical observations:** hidden-damage estimation requires a
  model-derived intermediate state at every non-terminal week, fit
  in-sample on 48 rows (Chapter 4 §3.4.2); its own degradation-curve
  extrapolation and proxy-RUL derivation compound that uncertainty further
  (Chapter 4 §3.5); ultimate load is the one structural quantity directly
  measured at a single well-defined terminal timepoint for every specimen
  (Chapter 2 §1.1/§1.4); the refocused study evaluates a specific,
  falsifiable incremental-value question under a designed three-way
  ablation plus subgroup and campaign-holdout checks (Chapter 4 §3.7).
- **Safe inference:** narrowing the target from a multi-step, model-derived
  chain to the one directly measured endpoint available for every specimen
  is a way of asking a smaller but more answerable question, and framing
  it as an explicit incremental-value test (rather than a standalone
  accuracy claim) is a stronger experimental design than the chain it
  replaced, because every step of the chain it replaced introduces
  additional, unverifiable modelling assumptions (Chapter 3 §2.8's
  four-step derivation).
- **Must not infer:** that the refocus was undertaken because hidden-damage
  estimation "failed" in some absolute sense, or that it was a retreat from
  a more ambitious goal — the chapter must frame this as a scientifically
  motivated narrowing of claim scope, not an admission of defeat.
- **Resulting research decision:** Phase 4b itself (already reported,
  Chapter 4 §3.7) — this section interprets why that decision was
  sound, it does not re-report the decision's results.
- **Category:** evidence-backed interpretation / project decision
  (the decision is Phase 4b's own; this section supplies the
  methodological justification for why it was the right one to make).

## Q6. What does the proxy-RUL work actually contribute despite not yielding validated RUL?

- **Empirical observations:** the four-step derivation (Chapter 3 §2.8) was
  executed end-to-end in two independently configured generations (Chapter
  5 §4.6); the second generation's own saved output shows zero
  forward-looking crossings at any tested threshold (Chapter 5 §4.6, newly
  verified in the prior session); `main_4/NEXT_STEPS_PLAN.md` explicitly
  recommends exporting genuine out-of-fold structural predictions "as the
  basis for any degradation modelling experiment" and separately flags
  that current degradation/proxy outputs "were generated from in-sample
  hidden-damage refits, not out-of-fold structural predictions" (already
  logged, Chapter 4 QC-pass evidence-log row) — i.e., the project's own
  documentation names a **downstream-optimism risk**: an in-sample
  structural estimate feeding a degradation curve can look more confident
  than a genuinely held-out one would.
- **Safe inference:** the pipeline's methodological value lies in what it
  forced the project to make explicit — a formal separation between
  observed and model-estimated condition series (Table 1.3), a threshold-
  status taxonomy that replaced an ambiguous single "weeks remaining"
  number (Chapter 4 §3.6), and a concrete demonstration (via the
  all-zero-crossings result) of how conservative and how baseline-
  dominated the estimated trajectories actually are once examined
  critically. This is diagnostic and methodological value, not prognostic
  value.
- **Must not infer:** that either generation constitutes a validated
  remaining-life estimate, or that the second generation's more
  conservative output makes it "more correct" in an absolute sense — it is
  differently configured (Chapter 5 §4.6), not a validated improvement.
  True RUL validation is not established and is not claimed.
- **Resulting research decision:** none new to report here — this
  interprets already-completed work; the natural forward-looking
  implication (what data would be needed) is a future hypothesis, not a
  decision taken.
- **Category:** evidence-backed interpretation, ending in one explicit
  **future hypothesis**: genuine forward-looking RUL validation would
  require either a recorded failure-event time or repeated (not
  single-terminal) structural measurements per specimen — restating
  Chapter 3 §2.8's already-established requirement, applied here as the
  concrete data gap this chapter's interpretation exposes.

## Q7. Why is the current four-class classification branch a reasonable next direction?

- **Empirical observations:** the branch targets a directly observable
  quantity (image → severity category) rather than a model-derived or
  extrapolated one (Chapter 3 §2.4, strategy E); the current four-level
  schema is explicit and distinct from the historical five-level one
  (Chapter 2 §1.5, Table 1.6); class imbalance was characterised before
  any training was attempted (658/99/20/14, Chapter 4 §3.8); the
  specimen-level grouped split and leakage-safety runtime check were
  implemented and verified (Chapter 4 §3.8, Chapter 5 §4.7); augmentation
  recipes were chosen and rejected on stated physical-plausibility grounds
  (Chapter 4 §3.8).
- **Safe inference:** the branch's design incorporates, from the outset,
  every methodological lesson the earlier regression work had to learn the
  hard way — specimen grouping, leakage control, explicit schema
  versioning, and imbalance-awareness before training — which is a
  reasonable basis for treating it as a scientifically well-prepared next
  direction, independent of what a future trained classifier will show.
- **Must not infer:** that a classifier has been trained, compared, or
  evaluated — no accuracy, macro-F1, or confusion-matrix result exists
  (Chapter 4 §3.8, Chapter 5 §4.7) — and no ResNet-50 or Vision Transformer
  experiment may be described as completed.
- **Resulting research decision:** none new; this section explains why the
  already-completed data-preparation decisions (Phase 5, Chapter 4 §3.8)
  constitute reasonable groundwork, and states as a **future hypothesis**
  /recommendation the concrete evaluation practice the next phase should
  follow (macro-F1/recall over accuracy, per-class confusion matrix,
  untouched test set) — already specified in Chapter 3 §2.7 as the
  planned evaluation, not invented here.
- **Category:** evidence-backed interpretation + future hypothesis
  (recommended evaluation practice for the not-yet-run training phase).

## Q8. What general methodological lessons emerge from the whole project?

Synthesised from Q1–Q7, not independently sourced. Each lesson below cites
which section it is drawn from, to avoid re-deriving Chapter 5's numbers:

1. Evaluation design can matter more than model complexity (Q4; Chapter 4
   §3.2's model-family comparisons vs. §3.4's regime comparisons).
2. Grouped holdout is necessary but not sufficient (Q4; Chapter 3 §2.9).
3. Accuracy without target provenance can be misleading (Q1; Chapter 5
   §4.2.2).
4. Metadata baselines are essential before any image-value claim (Q3;
   Chapter 4 §3.7.1).
5. Sparse downstream labels bound what any model, however capable, can
   establish (Q2; Chapter 2 §1.4).
6. Negative results should drive scope refinement, not be hidden (Q5, Q6;
   Chapter 4 §3.7.4's residual-correction attempt, explicitly logged as
   "worsened" rather than omitted).
7. Directly measured targets should be preferred over long chains of
   model-derived proxies where a directly measured alternative exists (Q5;
   Chapter 3 §2.9's own stated principle).

**Category:** methodological lesson (all seven); presented as concise
prose or one compact list, not a numeric scorecard, per instruction to
avoid "a long numbered manifesto."

---

## Interpretive discipline checklist (applied during drafting)

- No unqualified causal wording ("X caused Y") anywhere in Chapter 6;
  prefer "is consistent with," "suggests," "supports the interpretation
  that," "may reflect," "cannot distinguish between."
- No invented physical mechanism beyond what Chapter 2's predecessor-thesis
  attribution or the project's own documentation establishes.
- Physical-relationship-vs-predictive-identifiability distinction (Q2) is
  explicit, not implicit.
- Metadata is never called "bad" or "invalid" (Q3).
- True RUL remains explicitly unsupported (Q6).
- Four-class branch remains explicitly preparation-only (Q7).
- Terminal-load refocus is framed as scientific narrowing, not failure
  (Q5).
- No Chapter 5 metric is re-reported in Chapter 6 unless it is the direct
  subject of an interpretive claim, and then only briefly, by reference
  (e.g. "$\rho\approx0.83$ campaign alignment" cited once in Q3, not the
  full feature list).

## Planned chapter structure and visual budget

6.1 From Visible Corrosion to Structural Condition: An Evidence Hierarchy
    — includes the chapter's one figure: a conceptual schematic (new TikZ
    diagram, explicitly labelled as a report schematic, not a measured
    result) showing observed surface corrosion → image descriptors/
    embeddings → hidden structural condition → degradation trajectories →
    proxy-RUL, with decreasing supervision density and increasing model
    dependence annotated.
6.2 Why Visible Corrosion Was the Strongest Image-Based Task (Q1)
6.3 Why Structural Inference Was Harder (Q2)
6.4 Metadata Dominance: Signal or Shortcut? (Q3)
6.5 Why the Research Question Was Refocused (Q5)
6.6 Scientific Value of the Negative Results
6.7 What the Proxy-RUL Work Contributes (Q6)
6.8 Interpretation of the Four-Class Classification Direction (Q7)
6.9 Methodological Lessons (Q8, Q4 folded in) — prose/short list, no table,
    since the chapter's one-visual budget is used by the §6.1 schematic.

Q4 (stricter validation changing interpretation) is folded into §6.9 and
referenced briefly in §6.3/§6.5 rather than given its own section, since it
is a lesson that recurs across §6.2–6.5 rather than a standalone finding.

Target length: 4–5 pages, hard ceiling 6. No new quantitative figures; one
conceptual schematic only. No Chapter 5 table is reproduced.

---

## QC correction pass (post-approval, targeted interpretive review)

Eight micro-corrections were applied after substantive approval, all
softening over-strong wording rather than changing which evidence is
cited. None required new repository verification; all are wording fixes
to claims already grounded in already-verified Chapter 4/5 facts.

1. **Evidence-hierarchy semantics (§6.1/Figure 6.1).** The original figure
   and prose implied a literal universal computational pipeline (each
   stage generated from the stage above it). This is false for the
   structural-estimate stage specifically: main_3's structural models are
   mixed-input (metadata + manual labels + image features) and main_4's
   final selections are metadata-only (Section~Q2 above), so structural
   estimates do not depend on the image-representation stage alone, or
   even necessarily at all. Figure regenerated as a ladder connected by
   dashed (non-directional) lines rather than solid arrows, with an
   explicit side-bracket labelled "increasing inferential distance" and an
   in-figure footnote stating the ladder position is not a computational
   dependency; prose revised to state feature inputs are phase-dependent
   and to give the structural-tier example explicitly.
2. **Treatment-level LOTO divergence (§6.2).** Softened "consistent with
   treatment-group size and composition ... being the limiting factor" (a
   near-causal mechanism claim) to "may partly reflect changes in
   treatment-group definition, size, or composition ... the available
   evidence establishes the disagreement itself, not its mechanism," and
   added an explicit statement that the visual task is not thereby ruled
   out as a contributor.
3. **Structural-supervision claim (§6.3).** "Is, on its own, sufficient to
   explain" softened to "is a major limitation consistent with the
   observed instability." "Only two independent design points" (which
   would wrongly imply the entire experiment has only two independent
   conditions) corrected to "only two campaign-level combinations of the
   principal design variables (mesh configuration, chloride level, and
   terminal duration)," with an explicit note that treatment variation
   still exists within each campaign.
4. **Metadata counterfactual (§6.4).** "Should survive being tested ...
   and it does not" (a deterministic claim that a genuine effect must
   survive stratification) replaced with "weakens the evidence that the
   pooled metadata relationship is transferable ... does not disprove a
   genuine physical metadata effect, only the claim that the pooled result
   demonstrates one."
5. **"Not falsifiable" (§6.5).** The hidden-state → degradation → proxy-RUL
   question was mischaracterised as "not falsifiable." Corrected to "not
   incoherent, but substantially harder to validate and diagnose, because
   disagreement at the final stage cannot be cleanly attributed to one
   component without independent intermediate ground truth" — matching the
   reviewer's suggested wording exactly. The terminal-load question
   remains described as bounded and directly testable.
6. **"Rules out" (§6.6).** Generalised negative-result language narrowed
   to "provides evidence against an otherwise plausible claim in this
   dataset, under the tested pooled setting" — scoped to the tested
   dataset/setting rather than a general claim.
7. **Proxy-RUL crossing terminology (§6.6/§6.7).** "All-zero-crossings"
   replaced throughout with "zero future-crossings," explicitly
   distinguishing baseline-crossed and during-observation-crossed cases
   from the (zero) future-projected crossings. "Exposes how much ...
   signal is attributable to baseline estimates" (an unquantified
   decomposition claim) softened to "is consistent with threshold status
   being strongly influenced by already-elevated baseline structural
   estimates, although that decomposition was not itself quantified," with
   the repository's own "unresolved validation check" caveat on baseline
   plausibility restated explicitly. The downstream-optimism /
   out-of-fold-vs-in-sample statement from `NEXT_STEPS_PLAN.md` is
   retained verbatim in substance, attributed to the project's own
   documentation rather than to the pipeline's outputs in general.
8. **Schema wording (§6.8).** "The historical five-level scheme it
   supersedes" (implies a deliberate supersession process not established)
   corrected to "the historical five-level scheme used in the earlier
   dataset build."

All eight corrections re-checked by grep against the compiled chapter
source: no instance of "should survive," "not falsifiable," "rules out,"
"all-zero-crossings," "supersedes," "two independent design points," or
"sufficient to explain" remains.

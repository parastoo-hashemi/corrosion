# Autonomous overnight task: rebuild the ferrocement-corrosion technical report as a first-class scientific document, an IEEE-style article, and thesis material

## 0. Operating rules — read this section first

You are running **unattended overnight**. The user will not be available to
answer questions, approve choices, or unblock you. This changes how you must
work:

- **Never stop and wait for input.** If you would normally ask a clarifying
  question, instead: pick the most conservative, most defensible option;
  write down what you chose and why in `DECISIONS.md` (create it at the
  repo root of your working branch); and continue.
- **Never invent facts, numbers, or results.** Every number, figure, and
  claim in the report must trace back to something that actually exists in
  this repository: a saved CSV/JSON/PNG output, a script you ran yourself
  and can show the output of, or the predecessor sources already cited in
  `activity_report/references/references.bib`. If you cannot verify a
  number, do not use it — state the gap in `DECISIONS.md` instead of
  guessing.
- **Do not fabricate citations.** Only cite works you can actually verify
  the metadata of (via any web/literature access you have) or that are
  already in this repo's bibliography. If you add new references, record
  where each one came from.
- **Work on an isolated git branch**, e.g. `report-rebuild-codex`, created
  from `master` before you touch anything. Commit after every phase below
  with a clear message. Do **not** force-push, do not delete or rewrite
  history, do not touch `master`, and do not push to any remote unless a
  remote is already configured and the user has clearly asked for that
  elsewhere (they have not, so: do not push).
- **Do not run long/expensive retraining.** You may re-run small, fast
  scripts (figure/table generation, aggregation, verification checks) that
  read already-saved outputs. Do not kick off multi-hour model training.
  If a figure/number depends on a saved artifact, use the saved artifact;
  only regenerate it if the regeneration is cheap (a script that runs in a
  couple of minutes against saved CSV/parquet files) and you can verify the
  regenerated number matches what is already reported.
- **Checkpoint constantly.** Commit after each phase (below) so that if you
  run out of time or crash, partial progress survives. At the very end,
  write a single `MORNING_SUMMARY.md` at the repo root describing exactly
  what was produced, what decisions were made, what remains uncertain, and
  how to compile everything.
- **Do not touch or overwrite** the existing frozen report at
  `activity_report/activity_report.tex` and its `chapters/`/`frontmatter/`
  directories. That document has already been through many rounds of
  scientific QC and is a known-good artifact. Build the new material in a
  **new directory**, e.g. `report_v2/`, so both versions exist side by side
  and nothing already-approved can be silently lost. You may read the old
  report as a source of verified facts and wording, but the new report is a
  fresh composition aimed at a higher bar (see Phase 2).

## 1. What this project is (ground truth — do not contradict this)

This is an MSc-level technical activity on inferring the condition of
ferrocement (thin, steel-mesh-reinforced cementitious composite) specimens
from repeated corrosion photography, plus terminal structural testing. It
builds on a **predecessor experimental dataset**, external to this activity,
already cited in `activity_report/references/references.bib` as
`hossain_thesis` and `artiste2025`:

- 48 physical specimens, tested across **two experimental campaigns**, in
  which steel-mesh configuration, chloride concentration, and terminal
  ageing duration co-vary almost perfectly with campaign identity (a
  confound you must respect, not ignore or explain away).
- A photographic record with dense visible-corrosion labels: 791 aligned,
  readable observations in the current audited basis (out of 792 raw
  files; one corrupted).
- Terminal structural measurements — **wire-area loss** and **ultimate
  load** — obtained **once per specimen**, destructively, at the end of its
  exposure period. There are two directly measured terminal structural
  endpoints, not one; do not describe either as "the one structural
  quantity directly measured."
- No true remaining-useful-life (RUL) supervision exists anywhere in the
  dataset: no repeated structural measurement, no observed failure/lifetime
  event.

The project's own implementation history lives in these directories, in
this chronological order — **read all of them before writing anything**:

- `main_first/` — earliest exploratory prototype (no held-out evaluation,
  no saved metrics).
- `main/`, `main_2/` — classical ML baseline and deep-embedding phases.
- `main_3/` — interpretable multi-family feature phase (structural
  feasibility, first campaign/treatment robustness testing).
- `main_4/` — robustness-quantification and refocused terminal-ultimate-load
  phase (the project's most mature modelling generation; has its own
  `SCIENTIFIC_REPORT.md`, `BENCHMARK_DIAGNOSTICS.md`,
  `FEATURE_DIAGNOSTICS.md`, `NEXT_STEPS_PLAN.md`, etc. — read these, they
  contain the project's own internal scientific narrative).
- `main_4_old/` — archival snapshot, not otherwise load-bearing.
- `augmentation/` — later, separate branch: leakage-safe data prep and
  augmentation for a **four-class visible-corrosion severity classifier**
  that has been prepared but **never trained**. Do not claim a
  classification result exists.
- `emiling/` — additional saved output artifacts (figures, metrics) from
  `main_3`/`main_4`/`main_4_v2` re-runs; useful as a source of already-computed
  figures/tables.
- `Data/` — underlying data tables/workbooks and split manifests.
- `activity_report/` — the existing, already-QC'd 70-page report (10
  chapters + abstract + executive summary). Its `notes/evidence_log.md` and
  `notes/*_plan.md` files are an **internal evidence audit trail**: read
  them as a map of which claim is backed by which file/line, but do not
  expose that audit machinery in the new report's reader-facing prose —
  the new report should read as a polished scientific document, not an
  internal QA log.

Known, already-verified engineering issues you must acknowledge honestly if
your own re-verification confirms them (do not re-litigate the root cause,
just confirm current status and report it factually):

- A YAML boolean-parsing bug: `main_4/configs/specimen_mapping.yaml` has an
  unquoted `treatment_coarse: NO`, parsed by PyYAML as boolean `False`
  rather than the string `"NO"` for the ten no-treatment specimens.
- A "1"/"first" → "main_first" string-substitution corruption pattern,
  live in `main`, `main_2`, `main_3`, `main_4`, confirmed absent from
  `augmentation`. Confirmed not to affect any already-reported result,
  because the affected saved artifacts predate the corruption timestamps —
  verify this claim yourself against file modification times before
  repeating it.

Established, already-defensible scientific findings (your new report should
reproduce and better-argue these, not contradict them, unless your own
re-verification against the saved data turns up a genuine error — if so,
document the discrepancy in `DECISIONS.md` and flag it prominently rather
than silently "fixing" the number):

1. Visible surface corrosion is the strongest, most consistently learnable
   image-based quantity, across three independent representations
   (handcrafted threshold, frozen deep embedding, interpretable
   multi-family features) — with a real label-adjacency/shortcut risk in
   specific benchmarks (a rust-mask feature at Spearman ρ≈0.9996 with its
   own label in one phase).
2. Hidden structural-condition inference is substantially weaker and less
   transferable, consistent with — not necessarily *caused solely by* — its
   sparse (48 rows, one per specimen), terminal, campaign-confounded
   supervision. The project's own most carefully selected, robustness-
   weighted structural models use metadata alone, not image features.
3. Under pooled evaluation, image-derived features do not provide reliable
   incremental predictive value over specimen/exposure metadata for
   terminal ultimate load; a narrow, non-overturning exception exists once
   corrosion has visibly onset. Within a single mesh family or under
   leave-one-campaign-out, this relationship collapses further.
4. Evaluation regime materially changes what can be claimed.
   Leave-one-campaign-out (LOCO) is best understood as a severe
   **extrapolation stress test**, not ordinary generalisation, because
   campaign identity is perfectly confounded with mesh/chloride/duration.
   Leave-one-treatment-out (LOTO) results for visible corrosion are
   phase-dependent, not a settled project-wide property.
5. The degradation-curve / proxy-RUL pipeline is methodological and
   diagnostic, not a validated prognostic method: its structural inputs are
   model-derived, not measured; and its refined configuration shows **zero
   future** threshold crossings (not zero crossings overall — many cases
   are already crossed at baseline or during observation).
6. The four-class classification branch has complete, leakage-safe,
   augmented, specimen-disjoint data preparation but **zero trained
   models**. Do not report or imply any accuracy/F1/confusion-matrix result
   for it.

You are free to dig deeper into the saved outputs in `main_4/outputs/`,
`emiling/`, and `Data/` to find additional genuine, verifiable evidence that
strengthens the report — the above is the minimum you must not contradict,
not a ceiling on what you may discover and use.

## 2. What "best in the AI world" means here — do the research

Before drafting anything, spend real effort researching what separates a
genuinely first-class, defensible scientific ML report/paper from a
mediocre one. If you have web/literature search available, use it — look
at guidance and conventions from sources such as:

- Widely used research-paper-writing guides (e.g. "How to Write a Great
  Research Paper" — Simon Peyton Jones; "Ten Simple Rules" series in PLOS
  Computational Biology; MLCommons/NeurIPS "reproducibility checklist"
  guidance; ACM/IEEE author guidelines for empirical papers).
- How strong, well-known empirical ML papers structure their claims:
  explicit research questions, explicit threats-to-validity / limitations
  sections, ablations that isolate one variable at a time, evaluation
  protocols chosen to prevent leakage, and a clear separation between
  "what we observed" and "what we infer."
- IEEE conference/journal paper structure and formatting conventions
  (title/abstract/keywords, numbered sections, IEEE reference style,
  figure/table captioning conventions, notation consistency).
- Standard MSc thesis structure and expectations (front matter, literature
  review/related work, methodology, results, discussion, limitations,
  conclusion and future work, full bibliography, appendices for
  supplementary detail).

If you do **not** have live web access, fall back on your own trained
knowledge of these conventions — do not skip this step, just do it from
what you already know rather than stopping to ask for browsing access.
Write a short `RESEARCH_NOTES.md` (in `report_v2/`) summarising the concrete
standards you decided to hold this report to (e.g., "every reported metric
must state its evaluation regime and n"; "every figure caption must be
readable without the surrounding prose"; "limitations must be a first-class
section, not a footnote"). Use this as your own rubric in Phase 5.

## 3. Deliverables — build all of these

Create a new directory `report_v2/` (sibling to `activity_report/`) with:

```
report_v2/
  thesis/            <- full thesis-style LaTeX report, v1
  thesis/v2/         <- revised thesis-style LaTeX report, v2 (post-critique)
  article/           <- condensed IEEE-format article LaTeX (conference or
                        journal double-column style), derived from the same
                        evidence, v1 and v2
  figures/           <- every figure used, regenerated or copied from a
                        verifiable saved source, with a script or provenance
                        note for each
  references/        <- shared .bib file(s)
  critique/           <- the self-critique document(s) from Phase 5
  DECISIONS.md
  RESEARCH_NOTES.md
  MORNING_SUMMARY.md
```

### 3a. Thesis-style report (v1)

Full LaTeX document (own `.tex` master file, modular chapters like the
existing `activity_report/` for maintainability). Required content:

- Title page, abstract, (optionally) executive summary.
- Introduction: motivation, problem statement, research questions,
  contributions, scope, and an honest statement of what this activity does
  and does not claim.
- **Related work / background**: situate this work against the predecessor
  thesis/paper and, if you have literature access, against relevant
  published work on corrosion assessment via imaging, structural health
  monitoring with ML, and leakage-safe evaluation for small structural
  datasets. Cite properly.
- Dataset and experimental context (campaigns, specimens, modalities,
  supervision asymmetry, confounding structure) — with at least one clear
  schematic figure.
- Methodology: evaluation regimes (grouped holdout, LOTO, LOCO) and why
  each matters, representation strategies, model families, the
  observed/model-derived/derived-screening quantity distinction, the
  proxy-RUL derivation chain and why it is not true RUL.
- Results: organized by scientific question, not by implementation phase,
  with real tables and real figures (regenerated or provenance-checked) for
  every quantitative claim.
- Discussion / interpretation: why structural inference is harder than
  visible-corrosion estimation, what the metadata-dominance finding means
  and does not mean, why the terminal-ultimate-load refocus was the right
  call, the scientific value of the negative results.
- Limitations: a full, explicit, well-organized limitations chapter/section
  — dataset/design, labels/targets, generalisation, structural modelling,
  proxy-RUL, classification branch, software/reproducibility.
- Current status, remaining work, and concrete next steps.
- Conclusion.
- Full bibliography (BibTeX), consistently cited throughout with `\citep`
  or IEEE numeric style as appropriate to the chosen template.
- Appendices as needed for supplementary tables/figures/implementation
  detail that would clutter the main narrative.

Writing-quality bar: every figure/table caption must stand alone; every
chapter must open with 1-2 sentences of orientation and close with a
transition; hedging language must be precise and non-repetitive; avoid
internal-project jargon and implementation names (`main_3`, `main_4`, file
paths) in the main narrative — push that detail into footnotes, a
dedicated reproducibility chapter, or appendices, the way a real thesis
would.

### 3b. IEEE-style article

A condensed, single-contribution-focused article (pick the strongest,
most defensible storyline — most likely: the supervision-asymmetry /
evaluation-regime story, i.e. what evaluation regime and confounding
structure imply for structural-condition inference from images in small
specimen datasets) in IEEE double-column conference or journal format.
This is not a copy-paste shrink of the thesis — write it as its own
paper with its own abstract, introduction with a clear stated
contribution, focused related work, one coherent experimental narrative,
and a real "Conclusion and Future Work" section. Use a standard IEEEtran
class if available in the LaTeX environment; if not installable, use the
closest achievable two-column IEEE-like layout and note the substitution in
`DECISIONS.md`.

### 3c. Figures, tables, diagrams

- Reuse verified figures from `activity_report/figures/`, `main_4/`,
  `main_3/`, and `emiling/` where they are already correct and well-made.
- Regenerate or newly create any figure/diagram that is missing, unclear,
  or was flagged as weak in the existing report (check
  `activity_report/notes/evidence_log.md` and `main_4/FIGURE_REVIEW.md` for
  prior figure critiques).
- Add at least: a dataset/supervision-asymmetry schematic, an
  evaluation-regime schematic (grouped holdout vs LOTO vs LOCO), a
  results-robustness-synthesis figure, and a confounding-illustration
  figure (mesh/campaign/chloride co-variation). These may already exist —
  verify and reuse rather than duplicate.
- Every figure must have a documented source: either "reproduced from
  `<exact file path>`" or "generated by `<script path>` from
  `<exact saved data file>`, re-run on `<date>`, output verified to match."

### 3d. Referencing

Use BibTeX with a consistent style (IEEE numeric for the article; author-year
or numeric — your choice, document it — for the thesis, but be consistent
within each document). Include the predecessor sources already in
`activity_report/references/references.bib`, plus any literature you cite
for related work/background. Do not leave any `\cite{}` unresolved —
compilation must show zero "undefined citation" warnings.

## 4. Verification / "tests" to run before you consider a draft done

- Recompile every LaTeX document you produce (`pdflatex` → `bibtex` →
  `pdflatex` → `pdflatex`, or `latexmk`) and confirm: zero errors, zero
  undefined references, zero undefined citations, no "Rerun to get
  cross-references right" warnings left unresolved.
- For every numeric claim in the text, grep/verify it against the saved
  source file you cite for it. Keep a running verification log (can be part
  of `DECISIONS.md` or a separate `VERIFICATION_LOG.md`) mapping claim →
  source file → verified (yes/no).
- If a figure is regenerated by a script, actually run the script and
  confirm the script exits successfully and the output matches what is
  described in the caption.
- Spell-check / grammar-pass the final text (you may use any tool available
  to you, or careful re-reading) before calling a version final.
- Confirm no scientific guardrail from Section 1 is violated anywhere in
  the new text (do a final grep pass for phrasing like "the one structural
  quantity", "proves", "causes", "validated RUL", "the classifier
  achieves").

## 5. Self-critique and v2

After v1 of both the thesis and the article are complete and compiling
cleanly, act as a skeptical, senior reviewer (a hostile-but-fair examiner or
peer reviewer) and write a genuine, substantive critique in
`report_v2/critique/`:

- Score/critique against the rubric you built in `RESEARCH_NOTES.md`
  (Phase 2).
- Be specific: cite section/page/figure numbers, not generic complaints.
- Cover at minimum: strength and clarity of the central contribution/claim;
  rigor and defensibility of every quantitative claim; quality and
  necessity of every figure/table; writing quality and structure; adequacy
  of the limitations and related-work sections; whether the narrative would
  survive a hostile peer reviewer or examiner; anything that reads as
  overclaiming or underclaiming.
- Explicitly list every change you will make in response, and why.

Then produce **v2** of both documents in `report_v2/thesis/v2/` and
`report_v2/article/v2/` (or `article/` overwritten with a clear version
note — your call, documented), implementing the critique's
recommendations. v2 must also compile cleanly and pass the same
verification pass as v1. Do not silently drop the critique items you choose
not to act on — list them in the critique document with a one-line reason
(this mirrors how the existing `activity_report/` was QC'd — see
`activity_report/notes/evidence_log.md` for the style of reasoning
expected).

## 6. When you finish (or when you run out of runway)

Write `MORNING_SUMMARY.md` at the repo root of your branch with:

1. What was produced and where (exact paths).
2. How to compile each document (exact commands).
3. Every non-obvious decision you made and why (pointer into
   `DECISIONS.md`).
4. The full self-critique summary and what changed between v1 and v2.
5. Anything you were not able to verify, finish, or are uncertain about —
   be honest, do not paper over gaps.
6. A short "read this first" section: the single most important thing the
   user should look at first when they wake up.

Commit everything to the `report-rebuild-codex` branch with a final commit
summarizing the work. Do not merge to `master`, do not push, do not delete
the existing `activity_report/`. Stop only when this is done or you
genuinely cannot make further progress — never stop to ask a question in
between.

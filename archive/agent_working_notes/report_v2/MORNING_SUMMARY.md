# Morning summary: corrosion report rebuild

Completed 16 September 2026 on branch `report-rebuild-codex`.

## Read this first

Read the revised five-page IEEE article:

[Surface Evidence and Terminal Capacity](/Users/parastoo/All_projects/Proj_corrosion/corrosion/report_v2/article/v2/article.pdf)

It presents the strongest conclusion: these saved experiments support surface
assessment more directly than transferable structural inference. The focused
terminal-load experiment does not establish reliable added value from the tested
image descriptors over metadata. Its score uses terminal images; it is not
early-warning performance. The 37-page revised thesis provides the full argument,
methods, limitations, and supplementary tables.

## What was produced

Repository root: `/Users/parastoo/All_projects/Proj_corrosion/corrosion`.

| Deliverable | Exact path relative to that root |
|---|---|
| Thesis v1, 44 pages | `report_v2/thesis/thesis.pdf` and `thesis.tex`; modular `chapters/` |
| Thesis v2, 37 pages | `report_v2/thesis/v2/thesis.pdf` and `thesis.tex`; modular `chapters/` |
| IEEE article v1, 5 pages | `report_v2/article/article.pdf` and `article.tex` |
| IEEE article v2, 5 pages | `report_v2/article/v2/article.pdf` and `article.tex` |
| Eight vector figures plus PNG copies | `report_v2/figures/`, with two provenance ledgers and plotting checks |
| Shared verified bibliography | `report_v2/references/references.bib`, `SOURCES.md`, metadata records |
| Scientific-writing research/rubric | `report_v2/RESEARCH_NOTES.md` |
| Substantive first-draft review / response | `report_v2/critique/V1_REVIEW.md`, `V2_RESPONSE.md` |
| Claim audit / final verification | `report_v2/VERIFICATION_LOG.md`, `FINAL_VERIFICATION.md`, `evidence/`, `qa/` |
| Full-precision tables / scripts | `report_v2/tables/`, `report_v2/scripts/` |
| Reproduction entry point | `report_v2/README.md` |
| Complete decision record | `DECISIONS.md`, mirrored to `report_v2/DECISIONS.md` |
| This summary | `MORNING_SUMMARY.md`, mirrored to `report_v2/MORNING_SUMMARY.md` |

## Main verified findings

- The aligned basis has 791 readable images and 48 physical specimens. Both
  wire-area loss and ultimate load are measured once per specimen at terminal
  testing. The single unreadable raw PNG was independently confirmed.
- Campaign, mesh, chloride, and terminal duration are confounded. Campaign
  exclusion is a severe extrapolation stress test; treatment exclusion remains
  phase-dependent across representations.
- Total-rust label/feature Spearman correlation is approximately 0.9996. This
  limits claims of independent predictive discovery from that benchmark.
- Pooled metadata-only Ridge gives mean terminal-test MAE 0.173 kN, fold SD
  0.046 kN. Adding HSV does not improve mean MAE in the saved comparison.
- New descriptive reanalysis of saved paired Ridge predictions: HSV improves
  19 specimens and worsens 29. Specimen-weighted mean error change is
  +0.000218646 kN; median +0.009439030 kN. Positive means worse with HSV. This
  is post-selection analysis, not a significance or equivalence result.
- The post-onset subset has a limited combined-model MAE gain but slightly worse
  rank correlation than metadata alone. All selected within-mesh feature-family
  models have negative mean test R-squared; some retain moderate ranking.
- Final robustness-selected wire-loss modelling uses metadata-only CatBoost
  (grouped MAE 0.123797 as a fraction). The lower 0.105037 diagnostic error belongs
  to a different RandomForest model; these were kept separate.
- Refined threshold output has 45 baseline crossings, two during observation,
  97 non-crossings within the horizon, and zero future crossings across 144
  specimen-threshold combinations. It does not validate remaining useful life.
- The current four-class classifier has complete specimen-disjoint preparation
  and no trained model or performance result.

The exact source mappings and aggregation methods are in the verification log.

## Self-critique and what changed

The v1 review judged the central claim defensible but challenged the mean-only
image increment, insufficiently prominent prediction time, incomplete small-fold
counts, weakly inspectable subgroup results in the article, excessive thesis
caption lists, late article figures, implicit literature positioning, and a
fragmented reproduction guide. All eight items have explicit responses in
`report_v2/critique/V2_RESPONSE.md`:

1. Added the paired fixed-Ridge analysis and specimen-level error figure.
2. Put terminal-image scoring in both abstracts and added an input-timing table,
   including the unverified pre-test availability of failure-surface cover.
3. Verified actual subgroup test sizes and labelled the classical split-count
   reconstruction honestly.
4. Added an article table of metadata, best within-mesh alternatives, and LOCO
   controls; retained complete subgroup tables in the thesis.
5. Shortened navigation entries, compacted headings, improved float placement,
   consolidated the source map, and moved the repeated threshold table to the
   appendix. The thesis is seven pages shorter with additional evidence.
6. Improved article figure placement and balanced the final columns at normal
   IEEE font size and margins.
7. Stated the focused literature gap without claiming exhaustive novelty.
8. Consolidated commands, numerical inventory, environment, source/PDF hashes,
   logs, visual review, and guardrail checks.

Final full-resolution inspection also caught a plotting defect in the newly
generated confounding figure: a fixed load-axis range hid most data points.
Corrected it with shared data-derived axes and explicit 48/24/24 point/bounds
checks. Fixed two plot-label collisions, the supervision schematic, a one-line
chapter spill, and duplicate front-matter PDF links. Shared correctness fixes
appear in both rebuilt draft versions; v1 prose/results and the original Git
checkpoint remain preserved. The critique response openly records the miss in
the first contact-sheet review.

The final rubric rates reporting as strong, with the highest scores for evidence
traceability, explicit units/sample sizes, provenance distinctions, limitations,
and calibration. It does not assert external peer-review approval. Independent
replication, nested selection estimates, genuine lifetime validation, historical
environment recovery, and causal decomposition remain unresolved by design.

## Non-obvious decisions

All choices and reasons are numbered in `DECISIONS.md`:

- 1–4: report-only scope, verified authorship, saved-file authority, and distinct
  historical data/label schemas.
- 5–8: terminal-image estimand, dependent/non-nested evaluation, extrapolation
  interpretation, and cautious post-onset interpretation.
- 9–15: preserve and disclose source defects; use real IEEEtran and a conventional
  thesis; regenerate readable figures; verify literature; use the local archive;
  preserve measurement definitions and untrained-classifier status.
- 16–18: paired aggregation, prediction-time availability, verified test sizes,
  and separate v2 source trees with clearer layout.
- 19–22: share essential figure/navigation corrections across drafts, document
  checks and their limits, and deliver the completed local reporting package.

## How to compile

The saved PDFs are ready to read. To rebuild and verify all four:

```bash
cd /Users/parastoo/All_projects/Proj_corrosion/corrosion
/opt/anaconda3/envs/env/bin/python report_v2/scripts/build_reports.py
/opt/anaconda3/envs/env/bin/python report_v2/scripts/validate_documents.py
```

Exact individual compilation commands, from the repository root:

```bash
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error report_v2/thesis/thesis.tex
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error report_v2/thesis/v2/thesis.tex
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error report_v2/article/article.tex
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error report_v2/article/v2/article.tex
```

`report_v2/README.md` contains the full audit/figure/render sequence and records
the environment. `revise_drafts.py` reconstructs v2 and would overwrite later
manual v2 edits; routine compilation does not invoke it. No training is needed.

## Verification and uncertainty

All four compile with zero errors, unresolved citations/references, overflowing
boxes, or LaTeX/package/PDF-engine warnings. The first-draft thesis retains one
benign underfull source-map line; v2 has none. All 91 final PDF pages were
rendered and reviewed, with targeted full-resolution checks. The final PDF-link
fix was rerendered and all 91 page images matched the reviewed images exactly.
The evidence package contains 43 verified claim groups, 72 source hashes,
60 split checks, eight figure provenance records, and a 181-line numerical
inventory with no unresolved decimal lint exceptions.

The exact historical executable, full training environment/compute budget,
predecessor image-generation recipe, and early availability of cover cannot be
fully recovered. The YAML `NO`/boolean defect and live `main_first` substitution
corruption remain unrepaired. Saved-output mtimes predate the affected source
timestamps, supporting chronology but not proving absence of every historical
error. There is no independent campaign confirmation, nested selection estimate,
measured structural trajectory, or true lifetime supervision. No separate
`emiling/main_4_v2` export exists in this checkout.

## Completion and preservation

All requested reporting deliverables are complete. Checkpoints retain the audit,
first drafts, critique, and revised drafts; the final commit adds this handoff
and the last verification refinements. All 23 frozen-report source hashes match
their initial values. Changes are confined to `report_v2/`, `DECISIONS.md`, and
this summary. `master` remains at
`1089b3e7f6c7f798a3bf5c6ccd07eb6c1fb3e322`. No model was trained, no original
report/data/model source was edited, and no push or merge was performed.

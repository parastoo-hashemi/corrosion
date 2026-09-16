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


# v3: figure audit and integration

## What was produced

The work is on **`report-rebuild-codex-v3`**, branched from **`c5a4f1a`**. V1/v2 sources and PDFs remain byte-for-byte unchanged.

- `report_v2/thesis/v3/thesis.pdf`: **40-page** thesis with three new Ridge diagnostics and modular sources.
- `report_v2/article/v3/article.pdf`: **five-page** IEEE article, with one new parity/residual figure and tighter repeated prose.
- `report_v2/thesis/v3/FIGURE_AUDIT.md`: complete file-by-file audit.
- `report_v2/thesis/v3/V3_CHANGE_SUMMARY.md`: changes, decisions and preservation confirmation.
- `report_v2/qa/v3/VERIFICATION.md`: numerical, scientific, compilation and visual checks; adjacent JSON files record exact PDF hashes, source checks and preservation.
- Three new vector-PDF/PNG pairs in `report_v2/figures/`: `ridge_terminal_diagnostics`, `ridge_coefficients`, `ridge_learning_curve`. The shared provenance ledger is extended without changing original entries.

## Audit headline

**30 files reviewed:** 16 historical main_3 candidates, six top-level main_4 files, and eight Ridge diagnostics. All 28 PNGs and all 13 pages in the two PDFs were viewed. **Four source files included with regeneration, consolidated into three figures; 26 rejected.** Redundancy is the most common primary rejection reason (**16 of 26**). Eighteen pure plotting functions were replayed against saved data without retraining; fifteen reproduce the candidate pixels exactly.

The two most useful additions are:

1. **Ridge terminal parity and residuals:** puts all 48 specimen-level errors behind the headline MAE in view, including substantial errors in both mesh groups. It complements the existing paired HSV comparison and does not imply calibrated uncertainty.
2. **Saved learning curve:** reveals the train/test gap and all individual fold errors as training-specimen count changes. This supports a precise small-sample diagnostic without forecasting what additional campaigns would achieve.

The coefficient plot makes the fitted metadata representation inspectable, but is explicitly a full-fit, encoding-dependent summary rather than an independent or causal feature ranking.

## Scientific clarifications

The older main_3 feature-alignment plot has weak correlations and does not contradict main_4's different, nearly reconstructive rust-area feature. V3 states this generation boundary. The learning curve shows that specimen count was varied with the representation fixed; the unresolved limitation is that subset composition and design coverage change too. The new parity's MAE of averaged predictions (0.171941 kN) is distinguished from the unchanged primary fold-mean MAE (0.172711 kN) and from the paired mean-absolute-error statistic.

## Exact recompile commands

From the repository root:

```sh
cd /Users/parastoo/All_projects/Proj_corrosion/corrosion
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error report_v2/thesis/v3/thesis.tex
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error report_v2/article/v3/article.tex
/opt/anaconda3/envs/env/bin/python report_v2/scripts/validate_documents.py
```

For the complete v3 saved-data presentation workflow, without fitting models:

```sh
/opt/anaconda3/envs/env/bin/python report_v2/scripts/audit_saved_figures.py
/opt/anaconda3/envs/env/bin/python report_v2/scripts/make_v3_figures.py
/opt/anaconda3/envs/env/bin/python report_v2/scripts/build_v3_reports.py
/opt/anaconda3/envs/env/bin/python report_v2/scripts/validate_documents.py
/opt/anaconda3/envs/env/bin/python report_v2/scripts/render_v3_review.py
```

Do not run the older general rebuild scripts as part of the preservation workflow: they regenerate v1/v2 assets. The v3 scripts restrict their writes to new artifacts and the authorized provenance extension.

## Verification and remaining limits

Both documents compile to a fixpoint with zero errors, undefined references/citations, rerun warnings, PDF-engine warnings or overfull boxes. The extended validator checks all six versions, 11 shared figures and 287 numeric-bearing lines, with zero unresolved numeric lint exceptions. All 45 new PDF page layouts and the three full-resolution figures were visually reviewed. Preservation checks verify 151 pre-existing artifacts, all 32 earlier tracked manuscript files and all 30 candidate hashes; original ledger entries and protected source/data paths remain unchanged.

Exact generators for several historical meeting panels, raw-to-montage fidelity of the rejected image gallery, and exact edit histories of the older PDF drafts could not be established. Three plot replays differ in pixels, as individually recorded; no exact reproduction is claimed for them. Historical model training was not repeated, and existing source/configuration defects were left untouched. There is no new independent validation, causal identification, calibrated prediction interval or RUL performance claim.

No push, merge, force-push or training occurred. The initially untracked user audit prompt is left outside the commits.

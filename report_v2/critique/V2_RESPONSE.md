# Response to first-draft review

2026-09-16. This is a documented self-review and revision, not independent peer
review. Locations below refer to the final 37-page thesis and 5-page article.
Thesis page numbers are printed Arabic numbers; article pages are PDF pages.

## Disposition of every requested change

| Item | Implemented response | Final location |
|---|---|---|
| C1: Mean-only incremental comparison | Paired saved Ridge predictions with matching specimen/split keys; average two errors per specimen. Report 19 improvements, 29 worsenings, mean +0.0002 kN, median +0.0094 kN. Separate specimen weighting from fold weighting and retain the post-selection caveat. | Thesis §6.2.1, pp.15–16, Fig.6.2; article §IV-C, p.3, Fig.2 p.4; `evidence/paired_diagnostics.json`. |
| C2: Prediction time and input availability | Both abstracts state terminal-image scoring. Add a timing table and the specific uncertainty about failure-surface cover. | Thesis abstract, Table 4.1 p.7, §9.4 p.23; article abstract and §V-B p.5. |
| C3: Small test folds | Verify four/five within-mesh and eight/nine post-onset test specimens. Reconstruct the classical 159-image/ten-specimen holdout and label the reconstruction. | Thesis §4.4 p.9 and Table 5.1 p.11; article §III-C p.2. |
| C4: Inspectable negative result | Add metadata and lowest-MAE selected within-mesh controls, plus the selected metadata LOCO row. Retain all seven families per mesh in the thesis. | Article Table II p.4; thesis Table A.3 p.28. |
| C5: Thesis navigation/layout | Short list captions, compact chapter headings, revised float placement and sizes, one-page source map, concise transition, and threshold table moved to the appendix. Retain standalone captions and all results. | Contents/lists pp.iii–vi; Table A.1 p.26; Fig.7.1 p.19 and Table A.4 p.28. Thesis reduced from 44 to 37 pages. |
| C6: Article flow | Place the design figure earlier, add paired errors and controls, and automatically balance the final columns without shrinking IEEE text or margins. | Fig.1 p.3, Fig.2/Table II p.4, discussion/conclusion/references p.5. |
| C7: Literature positioning | State the target-specific metadata-controlled capacity question directly; explicitly avoid an exhaustive novelty claim. | Thesis §2.4 p.4; article end of §II p.1. |
| C8: Reproduction and final verification | Add README, exact commands, environment record, full final LaTeX logs, numeric inventory, PDF/source/figure hashes, rendering script, manual sign-off, and morning summary. | Package root, `scripts/`, `evidence/`, and `qa/`; thesis Appendix A. |

All C1–C8 reporting changes are implemented. The original critique proposed
retaining both the threshold table and figure in the main chapter. Both remain,
but the table is now in the appendix to remove visual repetition from the main
argument. This is a placement change, not omission of an unfavourable result.

## Additional defects caught during final inspection

The first contact-sheet review was insufficient to detect a serious plotting
error: the newly generated confounding plot had a hard-coded vertical range of
0.1–1.7 kN, while the saved terminal loads span 1.60–2.87 kN. That hid most points
even though the correlations were correctly computed from all specimens.
Full-resolution inspection exposed it. The figure now uses shared, data-derived
axis limits, displays all 48/24/24 points, and asserts both plotted counts and
bounds. Results are in `figures/FIGURE_DATA_CHECKS.json`. This correction is
required for scientific accuracy; compilation and numeric lint did not catch it.

Also corrected the supervision arrows/box text, separated the paired annotation
from the largest positive point, moved the residual histogram's scale into its
axis label, and removed a one-line chapter spill. A misplaced column-balancing
command produced a warning during intermediate builds; automatic final-page
balancing replaced it and the final logs have no warnings.

A subsequent full-log audit caught duplicate PDF page anchors on the unnumbered
thesis title page and abstract. Disable the title-page anchor in both thesis
masters, preserving the abstract's link. Extend the build/validation checks to
reject PDF-engine warnings as well as LaTeX/package warnings. This does not
change the visible pages or scientific content. Saved text logs normalize trailing
whitespace only.

The shared figure corrections appear in both rebuilt v1 and v2 PDFs. V1 prose,
structure, and scientific numbers remain unchanged. The original committed v1
and the initial critique remain in Git, so the review history is inspectable.

## Final rubric reassessment

Scale: 0 missing, 1 weak, 2 adequate, 3 strong, 4 exemplary. Scores evaluate
reporting quality, not validation of a deployable structural model.

| Criterion | Thesis | Article | Reason for final score |
|---|---:|---:|---|
| R1 Contribution | 3 | 3 | Clear bounded case study; no general methodological novelty established. |
| R2 Provenance | 4 | 4 | Claim records, recomputation, hashes, and figure bounds exposed and checked. |
| R3 Units and n | 4 | 4 | Structural unit, actual fold sizes, units, and aggregation are explicit. |
| R4 Evaluation | 3 | 3 | Fixed-family paired evidence improves interpretation; selection remains non-nested. |
| R5 Uncertainty | 3 | 3 | Descriptive uncertainty is honest; no independent confirmation exists. |
| R6 Observed/inferred | 4 | 4 | Both measured endpoints and all derived statuses remain distinct. |
| R7 Visuals | 3 | 3 | Correct, legible figures and improved flow; conventional thesis chapter breaks still leave some whitespace. |
| R8 Related work | 3 | 3 | Verified focused context, not a systematic literature review. |
| R9 Limitations | 4 | 4 | Target timing, cover, confounding, selection, software, and prognosis are explicit. |
| R10 Writing | 3 | 3 | Coherent question-led argument; some caveats intentionally recur in captions. |
| R11 Reproduction | 4 | 4 | Reporting commands and audit are reproducible; historical training boundary is disclosed. |
| R12 Calibration | 4 | 4 | No causal, RUL-validation, or current-classifier performance overclaim found. |

## Scientific requests that remain deferred

- Independent replication/crossed campaigns: requires new physical observations.
- Nested selection evaluation: requires a separately specified retraining study.
- Validated structural trajectories or lifetime outcomes: absent from this dataset.
- Exact historical software/hardware environment: incompletely archived; not guessed.
- Causal decomposition of metadata dominance: not identifiable from these two design combinations.

These remain limitations in both v2 documents. They cannot be solved by editing
prose or adding another derived table. The reporting task is complete; the
manuscripts are ready for the user's scientific review, not represented as
externally accepted or as validated operational predictors.

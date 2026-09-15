# Final verification record

Completed 2026-09-16 for the four delivered PDFs. This records reporting checks;
it is not independent peer review or validation of a deployed predictor.

## Build and visual inspection

| Document | Pages | Cited bibliography entries | Build result |
|---|---:|---:|---|
| `thesis/thesis.pdf` (v1) | 44 | 8 | Pass; one benign underfull source-map line |
| `article/article.pdf` (v1) | 5 | 7 | Pass |
| `thesis/v2/thesis.pdf` | 37 | 8 | Pass |
| `article/v2/article.pdf` | 5 | 7 | Pass |

All four have zero compile errors, undefined references/citations, unresolved
cross-reference rerun requests, missing glyphs, overflowing boxes, and
LaTeX/package warning messages. V1 retains its documented draft page-economy
weaknesses; v2 is the recommended reading version. The benign v1 underfull-box
diagnostic is retained in `qa/build_results.json`, rather than hidden.

Every final page was rendered with Poppler and inspected in contact sheets:
44 + 5 + 37 + 5 = 91 pages. Additional full-resolution inspection covered all
eight figure images, the final article page, the information-availability table,
and the source-map page. The final v2 pages have no observed clipped text,
overlapping labels, broken tables, or missing plotted points. Front-matter lists,
cross-references, captions, units, and bibliographies were checked. Conventional
chapter starts leave some whitespace; no one-line chapter spill remains in v2.

`qa/rendered_documents.json` hashes match the current PDFs and
`qa/final_validation.json`. Full final TeX logs are saved as
`qa/*_latex_log.txt`; `qa/*_build.txt` records latexmk execution.

## Numerical and source verification

- The audit verifies 43 claim groups against 72 hashed source files and checks
  60 specimen-disjoint split partitions. All recorded claim statuses are true.
- All 792 archived PNGs were checked using Pillow; the single unreadable file
  and resulting 791-row basis were confirmed without replacing the source data.
- Primary capacity fold MAEs were recomputed from saved terminal predictions;
  fold means and sample SDs were compared with saved feature-family summaries.
- The paired Ridge diagnostic matches 96 specimen/split keys and target values,
  then averages errors within 48 specimens. The 19/29 counts and signed mean/
  median are reproduced from those pairs, with no training or significance test.
- Group sample sizes, correlations, fixed-model robustness ratios, final versus
  diagnostic wire-loss winners, residual-refinement selection, curve counts,
  threshold statuses, feature counts, and augmentation manifests were checked
  against their specific sources in `VERIFICATION_LOG.md` and the paired record.
- The text/caption inventory has 181 lines with numerical expressions and zero
  unresolved decimal lint exceptions. Generated tables retain full-precision CSV
  companions. Matching a number is not proof of provenance: the source-specific
  audit and manual reading supply its target, regime, unit, and denominator.
- Final validation rechecks all source-file hashes and the two paired prediction
  hashes. Every figure PDF matches its provenance hash; all source paths exist.
- The confounding figure asserts 48/24/24 plotted points and checks every value
  falls inside its common data-derived axes. The earlier plotting-range defect,
  missed at contact-sheet scale, is explicitly recorded in the critique response.

## Manual scientific and language pass

Both revised manuscripts were reread, including abstracts, captions, conclusions,
and supplementary tables. The review checked these distinctions in context:

1. Two measured terminal structural endpoints, each once per specimen; no extra
   independent structural observations from target repetition or augmentation.
2. Surface-label adjacency does not establish identical historical code or
   hidden-condition inference. Cross-representation evidence reuses specimens.
3. Primary load scoring uses terminal images. Cover's pre-test availability is
   unverified. Within-fold preprocessing and non-nested model selection are
   distinguished.
4. LOCO is extrapolation under confounded design; treatment transfer is
   phase-dependent. Ratios use a fixed model, and descriptive SD is not a CI.
5. The post-onset result has changed eligibility/model choice and mixed metric
   gains. Negative subgroup R-squared is not universally absent rank information.
6. Zero future crossings coexist with 45 baseline and two observed-period
   crossings. Derived non-crossing is not observed survival censoring.
7. The current four-class branch is prepared and untrained. Historical and
   predecessor classification tasks are separate.
8. Software mtimes support chronology, not proof of the historical executable
   or complete freedom from old bugs. No historical environment is invented.

A final case-insensitive source scan found no exclusive structural-endpoint
claim, unqualified proof claim, classifier-achievement claim, TODO/TBD marker,
or unresolved placeholder. The only match for “causes” explicitly described
unresolved possibilities rather than estimated causes. The language pass corrected
an inappropriate “clinically” phrase and its replacement's indefinite article.

Eight bibliography entries are supported by the predecessor sources or verified
publisher/author metadata. The focused review does not claim systematic coverage.

## Preservation and remaining limits

All 23 initially hashed frozen-report source files remain byte-identical.
The branch is `report-rebuild-codex`; original data, historical model source,
saved model outputs, and `activity_report/` were not edited. No model fitting,
push, or merge was performed. Final Git scope/cleanliness is recorded in the
morning-summary completion check.

Independent replication, nested selection estimates, validated structural
trajectories, true lifetime outcomes, and complete historical execution metadata
remain unavailable. They are disclosed scientific limits, not failed PDF checks.

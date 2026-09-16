# V3 verification record

## Result

Both new documents compile to a fixpoint with **zero errors, undefined references/citations, unresolved rerun warnings, PDF-engine warnings or overfull boxes**. The thesis is **40 pages** and the IEEE article **5 pages**, retaining normal IEEEtran type and margins. Final full logs, build outputs, PDF hashes and rendered-PDF hashes are stored in this directory.

The extended `report_v2/scripts/validate_documents.py` reads all six manuscript versions and writes its new results here, preserving the earlier QA files. It checks **287 numeric-bearing lines** with **zero unresolved numeric lint exceptions**. Numeric matching is only a lint aid; the source-specific checks below establish the meaning of the new quantities.

## Numerical and scientific checks

- Reconstructed 48 terminal means and sample SDs from all 96 per-fold Ridge predictions. Each specimen has exactly two held-out terminal predictions, with observed loads from 1.60 to 2.87 kN. Verified prediction-minus-observation residuals and absolute errors.
- Rechecked the grouped specimen manifests and the exact test-specimen keys of the Ridge fold predictions. Recomputed grouped and campaign-out balance counts from manifests.
- Recomputed every mean and sample SD in the five-point learning summary from 50 saved subset/split runs. Its full-size held-out MAEs match the primary fold-metric table. These operations do not refit models.
- Inspected source code for Ridge standardization, one-hot encoding and within-field sums of absolute coefficients. Read all 11 saved full-fit magnitudes. This verifies their presentation and interpretation, not independent regeneration of the historical fit.
- Recomputed earlier feature-alignment Pearson correlations from a one-to-one join of the 792-row main_3 tables. Distinguished them from the later main_4 near-identity claim.
- Replayed 18 original plotting functions from saved tables; 15 are pixel-identical. Exact results and source hashes are in `report_v2/evidence/v3/figure_checks.json`.
- The new parity/residual plot has 48 points in each panel, all inside the axes. All 11 coefficient fields are shown, including the two tiny coefficients. The learning curve retains all 50 training and all 50 test errors, including the large small-subset error beyond the original mean-plus-SD view. Bounds and counts are checked in `new_figure_checks.json`.
- Broad guardrail scan and contextual review found no violations. Hits and dispositions are in `guardrail_review.json`. Both terminal structural endpoints, terminal-image scoring, dependent-fold SD, model-selection limitations, noncausal interpretation, untrained classifier status and lack of validated RUL remain explicit.

## Coherence and visual review

The full thesis and article prose were reread. The new section proceeds from the paired image increment to baseline errors, then fitted coefficient interpretation and the training-subset diagnostic. Cross-references connect these diagnostics to the confounding analysis and discussion. Two scope issues were explicitly clarified: historical versus refined feature alignment, and the learning curve's variation of sample count together with composition.

All 45 final PDF page layouts were viewed: five contact sheets cover all 40 thesis pages, with thesis PDF pages 23–25 and 39 inspected separately at 1600 px; all five article pages were inspected individually at 1600 px. All three new PNGs were viewed at original resolution. Labels, units, captions, legends, bounds and figure placements are legible; there are no unresolved layout problems. The two supplementary diagnostics share a clean thesis figure page. The article retains both previous figures and adds only the parity/residual composite.

## Preservation

`preservation_check.json` verifies **151 pre-existing files byte-for-byte**, including earlier manuscript sources, PDFs, build artifacts, bibliography, tables, evidence and figure assets. It additionally compares **32 tracked v1/v2 manuscript files directly with c5a4f1a**. All **30 candidate files** retain their initial SHA-256 hashes. All original shared-provenance entries remain unchanged; the JSON ledger has three appended entries and the Markdown ledger preserves its original byte prefix.

The frozen original report and all previously hashed modelling inputs also pass the existing validator. Git comparison against c5a4f1a shows no tracked changes under activity_report, main, main_2, main_3, main_4, main_4_old, augmentation, Data or emiling. The user's initially untracked audit prompt remains outside the commits. No training, source repair, push or merge occurred.

## Limits of verification

Exact meeting-montage generation recipes and the edit histories of the two older PDFs were not reconstructed. One gallery's blank/patterned low-corrosion example is not accepted as verified raw-image evidence. The full fitted model coefficients were read from the saved table, not re-estimated. Replayed plots and checked aggregates do not prove the historical training executable or eliminate model-selection bias. No independent data, calibrated prediction intervals or new prognostic validation are claimed.

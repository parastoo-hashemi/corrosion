# V3 change summary

## Delivered

- **Thesis:** `report_v2/thesis/v3/thesis.pdf` — 40 pages, forked from the 37-page v2 thesis, with modular chapter sources.
- **IEEE article:** `report_v2/article/v3/article.pdf` — five pages, preserving normal IEEEtran typography.
- **Complete audit:** `FIGURE_AUDIT.md` — one entry for each of 30 candidate files, including every page of both manuscript PDFs.

## Added and why

| New shared figure | Candidate sources | Contribution | Placement |
|---|---|---|---|
| `ridge_terminal_diagnostics.pdf` + PNG | R-06 parity, R-07 residuals | Shows individual baseline errors behind the competitive average, using all 48 terminal specimens; complements the paired HSV comparison. | Thesis Fig. 6.3; article Fig. 3 |
| `ridge_coefficients.pdf` + PNG | R-03 feature importance | Exposes the saved full fit's coefficient allocation, with explicit categorical aggregation, collinearity and noncausal limits. | Thesis Fig. 6.4 |
| `ridge_learning_curve.pdf` + PNG | R-04 learning curve | Shows train/test error sensitivity to training-specimen count and composition, retaining every saved fold value. | Thesis Fig. 6.5 |

Four source files were included with regeneration and consolidated into three figures; **26 were rejected**, chiefly for redundancy (**16**). Other exclusions concern mixed targets/units, unvalidated risk or uncertainty meanings, partial dependence over unobserved design combinations, and an unverified image montage. All decisions and source details are in the audit.

## Interpretation and editorial changes

The primary metadata-only Ridge result remains mean fold MAE 0.172711 kN (0.173 rounded). The new parity instead averages predictions per specimen and then computes errors; its MAE is 0.171941 kN. The v2 paired comparison averages absolute errors first. V3 distinguishes these aggregations and does not recast two-repeat SD as a prediction interval.

The earlier main_3 alignment figure has weak correlations, while the refined main_4 feature is nearly identical to the total-rust label. V3 states that generation boundary. The new learning evidence also narrows an overbroad v2 sentence: training-specimen count was varied with a fixed metadata representation, although subset composition and design coverage changed too. Neither finding establishes a causal effect.

The article retains its original confounding and paired-comparison figures. Repeated introductory, background and discussion prose was shortened to accommodate one essential diagnostic at five pages. The thesis connects all new figures to its existing results and discussion and adds exact saved-data reproduction commands to the appendix. No model was trained and no bibliography entries were added.

## Verification and preservation

Both PDFs compile without errors, unresolved references/citations, rerun warnings or overfull boxes. All new figures were viewed at full resolution; all 45 final PDF page layouts were reviewed. The extended validator reports 287 numeric-bearing lines and zero unresolved numeric lint exceptions. See `report_v2/qa/v3/VERIFICATION.md` for the check details and limitations.

**V1 and v2 are byte-for-byte unchanged.** The check covers 151 pre-existing artifact files and separately compares all 32 earlier tracked manuscript files with commit `c5a4f1a`. Existing eight figure PDFs/PNGs, bibliography, tables and evidence were preserved. The only extended shared artifact is the provenance ledger, whose original entries and Markdown prefix remain intact. Original source/data generations and all emiling candidates are unchanged. Earlier QA results were preserved; new QA records live under `report_v2/qa/v3/`.

Work is committed locally on `report-rebuild-codex-v3`; no push, merge or history rewrite is performed.

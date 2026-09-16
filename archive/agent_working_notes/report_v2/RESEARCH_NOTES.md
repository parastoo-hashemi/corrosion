# Research and writing rubric

Accessed 2026-09-16. This rubric was set before drafting; the self-review
scores the two first drafts against it. These are working standards, not
an assertion that any venue or university has accepted the manuscripts.

## Sources consulted and concrete choices

- Simon Peyton Jones, [How to write a great research paper](https://www.microsoft.com/en-us/research/academic-program/write-great-research-paper/): make the problem and central idea apparent early; make each result serve that idea.
- Mensh and Kording (2017), [Ten simple rules for structuring papers](https://doi.org/10.1371/journal.pcbi.1005619): organize around one contribution and a clear logical chain; paragraphs and sections have a purpose. The article's contribution is the evaluation boundary between image-based surface assessment and terminal structural inference.
- [NeurIPS Paper Checklist](https://nips.cc/public/guides/PaperChecklist): align abstract claims with evidence; disclose limitations, experimental settings, selection procedure, and the meaning of error bars. Explicitly label fold SD, dependent repeats, non-nested selection, and unavailable historical compute metadata.
- [IEEE Author Center templates](https://conferences.ieeeauthorcenter.ieee.org/write-your-paper/authoring-tools-and-templates/): use the real IEEEtran class, two columns, abstract, index terms, numbered sections, and numeric references. Place table captions above and figure captions below. No claim of conference submission.
- Politecnico di Torino, [Writing your thesis](https://didattica.polito.it/guida/2026/en/stesura_della_tesi?cds=473&sdu=81): institutional title metadata need verification, and programme-specific instructions matter. This page is for a different programme, so it is contextual guidance, not binding formatting authority. Use a conventional monograph structure; do not invent the present programme or supervisors.
- Cawley and Talbot (2010), [model selection and evaluation](https://www.jmlr.org/papers/v11/cawley10a.html): distinguish selecting a winning model from estimating the performance of the selection process.
- Roberts et al. (2017), [structured cross-validation](https://doi.org/10.1111/ecog.02881): choose a blocking unit tied to the prediction question; report when blocking also changes covariate support.
- Kapoor and Narayanan (2023), [leakage in ML-based science](https://doi.org/10.1016/j.patter.2023.100804): tie performance to a scientific claim and document information flow.

## Scored rubric (0 missing, 1 weak, 2 adequate, 3 strong, 4 exemplary)

| ID | Criterion | Passing evidence |
|---|---|---|
| R1 | Central contribution | Title/abstract/RQs/conclusion agree; article has one coherent empirical story. |
| R2 | Provenance and accuracy | Every empirical number maps to saved files or a run script; all figure sources documented; no invented references. |
| R3 | Unit of analysis | Every metric specifies target, units, dataset/specimen n, test unit, folds, and aggregation in text/table context. |
| R4 | Evaluation rigor | Group membership checked; prediction time explicit; selected winners distinguished from fixed-model robustness. |
| R5 | Uncertainty and selection | SD defined; repeated folds not treated as independent; no equivalence or significance claim from point estimates. |
| R6 | Observed vs inferred | Both structural endpoints named; derived trajectories and threshold status separated from measurements. |
| R7 | Visual communication | Standalone captions; legible at final size; consistent colors; no incompatible raw-metric ranking. |
| R8 | Related work | Predecessor contribution credited; detection/structural prediction/prognosis distinguished; verified citations. |
| R9 | Limitations and future work | Explicit design, labels, transfer, selection, prognostic, classification, and software limits; next steps tied to them. |
| R10 | Writing and structure | Results organized by question; chapters orient and transition; implementation names confined to reproducibility appendix. |
| R11 | Reproducibility | One command for figures/audit/build; frozen-source hash check; source/figure ledger; compile without unresolved citations/references. |
| R12 | Scientific calibration | No causal explanation claimed from confounding; no true RUL validation; no trained four-class result; phase-dependent LOTO described correctly. |

## Empirical-paper conventions adopted

Primary narrative: question -> design -> observations -> interpretation -> limits.
The full report adds dataset definitions, methodological detail, and a concrete
research agenda. Main results use all saved feature families so the reader can
see contrary as well as supporting cases. The article uses the same evidence but
its own prose. No new model fitting is required to achieve the reporting task.

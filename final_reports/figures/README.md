# Publication figures

**11 figures, each with a PDF publication version and a PNG viewing copy.**
The v3 manuscripts include the PDFs directly. PNG files are convenient for
browsing and presentations; the two formats are intentional companions.
This directory is shared by the thesis and article.

## Figure index

“Both” means the current v3 thesis and article. The notes summarize interpretation
limits; consult the manuscript captions for the complete context.

| Figure | Files | Used in v3 | Interpretation note |
|---|---|---|---|
| Dataset and supervision structure | [PDF](dataset_supervision.pdf) · [PNG](dataset_supervision.png) | Thesis | Counts and schematic geometry; the layout is illustrative. |
| Evaluation design | [PDF](evaluation_regimes.pdf) · [PNG](evaluation_regimes.png) | Thesis | Specimen grouping schematic; tile counts are illustrative. |
| Surface label/feature alignment | [PDF](label_adjacency.pdf) · [PNG](label_adjacency.png) | Thesis | Near reconstruction of a label does not verify identical label-generation code. |
| Robustness across evaluation regimes | [PDF](robustness_synthesis.pdf) · [PNG](robustness_synthesis.png) | Thesis | Errors normalized within each generation; not a raw-metric ranking across generations. |
| Pooled terminal-load feature comparison | [PDF](capacity_ablation.pdf) · [PNG](capacity_ablation.png) | Thesis | Selected models; fold standard deviations are descriptive, not confidence intervals. |
| Paired effect of adding HSV features | [PDF](paired_specimen_errors.pdf) · [PNG](paired_specimen_errors.png) | Both | Per-specimen error differences after model selection; no significance claim. |
| Ridge terminal parity and residuals | [PDF](ridge_terminal_diagnostics.pdf) · [PNG](ridge_terminal_diagnostics.png) | Both | Averages two held-out predictions per specimen; no calibrated intervals. |
| Ridge coefficient magnitudes | [PDF](ridge_coefficients.pdf) · [PNG](ridge_coefficients.png) | Thesis | Full-fit field-level absolute coefficient sums; not causal or held-out importance. |
| Saved Ridge training-subset diagnostic | [PDF](ridge_learning_curve.pdf) · [PNG](ridge_learning_curve.png) | Thesis | Saved runs across dependent folds; means and standard deviations are descriptive. |
| Campaign design and rust/load associations | [PDF](confounding.pdf) · [PNG](confounding.png) | Both | Observed campaign combinations confound several factors; associations are not causal effects. |
| Exploratory threshold status | [PDF](threshold_status.pdf) · [PNG](threshold_status.png) | Thesis | Model-derived wire-loss trajectories, not observed lifetime events. |

## Provenance and evidence

- [PROVENANCE.md](PROVENANCE.md) and [PROVENANCE.json](PROVENANCE.json): source paths,
  generator names and the main figure ledger, including the three v3 Ridge additions.
- [PAIRED_PROVENANCE.md](PAIRED_PROVENANCE.md) and
  [PAIRED_PROVENANCE.json](PAIRED_PROVENANCE.json): separate paired-error ledger.
- [FIGURE_DATA_CHECKS.json](FIGURE_DATA_CHECKS.json): saved numerical checks for
  the confounding panels.
- [Archived v3 evidence](../records/evidence/v3): saved inventories and figure checks.

These provenance records keep historical paths. The [folder migration guide](../../docs/folder_migration.md)
and root path resolver map old experiment names to their current locations.
The [script guide](../scripts/README.md) explains which utilities can overwrite
figures and provenance. All existing assets and ledgers remain unchanged.
[Return to the report guide](../README.md).

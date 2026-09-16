# Ferrocement corrosion: images, structural capacity, and research handoff

## Project Overview

This MSc technical activity studies what repeated photographs of surface corrosion
can tell us about ferrocement specimens and their terminal structural capacity.
The most mature completed experiment asks whether image-derived corrosion features
add information beyond specimen metadata when estimating **terminal ultimate load**.
A separate, later workstream prepares images for four-class corrosion classification.

Start with the [report guide](report_v2/README.md), then the
[experiment map](docs/experiments.md). For continuing the work, read
[reproduction](docs/reproduction.md) and [known issues](docs/known_issues.md).

## Dataset

The current basis is **48 specimens in two campaigns**, with 792 source images and
**791 readable, aligned observations**. Each specimen has repeated photographs;
**both wire-area loss and ultimate load are measured once, at the terminal test**.
Images therefore do not provide hundreds of independent structural outcomes.
Campaign, mesh family, chloride concentration, and exposure schedule are aligned,
which limits generalization and prevents separating their causal contributions.

Raw and prepared assets are in [Data/](Data/). The classification workbook is
[Images_Dataset_A-Z-1.xlsx](Data/Images_Dataset_A-Z-1.xlsx); historical structural
pipelines use their own configured workbook copies. Do not substitute one workbook
for another. See the [data dictionary](docs/data_dictionary.md).

## Project Structure

| Location | Role |
|---|---|
| [Data/](Data/) | Raw workbooks/images, prepared classification images, variants, and fixed splits; locally present, ignored by Git |
| [main_first/](main_first/) | Exploratory prototype; no defensible held-out benchmark |
| [main/](main/) | Historical classical corrosion baseline and API code |
| [main_2/](main_2/) | Historical frozen deep-image embeddings with tabular context |
| [main_3/](main_3/) | Interpretable features, structural feasibility, and first proxy-RUL pipeline |
| [main_4/](main_4/) | Most mature structural generation: robustness analysis and terminal-load refocus |
| [main_4_old/](main_4_old/) | Retained earlier baseline snapshot; not the current entry point |
| [augmentation/](augmentation/) | Separate four-class data preparation and specimen split scripts |
| [activity_report/](activity_report/) | Original technical activity report, source, figures, and bibliography |
| [report_v2/](report_v2/) | Thesis/article manuscript versions, shared figures, tables, and reporting scripts |
| [Documentation/](Documentation/) | Source thesis/conference material and saved augmentation reports; locally present, ignored by Git |
| [emiling/](emiling/) | Historical presentation/export copies; retained for traceability |
| [out/](out/) | Mixed historical build/output tree of uncertain ownership; preserved |
| [docs/](docs/) | Curated handoff documentation |
| [archive/agent_working_notes/](archive/agent_working_notes/) | Historical plans, reviews, prompts, and evidence records, mirrored by original path |
| [report_cleanup/](report_cleanup/) | Move manifest, preservation snapshots, and cleanup checks |

Physical implementation names are retained because imports, configs, saved paths,
and report citations depend on them. The [project history](docs/project_history.md)
explains the phases. Compatibility links retain certain archived lookup paths.
Local caches, editor settings, and an empty `tmp/` are not research entry points.

## Research Workflow

Data audit → visible-corrosion modelling → structural feasibility → robustness
analysis → terminal-load refocus → degradation/proxy-RUL screening → four-class
classification preparation. This is a research map, not an instruction to rerun
all historical pipelines; degradation screening also existed in earlier phases.

## Key Findings

- Visible corrosion and hidden structural damage are different prediction targets.
- Some strong surface results mainly reconstruct a closely related image-derived label.
- Metadata is a strong terminal-load baseline; images do not show a consistent
  improvement across the evaluated settings.
- Campaign holdout exposes poor structural transfer; pooled results need that context.
- Model-derived degradation curves and threshold crossings are exploratory.
  They are not validated remaining-life predictions.

Detailed numbers and interpretation belong in the manuscripts and their saved tables.

## How to Run

From this repository's root, with the Python environment described below:

```bash
python report_cleanup/verify_delivery.py --quick
python augmentation/augment_dataset.py --help
python augmentation/make_splits.py --help
```

These commands check the delivered structure or show command-line options; they
neither train models nor replace datasets. The full preservation check is:

```bash
python report_cleanup/verify_delivery.py --full
```

[Reproduction instructions](docs/reproduction.md) give the exact preparation and
PDF build commands for a separate working copy. Historical training commands are
in [experiments](docs/experiments.md), with their current execution blockers.

## Environment / Dependencies

This handoff was checked with `/opt/anaconda3/envs/env/bin/python` on the delivery
machine. Substitute your environment's `python` elsewhere. Existing dependency
files are [main/requirements.txt](main/requirements.txt),
[main_2/requirements.txt](main_2/requirements.txt),
[main_3/requirements.txt](main_3/requirements.txt), and
[augmentation/requirements.txt](augmentation/requirements.txt).
They specify minimum versions, not locked historical environments.
**There is no `main_4/requirements.txt`.**

The current structural code imports NumPy, pandas, SciPy, scikit-learn, PyYAML,
Pillow, scikit-image, matplotlib, seaborn, joblib, XGBoost, and CatBoost.
The split script also needs pandas, which the augmentation requirements file
currently omits. PDF compilation needs `latexmk`, a LaTeX distribution, BibTeX,
and the packages declared in each master, including IEEEtran for the article.
[Verified environment records](report_cleanup/environment.json) describe the
handoff machine; they do not establish the original training environment.

## Outputs

- Most mature structural results: [main_4/outputs/ultimate_load_refocus/](main_4/outputs/ultimate_load_refocus/).
  Its `splits/` holds specimen/row manifests; experiment directories hold fold
  metrics, terminal predictions, fitted models, and diagnostic figures.
- Earlier robustness/degradation outputs: [main_4/outputs/models/](main_4/outputs/models/)
  and [diagnostics/](main_4/outputs/diagnostics/).
- Classification partitions: [Data/splits/](Data/splits/) — 3,846 training rows
  (641 originals plus 3,205 augmentations), 75 validation originals, and 75 test
  originals; 38/5/5 disjoint specimens. Classifier training/evaluation is pending.
- Report assets: [report_v2/tables/](report_v2/tables/),
  [figures/](report_v2/figures/), and the PDFs below.
- The [experiment map](docs/experiments.md) locates outputs for every historical phase.

## Reproducibility Notes

Keep all images and augmented copies of a specimen in one split; held-out
classification partitions contain originals only. The terminal-load workflow
fits historical image rows with repeated terminal targets and evaluates terminal
images. It is not an early-warning validation. Model selection used the reported
folds, and fold variability is descriptive rather than an independent confidence interval.

Saved outputs are preserved. Current historical modelling code has unresolved
`main_first` substitutions and a YAML `NO`/`False` category issue. Parsing code or
loading YAML does not establish that training can run correctly. See
[known issues](docs/known_issues.md) before attempting a new experiment.

A Git clone alone omits ignored raw data, some local model artifacts, and three
historical `main_3/src/data/` source files. A full
handoff needs the local data/output bundle as well as the repository. Preserve
symbolic links when copying the delivery. Do not regenerate results over the
saved evidence merely to test installation.

## Current Status

**Four-class classifier data preparation: complete. Training and evaluation: not
yet done.** Historical five-class and predecessor three-class results are different
experiments. Structural results and reports are available for review; the modelling
source is not a clean, validated rerun baseline.

## Recommended Next Steps

1. Select the authoritative manuscript version with the supervisor.
2. In an isolated development copy, recover and verify a runnable modelling source
   state and repair category handling before producing new results.
3. Implement the four-class training/evaluation study using the saved specimen
   partitions, reporting per-class performance and imbalance explicitly.
4. For structural claims, prioritize independent specimens, crossed experimental
   factors, and repeated structural measurements over model complexity.

## Final Report Location

- [Original activity report](activity_report/activity_report.pdf).
- Latest produced alternatives: [v3 thesis](report_v2/thesis/v3/thesis.pdf)
  (40 pages) and [v3 IEEE article](report_v2/article/v3/article.pdf) (5 pages).
- Earlier manuscript versions remain in [report_v2/](report_v2/).

**The authoritative report version has not been selected.** “Latest produced”
does not mean approved or accepted. All report sources and PDFs retain their
pre-cleanup bytes. The [cleanup handoff](CLEANUP_HANDOFF.md) records the delivery checks.

# Reproduction and safe continuation

## 1. Open and check the delivered repository

Use the repository root as the working directory. On the delivery machine:

```bash
cd /Users/parastoo/All_projects/Proj_corrosion/corrosion
/opt/anaconda3/envs/env/bin/python -B archive/repository_maintenance/renaming/verify_renaming.py --quick --output /tmp/corrosion-handoff-check.json
/opt/anaconda3/envs/env/bin/python classification_data_preparation/augment_dataset.py --help
/opt/anaconda3/envs/env/bin/python classification_data_preparation/make_splits.py --help
```

On another machine, substitute its checkout and Python interpreter. The verifier uses Python standard-library modules. CLI help checks require the
imports declared in those scripts. Quick verification checks folder targets, source
syntax, edited-file hashes, absence of obsolete root aliases, retained archive links,
current documentation links, and
TeX input paths. The saved migration receipts also contain import, configuration,
model-loading and prediction checks. To hash every pre-existing file against the
immediately pre-rename inventory:

```bash
python -B archive/repository_maintenance/renaming/verify_renaming.py --full --output /tmp/corrosion-handoff-full-check.json
```

The full check reads approximately 49 GB. These commands write receipts to the
specified temporary paths, preserving earlier verification records. The checker
compares historical baselines; consult the [latest review](../archive/repository_maintenance/handoff_guides/README.md)
for pre-existing differences. It does not run models or modify saved outputs.
A clean checkout needs the ignored local data and artifacts too. Preserve symlinks
when copying the retained archive-document links. The seven old root folder
shortcuts have been removed; use the new names in commands and imports.

## Environment and dependencies

The handoff was checked using `/opt/anaconda3/envs/env/bin/python` on the delivery
machine. Use your environment's Python executable elsewhere. The
[environment record](../archive/repository_maintenance/environment.json) describes that check
runtime; it does not establish the original training runtime of saved estimators.

Existing minimum-version dependency lists are:

- [Classical models](../classical_corrosion/requirements.txt)
- [Image embeddings](../image_embeddings/requirements.txt)
- [Condition assessment](../condition_assessment/requirements.txt)
- [Classification preparation](../classification_data_preparation/requirements.txt)

There is no `structural_capacity/requirements.txt`. Its current source imports
NumPy, pandas, SciPy, scikit-learn, PyYAML, Pillow, scikit-image, matplotlib,
seaborn, joblib, XGBoost and CatBoost. The classification requirements also omit
pandas, which the split and variant scripts need. These are installation gaps,
not a tested environment specification. Consult [known issues](known_issues.md)
before choosing versions; no packages were installed or upgraded during cleanup.

Report builds require `latexmk`, a LaTeX distribution, BibTeX and the packages
declared in the masters, including IEEEtran for the article.

The three files in `condition_assessment/src/data/` are tracked and pass the
ignore-rule eligibility check at this handoff review. Include the ignored local
data/model bundle when transferring the project; a Git-only clone is not the
complete handoff. This documentation review does not stage or commit files.

## 2. Prepare a separate reproduction copy

Keep the delivered outputs untouched. Copy the complete local repository, including
ignored data and models, to a separate working location with sufficient disk space.
Compare the full preservation inventory before beginning any new experiment.
Inspect [known issues](known_issues.md) before running historical modelling code.
The observed Python package versions are recorded in
[environment.json](../archive/repository_maintenance/environment.json); they establish this check
runtime, not the training runtime of historical saved estimators.

For classification preparation, `classification_data_preparation/requirements.txt` supplies NumPy,
openpyxl and Pillow minimums. Also install pandas for split/variant scripts. No
package installation or version changes were performed during cleanup.

## 3. Classification data preparation, in order

The existing prepared dataset uses **five** augmented copies and seed **20260630**.
The script default is four copies, so use the explicit argument when reproducing
this package. The commands below write to a new folder in the reproduction copy,
leaving the canonical saved dataset and split files in place:

```bash
python classification_data_preparation/augment_dataset.py \
  --copies 5 --seed 20260630 \
  --output-dir reproduction_run/images \
  --output-csv reproduction_run/augmented.csv \
  --report reproduction_run/augmentation_report.md \
  --codex-report reproduction_run/augmentation_report_copy.md \
  --contact-sheet reproduction_run/contact_sheet.png

python classification_data_preparation/make_splits.py \
  --input-csv reproduction_run/augmented.csv \
  --output-dir reproduction_run/splits \
  --report reproduction_run/split_report.md
```

These are full generation commands and were not executed during cleanup. Their
arguments were checked against the scripts' CLI help. Paths are relative to the
repository root. Existing output protection remains active; do not use `--overwrite`
against the handoff evidence. The scripts keep specimen identity and original-image
provenance; the split script uses the existing explicit 38/5/5 specimen assignment.

Controlled variants are generated separately by
`python classification_data_preparation/create_dataset_variants.py`; consult its `--help` before choosing
new destinations. Its contact sheets still use a fixed phase figure directory,
so `--output-dir` alone does not redirect every write; use the separate copy.
The saved [variant package](../Data/augmentation_variants) needs
[metadata reconciliation](known_issues.md#controlled-variant-metadata-needs-reconciliation)
before classifier use. Its `sigma*` CSVs do not match the current generator's full
provenance schema, and `sigma2_noise` has two missing original metadata rows.
The former `Documentation/codex/augmentation_variant_report.md`
path is absent in this delivery; it is not a current reproduction dependency.
Prepared data do not demonstrate classifier accuracy.

## 4. Compile a report without fitting a model

Use a separate copy for builds, because compilation changes PDFs and auxiliary
files even when the scientific source is unchanged. The current manuscripts
use existing shared figures/tables/bibliography:

```bash
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error final_reports/sources/thesis/thesis.tex
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error final_reports/sources/article/article.tex
```

The new PDF is written beside its source under `final_reports/sources/`. Review
it before replacing the delivered PDF at the top of `final_reports/`.

The original activity-report source directory and earlier `report_v2` draft
versions (v1, v2) were removed from the working tree. A historical compiled
[activity-report draft](../out/activity_report.pdf) remains among the six PDFs
in `out/`; it is not the current delivery report. See the
[export audit](../archive/repository_maintenance/out_audit/README.md) for document provenance.

The delivered PDFs remain the reference copies; prior report QA retains build
and visual-review records. Rebuilding on another TeX installation need not yield
the same binary hash. After any manuscript edit, compile, render, and visually
inspect all affected pages. The current documentation review did not rebuild them.

The retained [scientific report scripts](../final_reports/scripts/README.md) audit saved
results, recompute summary statistics and regenerate scientific figures/tables.
They can overwrite outputs and should run only in an intentional reproduction
copy. `make_figures.py`, `paired_diagnostics.py` and `make_v3_figures.py` regenerate
assets used by the current manuscripts. `audit_evidence.py` and
`audit_saved_figures.py` support the scientific provenance checks.

Optional Python manuscript-build wrappers, draft-revision/bibliography assembly,
PDF contact-sheet rendering and the obsolete all-draft document checker were
removed. Use the direct `latexmk` commands above for PDF builds and the current
folder-migration verifier for read-only preservation checks. The
[publication-tool cleanup record](../archive/repository_maintenance/publication_tools/README.md)
lists removed files and explains how to recover their external backup.

## 5. Resume modelling only after a separate repair

[Experiments](experiments.md#working-directories) lists the working directories.
Start with the phase guide: [classical models](../classical_corrosion/README.md),
[image embeddings](../image_embeddings/README.md), [condition assessment](../condition_assessment/README.md)
or [structural capacity](../structural_capacity/README.md). The
[exploratory scripts](../exploratory_prototype/README.md) need source review before
execution and are not a package import smoke test.
First recover intended source/config values and category types; then confirm
specimen grouping, train-only preprocessing, target units, and evaluation time.
Do not infer that AST or YAML parsing success proves end-to-end execution.
Do not silently update saved metrics to match repaired code. A future run must have
its own results namespace, environment record, and comparison with the frozen evidence.

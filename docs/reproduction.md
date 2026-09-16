# Reproduction and safe continuation

## 1. Open and check the delivered repository

Use the repository root as the working directory. On the delivery machine:

```bash
cd /Users/parastoo/All_projects/Proj_corrosion/corrosion
/opt/anaconda3/envs/env/bin/python report_cleanup/verify_delivery.py --quick
/opt/anaconda3/envs/env/bin/python augmentation/augment_dataset.py --help
/opt/anaconda3/envs/env/bin/python augmentation/make_splits.py --help
```

On another machine, substitute its checkout and Python interpreter. The check
requires PyYAML; the CLI help checks require the imports declared in those scripts.
Quick verification checks source syntax/AST invariance, configs, compatibility
links, curated documentation links, report inputs, and stored provenance inputs.
It reports known pre-existing path/config defects separately. To check every
preserved input/output byte against the pre-cleanup inventory:

```bash
python report_cleanup/verify_delivery.py --full
```

The full check reads approximately 49 GB and writes only its own verification
records under `report_cleanup/`. It does not run models or modify saved outputs.
A clean checkout needs the ignored local data and artifacts too. Preserve symlinks
when copying; the archive and compatibility paths form one delivery tree.

## 2. Prepare a separate reproduction copy

Keep the delivered outputs untouched. Copy the complete local repository, including
ignored data and models, to a separate working location with sufficient disk space.
Compare the full preservation inventory before beginning any new experiment.
Inspect [known issues](known_issues.md) before running historical modelling code.
The observed Python package versions are recorded in
[environment.json](../report_cleanup/environment.json); they establish this check
runtime, not the training runtime of historical saved estimators.

For classification preparation, `augmentation/requirements.txt` supplies NumPy,
openpyxl and Pillow minimums. Also install pandas for split/variant scripts. No
package installation or version changes were performed during cleanup.

## 3. Classification data preparation, in order

The existing prepared dataset uses **five** augmented copies and seed **20260630**.
The script default is four copies, so use the explicit argument when reproducing
this package. The commands below write to a new folder in the reproduction copy,
leaving the canonical saved dataset and split files in place:

```bash
python augmentation/augment_dataset.py \
  --copies 5 --seed 20260630 \
  --output-dir reproduction_run/images \
  --output-csv reproduction_run/augmented.csv \
  --report reproduction_run/augmentation_report.md \
  --codex-report reproduction_run/augmentation_report_copy.md \
  --contact-sheet reproduction_run/contact_sheet.png

python augmentation/make_splits.py \
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
`python augmentation/create_dataset_variants.py`; consult its `--help` before choosing
new destinations. The existing [variant package](../Data/augmentation_variants/)
and [variant report](../Documentation/codex/augmentation_variant_report.md) already
contain the completed preparation results. None demonstrate classifier accuracy.

## 4. Compile a report without fitting a model

Use a separate copy for builds, because compilation changes PDFs and auxiliary
files even when the scientific source is unchanged. The latest produced manuscripts
use existing shared figures/tables/bibliography:

```bash
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error report_v2/thesis/v3/thesis.tex
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error report_v2/article/v3/article.tex
```

The original activity report is compiled independently:

```bash
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error activity_report/activity_report.tex
```

These build commands were inspected but not executed during cleanup: the delivered
PDF hashes are preserved, and the prior report QA contains their compilation and
visual review records. Rebuilding on another TeX installation need not yield the
same binary hash. After any manuscript edit, compile, render, and visually inspect
all affected pages.

Reporting scripts in [report_v2/scripts/](../report_v2/scripts/) include commands
that regenerate shared tables/figures or earlier manuscripts. They are not a
read-only installation test. In particular, `revise_drafts.py` reconstructs v2,
and `make_figures.py`, `paired_diagnostics.py`, and `make_v3_figures.py` replace assets.
`validate_documents.py` also writes QA files. Use the cleanup verifier for read-only
checks of preserved scientific artifacts; use the historical report tools only in
an intentional report-editing copy.

## 5. Resume modelling only after a separate repair

[Experiments](experiments.md) lists the historical commands and working directories.
First recover intended source/config values and category types; then confirm
specimen grouping, train-only preprocessing, target units, and evaluation time.
Do not infer that AST or YAML parsing success proves end-to-end execution.
Do not silently update saved metrics to match repaired code. A future run must have
its own results namespace, environment record, and comparison with the frozen evidence.

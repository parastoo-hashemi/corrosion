# Folder names and migration guide

The project was reorganized on 2026-09-16 around research purpose. Use the new
names in current commands and new code. The rename leaves scientific data,
configuration values, fitted objects, metrics, figures and manuscripts unchanged.

| Original name | Current directory | Research role |
|---|---|---|
| `main_first/` | [exploratory_prototype/](../exploratory_prototype/) | Early exploration and simulations |
| `main/` | [classical_corrosion/](../classical_corrosion/) | Classical corrosion baselines |
| `main_2/` | [image_embeddings/](../image_embeddings/) | Frozen image embeddings plus tabular context |
| `main_3/` | [condition_assessment/](../condition_assessment/) | Interpretable condition assessment and first structural/proxy-RUL work |
| `main_4/` | [structural_capacity/](../structural_capacity/) | Structural robustness and terminal-load study |
| `main_4_old/` | [archive/structural_baseline_snapshot/](../archive/structural_baseline_snapshot/) | Retained earlier structural baseline |
| `augmentation/` | [classification_data_preparation/](../classification_data_preparation/) | Four-class image preparation and specimen partitions |

## Why the old names still appear

Each original root name is a relative symbolic link to the new directory, not a
second copy. These links preserve old saved relative paths, manuscript citations,
and imports. Keep them when copying the project. On a destination without symlink
support, extract the handoff on a filesystem that supports links before verification;
simply dropping the links will break historical references. The source checkout
itself must still be named `corrosion` for qualified package commands.

Historical archive trees, generated reports, TeX, metadata, model manifests and
checksum ledgers retain their original wording and paths. `main_first` also occurs
as pre-existing corrupted scientific values: these occurrences were not renamed
or repaired. See [known issues](known_issues.md).

## Running current entry points

From the **parent** of the `corrosion` checkout:

```bash
python -m corrosion.classical_corrosion.train_models --help
python -m corrosion.image_embeddings.train_phase2 --help
```

From the **repository root**:

```bash
python classification_data_preparation/augment_dataset.py --help
python classification_data_preparation/make_splits.py --help
python report_cleanup/renaming/verify_renaming.py --quick
python -B -m unittest discover -s tests
python -B -m unittest discover -s condition_assessment/tests
```

Condition-assessment scripts retain their local `src` bootstrap. Structural scripts
must run with `structural_capacity/` as the working directory. For the archived
baseline, use `archive/structural_baseline_snapshot/` as the working directory.
Run generations in separate Python processes because some internal package names
overlap. [Experiments](experiments.md) maps the historical training entry points;
help/import checks do not certify an end-to-end scientific rerun.

## Artifact portability

The classical and embedding inference loaders retain an existing recorded model
path. If it is missing, they look for the same filename inside the caller-supplied
artifact directory. They do not search other experiments, change a saved manifest,
or modify an estimator. Keep all components of each artifact bundle together.
The embedding preprocessor's existing scikit-learn compatibility problem still
needs a separate environment repair.

## Evidence and recovery

The [migration report](../report_cleanup/renaming/RENAMING_REPORT.md) records tests
and limitations. [move_manifest.csv](../report_cleanup/renaming/move_manifest.csv)
maps every relocated regular file, and [folder_map.json](../report_cleanup/renaming/folder_map.json)
maps the seven directories. The immediately pre-rename file hashes, original text
of edited files, and before/after test records are alongside them.

A source/document backup is outside the repository at
`../corrosion_pre_rename_sources_20260916.tar.gz`. It is a source backup, not a second
copy of the 49 GB data bundle. The full pre-cleanup backup predates later deliberate
report removals and must not be treated as the current delivery state.

To undo this migration in an isolated copy, first check that no later work would
be overwritten. Restore edited files from `source_before/`, reverse the directory
mapping, restore the recorded original symlink targets, and remove only files
created by this migration (listed in its final inventory). Do not use Git reset or
restore operations against unrelated work. No staging, commit, or other Git
mutation was performed for this migration.

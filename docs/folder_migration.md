# Folder names and migration guide

The project was reorganized on 2026-09-16 around research purpose. Use the new
names in current commands and new code. The rename leaves scientific data,
configuration values, fitted objects, metrics, figures and manuscripts unchanged.

| Original name | Current directory | Research role |
|---|---|---|
| `main_first/` | [exploratory_prototype/](../exploratory_prototype) | Early exploration and simulations |
| `main/` | [classical_corrosion/](../classical_corrosion) | Classical corrosion baselines |
| `main_2/` | [image_embeddings/](../image_embeddings) | Frozen image embeddings plus tabular context |
| `main_3/` | [condition_assessment/](../condition_assessment) | Interpretable condition assessment and first structural/proxy-RUL work |
| `main_4/` | [structural_capacity/](../structural_capacity) | Structural robustness and terminal-load study |
| `main_4_old/` | [archive/structural_baseline_snapshot/](../archive/structural_baseline_snapshot) | Retained earlier structural baseline |
| `augmentation/` | [classification_data_preparation/](../classification_data_preparation) | Four-class image preparation and specimen partitions |

The selected sharing collection was also renamed, preserving every file:

| Original collection path | Current location |
|---|---|
| `emiling/` | [selected_results/](../selected_results/README.md) |
| `emiling/main_3/` | [selected_results/condition_assessment/](../selected_results/condition_assessment/README.md) |
| `emiling/main_4/` | [selected_results/structural_capacity/](../selected_results/structural_capacity/README.md) |

The nested `metadata_only+Ridge/` folder and all research filenames are unchanged.
See the [backup and preservation record](../archive/repository_maintenance/selected_results/README.md).

## Final report package

| Previous path | Current location |
|---|---|
| `report_v2/` | [final_reports/](../final_reports/README.md) |
| `report_v2/thesis/v3/thesis.pdf` | [final_reports/thesis.pdf](../final_reports/thesis.pdf) |
| `report_v2/article/v3/article.pdf` | [final_reports/article.pdf](../final_reports/article.pdf) |
| `report_v2/thesis/v3/` sources | [final_reports/sources/thesis/](../final_reports/sources/thesis/README.md) |
| `report_v2/article/v3/` sources | [final_reports/sources/article/](../final_reports/sources/article/README.md) |
| Shared figures, tables, references and scripts | Same subfolder names under `final_reports/` |
| Scattered evidence, QA and review links; former `final_reports/records/` | [Manuscript archive](../archive/agent_working_notes/report_v2) |

Both delivered PDFs and all LaTeX content are unchanged. Sources retain the same
relative depth to their shared assets. Build products were removed after backup;
see the [recovery record](../archive/repository_maintenance/final_reports/README.md). Old citations
can be located with `python research_paths.py "report_v2/thesis/v3/thesis.pdf"`.

## Repository maintenance records

The former `report_cleanup/` directory now lives in
[archive/repository_maintenance/](../archive/repository_maintenance/README.md).
It contains cleanup inventories, verification tools and recovery records. Its
current tools and guide links use the archive directly; no root shortcut is needed.
Historical recorded paths still resolve with `python research_paths.py`.

## Structural study documentation

`structural_capacity/README.md` is the current guide to the structural phases and
saved results. Nine historical Markdown shortcuts were removed from that folder;
their documents remain in [the development archive](../archive/agent_working_notes/main_4).
The path resolver accepts both `main_4/<note>.md` and `structural_capacity/<note>.md`.
Future generated notes go into the appropriate `outputs/reports/`,
`outputs/diagnostics/` or `outputs/improvements/` subfolder and preserve the curated
README. See the [documentation cleanup record](../archive/repository_maintenance/structural_documentation/README.md).

## Clean root and historical paths

The seven old root shortcuts have been removed. Use only the descriptive names in
commands, imports and new work. The source checkout itself must still be named
`corrosion` for qualified package commands.

Historical archive trees, generated reports, TeX, metadata, model manifests and
checksum ledgers retain their original wording and paths. To locate a recorded
repository-relative path, run from the repository root:

```bash
python research_paths.py "main_4/outputs/data/master_table.csv"
```

This prints the current location. Report readers use the same explicit mapping:
legacy experiment roots, report-package paths and the old `emiling/` collection
prefixes are translated.
Names embedded in other directories, such as `archive/agent_working_notes/main_4/`,
keep their historical identities. Paths outside
this checkout are not guessed. Old manuscript path citations and archived Markdown
links should be interpreted using the mapping above; the frozen documents are not
rewritten. External scripts using old import names must use the new names.

The remaining archive links are part of the delivery. Manuscript audit records
are accessed directly in `archive/agent_working_notes/report_v2/`; the temporary
`final_reports/records/` shortcut has been removed. Scripts and current guides use
the archive directly, and the path resolver also accepts the former shortcut paths.
Preserve the archive when copying the repository. `main_first` also occurs as pre-existing corrupted
scientific values: these occurrences were not renamed or repaired. See
[known issues](known_issues.md).

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
python archive/repository_maintenance/renaming/verify_renaming.py --quick
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

The [cleanup report](../archive/repository_maintenance/alias_removal/CLEANUP_REPORT.md) records the
current alias-free layout and verification. The [earlier migration report](../archive/repository_maintenance/renaming/RENAMING_REPORT.md)
records the preceding rename stage. [move_manifest.csv](../archive/repository_maintenance/renaming/move_manifest.csv)
maps every relocated regular file, and [folder_map.json](../archive/repository_maintenance/renaming/folder_map.json)
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

The subsequent alias-removal stage keeps its immediately preceding source/guide
versions in `archive/repository_maintenance/alias_removal/source_before/`. The removed links and
their exact targets are recorded in `archive/repository_maintenance/alias_removal/removed_links.json`.
No real research directory was deleted.

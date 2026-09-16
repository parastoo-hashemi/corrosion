# Research-folder migration — 2026-09-16

**Historical migration stage:** the root aliases described below were subsequently
removed. See [the current cleanup report](../alias_removal/CLEANUP_REPORT.md) and
[current folder guide](../../docs/folder_migration.md). The preceding verification
receipts and source text are preserved under `alias_removal/source_before/`.

## Delivery

Seven research directories have descriptive names. Current imports, path builders,
reporting-script inputs and handoff guides use those names. Seven relative links
retain the original root paths for historical records and imports; no data was
duplicated. Nine pre-existing links inside the relocated baseline snapshot were
retargeted. The existing v3-only report selection is preserved.

See [the folder guide](../../docs/folder_migration.md) for the full mapping and working
directories. [move_manifest.csv](move_manifest.csv) lists every relocated regular
file. The physical snapshot is `archive/structural_baseline_snapshot/`.

## Dependency changes

- Qualified Python imports now use `corrosion.classical_corrosion` and
  `corrosion.image_embeddings`. These module commands run from the checkout's parent.
- Classification preparation defaults and current report scripts use the descriptive
  directory paths. Internal `src` and `corrosion_proxy_rul` package names are unchanged.
- The nested structural snapshot retains its internal data/config/output layout;
  its README and archive links account for its new depth.
- The two inference loaders resolve a missing historical artifact path to the same
  filename inside the explicitly supplied artifact bundle. Existing recorded paths
  retain precedence. Manifests and serialized models are not rewritten.
- Curated guides identify the v3 thesis/article as the delivered manuscripts and
  point to the current verifier. The earlier cleanup verifier and checksum ledgers
  remain historical records, since delivery scope and selected source paths changed.

Only imports, path lookup and current documentation changed. Historical scientific
`main_first` substitutions, YAML scalar/category values, seeds, formulas and
hyperparameters were preserved. No training, data generation or PDF build was run.

## Verification

The reproducible checker is [verify_renaming.py](verify_renaming.py):

```bash
python report_cleanup/renaming/verify_renaming.py --quick
python report_cleanup/renaming/verify_renaming.py --full
```

The full mode reads approximately 49 GB. `--check-git` additionally checks that
HEAD, branch, refs and index still equal this migration's starting state; omit that
option on a transferred copy or after a later approved commit.

Runtime receipts are [smoke_after.json](smoke_after.json),
[models_before.json](models_before.json), [models_after.json](models_after.json),
[predictions_before.json](predictions_before.json) and
[predictions_after.json](predictions_after.json). They record:

- 21 successful runtime checks: five original unit tests, five artifact-path tests,
  canonical/legacy imports, both generations' CLI help, seven preparation-script
  help commands, isolated configuration roots, and six bundled artifact lookups.
- All 122 serialized files tested in isolated subprocesses; 121 load before and
  after. Types, dictionary keys, warnings and the one failure are unchanged.
- Four fixed synthetic-input prediction probes agree within `1e-12` absolute error.
Three are byte-identical; the threshold-time forest differs by approximately
  `3.55e-15`, consistent with floating-point reduction roundoff. These are smoke
  probes, not new scientific results or a full model-validation study.

The final preservation check **passed**: 16,167 unedited research/source/document
files are byte-identical, 34 source/guide edits are recorded, and one live IDE
workspace file is reported separately. Both v3 PDFs and all data, configs, models,
metrics, figures and saved scientific outputs retain their original bytes.
See [verification_full.json](verification_full.json).
It checks every pre-existing regular file against the immediately pre-rename
inventory, allowing the 34 explicitly recorded source/guide edits and separately reporting
mutable IDE session metadata. Python AST checks
compare existing code after normalizing folder names and the tested path resolver.
All 166 original Python files parse; the 20 edited Python files pass the normalized
syntax-tree comparison. Model calculations must otherwise remain unchanged. Current guide links and static
TeX input/figure paths are checked without rebuilding the reports.

## Remaining limitations

`image_embeddings/artifacts/tabular_preprocessor.joblib` still cannot load because
its saved scikit-learn `_RemainderColsList` class is missing in this environment.
The same failure occurred before migration; the embedding API remains blocked by
it. Other version warnings also predate the rename. Successful loading does not
establish the historical training environment.

Existing scientific source/config defects remain listed in
[known issues](../../docs/known_issues.md). End-to-end historical training was not
validated. External jobs using the old relative names need the compatibility links;
absolute paths to a different computer still need that computer's own path setup.

## Preservation and review

[files_before.json](files_before.json) records 16,202 regular files, totaling
48,954,519,903 bytes. [edited_files.json](edited_files.json) records original and
current hashes for every modified existing file; `source_before/` retains its
original text. Old source-hash ledgers were not rewritten to make edited code appear
unchanged. [added_files.json](added_files.json) records new static files; rerunnable verification
and runtime receipts are reported separately.

The ignored `.idea/workspace.xml` changed during this work and was left untouched.
Its before/observed hashes are in [incidental_changes.json](incidental_changes.json).
The verifier reports this live IDE metadata separately from research preservation.

The fresh source/document backup is outside the repository at
`../corrosion_pre_rename_sources_20260916.tar.gz`. Data and saved research outputs
were moved in place. The prior full cleanup backup is older than the selected
v3-only delivery and is not a current-layout backup.

All changes are left for review. Since nothing was staged, Git may display old
paths as deletions and new directories as untracked; the move manifest and byte
checks establish their relocation. Scientific files were not deleted. No staging, commit, push, merge, tag, rebase,
amendment, branch deletion or remote modification was performed. The baseline Git
state is [git_before.json](git_before.json); the final verifier checks it directly.

# Clean research root: removal of old folder shortcuts

The seven old root symlinks (`main_first`, `main`, `main_2`, `main_3`, `main_4`,
`main_4_old`, and `augmentation`) have been removed. Their seven destination
directories remain intact. No real research directory or scientific file was deleted.
The 25 existing links to archived documents remain usable.

[Folder map and current commands](../../docs/folder_migration.md)

## Dependencies updated

`research_paths.resolve_project_path` translates a historical repository path to
the current directory. It maps only the first component, preserves names embedded
inside archive/export trees, and rejects paths outside this checkout. The two
report readers that consume saved path records now use it. Frozen provenance,
manifests, report sources, PDFs, and saved scientific outputs were not rewritten.

The current smoke/model checks use the descriptive packages and folders. Current
READMEs and handoff guides describe the root without the old aliases. The old
`corrosion.main*` module commands must be replaced with their documented new names;
no legacy package shim is installed. Historical manuscript citations and archived
links can be located through the folder map or this read-only command:

```bash
python research_paths.py "main_4/outputs/data/master_table.csv"
```

## Verification

- All 274 previously resolvable historical path records still reach their mapped
  files after removing the aliases. The audit also records 32 pre-existing entries
  that do not represent a currently available exact path; many are explanatory
  prose containing a path. None became unavailable because of this cleanup.
- All 17 current runtime checks pass, including 12 path-resolution unit tests,
  the five original condition-assessment tests, imports, help commands, configuration
  roots, and bundled artifact lookup. Retired legacy-import checks were removed.
- All 122 serialized artifacts were rechecked with the aliases absent. The same
  121 load; the embedding preprocessor's existing scikit-learn incompatibility is
  unchanged. Warnings and loaded types are compared with the original receipts.
- Four fixed-input prediction probes are compared with the original results using
  an absolute tolerance of `1e-12`; floating-point reduction roundoff is allowed.
- The full verifier checks scientific bytes against the pre-rename inventory and
  all 16,265 regular files against the immediately pre-removal inventory. Only
  backed-up source/guide/check-record changes are allowed; live IDE/Finder metadata
  are reported separately. All other regular files must retain their hashes.

The current verification records are
[full](../renaming/verification_full.json) and [quick](../renaming/verification_quick.json).
The direct dependency check is [references_resolved_after.json](references_resolved_after.json).
The preserved scientific defects and environment limitations remain documented in
[known issues](../../docs/known_issues.md). No model training, data regeneration,
figure regeneration or PDF build was run.

From the repository root:

```bash
python report_cleanup/alias_removal/check_dependencies.py after
python report_cleanup/renaming/verify_renaming.py --quick
python report_cleanup/renaming/verify_renaming.py --full --check-git
```

Use `--check-git` only while reviewing this uncommitted change in the original
checkout; it requires the original HEAD, branch, refs and index. A transferred copy
can use the verifier without that flag.

## Evidence and recovery

[removed_links.json](removed_links.json) records the exact seven removed links and
their targets. [files_before.json](files_before.json) records the immediately prior
file inventory. `source_before/` preserves previous versions of edited source,
guides, and check records, including the preceding stage's verification results.
The existing historical structural baseline remains at
`archive/structural_baseline_snapshot/`.

To reverse just this cleanup, recreate only the seven recorded relative symlinks
if those names remain unoccupied, and restore this stage's backed-up source/guide
versions after checking for later work. Do not overwrite unrelated changes.

No staging, commit, push, merge, tag, rebase, amendment, branch deletion or remote
modification was performed. The Git index and refs are checked against the saved
starting state. All changes remain available for review.

The root `.DS_Store` is Finder folder-view metadata. Its hash differs from the
original rename baseline, but equals the immediately pre-removal hash. It was left
untouched; see [the recorded comparison](finder_metadata_note.json).

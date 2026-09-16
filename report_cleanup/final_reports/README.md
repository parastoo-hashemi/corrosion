# Final-report layout and build cleanup

Date: 16 September 2026. The user requested a simpler final-report package while
keeping editable LaTeX sources, bibliography, figures, tables and scientific work.

## Current layout

[final_reports/](../../final_reports/README.md) contains the unchanged delivered
[thesis.pdf](../../final_reports/thesis.pdf) and [article.pdf](../../final_reports/article.pdf).
Editable manuscripts live under `sources/thesis/` and `sources/article/`; shared
`figures/`, `tables/`, `references/` and `scripts/` remain at the package level.
One `records/` link points to the preserved manuscript archive.

The two source masters remain two directory levels below the shared assets, so
all LaTeX source bytes, including their relative dependencies, are unchanged.
Future compilation writes PDFs beside their sources; the root delivery PDFs
should be replaced only after reviewing those new builds.

## Removed material

- **28 generated LaTeX files**: `.aux`, `.bbl`, `.blg`, `.fdb_latexmk`, `.fls`,
  `.log`, `.out`, `.toc`, `.lof` and `.lot`. The `.tex` and `.bib` inputs are retained.
- **One 200-byte placeholder README** in the otherwise empty thesis-local figure
  directory. Its direction to the shared figures is included in the current guides.
- **Seven archive shortcuts**, consolidated into `final_reports/records/`.
  Their target files were retained unchanged.
- **11 emptied old directories**, including the redundant v3 layers and the
  old `report_v2/` root.

The [manifest](manifest.json) lists each moved file, removed build/pointer file
and removed shortcut. No scientific figure, numerical table, PDF manuscript,
bibliography, manuscript chapter or analysis script was deleted. Five scientific
scripts received path-only edits; no scientific calculation was changed or run.

## Backup and recovery

Before changing the layout, the complete report package, manuscript archive and
files planned for editing were saved outside the repository:

```text
../corrosion_reports_before_final_layout_20260916_153201.tar.gz
```

SHA-256:

```text
d233cb39f8fa9db66c5b435d7a64e64b59004ac0e4d9448882694fda398f181f
```

The archive contains verified copies of all 383 backed-up regular files and
preserves the original seven report links. To recover, check that checksum and
extract into a **new empty directory**, then inspect before restoring any paths.
Keep this external backup alongside the project handoff.

## Validation records

- [before.json](before.json): original file/link inventory, archive hashes and Git state.
- [modified_before.json](modified_before.json): pre-edit hashes of guides, helpers,
  scientific scripts and maintenance bookkeeping.
- [source_before/](source_before/): exact pre-edit text copies for review/recovery.
- [verification.json](verification.json): preserved-content hashes, path-only script
  comparison, historical paths, link checks and Git-state comparison.
- [Full repository verification](../renaming/verification_full.json): broader
  preservation checks accounting for these documented moves and removals.

Historic manifests and manuscript path citations retain their recorded names.
The root resolver maps those references to current paths. The prior
[navigation-only record](../report_navigation/README.md) describes the preceding
step; its links now point to the current guides.

No LaTeX rebuild, figure generation or model experiment was run. Nothing was
staged, committed, pushed, merged, tagged or otherwise changed in Git's index or history.

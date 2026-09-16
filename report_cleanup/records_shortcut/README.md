# Manuscript records shortcut removal

The `final_reports/records` symbolic link was removed after its live dependencies
were redirected to [the existing manuscript archive](../../archive/agent_working_notes/report_v2/).
No archive directory or regular research file was deleted or moved.

## Changes

- Four scientific scripts now use direct archive paths for evidence and QA files.
  An AST comparison confirmed that only paths changed; calculations are unchanged.
- Current report guides and the migration guide link directly to the archive.
- `research_paths.py` resolves historical report audit paths and former
  `final_reports/records/` paths without requiring a physical shortcut.
- The maintenance verifier checks the shortcut's absence and the archive's presence.
  The earlier layout manifest remains an unchanged historical record.

The delivered PDFs, LaTeX sources, bibliography, figures, numerical tables and
saved provenance were preserved. All 241 archive files were checked by SHA-256.
No scientific generation scripts or manuscript builds were run during this step.

## Verification and existing drift

[before.json](before.json) records the files and Git state at the start of this step.
[dependency_checks.json](dependency_checks.json) records script comparisons and
archive output paths. The existing path tests also cover operation without the link.

[The older verification snapshot](legacy_verification_before.json) already reported
regenerated build files under `out/chapters/`, changes to `.gitignore` and the two
PyCharm run configurations, and Git state different from its original baseline.
These unrelated changes were not modified or accepted into that older baseline.
This step instead checks preservation against its own fresh snapshot, including
Git HEAD, refs and index. No staging or Git-history operations were performed.

## Recovery

The exact pre-edit texts are in [source_before/](source_before/). An external
backup contains those 16 files plus the symbolic link itself:

```text
../corrosion_before_records_shortcut_removal_20260916_185251.tar.gz
```

SHA-256: `60f19ef18361af4398c8a25f9d64c9da8a38bb0652ebc032e9fd052fa79fcb68`.

The [manifest](manifest.json) records the removed link and its exact target.
The archive already remains in place. To undo this step, restore the edited files
from this backup and recreate the recorded symbolic link in an isolated copy first.
The earlier [complete report/archive backup](../final_reports/README.md) remains available.

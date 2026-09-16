# Selected-results preservation record

Date: 16 September 2026. Scope: organize the user's selected figures and papers
for a research handoff while preserving the complete collection.

## Changes

| Former directory | Current directory |
|---|---|
| `emiling/` | [selected_results/](../../selected_results/README.md) |
| `emiling/main_3/` | [condition_assessment selection](../../selected_results/condition_assessment/README.md) |
| `emiling/main_4/` | [structural_capacity selection](../../selected_results/structural_capacity/README.md) |

The 28 PNG figures, two PDF papers and one Finder metadata file were moved
unchanged. The nested `metadata_only+Ridge/` folder and research filenames were
retained. The collection contains real copies, including intentional duplicates
of experiment/export files. No research file was removed, regenerated or replaced
with a symlink.

Three indexes now explain the selected results and their limits. Current entry
guides and the export audit link to the new locations. The root path resolver
maps historical `emiling/` citations; frozen scientific reports and inventories
retain their original paths. Path tests and the preservation verifier were
updated to cover the relocation.

## Verified backup and recovery

The original collection was archived **before moving it** outside the repository:

```text
../corrosion_selected_results_before_reorganization_20260916_145900.tar.gz
```

SHA-256:

```text
bc0db26718842526b017fee1941ff553c4c4064ca0ca326371a450d3ccd255ba
```

The archive is 8,696,768 bytes. Its 31 regular files and four directory entries
were verified against the original collection before relocation. Keep this
archive alongside the handoff and copy it to a separate backup location.
A repository-only copy does not include this external archive.

To recover the original layout, first verify the archive checksum, then extract
it into a **new, empty recovery directory**. It contains an `emiling/` root.
Compare it with the current selection before any replacement; do not extract
over the working repository.

## Evidence and checks

- [before.json](before.json): original file hashes/sizes, directories and Git state.
- [move_manifest.json](move_manifest.json): exact old/new paths and backup identity.
- [modified_before.json](modified_before.json): pre-edit hashes of the guides,
  resolver, tests and preservation bookkeeping touched by this task.
- [Research provenance manifest](../../selected_results/manifest.json): all 30
  research files and exact matching copies elsewhere in the repository.
- [verification.json](verification.json): collection hashes, archive verification,
  index coverage, local links, historical paths and Git state.
- [Full preservation check](../renaming/verification_full.json): repository-wide
  checks, including original research files at their relocated paths.

The verification is read-only apart from its JSON receipts. Model training and
figure generation were not rerun. No file was staged, and Git history, refs and
the index were unchanged. New local files still require an explicitly approved
tracking/commit step; this task performed neither.

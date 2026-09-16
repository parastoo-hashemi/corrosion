# Report-folder navigation update

Date: 16 September 2026. Scope: make `report_v2/` easier to understand while
preserving the current v3 thesis and article and their dependencies.

## What changed

- Rewrote the [report entry guide](../../report_v2/README.md) with direct PDF links,
  reading routes, a folder map and an explanation of the retained `report_v2` name.
- Added [article](../../report_v2/article/README.md) and
  [thesis](../../report_v2/thesis/README.md) guides outside the v3 trees.
- Added indexes for [figures](../../report_v2/figures/README.md),
  [tables](../../report_v2/tables/README.md) and
  [references](../../report_v2/references/README.md).
- Expanded the [script guide](../../report_v2/scripts/README.md) to identify outputs
  and writes through archive links.
- Included the new guides in the existing maintenance link checker.

No folder or asset was moved, renamed or deleted. Of 117 pre-existing regular
files under `report_v2/`, only its root and script READMEs were edited. The other
115 files, all seven symbolic links and 237 regular files reached through those
links were checked against their pre-edit identities. All 45 regular files within
the two v3 trees remain unchanged, including build records. Shared figures,
tables, bibliography and scientific Python scripts also remain unchanged.

## Evidence and recovery

- [before.json](before.json): file hashes, directory/link inventory, linked archive
  file hashes and original Git state.
- [modified_before.json](modified_before.json): hashes of the two edited guides
  and maintenance bookkeeping before this update.
- [Original report guide](source_before/report_v2/README.md) and
  [original script guide](source_before/report_v2/scripts/README.md): exact pre-edit
  copies, retained for recovery rather than current navigation.
- [verification.json](verification.json): preservation, link and coverage checks.
- [Current maintenance check](../renaming/verification_quick.json): existing
  repository checks, extended to the new guide links.

The saved README copies contain their original relative links; read them as
historical text or restore them to their original locations before following links.
No manuscript compilation, scientific script execution or model experiment was
performed. No staging, commit, push or other Git-history/index operation occurred.

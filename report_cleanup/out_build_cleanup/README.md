# Build-file cleanup in `out/`

Completed on 16 September 2026 following the user's instruction to clean build
files safely. The scope was the generated build files and empty scaffolding
identified in the [preceding audit](../out_audit/README.md).

## Result

- Removed exactly 36 audited LaTeX build files: 20 `.aux`, 5 `.log`,
  5 `.synctex.gz`, 2 `.out`, 2 `.toc`, 1 `.bbl` and 1 `.blg`.
- Removed 149 empty subdirectories using empty-directory removal only. This
  includes 147 previously empty subdirectories and `chapters/` and `mainreport/`,
  which became empty after their `.aux` files were removed.
- Removed file bytes total 1,354,215 (1.35 MB); this is logical file size, not
  measured filesystem space reclaimed.
- Preserved all six PDFs in [out/](../../out) at their original paths, with
  matching SHA-256 hashes. No document deduplication or PDF revision was performed.
- Kept the Git index, branch, HEAD and refs unchanged. The tracked build files
  now appear as unstaged deletions. Nothing was staged, committed or pushed.

## Verified recovery backup

The complete pre-cleanup `out/` tree is stored outside the repository, in its
parent directory:

```text
corrosion_out_before_build_cleanup_20260916_104012.tar.gz
SHA-256: 63260d1f82b9971a0b4984d167cd9d4719fa6ad0953d8731358eba387863cd39
```

Before any deletion, all 42 archived file hashes and the complete directory tree
were verified against the live files. The archive contains six PDFs, all removed
build files (including unique historical compiler logs), and 150 directory
entries including the `out/` root. Its size is 20,581,847 bytes.

For recovery, verify the archive hash and extract it into a new, empty recovery
directory. Copy back only the desired files after comparison; avoid extracting
over the current repository. The backup is deliberately outside Git and should
be transferred separately if the recipient needs the removed build records.
The research handoff and current verifier can operate without this optional
external recovery archive.

## Preservation records

- [Pre-cleanup file/directory and Git state](before.json)
- [Verified archive record](backup_verification.json)
- [Exact removal manifest and preserved PDF hashes](removal_manifest.json)
- [Hashes of maintenance files before updates](modified_before.json)
- [Post-cleanup verification](verification.json)

The original audit inventory and verification receipt remain unchanged as
historical snapshots. Its README now points to this completed cleanup. The root
README describes the six remaining PDFs.

The current [handoff verifier](../renaming/verify_renaming.py) now recognizes only
the explicitly audited build removals, checks their identities against the
original baselines, verifies all six preserved PDF hashes, and verifies the
external archive hash when that backup is present. Original preservation
inventories were not rewritten to hide removals.

Run from the repository root:

```bash
python report_cleanup/renaming/verify_renaming.py --quick
```

The `--full` mode also hashes the remaining baseline research files. Add
`--check-git` only in this original checkout while reviewing the unstaged
migration; it requires the original branch, refs and index to remain unchanged.

Historical audit reference lists can still mention the removed build paths;
their contents are recoverable from the backup. Current PDF paths are unchanged.

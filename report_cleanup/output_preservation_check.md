# Output preservation check

## Result

**PASS: all 15,566 protected scientific input/output files
match their pre-cleanup sizes and SHA-256 hashes. Zero output differences.**
No model was retrained, scientific artifact regenerated, or manuscript source/PDF
rebuilt. Logged moves change storage paths only; compatibility links preserve
required old lookup paths.

The inventory is deliberately broad: raw/augmented images, workbooks, compressed
datasets, models, CSV/JSON/parquet/TSV, manifests, figures, PDFs, TeX/Bib sources,
and generated experiment/data documentation. It covers 48,917,480,102 bytes.
It includes inputs as well as generated outputs, and some preserved auxiliary
JSON; it is not a claim that every listed file is an independent result.

## Snapshots and diff

- [Before: path, size, SHA-256](outputs_before.json)
- [After: original path, current path, size, SHA-256](outputs_after.json)
- [Machine-readable differences](output_preservation_diff.json): empty list
- [Per-file move mapping](move_manifest.csv): 329 preserved files, no deletion
- [Complete pre-cleanup inventory](all_files_before.json)
- [Complete post-cleanup original-file comparison](all_files_after.json)
- [Full verification record](verification_full.json)
- [Seven report PDF checks](report_pdf_preservation.json)

The full original-file comparison checked 16,131 files.
Eight Python files are intentionally documented; their ASTs and executable tokens
are identical after removing docstrings/comments/layout. `.gitignore` is the other
intentional original-file edit. Replaced README/agent-guide originals were archived
and hash-checked rather than excluded. The user's already-staged prompt deletion
was preserved in place, with original Git content recovered in the archive and
verified separately.

## One non-scientific local state exception

`.idea/workspace.xml` differed from the starting snapshot during this task. It is
untracked local IDE state, not a scientific output, and no cleanup action targets
it. Its current copy was left untouched; the initial copy remains in the full
backup. [Exact before/after record](local_state_drift.json) discloses the difference.
The [initial full check](verification_initial_full.json) reported it as a failure;
the final verifier distinguishes this disclosed local state drift from scientific
preservation failures. No other unexplained original-file changes were found.

## Functional checks

- All 169 pre-existing Python files parse; eight touched files compile and have
  identical executable tokens/ASTs after excluding docstrings/comments/layout.
- Five touched main_4 modules import; six configs load through the actual loader.
  The touched main_3 split module imports independently; both touched augmentation
  scripts import successfully while showing `--help`.
- All 12 YAML/TOML configs parse and have unchanged hashes. The existing NO→False
  category and main_first scalar defects remain recorded, not repaired.
- Three augmentation CLI help commands succeed; current docs link to accurate flags.
- 26 compatibility links and 131 curated documentation links resolve.
- 120 LaTeX includes, shared table/bibliography inputs and figure references resolve;
  literal full repository paths in the report sources still resolve.
- All 96 checked historical source-hash records still match.
- The existing main_3 specimen-grouping unit test passes (one test, no model fitting).
- New source/current-guide diffs pass whitespace checks. Raw search evidence and
  an archived README retain original whitespace; they were not reformatted.

## Re-run

From the repository root:

```bash
/opt/anaconda3/envs/env/bin/python -B report_cleanup/verify_delivery.py --full
```

This hashes the full preserved dataset and writes only cleanup verification records.
`--quick` skips the large-file pass. Neither mode proves an end-to-end historical
training rerun; documented source/config and environment limits still apply.

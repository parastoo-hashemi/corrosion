# Audit of `out/`

**Subsequent cleanup:** the 36 build files and 149 subdirectories were removed
after a verified backup; all six PDFs remain unchanged. See the
[build cleanup record](../out_build_cleanup/README.md). The findings and counts
below describe the preserved pre-cleanup audit snapshot. The selected copies
formerly in `emiling/` now live in [selected_results](../../selected_results/README.md);
the two PDF links below point to their new locations. Both copies are intentionally
retained as part of that curated collection.

Audit date: 16 September 2026. Scope: identify build products, duplicates and
historical research documents before any removal. **No files in `out/` were
removed, moved, renamed or rewritten. No Git index or history changes were made.**

## Findings

`out/` is a historical document-build/export directory. It contains **42 regular
files, totalling 21,362,166 bytes (21.36 MB)**, and 149 subdirectories. It contains
no Python source, datasets, fitted models, configurations or standalone result
tables. Its experiment-like directory names are empty scaffolding.

| Category | Files | Suggested future treatment |
|---|---:|---|
| LaTeX build products | 36 | Cleanup candidates after a verified backup and preservation-ledger update |
| PDFs with byte-identical copies outside `out/` | 2 | Keep one verified copy of each document; update path references before removing either location |
| Additional PDF copy with equivalent tested content | 1 | Keep the original seven-page PDF; redundant copy is a cleanup candidate |
| Historical documents requiring preservation | 2 | Retain; consider a clearly labelled historical-document archive |
| Incomplete augmentation-document variant | 1 | Retain pending version review; use the current classification document for the handoff |

All 42 files are currently tracked in the Git index. The 36 build products also
match ignore rules, which does not untrack existing files. This audit changes
neither their tracked state nor the existing unstaged repository migration.

## The six PDFs

### 1. Seven-page corrosion/feasibility paper: retain a historical copy

- [Original PDF](../../out/1_corrosion_condition_pipeline_ieee.tex.pdf): 7 pages,
  647,124 bytes.
- [Additional copy](../../out/1_corrosion_condition_pipeline_ieee.tex copy.pdf):
  7 pages, 650,188 bytes.
- Title: *From Repeated Corrosion Images to Proxy Remaining Useful Life: An
  Interpretable Feasibility Pipeline for Ferrocement Specimens*.
- Neither binary has an exact match elsewhere in the current working tree.
- The two files have identical normalized extracted text, identical decoded
  content streams for all seven pages, and identical RGB page renders at 100 dpi.
  Neither contains annotations, form fields or embedded attachments. Their binary
  hashes and producer/modification metadata differ. This establishes equivalent
  tested document content, not byte identity.
- The build log names the historical source
  `main_3/reports/1_corrosion_condition_pipeline_ieee.tex.tex`; that source is absent
  from the current working tree. The seven-page paper differs from the later
  eight-page paper below.

**Recommendation:** preserve the original as a historical draft. The extra
`copy.pdf` is a candidate for later removal after backing it up.

### 2. Activity report: unique local historical document

- [PDF](../../out/activity_report.pdf): 70 pages, 1,195,126 bytes.
- Title: *Technical Activity Report: A Multi-Phase Investigation of Visible
  Corrosion and Structural Condition in Ferrocement Specimens*.
- The cover explicitly marks it as a draft working document, not for distribution.
- Its abstract, executive summary and contents document the project phases,
  dataset audit, integrated results, limitations and continuation plan.
- No byte-identical or normalized-text-identical PDF exists elsewhere in the
  current repository. The logged source, `activity_report/activity_report.tex`,
  is absent from the working tree.
- This is a retained historical synthesis, not a newly discovered experiment or
  an alternative current final report. The delivered thesis and article remain
  under `report_v2/thesis/v3/` and `report_v2/article/v3/`.

**Recommendation:** preserve and label as historical. Current documentation saying
the original activity report was removed from the working tree needs qualification:
its former source directory was removed, but this compiled copy remains in `out/`.

### 3. Augmentation methodology: incomplete build variant

- [PDF in out](../../out/augmentation_methodology_final.pdf): 22 pages,
  16,395,919 bytes; about 77% of `out/`'s file bytes.
- [Current classification PDF](../../classification_data_preparation/augmentation_methodology_final.pdf):
  21 pages, with [retained TeX source](../../classification_data_preparation/augmentation_methodology_final.tex).
- The `out/` copy has an empty contents page, 21 extracted `??` cross-reference
  placeholders, unresolved citations and an overflowing file path on page 2.
  The associated build log records unresolved references and a request to rerun
  LaTeX. Visual inspection confirmed the page-2 defects.
- The current classification PDF has populated contents, zero extracted `??`
  placeholders, and resolved table references on the compared page. Pagination,
  wording and formatting differ between the PDFs.
- The log points to the former
  `Documentation/augmentation_methodology_final.tex` source location.

**Recommendation:** classify the `out/` copy as an incomplete historical build
variant, not an exact duplicate. Retain until any uniquely worded material has
been reviewed or the entire variant has been archived. The current classification
PDF is the appropriate existing handoff entry; this audit does not certify its
scientific claims or all of its pages.

### 4. Eight-page corrosion/condition paper: exact export duplicate

- [PDF in out](../../out/corrosion_condition_pipeline_ieee.pdf): 8 pages,
  749,962 bytes.
- Exact SHA-256 match:
  [selected condition-assessment paper](../../selected_results/condition_assessment/corrosion_condition_pipeline_ieee.pdf).
- The [condition-assessment PDF](../../condition_assessment/reports/corrosion_condition_pipeline_ieee.pdf)
  is a different build/version, with differences including author information,
  extracted caption text and a cross-reference. It must not be substituted on
  the assumption of byte equivalence.

**Current decision:** retain both exact export copies. The selected copy belongs
to the user's curated results collection; a duplicate hash is not a deletion request.

### 5. Five-page terminal-load paper: exact export duplicate

- [PDF in out](../../out/ultimate_load_refocus_ieee.pdf): 5 pages, 369,632 bytes.
- Exact SHA-256 match:
  [selected terminal-load paper](../../selected_results/structural_capacity/ultimate_load_refocus_ieee.pdf).
- The [structural-capacity PDF](../../structural_capacity/outputs/reports/ultimate_load_refocus_ieee.pdf)
  has different bytes and extracted text/layout. It is not the verified exact
  duplicate. The associated TeX source remains in the structural report directory.

**Current decision:** retain both exact export copies. The current five-page v3
article is a different document.

## Build products and empty directories

The 36 build files total **1,354,215 bytes (1.35 MB)**:

| Type | Count | Role |
|---|---:|---|
| `.aux` | 20 | LaTeX labels, citations and cross-reference state |
| `.log` | 5 | Compiler output and historical source/build paths |
| `.synctex.gz` | 5 | Editor-to-PDF source synchronization |
| `.out` | 2 | PDF bookmark/build state |
| `.toc` | 2 | Generated contents entries |
| `.bbl` | 1 | Generated bibliography for the activity report |
| `.blg` | 1 | Bibliography build log |

These are generated documents and compiler state, not raw scientific observations.
Some contain unique build provenance. Because some historical sources are absent,
this audit does not assume every auxiliary file can currently be regenerated.
Back up the complete small `out/` package before any future removal.

There are **147 subdirectories containing no files, including their descendants**.
They form 15 non-overlapping empty trees directly under `out/`: `Conferences/`,
`Data/`, `Documentation/`, `Thesis/`, `__pycache__/`, `catboost_info/`, `codex/`,
`configs/`, `figures/`, `frontmatter/`, `notes/`, `outputs/`, `references/`, `src/`
and `tables/`. The other two subdirectories, `chapters/` and `mainreport/`, contain
only `.aux` files. No symlinks were found inside `out/`.

## Dependencies and limits

- The root README links to `out/`; historical planning/evidence documents also
  cite its PDFs. Any later relocation should preserve traceability and repair
  current links.
- Static searches found no current modelling or manuscript-build source that
  literally uses root `out/` as an input/output path. This is a bounded search,
  not proof about dynamically constructed paths or external editor settings.
- `report_v2/scripts/audit_saved_figures.py` reads the PDFs in the condition and
  structural report directories, not the copies in `out/`.
- The current preservation verifier expects all 42 files through its original
  baseline inventory. An authorized removal or move must be recorded explicitly;
  it should not be hidden by rewriting the original inventory.
- Exact duplicate search covered **16,301 regular files** in the local repository,
  including ignored data. Git internals and symlinks were excluded. Size filtering
  reduced fresh SHA-256 hashing to 46 files, including the 42 `out/` files.
- All 42 local PDFs were text-extracted to look for matching documents. The six
  `out/` covers and the relevant augmentation comparison page were visually
  inspected; all seven pages of the additional copy were compared as raster data.
- Local uniqueness means no matching local document was found. It does not imply
  unique experimental findings, no version in Git history, or scientific validity.

## Evidence and future cleanup order

- [File-by-file inventory, hashes, classifications and empty directories](inventory.json)
- [PDF metadata, exact-text matches, content/render comparisons and version differences](pdf_comparisons.json)
- [Reference search and dependency interpretation](references.json)
- [Post-audit preservation and Git check](verification.json)

Recommended future order: preserve a verified backup; remove approved build
products/empty scaffolding; consolidate exact/equivalent copies while retaining
their identified counterparts; archive the historical PDFs; review the incomplete
augmentation variant separately. The first two file-cleanup categories plus the
equivalent copy represent **39 candidates, 3,123,997 bytes (3.12 MB)**. This is a
classification and proposal only: all 42 files and all directories remain present.

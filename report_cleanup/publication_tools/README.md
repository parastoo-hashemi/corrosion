# Optional publication Python tools removed

Eight optional publication/presentation scripts and two redundant Python backup
copies were removed for the professor/teammate handoff. The exact paths, reasons
and pre-deletion hashes are in [removal_manifest.json](removal_manifest.json).

## Removed active scripts

| File | Reason |
|---|---|
| `report_v2/scripts/build_reports.py` | Build wrapper for previously removed v1/v2 drafts. |
| `report_v2/scripts/build_v3_reports.py` | Optional LaTeX wrapper; direct build commands are documented. |
| `report_v2/scripts/render_review.py` | Contact-sheet renderer for previously removed drafts. |
| `report_v2/scripts/render_v3_review.py` | Optional PDF review contact-sheet renderer. |
| `report_v2/scripts/revise_drafts.py` | One-off v1-to-v2 manuscript transformation. |
| `report_v2/scripts/make_bibliography.py` | One-off bibliography assembly; final bibliography and metadata remain. |
| `report_v2/scripts/validate_documents.py` | Obsolete all-draft document QA; assumes manuscripts already removed. |
| `exploratory_prototype/generate_slide_image.py` | Standalone presentation mask with an old Windows input path. |

Two `validate_documents.py` copies under prior `report_cleanup/*/source_before/`
were also removed. Their exact bytes are included in the same external archive.

## Kept because they support the science

- The six [scientific report scripts](../../final_reports/scripts/README.md) preserve
  the numerical audits, paired analysis and figure-reproduction recipes.
- `image_embeddings/report_writer.py` is imported by model training.
- `image_embeddings/build_pdf_report.py` also computes and exports specimen/material
  summary tables, so it retains a historical reproduction role.
- `condition_assessment/scripts/09_generate_reports.py` and its underlying modules
  are part of the research pipeline and produce scientific diagnostic summaries.
- Structural `reporting.py` modules are used by the baseline/improvement runners;
  the historical snapshot retains those dependencies.
- `exploratory_prototype/thesis_report.py` actually trains and evaluates a model.
  Its report-like name is not a reason to remove an experiment.
- Classification preparation/statistics/plotting code remains available.

Data, models, scientific outputs, figures, PDFs, LaTeX and bibliography files were
preserved. Nothing was rebuilt, trained or regenerated during this cleanup.

## Recovery and verification

The removed Python files and pre-edit documentation/checker versions are in a
verified compressed archive **outside the repository**, beside the `corrosion/`
folder. Its exact name and SHA-256 are recorded in the removal manifest. Restore
individual members to a separate folder first and review any later work before
putting a file back. The handoff itself does not require this optional archive.

No remaining active Python imports or filename/module references point to the
removed utilities. Current document links, surviving Python syntax, unit tests,
entry-point imports/help and full preservation hashes are checked by the retained
[delivery verifier](../renaming/verify_renaming.py). It distinguishes these explicit
removals from unexpected missing files. Previous inventories retain their original
entries for traceability; the removal manifest records this later change.

Current check records: [full](../renaming/verification_full.json) and
[quick](../renaming/verification_quick.json). Existing scientific/runtime limitations
remain in [known issues](../../docs/known_issues.md).

No files were staged or committed, and no Git refs or remotes were changed.

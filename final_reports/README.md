# Final research reports

The current **v3 thesis and article** are ready to read at the top of this folder.
Their editable LaTeX sources, bibliography, figures, tables and scientific scripts
are kept alongside them for future revisions. This package was formerly `report_v2/`.

## Start here

| Purpose | Open |
|---|---|
| Read the concise account | [Article — 5 pages](article.pdf) |
| Read the full research account | [Thesis — 40 pages](thesis.pdf) |
| Edit the manuscripts | [Thesis sources and chapter map](sources/thesis/README.md) · [Article source guide](sources/article/README.md) |
| Find publication assets | [Figure index](figures/README.md) · [Table index](tables/README.md) |
| Inspect citations | [Bibliography guide](references/README.md) |
| Understand scientific utilities | [Script guide](scripts/README.md) |
| Inspect earlier audits and reviews | [Historical records](records/) |

## Folder layout

```text
final_reports/
├── thesis.pdf
├── article.pdf
├── README.md
├── sources/
│   ├── thesis/       thesis.tex, chapters/ and source guide
│   └── article/      article.tex and source guide
├── figures/          Publication PDFs, PNG viewing copies and provenance
├── tables/           Saved numerical results and LaTeX tables
├── references/       Bibliography and citation metadata
├── scripts/          Scientific evidence and figure utilities
└── records/          One link to the preserved manuscript archive
```

The PDFs and every LaTeX source, bibliography entry, figure, numerical table and
saved provenance ledger retain their previous bytes. Only navigation and script
paths were updated. Temporary LaTeX files were removed after a verified backup;
the old version-directory layers and scattered archive shortcuts were consolidated.
See the [cleanup and recovery record](../report_cleanup/final_reports/README.md).

## Future edits

Edit the `.tex` files under `sources/`. Both masters still reference shared assets
through `../..`, so they find this folder's `figures/`, `tables/` and `references/`.
In a separate editing copy, run from the repository root:

```bash
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error final_reports/sources/thesis/thesis.tex
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error final_reports/sources/article/article.tex
```

A build writes its PDF and temporary files beside the corresponding `.tex` master.
Review that PDF before replacing `thesis.pdf` or `article.pdf` at the package root.
The delivered PDFs were not rebuilt during this cleanup. Scientific scripts can
write shared assets and records; consult the script guide before future execution.

`records/` links to [archive/agent_working_notes/report_v2/](../archive/agent_working_notes/report_v2/).
Preserve that archive and the relative link when transferring the full repository.
Historical paths inside saved manuscripts and provenance remain as recorded; the
[folder migration guide](../docs/folder_migration.md) and root `research_paths.py`
resolve them. The [experiment map](../docs/experiments.md), [selected results](../selected_results/README.md)
and [known issues](../docs/known_issues.md) provide the wider research context.

# Research reports — start here

This folder contains the **current v3 article and thesis**, their shared scientific
assets, and links to historical review records. `report_v2` is a retained folder
name; it does not identify the current manuscript version. Existing paths are
kept so manuscript inputs and saved provenance remain valid.

## Read the reports

| Your goal | Open |
|---|---|
| Read the concise scientific account | [Article PDF — v3, 5 pages](article/v3/article.pdf) |
| Read the full methods, results and limitations | [Thesis PDF — v3, 40 pages](thesis/v3/thesis.pdf) |
| Navigate manuscript source files | [Article guide](article/README.md) · [Thesis and chapter guide](thesis/README.md) |
| Find a publication figure and its source | [Figure index](figures/README.md) |
| Inspect saved numbers and table formats | [Table index](tables/README.md) |
| Understand citations and bibliography records | [Reference guide](references/README.md) |
| Understand the retained analysis utilities | [Script guide](scripts/README.md) |

For the wider project, use the [experiment map](../docs/experiments.md) or the
[separate selected-results collection](../selected_results/README.md).

## Folder map

```text
report_v2/
├── article/       Guide and current article in v3/
├── thesis/        Guide and current thesis/chapters in v3/
├── figures/       Shared publication figures, viewing copies and provenance
├── tables/        Saved CSV results and LaTeX presentation files
├── references/    Shared bibliography and stored citation metadata
├── scripts/       Scientific evidence and figure utilities
├── evidence/     Link to archived evidence records
├── qa/           Link to archived quality checks
└── critique/     Link to archived review notes
```

Both manuscripts use `figures/`, `tables/` and `references/` through relative
paths. These shared assets are part of the manuscripts' dependency set. The
clarity update changes navigation documents only: the complete `article/v3/` and
`thesis/v3/` trees, shared scientific assets, scripts and archive records are
preserved. See the [preservation record](../report_cleanup/report_navigation/README.md).

## Historical records

[evidence/](evidence/), [qa/](qa/) and [critique/](critique/) are links to the
[manuscript archive](../archive/agent_working_notes/report_v2/). The root
[FINAL_VERIFICATION.md](FINAL_VERIFICATION.md), [RESEARCH_NOTES.md](RESEARCH_NOTES.md)
and [VERIFICATION_LOG.md](VERIFICATION_LOG.md) are historical records linked to
that archive as well. They document earlier checks and decisions; they are not
fresh verification of the current software environment. Preserve the archive and
relative links when transferring the repository.

Earlier v1/v2 manuscript trees and activity-report source are absent from this
working tree. A historical [70-page activity-report draft](../out/activity_report.pdf)
remains; the [export audit](../report_cleanup/out_audit/README.md) explains its
relationship to the current delivery.

## For future manuscript editing

Reading the existing PDFs requires no build. In a separate editing copy, the
existing build commands are, from the repository root:

```bash
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error report_v2/thesis/v3/thesis.tex
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error report_v2/article/v3/article.tex
```

These commands overwrite compiled files. Scientific scripts also write outputs;
the [script guide](scripts/README.md) identifies where. Optional publication-build
utilities were previously removed; see their [recovery record](../report_cleanup/publication_tools/README.md).
The [environment notes](../docs/reproduction.md) and [known issues](../docs/known_issues.md)
remain available for future work. No build, figure generation or experiment run
was performed for this navigation update.

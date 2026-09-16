# Research manuscripts and report assets

## Which PDF should I read?

The authoritative manuscript version has **not** been selected. The latest produced
alternatives are the [v3 IEEE article](article/v3/article.pdf) (5 pages) and
[v3 thesis](thesis/v3/thesis.pdf) (40 pages). The original
[technical activity report](../activity_report/activity_report.pdf) remains available.
These are research documents for review; production order is not approval status.

| Version | Thesis | IEEE article |
|---|---|---|
| First draft | [44 pages](thesis/thesis.pdf) | [5 pages](article/article.pdf) |
| v2 | [37 pages](thesis/v2/thesis.pdf) | [5 pages](article/v2/article.pdf) |
| v3 | [40 pages](thesis/v3/thesis.pdf) | [5 pages](article/v3/article.pdf) |

Each PDF's LaTeX master and modular sources are beside it. Cleanup changed none of
their bytes, claims, numbers, figures, or bibliography.

## Package map

- [figures/](figures/): shared publication assets and provenance.
- [tables/](tables/): saved full-precision result tables.
- [references/](references/): bibliography and source verification.
- [scripts/](scripts/): reporting/aggregation/build tools; many write outputs.
- [Archived manuscript records](../archive/agent_working_notes/report_v2/):
  prior reviews, evidence, verification, and revision decisions.

The `evidence/`, `qa/`, and `critique/` entries are relative compatibility links to
that archive. Selected old file paths also remain links because scripts or frozen
manuscripts cite them. Keep the archive with this package and preserve the links.
Saved evidence and QA bytes are unchanged.

## Build / verify

From the repository root, in a separate report-editing copy:

```bash
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error report_v2/thesis/v3/thesis.tex
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error report_v2/article/v3/article.tex
```

To check the delivery without rebuilding scientific assets:

```bash
python report_cleanup/verify_delivery.py --quick
```

See [reproduction](../docs/reproduction.md) for environment, full preservation checks,
and commands that overwrite files. Existing saved inputs suffice for compilation;
no model training is needed. Historical model-source defects remain documented in
[known issues](../docs/known_issues.md).

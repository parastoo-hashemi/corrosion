# Research manuscripts and report assets

## Which PDF should I read?

These are the current reports for this project: the
[IEEE article](article/v3/article.pdf) (5 pages) and the
[thesis](thesis/v3/thesis.pdf) (40 pages). Each PDF's LaTeX master and modular
sources are beside it.

The original activity-report source directory and earlier `report_v2` draft
versions (v1, v2) were removed from the working tree. Historical versions remain
in Git history. A compiled 70-page [activity-report draft](../out/activity_report.pdf)
also remains locally; its cover marks it as a working draft. Use the v3 article
and thesis above for the current delivery. The [export audit](../report_cleanup/out_audit/README.md)
distinguishes the historical document variants.

## Package map

- [figures/](figures/): shared publication assets and provenance.
- [tables/](tables/): saved full-precision result tables.
- [references/](references/): bibliography and source verification.
- [Scientific scripts](scripts/README.md): evidence checks, result aggregation and
  reproducible scientific figures. Optional manuscript-build and review utilities
  have been removed.
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
python report_cleanup/renaming/verify_renaming.py --quick
```

See [reproduction](../docs/reproduction.md) for environment, full preservation checks,
and commands that overwrite files. Existing saved inputs suffice for compilation;
no model training is needed. Historical model-source defects remain documented in
[known issues](../docs/known_issues.md).

## Publication-tool cleanup

The final PDFs, LaTeX sources, bibliography, figures and tables are retained.
Use the direct LaTeX commands above to compile edited manuscripts. The removed
Python utilities and their recovery archive are documented in the
[cleanup record](../report_cleanup/publication_tools/README.md).

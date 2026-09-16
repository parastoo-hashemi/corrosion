# Research manuscripts and report assets

## Which PDF should I read?

These are the current reports for this project: the
[IEEE article](article/v3/article.pdf) (5 pages) and the
[thesis](thesis/v3/thesis.pdf) (40 pages). Each PDF's LaTeX master and modular
sources are beside it.

The original activity report and earlier `report_v2` draft versions (v1, v2)
were removed from the working tree once this v3 version was confirmed as the
one to deliver. They are not lost — every byte remains recoverable from Git
history (branches `report-rebuild-codex` and `report-rebuild-codex-v3`) — but
they are no longer part of the delivered copy.

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

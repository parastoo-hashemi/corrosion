# Scientific scripts

These six Python files retain evidence checks, result aggregation and scientific
figure generation. They are not required to read the delivered PDFs. Paths were updated for the final-report layout; scientific logic is unchanged.
No script was executed during this cleanup.

## Purpose and output locations

| Script | Purpose | Files it can write |
|---|---|---|
| [audit_evidence.py](audit_evidence.py) | Checks saved numerical claims, prediction grouping and dataset facts | CSV tables, `archive/agent_working_notes/report_v2/evidence/claims.json`, `archive/agent_working_notes/report_v2/VERIFICATION_LOG.md` |
| [paired_diagnostics.py](paired_diagnostics.py) | Compares saved specimen errors for metadata-only and metadata+HSV Ridge | Paired CSV/LaTeX statistics, paired figure/provenance, `archive/agent_working_notes/report_v2/evidence/paired_diagnostics.json` |
| [make_figures.py](make_figures.py) | Produces the main figures and formatted tables from saved evidence | Shared PDF/PNG figures, LaTeX tables, main provenance and figure-data checks |
| [make_v3_figures.py](make_v3_figures.py) | Produces the three additional v3 Ridge diagnostics from saved results | Ridge PDF/PNG figures, main provenance, `archive/agent_working_notes/report_v2/evidence/v3/new_figure_checks.json` |
| [audit_saved_figures.py](audit_saved_figures.py) | Audits saved figure inputs and replays selected plotting functions | `archive/agent_working_notes/report_v2/qa/v3/` replay outputs and `archive/agent_working_notes/report_v2/evidence/v3/figure_checks.json` |
| [_project_paths.py](_project_paths.py) | Imports the root resolver for historical source paths | Helper; no standalone output |

## Relationship to the manuscripts

The scientific scripts consume saved data/predictions and do not train the main
models. Their outputs can still change manuscript inputs. In particular,
`make_figures.py` rewrites the main provenance files, while `make_v3_figures.py`
adds the v3 entries. Treat them as generation utilities, not read-only viewers.

Evidence and QA paths in the table are relative to the repository root. Figure,
table and provenance outputs remain under `final_reports/`. The scripts access
the [manuscript archive](../../archive/agent_working_notes/report_v2) directly;
running them can overwrite saved audit records. Use a separate complete repository copy
for future execution, including the archive. The [environment notes](../../docs/reproduction.md)
and [known issues](../../docs/known_issues.md) describe existing execution limits;
retaining a script does not certify a new run.

Manuscript compilation uses the direct LaTeX commands in the [report guide](../README.md).
Optional publication-build utilities and the obsolete all-draft checker were
previously removed; their [removal record](../../archive/repository_maintenance/publication_tools/README.md)
explains recovery.

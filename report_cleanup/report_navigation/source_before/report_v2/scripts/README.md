# Scientific scripts retained for the research handoff

These scripts help a teammate check the results and reproduce the scientific
figures. They use saved data and predictions; they are not model-training entry
points. They write outputs, so run them in a separate reproduction copy.

| Script | Why it remains |
|---|---|
| [audit_evidence.py](audit_evidence.py) | Checks numerical claims, saved predictions, grouping and dataset facts; exports audited tables. |
| [paired_diagnostics.py](paired_diagnostics.py) | Computes paired specimen errors and descriptive statistics from saved predictions. |
| [make_figures.py](make_figures.py) | Reproduces the main scientific figures and table formatting from saved evidence. |
| [make_v3_figures.py](make_v3_figures.py) | Reproduces v3 diagnostic figures from the saved Ridge results. |
| [audit_saved_figures.py](audit_saved_figures.py) | Checks saved figure inputs and replays selected plotting functions without fitting models. |
| [_project_paths.py](_project_paths.py) | Resolves historical source paths for the retained figure audit. |

Manuscript compilation uses the direct `latexmk` commands in the
[report guide](../README.md). One-off publication utilities and the obsolete
all-draft checker have been removed; see the
[removal record](../../report_cleanup/publication_tools/README.md).

The preserved source/config defects and historical provenance limits remain
listed in [known issues](../../docs/known_issues.md). Retaining a script is not
certification that an entire historical experiment can run in today's environment.

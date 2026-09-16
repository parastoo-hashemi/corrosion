# Maintainer entry guide

Read [README.md](README.md), [reproduction](docs/reproduction.md), and
[known issues](docs/known_issues.md) before changing this research repository.

The most mature saved structural experiment is in `structural_capacity/`; the separate
`classification_data_preparation/` workstream has completed four-class data preparation only.
Neither current modelling source nor historical plans establish a validated rerun.
The delivered manuscripts are the v3 thesis and article in `report_v2/`.

Keep specimen-level split boundaries, target units, terminal evaluation scope, and
the distinction between observed and model-estimated quantities explicit. Do not
silently alter saved data, metrics, predictions, models, figures or report claims.
Code/config repairs and new training require a separate intentional task and
results namespace. Existing main_first substitutions and YAML NO coercion are
unresolved; no broad replacement is safe.

Source directories use the descriptive names listed in [the migration guide](docs/folder_migration.md).
The old root aliases have been removed. Retain the archive-document links and
use `research_paths.resolve_project_path` when reading historical repository paths. Use the current
`report_cleanup/renaming/verify_renaming.py` checker for this layout. The original longer agent guide is preserved in
[the development archive](archive/agent_working_notes/CLAUDE.md).

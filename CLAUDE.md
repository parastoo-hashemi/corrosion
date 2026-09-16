# Maintainer entry guide

Read [README.md](README.md), [reproduction](docs/reproduction.md), and
[known issues](docs/known_issues.md) before changing this research repository.

The most mature saved structural experiment is in `main_4/`; the separate
`augmentation/` workstream has completed four-class data preparation only.
Neither current modelling source nor historical plans establish a validated rerun.
The authoritative manuscript version is undecided.

Keep specimen-level split boundaries, target units, terminal evaluation scope, and
the distinction between observed and model-estimated quantities explicit. Do not
silently alter saved data, metrics, predictions, models, figures or report claims.
Code/config repairs and new training require a separate intentional task and
results namespace. Existing main_first substitutions and YAML NO coercion are
unresolved; no broad replacement is safe.

Historical source directories retain their names. Archive compatibility links must
remain usable. The original longer agent guide is preserved in
[the development archive](archive/agent_working_notes/CLAUDE.md).

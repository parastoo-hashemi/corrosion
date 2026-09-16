# Log policy

Generated `.log` files, numbered rotations, compressed `.log.gz` files and the
Matplotlib cache under `logs/.mpl/` are ignored by default. Metrics, predictions,
split manifests, configs and environment records are not covered by these rules.

Nine exact historical filenames are exceptions:

| Location | Records retained | Why |
|---|---|---|
| `condition_assessment/logs/` | `run_all.log`, `07_fit_degradation_models.log` | Earlier pipeline progress and specimen-level degradation fitting. The partial run log does not establish completion. |
| `structural_capacity/outputs/logs/` | `run_ultimate_load_refocus.log` | Chronology and settings/output locations of the focused terminal-load study. |
| `archive/structural_baseline_snapshot/outputs/logs/` | `run_audit_validation.log`, `run_full_baseline.log`, `train_surface_models.log`, `train_hidden_damage_models.log`, `train_degradation_models.log`, `train_rul_proxy_models.log` | Historical audit, execution, model-selection and threshold-status records. |

The six selected archived baseline logs are byte-identical to their counterparts
in `structural_capacity/outputs/logs/`. The archive copies are the exceptions;
the duplicate active-directory logs follow the default ignore rule.

Preserve these named records as historical evidence. Run new experiments in a
separate output directory, as described in [reproduction](reproduction.md). New
log filenames are ignored unless deliberately added to the exception list.
Logs support chronology and interpretation; they do not by themselves validate
the scientific results or current source code.

This policy change does not delete log files or untrack existing Git entries.
Already tracked logs remain tracked until an explicitly approved index change.
No staging, commit or push was performed.

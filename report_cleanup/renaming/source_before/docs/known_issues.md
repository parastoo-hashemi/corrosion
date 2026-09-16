# Known issues requiring future work

This is the unresolved status at handoff. Cleanup did not repair scientific code,
change configs, retrain models, or revise report claims.

## Current modelling source cannot be treated as a verified rerun

The existing report documents widespread `main_first` text substitutions in older
Python/config sources, including aggregation names and values expected to be
numeric. Python can parse a module while those expressions still fail at runtime.
Do not globally replace this token: `main_first/` is also a legitimate historical
folder. Recovery requires a separate, reviewed repair against the intended schema
and saved evidence. File modification times are not proof of historical execution.

`main_3` uses the top-level package name `src`, while `main_4` scripts insert a
relative `src` directory. The first two generations import through `corrosion`.
Use the documented working directory and a separate process for each generation;
renaming folders or mixing module roots can change imports.

## YAML categories and invalid scalar types

In [main_4/configs/specimen_mapping.yaml](../main_4/configs/specimen_mapping.yaml),
unquoted `NO` is parsed as Boolean `False` by the current PyYAML loader. The report
records ten affected specimen mappings and 168 master-table rows. Other YAML fields
contain `main_first` strings where numeric values were intended. Loading YAML
successfully therefore means syntax is valid, not that the config is fit for training.
Original configs and saved results retain these defects for traceability.

## Environment and data portability

There is no verified historical training lockfile and no `main_4/requirements.txt`.
The augmentation requirements omit pandas, which its split/variant scripts import.
Older manifests and prose include absolute paths from previous checkout locations.
They were not rewritten because they are saved records. Curated docs use current
relative paths. A bare Git clone omits ignored `Data/`, `Documentation/`, `.pkl`
artifacts and local render/build files; provide the complete local bundle for handoff.
The broad existing `Data/` ignore rule also ignores `main_3/src/data/` on this
checkout: `io.py`, `canonical.py`, and `__init__.py` are present locally but untracked.
They are included in the full backup and preservation inventory. A Git-only transfer
does not contain that complete historical source tree either. No source-tracking
or ignore-rule change was made to those files during this documentation cleanup.
Compatibility links must be retained on systems that support symbolic links.

## Scientific and continuation limits

- Both structural targets are terminal-only; model-derived curves do not validate
  early warning, actual degradation laws, or remaining useful life.
- Campaign/mesh/chloride/exposure confounding limits transport and causal claims.
- Pre-test availability of failure-surface cover is unverified.
- Model selection used reported evaluation folds; fold SD and two-repeat prediction
  SD are descriptive, not calibrated uncertainty intervals.
- Exact earlier image normalization and some historical figure assembly recipes
  remain unavailable. Saved figures are evidence of outputs, not full execution provenance.
- Four-class classifier training/evaluation remains undone. The fixed split is
  small and imbalanced, particularly for higher severity classes.
- Manuscript authority has not been selected. The original activity report and
  all thesis/article versions remain available unchanged.

Start future repairs in a separate copy with saved outputs protected. Reassess
reproducibility and scientific claims after any functional change; this handoff's
preservation checks alone cannot validate new experiments.

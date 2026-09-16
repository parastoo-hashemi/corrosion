# Known issues requiring future work

This is the unresolved status at handoff. Folder migration updated imports and file lookup, but did not repair scientific
algorithms, change configs, retrain models, or revise report claims.

## Current modelling source cannot be treated as a verified rerun

The existing report documents widespread `main_first` text substitutions in older
Python/config sources, including aggregation names and values expected to be
numeric. Python can parse a module while those expressions still fail at runtime.
Do not globally replace this token: `main_first/` is also the original name
of the folder now called `exploratory_prototype/`. Recovery requires a separate, reviewed repair against the intended schema
and saved evidence. File modification times are not proof of historical execution.

`condition_assessment` uses the top-level package name `src`, while `structural_capacity` scripts insert a
relative `src` directory. The first two generations import through `corrosion`.
Use the documented working directory and a separate process for each generation;
mixing module roots can select a different generation. The folder migration keeps
the internal package names and verifies each generation in a separate process.

## YAML categories and invalid scalar types

In [structural_capacity/configs/specimen_mapping.yaml](../structural_capacity/configs/specimen_mapping.yaml),
unquoted `NO` is parsed as Boolean `False` by the current PyYAML loader. The report
records ten affected specimen mappings and 168 master-table rows. Other YAML fields
contain `main_first` strings where numeric values were intended. Loading YAML
successfully therefore means syntax is valid, not that the config is fit for training.
Original configs and saved results retain these defects for traceability.

## Environment and data portability

There is no verified historical training lockfile and no `structural_capacity/requirements.txt`.
The augmentation requirements omit pandas, which its split/variant scripts import.
Older manifests and prose include absolute paths from previous checkout locations.
They were not rewritten because they are saved records. Curated docs use current
relative paths. Classical and embedding inference now use a same-named file in the
explicitly supplied artifact bundle when a recorded path no longer exists; valid
recorded paths retain precedence. This does not rewrite any manifest or model. A bare Git clone omits ignored `Data/`, `Documentation/`, `.pkl`
artifacts and local render/build files; provide the complete local bundle for handoff.
The accidental source exclusion is resolved: `.gitignore` now names the actual
raw/generated data directories explicitly. It no longer hides
`condition_assessment/src/data/io.py`, `canonical.py` or `__init__.py` on this
case-insensitive checkout. At the final handoff review, read-only Git checks show
all three files are tracked and not ignored. The earlier statements that they
were untracked are superseded by this observed checkout state. No staging or
commit is part of this documentation review; ignored data/model assets still
need inclusion in the local transfer.
The retained archive-document links must be preserved when copying. The seven
old root aliases are removed; use the descriptive package names and the folder
map to interpret historical commands. Saved metadata readers translate historical
repository paths with `research_paths.resolve_project_path`.

## Saved model compatibility and historical verification

Before and after the rename, 121 of 122 serialized model files loaded in the current
environment. `image_embeddings/artifacts/tabular_preprocessor.joblib` cannot load
because its saved scikit-learn `_RemainderColsList` class is unavailable in the installed
version. Some other estimators emit version warnings. Successful loading is not
proof of an exact historical environment; see the migration verification records.
The embedding API remains blocked by this pre-existing preprocessor incompatibility.

The old `archive/repository_maintenance/verify_delivery.py` and its receipts describe an earlier
delivery state. They assume files that were subsequently removed and unmodified
source hashes. Use `archive/repository_maintenance/renaming/verify_renaming.py` for the current
layout. Historical evidence ledgers retain their original paths and hashes; changed
source hashes are recorded separately in the migration receipts.

## Controlled-variant metadata needs reconciliation

The main four-class augmentation metadata and fixed split manifests remain the
starting point for classifier work. Optional [controlled variants](../Data/augmentation_variants/)
need a separate metadata review before use:

- All four `sigma*` CSVs retain only six columns and omit `specimen_id`,
  `image_path` and `original_image_path`. Join `original_image_name` to the main
  augmentation metadata to recover grouping. Verify image locations and apply
  the fixed specimen assignments before selecting training augmentations.
- [sigma2_noise metadata](../Data/augmentation_variants/sigma2_noise/metadata.csv)
  currently contain **1,580 rows: 789 originals + 791 augmentations**. Its retained
  README states 1,582. Original rows for `D01-20240110-0W.png` and
  `D01-20240124-2W.png` are absent; their augmented counterparts are present.
- The referenced generated variant images checked during this review are present.
  These are metadata discrepancies, not a finding that the source originals were lost.
  The [inspection record](../archive/repository_maintenance/handoff_guides/variant_inspection.json)
  records counts and checks without rewriting any dataset.

The current generator writes a fuller schema than these saved sigma CSVs. A seed
and command alone therefore do not establish exact reproduction of their present
contents. Preserve these records, review the discrepancy, then create a separately
versioned reconciled dataset. Classifier training/evaluation remain unfinished.

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
- The delivered manuscripts are the v3 thesis and article. Earlier report versions
  were already removed from the working tree before folder migration; Git history
  retains them.

Start future repairs in a separate copy with saved outputs protected. Reassess
reproducibility and scientific claims after any functional change; this handoff's
preservation checks alone cannot validate new experiments.

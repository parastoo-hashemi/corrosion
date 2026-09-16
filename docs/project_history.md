# Project history and implementation map

The descriptive folder names identify successive research phases. Original names
remain documented in the folder map for saved paths and report citations; their
root shortcuts have been removed. See the
[old-to-new mapping](folder_migration.md); folder numbers in historical records
are phase identifiers, not a quality ranking.

| Folder | What it contributed | Status and safe use |
|---|---|---|
| [exploratory_prototype/](../exploratory_prototype/README.md) | Exploratory random-forest/image-processing scripts and simulated trajectories | Grouped-holdout scripts exist; no complete saved evaluation bundle for a comparable benchmark |
| [classical_corrosion/](../classical_corrosion/README.md) | Classical current-corrosion, progression, and threshold-time baselines; API wrappers | Historical corrosion benchmark, not structural lifetime validation |
| [image_embeddings/](../image_embeddings/README.md) | Frozen pretrained ResNet-18 image embeddings combined with tabular context and a regression head | Historical experiment; not the later untrained four-class ResNet50/ViT proposal |
| [condition_assessment/](../condition_assessment/README.md) | Interpretable image features, grouped surface/structural modelling, degradation curves, and first proxy-RUL outputs | Historical 792-row/five-class generation; its old “final implementation” wording is superseded by this phase map |
| [structural_capacity/](../structural_capacity/README.md) | Readable-image alignment, robustness diagnostics, then terminal ultimate-load refocus | Most mature saved structural study; current source still has unresolved execution defects |
| `archive/structural_baseline_snapshot/` | Retained earlier baseline tree and its output state | Historical snapshot, not a verified identical duplicate; internal code/data/output layout is preserved |
| [classification_data_preparation/](../classification_data_preparation/README.md) | Offline photometric/geometric augmentation, controlled variants, fixed specimen partitions | Main dataset/splits prepared; optional variant metadata need reconciliation; training/evaluation pending |
| [selected_results/](../selected_results/README.md), formerly `emiling/` | Selected figures and papers assembled for sharing | Preserved collection organized by phase, with source links and interpretation limits |

The phase interpretation is grounded in the scripts, configs, saved output
tables, and the [thesis](../final_reports/thesis.pdf), which is the
current report for this project.

## Reading historical records

Historical plans, meeting scripts, reviews, prompt files, and manuscript QA are in
[the archive](../archive/agent_working_notes/README.md), mirrored under their original
repository-relative paths. They describe the state at their writing date and can
contain proposals, obsolete counts, absolute paths from older checkouts, or claims
subsequently qualified. They are preserved records, not current operating instructions.
The [earlier cleanup manifest](../archive/repository_maintenance/move_manifest.csv) records the archive
cleanup. The [folder-renaming manifest](../archive/repository_maintenance/renaming/move_manifest.csv)
records this later migration.

## Conflicts retained explicitly

- The old `condition_assessment` README called that phase “final”; the mature structural results
  are now in `structural_capacity`. Its 792-row/five-class basis is not the 791-row/four-class basis.
- Historical report-package guidance mentioned earlier drafts. The selected delivery
  now contains the v3 thesis and article; older drafts remain in Git history.
- Older planning notes discuss possible model improvements or implied superiority;
  a recommendation is not evidence that an experiment ran or succeeded.
- One augmentation methodology file called minimum requirements “exact installed
  versions.” They are not an environment lockfile.
- Historical notes sometimes describe prototype proxy-RUL as feasible. The delivered
  interpretation is exploratory threshold status, without observed failure times.
- The original agent guide suggested a missing `structural_capacity/requirements.txt` and mixed
  repository-root and `structural_capacity/` working directories. Current commands distinguish them.

Original conflicting documents are retained unchanged in the archive. No report
number, scientific output, or manuscript claim was changed during cleanup.

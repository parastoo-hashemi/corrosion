# Project history and implementation map

The folder names record successive research phases. They are kept because Python
imports, working-directory assumptions, configs, saved manifests, and manuscript
citations depend on them. Folder numbers are not a quality ranking.

| Folder | What it contributed | Status and safe use |
|---|---|---|
| `main_first/` | Exploratory random-forest/image-processing scripts and simulated trajectories | Prototype; no defensible held-out evaluation or comparable saved benchmark |
| `main/` | Classical current-corrosion, progression, and threshold-time baselines; API wrappers | Historical corrosion benchmark, not structural lifetime validation |
| `main_2/` | Frozen pretrained ResNet-18 image embeddings combined with tabular context and a regression head | Historical experiment; not the later untrained four-class ResNet50/ViT proposal |
| `main_3/` | Interpretable image features, grouped surface/structural modelling, degradation curves, and first proxy-RUL outputs | Historical 792-row/five-class generation; its old “final implementation” wording is superseded by this phase map |
| `main_4/` | Readable-image alignment, robustness diagnostics, then terminal ultimate-load refocus | Most mature saved structural study; current source still has unresolved execution defects |
| `main_4_old/` | Retained earlier baseline tree and its output state | Historical snapshot, not a verified identical duplicate; code/data/output paths remain unchanged |
| `augmentation/` | Offline photometric/geometric augmentation, controlled variants, fixed specimen partitions | Later four-class data preparation; training/evaluation remains pending |
| `emiling/` | Copies assembled for presentation/report sharing | Export collection; use the source experiments and report provenance for interpretation |

The phase interpretation is grounded in the scripts, configs, saved output
tables, and the [thesis](../report_v2/thesis/v3/thesis.pdf), which is the
current report for this project.

## Reading historical records

Historical plans, meeting scripts, reviews, prompt files, and manuscript QA are in
[the archive](../archive/agent_working_notes/README.md), mirrored under their original
repository-relative paths. They describe the state at their writing date and can
contain proposals, obsolete counts, absolute paths from older checkouts, or claims
subsequently qualified. They are preserved records, not current operating instructions.
The [move manifest](../report_cleanup/move_manifest.csv) maps every moved file.

## Conflicts retained explicitly

- The old `main_3` README called that phase “final”; the mature structural results
  are now in `main_4`. Its 792-row/five-class basis is not the 791-row/four-class basis.
- The old report-package README recommended v2 and listed only four PDFs; v3 adds
  two more manuscripts. Latest production does not settle which is authoritative.
- Older planning notes discuss possible model improvements or implied superiority;
  a recommendation is not evidence that an experiment ran or succeeded.
- One augmentation methodology file called minimum requirements “exact installed
  versions.” They are not an environment lockfile.
- Historical notes sometimes describe prototype proxy-RUL as feasible. The delivered
  interpretation is exploratory threshold status, without observed failure times.
- The original agent guide suggested a missing `main_4/requirements.txt` and mixed
  repository-root and `main_4/` working directories. Current commands distinguish them.

Original conflicting documents are retained unchanged in the archive. No report
number, scientific output, or manuscript claim was changed during cleanup.

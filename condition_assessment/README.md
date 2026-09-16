# Interpretable condition assessment — historical experiment

This phase studies whether interpretable image features can describe surface
corrosion, support estimates of terminal structural damage, and produce exploratory
threshold-crossing forecasts. It preserves the earlier **792-record, five-class**
experiment, formerly named `main_3/`.

It follows [image embeddings](../image_embeddings/README.md) and precedes the later
[structural-capacity study](../structural_capacity/README.md). The separate
[four-class preparation work](../classification_data_preparation/README.md) uses a
different label scheme and has no completed classifier evaluation.

**Status:** saved results are available to inspect. Current source has unresolved
execution defects; an end-to-end rerun has not been verified. Read the
[known issues](../docs/known_issues.md) before continuing experiments.

## Start with the evidence

| Question | Read first | Supporting files |
|---|---|---|
| What was analysed? | [Dataset inspection](reports/dataset_inspection.md) | [Canonical records](outputs/canonical_dataset.csv), [dataset summary](outputs/dataset_summary.csv) |
| What results were saved? | [Pipeline summary](reports/pipeline_summary.md) | [Figures](reports/figures/) and the full metric tables below |
| How well was surface corrosion predicted? | [Regression metrics](outputs/corrosion_regression_metrics.csv), [five-class metrics](outputs/corrosion_classification_metrics.csv) | [Regression predictions](outputs/corrosion_regression_predictions.parquet), [classification predictions](outputs/corrosion_classification_predictions.parquet) |
| What supported structural-damage estimates? | [Damage metrics](outputs/damage_regression_metrics.csv) | [Held-out predictions](outputs/damage_regression_predictions.parquet), [fitted models](outputs/models/) |
| How were remaining-life estimates defined? | [RUL feasibility assessment](reports/rul_feasibility_assessment.md) | [Exploratory estimates](outputs/rul_estimates.csv), [forecast trajectories](outputs/rul_trajectories.parquet) |
| Why did this phase replace the earlier approach? | [Historical code audit](reports/code_audit.md) | [Original README and development notes](../archive/agent_working_notes/main_3/) |

The four Markdown reports above contain useful scientific context. The code audit's
`main_2` title refers to the preceding embedding phase. Its replacement decisions
describe historical code lineage. The pipeline summary shows only `group_shuffle`
results; the CSV tables also contain treatment and campaign holdouts. Compare
models within the same target, metric and evaluation strategy.

Older PDFs and LaTeX files in this directory are phase records. For the current
handoff, read the [delivered thesis and article](../final_reports/README.md).
Historical reports retain old absolute paths; use the current links here to reach
their evidence.

## What the results can support

- The saved canonical table contains **792 image records, 48 specimens and two
  campaigns**. Repeated images of one specimen do not create independent structural
  observations. Both surface-category targets use labels **1–5**.
- Only **48 records have structural labels**, at weeks **28 or 36**. Wire-area-loss
  and ultimate-load estimates therefore depend on sparse terminal measurements.
  Surface-classification accuracy alone does not validate hidden damage estimates.
- The metric files record three regimes: `group_shuffle`,
  `leave_one_treatment_out` and `leave_one_campaign_out`. Campaign, mesh, chloride
  and exposure differences limit transfer and causal interpretation. Preserve
  specimen grouping when continuing the work.
- Regression errors have target-specific units. Check each target and its recorded
  units before interpreting combined plots; load errors and percentage errors
  cannot be compared directly.
- Remaining useful life (RUL) here is an **exploratory threshold-crossing proxy**.
  There are no observed failure-time labels to validate lifetime predictions.
  The field `failure_probability` is an uncalibrated risk score. A missing RUL
  means no crossing was found within the configured horizon; it does not establish
  unlimited life. The feasibility report records the thresholds and scaling assumptions.

The `*_predictions.parquet` files hold evaluation predictions. In contrast,
`corrosion_state_estimates.parquet` and `damage_state_estimates.parquet` contain
estimates from models refitted on the available training data for downstream
analysis; they are not independent validation evidence.

## Pipeline and saved outputs

The numbered scripts call stages in [the orchestration module](src/orchestration.py).
Names below describe their intended workflow; the saved artifacts do not establish
that the present source reproduces the historical run.

| Stage and script | Purpose | Main destination |
|---|---|---|
| [01 — inspect dataset](scripts/01_inspect_dataset.py) | Parse inputs and summarize labels/specimens | `reports/dataset_inspection.md` |
| [02 — build metadata](scripts/02_build_metadata.py) | Export canonical records and summary | `outputs/canonical_dataset.*`, `dataset_summary.csv` |
| [03 — preview preprocessing](scripts/03_preprocess_images.py) | Create diagnostic crop previews | `reports/figures/preprocessing/`, `outputs/preprocessing_previews.csv` |
| [04 — extract features](scripts/04_extract_features.py) | Calculate interpretable image descriptors | `outputs/image_features.*` |
| [05 — train corrosion models](scripts/05_train_corrosion_models.py) | Evaluate surface regression and five-class classification | Corrosion metrics, predictions, state estimates and models in `outputs/` |
| [06 — train damage models](scripts/06_train_damage_models.py) | Evaluate terminal structural targets | Damage metrics, predictions, state estimates and models in `outputs/` |
| [07 — fit degradation curves](scripts/07_fit_degradation_models.py) | Fit observed and model-derived specimen trajectories | `outputs/degradation_curves.parquet`, `degradation_forecasts.parquet` |
| [08 — estimate proxy RUL](scripts/08_estimate_rul.py) | Calculate threshold crossings and risk scores | `outputs/rul_estimates.*`, `rul_trajectories.parquet` |
| [09 — generate summary](scripts/09_generate_reports.py) | Read saved results and produce plots/report | `reports/pipeline_summary.md`, `reports/figures/` |

## Folder guide and continuation

- [configs/default.toml](configs/default.toml): data/output paths, targets, seed,
  preprocessing settings and proxy thresholds. Paths resolve from this phase directory.
- [src/](src/): parsing, features, grouped splits, models, degradation, RUL and plotting.
- [scripts/](scripts/): stage entry points; [tests/](tests/) contains focused parsing,
  split and health-index checks.
- [outputs/](outputs/): saved tables, predictions, trajectories and model bundles.
- [reports/](reports/): scientific explanations, figures and historical report material.
- [logs/](logs/): local execution diagnostics.

Start with [reproduction guidance](../docs/reproduction.md),
[requirements](requirements.txt) and the configuration in a separate reproduction
copy. The requirements specify minimum versions, not the original training lockfile.
Include the local data and models when transferring the project.

The [experiment map](../docs/experiments.md) gives historical commands from the
repository root. For example, `python condition_assessment/scripts/01_inspect_dataset.py`
invokes stage 01. Even this stage writes a report and log. Stages 05–06 train models;
[run_all.py](scripts/run_all.py) runs the entire sequence and can overwrite saved
evidence. Use a separate Python process for this phase because its package name
`src` can conflict with other generations.

Return to the [project overview](../README.md) or consult the
[folder migration map](../docs/folder_migration.md) for older names.

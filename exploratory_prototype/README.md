# Exploratory corrosion prototype

This is the earliest image-processing, random-forest and trajectory-simulation
work, formerly `main_first/`. It records how the project moved from simple rust
masks and name-derived features toward the later
[classical corrosion baseline](../classical_corrosion/README.md).

**Status:** historical exploratory material. Some scripts implement grouped
holdouts, but this directory lacks a complete saved split/prediction/metric bundle
for a comparable benchmark. Its saved full-data model and simulated trajectories
do not establish validated remaining useful life.

## What is useful to keep and read

| Material | Purpose |
|---|---|
| [Images_Dataset_A-Z.xlsx](Images_Dataset_A-Z.xlsx), [local images](Images_dataset/Images_dataset/) | Inputs used by early scripts; retained separately from later shared data |
| [Final_Corrosion_Data.xlsx](Final_Corrosion_Data.xlsx) | Derived table used by percentage-regression scripts: image, specimen, week and rust percentage |
| [corrosion_model.pkl](corrosion_model.pkl), [series_encoder.pkl](series_encoder.pkl) | Saved regression model and its series encoder; keep the pair together |
| [Final_Prediction_Results.png](Final_Prediction_Results.png), [Thesis_Accuracy_Plot.png](Thesis_Accuracy_Plot.png) | Historical model illustrations; filenames alone do not establish an independently reproducible score |
| [feature_importance.png](feature_importance.png) | Exploratory feature-ranking illustration |
| [G04 simulation](RUL_Prediction_G04.png), [S4SAVF03 simulation](RUL_Prediction_S4SAVF03.png) | Examples of the threshold simulation, subject to the limits below |
| [ressult/](ressult/) | Three earlier plots: `RF_baseline.png`, `RandomForest_Advanced.png`, `myplot.png`; original spelling retained |

These are historical assets, not disposable duplicates. Read the
[current article and thesis](../final_reports/README.md) for the mature scientific conclusions.

## Script map

| Script | What it actually does |
|---|---|
| [process_images.py](process_images.py) | Uses an RGB rust mask to calculate image rust percentage and writes `Final_Corrosion_Data.xlsx` |
| [_data_visualization.py](_data_visualization.py) | Plots category trajectories from the local workbook |
| [_RandomForest_Baseline.py](_RandomForest_Baseline.py) | Plots category trends by series; despite its filename, the current file does not fit a random forest |
| [_RandomForest_Advanced.py](_RandomForest_Advanced.py) | Trains a next-observation category classifier using specimen-group holdout and writes a feature-importance plot |
| [_Corrosion_RUL_Predictor.py](_Corrosion_RUL_Predictor.py) | Fits a next-observation rust-percentage regressor with an observation-gap feature and grouped holdout; writes a comparison plot |
| [thesis_report.py](thesis_report.py) | Trains/evaluates a log-target regressor and writes an accuracy plot; it is a modelling script, not a thesis compiler |
| [build_model.py](build_model.py) | Fits the log-target model on all eligible observations and overwrites both `.pkl` files |
| [predict_future.py](predict_future.py) | Interactive prediction from a specimen's latest state using the saved model/encoder |
| [RUL_Simulation.py](RUL_Simulation.py) | Interactive repeated prediction toward a 10% rust threshold, with heuristic growth corrections and a week-150 cap |

The percentage-model workflow was broadly: extract the table → explore/evaluate
models → fit the saved full-data model → run prediction/simulation examples.
The category scripts form a separate exploratory branch. This is a reading map,
not a verified sequence that recreates every saved figure.

## Interpretation limits

- The prototype's rust-mask percentage is not interchangeable with later total-rust,
  peak-rust, four-class or structural targets. Check definitions before comparing scores.
- Features inferred from substrings such as `MI`, `SA`, `PA` and `VF` reflect early
  coding assumptions. Reconcile them with authoritative specimen/treatment
  metadata before reuse; the comments are not an experimental specification.
- Several targets use the next observed row, which may be more than one week away.
  `predict_future.py` labels its result “next week” and forces growth when the model
  predicts a decrease. The saved model itself was fitted on all eligible rows.
- The simulation imposes a 10% limit, smoothing and minimum growth. It prints a
  failure-time result even if its loop stops at the week-150 cap without crossing
  the threshold. Its displayed RUL is not evidence of an observed failure time.

## Continuing safely

Inspect source before execution. Most scripts run at import time, and some prompt
for input or open plotting windows. They have no general `--help` interface;
importing them is not a read-only installation check.

Most filenames resolve from the working directory, historically this phase folder.
`process_images.py` additionally contains an obsolete absolute Windows image path.
Any deliberate rerun needs a separate copy, reviewed input paths and protected
output destinations. Running the model/plot scripts can overwrite the saved table,
models or figures. There is no phase-specific requirements file or verified runtime.

For continuation, use the later [classical guide](../classical_corrosion/README.md),
[experiment map](../docs/experiments.md), [reproduction guide](../docs/reproduction.md)
and [known issues](../docs/known_issues.md). The [project history](../docs/project_history.md)
and [folder map](../docs/folder_migration.md) explain earlier names.

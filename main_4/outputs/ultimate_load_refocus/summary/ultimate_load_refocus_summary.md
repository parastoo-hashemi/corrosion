# Ultimate-Load Refocus Summary

## What was run

- A new leakage-safe terminal-capacity workflow under `outputs/ultimate_load_refocus/`.
- Pooled grouped cross-validation on all weeks retained.
- Pooled leave-one-campaign-out as a stress test only.
- Post-onset sensitivity analysis using `surface_total_rust_pct >= 0.500`.
- Mesh-stratified grouped analyses for 4-mesh and 7-mesh specimens.
- Feature-family comparisons across metadata, RGB, HSV, and combined descriptors.

## Best grouped-CV result

- Best grouped-CV configuration: `Ridge` with `metadata-only`.
- Grouped-CV MAE: `0.173 +- 0.046` kN.
- Grouped-CV RMSE: `0.214 +- 0.054` kN.
- Grouped-CV Spearman: `0.758 +- 0.205`.

## Does superficial corrosion add value beyond metadata?

- Metadata-only grouped-CV baseline: `Ridge` with MAE `0.173` kN and Spearman `0.758`.
- Best non-baseline feature set: `metadata+HSV` with `Ridge`.
- Relative to metadata-only, this was classified as `no_meaningful_change` (delta MAE `+0.000` kN, delta Spearman `+0.013`).
- See `feature_set_delta_vs_metadata_only.csv` for the full baseline-relative comparison table.

## Stress-test interpretation

- Leave-one-campaign-out is retained, but it should be interpreted conservatively because campaign and mesh family are perfectly aligned in this dataset.
- Mesh-stratified grouped analyses are the preferred basis for the main scientific claim about superficial corrosion versus terminal load.

## What should and should not be claimed

- The project estimates terminal structural capacity (`ultimate_load_kn`) from metadata and image-derived superficial-corrosion descriptors.
- The project does not measure hidden/internal corrosion directly.
- The project does not produce true RUL or full-life prediction.
- Any uncertainty reported here is approximate and comes from held-out prediction variability across repeated grouped folds.

## Leave-one-campaign-out best feature-set summary

- `metadata-only`: `GradientBoosting` with MAE `0.465` kN and Spearman `0.217`.
- `metadata+RGB`: `XGBoost` with MAE `0.481` kN and Spearman `0.278`.
- `metadata+RGB+HSV`: `GradientBoosting` with MAE `0.508` kN and Spearman `0.461`.
- `metadata+HSV`: `RandomForest` with MAE `0.512` kN and Spearman `0.271`.
- `HSV-only`: `Ridge` with MAE `0.631` kN and Spearman `0.056`.
- `RGB-only`: `XGBoost` with MAE `0.636` kN and Spearman `0.379`.
- `RGB+HSV`: `RandomForest` with MAE `0.642` kN and Spearman `0.316`.

## Mesh-stratified highlights

- `mesh_4` / `metadata+RGB+HSV`: `CatBoost` with MAE `0.194` kN and Spearman `0.081`.
- `mesh_4` / `RGB-only`: `CatBoost` with MAE `0.203` kN and Spearman `0.097`.
- `mesh_4` / `metadata-only`: `Ridge` with MAE `0.208` kN and Spearman `0.301`.
- `mesh_4` / `HSV-only`: `CatBoost` with MAE `0.210` kN and Spearman `0.057`.
- `mesh_4` / `RGB+HSV`: `CatBoost` with MAE `0.214` kN and Spearman `0.187`.
- `mesh_4` / `metadata+HSV`: `Ridge` with MAE `0.228` kN and Spearman `-0.025`.
- `mesh_4` / `metadata+RGB`: `Ridge` with MAE `0.261` kN and Spearman `0.085`.
- `mesh_7` / `HSV-only`: `CatBoost` with MAE `0.137` kN and Spearman `0.460`.
- `mesh_7` / `RGB+HSV`: `CatBoost` with MAE `0.138` kN and Spearman `0.330`.
- `mesh_7` / `RGB-only`: `CatBoost` with MAE `0.140` kN and Spearman `0.290`.
- `mesh_7` / `metadata+RGB+HSV`: `CatBoost` with MAE `0.204` kN and Spearman `0.010`.
- `mesh_7` / `metadata+RGB`: `Ridge` with MAE `0.214` kN and Spearman `0.030`.
- `mesh_7` / `metadata-only`: `Ridge` with MAE `0.216` kN and Spearman `-0.050`.
- `mesh_7` / `metadata+HSV`: `Ridge` with MAE `0.245` kN and Spearman `-0.000`.

## Baseline-relative comparison labels

- `metadata-only`: `no_meaningful_change` relative to metadata-only (delta MAE `+0.000` kN, delta Spearman `+0.000`).
- `metadata+HSV`: `no_meaningful_change` relative to metadata-only (delta MAE `+0.000` kN, delta Spearman `+0.013`).
- `metadata+RGB+HSV`: `no_meaningful_change` relative to metadata-only (delta MAE `+0.010` kN, delta Spearman `-0.005`).
- `metadata+RGB`: `no_meaningful_change` relative to metadata-only (delta MAE `+0.011` kN, delta Spearman `-0.010`).
- `HSV-only`: `worsened` relative to metadata-only (delta MAE `+0.038` kN, delta Spearman `-0.053`).
- `RGB+HSV`: `worsened` relative to metadata-only (delta MAE `+0.061` kN, delta Spearman `-0.090`).
- `RGB-only`: `worsened` relative to metadata-only (delta MAE `+0.081` kN, delta Spearman `-0.257`).
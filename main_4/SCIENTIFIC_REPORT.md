# Scientific Report

## Problem formulation

Direct supervised RUL is invalid for this dataset.

The current implementation should be interpreted conservatively as:

surface corrosion progression -> hidden damage estimation -> descriptive degradation smoothing -> exploratory threshold-status analysis

## Verified dataset facts

- aligned usable rows: 791
- unique specimens: 48
- image files found: 792
- orphan / corrupted image: ['E01-20240508-17W']
- structural-label rows: 48
- grouped split key: specimen_id

## What Ran Successfully

- audit and alignment validation
- deterministic specimen mapping from `configs/specimen_mapping.yaml`
- thesis-aligned interpretable image feature extraction
- grouped surface and hidden-damage benchmarks
- descriptive degradation fitting on model-based hidden-damage proxies
- exploratory threshold-status output generation

## What Is Scientifically Meaningful

- Data alignment and grouped split safety are credible.
- The rust-mask feature reconstructs `surface_total_rust_pct` almost exactly (MAE=0.000228, max abs diff=0.000500); this is useful as a sanity check on the image-analysis pipeline.
- `peak_rust_pct` remains a meaningful auxiliary surface benchmark (MAE=1.097, RMSE=2.805, Spearman=0.992) under grouped splitting.
- Leave-one-campaign-out structural failure remains the most informative negative result for the robustness-selected hidden-damage models: `wire_area_loss_frac` MAE=0.121, RMSE=0.150, Spearman=-0.266 and `ultimate_load_kn` MAE=0.564, RMSE=0.600, Spearman=0.353.
- The current robust hidden-damage selections are `metadata_only` for `wire_area_loss_frac` and `metadata_only` for `ultimate_load_kn`, which means the most stable structural signal in this round comes primarily from temporal / design metadata rather than from engineered image features.

## What Is Not A Valid Claim

- `surface_total_rust_pct` should not be presented as an independent predictive image-model result, because it is nearly equivalent to an engineered rust-area feature.
- `wire_area_loss_frac` is not a reliable hidden-damage predictor yet (MAE=0.105, RMSE=0.124, Spearman=0.280); ranking performance remains weak.
- The degradation stage is descriptive smoothing of model-generated hidden-damage proxies, not validated physical degradation identification.
- The threshold stage does not currently yield forward residual-life estimates; it is an exploratory threshold-status summary.

## Benchmark Snapshot

- surface sanity check `surface_total_rust_pct`: `GradientBoosting` (MAE=0.177, RMSE=0.821, Spearman=0.999)
- surface benchmark `peak_rust_pct`: `RandomForest` (MAE=1.097, RMSE=2.805, Spearman=0.992)
- structural benchmark `wire_area_loss_frac`: `CatBoost` with `metadata_only` (MAE=0.105, RMSE=0.124, Spearman=0.280)
- structural benchmark `ultimate_load_kn`: `RandomForest` with `metadata_only` (MAE=0.174, RMSE=0.214, Spearman=0.778)

## Feature Controls Applied

- `img_strip_count` excluded from modelling: constant feature for the current extraction pipeline
- `img_contrast` excluded from modelling: duplicate of img_brightness_std
- `img_edge_to_center_rust_ratio` excluded from modelling: unstable ratio in low-rust images
- `wire_area_loss_frac` final feature count: 8
- `ultimate_load_kn` final feature count: 8

## Degradation and Threshold-Status Outputs

- specimens fit successfully: 48
- selected family counts: {'linear': 27, 'monotone_isotonic': 21}
- future threshold crossings within the projection horizon: 0
- rows with non-null `proxy_rul_days`: 0 (only future crossings populate this column)
- baseline threshold crossings across all specimen-threshold pairs: 45

Threshold-status summary:

|   threshold_wire_area_loss_frac |   n_specimens |   n_crossed_by_baseline |   n_crossed_during_observation |   n_future_crossings_within_horizon |   n_right_censored |   n_crossed_by_last_observation |   frac_crossed_by_baseline |   frac_crossed_during_observation |   frac_crossed_by_last_observation |   frac_future_crossings_within_horizon |   frac_right_censored |
|--------------------------------:|--------------:|------------------------:|-------------------------------:|------------------------------------:|-------------------:|--------------------------------:|---------------------------:|----------------------------------:|-----------------------------------:|---------------------------------------:|----------------------:|
|                             0.2 |            48 |                      32 |                              1 |                                   0 |                 15 |                              33 |                   0.666667 |                         0.0208333 |                           0.6875   |                                      0 |              0.3125   |
|                             0.3 |            48 |                       8 |                              1 |                                   0 |                 39 |                               9 |                   0.166667 |                         0.0208333 |                           0.1875   |                                      0 |              0.8125   |
|                             0.4 |            48 |                       5 |                              0 |                                   0 |                 43 |                               5 |                   0.104167 |                         0         |                           0.104167 |                                      0 |              0.895833 |

## Limitations

- the aligned usable dataset is 791, not 792, because one PNG is orphaned and unreadable
- structural supervision is limited to 48 terminal rows and remains too sparse for strong prognostic claims
- campaign is confounded with mesh count, NaCl level, and terminal duration, so cross-campaign generalization remains weak
- exact GIMP preprocessing steps from the thesis are not fully reproducible from the provided files
- degradation and threshold-status outputs are downstream products of model-based hidden-damage proxies, not direct structural observations

## Current Bottom Line

This codebase is currently strongest as an auditable baseline for data validation, surface-label reconstruction, leakage-safe evaluation, and honest negative findings about structural generalization.
It is not yet strong enough to claim validated hidden-damage prognostics or decision-ready proxy-RUL.
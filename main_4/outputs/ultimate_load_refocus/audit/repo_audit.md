# Repo Audit For Ultimate-Load Refocus

## What already supports the refocused objective

- The canonical `master_table.csv` already preserves `ultimate_load_kn`, `wire_area_loss_frac`, specimen metadata, campaign labels, and the grouped leakage key `specimen_id`.
- The existing image-feature extractor is deterministic and interpretable, which is appropriate for a conservative thesis-style load-estimation study.
- The repo already contains grouped split utilities and a useful mesh-stratified correlation script for `ultimate_load_kn`.
- The current benchmark stack already supports `RandomForest`, `GradientBoosting`, `XGBoost`, and `CatBoost`, so the new workflow can reuse familiar model families.

## What conflicts with the refocused objective

- The repository README, reports, and top-level workflow still center hidden-damage inference, degradation modeling, and proxy-RUL rather than direct terminal-capacity estimation.
- The prior structural modeling stage uses only terminal rows, then immediately routes predictions into degradation and threshold logic, which is not the main research question here.
- The old output structure does not separate measured `ultimate_load_kn` from predicted load estimates for every observation.
- The previous evaluation bundle is leakage-safe but too minimal for the requested transparency package: it lacks specimen manifests, fold-balance summaries, uncertainty summaries, learning curves per experiment, and organized diagnostic outputs.
- HSV descriptors were not present in the original image characterization, so RGB-versus-HSV feature-family comparisons were not possible.

## Scientific cautions discovered during the audit

- `n_steel_mesh` is perfectly aligned with campaign in this dataset: all 7-mesh specimens are in `campaign_1`, and all 4-mesh specimens are in `campaign_2`.
- Because of that alignment, pooled leave-one-campaign-out is a harsh campaign-plus-mesh extrapolation stress test, not a clean within-mesh generalization estimate.
- For the central corrosion-versus-load question, mesh-stratified analyses are therefore scientifically preferred over pooled raw correlations.
- Visible surface corrosion remains only a superficial descriptor. It should not be described as a direct measurement of hidden/internal corrosion or as residual useful life.

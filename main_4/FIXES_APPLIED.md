# Fixes Applied

## Scope

Implemented only items 1-4 from Section 1 (`Immediate Fixes`) of [NEXT_STEPS_PLAN.md](/Users/parastoo/All_projects/Proj_corrosion/main_4/NEXT_STEPS_PLAN.md).

Those four items were:

1. Reframe the surface stage as a label-reconstruction sanity check, not a standalone predictive success.
2. Remove or neutralize degenerate image features before the next benchmark.
3. Downgrade all proxy-RUL claims to exploratory threshold-status analysis.
4. Rewrite `SCIENTIFIC_REPORT.md` so the written claims match the evidence and limitations.

## Which Items 1-4 Were Implemented

- Item 1 implemented.
  - The surface stage is now explicitly framed as a sanity-check / reconstruction stage in the regenerated [README.md](/Users/parastoo/All_projects/Proj_corrosion/main_4/README.md), [SCIENTIFIC_REPORT.md](/Users/parastoo/All_projects/Proj_corrosion/main_4/SCIENTIFIC_REPORT.md), and in the regenerated surface best-model metadata at [outputs/models/surface/best_models.csv](/Users/parastoo/All_projects/Proj_corrosion/main_4/outputs/models/surface/best_models.csv).
- Item 2 implemented.
  - The following features were excluded from modelling:
    - `img_strip_count`
    - `img_contrast`
    - `img_edge_to_center_rust_ratio`
- Item 3 implemented.
  - The threshold stage now writes exploratory threshold-status outputs instead of implying usable forward RUL when the threshold was already crossed during the observed window.
- Item 4 implemented.
  - The generated report language was rewritten conservatively, and the stale report-related sentence in [OUTPUT_REVIEW.md](/Users/parastoo/All_projects/Proj_corrosion/main_4/OUTPUT_REVIEW.md) was updated.

## Exactly Which Files Were Changed

### Manually Edited Source / Report Files

- [src/corrosion_proxy_rul/feature_engineering.py](/Users/parastoo/All_projects/Proj_corrosion/main_4/src/corrosion_proxy_rul/feature_engineering.py)
- [src/corrosion_proxy_rul/models_surface.py](/Users/parastoo/All_projects/Proj_corrosion/main_4/src/corrosion_proxy_rul/models_surface.py)
- [src/corrosion_proxy_rul/models_rul_proxy.py](/Users/parastoo/All_projects/Proj_corrosion/main_4/src/corrosion_proxy_rul/models_rul_proxy.py)
- [src/corrosion_proxy_rul/reporting.py](/Users/parastoo/All_projects/Proj_corrosion/main_4/src/corrosion_proxy_rul/reporting.py)
- [train_rul_proxy_models.py](/Users/parastoo/All_projects/Proj_corrosion/main_4/train_rul_proxy_models.py)
- [OUTPUT_REVIEW.md](/Users/parastoo/All_projects/Proj_corrosion/main_4/OUTPUT_REVIEW.md)

### Regenerated Root Documents

- [README.md](/Users/parastoo/All_projects/Proj_corrosion/main_4/README.md)
- [SCIENTIFIC_REPORT.md](/Users/parastoo/All_projects/Proj_corrosion/main_4/SCIENTIFIC_REPORT.md)

### Regenerated Stage Outputs

- [outputs/data/full_feature_table.csv](/Users/parastoo/All_projects/Proj_corrosion/main_4/outputs/data/full_feature_table.csv)
- All files under [outputs/models/surface](/Users/parastoo/All_projects/Proj_corrosion/main_4/outputs/models/surface)
- All files under [outputs/models/hidden_damage](/Users/parastoo/All_projects/Proj_corrosion/main_4/outputs/models/hidden_damage)
- All files under [outputs/models/degradation](/Users/parastoo/All_projects/Proj_corrosion/main_4/outputs/models/degradation)
- All files under [outputs/models/proxy_rul](/Users/parastoo/All_projects/Proj_corrosion/main_4/outputs/models/proxy_rul)
- [outputs/logs/train_surface_models.log](/Users/parastoo/All_projects/Proj_corrosion/main_4/outputs/logs/train_surface_models.log)
- [outputs/logs/train_hidden_damage_models.log](/Users/parastoo/All_projects/Proj_corrosion/main_4/outputs/logs/train_hidden_damage_models.log)
- [outputs/logs/train_degradation_models.log](/Users/parastoo/All_projects/Proj_corrosion/main_4/outputs/logs/train_degradation_models.log)
- [outputs/logs/train_rul_proxy_models.log](/Users/parastoo/All_projects/Proj_corrosion/main_4/outputs/logs/train_rul_proxy_models.log)

## What Was Changed In Each Manually Edited File

- [src/corrosion_proxy_rul/feature_engineering.py](/Users/parastoo/All_projects/Proj_corrosion/main_4/src/corrosion_proxy_rul/feature_engineering.py)
  - Added `MODELING_QC_EXCLUSIONS`.
  - Excluded `img_strip_count`, `img_contrast`, and `img_edge_to_center_rust_ratio` from model feature selection.
- [src/corrosion_proxy_rul/models_surface.py](/Users/parastoo/All_projects/Proj_corrosion/main_4/src/corrosion_proxy_rul/models_surface.py)
  - Added conservative benchmark notes for surface targets.
  - Marked `surface_total_rust_pct` as a `label_reconstruction_sanity_check` in the saved `best_models.csv`.
  - Updated the `surface_total_rust_pct` feature-importance plot title to reflect the sanity-check interpretation.
- [src/corrosion_proxy_rul/models_rul_proxy.py](/Users/parastoo/All_projects/Proj_corrosion/main_4/src/corrosion_proxy_rul/models_rul_proxy.py)
  - Added explicit threshold-status fields:
    - `threshold_reached_by_baseline`
    - `threshold_crossed_during_observation`
    - `future_crossing_within_horizon`
    - `threshold_status`
  - Changed `proxy_rul_days` so it is only populated for future crossings after the observed window.
  - Expanded `proxy_rul_summary.csv` to report baseline crossings, during-observation crossings, future crossings, and censoring counts.
  - Updated the proxy figure title to state that it is exploratory threshold-status output.
- [src/corrosion_proxy_rul/reporting.py](/Users/parastoo/All_projects/Proj_corrosion/main_4/src/corrosion_proxy_rul/reporting.py)
  - Rewrote README generation with conservative interpretation notes.
  - Rewrote scientific-report generation to:
    - foreground the invalidity of direct RUL claims
    - state the surface-stage tautology explicitly
    - report weak hidden-damage ranking performance
    - describe degradation as descriptive smoothing
    - describe proxy output as threshold-status only
    - report the QC feature exclusions
- [train_rul_proxy_models.py](/Users/parastoo/All_projects/Proj_corrosion/main_4/train_rul_proxy_models.py)
  - Updated the stage log message to say `Exploratory threshold-status analysis complete` instead of `Proxy-RUL generation complete`.
- [OUTPUT_REVIEW.md](/Users/parastoo/All_projects/Proj_corrosion/main_4/OUTPUT_REVIEW.md)
  - Replaced the stale sentence that described the previous scientific report as currently too optimistic.

## Which Stages Were Re-Run

- `conda run -n env python train_surface_models.py`
- `conda run -n env python train_hidden_damage_models.py`
- `conda run -n env python train_degradation_models.py`
- `conda run -n env python train_rul_proxy_models.py`
- A targeted Python call regenerated:
  - [README.md](/Users/parastoo/All_projects/Proj_corrosion/main_4/README.md)
  - [SCIENTIFIC_REPORT.md](/Users/parastoo/All_projects/Proj_corrosion/main_4/SCIENTIFIC_REPORT.md)

No audit, EDA, or image-feature extraction stages were re-run.

## What Improved

- The written outputs no longer present the surface stage as a generic predictive success.
- The three flagged QC features are no longer used in the model benchmarks.
- The excluded unstable ratio `img_edge_to_center_rust_ratio` no longer appears in the regenerated hidden-damage feature importance outputs.
- The threshold stage no longer writes zero-valued pseudo-RUL for already-crossed thresholds.
  - After the fix, [proxy_rul_estimates.csv](/Users/parastoo/All_projects/Proj_corrosion/main_4/outputs/models/proxy_rul/proxy_rul_estimates.csv) has `proxy_rul_days` populated only for future crossings, and there are currently zero such cases.
- The regenerated [proxy_rul_summary.csv](/Users/parastoo/All_projects/Proj_corrosion/main_4/outputs/models/proxy_rul/proxy_rul_summary.csv) is more informative:
  - threshold `0.2`: `32` baseline crossings, `13` crossings during observation, `0` future crossings, `3` censored
  - threshold `0.3`: `2` baseline crossings, `18` crossings during observation, `0` future crossings, `28` censored
  - threshold `0.4`: `0` baseline crossings, `7` crossings during observation, `0` future crossings, `41` censored

## What Is Still Unresolved

- `surface_total_rust_pct` remains almost numerically identical to `img_rust_area_ratio_pct`; the stage is now framed honestly, but the underlying tautology remains.
- `wire_area_loss_frac` remains weak as a hidden-damage predictor.
- Structural performance still collapses under leave-one-campaign-out.
- Degradation modelling still relies on model-based hidden-damage proxies fit in-sample for the final full-data trajectory generation.
- There are still no future threshold crossings within the current projection horizon, so the threshold stage remains exploratory rather than decision-ready.
- Campaign confounding, sparse structural labels, and incomplete recovery of the original thesis preprocessing remain unresolved.

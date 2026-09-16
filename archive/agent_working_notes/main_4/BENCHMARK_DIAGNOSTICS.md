# Benchmark Diagnostics

## What Was Generated

- consolidated benchmark summary table across stages, targets, and strategies
- consolidated fold-level benchmark table
- split-composition diagnostics
- group-shuffle model-comparison plots
- best-model robustness plots across split strategies
- fold-stability plots for the selected best models
- a relative-MAE collapse heatmap
- saved prediction diagnostics for every predictions CSV
- saved ranked bar plots for every feature-importance CSV

## Best-Model Robustness Snapshot

| stage         | target                 | best_model_name   | strategy                |   mae_mean |    mae_std |   spearman_mean |   spearman_std |   relative_mae_vs_group_shuffle |
|:--------------|:-----------------------|:------------------|:------------------------|-----------:|-----------:|----------------:|---------------:|--------------------------------:|
| surface       | peak_rust_pct          | RandomForest      | group_shuffle           |  1.09678   | 0.685256   |       0.992347  |    0.00348981  |                        1        |
| surface       | peak_rust_pct          | RandomForest      | leave_one_campaign_out  |  1.05773   | 0.302473   |       0.976852  |    0.000148574 |                        0.964394 |
| surface       | peak_rust_pct          | RandomForest      | leave_one_treatment_out |  0.831446  | 0.579725   |       0.972224  |    0.0362915   |                        0.75808  |
| surface       | surface_total_rust_pct | GradientBoosting  | group_shuffle           |  0.177346  | 0.282996   |       0.99875   |    0.00144674  |                        1        |
| surface       | surface_total_rust_pct | GradientBoosting  | leave_one_campaign_out  |  0.136108  | 0.057768   |       0.997067  |    0.00289435  |                        0.767472 |
| surface       | surface_total_rust_pct | GradientBoosting  | leave_one_treatment_out |  0.0974289 | 0.182779   |       0.989053  |    0.0306295   |                        0.549373 |
| hidden_damage | ultimate_load_kn       | RandomForest      | group_shuffle           |  0.17438   | 0.0201265  |       0.778265  |    0.111986    |                        1        |
| hidden_damage | ultimate_load_kn       | RandomForest      | leave_one_campaign_out  |  0.564247  | 0.00964632 |       0.353145  |    0.0172604   |                        3.23573  |
| hidden_damage | ultimate_load_kn       | RandomForest      | leave_one_treatment_out |  0.203404  | 0.0759968  |       0.121699  |    0.593321    |                        1.16644  |
| hidden_damage | wire_area_loss_frac    | RandomForest      | group_shuffle           |  0.105037  | 0.0355467  |       0.280092  |    0.21276     |                        1        |
| hidden_damage | wire_area_loss_frac    | RandomForest      | leave_one_campaign_out  |  0.124017  | 0.00202607 |      -0.0893225 |    0.133152    |                        1.1807   |
| hidden_damage | wire_area_loss_frac    | RandomForest      | leave_one_treatment_out |  0.119625  | 0.045768   |       0.275443  |    0.552812    |                        1.13888  |

## Interpretation

- These plots emphasize robustness and collapse, not only the lowest average MAE.
- Leave-one-campaign-out is the clearest stress test for scientific generalization in this project.
- Fold-stability plots should be consulted before claiming one model is meaningfully better than another.
- `ultimate_load_kn` degrades sharply under leave-one-campaign-out: relative MAE rises to 3.24x the group-shuffle baseline.
- `wire_area_loss_frac` remains weak even in the best grouped setting: best-model Spearman is only 0.280.
- Surface-stage prediction diagnostics are useful for communication, but `surface_total_rust_pct` should still be treated as a sanity-check target rather than a discovery result.

## Key Supporting Outputs

- `outputs/diagnostics/tables/benchmark_summary_long.csv`
- `outputs/diagnostics/tables/benchmark_fold_metrics_long.csv`
- `outputs/diagnostics/tables/benchmark_best_model_robustness.csv`
- `outputs/diagnostics/tables/split_summary_long.csv`
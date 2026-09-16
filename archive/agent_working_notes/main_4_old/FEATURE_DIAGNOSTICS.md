# Feature Diagnostics

## What Was Generated

- feature inventory by stage
- feature missingness and variance summaries
- near-constant feature detection
- duplicate and high-collinearity checks
- focused feature-feature and feature-target correlation plots

## Highest-Priority Findings

- Near-constant columns detected: 13 rows in `outputs/diagnostics/tables/near_constant_features.csv`.
- Exact duplicate feature pairs detected: 1.
- High-collinearity pairs (|Spearman| >= 0.95): 36.
- The collinearity figure prioritizes image-image pairs so the redundancy inside the image pipeline is visible at a glance; the CSV still keeps all pairs, including metadata and time variables.
- `surface_total_rust_pct` is almost numerically identical to `img_rust_area_ratio_pct` (Spearman 0.9996), which reinforces the existing label-reconstruction framing.
- The strongest univariate relationship with `wire_area_loss_frac` is only 0.3817, so the hidden-damage stage remains weak even before model fitting.
- Focused heatmaps were used instead of one giant unreadable matrix.

## Strongest Feature-Target Relationships

| target                 | feature_name                    | source_family    |   n_valid |   spearman_corr |   spearman_abs_corr |
|:-----------------------|:--------------------------------|:-----------------|----------:|----------------:|--------------------:|
| peak_rust_pct          | img_strip_rust_std_pct          | image_spatial    |       791 |        0.992944 |            0.992944 |
| peak_rust_pct          | img_strip_rust_max_pct          | image_spatial    |       791 |        0.988394 |            0.988394 |
| peak_rust_pct          | img_strip_rust_mean_pct         | image_spatial    |       791 |        0.985396 |            0.985396 |
| peak_rust_pct          | img_rust_area_ratio_pct         | image_mask       |       791 |        0.985148 |            0.985148 |
| peak_rust_pct          | img_strip_rust_p90_pct          | image_spatial    |       791 |        0.977698 |            0.977698 |
| surface_total_rust_pct | img_rust_area_ratio_pct         | image_mask       |       791 |        0.999636 |            0.999636 |
| surface_total_rust_pct | img_strip_rust_mean_pct         | image_spatial    |       791 |        0.999245 |            0.999245 |
| surface_total_rust_pct | img_strip_rust_p90_pct          | image_spatial    |       791 |        0.98988  |            0.98988  |
| surface_total_rust_pct | img_strip_rust_std_pct          | image_spatial    |       791 |        0.980973 |            0.980973 |
| surface_total_rust_pct | img_strip_rust_max_pct          | image_spatial    |       791 |        0.974257 |            0.974257 |
| ultimate_load_kn       | ageing_days                     | temporal         |        48 |       -0.827316 |            0.827316 |
| ultimate_load_kn       | week                            | temporal         |        48 |       -0.827316 |            0.827316 |
| ultimate_load_kn       | n_steel_mesh                    | tabular_metadata |        48 |        0.827316 |            0.827316 |
| ultimate_load_kn       | nacl_pct                        | tabular_metadata |        48 |       -0.827316 |            0.827316 |
| ultimate_load_kn       | terminal_week                   | temporal         |        48 |       -0.827316 |            0.827316 |
| wire_area_loss_frac    | img_rust_blob_eccentricity_mean | image_morphology |        48 |        0.381741 |            0.381741 |
| wire_area_loss_frac    | img_rust_blob_eccentricity_max  | image_morphology |        48 |        0.331133 |            0.331133 |
| wire_area_loss_frac    | ageing_days                     | temporal         |        48 |        0.306784 |            0.306784 |
| wire_area_loss_frac    | week                            | temporal         |        48 |        0.306784 |            0.306784 |
| wire_area_loss_frac    | n_steel_mesh                    | tabular_metadata |        48 |       -0.306784 |            0.306784 |

## Key Supporting Outputs

- `outputs/diagnostics/tables/feature_inventory_by_stage.csv`
- `outputs/diagnostics/tables/feature_missingness_summary.csv`
- `outputs/diagnostics/tables/feature_variance_summary.csv`
- `outputs/diagnostics/tables/near_constant_features.csv`
- `outputs/diagnostics/tables/duplicate_feature_pairs.csv`
- `outputs/diagnostics/tables/high_collinearity_pairs.csv`
- `outputs/diagnostics/tables/feature_target_correlation_summary.csv`
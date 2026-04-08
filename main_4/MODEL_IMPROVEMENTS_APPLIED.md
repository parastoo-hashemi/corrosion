# Model Improvements Applied

## Changes Made

- added hidden-damage feature-set cleanup with near-constant, duplicate, and high-collinearity filtering
- added hidden-damage feature-family ablations and robustness-aware model selection across split strategies
- allowed metadata-only hidden-damage models into final selection because they were more robust than image-heavy alternatives
- regenerated degradation outputs from the improved hidden-damage stage
- added raw-vs-monotone degradation trajectory artifacts and richer proxy threshold-status summaries

## Files Changed

- `MODEL_IMPROVEMENT_PLAN.md`
- `configs/modeling.yaml`
- `src/corrosion_proxy_rul/feature_engineering.py`
- `src/corrosion_proxy_rul/evaluation.py`
- `src/corrosion_proxy_rul/models_hidden_damage.py`
- `src/corrosion_proxy_rul/models_degradation.py`
- `src/corrosion_proxy_rul/models_rul_proxy.py`
- `src/corrosion_proxy_rul/reporting.py`
- `src/corrosion_proxy_rul/diagnostics.py`
- `run_model_improvement_analysis.py`

## Stages Rerun

- `conda run -n env python train_hidden_damage_models.py`
- `conda run -n env python train_degradation_models.py`
- `conda run -n env python train_rul_proxy_models.py`
- `conda run -n env python run_diagnostics_visualizations.py`
- `conda run -n env python run_model_improvement_analysis.py`

## Outputs Regenerated

- `outputs/models/hidden_damage/*`
- `outputs/models/degradation/*`
- `outputs/models/proxy_rul/*`
- `outputs/diagnostics/*`
- `outputs/improvements/tables/*`
- `SCIENTIFIC_REPORT.md`

## Before vs After Snapshot

| target              | strategy                | baseline_model_name   | baseline_feature_set_name   | baseline_target_transform   | baseline_n_features   |   baseline_mae_mean |   baseline_rmse_mean |   baseline_r2_mean |   baseline_spearman_mean | improved_model_name   | improved_feature_set_name   | improved_target_transform   |   improved_n_features |   improved_mae_mean |   improved_rmse_mean |   improved_r2_mean |   improved_spearman_mean |   delta_mae_mean |   delta_rmse_mean |   delta_r2_mean |   delta_spearman_mean |
|:--------------------|:------------------------|:----------------------|:----------------------------|:----------------------------|:----------------------|--------------------:|---------------------:|-------------------:|-------------------------:|:----------------------|:----------------------------|:----------------------------|----------------------:|--------------------:|---------------------:|-------------------:|-------------------------:|-----------------:|------------------:|----------------:|----------------------:|
| wire_area_loss_frac | group_shuffle           | CatBoost              | baseline_full_feature_space | none                        | <NA>                  |           0.0939569 |             0.120865 |          -0.458745 |                0.0569697 | CatBoost              | metadata_only               | none                        |                     8 |            0.123797 |             0.150004 |          -1.22513  |                 0.288791 |       0.0298405  |        0.0291386  |      -0.766382  |             0.231821  |
| wire_area_loss_frac | leave_one_treatment_out | CatBoost              | baseline_full_feature_space | none                        | <NA>                  |           0.12082   |             0.143117 |          -2.50937  |                0.0753968 | CatBoost              | metadata_only               | none                        |                     8 |            0.116063 |             0.141188 |          -1.79444  |                 0.185662 |      -0.00475697 |       -0.00192847 |       0.714928  |             0.110266  |
| wire_area_loss_frac | leave_one_campaign_out  | CatBoost              | baseline_full_feature_space | none                        | <NA>                  |           0.141765  |             0.17787  |          -0.829147 |               -0.0934783 | CatBoost              | metadata_only               | none                        |                     8 |            0.120828 |             0.150455 |          -0.321154 |                -0.265712 |      -0.020937   |       -0.0274145  |       0.507993  |            -0.172234  |
| ultimate_load_kn    | group_shuffle           | RandomForest          | baseline_full_feature_space | none                        | <NA>                  |           0.177548  |             0.205846 |           0.59344  |                0.737844  | RandomForest          | metadata_only               | none                        |                     8 |            0.17438  |             0.214164 |           0.51186  |                 0.778265 |      -0.00316806 |        0.00831799 |      -0.0815805 |             0.0404206 |
| ultimate_load_kn    | leave_one_treatment_out | RandomForest          | baseline_full_feature_space | none                        | <NA>                  |           0.20668   |             0.245752 |          -4.81235  |               -0.132484  | RandomForest          | metadata_only               | none                        |                     8 |            0.203404 |             0.24335  |          -4.07909  |                 0.121699 |      -0.00327619 |       -0.00240211 |       0.733258  |             0.254183  |
| ultimate_load_kn    | leave_one_campaign_out  | RandomForest          | baseline_full_feature_space | none                        | <NA>                  |           0.697547  |             0.730755 |         -10.6494   |                0.223029  | RandomForest          | metadata_only               | none                        |                     8 |            0.564247 |             0.600173 |          -6.82556  |                 0.353145 |      -0.133301   |       -0.130582   |       3.82385   |             0.130115  |

## What Improved

- `ultimate_load_kn` improved cleanly on absolute error across all three split strategies, with the largest gain under leave-one-campaign-out.
- `wire_area_loss_frac` improved on leave-one-treatment-out and leave-one-campaign-out MAE, and grouped Spearman improved materially from a near-zero baseline.
- both final hidden-damage models now use an explicit 8-feature metadata-only subset instead of the broader baseline feature space.

## What Did Not Improve Cleanly

- `wire_area_loss_frac` grouped MAE worsened after the robustness-oriented cleanup, so this should be treated as a trade-off rather than a net score win.
- `wire_area_loss_frac` leave-one-campaign-out Spearman became more negative even though MAE improved, so ranking quality remains unreliable.
- the stronger hidden-damage robustness comes from metadata-dominant models, not from stronger image-based structural inference.

## Unresolved Weaknesses

- `wire_area_loss_frac` remains weak in absolute predictive terms even though robustness improved
- leave-one-campaign-out still fails badly enough that no deployment-grade hidden-damage claim is justified
- the current best structural models rely on metadata-only feature sets, which shows that image features are not yet adding robust structural signal
- degradation and proxy stages remain descriptive / exploratory downstream analyses
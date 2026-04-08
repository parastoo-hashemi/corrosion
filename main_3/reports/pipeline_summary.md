# Pipeline Summary

## Dataset
- Canonical rows: **792**
- Specimens: **48**
- Campaigns: **2**
- Structural rows: **48**

## Corrosion Models
### Regression
| strategy      | fold_id   | holdout_group   | model                  | target                 | task       |   n_train |   n_test |     mae |    rmse |       r2 |
|:--------------|:----------|:----------------|:-----------------------|:-----------------------|:-----------|----------:|---------:|--------:|--------:|---------:|
| group_shuffle | fold_00   | mixed_specimens | linear_regression      | surface_total_rust_pct | regression |       633 |      159 | 2.52101 | 4.05582 | 0.409651 |
| group_shuffle | fold_00   | mixed_specimens | random_forest          | surface_total_rust_pct | regression |       633 |      159 | 1.38135 | 3.14167 | 0.645779 |
| group_shuffle | fold_00   | mixed_specimens | hist_gradient_boosting | surface_total_rust_pct | regression |       633 |      159 | 1.54058 | 2.8988  | 0.698429 |
| group_shuffle | fold_00   | mixed_specimens | mlp_regressor          | surface_total_rust_pct | regression |       633 |      159 | 2.76254 | 4.84389 | 0.157945 |
| group_shuffle | fold_00   | mixed_specimens | linear_regression      | peak_rust_pct          | regression |       633 |      159 | 5.66663 | 8.54014 | 0.595233 |
| group_shuffle | fold_00   | mixed_specimens | random_forest          | peak_rust_pct          | regression |       633 |      159 | 4.27183 | 7.60827 | 0.678747 |
| group_shuffle | fold_00   | mixed_specimens | hist_gradient_boosting | peak_rust_pct          | regression |       633 |      159 | 4.57593 | 7.36108 | 0.699283 |
| group_shuffle | fold_00   | mixed_specimens | mlp_regressor          | peak_rust_pct          | regression |       633 |      159 | 4.20869 | 6.23376 | 0.784337 |

### Classification
| strategy      | fold_id   | holdout_group   | model                  | target                      | task           |   n_train |   n_test |   accuracy |   macro_f1 |
|:--------------|:----------|:----------------|:-----------------------|:----------------------------|:---------------|----------:|---------:|-----------:|-----------:|
| group_shuffle | fold_00   | mixed_specimens | logistic_regression    | surface_total_rust_category | classification |       633 |      159 |   0.830189 |   0.573375 |
| group_shuffle | fold_00   | mixed_specimens | random_forest          | surface_total_rust_category | classification |       633 |      159 |   0.786164 |   0.414439 |
| group_shuffle | fold_00   | mixed_specimens | hist_gradient_boosting | surface_total_rust_category | classification |       633 |      159 |   0.798742 |   0.477041 |
| group_shuffle | fold_00   | mixed_specimens | mlp_classifier         | surface_total_rust_category | classification |       633 |      159 |   0.792453 |   0.42997  |
| group_shuffle | fold_00   | mixed_specimens | logistic_regression    | peak_rust_category          | classification |       633 |      159 |   0.578616 |   0.528961 |
| group_shuffle | fold_00   | mixed_specimens | random_forest          | peak_rust_category          | classification |       633 |      159 |   0.597484 |   0.476052 |
| group_shuffle | fold_00   | mixed_specimens | hist_gradient_boosting | peak_rust_category          | classification |       633 |      159 |   0.622642 |   0.517318 |
| group_shuffle | fold_00   | mixed_specimens | mlp_classifier         | peak_rust_category          | classification |       633 |      159 |   0.591195 |   0.531318 |

## Damage Models
| strategy      | fold_id   | holdout_group   | model                  | target             | task       |   n_train |   n_test |      mae |     rmse |        r2 |
|:--------------|:----------|:----------------|:-----------------------|:-------------------|:-----------|----------:|---------:|---------:|---------:|----------:|
| group_shuffle | fold_00   | mixed_specimens | random_forest          | wire_area_loss_pct | regression |        38 |       10 | 3.8993   | 4.99541  |  0.310377 |
| group_shuffle | fold_00   | mixed_specimens | extra_trees            | wire_area_loss_pct | regression |        38 |       10 | 5.44366  | 7.13752  | -0.407874 |
| group_shuffle | fold_00   | mixed_specimens | hist_gradient_boosting | wire_area_loss_pct | regression |        38 |       10 | 5.59846  | 6.95256  | -0.335854 |
| group_shuffle | fold_00   | mixed_specimens | mlp_regressor          | wire_area_loss_pct | regression |        38 |       10 | 5.90776  | 7.00087  | -0.354483 |
| group_shuffle | fold_00   | mixed_specimens | random_forest          | ultimate_load_kn   | regression |        38 |       10 | 0.120685 | 0.168166 |  0.384537 |
| group_shuffle | fold_00   | mixed_specimens | extra_trees            | ultimate_load_kn   | regression |        38 |       10 | 0.144564 | 0.163474 |  0.418402 |
| group_shuffle | fold_00   | mixed_specimens | hist_gradient_boosting | ultimate_load_kn   | regression |        38 |       10 | 0.256842 | 0.286931 | -0.791759 |
| group_shuffle | fold_00   | mixed_specimens | mlp_regressor          | ultimate_load_kn   | regression |        38 |       10 | 0.43849  | 0.545455 | -5.47502  |

## RUL Summary
- Low risk specimens: **20**
- Moderate risk specimens: **8**
- High risk specimens: **20**
- Critical specimens: **0**
- Median proxy-RUL (weeks): **0.00**

## Figures
- `corrosion_regression`: `/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/corrosion_regression_parity.png`
- `corrosion_metrics`: `/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/corrosion_model_mae.png`
- `corrosion_classification`: `/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/corrosion_model_macro_f1.png`
- `damage_regression`: `/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/damage_regression_parity.png`
- `damage_metrics`: `/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/damage_model_mae.png`
- `risk_distribution`: `/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/risk_distribution.png`
- `rul_histogram`: `/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/rul_histogram.png`
- `degradation_examples`: `/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/degradation_examples_peak_rust.png`

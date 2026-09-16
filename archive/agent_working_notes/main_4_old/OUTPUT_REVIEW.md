# Output Review

## Scope

This review inspects the generated pipeline outputs under `outputs/` plus the generated reporting files `README.md` and `SCIENTIFIC_REPORT.md`. The goal is not to confirm that files exist, but to judge whether the outputs support scientifically defensible claims.

## Outputs Found

- Audit and validation: `outputs/audit/*`
- Cleaned data tables: `outputs/data/*`
- EDA tables and figures: `outputs/eda/tables/*`, `outputs/eda/figures/*`
- Image features: `outputs/features/*`
- Split manifests: `outputs/splits/*`, `outputs/models/*/splits/*`
- Surface-model outputs: `outputs/models/surface/*`
- Hidden-damage outputs: `outputs/models/hidden_damage/*`
- Degradation outputs: `outputs/models/degradation/*`
- Proxy-RUL outputs: `outputs/models/proxy_rul/*`
- Run logs: `outputs/logs/*`
- Generated summaries: `README.md`, `SCIENTIFIC_REPORT.md`

`OUTPUT_INVENTORY.csv` contains the file-level inventory and artifact status labels.

## What Ran Successfully

- Validated finding: the full pipeline completed end to end. Evidence: `outputs/logs/run_full_baseline.log`, `outputs/logs/run_audit_validation.log`, `outputs/logs/run_eda.log`, `outputs/logs/run_extract_image_features.log`, `outputs/logs/train_surface_models.log`, `outputs/logs/train_hidden_damage_models.log`, `outputs/logs/train_degradation_models.log`, `outputs/logs/train_rul_proxy_models.log`.
- Validated finding: the validated master dataset, terminal structural subset, image feature table, split manifests, model summaries, degradation outputs, and proxy-RUL outputs were all generated. Evidence: `outputs/data/master_table.csv`, `outputs/data/terminal_structural_table.csv`, `outputs/features/image_features.csv`, `outputs/splits/*`, `outputs/models/**/*`.

## Data Validity

- Validated finding: row counts are internally consistent across the main audit artifacts. Evidence:
  - `outputs/audit/verified_facts.json`: `aligned_rows = 791`, `unique_specimens = 48`, `image_files = 792`, `structural_rows = 48`
  - `outputs/eda/tables/row_counts.csv`: `rows = 791`, `unique_specimens = 48`, `images_used = 791`
  - `outputs/data/master_table.csv`: 791 rows
  - `outputs/data/terminal_structural_table.csv`: 48 rows, 48 unique specimens
- Validated finding: the grouped unit is implemented consistently as `specimen_id`, and the terminal structural table contains exactly one structural row per specimen. Evidence: `outputs/data/terminal_structural_table.csv`, `outputs/splits/master_*_summary.csv`, `outputs/models/hidden_damage/splits/*_summary.csv`.
- Validated finding: image-table alignment looks correct for the usable data. Evidence:
  - `outputs/audit/image_scan.csv`: 791 readable images, 1 unreadable image
  - `outputs/audit/issues_log.csv`: one logged issue, `E01-20240508-17W.png`
  - `outputs/data/master_table.csv`: all aligned rows have `image_readable = True`, `image_error` empty
- Validated finding: specimen parsing appears correct. `specimen_id` and `specimen_id_from_name` agree for all aligned rows in `outputs/data/master_table.csv`.
- Validated finding: treatment/campaign reconstruction joined without missing specimen mappings. Evidence: `outputs/audit/specimen_mapping_validated.csv`, `outputs/data/master_table.csv`.
- Tentative interpretation: image geometry is almost uniform, but not perfectly uniform. Two campaign-1 images have heights `643` and `630` instead of `650`, which could matter for strip-location features if preprocessing assumes fixed framing. Evidence: `outputs/data/master_table.csv` for `S1MI01-20220616-4W` and `S1MI01-20221206-28W`.

## Leakage and Evaluation Validity

- Validated finding: the split manifests are leakage-safe at the specimen level. All summary files report `leakage_detected = False`. Evidence:
  - `outputs/splits/master_group_shuffle_summary.csv`
  - `outputs/splits/master_leave_one_treatment_out_summary.csv`
  - `outputs/splits/master_leave_one_campaign_out_summary.csv`
  - `outputs/models/surface/splits/*_summary.csv`
  - `outputs/models/hidden_damage/splits/*_summary.csv`
- Validated finding: `GroupShuffleSplit` here is repeated grouped holdout, not disjoint full-coverage cross-validation. Evidence:
  - `outputs/models/surface/surface_total_rust_pct/group_shuffle/surface_total_rust_pct_predictions.csv`: 815 prediction rows but only 563 unique samples for the selected model
  - `outputs/models/hidden_damage/wire_area_loss_frac/group_shuffle/wire_area_loss_frac_predictions.csv`: 50 prediction rows but only 34 unique samples for the selected model
- Weak assumption: because `GroupShuffleSplit` repeats overlapping test sets, fold means and standard deviations are informative but not independent confidence intervals.

## Feature Validity

- Validated finding: the image feature table is complete and readable. Evidence: `outputs/features/image_features.csv`, `outputs/features/image_feature_failures.csv`.
- Validated finding: some engineered features are degenerate or unstable:
  - `img_strip_count` is constant (`47`) for all rows. Evidence: `outputs/features/image_features.csv`.
  - `img_contrast` is numerically identical to `img_brightness_std` for all rows. Evidence: `outputs/features/image_features.csv`.
  - `img_edge_to_center_rust_ratio` is extremely unstable: 99th percentile about `1.14e5`, maximum about `2.03e6`. Evidence: `outputs/features/image_features.csv`.
- Tentative interpretation: `img_edge_to_center_rust_ratio` is probably exploding because its denominator approaches zero in low-rust images. That matters because it appears among the most important hidden-damage features. Evidence:
  - `outputs/features/image_features.csv`
  - `outputs/models/hidden_damage/wire_area_loss_frac/group_shuffle/wire_area_loss_frac_feature_importance.csv`
- Validated finding: the main rust-area image feature reproduces the workbook surface-area label almost exactly. Across all 791 aligned rows:
  - `MAE(surface_total_rust_pct, img_rust_area_ratio_pct) = 0.000228`
  - maximum absolute difference is below `0.0005`
  - all 791 rows are within `0.001`
  Evidence: `outputs/data/master_table.csv`, `outputs/features/image_features.csv`, `outputs/data/full_feature_table.csv`.
- Weak/invalid result: because `surface_total_rust_pct` is numerically equivalent to `img_rust_area_ratio_pct`, the `surface_total_rust_pct` model benchmark is not an independent predictive achievement. It is effectively label reconstruction from a feature generated by the same threshold logic. Evidence:
  - `outputs/models/surface/surface_total_rust_pct/group_shuffle/surface_total_rust_pct_feature_importance.csv`
  - `outputs/models/surface/surface_total_rust_pct/group_shuffle/surface_total_rust_pct_summary.csv`
- Tentative interpretation: `peak_rust_pct` is also partly tautological, but less strictly. `img_strip_rust_max_pct` tracks it strongly (`Spearman ≈ 0.988`, `MAE ≈ 3.05`) without exact equality. Evidence: `outputs/data/master_table.csv`, `outputs/features/image_features.csv`.

## Model Validity

### Surface Models

- Validated finding: the nominal best surface model is `GradientBoosting` for both reported targets. Evidence: `outputs/models/surface/best_models.csv`.
- Validated finding: the surface metrics are numerically very strong even under leave-one-campaign-out. Evidence:
  - `outputs/models/surface/surface_total_rust_pct/group_shuffle/surface_total_rust_pct_summary.csv`
  - `outputs/models/surface/surface_total_rust_pct/leave_one_campaign_out/surface_total_rust_pct_summary.csv`
  - `outputs/models/surface/peak_rust_pct/group_shuffle/peak_rust_pct_summary.csv`
  - `outputs/models/surface/peak_rust_pct/leave_one_campaign_out/peak_rust_pct_summary.csv`
- Weak/invalid result: those strong surface results should not be presented as major scientific evidence without the tautology caveat above. The strongest target is nearly identical to an input feature, and the second target is heavily derived from related strip features.
- Validated finding: error variance is not trivial on high-rust cases. `surface_total_rust_pct` has `mae_std = 0.2928`, larger than its mean `0.1705`, and the worst held-out errors are concentrated on severe-rust specimens such as `D04` and `S2SA03`. Evidence:
  - `outputs/models/surface/surface_total_rust_pct/group_shuffle/surface_total_rust_pct_summary.csv`
  - `outputs/models/surface/surface_total_rust_pct/group_shuffle/surface_total_rust_pct_predictions.csv`

### Hidden-Damage Models

- Validated finding: the structural targets are extremely sparse and terminal-only. Evidence:
  - `outputs/eda/tables/structural_target_sparsity.csv`
  - `outputs/data/terminal_structural_table.csv`
- Validated finding: `CatBoost` is the nominal best model for both structural targets by mean MAE. Evidence: `outputs/models/hidden_damage/best_models.csv`.
- Validated finding: `wire_area_loss_frac` performance is weak despite modest MAE:
  - grouped MAE about `0.0866`
  - grouped Spearman only about `0.110`
  - grouped fold-level `R^2` is often negative
  Evidence:
  - `outputs/models/hidden_damage/wire_area_loss_frac/group_shuffle/wire_area_loss_frac_summary.csv`
  - `outputs/models/hidden_damage/wire_area_loss_frac/group_shuffle/wire_area_loss_frac_fold_metrics.csv`
- Weak/invalid result: `wire_area_loss_frac` should not be claimed as a reliable predictive model. The low MAE mostly reflects limited target spread and regression toward the mean, not strong ranking or variance capture.
- Validated finding: `ultimate_load_kn` looks moderately learnable in grouped holdout but fails badly under leave-one-campaign-out:
  - grouped MAE about `0.175`, Spearman about `0.765`
  - leave-one-campaign-out MAE about `0.682`, `R^2 ≈ -10.0`, Spearman about `0.216`
  Evidence:
  - `outputs/models/hidden_damage/ultimate_load_kn/group_shuffle/ultimate_load_kn_summary.csv`
  - `outputs/models/hidden_damage/ultimate_load_kn/leave_one_campaign_out/ultimate_load_kn_summary.csv`
  - `outputs/models/hidden_damage/ultimate_load_kn/leave_one_campaign_out/ultimate_load_kn_fold_metrics.csv`
- Validated finding: the structural results are heavily confounded with campaign/time/mesh variables. Evidence:
  - `outputs/models/hidden_damage/ultimate_load_kn/group_shuffle/ultimate_load_kn_feature_importance.csv`
  - `outputs/data/terminal_structural_table.csv` shows strong campaign-level structural differences
- Strong negative result: the leave-one-campaign-out collapse is scientifically meaningful. It shows the current hidden-damage models do not support robust cross-campaign predictive claims.

## Degradation Modelling Validity

- Validated finding: all 48 specimens received a fitted degradation family. Evidence: `outputs/models/degradation/degradation_best_fits.csv`, `outputs/logs/train_degradation_models.log`.
- Validated finding: the fitted family counts are dominated by `monotone_isotonic` (`40/48`), with `linear` (`6/48`) and `gompertz` (`2/48`) selected rarely. Evidence: `outputs/models/degradation/degradation_best_fits.csv`.
- Validated finding: the degradation input signal is noisy and non-monotone before smoothing. Across specimens, the raw predicted hidden-damage trajectories decrease repeatedly within specimen, with a mean of about `7.9` decreases per specimen. Evidence: `outputs/models/degradation/full_feature_table_with_hidden_damage_proxy.csv`.
- Validated finding: the hidden-damage proxy used for degradation is in-sample optimistic at the terminal points:
  - terminal in-sample MAE is about `0.0037`
  - grouped held-out MAE for the same target is about `0.0866`
  Evidence:
  - `outputs/models/degradation/full_feature_table_with_hidden_damage_proxy.csv`
  - `outputs/models/hidden_damage/wire_area_loss_frac/group_shuffle/wire_area_loss_frac_summary.csv`
  - `outputs/models/hidden_damage/wire_area_loss_frac/group_shuffle/wire_area_loss_frac_predictions.csv`
- Weak/invalid result: the degradation stage is descriptive smoothing of model-generated latent trajectories, not validated prognostics.
- Weak/invalid result: the selected family should not be overinterpreted as a physically identified law. `monotone_isotonic` often achieves near-zero RMSE by interpolation, so the model-selection rule favors a flexible smoother rather than a mechanistic curve family. Evidence:
  - `outputs/models/degradation/degradation_fit_candidates.csv`
  - `outputs/models/degradation/degradation_best_fits.csv`

## Proxy-RUL Validity

- Validated finding: the proxy-RUL stage ran and produced threshold tables. Evidence: `outputs/models/proxy_rul/proxy_rul_estimates.csv`, `outputs/models/proxy_rul/proxy_rul_summary.csv`, `outputs/logs/train_rul_proxy_models.log`.
- Validated finding: the outputs are mostly censoring-status summaries, not future time-to-threshold predictions:
  - for every non-censored row, `proxy_rul_days = 0`
  - no non-censored threshold crossing occurs after the last observed day
  Evidence: `outputs/models/proxy_rul/proxy_rul_estimates.csv`
- Validated finding: threshold `0.2` is already reached at baseline for `32/48` specimens and by the last observation for `45/48` specimens. Evidence:
  - `outputs/models/proxy_rul/proxy_rul_estimates.csv`
  - `outputs/models/degradation/full_feature_table_with_hidden_damage_proxy.csv`
- Validated finding: baseline predicted hidden damage is already high even when visible surface rust is zero or near zero. At week 0, the mean predicted hidden-damage fraction is about `0.2035`. Evidence: `outputs/models/degradation/full_feature_table_with_hidden_damage_proxy.csv`.
- Weak/invalid result: the current proxy-RUL outputs are too fragile for decision support. They do not provide forward-looking residual life; they mainly say whether an arbitrary threshold has already been crossed within the observed window.
- Weak assumption: the thresholds `0.2`, `0.3`, and `0.4` are explicit and useful for exploration, but they are not calibrated to observed failure events in these outputs.

## Figure Quality

Figure usefulness here is judged from the paired tables and the scientific role of each plot. A separate manual visual-polish check is still advisable.

- Useful now:
  - `outputs/eda/figures/missingness.png`
  - `outputs/eda/figures/structural_target_sparsity.png`
  - `outputs/eda/figures/target_distributions.png`
  - `outputs/eda/figures/surface_rust_by_campaign.png`
  - `outputs/eda/figures/cross_campaign_peak_rust.png`
- Appendix only / low value as main figures:
  - `outputs/eda/figures/row_counts.png`
  - `outputs/eda/figures/campaign_counts.png`
  - `outputs/eda/figures/treatment_counts.png`
  - `outputs/eda/figures/week_distribution.png`
- Review before presentation:
  - `outputs/eda/figures/within_specimen_surface_total_rust.png` because one multi-specimen trajectory figure can easily become cluttered with 48 lines
  - `outputs/models/degradation/degradation_subset_trajectories.png` because it is not paired with the raw unsmoothed latent trajectories
- Not suitable as headline evidence in the current form:
  - `outputs/models/surface/*/*/*feature_importance.png` because the underlying task is partly tautological
  - `outputs/models/proxy_rul/proxy_rul_right_censored.png` because the proxy-RUL stage is exploratory only

### Figures That Should Be Added Next

- Surface label versus `img_rust_area_ratio_pct` parity plot to expose the near-identity directly.
- Actual-versus-predicted scatter plots for `wire_area_loss_frac` and `ultimate_load_kn`, split by evaluation regime.
- Week-0 predicted hidden-damage distribution by treatment/campaign.
- Raw hidden-damage proxy trajectory versus monotone-smoothed fit for representative specimens.
- Threshold-crossing timeline heatmap showing baseline-crossed, crossed-during-observation, and censored specimens.

## Strongest Findings

- Validated finding: the data audit is solid. Counts, specimen parsing, terminal-row extraction, mapping join, and split leakage checks are internally consistent. Evidence: `outputs/audit/verified_facts.json`, `outputs/data/master_table.csv`, `outputs/data/terminal_structural_table.csv`, `outputs/splits/*_summary.csv`.
- Validated finding: the negative leave-one-campaign-out results for structural targets are scientifically useful. They show that hidden-damage inference is currently confounded and not deployment-ready. Evidence: `outputs/models/hidden_damage/*/leave_one_campaign_out/*_summary.csv`.
- Validated finding: the surface feature extraction is strong as an audit/reconstruction tool. It reproduces the workbook surface-area label almost exactly. Evidence: `outputs/features/image_features.csv`, `outputs/data/master_table.csv`.

## Weakest Findings

- Weak/invalid result: the `surface_total_rust_pct` benchmark is not an independent ML result; it is essentially reconstructing a target-equivalent engineered feature.
- Weak/invalid result: the `wire_area_loss_frac` model is too weak in ranking and variance capture for strong claims. Evidence: `outputs/models/hidden_damage/wire_area_loss_frac/group_shuffle/wire_area_loss_frac_summary.csv`.
- Weak/invalid result: the degradation stage is mostly monotone smoothing of noisy in-sample hidden-damage proxies, not validated predictive degradation modelling. Evidence: `outputs/models/degradation/full_feature_table_with_hidden_damage_proxy.csv`, `outputs/models/degradation/degradation_fit_candidates.csv`.
- Weak/invalid result: the proxy-RUL stage currently yields no positive future residual-life predictions for non-censored cases. Evidence: `outputs/models/proxy_rul/proxy_rul_estimates.csv`.
- Validated finding: earlier generated report text overstated the surface and proxy-RUL stages; that language should remain corrected in any regenerated report.

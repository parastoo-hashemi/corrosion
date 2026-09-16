# Next Steps Plan

## 1. Immediate Fixes

1. Reframe the surface stage as a label-reconstruction sanity check, not as a standalone predictive success.
   Evidence: `outputs/data/master_table.csv` versus `outputs/features/image_features.csv` shows `surface_total_rust_pct` is nearly identical to `img_rust_area_ratio_pct`.
2. Remove or neutralize degenerate image features before any next benchmark.
   Immediate candidates:
   - drop `img_strip_count` because it is constant
   - collapse `img_contrast` into `img_brightness_std` because they are identical
   - cap, log-transform, or drop `img_edge_to_center_rust_ratio` because it is numerically unstable
3. Downgrade all proxy-RUL claims to “exploratory threshold-status analysis”.
   Evidence: `outputs/models/proxy_rul/proxy_rul_estimates.csv` has `proxy_rul_days = 0` for every non-censored case.
4. Rewrite `SCIENTIFIC_REPORT.md` before sharing it.
   It currently reports nominal best models but does not foreground the tautological surface benchmark, the weak structural ranking performance, or the zero-valued proxy-RUL outputs.

## 2. Validation Checks Still Needed

1. Verify from the thesis/workbook whether `surface_total_rust_pct` was generated from the same rust-mask logic used in feature extraction.
   If yes, the current surface benchmark should be explicitly marked as reconstruction, not prediction.
2. Manually inspect a sample of images for strip orientation and peak-location alignment.
   Priority:
   - random low-rust images
   - random high-rust images
   - `S1MI01-20220616-4W`
   - `S1MI01-20221206-28W`
3. Check whether baseline hidden-damage predictions are physically plausible.
   At week 0, many specimens already have predicted wire-area-loss fractions near or above `0.2`, even when visible rust is essentially zero.
4. Validate the effect of campaign confounding explicitly with treatment-level and campaign-level residual analyses for the structural targets.
5. Confirm whether the proxy thresholds `0.2`, `0.3`, and `0.4` have any domain justification beyond exploratory use.

## 3. Code Changes Needed

1. Save the exact feature list used by each trained model.
   The current feature tables include targets and identifiers, so the artifact contract is not self-documenting.
2. Export fully explicit out-of-fold predictions for the structural target models and use those out-of-fold values, not in-sample refits, as the basis for any degradation modelling experiment.
3. Prefer full-coverage group validation for the structural stage where possible.
   `GroupShuffleSplit` is acceptable, but it leaves many labeled specimens unevaluated in a given run.
4. Add an automatic feature-QC report.
   It should flag:
   - constant columns
   - duplicate columns
   - near-infinite or heavy-tail ratios
   - columns with extreme zero inflation
5. Separate “analysis tables” from “model-ready X matrices”.
   `surface_feature_table.csv` and `hidden_damage_feature_table.csv` currently mix features, targets, and identifiers in one artifact.
6. Add raw-versus-smoothed degradation artifacts.
   Without them, the monotone fitting step hides how non-monotone the latent proxy is before smoothing.

## 4. Reporting Changes Needed

1. Rewrite `SCIENTIFIC_REPORT.md` so the strongest negative findings are stated before the nominal best-model names.
2. Add a short “validated / tentative / weak-or-invalid” table to the scientific report.
3. Add a dedicated “Why direct RUL is still not supported” section to the report close-out, even though the pipeline avoided direct RUL training.
4. Add a “downstream optimism risk” note explaining that degradation/proxy outputs were generated from in-sample hidden-damage refits, not out-of-fold structural predictions.
5. Use the leave-one-campaign-out structural results as a central limitation, not a footnote.

## 5. Analysis and Visualization Improvements Needed

1. Create a parity plot of `surface_total_rust_pct` versus `img_rust_area_ratio_pct`.
   This should be shown internally before any surface-model benchmark is presented.
2. Create actual-versus-predicted scatter plots for:
   - `wire_area_loss_frac`
   - `ultimate_load_kn`
   Each should be shown for grouped holdout and leave-one-campaign-out.
3. Plot the week-0 hidden-damage proxy distribution by treatment/campaign.
   This will make the current threshold problem obvious.
4. Plot raw latent hidden-damage trajectories and monotone-smoothed trajectories together for representative specimens.
5. Replace the current proxy-RUL summary figure with a threshold-status figure that distinguishes:
   - already crossed at baseline
   - crossed during observation
   - not crossed by the end of observation
6. Add campaign-level terminal structural boxplots.
   These will help explain why leave-one-campaign-out generalization is poor.

## 6. What Is Ready To Show a Professor Now

1. `OUTPUT_REVIEW.md`
2. `NEXT_STEPS_PLAN.md`
3. `PROJECT_CONSTRAINTS.md`
4. `outputs/audit/verified_facts.json`
5. `outputs/eda/tables/specimen_summary.csv`
6. `outputs/eda/tables/structural_target_sparsity.csv`
7. `outputs/eda/figures/missingness.png`
8. `outputs/eda/figures/structural_target_sparsity.png`
9. `outputs/models/hidden_damage/wire_area_loss_frac/leave_one_campaign_out/wire_area_loss_frac_summary.csv`
10. `outputs/models/hidden_damage/ultimate_load_kn/leave_one_campaign_out/ultimate_load_kn_summary.csv`
11. `outputs/models/proxy_rul/proxy_rul_summary.csv`, but only as evidence that the current proxy-RUL stage is exploratory and weak

## 7. What Is Not Ready To Show Yet

1. `SCIENTIFIC_REPORT.md` in its current form.
2. The surface benchmark tables and feature-importance plots as headline evidence.
   They need the “label reconstruction” caveat attached first.
3. `outputs/models/degradation/degradation_best_fits.csv` and `outputs/models/degradation/degradation_subset_trajectories.png` as if they identify physical degradation laws.
4. `outputs/models/proxy_rul/proxy_rul_estimates.csv` and `outputs/models/proxy_rul/proxy_rul_right_censored.png` as if they provide actionable remaining life.
5. `outputs/models/degradation/full_feature_table_with_hidden_damage_proxy.csv` as a validated prognostic table.
6. The hidden-damage feature-importance plots as mechanistic explanations.
   They are too exposed to campaign confounding and unstable engineered ratios.

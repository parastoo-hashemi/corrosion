# Figure audit for v3

## Scope, method and outcome

All **30 files** were opened and inspected: **16** in `emiling/main_3/`, **6** at the top of `emiling/main_4/` (the task’s count of five was stale), and **8** Ridge diagnostics. The two PDFs contain **13 pages**, all viewed. The 28 PNGs were compared with their canonical saved outputs: every PNG is byte-identical to its corresponding canonical PNG. Hashes are in `report_v2/evidence/v3/candidate_inventory.json`.

**Decision: four candidate files survive, consolidated into three new figures; 26 are rejected.** All four surviving files require regeneration. The most common primary rejection reason is redundancy (**16 of 26**); eight have a substantive defensibility problem, one has unresolved raw-to-montage provenance, and one is better handled as a generation-specific scope clarification. No scientific result is inferred solely from a filename.

New shared assets: `ridge_terminal_diagnostics` (R-06 + R-07), `ridge_coefficients` (R-03), and `ridge_learning_curve` (R-04). The thesis uses all three. Article integration is limited to the central absolute-error diagnostic if it fits the five-page contribution; the coefficient and learning-curve analyses belong in the thesis.

### Verification and reproduction boundary

`report_v2/scripts/audit_saved_figures.py` checks numeric inputs and replays **18 pure plotting functions** against saved tables, without importing training orchestration or fitting models. **15 replays are pixel-identical** to the candidates. R-01 and R-07 include random strip jitter; their replay pixels differ. M4-05 also differs in rendering, so pixel reproduction is not asserted for it. Exact per-file outcomes and all input hashes are in `report_v2/evidence/v3/figure_checks.json`. Canonical PNG identity alone is not independent numerical validation.

The meeting-report montage/panel generators were not found. For those files, the audit distinguishes checked underlying tables from an unverified exact plotting recipe. Both manuscript PDFs differ from same-name canonical PDFs in normalized extracted text as well as bytes; they were inspected as earlier drafts, not asserted to be exact rebuilds. No expensive pipeline or historical model was rerun. Current source corruption involving `main_first` remains untouched.

All eight v2 figures were checked against their actual uses in the v2 thesis/article: dataset_supervision, evaluation_regimes, label_adjacency, capacity_ablation, robustness_synthesis, confounding, threshold_status and paired_specimen_errors. A figure can be rejected for repeating an existing table or paragraph even when its geometry differs. Conversely, the baseline parity is not a duplicate of the paired HSV comparison: they answer different questions.

### Scope discrepancy found and resolved

M3-12’s weak correlations are real for the earlier `main_3` features. Independent recomputation gives Pearson 0.257148, 0.182837 and 0.247840. The near-identity result in v2 concerns the later `main_4` rust-area feature, a different representation. v3 explicitly says so in its surface-results discussion; the earlier result neither invalidates the later join nor supports extending its near-identity claim to all generations.

The Ridge parity uses the mean prediction per specimen. Its mean absolute error is 0.171941 kN, whereas the primary result remains mean fold MAE 0.172711 kN. The v2 paired diagnostic first averages absolute errors per specimen; its metadata baseline is 0.172733 kN. These are different aggregations, not inconsistent scores. All 48 specimens and the complete observed 1.60–2.87 kN range are retained in the new parity axes.

## File-by-file decisions

### M3-01 — `emiling/main_3/corrosion_condition_pipeline_ieee.pdf`

**Viewed:** An eight-page two-column manuscript, not a standalone schematic. Page 3 contains the dataset panel and a seven-stage pipeline; page 6 has historical MAE bars and threshold tables; page 7 has trajectories and risk counts.

**Source and verification:** main_3/reports/corrosion_condition_pipeline_ieee.tex; embedded assets in main_3/reports/figures/ and main_3/reports/meeting_report/figures/. Same-name canonical PDF differs in both bytes and normalized extracted text; its exact editing/compilation history is not established.

**Redundancy check:** The dataset and workflow repeat dataset_supervision/evaluation_regimes; embedded MAE, trajectory and risk figures are also audited individually below.

**Decision: reject.** The historical manuscript contributes no distinct central diagnostic. Its 792-row historical basis and older threshold scheme cannot be imported as the refined 791-row experiment. All eight pages were viewed; no page is silently treated as a reusable figure.

### M3-02 — `emiling/main_3/corrosion_distributions.png`

**Viewed:** Three panels show strongly right-skewed total-rust and peak-rust percentage histograms and counts across four longitudinal peak-location bands. Low-corrosion observations dominate; the first location band has the largest count.

**Source and verification:** main_3/outputs/canonical_dataset.csv (792 rows: surface_total_rust_pct, peak_rust_pct, peak_rust_location_cm). Meeting-report panel generator not found; saved values, schema, and ranges checked, but exact bin-edge recipe was not reconstructed.
Canonical PNG SHA-256 matches `main_3/reports/meeting_report/figures/corrosion_distributions.png`.

**Redundancy check:** Dataset/schema discussion and dataset_supervision already establish imbalanced repeated surface observations; this is an older surface-distribution view, not a capacity diagnostic.

**Decision: reject.** Adds historical distribution detail without sharpening the terminal-load argument. The older five-class basis must remain distinct from the prepared four-class branch.

### M3-03 — `emiling/main_3/corrosion_examples.png`

**Viewed:** A three-row gallery pairs original ROI with normalized/mask views for low, medium and high peak-rust examples. The low example has a visually blank white original ROI but a patterned normalized panel; the other two show localized and broader rust.

**Source and verification:** main_3/reports/figures/preprocessing/{G01-20240221-6W,F03-20240417-14W,D05-20240807-30W}.png; main_3/src/visualization/plots.py:create_preprocessing_previews and main_3/src/features/image_processing.py are related preprocessing code. The meeting montage generator was not located, and raw-to-montage fidelity was not reconstructed.
Canonical PNG SHA-256 matches `main_3/reports/meeting_report/figures/corrosion_examples.png`.

**Redundancy check:** No existing report figure is an image gallery, so this is not rejected merely for duplication.

**Decision: reject.** The blank/patterned low-example pair cannot be confidently explained from the montage alone. Without verified raw-image fidelity, it cannot carry a measurement-quality claim; replacing it would require a separate curated raw-image audit.

### M3-04 — `emiling/main_3/corrosion_model_macro_f1.png`

**Viewed:** Grouped bars compare macro-F1 for four classifiers and two historical corrosion-category targets. Scores are moderate, and the legend occupies substantial plot area.

**Source and verification:** main_3/outputs/corrosion_classification_metrics.csv, strategy=group_shuffle; main_3/src/orchestration.py:run_report_stage and src/visualization/plots.py:plot_metric_bars.
Canonical PNG SHA-256 matches `main_3/reports/figures/corrosion_model_macro_f1.png`.
Pure plotting function replayed against saved data; pixels match exactly.

**Redundancy check:** Historical classification and label schemas are already separated in the surface-results chapter; this panel provides no result for the untrained current classifier.

**Decision: reject.** An additional historical leaderboard does not strengthen the selected Ridge finding. It would require an explicit five-class historical caption to avoid suggesting current four-class performance.

### M3-05 — `emiling/main_3/corrosion_model_mae.png`

**Viewed:** Eight bars compare total-rust and peak-rust MAE for four regressors. Total-rust errors are lower, while the two leading peak-rust bars are nearly equal.

**Source and verification:** main_3/outputs/corrosion_regression_metrics.csv, strategy=group_shuffle; run_report_stage and plot_metric_bars. Both targets are percentage errors, although the saved y-axis only says mae.
Canonical PNG SHA-256 matches `main_3/reports/figures/corrosion_model_mae.png`.
Pure plotting function replayed against saved data; pixels match exactly.

**Redundancy check:** The v2 surface-result table and robustness_synthesis already explain grouped accuracy and its evaluation limits; M3-13 repeats these bars.

**Decision: reject.** Duplicates historical benchmark prose/table detail and omits the evaluation and percentage-point labels needed in a standalone caption.

### M3-06 — `emiling/main_3/corrosion_regression_parity.png`

**Viewed:** Four model colours are overlaid in one observed-versus-predicted scatter, including some negative predictions and a dense low-value cluster. The axes identify neither target nor units.

**Source and verification:** main_3/outputs/corrosion_regression_predictions.parquet filtered only on strategy=group_shuffle; run_report_stage passes BOTH surface_total_rust_pct and peak_rust_pct to plot_regression_predictions.
Canonical PNG SHA-256 matches `main_3/reports/figures/corrosion_regression_parity.png`.
Pure plotting function replayed against saved data; pixels match exactly.

**Redundancy check:** Adds a parity view, but for mixed historical surface targets rather than the central terminal-load model.

**Decision: reject.** The plot pools two different targets without distinguishing them. A single dense cloud cannot establish target-specific calibration or a fair improvement over a separate peak-only baseline.

### M3-07 — `emiling/main_3/damage_model_mae.png`

**Viewed:** Paired bars show small ultimate-load errors beside much larger wire-loss errors on one numerical MAE axis. Four model families are compared.

**Source and verification:** main_3/outputs/damage_regression_metrics.csv, strategy=group_shuffle; run_report_stage and plot_metric_bars. Load is in kN and wire loss in percentage points.
Canonical PNG SHA-256 matches `main_3/reports/figures/damage_model_mae.png`.
Pure plotting function replayed against saved data; pixels match exactly.

**Redundancy check:** The historical structural results are already tabulated with explicit units; robustness_synthesis deliberately normalizes each target separately.

**Decision: reject.** Combines incomparable units on one axis and visually suppresses load errors. The existing table and dimensionless robustness comparison are clearer.

### M3-08 — `emiling/main_3/damage_regression_parity.png`

**Viewed:** A shared parity cloud has one cluster near two and another extending into the thirties, with four model colours and one identity line.

**Source and verification:** main_3/outputs/damage_regression_predictions.parquet, strategy=group_shuffle; run_report_stage passes BOTH ultimate_load_kn and wire_area_loss_pct to plot_regression_predictions.
Canonical PNG SHA-256 matches `main_3/reports/figures/damage_regression_parity.png`.
Pure plotting function replayed against saved data; pixels match exactly.

**Redundancy check:** Historical structural performance is already discussed, and the selected Ridge parity addresses the actual central model.

**Decision: reject.** Mixes kN and percentage-point targets without target identification; the apparent two-cluster geometry is partly a unit artefact.

### M3-09 — `emiling/main_3/dataset_overview.png`

**Viewed:** A four-panel overview shows treatment counts, image/structural-label coverage by week, five-category surface and peak counts, and 792 surface-labelled versus 48 structural-labelled rows.

**Source and verification:** main_3/outputs/canonical_dataset.csv and dataset_summary.csv; meeting-report generator not located. Counts and schema agree with saved historical data.
Canonical PNG SHA-256 matches `main_3/reports/meeting_report/figures/dataset_overview.png`.

**Redundancy check:** dataset_supervision and the dataset chapter already distinguish repeated images from terminal structural outcomes, with the refined 791-readable-image basis.

**Decision: reject.** Repeats the supervision message less directly and risks conflating older five-category labels with the prepared four-class branch.

### M3-10 — `emiling/main_3/degradation_examples_panel.png`

**Viewed:** The left panel connects cross-sectional weekly mean and median peak rust; the right plots six example fitted histories and long extrapolations, including a fall to zero and a rise capped at 100%.

**Source and verification:** main_3/outputs/canonical_dataset.csv and degradation_forecasts.parquet; selected curves E04, F02, F06, G04, S1MI01, S3PA03 are present. Meeting-panel generator/selection recipe not found.
Canonical PNG SHA-256 matches `main_3/reports/meeting_report/figures/degradation_examples_panel.png`.

**Redundancy check:** threshold_status and the downstream chapter already expose the distinction between fitted paths and validated prognosis; M3-11 duplicates the trajectory theme.

**Decision: reject.** Weekly composition changes between campaigns, and the extrapolation shapes are not validated trajectories. They add a historical illustration without new evidence for the report’s claims.

### M3-11 — `emiling/main_3/degradation_examples_peak_rust.png`

**Viewed:** Six specimen-specific peak-rust curves use solid historical and dashed forecast segments. Some forecasts decline, some grow, and two plateau at the 100% clipping boundary.

**Source and verification:** main_3/outputs/degradation_forecasts.parquet and rul_estimates.csv; run_report_stage selects the first six specimens after sorting failure_probability descending and estimated_rul_weeks ascending; plot_trajectory_examples.
Canonical PNG SHA-256 matches `main_3/reports/figures/degradation_examples_peak_rust.png`.
Pure plotting function replayed against saved data; pixels match exactly.

**Redundancy check:** Overlaps M3-10 and the existing model-derived threshold discussion.

**Decision: reject.** A selected historical curve gallery adds no independent forecasting validation. The bounded threshold-status figure is a more direct statement of the downstream limitation.

### M3-12 — `emiling/main_3/feature_alignment.png`

**Viewed:** Three label-versus-feature scatterplots show weak positive Pearson correlations, labelled 0.26 for total rust, 0.18 for peak rust, and 0.25 for peak location. Points are widely dispersed.

**Source and verification:** main_3/outputs/canonical_dataset.csv joined one-to-one to main_3/outputs/image_features.csv by record_id. Recomputed Pearson r=0.257148, 0.182837, 0.247840 on 792 complete pairs. Panel generator not found.
Canonical PNG SHA-256 matches `main_3/reports/meeting_report/figures/feature_alignment.png`.

**Redundancy check:** This is NOT a numerical duplicate of label_adjacency: that figure uses the distinct main_4 feature generation and Spearman correlation.

**Decision: reject.** Useful as a scope correction in prose, but a historical three-panel figure would divert the focused diagnostic addition. v3 explicitly states that near-identity applies to main_4 and not these earlier features. The apparent contradiction is recorded rather than suppressed.

### M3-13 — `emiling/main_3/grouped_regression_mae_summary.png`

**Viewed:** Two panels summarize grouped-holdout MAE: visible targets at left and wire-loss/load targets at right. Short model labels improve readability, but the structural panel shares an axis across different units.

**Source and verification:** main_3/outputs/corrosion_regression_metrics.csv and damage_regression_metrics.csv, strategy=group_shuffle. Values agree with those source rows and M3-05/M3-07; dedicated summary generator not found.
Canonical PNG SHA-256 matches `main_3/reports/figures/grouped_regression_mae_summary.png`.

**Redundancy check:** Repackages M3-05 and M3-07 and duplicates existing historical results/robustness_synthesis.

**Decision: reject.** The structural panel still mixes kN with percentage points, so it is not a defensible replacement for the existing normalized comparison.

### M3-14 — `emiling/main_3/hidden_damage_relationships.png`

**Viewed:** Three terminal scatterplots relate peak rust to wire loss, total surface rust to load, and wire loss to load, coloured by campaign and shaped by treatment. A large legend obscures much of the first panel; campaign-separated load clusters are visible in the latter panels.

**Source and verification:** main_3/outputs/canonical_dataset.csv restricted to has_structural_labels (48 terminal rows), with wire_area_loss_pct and ultimate_load_kn. Meeting-panel generator not found.
Canonical PNG SHA-256 matches `main_3/reports/meeting_report/figures/hidden_damage_relationships.png`.

**Redundancy check:** The load/rust relationship and campaign grouping are already clearer in confounding. The extra wire-loss associations do not identify an independent causal mechanism.

**Decision: reject.** Retains substantial clutter and repeats the key confounding message. Existing common-axis panels cover the full measured load range and are more legible.

### M3-15 — `emiling/main_3/risk_distribution.png`

**Viewed:** Four risk-category bars show 20 Low, 8 Moderate, 20 High and no Critical cases. These are assigned screening categories.

**Source and verification:** main_3/outputs/rul_estimates.csv and main_3/src/visualization/plots.py:plot_risk_distribution; counts independently checked.
Canonical PNG SHA-256 matches `main_3/reports/figures/risk_distribution.png`.
Pure plotting function replayed against saved data; pixels match exactly.

**Redundancy check:** threshold_status and the downstream chapter already report model-derived screening with clearer status semantics.

**Decision: reject.** Historical heuristic risk classes are not observed risks or calibrated probabilities. A polished risk chart would imply more validation than is available.

### M3-16 — `emiling/main_3/rul_histogram.png`

**Viewed:** A weeks-to-threshold histogram with a smooth density overlay concentrates near zero and has a sparse tail to 55.5 weeks.

**Source and verification:** main_3/outputs/rul_estimates.csv; plot_rul_histogram explicitly drops missing estimated_rul_weeks. There are 33 finite values, including 23 exactly zero, and 15 omitted non-crossings.
Canonical PNG SHA-256 matches `main_3/reports/figures/rul_histogram.png`.
Pure plotting function replayed against saved data; pixels match exactly.

**Redundancy check:** The newer threshold_status figure retains every specimen and explicitly separates non-crossing from crossing status.

**Decision: reject.** Dropping non-crossings hides a material part of the cohort; a density curve on heuristic times is not an observed lifetime distribution. The refined threshold experiment also uses a different scheme/horizon.

### M4-01 — `emiling/main_4/feature_set_comparison_bars.png`

**Viewed:** Two bar panels compare selected feature families by MAE and Spearman, with colour identifying Ridge or CatBoost. Metadata-only and metadata+HSV are nearly tied in MAE.

**Source and verification:** main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/feature_set_comparison.csv; ultimate_load_refocus.py:plot_best_feature_set_bars.
Canonical PNG SHA-256 matches `main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/feature_set_comparison_bars.png`.
Pure plotting function replayed against saved data; pixels match exactly.

**Redundancy check:** capacity_ablation uses this exact saved comparison, includes fold SD and clear uncertainty limits, and is accompanied by all seven numeric rows.

**Decision: reject.** Exact scientific duplication of an existing, more informative report figure.

### M4-02 — `emiling/main_4/grouped_cv_balance.png`

**Viewed:** Ten split bars show nine or ten held-out specimens; paired mesh-count bars show four or five specimens per mesh. Long split identifiers dominate the horizontal labels.

**Source and verification:** main_4/outputs/ultimate_load_refocus/splits/grouped_cv_balance_summary.csv and grouped_cv_specimen_manifest.csv; counts independently recomputed from manifest.
Canonical PNG SHA-256 matches `main_4/outputs/ultimate_load_refocus/splits/grouped_cv_balance.png`.

**Redundancy check:** evaluation_regimes and the methods text already define specimen grouping, repeats and test sizes; v2’s source audit checks disjointness.

**Decision: reject.** Balance is useful QA but not an additional result. Its title’s leakage-check claim cannot be established by bar heights alone; the manifest check supplies that evidence.

### M4-03 — `emiling/main_4/leave_one_campaign_out_balance.png`

**Viewed:** Two test-size bars each represent 24 specimens, and the adjacent mesh bars show that each held-out campaign contains only one mesh family.

**Source and verification:** main_4/outputs/ultimate_load_refocus/splits/leave_one_campaign_out_balance_summary.csv and leave_one_campaign_out_specimen_manifest.csv; counts independently recomputed.
Canonical PNG SHA-256 matches `main_4/outputs/ultimate_load_refocus/splits/leave_one_campaign_out_balance.png`.

**Redundancy check:** confounding already states the exact observed design combinations; evaluation_regimes explains whole-campaign exclusion.

**Decision: reject.** Repeats the reason LOCO is extrapolation without adding model diagnostics. Counts alone do not validate all preprocessing choices.

### M4-04 — `emiling/main_4/mesh_stratified_corrosion_vs_ultimate_load.png`

**Viewed:** A five-by-three scatter grid relates five corrosion descriptors to load within four meshes, seven meshes and the pooled cohort. Pooled slopes often differ from within-mesh slopes; axes vary across mesh panels.

**Source and verification:** main_4/outputs/ultimate_load_refocus/correlations/mesh_stratified_corrosion_vs_ultimate_load.csv and data/specimen_summary_table.csv; the total-rust correlations were independently verified in v2.
Canonical PNG SHA-256 matches `main_4/outputs/ultimate_load_refocus/correlations/mesh_stratified_corrosion_vs_ultimate_load.png`.

**Redundancy check:** confounding already presents the key total-rust relationship with common load axes, all 48 points and explicit design structure.

**Decision: reject.** The fifteen-panel grid repeats that point with much smaller labels and differently scaled load axes. Other descriptors do not remove campaign confounding.

### M4-05 — `emiling/main_4/model_metric_heatmap.png`

**Viewed:** Three annotated heatmaps display MAE, RMSE and Spearman for seven feature families crossed with five models. Ridge’s metadata and metadata+HSV MAEs both round to 0.173.

**Source and verification:** main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/model_comparison.csv (35 configurations); ultimate_load_refocus.py:plot_model_metric_heatmap.
Canonical PNG SHA-256 matches `main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/model_metric_heatmap.png`.
Pure plotting function replayed against saved data; rendered pixels differ; exact image reproduction is not claimed.

**Redundancy check:** capacity_ablation, the selected-family table and paired_specimen_errors already expose the primary contrast and selection caveat.

**Decision: reject.** A full leaderboard increases visual density without adding a diagnostic of the selected model’s errors. Selection uses the same reported folds.

### M4-06 — `emiling/main_4/ultimate_load_refocus_ieee.pdf`

**Viewed:** A five-page earlier article: page 2 contains a workflow and dataset/feature tables; page 3 contains Ridge parity; page 4 contains feature-family bars and results; page 5 contains stratified correlation bars.

**Source and verification:** main_4/outputs/reports/ultimate_load_refocus_ieee.tex; data and figure assets under main_4/outputs/ultimate_load_refocus/. Same-name canonical PDF differs in bytes and normalized text, so exact draft reproduction is not asserted.

**Redundancy check:** Its parity is audited separately as R-06; bars and associations overlap capacity_ablation and confounding. The workflow overlaps evaluation_regimes.

**Decision: reject.** Use verified saved numerical inputs rather than copying the earlier draft. Its prose interprets subgroup gains more strongly than justified by negative mean R²; v3 retains the calibrated v2 interpretation. All five pages were viewed.

### R-01 — `emiling/main_4/metadata_only+Ridge/cv_stability.png`

**Viewed:** Box/strip plots show the ten fold MAE, RMSE and Spearman values on a shared numeric axis. Spearman varies considerably between folds. 

**Source and verification:** main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/fold_metrics.csv; ultimate_load_refocus.py:plot_cv_stability.
Canonical PNG SHA-256 matches `main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/cv_stability.png`.
Pure plotting function replayed against saved data; rendered pixels differ; exact image reproduction is not claimed.

**Redundancy check:** capacity_ablation/table already show fold variation with SD, and the selected learning curve adds training-size context.

**Decision: reject.** Shared axes mix kN and dimensionless correlation. A separated redraw is possible but adds less than the selected diagnostics.

### R-02 — `emiling/main_4/metadata_only+Ridge/error_distribution.png`

**Viewed:** Two histograms show signed residuals and absolute errors of the 48 repeat-averaged terminal predictions. Most errors are small, with a negative residual extending to about −0.61 kN.

**Source and verification:** main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/terminal_oof_predictions.csv, independently reconstructed from terminal_fold_predictions.csv; plot_error_histogram.
Canonical PNG SHA-256 matches `main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/error_distribution.png`.
Pure plotting function replayed against saved data; pixels match exactly.

**Redundancy check:** The selected parity/residual composite retains the same 48 errors together with load and mesh context. paired_specimen_errors instead compares two models and is complementary.

**Decision: reject.** A third view of these same baseline errors would duplicate the included diagnostic; density smoothing adds no validation.

### R-03 — `emiling/main_4/metadata_only+Ridge/feature_importance.png`

**Viewed:** Eleven horizontal bars rank absolute coefficient sums by original metadata field. Treatment grouping and series are tied at the top, followed closely by protocol; observation-time coefficients are nearly zero.

**Source and verification:** main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/feature_importance_full_fit.csv; fit_model_bundle standardizes all encoded columns, including one-hot columns; extract_feature_importance sums absolute encoded coefficients by raw feature, and plot_feature_importance plots them.
Canonical PNG SHA-256 matches `main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/feature_importance.png`.
Pure plotting function replayed against saved data; pixels match exactly.

**Redundancy check:** No existing v2 figure shows how the selected Ridge full fit allocates coefficients; confounding provides needed context rather than this fitted-model quantity.

**Decision: include-with-regeneration.** Regenerate as neutral-colour coefficient magnitudes, with categorical aggregation defined. Remove misleading sign colours: a sum over categorical coefficients is not a feature-level causal direction. This is a full-data descriptive fit, not held-out importance, an ablation or evidence of independent drivers. Collinearity and number of categories affect ranking.

### R-04 — `emiling/main_4/metadata_only+Ridge/learning_curve.png`

**Viewed:** Two learning-curve panels show training error rising and held-out error falling as more training specimens are used, alongside rank correlation and broad fold variation. A train/test MAE gap remains at full size.

**Source and verification:** main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/learning_curve_raw.csv (50 rows), learning_curve_summary.csv (five fractions) and fold_metrics.csv; compute_learning_curve and plot_learning_curve. Every saved summary mean/sample SD is independently recomputed.
Canonical PNG SHA-256 matches `main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/learning_curve.png`.
Pure plotting function replayed against saved data; pixels match exactly.

**Redundancy check:** No v2 figure shows sensitivity to the number of independent training specimens. This complements, rather than repeats, capacity_ablation and evaluation_regimes.

**Decision: include-with-regeneration.** Regenerate the MAE panel with real specimen-count ranges, correct kN units, all ten individual fold values and descriptive mean±SD. Subsets need not be nested and test sets are reused. The plot cannot predict gains from collecting new campaigns or isolate sample size from subset composition. No refit is needed.

### R-05 — `emiling/main_4/metadata_only+Ridge/partial_dependence.png`

**Viewed:** Three panels change campaign, coarse treatment (including the literal False category), and mesh, showing mean predicted load under those substitutions.

**Source and verification:** main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/partial_dependence.csv; compute_partial_dependence_data copies the reference rows and replaces one field while leaving the rest fixed; plot_partial_dependence.
Canonical PNG SHA-256 matches `main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/partial_dependence.png`.
Pure plotting function replayed against saved data; pixels match exactly.

**Redundancy check:** Coefficient magnitudes and confounding address baseline dependence without creating unobserved design combinations.

**Decision: reject.** Changing campaign or mesh while holding their perfectly aligned partners fixed creates combinations absent from the experiment. The plot cannot identify a standalone engineering effect, and the False label exposes the known YAML category defect.

### R-06 — `emiling/main_4/metadata_only+Ridge/prediction_vs_ground_truth.png`

**Viewed:** An observed-versus-predicted terminal-load scatter shows two broad load clusters, an identity line and several substantial departures. Vertical bars are the SD of two held-out predictions, not prediction intervals.

**Source and verification:** main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/terminal_fold_predictions.csv (96 rows) and terminal_oof_predictions.csv (48 rows); aggregate_prediction_rows and plot_prediction_vs_truth. Mean, sample SD, counts and signed errors independently recomputed; observed range is 1.60–2.87 kN.
Canonical PNG SHA-256 matches `main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/prediction_vs_ground_truth.png`.
Pure plotting function replayed against saved data; pixels match exactly.

**Redundancy check:** capacity_ablation shows average model comparison; paired_specimen_errors shows incremental HSV effects. Neither shows absolute baseline calibration/error location.

**Decision: include-with-regeneration.** Merge with R-07 in ridge_terminal_diagnostics: all 48 points, common full-range parity axes, explicit mesh colours and signed residual definition. Omit two-repeat SD bars to avoid suggesting calibrated uncertainty. Averaging predictions before taking absolute error differs from the headline fold-mean MAE and from the v2 paired statistic.

### R-07 — `emiling/main_4/metadata_only+Ridge/residual_analysis.png`

**Viewed:** Residual-versus-prediction scatter and mesh-specific box/strip plots show signed error about zero, including negative outliers in both mesh groups.

**Source and verification:** main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/terminal_oof_predictions.csv, reconstructed from terminal_fold_predictions.csv; plot_residuals.
Canonical PNG SHA-256 matches `main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/residual_analysis.png`.
Pure plotting function replayed against saved data; rendered pixels differ; exact image reproduction is not claimed.

**Redundancy check:** Shares observations with R-06 and R-02, but signed errors add error direction to parity. Merge it into R-06, not a separate numbered figure.

**Decision: include-with-regeneration.** Use the residual-versus-prediction panel in the two-panel composite. The picture exposes large errors despite a moderate mean; it is descriptive after model selection and does not establish calibrated subgroup reliability.

### R-08 — `emiling/main_4/metadata_only+Ridge/uncertainty.png`

**Viewed:** The left panel compares terminal observations with repeat-mean predictions and SD bars in specimen rank order. The right plots repeat SD against absolute error; some large errors have very small repeat SD.

**Source and verification:** main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/terminal_oof_predictions.csv; plot_uncertainty. Each SD uses just two held-out predictions with overlapping training data.
Canonical PNG SHA-256 matches `main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/uncertainty.png`.
Pure plotting function replayed against saved data; pixels match exactly.

**Redundancy check:** The first panel repeats parity; the second explains why repeat stability is not accuracy, a limitation stated with the included diagnostic.

**Decision: reject.** This is not calibrated predictive uncertainty or empirical interval coverage. A standalone uncertainty figure would need a stronger evaluation design; its useful caution is retained in prose.

# Evidence Log — Chapters 2 and 3

Internal working documentation. Not part of the final report. Evidence
tiers follow REPORT_PLANNING.md: **A** executable code/config, **B**
generated metrics/tables/manifests/logs, **C** associated report/paper,
**D** project-internal descriptive documentation, **P**
predecessor/external experimental documentation, **E** inference.

All facts below were re-verified directly against repository files during
this drafting session (not merely carried over from REPORT_PLANNING.md),
per the evidence-discipline instruction. Paths are relative to the
project root `/Users/parastoo/All_projects/Proj_corrosion/corrosion/`.

## Chapter 2 — Dataset, Experimental Context, and Data Audit

| Section | Claim | Source | Tier | Variable/line | Caveat |
|---|---|---|---|---|---|
| 2.1 | Two campaigns, 24 specimens each | `main_4/configs/specimen_mapping.yaml`, parsed directly (Python/yaml) | A | `Counter(campaign_id)` = `{campaign_1: 24, campaign_2: 24}` | — |
| 2.1 | Campaign 1: 5 series (S1–S5), mesh=7, NaCl=3.5%, terminal week 28 / day 196 | `specimen_mapping.yaml` | A | `n_steel_mesh: 7, nacl_pct: 3.5, terminal_week: 28, terminal_days: 196` (all campaign_1 rows) | — |
| 2.1 | Campaign 2: 4 series (D,E,F,G), mesh=4, NaCl=5.0%, terminal week 36 / day 252 | `specimen_mapping.yaml` | A | `n_steel_mesh: 4, nacl_pct: 5.0, terminal_week: 36, terminal_days: 252` (all campaign_2 rows) | — |
| 2.1 | Series specimen counts: S1=7, S2=7, S3=4, S4=3, S5=3, D=6, E=6, F=6, G=6 | `specimen_mapping.yaml`, parsed | A | `Counter(series_id)` | — |
| 2.1 | Treatment-coarse counts: NO=10, MI=6, SA=18, PA=7, SA_PA=3, SA_VF=2, VF=2 (sum 48) | `specimen_mapping.yaml`, parsed and cross-tabulated by campaign | A | manual cross-tab, verified sum=48 | **Important caveat, not put in report body**: PyYAML's `safe_load` (used by `main_4/src/corrosion_proxy_rul/config.py:12`) parses the unquoted YAML value `NO` as the Python boolean `False` (YAML 1.1 boolean literal), not the string `"NO"`. Confirmed this literal `False` (stringified as `"False"` on CSV write) appears in `main_4/outputs/data/master_table.csv`'s `treatment_coarse` column for all 10 no-treatment-control specimens; a separate, correctly-populated `treatment_raw` column in the same file does contain `"NO"`. This is a genuine, currently-live bug in the pipeline's own generated `treatment_coarse` column, not a documentation error. Table 2.1 in the report describes the *intended* treatment semantics (verified against `specimen_mapping.yaml`'s `treatment_protocol` field, e.g. `no_treatment_control`), which is unaffected by this string-parsing bug. Flagged for Chapter 7 (Software Engineering/Reproducibility); not mentioned in Chapter 2 body per the instruction to keep code-level detail out of the dataset chapter. |
| 2.1 | Treatment protocol descriptions (mixed-in inhibitor, surface-applied by spray/brush, paint, paint+surface combination, surface+glass compound, glass compound alone) | `specimen_mapping.yaml`, `series_groups` and `specimens` `treatment_protocol` field | A | e.g. `mixed_in_inhibitor`, `surface_inhibitor_spray_campaign2`, `surface_inhibitor_brush_campaign2`, `glass_based_compound` | — |
| 2.1 | Terminal structural test = four-point bending test; ultimate load = peak load from that test; wire-area loss = cross-sectional loss of outermost longitudinal wires near failure surface, from microscopic cross-section | `main_4/PROJECT_AUDIT.md:324-328`, citing "thesis Chapter 5 and Chapter 7" | D relaying P | — | This is a **secondary citation**: the present audit did not itself read the full predecessor thesis (`Documentation/Thesis/s313940_...pdf`, 191 MB) to confirm this definition; it is relayed via the project's own audit documentation, which explicitly cites the thesis chapters. Footnoted as such in Chapter 2. |
| 2.1 | Predecessor thesis author (Al Amin Hossain, s313940) is a different person from the current project author (Parastoo Hashemi Alvar, s339438) | Filename `Documentation/Thesis/s313940_Tesi_conv_msc_thesis_final_md_al_amin_hossain_s313940.pdf`; author block of `out/corrosion_condition_pipeline_ieee.pdf` / `.tex` | D/C | — | Filename-derived identity claim; not opened/verified against the PDF's internal title page in this drafting session (re-verified in a prior audit session, not re-opened now). |
| 2.2 | Visible-corrosion labels: total rust % and peak rust %, each with a 4-class ordinal category | `main_4/src/corrosion_proxy_rul/data_loading.py` column rename map (`A_Total_Rust_Category...` → `surface_total_rust_category`; peak analogue → `peak_rust_category`) | A | — | Noted (evidence log only) that the *source string* for the total-rust category column in the current `data_loading.py` reads `A_Total_Rust_Category_(main_first–4)` rather than `(1–4)` — the same "1→main_first" corruption pattern already catalogued in REPORT_PLANNING.md's contradiction register, but here found in a `.py` file rather than a YAML config, broadening that finding's scope. Despite this, the **already-generated** `master_table.csv` (dated 2026-03-16, i.e. before the 2026-04-01 16:58 corruption-timestamp cluster) has fully valid category values (see next row) — consistent with the "historical valid / current corrupted, cause unproven" framing already adopted in REPORT_PLANNING.md. Not re-opened as a new contradiction-register item per the "no further general audit" instruction; logged here for Chapter 7. |
| 2.2 | Total-rust category counts: 658/99/20/14 (classes 1–4) | `main_4/outputs/data/master_table.csv`, column `surface_total_rust_category`, `value_counts()` | B | — | — |
| 2.2 | Peak-rust category counts: 526/107/95/63 (classes 1–4) | Same file, column `peak_rust_category` | B | — | This exact breakdown was not previously recorded in REPORT_PLANNING.md (which only had the total-rust breakdown from the augmentation documentation); newly verified directly against the data table for this chapter. |
| 2.3 | 15–18 images per specimen (median 16); 25 distinct observation weeks, range 0–36 | `master_table.csv`, `groupby('specimen_id').size()`, `sorted(df['week'].unique())` | B | min=15, median=16.0, max=18; 25 unique week values | — |
| 2.4 | Exactly 48 rows carry structural labels, at week 36 (campaign_2) or week 28 (campaign_1) | `master_table.csv`, columns `has_structural_label`, `is_terminal_structural_row` | B | both sum to 48; `df.loc[has_structural_label, 'week'].unique()` = {28, 36} | Confirms consistency with `specimen_mapping.yaml`'s per-specimen `terminal_week` field. |
| 2.5 | 792 image files; 1 corrupted (`E01-20240508-17W.png`, a Campaign-2, series-E [surface inhibitor, spray] specimen); 791 aligned rows | `main_4/outputs/audit/verified_facts.json`; specimen `E01` cross-referenced against `specimen_mapping.yaml` (`series_id: E`, `treatment_protocol: surface_inhibitor_spray_campaign2`) | A/B | `image_files: 792, aligned_rows: 791, orphan_images: ["E01-20240508-17W"]` | — |
| 2.5 | Corrupted-image handling across 5 phases (drop / impute×3 / exclude) | `main_first/process_images.py` (drop, verified by prior audit agent, re-confirmed via REPORT_PLANNING.md §4 item 2); `main/image_features.py:103,118` (`fillna(median())`); `main_2/data.py:158-175` (NaN embedding → column-median fill); `main_3/src/features/extractor.py` (try/except → `feature_extraction_failed=1` → median-impute); `main_4/configs/dataset.yaml` (`data_policy.use_only_aligned_readable_images: true`) + `main_4/src/corrosion_proxy_rul/data_cleaning.py:107-111` (`orphan_images = image_df.loc[~image_df["sample_name"].isin(workbook_names)]`) | A | — | Re-verified `main/image_features.py` and `main_4/data_cleaning.py` directly in this session (not solely carried over); `main_first`, `main_2`, `main_3` mechanisms carried over from the prior audit session's agent reports without re-opening those files line-by-line in this session (time/scope trade-off; low risk given prior verification was already code-level). |
| 2.6 | Campaign perfectly co-varies with mesh/NaCl/duration (no cross-combination exists) | Direct consequence of Table 2.5's design matrix (`specimen_mapping.yaml`), confirmed no specimen has e.g. `n_steel_mesh=7` with `nacl_pct=5.0` | A | — | Stated non-causally, no model-performance claim made in §2.6 per instruction. |

## Chapter 3 — Common Methodological Framework

| Section | Claim | Source | Tier | Variable/line | Caveat |
|---|---|---|---|---|---|
| 3.2/3.3 | Leakage risk from row-wise random splitting given repeated specimen images | General methodological argument grounded in Ch.2's dataset facts (15-18 images/specimen, §2.3) | E (argument), grounded in A/B facts | — | Presented as an illustrative argument, not a citation to a specific historical bug (no specific pre-grouping evaluation result from an early phase was re-verified for this chapter; this was already a finding of the prior audit for `main` — GroupShuffleSplit was already used there — so no phase in this project actually shipped a naive row-wise split. The example is used purely pedagogically to motivate the grouping principle, and is worded as a general risk, not as "phase X made this mistake."). |
| 3.3.1–3.3.3 | Definitions of GroupShuffleSplit, LOTO, LOCO and their respective purposes | `main_3/src/cv/splits.py` (`group_shuffle_split`, `leave_one_group_out` used for both LOTO on `treatment_code` and LOCO on `campaign_id`); `main_4/src/corrosion_proxy_rul/splits.py` (same three regimes) | A | — | Carried over from prior audit session's direct code reading; not re-opened in this session. |
| 3.3.3 | LOCO is an extrapolation stress test, not ordinary generalisation, because campaign covaries with mesh/NaCl/duration | Direct consequence of Ch.2 §2.6 finding | A (underlying fact), E (methodological conclusion) | — | No quantitative LOCO result is cited in Chapter 3 itself (deferred to Ch.4/5) per the instruction not to discuss model performance in this chapter. |
| 3.4 | Five representation strategies (A–E) | `main/image_features.py` (A); `main_2/data.py` frozen ResNet-18 (B); `main_3/src/features/extractor.py` 91-feature set (C); `main_4/src/corrosion_proxy_rul/image_features.py` HSV block + `configs/ultimate_load_refocus.yaml` feature_sets (D); `augmentation/` five-recipe pipeline + no classifier trained yet (E) | A | — | Carried over from prior audit session for A–D; E (four-class classification status) re-confirmed against the instruction's explicit decision ("dataset prep/splitting/augmentation completed; training/evaluation not yet completed") rather than re-reading the augmentation code in this session. |
| 3.5 | Image-only vs metadata-only vs multimodal comparison performed in multiple phases | `main_2/train_phase2.py` (image_only_mlp vs multimodal_mlp); `main_4/configs/ultimate_load_refocus.yaml` (`feature_sets`: metadata_only, rgb_only, hsv_only, combined) | A | — | Carried over from prior audit session. |
| 3.6 | Model families table | Aggregated from prior audit findings across all phases (main: ElasticNet/RF/GB/XGBoost; main_2: ResNet-18+MLP; main_3: RF/ExtraTrees/HistGB/MLP/LogisticRegression + degradation curve families incl. monotone-isotonic; main_4: RF/CatBoost/GB/Ridge) | A | — | ElasticNet and LogisticRegression, present in the underlying phases, are not separately listed in Table 3.2's row set (grouped under "Ridge/linear regression" and omitted for classification since Ch.3's model-family table focuses on the regression/degradation families common to most phases); this is a simplification for the "concise overview, not a textbook chapter" instruction, not an error — noted here so it is not mistaken for an omission if cross-checked later. |
| 3.7 | Metrics used: MAE, RMSE, R², Spearman, accuracy, macro-F1, per-class recall/confusion matrix | Aggregated from prior audit findings (e.g., `main_2/reports/metrics_by_treatment.csv`; `main_4/outputs/diagnostics/tables/benchmark_best_model_robustness.csv` columns; `augmentation_methodology_final.md` stating macro-F1/class-weighting as a stated future requirement) | A/B/D | — | — |
| 3.8 | No repeated/intermediate structural measurement exists; proxy-RUL derivation steps (estimate → curve fit → threshold → crossing time) | `main_3/src/rul/estimator.py::estimate_rul` (forecast → threshold crossing per specimen); `main_4/train_rul_proxy_models.py` / `models_rul_proxy.py` | A | — | Carried over from prior audit session; re-confirmed consistent with Ch.2's structural-supervision facts (48 rows, one per specimen) verified directly in this session. |
| 3.8 | Proxy-RUL never mislabeled as true RUL anywhere in project documentation | Exhaustive grep for "true RUL" across `main_3` and `main_4` markdown/tex in prior audit session; all occurrences are negations | C/D | — | Not re-run as a fresh grep in this session; relying on prior session's exhaustive search, which is a targeted, already-completed piece of evidence rather than a general audit. |

## Corrections made during quality control (this session)

- **Bibliography accuracy.** The `references.bib` entries for the predecessor thesis and the ARTISTE paper were initially drafted from filenames/prior-session summaries only. During QC, both source PDFs' title pages were read directly with `pdftotext` and the bib entries were corrected:
  - Thesis: exact title "Automated Image Analysis Techniques for Assessing the Corrosion in Historical Cementitious Composites: An Experimental Analysis of Ferrocement Samples"; candidate Md Al Amin Hossain (S313940); supervisor Erica Lenticchia; co-supervisor Francesco Tondolo; submitted 3 October 2025 (not 2026 as initially guessed from repository mtimes).
  - ARTISTE paper: exact title "AI-Driven Corrosion Estimation in Ferrocement for Structural Health Monitoring" (the filename's title, "...Corrosion Quantification in Cementitious Materials...", is an inexact paraphrase and was replaced); authors Gerardo Sorrentino, Jonathan Melchiorre, Md Al Amin Hossain, Erica Lenticchia (corresponding), Francesco Tondolo, DISEG, Politecnico di Torino.
  - **Important scope caveat surfaced by this check**: the ARTISTE paper's own image-analysis method classifies corrosion into **three** categories using a MATLAB/RGB-threshold pipeline, distinct from the present project's **four**-class severity scheme (`A_Total_Rust_Category_(1-4)`, Table 2.2) and from the present project's Python-based feature pipelines. Chapters 2-3 do not attribute the four-class scheme's design to either predecessor source (they describe it only as an existing column in the current project's data table, tier B), so no correction to the chapter text was needed — this is logged here so a later chapter does not inadvertently conflate the two classification schemes.
  - Both predecessor authorship teams overlap (Md Al Amin Hossain is both the thesis candidate and a co-author of the conference paper; Erica Lenticchia and Francesco Tondolo supervise/co-author both), consistent with the conference paper being a shorter, related publication arising from the same thesis project.

## Correction pass (second revision session)

- **Category-schema versioning verified.** Re-confirmed directly against `main_3/outputs/canonical_dataset.csv` (792-row basis): `surface_total_rust_category` = 493/51/38/77/133 (5 classes); `peak_rust_category` = 304/159/72/122/135 (5 classes) — exact match to the user-supplied figures. Root cause confirmed in `main_3/src/data/io.py:21,23`, whose column-rename map expects a raw workbook column defined over a `(1–5)` range (`"A_Total_Rust_Category_(main_first–5)"`, `"B_Peak_Rust_Category_(main_first–5)"` — again showing the "1→main_first" string-corruption pattern already catalogued, here confirming the *underlying* semantic range was 5, not corrupted numerals). The currently audited `main_4` workbook instead defines these columns over a `(1–4)` range (`main_4/src/corrosion_proxy_rul/data_loading.py`, already noted above). This is a genuine, verified schema change in the source workbook between the two project snapshots, not a project-side error. Added to Chapter 2 §"Dataset Audit and Alignment" (new Table "Visible-corrosion severity category schema across dataset builds") and to REPORT_PLANNING.md's contradiction/version-change register.
- **Model-family claims re-verified against code/outputs** (per instruction to target-verify before finalizing Table 3.2): confirmed XGBoost has genuine saved metrics in both `main/reports/current_corrosion_metrics.csv` (four-model benchmark: RandomForest, GradientBoosting, XGBoost, ElasticNet) and `main_4/outputs/ultimate_load_refocus/.../XGBoost/summary_metrics.csv` — corrected the chapter table, which had previously stated XGBoost was used only "in the earliest benchmarked phase." Confirmed CatBoost is constructed in `main_4/src/corrosion_proxy_rul/evaluation.py:48` and `ultimate_load_refocus.py:135` as `CatBoostRegressor(random_seed=..., verbose=False, **models_cfg["catboost"])` with **no `cat_features` argument**, and `main_4/configs/modeling.yaml`'s `catboost:` block contains only `iterations`, `learning_rate`, `depth`, `loss_function` — no categorical-feature configuration. The chapter's prior claim that CatBoost was used "with native categorical-feature handling" was therefore not supported by the repository and has been corrected to state it was used with the same numeric feature tables as the other ensembles.
- **Bibliography cleaned**: `references.bib` entries no longer print student IDs, supervisor names, submission dates, verification methodology, repository paths, or the ARTISTE-paper's-own-method caveat in the compiled bibliography — these are retained above (rows dated from the prior QC pass) and are not lost, just no longer duplicated into reader-facing output.
- **Evidence-tier language removed from Chapters 2–3** (prose, footnotes, table captions): the A/B/C/D/P/E system is now used only in this file, per instruction. No factual claim was changed by this removal — only its explicit tier label was dropped from the reader-facing text.
- **Cross-reference audit**: found and fixed one hardcoded reference outside the two chapter `.tex` files — the LOCO panel text inside `figures/fig_3_2_evaluation_regimes.tex` read "(Section 2.6)" as a literal string rather than `\ref{sec:confounding}` (now fixed to `\S\ref{sec:confounding}`). Also updated two source comments (non-printing) in the figure files that referenced "Chapter 2"/"Section 2.5" by number. No other hardcoded `Section N`/`Chapter N` patterns were found in either chapter `.tex` file on a full grep — all in-chapter cross-references already used `\ref`.
- **GroupShuffleSplit wording corrected**: the prior text claimed grouped specimen holdout draws from "the same range of campaigns and treatments in similar proportions," which overstated what an unstratified random specimen split guarantees. Corrected per the user's supplied wording (§3.3.1).
- **Metadata/multimodal ablation history corrected**: the prior text implied every phase that studied multimodal prediction compared image-only, metadata-only, and combined configurations. Verified this was not so: the deep-embedding phase (`main_2/train_phase2.py`) compared only `image_only_mlp` vs `multimodal_mlp` (image+metadata) — no metadata-only baseline was trained in that phase. The three-way comparison was first made central and systematic in the terminal-load-focused phase (`main_4/configs/ultimate_load_refocus.yaml`'s `feature_sets`). Chapter 3 §3.5 and §3.9 now describe this as a methodological evolution rather than a constant framework.
- **Section 3.9 reframed**: no longer asserts the listed principles as retroactively true of every historical phase (this was inaccurate for the earliest exploratory prototype, whose "production" model had no held-out evaluation at all — already documented in Chapter 2's corrupted-image-handling table row for that phase and in the original repository audit). The section now explicitly states this caveat and frames the list as the mature pipeline's standard, used in this report to judge what constitutes valid evidence, rather than as a description of every phase's practice.

## Chapter 4, Batch A (Sections 4.1-4.4) — evidence log

All numbers below were freshly recomputed from the saved CSVs in this session
(not copied from prior-session agent summaries), using direct `pandas`
inspection, except where noted as carried over from the prior audit.

| Section | Claim | Source | Dataset basis | Split regime | Caveat |
|---|---|---|---|---|---|
| 4.1 | No held-out evaluation for the "production" model; no persisted metrics | `main_first/build_model.py` (fits on 100% of data); absence of any metrics file anywhere under `main_first/` | 792/791 (informal) | none | Carried over from prior audit session's direct code reading; not re-opened this session (low risk, purely qualitative claim). |
| 4.2 | Task A (current corrosion): RandomForest, MAE 2.3794, RMSE 4.2543, R²=0.8996, CV MAE 3.0204 | `main/reports/current_corrosion_metrics.csv` | 792 (main's own basis) | grouped holdout + grouped CV | Re-verified directly this session. |
| 4.2 | `img_rust_mask_pct` = 91.5% of RF importance for Task A | `main/reports/current_corrosion_feature_importance.csv`, row 1 = 0.9151766609430526 | same | n/a | Re-verified exactly this session. |
| 4.2 | Task B (progression): GradientBoosting, MAE 6.7144, RMSE 9.3294, R²=0.5170 | `main/reports/progression_metrics.csv` | 792 | grouped holdout + grouped CV | Re-verified this session; confirmed GradientBoosting has lowest holdout_mae among the 4 candidates. |
| 4.2 | Task C (threshold-timing): RandomForest, MAE 2.2114 wk, RMSE 3.0947 wk, R²=0.7820; XGBoost has better RMSE (2.824) and R² (0.818) but is not selected | `main/reports/time_to_threshold_metrics.csv` | 792 | grouped holdout + grouped CV | Re-verified this session; selection driven by holdout MAE only, confirmed by direct row comparison. |
| 4.3 | Frozen ResNet-18 (ImageNet), final layer replaced with Identity(), run under no_grad() | `main_2/data.py` (lines documenting `ResNet18_Weights.IMAGENET1K_V1`, `Identity()`, `no_grad()`) | n/a | n/a | Carried over from prior audit session's direct code reading. |
| 4.3 | No metadata-only baseline in this phase; only `image_only_mlp` and `multimodal_mlp` exist | `main_2/reports/model_comparison.csv` (2 rows only), `main_2/artifacts/run_info.json` | 792 | n/a | Re-verified this session (file has exactly 2 model rows). |
| 4.3 | Best validation MAE: image-only 4.9595 (epoch 14), multimodal 4.0161 (epoch 45) | `main_2/reports/training_history.csv`, `groupby('model')['val_mae'].min()` | 792 | validation split within training | Re-verified this session via direct pandas computation. |
| 4.3 | Test MAE: image-only 5.6255, multimodal 5.7476 | `main_2/reports/model_comparison.csv` | 792 | held-out test | Re-verified this session. |
| 4.3 | Deployed model = image_only_mlp, selected on test MAE | `main_2/artifacts/run_info.json`: `"best_model": "image_only_mlp"` | 792 | n/a | Re-verified this session. |
| 4.3 | Late-week bias: MAE 2.220/+0.854 (≤wk10), 6.617/−1.314 (wk12-20), 12.075/−6.912 (≥wk23) | `main_2/main.tex` lines 536-540 | 792 | held-out test | Re-verified this session via direct grep of main.tex; this is a phase-native computed statistic, not independently recomputed from raw predictions in this session (would require re-binning `predictions_best_model.csv` by week — deferred as the report text itself is a direct, dated, code-adjacent source). |
| 4.4 | main_3 category schema = 5 classes | Already verified and logged above (Chapter 2 correction pass) | 792 | n/a | Reused, not re-verified again. |
| 4.4 | Corrosion group_shuffle: surface RF 1.381/3.142/0.646; peak MLP 4.209/6.234/0.784 | `main_3/outputs/corrosion_regression_metrics.csv`, direct groupby | 792 | group_shuffle | Re-verified this session; cross-checked exactly against `main_3/main.tex`'s own summary table (Table label `tab:continuous-results`), which matched to 3 decimal places. |
| 4.4 | Corrosion LOCO: surface RF 2.096/3.906/0.582 (mean of 2 folds); peak HGB 6.211/8.883/0.595 | Same file, filtered `strategy=='leave_one_campaign_out'`, grouped by model, mean of 2 folds | 792 | LOCO | Re-verified this session; matches main_3's own summary table exactly. |
| 4.4 | Corrosion LOTO: surface MLP 1.533/2.659/−0.677; peak RF 4.742/7.245/−0.077 | Same file, `strategy=='leave_one_treatment_out'`, mean of 7 folds | 792 | LOTO | Re-verified this session; matches main_3's own summary table exactly. Negative mean R² driven by a strongly negative per-fold R² for at least one small treatment group (e.g. PA fold: R²=−50.7 for linear_regression, though the *selected* MLP/RF models are less extreme per-fold — mean is still negative because some folds are very poor). |
| 4.4 | Classification (5-category) group_shuffle: surface Logistic acc 0.830/F1 0.573; peak MLP acc 0.591/F1 0.531; degrading under LOCO/LOTO, macro-F1 not exceeding ~0.47 under either | `main_3/main.tex` lines 541-555 (`tab:classification-results`) | 792 | all three regimes | Verified against main.tex table; underlying classification-metrics CSV not independently re-opened this session (report table is itself computed "from the saved corrosion-classification metrics" per its own caption — treated as a reliable secondary source of a primary artifact). |
| 4.4 | Damage group_shuffle: wire RF 3.899/4.995/0.310; ultimate load RF 0.121/0.168/0.385 (38/10 split) | `main_3/outputs/damage_regression_metrics.csv` | 792 | group_shuffle | Re-verified this session; exact match to main_3's own summary table and to the n_train=38/n_test=10 fold. |
| 4.4 | Damage LOCO: wire HGB 12.280/15.410/−0.387; ultimate load ExtraTrees 0.624/0.655/−8.356 | Same file, `strategy=='leave_one_campaign_out'`, mean of 2 folds | 792 | LOCO | Re-verified this session via direct pandas groupby; matches main_3's own summary table exactly. |
| 4.4 | Damage LOTO: wire HGB 10.759/13.065/−5.481; ultimate load RF 0.158/0.189/−4.569 | Same file, `strategy=='leave_one_treatment_out'`, mean of 7 folds | 792 | LOTO | Re-verified this session; RF and ExtraTrees are near-tied on MAE (0.158158 vs 0.158199) for ultimate load — RF selected by the tie-break (lower MAE), matches main_3's own table exactly. |
| 4.4 | Damage feature list includes metadata + manual corrosion labels/categories + selected image features; does NOT include the model's own predicted corrosion columns | `main_3/src/orchestration.py`, function `_damage_feature_columns` (lines 230-255) | n/a | n/a | Re-verified this session by direct code reading — confirmed the preferred feature list names `surface_total_rust_pct`, `peak_rust_pct` (manual labels) and does not reference any `predicted_*`/`estimated_*` corrosion column. |
| 4.4 | Ultimate-load RF feature importance dominated by n_steel_mesh (0.172) and campaign one-hot indicators (0.128, 0.105); wire-loss vs. total/peak rust correlation r=0.021/0.011 | `main_3/main.tex` lines 583-585 | 792 (48 structural rows) | n/a (full-data model) | Verified against main.tex; the underlying feature-importance/correlation table itself was not located as a separate saved CSV by that exact name in this session — treated as a claim from the phase's own technical report (a project-internal document, not independently re-derived from raw importances in this session). Flagged as a minor residual gap: a future pass could locate and re-verify the exact source CSV if greater precision is required. |
| 4.4 | Final damage estimator fit on all 48 structural rows (no further holdout at this step), then applied to all 792 rows to produce `estimated_wire_area_loss_pct`/`estimated_ultimate_load_kn` | `main_3/src/orchestration.py` lines 294-316 (`fit_full_pipeline(dataset=structural_df, ...)` then `.predict(design_df[feature_cols])` over the full `design_df`) | 792 | n/a (full-data refit) | Re-verified this session by direct code reading. |
| 4.4 | 91-feature representation is a "Python reconstruction and extension," not an exact reproduction of the GIMP/BIMP/MATLAB predecessor workflow | Carried over from prior audit session's finding (main_2's own future-work section references the documented predecessor workflow; main_3's feature set is implemented independently in Python) | n/a | n/a | Not re-verified line-by-line against the predecessor thesis in this session; wording chosen deliberately to avoid overclaiming reproduction, per instruction. |

### Figures created/reused for Chapter 4, Batch A

| Figure | Type | Source script/file | Reproducible from |
|---|---|---|---|
| `fig_4_1_main2_image_only_vs_multimodal.png` | New, generated | `activity_report/figures/generated_scripts/make_fig_4_1_main2_fusion.py` | `main_2/reports/training_history.csv` + `main_2/reports/model_comparison.csv` (script reads these directly, not hardcoded values) |
| `fig_4_2_main2_residual_vs_week.png` | Reused as-is (copied) | Original: `main_2/reports/figures/04_residual_vs_week.png` | Original project-generated figure; provenance-preserving filename used in `activity_report/figures/` |
| `fig_4_3_main3_robustness_by_regime.png` | New, generated | `activity_report/figures/generated_scripts/make_fig_4_3_main3_robustness.py` | `main_3/outputs/corrosion_regression_metrics.csv` + `main_3/outputs/damage_regression_metrics.csv` (script reads these directly) |

### Figures/tables considered and deliberately omitted (with reasons)

See `activity_report/notes/chapter4_batchA_evidence_plan.md` for the full
rationale per phase. Summary: `main/reports/fig_current_feature_importance.png`
and `fig_holdout_mae_by_task.png` (redundant with prose/table, or mix
incompatible units across tasks); `main_2/reports/figures/05_model_comparison.png`
(test-MAE-only, truncated axis, omits the validation reversal that is the
actual finding); `main_2` per-material trajectory panels (too granular for
the main narrative); `main_3`'s existing MAE-by-model bar charts and parity
plots (group_shuffle only, do not show the cross-regime robustness contrast
that is the phase's central diagnostic finding).

## Chapter 4, Batch B (Sections 4.5-4.8) — evidence log

All numbers below were freshly computed from the saved artifacts in this
session via direct `pandas`/`scipy` inspection.

| Section | Claim | Source | Dataset basis | Regime | Caveat |
|---|---|---|---|---|---|
| 4.5 | 192 degradation curves (48×4); family counts and median R² per target (surface 40 PL/8 exp, R²=0.903; peak 44/4, R²=0.916; wire-loss 48 PL, R²=0.636; load 48 PL, R²=0.601); n_obs=15-18 per curve for all 4 targets | `main_3/outputs/degradation_curves.parquet` | 792 | n/a | Re-verified directly via pandas this session. |
| 4.5 | Proxy-RUL: 33/48 finite within 104-week horizon; 23/33 exactly 0 weeks; 15/48 censored; risk classes Low 20/Moderate 8/High 20/Critical 0 | `main_3/outputs/rul_estimates.csv` | 792 | n/a | Re-verified directly via pandas this session. |
| 4.5 | Threshold/horizon config: wire-loss thresholds [20,25,30]%, load threshold = 0.8×campaign reference, health-index threshold 0.35, horizon 104 weeks; final estimate = min(wire-25%, load, health) crossing | `main_3/configs/default.toml`, `main_3/src/rul/estimator.py` (`estimate_rul`, `_crossing_week`) | n/a | n/a | Re-verified directly by reading code this session. |
| 4.6 | Feature audit: 13 near-constant, 1 duplicate, 36 high-collinearity (\|Spearman\|≥0.95) pairs; surface_total_rust_pct vs img_rust_area_ratio_pct Spearman=0.9996 | `main_4/FEATURE_DIAGNOSTICS.md` | 791 | n/a | Verified against the report's own stated numbers; underlying CSVs (`near_constant_features.csv` etc.) not re-opened individually this session (report text is itself generated from them per its own description). |
| 4.6 | Top univariate correlate of wire_area_loss_frac: image morphology feature, r=0.382; top-5 for ultimate_load_kn: ageing_days/week/n_steel_mesh/nacl_pct/terminal_week, all \|r\|=0.827316 | `main_4/FEATURE_DIAGNOSTICS.md` table | 791 (48 structural rows) | n/a | Re-verified exact values against the markdown table this session. |
| 4.6 | Robustness table (surface GB 0.177/0.999 group_shuffle, 0.136/0.997 LOCO; peak RF 1.097/0.992, 1.058/0.977; wire RF 0.105/0.280, 0.124/-0.089; load RF 0.174/0.778, 0.564/0.353) | `main_4/outputs/diagnostics/tables/benchmark_best_model_robustness.csv` | 791 | group_shuffle, LOCO | Re-verified directly via `cat` this session; exact match. |
| 4.6 | Model-selection weights: LOCO 0.45, LOTO 0.25, group_shuffle MAE 0.20, group_shuffle Spearman 0.10 | `main_4/configs/modeling.yaml`, `robustness_weights` block | n/a | n/a | Re-verified directly this session. |
| 4.6 | Degradation family shift: baseline {gompertz:1, linear:3, monotone_isotonic:44} → improved {linear:27, monotone_isotonic:21} | `main_4/MODEL_IMPROVEMENT_RESULTS.md` | 791 | n/a | Re-verified directly by reading the markdown table this session. |
| 4.6 | Quoted conclusion: "The improved models are metadata-dominant, so the project still does not support strong claims that surface image features robustly infer hidden damage." | `main_4/MODEL_IMPROVEMENT_RESULTS.md`, "Final Recommendation" section | 791 | n/a | Direct quote, verified this session. |
| 4.7 | Pooled feature-set comparison, 7 rows (metadata_only MAE 0.173/R²0.645/Spearman0.758 through rgb_only 0.253/0.269/0.501) | `main_4/outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/feature_set_comparison.csv` | 791 | grouped_cv (10 splits) | Re-verified directly via `cat` this session. |
| 4.7 | Post-onset subset (43 specimens): metadata_rgb_hsv MAE 0.163/R²0.660/Spearman0.791 vs metadata_only 0.173/0.633/0.803 | `main_4/outputs/ultimate_load_refocus/pooled_post_onset/grouped_cv/feature_set_comparison.csv` (via `final_leaderboard.csv` rows) | 791 (43-row subset) | grouped_cv | Re-verified directly this session. |
| 4.7 | Mesh-stratified feature-set results: all configurations have negative mean R² within mesh_4 (-0.81 to -3.56) and mesh_7 (-0.30 to -4.65) despite MAE 0.14-0.26 | `main_4/outputs/ultimate_load_refocus/comparisons/final_leaderboard.csv`, rows with `analysis_name` = mesh_4/mesh_7 | 791 | grouped_cv | Re-verified directly this session via `cat`; this is the guardrail case (subgroup MAE looks fine, R²/Spearman do not) — stated prominently per instructions. |
| 4.7 | Mesh-stratified correlation: pooled Spearman ρ=0.462 (p=0.0009, n=48); mesh_4 ρ=-0.046 (p=0.83); mesh_7 ρ=-0.401 (p=0.052); pooled row labelled "Pooled (confounded)" in the saved file itself | `main_4/outputs/ultimate_load_refocus/correlations/mesh_stratified_corrosion_vs_ultimate_load.csv` | 791 | n/a (correlation, not model) | Independently cross-verified by recomputing from `specimen_summary_table.csv`'s `surface_total_rust_pct_terminal` column with `scipy.stats.spearmanr`/`pearsonr` this session — exact match to 3 decimal places. |
| 4.7 | LOCO collapse: metadata_only MAE 0.465/R²=-4.64 (pooled, 2 folds) | `final_leaderboard.csv`, `pooled_all_weeks` + `leave_one_campaign_out` rows | 791 | LOCO | Re-verified directly this session. |
| 4.7 | Residual-refinement attempt worsened baseline (explicitly labelled "worsened" in saved table) | `final_leaderboard.csv`, `specimen_summary_residual_refinement` rows, `baseline_comparison_status` column | 791 | grouped_cv | Re-verified directly this session; both `mesh_residual_summary` variants (CatBoost and Ridge stage-2) show `worsened`. |
| 4.8 | Class distribution 658/99/20/14 (83.2%/12.5%/2.5%/1.8%); uniform 6× expansion per class → 3948/594/120/84 (4,746 total) | `Documentation/augmentation_methodology_final.md`, Table 9 | 791 | n/a | Re-verified directly by reading the markdown table this session; cross-checked against Chapter 2 Table 1.2's already-verified 658/99/20/14 figures (computed independently from `master_table.csv` in the earlier Chapter 2 pass). |
| 4.8 | Mirror-flip justification: "total coverage is position-invariant" (accepted here) vs. position-sensitive features banned from flip elsewhere | `Documentation/augmentation_methodology_final.md`, parameter-justification table (row "Mirror flip") | n/a | n/a | Re-verified directly this session. |
| 4.8 | Rejected techniques and reasons (MixUp, CutMix, GAN/diffusion, elastic deformation, cutout, heavy colour shift, vertical flip, large rotation) | `Documentation/augmentation_methodology_final.md`, exclusion-rationale table | n/a | n/a | Re-verified directly this session; summarised rather than quoted in full. |
| 4.8 | Leakage-safety runtime check: `raise RuntimeError` if augmented row in val/test manifest | `augmentation/make_splits.py`, lines ~360-363 | n/a | n/a | Re-verified directly this session (already logged once in an earlier pass; re-confirmed). |
| 4.8 | Split sizes: train 3,846; val 75; test 75 | `Data/splits/{train,val,test}_manifest.csv` row counts (`wc -l`, minus header) | 791-based augmented pool | n/a | Re-verified directly this session. |
| 4.8 | No classifier training code exists anywhere in `augmentation/` | Fresh `find augmentation -name "*.py"` listing this session (4 scripts: `augment_dataset.py`, `create_dataset_variants.py`, `make_splits.py`, plus `scripts/` utilities — none train a model) | n/a | n/a | Re-verified directly this session; consistent with git log showing the latest commit (`e1e88fb`) is explicitly titled "...without training models." |

### Figures created/reused for Chapter 4, Batch B

| Figure | Type | Source script/file | Reproducible from |
|---|---|---|---|
| `fig_4_4_main3_proxy_rul_histogram.png` | Reused as-is (copied) | Original: `main_3/reports/figures/rul_histogram.png` | Original project-generated figure |
| `fig_4_5_main4_relative_mae_collapse_heatmap.png` | Reused as-is (copied) | Original: `main_4/outputs/diagnostics/figures/benchmarks/best_model_relative_mae_collapse_heatmap.png` | Original project-generated figure |
| `fig_4_6_mesh_stratified_corrosion_vs_load.png` | New, generated | `activity_report/figures/generated_scripts/make_fig_4_6_mesh_stratified.py` | `main_4/outputs/ultimate_load_refocus/data/specimen_summary_table.csv` (script reads this directly; verified output matches the phase's own saved correlation CSV exactly) |

### Figures/tables considered and deliberately omitted (Batch B)

See `activity_report/notes/chapter4_batchB_evidence_plan.md` for full detail.
Summary: `main_3`'s `risk_distribution.png` and per-specimen degradation
panels (redundant with the reported summary statistics); `main_4`'s
per-fold stability plots and full 36-pair collinearity heatmap (too dense
for the main narrative); the existing 15-panel mesh-stratified correlation
figure (superseded by the focused 3-panel reproduction, Fig.~4.6, which
shows the one variable needed); per-specimen trajectory and
residual/uncertainty diagnostic plots under `residual_refinement/` (the
one relevant negative finding is fully captured by prose plus the
leaderboard row); an augmentation before/after example panel (omitted to
keep Section 4.8 within its length budget, per the "not a full
methodology paper" instruction).

## Chapter 4 QC correction pass (post Batch B) — corrections and re-verifications

Targeted correction pass performed after Batch B approval, addressing seven
specific factual/interpretive issues identified by review. All figures
below were freshly re-verified against repository files this session.

| Issue | Finding | Source | Resolution |
|---|---|---|---|
| Fig. 3.3 / Table 3.2 caption said visible-corrosion targets "remain at or above zero under every regime" | False: Table 3.2 itself shows LOTO total-rust R²=-0.677 and LOTO peak-rust R²=-0.077. LOCO is positive for both (0.582, 0.595); LOTO is negative for both. | `main_3/outputs/corrosion_regression_metrics.csv` (already the source of Table 3.2, re-checked against the table itself) | Caption and nearby prose ("...visible-corrosion layer, which retains useful accuracy under the same settings") rewritten to state LOCO/LOTO separately: visible-corrosion is more robust overall and stays positive under LOCO, but LOTO drives both visible-corrosion targets negative too, so the two regimes are not interchangeable. |
| Chapter claimed the post-Phase-3 work included "a shift toward out-of-fold rather than in-sample structural estimates" | Not supported: `main_4/NEXT_STEPS_PLAN.md` explicitly lists "export fully explicit out-of-fold predictions for the structural target models ... as the basis for any degradation modelling experiment" as a **recommended future step**, and separately states current degradation/proxy outputs "were generated from in-sample hidden-damage refits, not out-of-fold structural predictions." `ultimate_load_refocus.py` does produce out-of-fold ("terminal_oof") predictions, but for the terminal ultimate-load evaluation/robustness benchmarking, not for feeding degradation-curve trajectories. | `main_4/NEXT_STEPS_PLAN.md` (§3.2, §4.4); `main_4/src/corrosion_proxy_rul/ultimate_load_refocus.py` (`terminal_oof`, `all_row_oof`) | Claim removed; replaced with the reviewer-suggested wording ("stronger attention to out-of-sample structural estimation, explicit image-versus-metadata ablations, robustness-oriented model selection, feature cleanup, and monotonicity-aware degradation modelling"), which does not assert an OOF structural-trajectory implementation that does not exist. |
| Section 4.8 said train/val/test (3,846/75/75) were "all composed of unaugmented images," and that augmentation produced "4,746 training-eligible images" | False on both counts, verified directly with pandas against the manifests: train has `is_augmented` True=3,205 / False=641 (i.e. training rows include augmented copies); val and test are 100% `is_augmented`=False (75/75, confirmed). 4,746 = 791 originals + 3,955 augmented copies is the **global offline inventory before** leakage-safe exclusion of val/test specimens' augmented copies. Val+test = 150 originals × 5 copies = 750 augmented copies excluded. Final used total = 3,846+75+75 = 3,996, not 4,746. Training manifest's own label distribution (`label` column, computed directly): 3,156/540/78/72 = 82.1%/14.0%/2.0%/1.9% — close to but not identical with the global 83.2%/12.5%/2.5%/1.8%, since val/test specimen assignment is not itself class-balanced. | `Data/splits/{train,val,test}_manifest.csv`, `is_augmented` and `label` columns, computed directly with pandas this session | Paragraph rewritten to separate the global offline augmentation inventory (Table 3.5, recaptioned to say so explicitly) from the actual, smaller, leakage-filtered manifests actually used (3,846/75/75 = 3,996 total), with the freshly computed training-manifest class distribution stated explicitly rather than assumed identical to the global one. |
| Table 3.3 (robustness benchmark) captioned as "the best-selected model per target" | Table 3.3 is sourced from `benchmark_best_model_robustness.csv`, which reports the best model **per individual evaluation strategy** considered in isolation — a diagnostic comparison. The phase's actual final robustness-weighted selection is recorded separately in `outputs/models/hidden_damage/best_models.csv`. For `ultimate_load_kn` the two agree exactly (RandomForest, metadata_only, identical MAE/Spearman values). For `wire_area_loss_frac` they differ: the diagnostic per-strategy winner is RandomForest (MAE 0.105 group_shuffle / 0.124 LOCO), but the final robustness-weighted selection is CatBoost, metadata_only (group_shuffle MAE 0.1238, LOTO MAE 0.1161, LOCO MAE 0.1208, group_shuffle Spearman 0.2888, robustness_score 5.45). | `main_4/outputs/diagnostics/tables/benchmark_best_model_robustness.csv` vs. `main_4/outputs/models/hidden_damage/best_models.csv` (both re-`cat`'d directly this session) | Caption reworded to state this is a per-strategy diagnostic comparison; new paragraph added after Table 3.3/Fig. 3.5 explicitly distinguishing the diagnostic winner from the final robustness-weighted selection, with both target's exact final-selection numbers stated. |
| Section 4.7 said the pooled corrosion-load trend "is attributable to" the mesh/campaign group structure, and the mesh-stratified figure caption said the pooled trend "reverses sign within either mesh family" | Overclaims a full causal decomposition from correlational confounding evidence; and the 4-mesh result (ρ=-0.046, p=0.83) is a null result, not a sign reversal in the same sense as the 7-mesh result (ρ=-0.401) — the original wording blurred that distinction. | `main_4/outputs/ultimate_load_refocus/correlations/mesh_stratified_corrosion_vs_ultimate_load.csv` (re-verified via independent `scipy.stats.spearmanr` recomputation this session, exact match) | Prose changed to "the pooled trend is strongly influenced by between-group differences ... rather than demonstrating a direct effect," with an added clause noting the evidence does not "fully decompose the pooled association into its causal components." Figure caption changed to state the 4-mesh result is "approximately null" and the 7-mesh result is "negative," rather than describing both as a "sign reversal." |
| Proxy-RUL synthesis sentence described the four-step derivation as running "from repeated visible-corrosion observations" to a threshold-crossing quantity | Two of the four per-week series feeding the degradation curves are model-estimated structural quantities (Section 3.4.2), not observed visible-corrosion measurements; the original wording implied a pure image-to-RUL chain. | Cross-checked against the phase's own description already correctly stated earlier in the same section ("the two directly observed visible-corrosion measures and the two model-estimated structural measures") | Wording changed to "from repeated observed and model-estimated condition series," matching the phase's own already-correct description elsewhere in the section. |

**Chapter-level QC re-check after corrections:** re-grepped the full chapter
for "true RUL", "attributable to", "retains useful accuracy ... same
settings", "out-of-fold", and "image-only" — no remaining instances of the
corrected phrasings, and every surviving "image-only" reference is to a
genuinely image-only model (Phase 2), correctly distinguished from the
mixed-input structural models elsewhere. No further correction to frozen
Chapters 2–3 or to Batch A (Sections 4.1–4.4) was found necessary; all
Batch B corrections were self-contained within Sections 4.5–4.8, except
for the Figure 3.3/Table 3.2 caption and nearby prose in Section 4.4
(`sec:phase3-structural`), which was provisionally approved as part of
Batch A but is corrected here because the review flagged it directly.

## Chapter 5 (Integrated Results and Comparative Analysis) — synthesis evidence log

Chapter 5 synthesises Chapters 2–4 by scientific question rather than
repository phase; see `notes/chapter5_evidence_plan.md` for the full
per-question rationale (strongest supporting/contradicting evidence,
comparability judgement, bounded conclusion, deliberately-avoided
comparisons). This entry records only claims that are new to Chapter 5 —
newly computed this session, or newly stated as a synthesis-level
conclusion not present verbatim in any Chapter 4 row — rather than
duplicating every already-logged Chapter 4 fact Chapter 5 cites by
reference.

| Scientific question | Contributing phases/sources | Comparison type | Final wording limitation |
|---|---|---|---|
| Q1 Visible-corrosion reliability | Phase 1 (`main`), Phase 3 (`main_3`), Phase 4a (`main_4`) | Qualitative (robustness pattern) | Total-rust benchmarks stated as supportive, not headline, evidence given the tautology risk found independently in two phases (§4.2, §4.6). |
| Q2 Structural-condition reliability | Phase 3 (`main_3`), Phase 4a (`main_4`) | Qualitative + one explicit ratio | New synthesis-level claim: "the project's own best-performing, most carefully selected structural models therefore use no image input at all" — a direct restatement of the already-logged `best_models.csv` fact (Chapter 4 QC-pass row), elevated here to the chapter's central Q2 conclusion rather than a Section 4.6 aside. |
| Q3 Incremental image value | Phase 2 (`main_2`, explicitly flagged incomplete), Phase 4b (`main_4`, complete three-way) | Qualitative (main_2 vs.\ main_4 not compared numerically at all) | Explicit statement that main_2's two-way comparison cannot answer the incremental-value question; not previously stated this directly in Chapter 4, which described main_2's ablation as incomplete but did not draw the Q3 conclusion from it. |
| Q4 Regime sensitivity / robustness replication | Phase 3 (`main_3`), Phase 4a (`main_4`) | Ratio (regime MAE / own grouped-holdout MAE), cross-phase | **NEW, computed directly this session:** main_4 LOTO/GH ratios for all four targets (surface 0.549, peak 0.758, wire-loss 1.139, load 1.166) and LOCO/GH ratios (0.767, 0.964, 1.181, 3.236), from `main_4/outputs/diagnostics/tables/benchmark_best_model_robustness.csv`; main_3 equivalents (already-logged Table 3.2 MAEs, ratios computed fresh this session). Basis for Figure 5.1. |
| Q5 Degradation/proxy-RUL evolution | Phase 3 (`main_3`), Phase 4a (`main_4`) | Qualitative only (different target composition, thresholds, horizon) | **NEW, verified directly this session:** `main_4/configs/thresholds.yaml` (single-target `predicted_wire_area_loss_frac`, thresholds 0.20/0.30/0.40, `projection_horizon_days: 365`); `main_4/outputs/models/proxy_rul/proxy_rul_summary.json` and `proxy_rul_estimates.csv` (144 rows = 48 × 3 thresholds): `n_future_crossings_within_horizon = 0` at every threshold; `threshold_status` value counts `not_crossed_within_horizon`=97, `crossed_by_baseline`=45, `crossed_during_observation`=2. Cross-referenced against `main_4/NEXT_STEPS_PLAN.md` §2.3's open (unresolved) concern about implausible baseline wire-loss predictions — stated in Chapter 5 as an open concern, not a confirmed defect, consistent with the document's own framing. |
| Q6 Four-class classification status | Classification/augmentation effort only | Not applicable (no comparison) | No new facts; restates already-logged Chapter 4 §4.8 status. |

**Cross-cutting comparability rules enforced in drafting (restated from
the evidence plan):** no raw MAE/R² compared across phases without stating
protocol differences or using a ratio; "images contain signal" vs.\
"images add incremental value" kept distinct; every LOCO reference tied to
its extrapolation-stress-test framing; diagnostic vs.\ final-selected
structural models kept distinct; "proxy-RUL" never shortened to "RUL";
main_3's five-class results never placed in the same comparative sentence
as the current four-class branch.

**QC performed on Chapter 5 before finalising:** grepped the compiled
chapter source for "true RUL" (none — only "proxy-RUL", correctly
qualified throughout), causal-language markers ("attributable to", "due
to", "caused by" — none found), "image-only" (all three occurrences
correctly describe the genuinely image-only deep-embedding configuration,
never applied to a mixed-input model), and five-class/four-class markers
(schema distinction maintained in every occurrence, including in
Table 5.1's explicit "not compared" row for this pair). Visually inspected
the full compiled chapter (pages 34–41) after a LaTeX float-ordering fix
(see below).

**LaTeX fix applied:** the closing synthesis paragraph (following
Table 5.2) initially printed on the page *before* Table 5.2 itself,
because Table 5.2's float was deferred to a later page while the
following body text was not; a reader would have hit "read together,
these rows describe..." before ever seeing the table it refers to. Fixed
by adding `\usepackage{placeins}` to the preamble and a `\FloatBarrier`
immediately after each of Tables 5.1 and 5.2, forcing correct reading
order (verified in the recompiled PDF: Table 5.1 → its own discussion →
Table 5.2 → the closing paragraph, in that order, pages 39–41). Table 5.2
was also set in `\footnotesize` to reduce its footprint.

## Chapter 5 QC correction pass — targeted scientific review

Six issues raised by review, all resolved by direct re-verification against
repository outputs this session. Full rationale in
`notes/chapter5_evidence_plan.md`'s "QC correction pass" section; this
entry records the exact source-verified numbers.

| Issue | Verified fact | Source | Resolution |
|---|---|---|---|
| Chapter 5 claimed main_4 "reproduces" main_3's visible-corrosion treatment-level (LOTO) fragility | False. `benchmark_best_model_robustness.csv`: `surface_total_rust_pct` (GradientBoosting) LOTO MAE 0.0974 vs.\ GH MAE 0.1773 (ratio 0.549); `peak_rust_pct` (RandomForest) LOTO MAE 0.8314 vs.\ GH MAE 1.0968 (ratio 0.758); Spearman ≥0.97 for both. R² not in that table; computed directly from per-fold files `main_4/outputs/models/surface/{surface_total_rust_pct,peak_rust_pct}/leave_one_treatment_out/*_fold_metrics.csv` (9 folds each): mean R² = 0.9948 and 0.9574 respectively — near-perfect, not negative. main_4's LOTO uses 9 finer treatment groups (`split_group_treatment`) vs.\ main_3's 7 coarse protocols. | `main_4/outputs/diagnostics/tables/benchmark_best_model_robustness.csv`; `main_4/outputs/models/surface/.../leave_one_treatment_out/*_fold_metrics.csv`; `main_4/src/corrosion_proxy_rul/models_surface.py` (`treatment_col="split_group_treatment"`) | Section 5.2 (Robustness) and Section 5.5 rewritten to state main_3's LOTO collapse and main_4's LOTO robustness as two separate, non-replicating findings, with all three metrics (MAE, R², Spearman) reported; Table 5.2 updated on both affected rows. |
| Figure 5.1 ratio not a same-model comparison for main_3 (winning model changes by regime in Table 3.2, e.g.\ total rust: RF at GH/LOCO, MLP at LOTO) | Recomputed fixed-model (grouped-holdout-winner) ratios directly from `main_3/outputs/corrosion_regression_metrics.csv` and `damage_regression_metrics.csv` (per-fold rows aggregated by target/strategy/model): total rust (random_forest) GH 1.3814, LOTO/GH 1.194, LOCO/GH 1.517; peak rust (mlp_regressor) GH 4.2087, LOTO/GH 1.127, LOCO/GH 1.767; wire-area loss (random_forest) GH 3.8993, LOTO/GH 2.804, LOCO/GH 3.679; ultimate load (random_forest) GH 0.1207, LOTO/GH 1.311, LOCO/GH 5.375. main_4's existing ratios independently confirmed already fixed-model by reading `build_best_model_robustness()` in `main_4/src/corrosion_proxy_rul/diagnostics.py` — no change needed. | `main_3/outputs/corrosion_regression_metrics.csv`, `main_3/outputs/damage_regression_metrics.csv`; `main_4/src/corrosion_proxy_rul/diagnostics.py` lines 528–563 | Figure 5.1 regenerated (`activity_report/figures/generated_scripts/make_fig_5_1_robustness_synthesis.py`, v2) with corrected main_3 values; caption rewritten to name the exact fixed model per target/phase and state the grouped-holdout-winner selection rule explicitly. |
| "Same target" conflation in tautology synthesis; unverified label-construction provenance claim | Phase 1's near-tautology concerns peak-rust; main_4's directly-quantified near-identity (Spearman 0.9996) concerns `surface_total_rust_pct` — different targets. Also, `main/image_features.py` shows `img_rust_mask_pct` is computed by this project's own fixed-threshold colour-mask code, independent of the (manually assigned, per Chapter 2 §1.2) label; the repository does not establish that this feature is computed by "the same rule" used to assign the manual label. | `main/image_features.py` (lines 46, 60, 63, 81); Chapter 2 §1.2 (modality C, manually assigned labels) | Section 5.2 (Interpretability and the tautology risk) rewritten to separate the two findings by target and to replace "the same colour-threshold rule used to construct its own label" with "a rust-mask-derived feature closely aligned with the target," reserving "near label reconstruction" for the main_4 case where the near-identity is directly quantified. |
| Table 5.1 said proxy-RUL horizons were "104 vs.\ 365 days" | Wrong: main_3's horizon is 104 weeks (≈728 days), not 104 days. | Already-verified facts (main_3 `default.toml`: horizon 104 weeks; main_4 `thresholds.yaml`: `projection_horizon_days: 365`) | Corrected to "104 weeks ≈ 728 days versus 365 days ≈ 52 weeks." Checked full chapter source and both notes files for other "104-day" instances: none found; main prose already said "104-week" correctly throughout. |
| Closing paragraph described all three negative findings as "independently reproduced by later phases" | Not true of all three: campaign-confounded structural inference and proxy-RUL's non-validated status are each reinforced by an independent second phase/generation; the lack of incremental image value for terminal ultimate load rests on one phase's (main_4's) own three-way ablation, with no independent second experiment corroborating it. | Re-checked against already-established Chapter 4/5 facts; no new source needed | Closing paragraph rewritten to distinguish findings reinforced across independent phases (structural confounding, proxy-RUL) from a finding established by one well-designed experiment (incremental image value). |
| Table 5.2 rows ("Visible surface corrosion", "Cross-regime / cross-campaign robustness") still described treatment-level fragility as a replicated, project-wide conclusion | Follows directly from the first correction above | — | Both rows revised: campaign-level robustness and structural fragility stated as replicated; treatment-level visible-corrosion behaviour stated as phase-dependent/diverging, not settled. |

**Scope check:** targeted re-verification of Q2 (structural-condition),
Q3 (incremental image value, aside from the closing-paragraph wording),
and Q6 (four-class classification) during this pass did not surface any
further error; no change was made to those sections beyond what is listed
above.

## Chapter 6 (Scientific Interpretation and Research Decisions) — interpretive claims log

Chapter 6 interprets already-established Chapters 2–5 evidence; it does not
introduce new quantitative claims. See
`notes/chapter6_interpretation_plan.md` for the full per-question rationale
(empirical basis / safe inference / must-not-infer / resulting decision /
category label). This entry records only the one piece of evidence newly
located and quoted this session, plus a summary of each section's
empirical basis, interpretation, limitation, and resulting decision, per
instruction not to duplicate every Chapter 5 metric.

| Section | Empirical basis (already established, cited by reference) | Interpretation | Limitation stated | Resulting project decision |
|---|---|---|---|---|
| §5.1 Evidence hierarchy | Supervision density and model-dependence facts from Chapters 2–4 (Table 1.3; §3.4.2/§3.5 model-estimated vs.\ observed series) | Organises the project's five research questions as a hierarchy of decreasing directness | Explicitly stated as an organising explanation, not proof of downstream impossibility | None (conceptual framing only) |
| §5.2 Visible corrosion | Cross-phase replication of grouped-holdout accuracy (§4.2.1); two independent label-adjacency findings (§4.2.2); campaign-vs-treatment robustness divergence (§4.2.3/§4.5) | Dense, fine-resolution supervision plausibly explains the task's comparative learnability | High accuracy is not sufficient if the dominant feature reconstructs the label; the main_3/main_4 treatment-level (LOTO) divergence is stated as an established disagreement whose mechanism (possibly treatment-group definition/size/composition) is not established, and the visual task itself is not ruled out as a contributor | None new; interprets Phase-1→Phase-3 decision already reported |
| §5.3 Structural inference | Sparse single-timepoint supervision (§1.4); campaign/mesh/NaCl/duration entanglement (§1.6); cross-phase regime collapse (§4.3) | Sparse supervision plus design confounding is a major limitation consistent with the observed instability of structural models, not asserted as sufficient on its own to explain it | Explicit physical-relationship-vs-predictive-identifiability distinction; "surface corrosion does not affect structural capacity" is named as the wrong conclusion; "only two design points" corrected to "two campaign-level combinations of the principal design variables," with treatment variation within each campaign noted explicitly | None new; interprets Phase 4a's audit-and-reweighting decision already reported |
| §5.4 Metadata dominance | Metadata-only strongest pooled predictor (§4.4); campaign-alignment correlate magnitudes (§3.6); mesh-stratified/LOCO non-transfer (§4.3) | Metadata dominance admits two simultaneously true readings (genuine design signal; campaign shortcut) not adjudicated by pooled evidence alone | Metadata explicitly not described as invalid; the mesh-stratified/LOCO non-transfer evidence is stated as weakening the case for a transferable pooled relationship, not as proof that a genuine physical metadata effect does not exist; pooled usefulness and insufficiency stated as compatible, not contradictory | None new; interprets the three-way ablation design decision (Phase 4b) already reported |
| §5.5 Terminal-load refocus | Hidden-damage chain's compounding uncertainty (§4.5/§4.6); terminal load's single-timepoint direct measurement (§1.1) | Refocus is a scientifically motivated narrowing of claim scope to a more bounded, directly testable question, not a retreat; the longer hidden-state/degradation/proxy-RUL chain is described as substantially harder to validate and diagnose (disagreement cannot be cleanly attributed to one component without independent intermediate ground truth), not as "unfalsifiable" | Explicitly states what conclusion would be wrong ("failed experiment") | Interprets Phase 4b's own decision (already reported); no new decision |
| §5.6 Negative results | Six specific negative findings already established in Ch.\ 4/5 (incremental-value null result, mesh-stratified negative $R^2$, LOCO collapse, zero future-crossings proxy-RUL result, worsened residual correction) | Each negative result narrows defensible claims, exposes a confound, or motivates a specific check; the incremental-value null result is stated as evidence against the claim in this dataset under the tested pooled setting, not as a general "rules out" | None beyond what each finding already states | None new; synthesises already-reported findings |
| §5.7 Proxy-RUL contribution | Two-generation derivation (§4.6); **NEW this session, re-cited from the already-logged Chapter 4 QC-pass row:** `main_4/NEXT_STEPS_PLAN.md`'s "downstream optimism risk" language (in-sample refits vs.\ out-of-fold predictions) | Contribution is methodological/diagnostic (explicit observed-vs-estimated separation, threshold-status taxonomy, downstream-optimism risk made visible), not prognostic | True RUL validation requires a failure-event time or repeated structural measurements, neither present (§2.8) | None new; states the future-hypothesis data requirement already established in Chapter 3 §2.8 |
| §5.8 Classification direction | Data-preparation completeness (§3.8/§4.7); planned macro-F1/recall evaluation practice (§2.7) | Branch's preparation incorporates lessons the regression work learned incrementally, independent of eventual accuracy | Explicitly: no classifier trained, compared, or evaluated; no ResNet-50/ViT experiment exists | States (does not invent) the evaluation standard already specified in Chapter 3 for the not-yet-run training phase |
| §5.9 Methodological lessons | Synthesised from §5.2–5.7, each lesson cross-referenced to its source section | Seven lessons stated as this project's own accumulated position | Explicitly scoped to this project, not generalised to ML practice at large | None new |

**Housekeeping note:** the five rows above (§5.2, §5.3, §5.4, §5.5, §5.6)
were updated to match the final, QC-corrected chapter wording after the
"Chapter 6 QC correction pass" section further below identified several
pre-QC formulations that had not been carried back into this primary
summary table. The QC-pass section itself is left unchanged as the
historical record of what was found and why; this table now reflects the
frozen chapter's actual wording, not the draft that preceded it.

**QC performed before finalising:** grepped the compiled chapter for
causal-overclaiming markers ("caused," "X caused Y" — none found beyond
the neutral word "caused" not appearing at all); confirmed the
physical-relationship-vs-predictive-identifiability distinction is stated
explicitly (§5.3); confirmed metadata is explicitly stated as not invalid
(§5.4); confirmed true RUL is explicitly stated as unsupported and its
data requirements restated (§5.7); confirmed the four-class branch is
explicitly stated as untrained (§5.8); confirmed the terminal-load refocus
is explicitly framed as narrowing rather than failure (§5.5); and
confirmed near-zero repeated numeric results from Chapter 5 (a single
grep for decimal numbers in the chapter source returns only a
`\resizebox` width parameter, not a restated metric).

## Chapter 6 QC correction pass — targeted interpretive review

Eight micro-corrections applied after substantive approval of Chapter 6,
all softening over-strong or imprecise interpretive wording. No new
repository verification was required; each correction is a wording fix to
a claim already grounded in already-verified Chapter 4/5 facts. Full
rationale in `notes/chapter6_interpretation_plan.md`'s "QC correction
pass" section.

| Issue | Correction | Grounding fact (already verified) |
|---|---|---|
| Figure 6.1 / §6.1 implied a literal universal computational pipeline | Figure regenerated with dashed non-directional connectors, an explicit "increasing inferential distance" side-bracket, and an in-figure note that ladder position is not computational dependency; prose states feature inputs are phase-dependent, using the structural-estimate stage as the explicit counter-example | main_3 structural models are mixed-input; main_4 final structural selections are metadata-only (Chapter 4 §3.6 QC-pass row) |
| §6.2 implied treatment-group composition is *the* explanation for the main_3/main_4 LOTO divergence | Softened to "may partly reflect ... the available evidence establishes the disagreement itself, not its mechanism"; explicit that the visual task is not ruled out as a contributor | Chapter 5 §4.2.3 QC-pass finding: main_4 LOTO uses 9 finer treatment groups vs. main_3's 7 coarse protocols — a stated but unconfirmed mechanism |
| §6.3 overclaimed sparse supervision as sufficient explanation and mischaracterised design-point count | "Sufficient to explain" → "a major limitation consistent with"; "two independent design points" → "two campaign-level combinations of the principal design variables ... treatment variation still exists within each campaign" | Chapter 2 §1.6 (campaign/mesh/NaCl/duration alignment); Chapter 2 §1.1 (7 treatment protocols exist within the two campaigns) |
| §6.4 metadata counterfactual was deterministic ("should survive ... and it does not") | Replaced with "weakens the evidence that the pooled metadata relationship is transferable ... does not disprove a genuine physical metadata effect" | Chapter 4 §3.7.2–3.7.4 (mesh-stratified and LOCO non-transfer, already established) |
| §6.5 called the hidden-state/degradation/proxy-RUL question "not falsifiable" | Corrected to "substantially harder to validate and diagnose, because disagreement at the final stage cannot be cleanly attributed to one component without independent intermediate ground truth" | No new fact; wording precision only |
| §6.6 said a negative result "rules out" a claim | Narrowed to "provides evidence against ... in this dataset, under the tested pooled setting" | Chapter 4 §3.7.1 (pooled ablation result, single dataset) |
| §6.6/§6.7 used "all-zero-crossings" and an unquantified "attributable to baseline" decomposition | "Zero future-crossings result," explicitly distinguishing baseline-crossed/during-observation-crossed from (zero) future-projected crossings; decomposition claim softened to "consistent with ... although that decomposition was not itself quantified," with the repository's own "unresolved validation check" caveat restated | Already-verified Chapter 5 §4.6 finding: `main_4/outputs/models/proxy_rul/proxy_rul_summary.json`, `n_future_crossings_within_horizon=0` at all three thresholds; `main_4/NEXT_STEPS_PLAN.md`'s baseline-plausibility caveat (already logged) |
| §6.8 said the current four-class schema "supersedes" the historical five-level one | Corrected to "the historical five-level scheme used in the earlier dataset build" — schema evolution is verified; a deliberate supersession process is not | Chapter 2 §1.5, Table 1.6 (verified schema change between dataset builds, cause not established) |

**Verification of correction completeness:** grepped the compiled chapter
source for all eight flagged phrases ("should survive," "not falsifiable,"
"rules out," "all-zero-crossings," "supersedes," "two independent design
points," "sufficient to explain," "attributable to already-elevated") —
none remain.

## Chapters 7–9 (Software Engineering, Limitations, Current Status) — evidence log

Full per-item rationale in `notes/chapter7_9_plan.md`. This entry records
exact source/status for every engineering claim (Chapter 7) and marks
every Chapter 9 item completed/prepared/recommended/unresolved, per
instruction.

### Chapter 7 — engineering claims

| Claim | Exact source | Verified this session? |
|---|---|---|
| `main_4` config loading via `load_configs()`, six YAML files, `yaml.safe_load` | `main_4/src/corrosion_proxy_rul/config.py` | Yes, read directly |
| `main_3` centralised TOML config | `main_3/configs/default.toml` | Carried over (already cited Ch.4 §4.5) |
| Deterministic augmentation RNG, hash-derived per image/copy, default seed 20260630, seed recorded in generated report | `augmentation/augment_dataset.py` lines 91, 388–392, 780 | Yes, read directly |
| Split-manifest determinism via hardcoded, disjointness-checked specimen lists; `RuntimeError` on overlap/leakage | `augmentation/make_splits.py` (leakage check previously logged; disjointness check re-confirmed) | Yes |
| `random_state: 42` | `main_4/configs/modeling.yaml:1`, `main_4/configs/ultimate_load_refocus.yaml:1` | Yes |
| `requirements.txt` present in `main`/`main_2`/`main_3`/`augmentation`, absent in `main_4` | Directory listing of all five roots; `main_4/README.md` ("use the existing conda environment") | Yes |
| **YAML `NO`→`False` bug**: `treatment_coarse` = `"False"` for 168 rows in `master_table.csv`; `treatment_raw`/`treatment_protocol` unaffected; root cause is the unquoted `treatment_coarse: NO` literal in `specimen_mapping.yaml` | `main_4/configs/specimen_mapping.yaml` line 46 (and all `NO` entries); `main_4/outputs/data/master_table.csv`, `pandas.value_counts()` | Yes, re-verified and root-caused precisely to the YAML file this session (previously only the downstream symptom was logged) |
| **"1"/"first"→"main_first" pattern, broadened**: confirmed to also corrupt pandas aggregation-function names (`AttributeError` reproduced directly) and bare-numeral YAML hyperparameters (`n_jobs`, `reg_lambda`, `alpha`, `curve_grid_step_days`, `glcm_distances`, `strip_width_cm`, `train_size_fractions`); confirmed present in 9 files in `main_4` plus files in `main`, `main_2`, `main_3`; confirmed absent from `augmentation` | `grep -rl "main_first"` across the full repository; direct pandas reproduction of the `AttributeError`; each affected line read directly | Yes, new and substantially broader than previously logged |
| Timestamp clustering: most affected files at `2026-04-01 16:58:13`; two files in `main/` at `2026-04-08 14:10:24`; all cited output artifacts predate both | `stat -f "%Sm"` on ~15 files this session | Yes; mechanism/cause explicitly not claimed |
| NEXT_STEPS_PLAN.md item-by-item re-verification (feature-QC: done; raw/smoothed trajectories: done; feature-list persistence: partial; OOF for degradation: not done; analysis/model-ready table separation: not done) | `main_4/FEATURE_DIAGNOSTICS.md` + `diagnostics.py` (grep-confirmed generator); `main_4/outputs/models/degradation/degradation_raw_vs_monotone_proxy.csv`; `main_4/outputs/models/hidden_damage/hidden_damage_selected_feature_list.csv` + per-model `best_model.json` (keys checked); `main_4/outputs/models/surface/surface_feature_table.csv` | Yes, all five items individually re-checked this session rather than assumed |

### Chapter 9 — status classification

Every workstream in Table~9.1/§9.1 is explicitly labelled: **completed**
(dataset audit, visible-corrosion regression, structural feasibility,
robustness diagnostics, terminal-load refocus, degradation/proxy-RUL
screening — six workstreams); **prepared, not started** (four-class
classification — the only workstream in this category); **mixed**
(software/reproducibility cleanup — some sub-items completed, some live);
**in progress** (final report/documentation). §9.2's next-step checklist
and §9.3's data-requirement list are explicitly framed as recommendations,
not completed or scheduled work, per instruction; §9.4's cleanup list and
§9.5's validation list are likewise recommendations, cross-referenced to
Chapter 7 rather than re-verified independently.

**QC performed before finalising:** confirmed Chapter 7 cites only
project-specific files/lines, no generic MLOps prose; confirmed historical
corruption-handling policy (Table 1.5) is kept distinct from the two live
bugs; confirmed the category-schema difference is explicitly labelled
"not an instance of (A) or (B)"; confirmed the corruption's cause is
stated as unknown in both Chapters 7 and 8; confirmed Chapter 8 cites
Chapter 5 findings by reference without repeating metrics; confirmed the
physical-relationship-vs-predictive-identifiability distinction is
restated (not re-derived) in §8.4; confirmed Chapter 9's table uses
exactly three status categories plus "mixed"/"in progress" for the two
items that are neither purely completed nor purely prepared; confirmed
"zero future crossings" (not "zero crossings") in §8.5; confirmed no
ResNet-50/ViT result is described as obtained anywhere in Chapters 7–9.

## Chapters 7–9 QC correction pass — targeted review

Eight items corrected after substantive approval. Full rationale in
`notes/chapter7_9_plan.md`'s "QC correction pass" section.

| Issue | Re-verified fact | Resolution |
|---|---|---|
| §7.1 omitted the exploratory `main_first` phase from the repository-evolution count | `main_first/` exists as a directory and is already cited in Chapter 4 §3.1 (footnote, "earliest exploratory implementation"); `out/` and `main_4_old/` also exist but are, respectively, a dissemination layer (already established, Chapter 2) and an archival snapshot | §7.1 rewritten: `main_first` = exploratory prototype; `main`/`main_2`/`main_3`/`main_4` = four structured modelling generations; `augmentation` = later separate branch; `out/` and `main_4_old` explicitly excluded from the generation count |
| Corruption-timestamp claim ("every already-generated output artifact... predates," "every result... was generated before") was too broad | Re-checked timestamps of 26 specific saved output artifacts across `main`/`main_2`/`main_3`/`main_4` cited in Chapters 4–6 (`main/reports/*.csv`, `main_2/reports/*.csv`+figure, `main_3/outputs/*.csv`+`.parquet`, `main_4/outputs/**/*.csv`+`.json`, `main_4/FEATURE_DIAGNOSTICS.md`, `main_4/NEXT_STEPS_PLAN.md`, `main_4/configs/thresholds.yaml`): all dated 2026-03-06 to 2026-03-25, all predating both corruption timestamps (2026-04-01 16:58:13, 2026-04-08 14:10:24). **Exception found:** `main_4/configs/specimen_mapping.yaml` itself carries the *later* timestamp (2026-04-01 16:58:13) and does contain 6 instances of the "main\_first" pattern (a top-level `version: main_first` and five `series_description: Campaign main_first ...` narrative fields) — but the specific fields this report cites from that file (`treatment_protocol`, `n_steel_mesh`, `nacl_pct`, `terminal_week`, `terminal_days`, `campaign_id`, `series_id`) are unaffected; `campaign_id: campaign_1` (29 occurrences) is intact. Augmentation-branch artifacts (`Data/splits/train_manifest.csv`, `Documentation/augmentation_methodology_final.md`) are dated 2026-06-30, well after the corruption, but from the independently-verified-clean `augmentation/` codebase. | Chapter 7 §7.5 and Chapter 8 §8.7 both narrowed to "the saved scientific-output artifacts... that underpin the results reported here predate," with the `specimen_mapping.yaml` exception stated explicitly in Chapter 7 |
| Proxy-RUL status-table entry ("None required; not extendable without new data") conflated technical refinement with evidential validation | Cross-checked against Chapter 7 §7.6's own findings (OOF-for-degradation and feature-contract improvements are concrete, currently-unimplemented, existing-data-compatible engineering steps) | Table 9.1 entry revised to distinguish "further methodological refinement possible with existing data" from "validated prognostic claims require additional longitudinal/failure data" |
| §9.2 described classifier training as "the single highest-priority actionable step" without scoping to research/modelling workstreams specifically | The report itself (Chapters 1, 10, front matter, appendices) is still the project's immediate task | Reworded to "among the research and modelling workstreams... the highest-priority next technical step," with an explicit aside that completing the report remains the immediate task |
| §9.3 listed "running independent feature ablations" as an unimplemented improvement | `grep -n "ablation" main_4/NEXT_STEPS_PLAN.md` returns **no matches** — this was not a documented project recommendation. The terminal-load-focused phase already ran an explicit image-only/metadata-only/combined ablation for its own target (Chapter 4 §3.7, already established) | Item removed from the unimplemented-improvements list; a sentence added noting the existing ablation for terminal ultimate load and that no distinct, specific degradation-stage ablation recommendation is identified in the project's own documentation |
| §9.5 linked OOF structural predictions too closely to threshold validity, implying OOF regeneration would validate the thresholds | Conceptual distinction only; no new fact needed | Rewritten as two separate requirements: OOF regeneration before trajectories are read as genuinely out-of-sample, and independent domain/physical justification of threshold values, with an explicit sentence that OOF inputs do not themselves validate thresholds |
| Chapter 9's status table needed a way to remain provisional for one row without unfreezing the rest of the chapter | N/A (process fix) | Added a LaTeX-comment internal TODO directly above the "Final report/documentation" row of Table 9.1, and a matching note in `chapter7_9_plan.md`, both stating the row must be refreshed at final whole-report QA; Chapters 2–8 frozen, Chapter 9 frozen except this one row |

## Chapter 1 (Introduction and Project Scope) — evidence log

Chapter 1 was drafted last, entirely from already-frozen Chapters 2–9 and
the two predecessor sources already in `references.bib`; no new
repository verification was required or performed. Full per-claim
classification in `notes/chapter1_plan.md`.

| Section | Claim class | Source |
|---|---|---|
| §1.1 (durability context, dense-vs-sparse distinction, predecessor attribution) | Physical/experimental context + attribution | Chapter 2 §1.1/§1.2/§1.4 (frozen); `references.bib` (`hossain_thesis`, `artiste2025`); REPORT_PLANNING.md §8 item 3 (predecessor author distinct from present author, already resolved) |
| §1.2 (48 specimens, two campaigns, 791/792 aligned observations, supervision asymmetry) | Physical/experimental context + established finding | Chapter 2 §1.1/§1.2/§1.4/§1.5/§1.7 (frozen); no new numbers computed, all cited by reference only |
| §1.3 (five RQs) | Project objectives | Mapped directly onto completed Chapter 4/5 sections, per `chapter1_plan.md`'s RQ table; four-class branch deliberately not framed as a sixth RQ since untrained |
| §1.4 (activity list, five scope boundaries) | Completed activity + scope boundary | Chapter 4 (activity list); Chapter 3 §2.8, Chapter 5 §4.3/§4.4 (QC-corrected), Chapter 6 §6.3/§6.4, Chapter 9 §8.5, Chapter 2 Table 1.3 (five boundaries, each already frozen) |
| §1.5 (contributions A–G, bounded findings preview) | Completed activity + established finding (preview only, no metrics) | Chapters 2, 4, 5, 6, 7 (contributions); Chapter 5 §4.2–4.6 and Chapter 6 §6.7 (the four-bullet preview, stated at the same bounded level already used in those chapters' own closing synthesis, no new number introduced) |
| §1.6 (report organisation) | N/A (structural) | All chapter labels (`\ref`), no hard-coded numbers |

**QC performed before finalising:** grepped the compiled chapter for
unqualified "RUL" (only "proxy-RUL" and the explicit negation "no true RUL
supervision exists" found); causal wording (none found); "failure load"
(not used); "we reproduce the predecessor" (not used); "true structural
state" (not used); confirmed the four-class classifier is stated as
untrained twice. Confirmed, after inserting Chapter 1 and a full
three-pass recompile, that every chapter number shifted correctly
(Chapter 4→5 Integrated Results, 5→6 Interpretation, 6→7 Engineering,
7→8 Limitations, 8→9 Status) with zero undefined references and zero
"Rerun to get cross-references right" warnings remaining — confirming no
cross-reference in Chapters 2–9 was ever hard-coded to a chapter number.

## Chapter 10 (Conclusions and Next Steps) — evidence log

Chapter 10 is a pure synthesis of already-frozen Chapters 1–8 and
provisional Chapter 9; no new repository verification was performed or
needed, and no new numeric result appears anywhere in the chapter
(confirmed by grep: zero MAE/R²/Spearman/percentage/kN occurrences).

| RQ | Final answer as written (post-QC) | Source chapters | Attached qualification |
|---|---|---|---|
| RQ1 | Visible surface corrosion is the strongest, most consistently learnable image-based quantity, reached by three *distinct* representations | Ch.4, Ch.5, Ch.6 | Total-rust label-adjacency risk; campaign-level visible-corrosion robustness supported across both later phases; treatment-level behaviour is phase-dependent (**not** "campaign robustness consistently stronger than treatment robustness" — corrected, see QC pass below); bounded to this dataset |
| RQ2 | Structural inference substantially weaker and far less transferable | Ch.1, Ch.2, Ch.5, Ch.6 | Weaker results "must be interpreted in light of" (not "follow from"/"track directly to") sparse/terminal/campaign-confounded supervision; mixed-input vs. metadata-only structural models across implementations; LOCO exposes severe limits; does not establish absence of a physical relationship; explicitly states the relative contribution of data limitations, image information, and model representation is not isolated by the available experiments |
| RQ3 | No reliable pooled incremental image value for terminal ultimate load under the tested setting | Ch.4, Ch.5 | A post-onset analysis showed a limited improvement in some metrics (**not** a "conditional exception" — corrected) but did not overturn the pooled result; scoped to this target/representations only |
| RQ4 | Evaluation regime materially changes what can be claimed; grouped holdout insufficient alone for transfer claims | Ch.2, Ch.5, Ch.6 | LOCO is an extrapolative stress test, not ordinary future-performance estimate; treatment-level visible-corrosion fragility is phase-specific |
| RQ5 | Functioning methodological/diagnostic threshold-screening pipeline, not validated remaining-life prediction | Ch.5, Ch.6, Ch.7 | Model-derived trajectories; no true RUL supervision; zero *future* crossings (not zero overall); inputs not yet out-of-fold |

**Overall scientific conclusion (§10.2):** three-level hierarchy of
confidence (visible surface condition > hidden structural inference >
degradation/proxy-RUL), governed by target observability, supervision
density, label provenance, metadata controls, and evaluation design —
synthesised from Chapter 6 §6.1's evidence hierarchy by reference, not
redrawn or re-derived. Terminal-load refocus restated as a sound
narrowing of scope, consistent with Chapter 6 §6.5, not re-argued.

**Next steps (§10.3), explicitly labelled per instruction:** four-class
classification = prepared, not trained; OOF/artifact/reproducibility
refinement = recommended, with key items still incomplete (revised from
"recommended, not implemented" — some artifact/reproducibility work is
already partially done per Chapter 7 §6.6); additional campaigns/structural
measurements/lifetime data = future data requirement, not scheduled work.
All three compressed from, and cross-referencing, Chapter 9 §8.2/§8.3/§8.4
rather than duplicating their full checklists.

**QC performed before finalising (original draft):** grepped for numeric
content (none found beyond section/chapter numbers); confirmed "RUL"
appears only as "proxy-RUL," with one explicit "not a validated
remaining-life prediction method" negation; confirmed no causal wording;
confirmed "zero future crossings" (not "zero crossings"); confirmed the
classifier is stated as untrained twice; confirmed no deployment or
generalisation claim (both explicitly negated in §10.4); confirmed each of
the five RQs from Chapter 1 §1.3 receives an explicit, individually
labelled answer in §10.1; visually inspected the compiled chapter (3
pages) for correct cross-reference resolution.

### Chapter 10 QC correction pass (post-approval, targeted review)

Six items corrected after substantive approval; the RQ1–RQ3 rows above
already carry the corrected, primary wording. Full rationale in
`notes/chapter10_plan.md`'s matching "QC correction pass" section.

| Issue | Correction |
|---|---|
| RQ1 overstated "campaign-level robustness is consistently stronger than treatment-level robustness" | Chapter 5's fixed-model evidence (main_4 LOTO/GH MAE 0.549 total rust, 0.758 peak rust, both with strong R²/Spearman) shows treatment-level robustness holding in that phase; corrected to "campaign-level visible-corrosion robustness is supported across both later phases, whereas treatment-level behaviour is phase-dependent" |
| RQ2/§10.2 asserted a causal decomposition ("follows from," "tracks directly to... not primarily to any deficiency in the images or models") not established by the project's experiments | Reworded to "must be interpreted in light of" in both places; added an explicit sentence that the available experiments do not isolate the relative contribution of data limitations, image information, and model representation |
| RQ3 described the post-onset result as a "conditional exception" | Reworded to "a post-onset analysis showed a limited improvement in some metrics," removing the implication of a demonstrated exception; "did not overturn the pooled result" retained |
| Closing statement claimed "a reproducible, source-cited basis" | Corrected to "a progressively more reproducible and source-traceable basis," consistent with Chapter 7's own finding that push-button reproducibility is not currently achieved |
| "Three independent representations" (RQ1) | Corrected to "three distinct representations" |
| §10.3 heading "recommended, not implemented" | Corrected to "recommended, with key items still incomplete," since some artifact/reproducibility infrastructure is already partially implemented (Chapter 7 §6.6) |

No repository re-verification was required for any of these six
corrections — all are wording-precision fixes against already-frozen
Chapter 5/6/7 facts.

### Chapter 10 §10.2 — later correction (front-matter QC pass)

A seventh issue, found during the front-matter QC pass and corrected at
the same time: §10.2 stated terminal ultimate load was "the one structural
quantity measured directly, for every specimen, at a single defined
timepoint" — a genuine exclusivity error. The dataset has two directly
measured terminal structural endpoints (wire-area loss and ultimate load,
established since Chapter 2 §1.1); ultimate load is the one *selected*
for the refocused analysis, not the only one measured. Corrected to "one
of the two structural quantities measured directly, for every specimen,
at a single defined timepoint, and the one selected for this analysis."
See the front-matter QC entry below for the other three reader-facing
locations (two in the previously frozen Chapter 4) carrying the same
error, found by a full-report grep triggered by this same review.

## Front matter (Abstract, Executive Summary) — QC correction pass

Full rationale in `notes/front_matter_summary_plan.md`'s "QC correction
pass" section. Four items corrected after substantive approval:

| Issue | Correction |
|---|---|
| Executive Summary label-adjacency claim ("a benchmark can look accurate while substantially restating the rule used to construct its own label") reintroduced wording already removed from Chapter 5 | Corrected to name only the directly quantified case: "some strong visible-corrosion benchmarks rely on image-derived features that are very closely aligned with the target... the strongest case is the near-reconstructive total-rust pairing identified by the later feature audit" |
| "The one structural quantity directly measured for every specimen" — genuine exclusivity error, present in 4 reader-facing locations | Found by full-report grep: `frontmatter/executive_summary.tex` (finding 3), `chapters/01_introduction.tex` (Contribution D), `chapters/10_conclusions_and_next_steps.tex` (§10.2, see above), and **two instances in the previously frozen `chapters/04_research_and_development_activities.tex`** (Phase 4b section intro; Phase 4a→4b transition sentence) that had carried this error uncaught since Batch B. All corrected to "one of the two directly measured terminal structural endpoints... selected for this analysis" or equivalent. Post-fix grep for exclusivity variants confirms none remain anywhere in the report. |
| Abstract structural-inference sentence ("consistent with its sparse... supervision rather than an established deficiency of the images themselves") implied an isolated causal contrast not established by the experiments | Corrected to "must be interpreted in light of its sparse, terminal, campaign-confounded supervision," dropping the "rather than" contrast, consistent with the equivalent Chapter 10 RQ2 wording |
| Verification scope | No new repository verification required — all four corrections are wording-precision fixes against already-frozen Chapter 2/4/5 facts (the two structural endpoints have been established since Chapter 2 §1.1) |

**Note on scope:** this pass required editing two previously frozen
chapters (Chapter 1 and Chapter 4) beyond the front-matter files
themselves, because the exclusivity error pre-dated the front-matter work
and was only surfaced by the full-report grep this review triggered. Per
explicit instruction, this is treated as a legitimate factual correction
to an otherwise-frozen chapter, not a reopening of Chapter 4's substantive
content. Abstract word count after this pass: 301. Executive Summary
length unchanged (2 pages).

## Notes on scope of verification in this session

- Facts newly and directly re-verified in this session (not merely carried over): the full campaign/treatment/mesh/NaCl/terminal-week design matrix and specimen counts (`specimen_mapping.yaml`, parsed with Python); the 15–18 images/specimen and 25-week-range facts; the exact 48-row structural-label confirmation and its week values; the peak-rust category class counts; the `main`/`main_4` corrupted-image-handling code paths; and the YAML-boolean / `data_loading.py` string-corruption findings noted as caveats above.
- Facts carried over from the prior audit session's agent reports without re-opening the underlying files in this session: the precise mechanics of `main_2`'s embedding imputation, `main_3`'s split-strategy code, and the full model-family/metric inventory across all phases. These were already verified at the code level in the prior session and are lower-risk to carry forward than re-deriving from scratch; they are flagged here in case a later chapter needs a fresh check.
- No claim in Chapters 2–3 relies on evidence tier E (inference) for a scientific or quantitative statement; tier E is used only for the pedagogical leakage example in §3.2, which is explicitly presented as illustrative rather than as a historical event.

# Chapter 4, Batch A (Sections 4.1–4.4) — Evidence Selection Plan

Internal planning document. Not part of the final report. Written before drafting,
per instructions, to fix what evidence will and will not be used and why.

## Phase 0 — Exploratory prototype (`main_first`)

- **Research question:** can week-to-week visible rust percentage, and a heuristic
  notion of remaining service life, be estimated from images using an off-the-shelf
  colour mask and a single algorithm?
- **Target(s):** next-week rust percentage (regression); a hand-tuned rust-colour
  mask percentage as an intermediate quantity; an autoregressive threshold-crossing
  simulation loosely labelled "RUL."
- **Inputs/representation:** one fixed RGB colour-threshold mask per image; a few
  string-parsed identifiers (mesh/treatment/series) extracted from the specimen ID
  rather than read from structured metadata.
- **Models:** RandomForest only (classifier for one script, regressor for another).
- **Evaluation design:** inconsistent across scripts; critically, the script that
  produces the "production" model (`build_model.py`) fits on 100% of the data with
  no held-out partition at all.
- **Strongest useful result:** none reported with a defensible held-out estimate —
  no metrics are persisted anywhere in this phase (console prints only).
- **Most important limiting result:** the deployed/"production" model has zero
  train/test separation; RUL is produced by an autoregressive simulation loop, not
  a learned or validated target.
- **Diagnostic finding(s):** none — no diagnostics were computed at this phase.
- **Implementation issues materially affecting interpretation:** no persisted
  metrics; no specimen-level grouping in the production path; features derived by
  string-parsing the specimen ID rather than from the metadata table.
- **Decision motivating next phase:** the absence of any persisted, benchmarked,
  leakage-aware evaluation is itself the reason a properly benchmarked pipeline
  (Phase 1) was built next.
- **Figures/tables:** none exist for this phase; none will be created — a
  paragraph-level description is sufficient and proportionate to the phase's own
  rigor.
- **Verdict:** essential to mention (as motivation), but only briefly. No table
  row with fabricated metrics — there are none to report.

## Phase 1 — Classical-ML baseline (`main`)

Verified directly against `main/reports/*.csv` in this session:

| Task | Selected model | Holdout MAE | Holdout RMSE | Holdout R² | CV MAE |
|---|---|---|---|---|---|
| A. Current corrosion (`B_Peak_Rust_Percentage_[%]`, image+metadata) | RandomForest | 2.3794 | 4.2543 | 0.8996 | 3.0204 |
| B. Progression (metadata + week only, no image) | GradientBoosting | 6.7144 | 9.3294 | 0.5170 | 6.6850 |
| C. Time-to-threshold (weeks to 20% peak rust) | RandomForest | 2.2114 | 3.0947 | 0.7820 | 2.6535 |

- Feature importance for Task A (`main/reports/current_corrosion_feature_importance.csv`):
  `img_rust_mask_pct` alone = 0.9152 (91.5%) of RandomForest importance — verified exactly.
- Model-selection check (Task C): XGBoost has better holdout RMSE (2.824 vs 3.095)
  and R² (0.818 vs 0.782) than the selected RandomForest, which wins only on
  holdout MAE (2.2114 vs 2.2405) — confirms selection is driven by holdout MAE
  alone, and holdout data is used for both selection and reporting.
- **Diagnostic finding:** Task A's headline accuracy is largely a restatement of
  the same colour-threshold rule used to compute the label it predicts — a
  near-tautology, not evidence of learned generalisation from image content.
- **Task B is not a sequence/forecasting model:** verified in `data_utils.py`/
  `modeling.py` — Task B regresses the same current-week target from metadata and
  `week` alone, with no image input and no recurrent or sequential architecture.
- **Task C is not RUL:** the timing target is time-to-a-fixed-threshold, computed
  from *true* current corrosion (not a model's own prediction), and is explicitly
  a proxy quantity, not an observed service-life target.
- **Figures available:** `main/reports/fig_current_feature_importance.png` (Task A
  importance — could reuse, but the same information is more precisely stated as a
  single number in prose; a figure would add a dedicated page for one bar chart of
  limited independent value) — **decision: omit, cite the number in prose instead.**
  `main/reports/fig_holdout_mae_by_task.png` — mixes three tasks with incompatible
  units/targets on one axis; **decision: omit**, use Table 4.2 instead (units and
  task identity stated in a table are less ambiguous than a bar chart mixing weeks
  and percentages).
- **Table:** Table 4.2 (new, from the verified numbers above).
- **Decision motivating next phase:** whether a *learned* image representation
  (rather than a fixed threshold) could add genuine, non-tautological signal —
  motivates Phase 2.

## Phase 2 — Deep image-embedding experiment (`main_2`)

Verified directly against `main_2/reports/model_comparison.csv`,
`main_2/reports/training_history.csv`, and `main_2/main.tex` in this session:

- **Target:** `B_Peak_Rust_Percentage_[%]` (current-week peak rust, continuous) —
  same family of target as Phase 1 Task A, not a new/structural target.
- **Representation:** frozen, pretrained ImageNet ResNet-18 (`ResNet18_Weights.IMAGENET1K_V1`),
  final layer replaced with `Identity()`, run under `no_grad()` — a 512-d frozen
  embedding, **not fine-tuned**. Confirmed in `main_2/data.py`.
- **Two branches, not three:** `image_only_mlp` (embedding only) vs. `multimodal_mlp`
  (embedding concatenated with 7 metadata fields). **No metadata-only baseline was
  trained in this phase** — confirmed, no third model exists in `model_comparison.csv`
  or `run_info.json`.
- **Verified results:**
  - Best validation MAE during training (`training_history.csv`, minimum `val_mae`
    per model): image-only 4.9595 (epoch 14); multimodal 4.0161 (epoch 45).
  - Test MAE (`model_comparison.csv`): image-only 5.6255; multimodal 5.7476.
  - Deployed model: `image_only_mlp` (`run_info.json: "best_model": "image_only_mlp"`),
    selected because it has the lower **test** MAE — despite multimodal having the
    better **validation** MAE. This is a test-set-driven selection, carried out on
    the same partition used to report the final metric.
- **Late-stage bias, verified directly against `main_2/main.tex` (lines 536-540):**
  weeks ≤10: MAE 2.220, bias +0.854; weeks 12–20: MAE 6.617, bias −1.314; weeks ≥23:
  MAE 12.075, bias −6.912. Systematic underestimation of severe, late-stage corrosion.
- **792-row basis:** confirmed via `run_info.json` (`"rows": 792`) and `data.py`
  (corrupted embedding → NaN → column-median fill) — one sentence only, full story
  already told in Chapter 2.
- **Figures:**
  - `main_2/reports/figures/05_model_comparison.png` exists but shows **test MAE
    only** with a truncated y-axis that visually flattens the (small) gap and
    entirely omits the validation-MAE reversal, which is the actual scientific
    point. **Decision: do not reuse as-is; create a new two-panel figure (Fig. 4.1)
    from the same underlying verified numbers (validation MAE and test MAE, both
    models), so the reversal is visible.** Documented as reproducible from
    `training_history.csv` + `model_comparison.csv` in evidence_log.md.
  - `main_2/reports/figures/04_residual_vs_week.png`: genuine, directly generated
    project figure; clearly shows growing negative residuals at later weeks across
    all series. **Decision: reuse as-is (Fig. 4.2)**, copied into
    `activity_report/figures/` with a provenance-preserving name, new caption.
  - Per-material trajectory panels (`per_material/*.png`, e.g. D05): informative in
    the original report but too granular for the main chapter narrative; **omit**,
    optionally referenced in an appendix later.
- **Decision motivating next phase:** the phase's own future-work section
  recommends returning to interpretable, image-derived descriptors and comparing
  them against the deep-embedding approach — the direct, code-documented seed of
  Phase 3.

## Phase 3 — Interpretable corrosion quantification and structural-condition feasibility (`main_3`)

Verified directly against `main_3/outputs/corrosion_regression_metrics.csv`,
`main_3/outputs/damage_regression_metrics.csv`, `main_3/src/orchestration.py`, and
`main_3/main.tex` in this session (all numbers below independently recomputed from
the CSVs and cross-checked against the project's own summary table in `main.tex`,
which matched exactly).

- **Category-schema check:** `main_3/outputs/canonical_dataset.csv` uses a
  **five**-level ordinal scale for both corrosion category targets (already
  established in Chapter 2, Table 1.6) — Chapter 4 must not call these "four-class."
- **91-feature representation:** spans colour (RGB/HSV/Lab), texture (GLCM/LBP),
  morphology/connected-components, and spatial/segment location. Not an exact
  reproduction of the predecessor GIMP/BIMP/MATLAB workflow — a Python
  reconstruction and extension, per the phase's own report language.
- **Visible-corrosion results** (best mean model per regime, verified against CSVs):

  | Target | Regime | Model | MAE | RMSE | R² |
  |---|---|---|---|---|---|
  | surface_total_rust_pct | group_shuffle | RF | 1.381 | 3.142 | 0.646 |
  | surface_total_rust_pct | LOCO | RF | 2.096 | 3.906 | 0.582 |
  | surface_total_rust_pct | LOTO | MLP | 1.533 | 2.659 | −0.677 |
  | peak_rust_pct | group_shuffle | MLP | 4.209 | 6.234 | 0.784 |
  | peak_rust_pct | LOCO | HGB | 6.211 | 8.883 | 0.595 |
  | peak_rust_pct | LOTO | RF | 4.742 | 7.245 | −0.077 |

  (Five-category classification results also verified: group_shuffle accuracy
  0.830/0.591, macro-F1 0.573/0.531 for surface/peak; degrading under LOCO/LOTO,
  macro-F1 never exceeding ~0.47 under either stricter regime.)
- **Structural-condition results** (verified against `damage_regression_metrics.csv`):

  | Target | Regime | Model | MAE | RMSE | R² |
  |---|---|---|---|---|---|
  | wire_area_loss_pct | group_shuffle | RF | 3.899 | 4.995 | 0.310 |
  | wire_area_loss_pct | LOCO | HGB | 12.280 | 15.410 | −0.387 |
  | wire_area_loss_pct | LOTO | HGB | 10.759 | 13.065 | −5.481 |
  | ultimate_load_kn | group_shuffle | RF | 0.121 | 0.168 | 0.385 |
  | ultimate_load_kn | LOCO | ExtraTrees | 0.624 | 0.655 | −8.356 |
  | ultimate_load_kn | LOTO | RF | 0.158 | 0.189 | −4.569 |

  These are **main_3-specific, 792-row-basis, historical** results and are never
  placed next to main_4's later 0.174/0.173 kN figures as if from the same
  experiment.
- **Damage feature list, verified directly against `main_3/src/orchestration.py`
  (`_damage_feature_columns`, lines 230–255):** includes metadata (week, mesh
  count, ageing days, NaCl%, cover, treatment/campaign/series codes), **manual**
  corrosion labels (`surface_total_rust_pct`, `peak_rust_pct`, and their
  categories — ground truth, not model predictions), and a subset of the image
  features. **Confirmed: the model's own upstream-predicted corrosion values are
  not in this feature list** — only the manually assigned labels are. The damage
  stage is therefore mixed-input, not image-only, and does not chain a corrosion
  *prediction* into a damage *prediction*.
- **Feature-importance / correlation diagnostics, verified against `main_3/main.tex`
  lines 583–585:** for ultimate load, top RF importances are `n_steel_mesh` (0.172)
  and two one-hot campaign indicators (0.128, 0.105) — campaign-linked metadata
  dominates over image-derived features. Structural-label correlations: total rust
  vs. wire loss r=0.021; peak rust vs. wire loss r=0.011 (both computed over the 48
  structural rows).
- **In-sample refit, verified directly against `orchestration.py` lines 294–316:**
  the final damage estimator for each target is fit on all 48 structural rows (no
  held-out partition at this final step) and then applied to all 792 rows to
  produce `estimated_wire_area_loss_pct`/`estimated_ultimate_load_kn` at every
  observation week — these are the "model-derived" intermediate structural states
  from Chapter 2's Table 1.3, not repeated measurements.
- **Figures:**
  - `main_3/reports/figures/grouped_regression_mae_summary.png` and
    `corrosion_model_mae.png`/`damage_model_mae.png`: all show group_shuffle-only
    comparisons across model families; **none show the group_shuffle vs. LOCO vs.
    LOTO robustness contrast**, which is the chapter's central diagnostic point.
    **Decision: do not reuse; create one new figure (Fig. 4.3)** — grouped R² by
    split regime for the four continuous targets — generated directly from the
    two verified CSVs above (documented as reproducible in evidence_log.md).
  - `corrosion_regression_parity.png` / `damage_regression_parity.png`: real
    parity plots, potentially useful but largely redundant with the numeric
    table once R² is already reported; **omit from the main chapter**, candidate
    for an appendix.
  - Meeting-report figures (`dataset_overview.png`, `feature_alignment.png`,
    `corrosion_examples.png`): overlap with material already in Chapter 2;
    **omit**.
- **Tables:** Table 4.3 (new, compact version of the two verified result tables
  above, GroupShuffle/LOTO/LOCO columns as requested).
- **Decision motivating next phase:** Phase 3's own report already names campaign
  confounding and the sparse-structural-supervision bottleneck explicitly — the
  next phase (Section 4.5 onward, not written in this batch) quantifies and acts
  on these already-identified problems rather than discovering them.

## Overall figure/table budget for this batch

- Figures: 2 new (Fig. 4.1 main_2 validation/test MAE; Fig. 4.3 main_3 robustness
  by split regime) + 1 reused-as-is (Fig. 4.2, main_2 residual-vs-week).
- Tables: Table 4.1 (phase-level compact summary, Phases 0–3), Table 4.2 (Phase 1
  task results), Table 4.3 (Phase 3 representative results by regime).
- Deliberately omitted: Phase-1 feature-importance and holdout-MAE-by-task bar
  charts (redundant with prose/table and mix incompatible units); main_2's
  existing model-comparison bar chart (misleading due to truncated axis and
  missing validation panel) and per-material trajectory panels (too granular);
  main_3's existing MAE-by-model bar charts (group_shuffle only, do not show the
  robustness story) and parity plots (redundant with reported R²).

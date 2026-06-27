# Model Improvement Plan

## Scope

This round will only implement focused refinements already justified by the current diagnostics. The core formulation remains:

surface corrosion progression -> hidden damage estimation -> degradation modelling -> proxy-RUL / threshold-status

No new model families will be added. The existing tree-ensemble baselines remain the only candidate learners.

## Evidence Base

- `FEATURE_DIAGNOSTICS.md`
- `BENCHMARK_DIAGNOSTICS.md`
- `OUTPUT_REVIEW.md`
- `outputs/diagnostics/tables/feature_inventory_by_stage.csv`
- `outputs/diagnostics/tables/high_collinearity_pairs.csv`
- `outputs/diagnostics/tables/benchmark_best_model_robustness.csv`

The key facts driving this plan are:

- the surface stage is partly tautological and should not be treated as the main optimization target
- the current feature space is redundant and contains degenerate columns
- hidden-damage results are weak, especially for `wire_area_loss_frac`
- structural performance collapses under leave-one-campaign-out
- degradation and proxy stages currently inherit optimistic upstream hidden-damage outputs

## Planned Changes

### 1. Feature-space cleanup

Implement stage-aware feature filtering with full traceability.

- keep the existing hard QC exclusions
- add automatic removal of near-constant columns from model-ready matrices
- add exact-duplicate removal from model-ready matrices
- add correlation pruning for numeric features using a conservative threshold, with protected features retained only when scientifically justified
- save before/after feature inventories and exclusion reasons

Rationale:
- the diagnostics already showed redundant and degenerate features
- this is a justified cleanup, not a new modelling idea

### 2. Hidden-damage model improvement

Refine the hidden-damage stage only through disciplined preprocessing and selection.

- evaluate filtered feature sets instead of the current broad matrix
- add optional reversible target transformation for `wire_area_loss_frac` only if it improves robustness, not only grouped MAE
- compare feature-family ablations for hidden-damage targets
- switch final hidden-damage model selection from “lowest grouped MAE only” to a robustness-aware rule that considers:
  - grouped MAE
  - leave-one-treatment-out MAE
  - leave-one-campaign-out MAE
  - grouped Spearman as a secondary signal
- save explicit model-ready feature lists per target and per stage

Rationale:
- the current winner selection is too permissive for a confounded, small-sample structural stage
- feature-family ablations are directly supported by the diagnostics request and do not change model families

### 3. Campaign-confounding mitigation

Add controlled comparisons to measure shortcut dependence.

- benchmark the hidden-damage stage with:
  - the cleaned full feature set
  - a campaign-sensitive reduced set with obvious shortcut features removed
  - an image-plus-time oriented set for comparison
- save a campaign-confounding comparison table
- report explicitly when a feature set improves grouped metrics but worsens leave-one-campaign-out robustness

Rationale:
- leave-one-campaign-out collapse is currently the central limitation
- this step measures confounding rather than hiding it

### 4. Degradation and proxy refinement

Propagate the improved hidden-damage outputs downstream while staying conservative.

- rebuild degradation inputs from the improved hidden-damage stage artifacts
- save raw proxy trajectories and monotone-smoothed trajectories together
- retain the current degradation families, but make the report language explicitly descriptive
- keep proxy outputs in threshold-status form
- update proxy summaries so the interpretation is tied to improved upstream hidden-damage predictions without implying decision-grade residual life

Rationale:
- downstream stages should reflect the improved upstream structural model, but the scientific claims must remain limited

### 5. Before/after comparison outputs

Generate explicit baseline-vs-improved artifacts.

- baseline vs improved benchmark comparison CSV
- before/after feature inventory comparison CSV
- feature ablation results CSV
- split-strategy robustness comparison CSV
- campaign-confounding comparison CSV
- updated `MODEL_IMPROVEMENTS_APPLIED.md`
- updated `MODEL_IMPROVEMENT_RESULTS.md`

## Stages To Rerun

Only affected stages will be rerun:

- `train_hidden_damage_models.py`
- `train_degradation_models.py`
- `train_rul_proxy_models.py`
- `run_diagnostics_visualizations.py`

The surface stage will only be touched if required for feature-inventory consistency, not for target optimization.

## Success Criteria

This round counts as useful if it produces at least one of the following without overstating the result:

- a smaller, better-documented hidden-damage feature space
- improved robustness for `ultimate_load_kn`
- improved or at least clearer stability for `wire_area_loss_frac`
- clearer evidence about whether campaign-linked shortcuts drive apparent performance
- cleaner downstream degradation / proxy outputs tied to the improved upstream stage

If robustness does not improve, the result will still be reported honestly as a negative finding.

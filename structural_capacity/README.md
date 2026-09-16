# Structural capacity: terminal-load study and earlier robustness work

This folder contains the most mature structural experiments in the project,
formerly named `main_4/`. The later study asks whether image-derived surface
corrosion descriptors improve terminal ultimate-load estimates beyond specimen
metadata. Earlier surface, hidden-damage and exploratory proxy-RUL experiments
are retained as separate historical phases.

**Current status:** saved results are available for review. The present modelling
source has unresolved execution/configuration defects and has not been validated
as an end-to-end reproduction. See [known issues](../docs/known_issues.md).

## Start with the important results

| Question | Saved evidence |
|---|---|
| What did the terminal-load study find? | [Main results summary](outputs/ultimate_load_refocus/summary/ultimate_load_refocus_summary.md) and [grouped feature comparison](outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/feature_set_comparison.csv) |
| How strong is the metadata baseline? | [Metadata-only Ridge bundle](outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge), including [terminal held-out predictions](outputs/ultimate_load_refocus/pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/terminal_oof_predictions.csv) |
| Does the result transfer between campaigns? | [Campaign-holdout comparison](outputs/ultimate_load_refocus/pooled_all_weeks/leave_one_campaign_out/feature_set_comparison.csv) |
| What changes across cohorts and refinements? | [Mesh-stratified results](outputs/ultimate_load_refocus/mesh_stratified), [post-onset sensitivity](outputs/ultimate_load_refocus/pooled_post_onset) and [specimen-gap/refinement summary](outputs/ultimate_load_refocus/summary/specimen_gap_refinement_summary.md) |
| Where is the full scientific account? | [Final article](../final_reports/article.pdf), [thesis](../final_reports/thesis.pdf) and [cross-project experiment map](../docs/experiments.md) |

In the saved pooled grouped evaluation, metadata-only Ridge and metadata+HSV Ridge
both have mean fold MAE about **0.173 kN**; the image features did not establish a
consistent improvement. Campaign holdout is much weaker: the selected metadata-only
GradientBoosting model has mean MAE about **0.465 kN**. These are different selected
estimators and evaluation protocols; consult the linked comparisons before ranking them.

## Historical experiment phases

| Phase | Purpose and entry points | Outputs to inspect |
|---|---|---|
| 1. Surface and structural baseline | [run_full_baseline.py](run_full_baseline.py) chains data validation, image features, surface/hidden-damage training, degradation and threshold-status analysis. The individual `train_*` files run those stages. | [Baseline model results](outputs/models), [data](outputs/data) and [specimen splits](outputs/splits) |
| 2. Diagnostics and robustness refinements | [run_diagnostics_visualizations.py](run_diagnostics_visualizations.py) summarizes saved outputs; [run_model_improvement_analysis.py](run_model_improvement_analysis.py) compares the earlier snapshot with refined models. | [Diagnostics](outputs/diagnostics), [improvement comparisons](outputs/improvements) and [retained baseline snapshot](outputs/improvements/baseline_snapshot) |
| 3. Direct terminal-load refocus | [run_ultimate_load_refocus.py](run_ultimate_load_refocus.py) is the later workflow, configured by [ultimate_load_refocus.yaml](configs/ultimate_load_refocus.yaml). | [Refocus results](outputs/ultimate_load_refocus), [refocus specimen partitions](outputs/ultimate_load_refocus/splits) and [original refocus audit](outputs/ultimate_load_refocus/audit/repo_audit.md) |

`run_learning_curve_analysis.py` and `run_ultimate_load_diagnostic_plots.py` support
the earlier surface/hidden-damage experiments. The refocused workflow has its own
experiment-specific diagnostics and learning curves. `run_ultimate_load_mesh_analysis.py`
examines within-mesh relationships; `run_degradation_all_specimens_panel.py` plots
the earlier model-derived degradation trajectories. Their filenames alone do not
identify a common benchmark or evaluation protocol.

## Folder map

| Location | Purpose |
|---|---|
| [configs/](configs) | Dataset, specimen mapping and modelling settings |
| [src/corrosion_proxy_rul/](src/corrosion_proxy_rul) | Implementation shared by the workflows; the package retains its historical name |
| [Data/](Data) and [Documentation/](Documentation) | Local inputs and supporting experimental documents |
| [outputs/audit/](outputs/audit), [outputs/data/](outputs/data), [outputs/features/](outputs/features) | Alignment checks, prepared tables and extracted features |
| [outputs/ultimate_load_refocus/](outputs/ultimate_load_refocus) | Main terminal-load results, splits, predictions, comparisons and summaries |
| [outputs/models/](outputs/models), [outputs/diagnostics/](outputs/diagnostics), [outputs/improvements/](outputs/improvements) | Earlier models, diagnostics and refinement evidence |
| [outputs/reports/](outputs/reports) | Structural report exports and destination for future generated baseline notes |
| [OUTPUT_INVENTORY.csv](OUTPUT_INVENTORY.csv) | Historical inventory; entries describe the state when it was generated |

The top-level `.tex` files and PDF exports are retained historical material.
The reviewed project delivery is the article/thesis in `../final_reports/`.
Existing result summaries remain beside their corresponding outputs.

## Continue or reproduce the work

The dataset has **791 aligned observations from 48 specimens**, with only one
terminal structural outcome per specimen. Preserve specimen-level splits and
terminal evaluation scope. Campaign, mesh, chloride and exposure are confounded.
Surface descriptors do not directly measure hidden damage, and model-derived
threshold curves do not establish validated remaining life.

Read the [reproduction guide](../docs/reproduction.md) and [known issues](../docs/known_issues.md)
before execution. Use a complete separate copy for new runs: the current scripts
can replace outputs, and several train models even when named as an analysis.
Run structural scripts with `structural_capacity/` as the working directory because
they import the relative `src/` package. Merely opening this README requires no run.
The [experiment map](../docs/experiments.md#structural-robustness-and-terminal-load-phases)
lists the historical command sequence.

## Historical notes and generated documentation

The nine former top-level Markdown shortcuts have been removed. Their original
contents remain in the [development archive](../archive/agent_working_notes/main_4),
including the [scientific report](../archive/agent_working_notes/main_4/SCIENTIFIC_REPORT.md),
[constraints](../archive/agent_working_notes/main_4/PROJECT_CONSTRAINTS.md),
[improvement plan](../archive/agent_working_notes/main_4/MODEL_IMPROVEMENT_PLAN.md)
and [improvement results](../archive/agent_working_notes/main_4/MODEL_IMPROVEMENT_RESULTS.md).
These documents describe historical stages. Old recorded paths can still be
located with the root `research_paths.py` helper.

Future generation writes notes to existing output groups:

- `outputs/reports/`: `BASELINE_WORKFLOW.md` and `SCIENTIFIC_REPORT.md`.
- `outputs/diagnostics/`: feature/benchmark diagnostics, figure review and visualization plan.
- `outputs/improvements/`: applied-change and result summaries.

These files are created only when their respective generators run. The generators
preserve this hand-maintained README and the archived notes. The
[cleanup and recovery record](../archive/repository_maintenance/structural_documentation/README.md)
records the path changes and preservation checks.

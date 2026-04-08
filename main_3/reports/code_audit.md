# `main_2` Code Audit

## Reused

- `main_2/data.py`
  Why: the Excel sheet uses a semantic first row rather than a normal header row, and the ID parsing plus grouped specimen split logic were correct and reusable.
  Refactored into: `main_3/src/data/io.py`, `main_3/src/data/canonical.py`, `main_3/src/cv/splits.py`

- `main_2/visualize.py`
  Why: plotting patterns for parity plots, grouped metrics, and progression summaries were reusable at the reporting level.
  Refactored into: `main_3/src/visualization/plots.py`

- `main_2/report_writer.py`
  Why: report generation as Markdown was a useful pattern for reproducible experiment summaries.
  Refactored into: `main_3/src/evaluation/reports.py` and `main_3/src/orchestration.py`

- `main_2/config.py`
  Why: centralized path handling and deterministic seed management were correct engineering choices.
  Refactored into: `main_3/src/config.py`

## Modified

- `main_2/train_phase2.py`
  Why modified: the previous training entry point only handled one regression target, used deep image embeddings, and assumed a torch-based pipeline. The new implementation needed multi-stage orchestration, multiple targets, grouped evaluation strategies, degradation modelling, and proxy-RUL estimation.
  Replacement: `main_3/src/orchestration.py` plus the scripts in `main_3/scripts/`

- `main_2/models.py`
  Why modified: the old MLP head was tied to a ResNet feature extractor and one continuous target. The new project needs classical regressors/classifiers for corrosion and hidden-damage stages, with optional future extension to other estimators.
  Replacement: `main_3/src/models/common.py`, `main_3/src/models/corrosion.py`, `main_3/src/models/damage.py`

## Discarded

- `main_2/inference.py`
  Why discarded: it depends on pretrained ResNet18 embeddings and torch artifacts that are not available in the current environment and do not match the final scientific formulation.

- `main_2/api.py`
  Why discarded: API deployment is not part of the required `main_3` deliverable, and the old API only exposed current peak-rust inference rather than the corrosion-to-RUL pipeline.

- `main_2/build_pdf_report.py`
  Why discarded: it was tightly coupled to the phase-2 report schema and single-target outputs. `main_3` uses stage-specific data products and Markdown-first reporting.

- `main_2/artifacts/*`
  Why discarded: the saved torch state, scaler, and joblib preprocessing artifacts are specific to the previous baseline and are not reusable for the new classical feature pipeline.

- `main_2/reports/*`
  Why discarded: these are phase-2 outputs, not source code. They remain useful as historical context but were not copied into `main_3`.

## Audit conclusion

`main_2` contained sound engineering around dataset parsing, grouped splitting, and reporting, but its core modeling stack was too narrow for the final objective. The reusable logic was refactored into `main_3`; the torch-specific multimodal baseline was not carried forward because the final system must model corrosion progression, hidden damage, degradation, and proxy-RUL while respecting the dataset’s lack of true failure-time supervision.

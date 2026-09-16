# Frozen image embeddings — historical experiment

This phase compares image-only regression with regression that also uses tabular
context to predict **peak surface rust percentage** (`B_Peak_Rust_Percentage_[%]`).
A pretrained ResNet-18 produces 512 image features; its weights remain frozen while
a small neural network learns the regression task.

Formerly `main_2/`, it follows [classical corrosion models](../classical_corrosion/README.md)
and precedes [interpretable condition assessment](../condition_assessment/README.md).
The saved winner is **`image_only_mlp`**, with `use_tabular: false`. The older
report's “multimodal” title describes the comparison, not the selected model's inputs.

**Status:** saved results can be inspected. A complete rerun has not been verified,
and recorded compatibility checks found a blocker in the inference/API loader.
See the reproduction notes below and the [shared known issues](../docs/known_issues.md).

## Start with the evidence

| Question | Files to read |
|---|---|
| What was the experiment? | [Scientific report](reports/phase2_scientific_report.md), [historical full PDF](reports/phase2_scientific_report_full.pdf) |
| Which model was selected? | [Model comparison](reports/model_comparison.csv), [run metadata](artifacts/run_info.json) |
| Which records were predicted? | [Predictions with train/validation/test labels](reports/predictions_best_model.csv) |
| Where did performance vary? | Test metrics by [treatment](reports/metrics_by_treatment.csv), [series](reports/metrics_by_series.csv) and [specimen](reports/metrics_by_specimen.csv) |
| How did training progress? | [Training history](reports/training_history.csv), [learning curves](reports/figures/00_learning_curves.png) |
| Which figures support the results? | [Test predictions](reports/figures/02_pred_vs_true_test.png), [residuals](reports/figures/03_residual_distribution.png), [all figures](reports/figures/), [specimen trajectories](reports/figures/per_material/) |

Keep the scientific report and its supporting tables. The `pdf_table_*.csv` files
are historical report exports; their scope can differ from the test metrics.
In particular, [PDF table 5](reports/pdf_table_5_material_level_results.csv) summarizes
all specimens across splits. The report and run metadata retain historical absolute
paths; the links here point to their current locations. Current deliverables are
the [final thesis and article](../final_reports/README.md).

## Saved experiment and main result

The saved predictions contain **792 records from 48 specimens**, covering weeks
0–36. They record **504 training rows / 30 specimens**, **129 validation rows /
8 specimens**, and **159 test rows / 10 specimens**. Specimen identities do not
overlap between these saved splits. The run metadata records seed 42 and one
corrupted image, `E01-20240508-17W`.

Values below come from the saved [comparison table](reports/model_comparison.csv):

| Model | Test MAE (percentage points) | Test RMSE (percentage points) | Test R² |
|---|---:|---:|---:|
| Image-only MLP | 5.6255 | 9.2639 | 0.5237 |
| Image + tabular MLP | 5.7476 | 9.8652 | 0.4599 |

The image-only model has the lower recorded test error in this run. This single
comparison does not establish that tabular context is generally unhelpful.

Interpret the results with these limits:

- **Model selection consulted test performance.** The training script chooses the
  saved model by lowest test MAE, after using validation MAE for early stopping.
  The selected test result is therefore not an untouched final evaluation.
- **Predictions contain all splits.** Filter `split == "test"` for test metrics.
  Treatment/series progression plots and the 48 specimen trajectories include
  training and validation records; they are descriptive and do not demonstrate
  prospective forecasting or remaining useful life.
- **Severity is derived from regression.** Low is below 1%, medium is 1% to below
  20%, and high is at least 20%. These are three interpretation bands, distinct
  from the later [four-class preparation](../classification_data_preparation/README.md).
- **Corrupted-image handling needs review for reproduction.** The current extractor
  fills missing embedding values using medians computed across the whole dataset.
  The corrupted record remains in this historical 792-row result.

## Code and model bundle

| File | Role |
|---|---|
| [train_phase2.py](train_phase2.py) | Runs both training variants, selects a model, writes predictions, metrics, figures, artifacts and the Markdown report |
| [data.py](data.py) | Reads the spreadsheet/images, creates specimen splits, prepares tabular inputs and extracts frozen embeddings |
| [models.py](models.py), [config.py](config.py) | Define the regression network, target, feature list, default paths and split settings |
| [inference.py](inference.py) | Loads the artifact bundle and predicts current peak rust for one image |
| [api.py](api.py) | Exposes `/health` and `/predict/current` through FastAPI |
| [visualize.py](visualize.py), [report_writer.py](report_writer.py) | Generate figures, grouped metrics and the scientific Markdown report |
| [build_pdf_report.py](build_pdf_report.py) | Builds the historical phase PDF and exports its CSV tables from saved results and the spreadsheet |

The [artifacts directory](artifacts/) contains four linked parts:

- `run_info.json`: selected architecture, dataset summary and recorded file paths.
- `best_model_state.pt`: learned regression-network weights.
- `target_scaler.joblib`: target scaling used with those weights.
- `tabular_preprocessor.joblib`: fitted tabular transformation retained with the run.

Keep the bundle together. The pretrained ResNet-18 encoder is obtained through
torchvision and may require cached weights or a download; it is not stored in
`best_model_state.pt`. The shared [path helper](../research_paths.py) lets inference
locate same-named artifacts in the supplied bundle when old recorded paths no longer exist.

## Reproduction and API limits

Use a separate reproduction copy with the local data and artifact bundle. Read
the [reproduction guide](../docs/reproduction.md) and [requirements](requirements.txt);
the latter lists minimum versions rather than a verified historical environment.

Run package commands from the **parent of the checkout**, with the checkout named
`corrosion`. On the delivery machine, that is `/Users/parastoo/All_projects/Proj_corrosion`:

```bash
python -m corrosion.image_embeddings.train_phase2 --help
```

Removing `--help` starts training and writes outputs. `--reports-dir` alone does
not isolate the run: figure directories still come from `config.py`, and grouped
metrics are written beside those figures. Review all destinations in the separate copy.

The recorded inference blocker is the saved tabular preprocessor's unavailable
scikit-learn `_RemainderColsList` class. **The loader attempts to load it even for
the selected image-only model.** Restore a compatible environment or review a
loader repair separately before expecting the API to work. After resolving that
blocker, the local API entry point is:

```bash
python -m uvicorn corrosion.image_embeddings.api:app --host 127.0.0.1 --port 8100
```

The existing PDF builder also contains invalid `main_first` aggregation names
and requires `reportlab`, which is absent from this phase's requirements.
Some plot labels contain the same historical text corruption. These issues must
be reviewed before regenerating reports; the existing reports remain preserved.

For wider context, see the [project overview](../README.md),
[experiment map](../docs/experiments.md), [folder migration guide](../docs/folder_migration.md)
and [original development records](../archive/agent_working_notes/main_2/).

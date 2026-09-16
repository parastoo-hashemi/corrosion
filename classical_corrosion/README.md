# Classical corrosion models — historical baseline

This phase uses specimen metadata and handcrafted image descriptors to estimate
surface corrosion. It develops three regression tasks on the historical
**792 records / 48 specimens / weeks 0–36** dataset. Formerly `main/`, it follows
the [exploratory prototype](../exploratory_prototype/README.md) and precedes the
[image-embedding comparison](../image_embeddings/README.md).

**Status:** saved benchmark tables and fitted models are available. A full
training rerun has not been verified. The threshold task concerns surface rust;
it does not validate structural failure time or remaining useful life.

## Three tasks and their saved results

Results below are rounded from the [manifest](artifacts/manifest.json) and matching
metric tables. MAE is mean absolute error; lower is better.

| Task | Inputs → output | Selected model | Holdout MAE | Holdout R² |
|---|---|---|---:|---:|
| [Current corrosion](reports/current_corrosion_metrics.csv) | Metadata + week + 18 image descriptors → current peak rust percentage | RandomForest | 2.3794 percentage points | 0.8996 |
| [Progression](reports/progression_metrics.csv) | Metadata + requested week → peak rust percentage | GradientBoosting | 6.7144 percentage points | 0.5170 |
| [Time to threshold](reports/time_to_threshold_metrics.csv) | Metadata + current week + current peak rust → weeks until first observed 20% crossing | RandomForest | 2.2114 weeks | 0.7820 |

Metadata includes mesh count, treatment, chloride concentration, ageing days,
failure-surface cover and series. The manifest lists exact feature names and the
recorded threshold/seed. The progression model evaluates a requested week using
these inputs; it is not a fitted physical degradation law.

The metric files contain grouped cross-validation summaries and holdout scores
for all candidates. Keep these evaluations separate from predictions made by the
saved models: the selected models were subsequently refitted on all eligible rows.

## Where to inspect the evidence

- [artifacts/](artifacts/): `manifest.json` and three fitted pipelines:
  `current_corrosion_model.joblib`, `progression_model.joblib`, and
  `time_to_threshold_model.joblib`. Keep all four files together; the inference
  loader loads the three pipelines as one bundle.
- [reports/](reports/): the three metric tables, the corresponding
  `*_feature_importance.csv` tables, and [cached image features](reports/image_features_cache.csv).
  Feature importance describes the refitted estimator, not causal effects.
  This folder has no saved row-level holdout predictions or split manifest.
- [scientific_solution.txt](scientific_solution.txt) and [1_main.pdf](1_main.pdf):
  historical narrative. Claims about validation or deployment describe that earlier
  record; use the limitations here when interpreting it.
- [Archived development notes](../archive/agent_working_notes/main/): earlier guidance.
  The current handoff manuscripts are the [final article and thesis](../final_reports/README.md).

Old absolute paths remain in the manifest for provenance. Inference uses the
shared [path helper](../research_paths.py) to find same-named models in the supplied
bundle when those recorded locations no longer exist.

## Scientific limits

- Splits group repeated observations by specimen, with grouped cross-validation
  inside the training subset. However, model selection ranks candidates by
  **holdout MAE**. The winning holdout score is therefore not an untouched final test.
- The threshold dataset keeps only specimens that reached 20% peak rust and only
  observations through their first recorded crossing. Non-crossing specimens are
  excluded, rather than treated as censored observations. The score cannot describe
  all specimens or structural lifetime.
- The saved threshold model was trained for **20%**. Changing the API's
  `threshold_pct` argument does not retrain that model for another threshold.
- Current corrosion features and the target both describe visible surface rust.
  Strong agreement does not establish hidden-damage prediction. Campaign factors
  are confounded, and availability of failure-surface cover before testing is unverified.
- The corrupted image `E01-20240508-17W` remains in this generation. The current
  feature builder imputes missing values using dataset-wide medians before the
  grouped evaluation; review this preprocessing when designing a new experiment.

## Source and execution

| File | Purpose |
|---|---|
| [train_models.py](train_models.py) | Runs all three tasks and writes models, metrics, importance tables, image cache and manifest |
| [data_utils.py](data_utils.py), [image_features.py](image_features.py) | Parse the historical workbook and extract image descriptors |
| [modeling.py](modeling.py) | Preprocessing, candidate estimators, grouped evaluation, selection and full-data refitting |
| [inference.py](inference.py) | Load saved pipelines; predict current rust, a progression curve or threshold time |
| [api.py](api.py) | FastAPI endpoints: `/health`, `/predict/current`, `/predict/progression`, `/predict/time-to-threshold` |

Read [known issues](../docs/known_issues.md), [reproduction guidance](../docs/reproduction.md)
and [requirements](requirements.txt) first. Requirements are minimum versions, not
a verified historical lockfile. Saved model-loading checks do not establish a
new training run's correctness.

Commands use the **parent of the checkout**, with its package directory named
`corrosion`. On the delivery machine this is `/Users/parastoo/All_projects/Proj_corrosion`.
Inspect the training interface with:

```bash
python -m corrosion.classical_corrosion.train_models --help
```

For a deliberate training attempt in a separate reproduction copy, use new output
directories. These paths are relative to the command's working directory:

```bash
python -m corrosion.classical_corrosion.train_models --artifacts-dir reproduction_run/classical/artifacts --reports-dir reproduction_run/classical/reports
```

For local inference after checking environment/model compatibility:

```bash
python -m uvicorn corrosion.classical_corrosion.api:app --host 127.0.0.1 --port 8000
```

The API loads this phase's default `artifacts/` bundle. Inspect the `/health` response
body for loading errors and use `/docs` for request fields. Starting the API does
not train models. No service or training run is needed to read the saved results.

Return to the [experiment map](../docs/experiments.md) or [project overview](../README.md).

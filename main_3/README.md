# `main_3`: Corrosion Degradation and Proxy-RUL Pipeline

`main_3` is the final implementation for the ferrocement corrosion project. It reconstructs the dataset, extracts classical corrosion features from images, models surface corrosion and hidden damage, fits specimen degradation curves, and estimates proxy Remaining Useful Life (RUL) from engineering limit states.

## Scientific scope

The dataset supports:

- surface corrosion supervision for all 792 image records
- hidden damage supervision for 48 late-stage records only
- degradation modelling from repeated specimen time series
- proxy-RUL estimation from threshold crossing

The dataset does **not** support direct supervised image-to-RUL learning because it does not contain true failure times.

## Project layout

```text
main_3/
  configs/
  src/
  scripts/
  notebooks/
  reports/
  outputs/
  tests/
  logs/
```

## Environment

Install dependencies:

```bash
pip install -r main_3/requirements.txt
```

## Run order

From the repository root:

```bash
python main_3/scripts/01_inspect_dataset.py
python main_3/scripts/02_build_metadata.py
python main_3/scripts/03_preprocess_images.py
python main_3/scripts/04_extract_features.py
python main_3/scripts/05_train_corrosion_models.py
python main_3/scripts/06_train_damage_models.py
python main_3/scripts/07_fit_degradation_models.py
python main_3/scripts/08_estimate_rul.py
python main_3/scripts/09_generate_reports.py
```

Or run everything in order:

```bash
python main_3/scripts/run_all.py
```

## Main outputs

- `main_3/outputs/canonical_dataset.csv`
- `main_3/outputs/canonical_dataset.parquet`
- `main_3/outputs/image_features.parquet`
- `main_3/outputs/corrosion_state_estimates.parquet`
- `main_3/outputs/damage_state_estimates.parquet`
- `main_3/outputs/degradation_curves.parquet`
- `main_3/outputs/degradation_forecasts.parquet`
- `main_3/outputs/rul_estimates.csv`
- `main_3/reports/pipeline_summary.md`
- `main_3/reports/code_audit.md`
- `main_3/reports/rul_feasibility_assessment.md`

## Key assumptions

- `Last_Wire_Area_Loss_(Faliure_Surface)_%` is treated as a fractional quantity and multiplied by 100 because the recorded values top out at `0.5698`, while the engineering thresholds are defined at 20%, 25%, and 30%.
- Ultimate-load thresholding is proxy-based and normalized by the best observed load within each campaign.
- Failure probability is a proxy score, not a calibrated reliability probability, because the dataset does not contain true failure events.

## Reproducibility

- deterministic seeds are set in configuration
- all paths are resolved from `main_3/configs/default.toml`
- grouped evaluation avoids specimen leakage across train and test

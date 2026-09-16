# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a ferrocement corrosion research project that predicts structural hidden damage and remaining useful life (RUL) from time-series surface images of corroding specimens. The repo contains four generations of the pipeline (`main`, `main_2`, `main_3`, `main_4`). **`main_4` is the current and canonical implementation.** `main_4/CODEBASE_GUIDE.md` is the authoritative reference for the architecture.

The primary research question in `main_4` (post-refocus): does superficial corrosion add predictive value for terminal ultimate load, after controlling for specimen design?

## Environment

The project uses a conda environment named `env`:

```bash
/opt/anaconda3/bin/conda run -n env python <script>
```

Install dependencies (per generation):

```bash
pip install -r main_4/requirements.txt   # or main_3/requirements.txt, etc.
```

## Running Scripts (main_4)

All scripts are run from the repository root with `main_4/` as working context, using `sys.path.insert(0, "src")` or conda run:

```bash
# Primary workflow (terminal ultimate-load refocus)
/opt/anaconda3/bin/conda run -n env python run_ultimate_load_refocus.py   # from main_4/

# Full pipeline in order
python run_audit_validation.py
python run_eda.py
python run_extract_image_features.py
python train_surface_models.py
python train_hidden_damage_models.py
python train_degradation_models.py
python train_rul_proxy_models.py
python run_diagnostics_visualizations.py
python run_model_improvement_analysis.py

# Or orchestrate everything
python run_full_baseline.py
```

## Running Tests

Tests live in `main_3/tests/` (no dedicated test suite in main_4):

```bash
# Run all tests
python -m pytest main_3/tests/

# Run a single test file
python -m pytest main_3/tests/test_data_parsing.py -v
```

## main_4 Architecture

The `main_4/src/corrosion_proxy_rul/` package contains all core logic. Entry scripts in `main_4/` call into this package.

**Data flow:**
1. `data_loading.py` — reads `Data/Images_Dataset_A-Z-1.xlsx` and scans `Data/Images_dataset/`
2. `schema_validation.py` + `specimen_mapping.py` + `data_cleaning.py` — builds `outputs/data/master_table.csv` (791 aligned rows, 48 specimens)
3. `image_features.py` — extracts deterministic interpretable features (rust masks, histograms, texture, morphology) → `outputs/features/image_features.csv`
4. `feature_engineering.py` — merges metadata + image features, enforces modelling exclusions → `outputs/data/full_feature_table.csv`
5. `splits.py` — grouped splits always keyed on `specimen_id` (GroupShuffleSplit, LOTO, LOCO)
6. `models_surface.py` / `models_hidden_damage.py` — trains four regressor families with feature-set ablations
7. `models_degradation.py` — fits specimen-level trajectory curves from hidden-damage predictions
8. `models_rul_proxy.py` — computes threshold-crossing time (proxy-RUL)
9. `diagnostics.py` / `reporting.py` — generates figures and markdown summaries

**Config files** (`main_4/configs/`): all YAML, loaded via `config.py` with `@lru_cache`. Key files: `dataset.yaml` (paths and targets), `features.yaml` (image feature extraction params), `modeling.yaml` (seeds, split settings, hyperparameters), `specimen_mapping.yaml` (ground-truth treatment/campaign labels — use this, not workbook columns), `thresholds.yaml` (proxy-RUL thresholds), `ultimate_load_refocus.yaml`.

**Output directory:** `main_4/outputs/` — subfolders: `audit/`, `data/`, `features/`, `eda/`, `splits/`, `models/`, `diagnostics/`, `improvements/`, `logs/`.

## Legacy Generations

| Folder | Description |
|--------|-------------|
| `main_first/` | Original exploratory scripts (Random Forest baseline, data visualization) |
| `main/` | Phase 1: classical ML with FastAPI inference endpoint (port 8000) |
| `main_2/` | Phase 2: deep image embeddings + tabular context, FastAPI (port 8100) |
| `main_3/` | Phase 3: full structured pipeline with tests, numbered scripts in `scripts/`, parquet outputs |

## Hard Scientific Constraints

These must not be violated in any code changes:

- **Direct supervised image→RUL prediction is invalid** for this dataset (no true failure times, only 48 structural-label rows — one per specimen at terminal stage).
- All splits must be grouped by `specimen_id`; no split may place observations from the same specimen in both train and test.
- `Last_Wire_Area_Loss_(Faliure_Surface)_%` is stored as a fraction in `[0,1]` despite the `%` suffix — multiply by 100 to get percent.
- `Treatment`/`Label_Treatment` columns in the workbook are insufficient; always reconstruct treatment groups from `configs/specimen_mapping.yaml`.
- `n_steel_mesh` is strongly correlated with `ultimate_load_kn`; do not interpret pooled corrosion-vs-load relationships without stratifying by mesh family.

## Key Data Facts

- Workbook: `Data/Images_Dataset_A-Z-1.xlsx` (792 image files, 791 aligned usable rows after excluding one corrupted orphan: `E01-20240508-17W.png`)
- 48 unique specimens, each with a time series of images (0W–36W)
- Surface corrosion labels: all 791 rows; structural labels (`wire_area_loss_frac`, `ultimate_load_kn`): only the 48 terminal-stage rows

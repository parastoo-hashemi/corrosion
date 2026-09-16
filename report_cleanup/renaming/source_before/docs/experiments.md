# Experiments and saved outputs

All paths below are relative to the repository root unless a working directory is
stated. **These historical training commands identify entry points; they have not
been certified runnable in the present source state.** Read
[known issues](known_issues.md) before attempting a new run. Training can overwrite
saved results. Use a separate copy for repairs or reproduction.

## Historical phase map

| Phase | Question / procedure | Saved outputs |
|---|---|---|
| Exploratory `main_first` | Handcrafted features, random forests, simulation | [main_first/ressult/](../main_first/ressult/); exploratory artifacts, no comparable held-out metrics |
| Classical `main` | Current peak corrosion, progression, threshold time | [main/reports/](../main/reports/) for metrics and [main/artifacts/](../main/artifacts/) for models/manifests |
| Embeddings `main_2` | Frozen ResNet-18 features plus tabular context | [main_2/reports/](../main_2/reports/) for predictions/figures and [artifacts/](../main_2/artifacts/) for fitted objects |
| Interpretable `main_3` | Surface regression/classification, structural feasibility, first degradation/proxy-RUL pipeline | [main_3/outputs/](../main_3/outputs/) for CSV/parquet/models and [reports/](../main_3/reports/) for generation-specific results |
| Robustness `main_4` | Grouped, treatment-holdout, and campaign-holdout structural benchmarks | [main_4/outputs/models/](../main_4/outputs/models/), [diagnostics/](../main_4/outputs/diagnostics/), [improvements/](../main_4/outputs/improvements/) |
| Refocus `main_4` | Terminal load: metadata versus RGB/HSV, grouped CV, mesh analyses, post-onset sensitivity, residual refinement | [ultimate_load_refocus/](../main_4/outputs/ultimate_load_refocus/) |
| Classification preparation | Offline augmentation and fixed specimen partitions | [Data/splits/](../Data/splits/), [augmentation tables](../augmentation/tables/), [figures](../augmentation/figures/) |

`main_4_old` is a retained baseline snapshot, not a second current experiment.
`emiling` holds historical export copies, not the canonical result store.

## Main structural results: where to start

Under [main_4/outputs/ultimate_load_refocus/](../main_4/outputs/ultimate_load_refocus/):

- `comparisons/final_leaderboard.csv`: comparison across saved settings.
- `pooled_all_weeks/grouped_cv/feature_set_comparison.csv`: grouped feature-family comparisons.
- `pooled_all_weeks/grouped_cv/experiments/metadata_only/Ridge/`: fold metrics,
  terminal fold/OOF predictions, full-fit coefficients, learning-curve data and diagnostics.
- `splits/`: specimen and row memberships, plus balance summaries.
- `mesh_stratified/`, `correlations/`: within-mesh context for pooled associations.
- `pooled_post_onset/`: selected post-visible-corrosion sensitivity.
- `residual_refinement/`, `error_audit/`: specimen-level error and refinement analyses.

The pooled metadata Ridge benchmark averages fold MAEs. A parity plot using mean
OOF predictions has a different aggregation. Do not interchange those values.
Full-fit coefficient magnitudes describe a fitted association and are not causal
or out-of-fold feature importance. Learning-curve subset sizes change composition
as well as sample count. See the manuscript for the scientific interpretation.

The earlier robustness-selected wire-loss and load models are distinct from the
later focused Ridge model. Do not combine their metrics into one headline.

## Historical entry commands

First and second generations import the `corrosion` package, so use the parent of
this checkout and keep the directory name `corrosion`:

```bash
cd ..
python -m corrosion.main.train_models --help
python -m corrosion.main_2.train_phase2 --help
```

These commands may fail on current source/dependencies before showing help; that
is an existing execution limitation, not a verified installation procedure.

For `main_3`, from the repository root the intended sequence is:

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

For the mature structural generation the working directory is **`main_4/`**, since
entry scripts add relative `src` to Python's import path:

```bash
cd main_4
python run_audit_validation.py
python run_eda.py
python run_extract_image_features.py
python train_surface_models.py
python train_hidden_damage_models.py
python train_degradation_models.py
python train_rul_proxy_models.py
python run_diagnostics_visualizations.py
python run_model_improvement_analysis.py
```

The refocused workflow uses the saved master table and configs, and has a separate
entry point from this same directory:

```bash
python run_ultimate_load_refocus.py
```

These sequences are historical execution maps. They include training, use the
currently defective source/configs, and were **not executed during cleanup**.
The original saved results remain the basis for the reports.

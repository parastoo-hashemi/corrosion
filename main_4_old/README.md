# Corrosion Proxy-RUL Baseline

This repository implements a leakage-safe, scientifically conservative baseline for:

surface corrosion progression -> hidden damage estimation -> degradation modelling -> exploratory threshold-status analysis (proxy-RUL).

Important interpretation notes:

- the `surface_total_rust_pct` benchmark is a label-reconstruction sanity check, not a standalone predictive success claim
- the threshold stage is exploratory threshold-status analysis, not validated forward RUL

## Reproduction

Use the existing conda environment and run:

- `conda run -n env python train_hidden_damage_models.py`
- `conda run -n env python train_degradation_models.py`
- `conda run -n env python train_rul_proxy_models.py`
- `conda run -n env python run_diagnostics_visualizations.py`
- `conda run -n env python run_model_improvement_analysis.py`

All generated artifacts are saved under `outputs/`.

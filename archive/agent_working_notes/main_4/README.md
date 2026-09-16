# Terminal Ultimate-Load Refocus

This repository now includes a leakage-safe, scientifically conservative workflow centered on:

`ultimate_load_kn` estimation from specimen metadata and image-derived superficial-corrosion descriptors.

Primary research question:

> After controlling for specimen design, does superficial corrosion add predictive value for terminal ultimate load?

Important interpretation notes:

- `ultimate_load_kn` is the primary target.
- `wire_area_loss_frac` is secondary and supporting only.
- Visible surface corrosion is not the same as hidden/internal corrosion.
- The project should not be presented as true RUL or full-life prediction.
- Because `n_steel_mesh` is strongly related to `ultimate_load_kn`, pooled raw corrosion-versus-load relationships should not be interpreted without accounting for mesh family.
- In this dataset, `n_steel_mesh` and `campaign_id` are aligned, so pooled leave-one-campaign-out is a stress test, not the main scientific conclusion.

## Main Workflow

Use the existing conda environment and run:

- `/opt/anaconda3/bin/conda run -n env python run_ultimate_load_refocus.py`

New outputs are written under:

- `outputs/ultimate_load_refocus/`

Key deliverables include:

- grouped specimen-level split manifests and balance summaries
- RGB versus HSV feature-family comparisons
- mesh-stratified corrosion-versus-load analyses
- pooled grouped-CV and leave-one-campaign-out model comparisons
- post-onset sensitivity analysis
- specimen-level out-of-fold terminal predictions
- a best-model diagnostic package with learning curves, residuals, feature importance, partial dependence, and uncertainty visualizations

## Legacy Context

The older hidden-damage, degradation, and proxy-RUL scripts remain in the repository for traceability, but they are not the preferred front-door workflow for the refocused terminal-load objective.

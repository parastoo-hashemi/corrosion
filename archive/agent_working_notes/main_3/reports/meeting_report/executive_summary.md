# Meeting Executive Summary

Prepared from existing artifacts only:

- `main_2/reports/*`
- `main_3/src/*`
- `main_3/outputs/*`
- `main_3/reports/*`
- `main_3/reports/figures/*`

No models were retrained for this report.

## Main message

`main_2` implemented a specimen-grouped deep baseline for predicting **peak surface corrosion** from images. `main_3` turns the project into a broader engineering pipeline: it reconstructs a canonical time-series dataset, extracts interpretable corrosion features from images, estimates hidden damage, fits specimen-level degradation curves, and converts those curves into **proxy Remaining Useful Life (proxy-RUL)** through engineering thresholds.

## Headline findings

- The dataset contains **792 image records**, **48 specimens**, **2 campaigns**, and **25 observed week values** from **0 to 36 weeks**.
- Surface corrosion labels are available for **all 792 rows**, but structural labels exist for only **48 rows (6.06%)**, all at **weeks 28 and 36**.
- `main_2` best baseline on the shared task (`peak_rust_pct`) was `image_only_mlp` with **MAE 5.63**, **RMSE 9.26**, **R2 0.524**.
- `main_3` improved the same grouped peak-corrosion task to **MAE 4.21**, **RMSE 6.23**, **R2 0.784** using hand-crafted image features plus classical models.
- `main_3` also added a new surface-corrosion task: `surface_total_rust_pct` reached **MAE 1.38** and **R2 0.646** with a random forest.
- Hidden-damage estimation is feasible but modest: `wire_area_loss_pct` reached **MAE 3.90**, **R2 0.310** and `ultimate_load_kn` reached **MAE 0.121 kN**, **R2 0.385** under specimen-grouped split.
- Degradation fitting produced **192 specimen-target curve fits**. Most selected models were **piecewise linear**, which is useful for trend extrapolation but also exposes a methodological limitation.
- Proxy-RUL results are screening-oriented, not failure-time prediction: **20 Low**, **8 Moderate**, **20 High**, **0 Critical** risk specimens, with **median estimated proxy-RUL = 0 weeks** and **23/48 specimens already at a proxy limit state** at the latest observation.

## What was built

| Stage | `main_2` | `main_3` |
|---|---|---|
| Dataset handling | Parse spreadsheet IDs and images for one regression task | Build canonical dataset with campaigns, treatments, weeks, structural-label flags, and integrity checks |
| Image representation | 512-d ResNet-18 embedding | Classical corrosion segmentation + 91 interpretable image features |
| Surface corrosion modeling | Peak-rust regression only | Surface and peak regression plus category classification |
| Hidden damage | Not modeled | Wire area loss and ultimate load regression |
| Time/degradation modeling | Not modeled | Per-specimen curve fitting on corrosion and damage states |
| Remaining life | Not available | Threshold-based proxy-RUL and risk classes |

## Why `main_3` matters scientifically

- It improves performance on the shared peak-corrosion regression task by about **25% lower MAE** relative to `main_2` under grouped evaluation.
- It moves the project from pure image-to-corrosion prediction toward an **engineering interpretation pipeline**: visible corrosion -> inferred hidden damage -> degradation curve -> proxy-RUL.
- It makes the pipeline more interpretable. The strongest learned signals are no longer opaque embeddings only; they include saturation/color histograms, texture, rust-component geometry, spatial peak location, and known specimen metadata.

## What the results do and do not support

Supported by the artifacts:

- Surface corrosion can be quantified reasonably well from images.
- Corrosion progression over time is visible across repeated specimen observations.
- A threshold-based proxy-RUL workflow is feasible with the available data.

Not supported by the artifacts:

- Direct supervised image-to-RUL prediction.
- Strong claims about internal-damage accuracy on unseen treatments or unseen campaigns.
- Treating the reported RUL values as true failure-time estimates.

## Most important caution

The project produces **proxy-RUL**, not true RUL. The dataset does not contain failure times. The reported `estimated_rul_weeks` is the time from the latest observed state to the first forecasted crossing of:

- wire-loss 25%
- campaign-specific load threshold (`0.8 x` reference load)
- health-index threshold (`< 0.35`)

## Recommended meeting takeaway

The strongest, most defensible claim is:

> `main_3` successfully converts dense image-based corrosion observations into an interpretable condition-assessment pipeline, and it demonstrates a feasible path to proxy-RUL estimation, while also revealing that hidden-damage inference is the current bottleneck because structural supervision is sparse and late-stage only.

![Dataset Overview](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/meeting_report/figures/dataset_overview.png)

![Risk Distribution](/Users/parastoo/All_projects/Proj_corrosion/main_3/reports/figures/risk_distribution.png)

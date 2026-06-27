# `main_2` vs `main_3`

## 1. High-level comparison

| Dimension | `main_2` baseline | `main_3` improved pipeline | Why `main_3` is an improvement |
|---|---|---|---|
| Objective | Predict current peak corrosion from image inputs | Build a full corrosion-to-proxy-RUL pipeline | Expands from a single regression task to condition assessment |
| Data representation | Spreadsheet rows + image paths for one task | Canonical dataset with campaigns, weeks, specimen IDs, structural-label flags, and integrity checks | Better reproducibility and cleaner scientific framing |
| Image representation | Pretrained ResNet-18 embeddings | Interpretable corrosion features from preprocessing, rust scoring, texture, color, and spatial segmentation | More explainable and easier to tie to corrosion physics |
| Surface targets | `peak_rust_pct` only | `surface_total_rust_pct`, `peak_rust_pct`, and both categorical versions | Covers more of the available corrosion supervision |
| Hidden damage | Not modeled | `wire_area_loss_pct`, `ultimate_load_kn` | Connects visible corrosion to structural proxies |
| Temporal modeling | Not modeled | Specimen-wise degradation curves | Uses the repeated measurements properly |
| Remaining life | None | Threshold-based proxy-RUL | Adds engineering decision support |
| Outputs | Model comparison, predictions, diagnostics, PDF report | Canonical dataset, feature table, state estimates, degradation curves, RUL tables, figures, reports | Much richer scientific output |
| Main limitation | Only current peak-corrosion regression | Hidden-damage supervision still sparse | `main_3` solves more, but also exposes the true data bottleneck |
| Scientific value | Strong proof of concept for image-based corrosion prediction | Coherent bridge from image condition to engineering proxy-RUL | Better aligned with academic research goals |

## 2. Quantitative comparison on the shared task

Both pipelines were evaluated with grouped specimen holdout on `peak_rust_pct`.

| Pipeline | Best model | MAE | RMSE | R2 |
|---|---|---:|---:|---:|
| `main_2` | `image_only_mlp` | 5.6255 | 9.2639 | 0.5237 |
| `main_3` | `mlp_regressor` on image features | 4.2087 | 6.2338 | 0.7843 |

Direct interpretation:

- `main_3` reduces MAE by about **25.2%**
- `main_3` improves explained variance substantially
- the improvement happens without relying on opaque deep embeddings as the only image representation

## 3. What `main_2` taught us

The baseline established four important facts:

1. Corrosion signal is present in the images.
2. Grouped splitting by specimen is necessary.
3. Deep embeddings alone already give workable peak-corrosion prediction.
4. Simply adding tabular context does not automatically improve performance.

Those findings were useful because they justified moving to a more structured and interpretable pipeline.

## 4. What `main_3` adds beyond better numbers

`main_3` is not just "the same task with a better model." It changes the research contribution.

New capabilities:

- canonical dataset construction
- explicit image preprocessing and corrosion localization
- engineered corrosion descriptors with physical interpretation
- hidden-damage estimation
- degradation curve fitting
- limit-state-based proxy-RUL and risk classes

This matters academically because it turns the work from a generic ML exercise into an engineering workflow.

## 5. Where `main_3` is still limited

`main_3` is clearly better than `main_2`, but the improvement is uneven across stages.

Strongest part:

- surface corrosion modeling

Weakest part:

- hidden-damage inference and anything downstream that depends on it

Why:

- 792 rows are available for surface corrosion
- only 48 rows are available for structural supervision

So the correct framing is:

> `main_3` is a strong improvement in system scope and corrosion-state modeling, while hidden-damage and proxy-RUL remain promising but preliminary because the structural label regime is still sparse.

## 6. Best way to explain the difference in the meeting

Use this short explanation:

> `main_2` asked whether a model can read current peak corrosion from an image. `main_3` asks whether the full experimental record can be turned into a condition-assessment pipeline that estimates visible corrosion, infers hidden damage, fits degradation over time, and outputs a threshold-based proxy-RUL. The answer is yes for corrosion and partly yes for hidden damage and proxy-RUL, with clear evidence that structural supervision is now the main research bottleneck.

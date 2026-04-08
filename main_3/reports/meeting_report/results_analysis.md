# Results Analysis

This file focuses on interpretation rather than implementation detail.

## 1. What the outputs really support

| Claim | Evidence from saved outputs | Confidence |
|---|---|---|
| Image features can quantify surface corrosion severity | `main_3` reaches `MAE 1.38 / R2 0.646` on `surface_total_rust_pct` and `MAE 4.21 / R2 0.784` on `peak_rust_pct` with grouped specimen holdout | High |
| `main_3` improves over the `main_2` baseline on the shared peak-rust task | `main_2` peak-rust baseline: `MAE 5.63 / R2 0.524`; `main_3`: `MAE 4.21 / R2 0.784` | High |
| Corrosion progression is visible over time | Cross-sectional mean `peak_rust_pct` rises from `0.42%` at week 0 to `29.26%` at week 28; mean last-minus-first specimen delta is `+24.99` | High |
| Extreme low/high corrosion states are easier to classify than middle states | Surface category class-1 F1 `0.932`, class-5 F1 `0.825`, but class-3 F1 `0.222` and class-4 F1 `0.316` | High |
| Visible corrosion alone is a weak direct proxy for hidden wire loss | Correlation of `peak_rust_pct` with `wire_area_loss_pct` is only `0.011` overall on structural rows | High |
| Hidden damage contains some learnable signal but remains uncertain | Damage models achieve only `R2 0.31` and `R2 0.385` under grouped split, then become negative under leave-one-treatment and leave-one-campaign evaluation | Medium |
| Degradation fitting is useful descriptively, but not yet mechanistic | Almost all fits are piecewise linear; some forecasts flatten or evolve unrealistically | Medium |
| Proxy-RUL is useful for condition screening, not for exact failure-time prediction | Dataset has no failure times; RUL is threshold crossing of forecasted states | High |

## 2. Strongest scientific result

The strongest result is not the RUL number by itself. The strongest result is that the project now has a coherent path:

`images -> interpretable corrosion features -> corrosion state -> hidden damage estimate -> degradation forecast -> proxy-RUL`

That chain is scientifically valuable because it matches the information actually present in the dataset.

Why this matters:

- the dataset is rich in repeated image observations
- the dataset is poor in direct failure annotations
- `main_3` respects that reality instead of pretending the project can already do end-to-end supervised RUL

## 3. What improved from `main_2` to `main_3`

`main_2` proved that peak corrosion can be learned from images. `main_3` improves the shared task and makes the output more interpretable.

The critical upgrade is not just the lower MAE. It is the change in scientific framing:

- `main_2` answer:
  - "Can we regress current peak corrosion from an image?"
- `main_3` answer:
  - "Can we build a condition-assessment workflow that starts from images and ends in an engineering proxy for remaining life?"

That is a meaningful research step.

## 4. What the corrosion results imply

The corrosion models are good enough to support several claims:

- corrosion severity leaves reproducible visual signatures
- handcrafted color and texture descriptors are sufficient to learn those signatures
- grouped splitting by specimen still leaves substantial predictive power, so the model is not just memorizing weekly frames of the same specimen

What the corrosion results do not imply:

- perfect calibration of raw segmentation features
- strong robustness to unseen treatment regimes

Important nuance:

- the best models do not simply read "rust area percent" from the image
- the strongest signals are color saturation bins, blue-channel suppression, texture variability, and spatial concentration patterns

This is why direct proxy-vs-label correlations are weak while multivariate model performance is much better.

## 5. Why the hidden-damage result is both promising and limited

The damage stage is promising because:

- it extracts non-trivial signal from only image-derived state plus metadata
- the grouped-split R2 values are positive
- wire loss and ultimate load can be forecasted and used downstream

The same stage is limited because:

- there are only 48 structural labels
- those labels occur only at late stages
- generalization collapses under stricter holdouts
- the load model relies heavily on campaign identity and specimen metadata

The academically honest interpretation is:

> The hidden-damage models are useful as latent-state estimators for a prototype pipeline, but they are not yet strong enough to claim robust structural-damage prediction across new conditions.

## 6. What the degradation outputs imply

The degradation outputs tell a coherent but limited story.

Supported:

- specimen trajectories can be fit with low historical error
- corrosion tends to grow across repeated observations
- the fitted curves give a practical bridge from current state to threshold crossing

Not yet supported:

- a physically grounded law of degradation
- guaranteed monotonic capacity loss
- extrapolation far beyond the observed horizon

The dominance of piecewise linear fits is revealing:

- it means the pipeline is capturing trend segments rather than discovering a universal corrosion-growth equation
- that is acceptable for a prototype screening model
- it is not enough for a final scientific claim about degradation physics

## 7. What the proxy-RUL outputs mean in engineering terms

Engineering meaning of the saved RUL values:

- `0 weeks`
  - the specimen is already at a chosen proxy threshold at the latest observed week
- `> 0 weeks`
  - the forecast reaches a chosen threshold later within the configured horizon
- missing RUL
  - no crossing was found inside the forecast window

The distribution is striking:

- 23 of 48 specimens already have proxy-RUL equal to zero
- 15 specimens never cross a threshold within the forecast horizon
- no specimen reaches the `Critical` risk band

This means the risk system is acting more like a **triage tool** than a fully graded lifetime model.

That is not a flaw if presented honestly. It is the correct behavior for the present data regime.

## 8. Most important limitations that change interpretation

These are the limitations that materially affect what can be claimed:

- Structural supervision is sparse and late-stage only.
- Direct failure times are absent, so supervised RUL is impossible.
- Damage-model generalization across unseen treatments/campaigns is poor.
- Degradation curves are mostly piecewise linear, not physics-informed.
- One corrupted image was handled by fallback rather than being recoverable from data.

Each of these limitations affects the RUL stage more than the corrosion stage.

## 9. Best one-sentence conclusion for the meeting

`main_3` successfully transforms the project from a single corrosion-regression baseline into an interpretable condition-assessment pipeline, with strong evidence for surface-corrosion modeling and only preliminary evidence for hidden-damage and proxy-RUL estimation.

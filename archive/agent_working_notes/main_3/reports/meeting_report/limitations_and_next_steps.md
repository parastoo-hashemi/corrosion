# Limitations and Next Steps

## 1. Main limitations

| Limitation | Evidence in artifacts | Effect on interpretation |
|---|---|---|
| Sparse structural labels | Only **48** rows with `wire_area_loss_pct` and `ultimate_load_kn` out of **792** total rows | Hidden-damage results are much less reliable than corrosion results |
| Structural labels only at late stages | Structural rows appear only at **weeks 28 and 36** | Damage models do not learn full-lifecycle structural evolution |
| No true failure times | Explicitly documented in `rul_feasibility_assessment.md` | Reported RUL must be called **proxy-RUL**, not true RUL |
| Weak generalization under stricter splits | Damage-model R2 becomes strongly negative under leave-one-treatment and leave-one-campaign evaluation | Hidden-damage models are not yet robust across new domains |
| Mostly piecewise-linear degradation fits | `degradation_curves.parquet` selects piecewise linear for almost all targets | Forecasts are pragmatic extrapolations, not mechanistic degradation laws |
| Health threshold is not the governing state in this run | No specimen is governed primarily by the health-index crossing | Health index is helpful for scoring but not yet central to RUL timing |
| One corrupted image handled by fallback | `E01-20240508-17W` failed feature extraction and was retained through imputation | Results are robust to one bad image, but this is still a data-quality weakness |
| Middle severity classes remain hard | Corrosion classification macro-F1 is only about `0.53-0.57`; class-3 and class-4 F1 values are low | Category predictions are most reliable at the extremes |

## 2. How these limitations affect the current conclusions

- The corrosion-stage conclusions are relatively strong because the label coverage is dense.
- The hidden-damage and RUL-stage conclusions are provisional because they rest on limited structural supervision.
- The RUL outputs are useful for ranking and screening, but not yet for claiming precise remaining service life.
- The degradation curves should be interpreted as empirical trend fits, not as final physical models of corrosion growth.

## 3. Highest-priority next research steps

### Priority 1: collect better structural supervision

- Add more destructive or structural measurements per specimen across multiple weeks, not just late-stage endpoints.
- Increase the number of specimens with measured wire-loss and capacity values.
- Make sure future datasets include repeated structural labels for the same specimens.

Why first:

- This directly addresses the weakest part of the current pipeline.

### Priority 2: validate proxy-RUL experimentally

- Track specimens until actual threshold crossing or failure.
- Compare forecasted crossing times with observed crossing times.
- Calibrate risk classes against real outcomes.

Why second:

- Without validation against actual outcomes, proxy-RUL remains a useful concept but not a validated engineering prediction.

### Priority 3: improve feature extraction and preprocessing

- Reduce over-segmentation on very low-corrosion or artifact-heavy images.
- Add features that better capture crack-like or edge-concentrated corrosion patterns.
- Consider combining the current interpretable features with learned embeddings instead of replacing one with the other.

Why:

- The current direct rust-mask percentages are not well calibrated, even though the multivariate models work.

### Priority 4: impose better degradation constraints

- Use monotonic or physics-informed models for corrosion growth and capacity loss.
- Prevent implausible forecast shapes such as flat or increasing capacity when degradation should dominate.
- Quantify uncertainty bands around fitted curves.

Why:

- Better degradation models would improve both the interpretability and the stability of proxy-RUL.

### Priority 5: strengthen out-of-domain evaluation

- Create evaluation setups by unseen treatment, unseen campaign, and unseen specimen family.
- Use these stricter splits as the main benchmark for future development.

Why:

- Current grouped-specimen results are good, but unseen-treatment robustness is still weak.

## 4. Practical next-step roadmap

If the project continues, the most sensible order is:

1. collect additional structural labels across time
2. re-train and re-evaluate damage models under strict splits
3. replace purely empirical curve fits with constrained degradation models
4. validate proxy-RUL against experimentally observed threshold crossings
5. only then consider stronger claims about predictive maintenance readiness

## 5. Best limitation statement for the meeting

Use this statement:

> The project is already strong on image-based corrosion quantification, but its hidden-damage and proxy-RUL stages are still limited by the fact that structural supervision is sparse, late-stage only, and not tied to true failure times.

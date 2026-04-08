# RUL Feasibility Assessment

## 1. Does the dataset contain true failure times?

No.

The dataset contains:

- 792 image records with full surface corrosion labels
- 48 records with structural labels
- structural measurements only at late exposure stages (`week = 28` and `week = 36`)

It does **not** contain time-to-failure annotations, repeated structural failure observations across the full specimen life, or explicit end-of-life timestamps.

## 2. Proxy-RUL methodology

Because true failure times are unavailable, `main_3` estimates **proxy RUL** as:

`time from the latest observed state to the first forecasted crossing of an engineering limit state`

The pipeline is:

1. reconstruct specimen time series from image IDs and spreadsheet rows
2. quantify surface corrosion from images
3. estimate hidden damage and residual capacity from late-stage structural supervision
4. fit specimen-level degradation curves over time
5. extrapolate to engineering thresholds

### Limit states used

- Wire-loss threshold:
  - 20%
  - 25%
  - 30%

- Ultimate-load threshold:
  - campaign-specific reference load multiplied by `0.8`

- Composite health-index threshold:
  - `health_index < 0.35`

### Reported RUL

The default `estimated_rul_weeks` is the minimum available crossing time among:

- wire-loss at 25%
- ultimate-load threshold
- health-index threshold

If no threshold is crossed within the configured forecast horizon, the script leaves RUL as missing instead of inventing a value.

## 3. Assumptions

- `Last_Wire_Area_Loss_(Faliure_Surface)_%` is interpreted as a fractional loss ratio and scaled by 100, because the observed maximum is `0.5698`, which is only meaningful against the requested 20/25/30 percent thresholds if treated as `56.98%`.
- Surface corrosion curves are fitted specimen by specimen using repeated image observations; hidden-damage and capacity trajectories are inferred from models trained on the 48 structural rows.
- Ultimate-load reference capacity is proxied by the best observed load inside each campaign, not by a pristine destructive baseline test.
- Failure probability is a proxy risk score derived from health, load margin, wire-loss margin, and estimated RUL. It is not a calibrated reliability probability.
- Forecasts are only trusted within the configured finite horizon and are not extrapolated indefinitely.

## Bottom line

Direct supervised RUL prediction is not scientifically supportable with this dataset.

Proxy-RUL estimation through:

- corrosion progression
- hidden-damage estimation
- degradation-curve fitting
- limit-state crossing

is feasible and is the correct formulation for `main_3`.

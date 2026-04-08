# Specimen Gap Refinement Summary

## What was added

- A specimen-level error audit across the best model from each main feature set.
- A leakage-safe two-stage refinement that predicts terminal load from metadata first, then applies a within-mesh residual correction using compact superficial-corrosion summaries.

## Specimen-level gap audit

- Persistent hard specimens (large error across many best-per-feature-set models): `F03, S2SA02, S5VF01, G03, S2SA05`.
- Approach-sensitive specimens (error changes materially by feature set/model): `S3PA02, F05, S2SA07, S3PA04, G02, D03, S4SAVF02, S3PA01`.

## Residual refinement result

- Specimen-summary metadata baseline: `Ridge` with MAE `0.173` kN and Spearman `0.749`.
- Best residual-refinement pipeline: stage-1 `Ridge` plus stage-2 `none` with MAE `0.173` kN and Spearman `0.749`.
- Relative to the specimen-summary metadata baseline, this was `no_meaningful_change` (delta MAE `+0.000` kN; delta Spearman `+0.000`).

## Specimen-level effect of the best refinement

- No specimen-level improvements exceeded the practical change threshold.
- No specimen-level worsenings exceeded the practical change threshold.

## Interpretation

- If a specimen remains hard across the error audit and the residual-refinement stage, that gap is unlikely to be resolved by model swapping alone.
- If a specimen improves only in some approaches, it is better described as model-sensitive than fundamentally unexplained.
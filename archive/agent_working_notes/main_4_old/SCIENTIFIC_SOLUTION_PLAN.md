# Scientific Solution Plan

## Problem Formulation

The correct formulation is:

```text
surface corrosion progression
-> hidden damage estimation
-> degradation modelling
-> time-to-threshold / proxy-RUL
```

The dataset does **not** support:

```text
image -> direct supervised RUL
```

## Why Direct RUL Prediction Is Invalid Here

Direct RUL prediction is scientifically invalid for this dataset because:

1. There is no observed failure-time or RUL label.
2. Structural targets are available only once per specimen, at the final observation.
3. Campaign 1 and Campaign 2 terminate at different ages and under different exposure regimes.
4. `Ultimate_Load_[kN]` is a terminal mechanical response, not a remaining-life label.
5. `Last_Wire_Area_Loss_(Faliure_Surface)_%` is a sparse hidden-damage endpoint, not a lifetime trajectory.
6. The data are longitudinal and specimen-grouped; random image splits would leak trajectory information.

The strongest defensible claim is therefore:

- estimate hidden structural degradation from surface evidence and metadata
- model degradation over time
- compute threshold-based proxy remaining life under explicitly chosen engineering thresholds

## Recommended Modelling Strategy

Use a staged, interpretable pipeline.

### Stage 1: canonical data assembly

Build a master table that reconstructs:

- `campaign_id`
- `series_id`
- `specimen_id`
- `treatment_protocol`
- `time_in_days`
- `time_in_weeks`
- `image_path`
- surface targets
- structural targets
- split-group labels

Do not use workbook `Treatment` alone as the definitive treatment variable. Reconstruct treatment protocol from thesis tables and specimen IDs.

### Stage 2: interpretable image features

Start with interpretable corrosion indicators aligned with the thesis methodology.

Recommended baseline image features:

- rust-mask area ratio using fixed RGB thresholds
- rust intensity summary in rust-colored pixels
- strip-wise corrosion descriptors:
  - max strip rust
  - mean strip rust
  - standard deviation across strips
  - number of high-rust strips
  - center-vs-edge corrosion ratio
  - peak-strip location
- morphology descriptors:
  - connected rust component count
  - maximum rust blob area
  - average blob area
  - blob elongation / compactness
- simple texture descriptors on the rust mask or the full cropped area:
  - grayscale entropy
  - local binary pattern summary
  - GLCM contrast / homogeneity

Important constraint:

- the workbook surface corrosion columns may be used as supervision and QA targets for this image-feature stage
- they should not be treated as freely available deployment inputs unless the same image-analysis procedure is reproduced in code

### Stage 3: surface-corrosion modelling

Model dense surface targets first.

Primary targets:

- `A_Surface_Total_Rust_Percentage[%]`
- `B_Peak_Rust_Percentage_[%]`

Secondary targets:

- `A_Total_Rust_Category_(1–4)`
- `B_Peak_Rust_Category_(1–4)`
- `B_Location_of_Peak_Rus_ in_length_[cm]`

Purpose:

- validate that engineered image features capture the corrosion information already encoded in the workbook
- create deployable surface estimators from images + metadata

### Stage 4: hidden damage estimation

Hidden damage should be treated as a sparse regression problem on terminal rows only.

Primary hidden-damage target:

- `Last_Wire_Area_Loss_(Faliure_Surface)_%`

Recommended inputs:

- specimen covariates:
  - campaign
  - reconstructed treatment protocol
  - steel mesh count
  - cover
- image-engineered features from the terminal image
- optionally predicted or rederived surface metrics from Stage 3

Critical rule:

- do not mix non-terminal rows into training for this target
- hidden-damage training rows must be the `48` terminal structural-label rows only

### Stage 5: structural-capacity modelling

Model `Ultimate_Load_[kN]` separately after hidden damage.

Recommended inputs:

- predicted hidden damage
- image-derived surface severity features
- cover
- steel mesh count
- campaign / treatment protocol

Scientific reasoning:

- ultimate load is influenced by internal corrosion, cover, reinforcement ratio, and campaign conditions
- a direct image-to-load mapping is weaker and less interpretable than a staged mapping through hidden damage

### Stage 6: degradation modelling

Build a latent degradation state over time for each specimen.

Recommended baseline approach:

1. smooth the surface trajectory per specimen
2. convert each time point into a hidden-damage proxy using the Stage 4 model
3. fit a monotone degradation curve for each specimen or treatment-conditioned subgroup
4. estimate threshold crossing times

Recommended curve families to compare:

- linear in time
- linear in log-time
- monotone spline
- Gompertz / logistic growth curve

Why monotone modelling is needed:

- observed surface series are noisy and non-monotonic
- physical degradation is cumulative even when the measured surface signal fluctuates

### Stage 7: proxy-RUL estimation

Define proxy-RUL as:

```text
proxy_RUL(t) = predicted_time_to_threshold - current_time
```

This requires an explicit threshold definition.

Recommended threshold families:

- hidden-damage thresholds:
  - wire area loss fraction `>= 0.20`
  - wire area loss fraction `>= 0.30`
  - wire area loss fraction `>= 0.40`
- structural-capacity thresholds:
  - predicted ultimate load drop below a chosen fraction of campaign-specific untreated reference

Recommendation:

- report multiple threshold scenarios, not a single absolute number
- label all outputs as `proxy-RUL` or `time-to-threshold`, never as true RUL

## Recommended Baseline

The baseline should remain fully non-neural and interpretable.

### Feature sets to compare

Run three ablation families:

1. metadata only
2. engineered image features only
3. fused metadata + engineered image features

### Candidate models

For every regression stage, compare:

- Random Forest
- Gradient Boosting
- XGBoost
- CatBoost

For ordinal targets, compare classifier variants of the same families when useful, but keep the main emphasis on regression of the continuous corrosion variables.

### Recommended baseline pipeline

1. Reconstruct campaign and treatment protocol from specimen IDs and thesis tables.
2. Remove the orphan unreadable image and lock the aligned dataset size to `791`.
3. Reproduce interpretable image corrosion features from the PNGs.
4. Train grouped surface models for dense corrosion targets.
5. Train hidden-damage models on the `48` terminal structural rows.
6. Train ultimate-load models using hidden-damage estimates plus structural covariates.
7. Build monotone degradation curves from repeated surface measurements.
8. Compute scenario-based proxy-RUL by threshold crossing.

## Recommended Advanced Path

Only pursue this after the baseline is stable and audited.

### Advanced path recommendation

Use a multi-view, weakly supervised approach:

1. keep the interpretable surface-feature pipeline
2. add a learned image embedding from a pretrained vision backbone
3. fuse:
   - learned embedding
   - interpretable corrosion features
   - metadata / treatment / cover / mesh variables
4. predict hidden damage and structural capacity on terminal rows
5. use a hierarchical latent degradation model for time-to-threshold estimation

### Scientifically justified neural usage

If a neural image model is introduced, it should be used for:

- better surface representation learning
- hidden damage estimation support

It should **not** be used first for:

- direct image-to-RUL prediction

Recommended advanced neural options:

- frozen pretrained encoder + tree model / linear head
- self-supervised embedding + CatBoost/XGBoost fusion
- segmentation-assisted encoder that predicts rust maps or strip severity first

Avoid end-to-end direct RUL networks unless a future dataset includes real failure-time supervision.

## Alternative Solution Paths

### Path A: tabular-only sanity baseline

Use workbook-derived surface metrics and specimen metadata only.

Purpose:

- establish the strongest no-image baseline
- measure the marginal value of engineered image features

### Path B: image-feature-first corrosion baseline

Train only the dense surface models first and stop there.

Purpose:

- validate image preprocessing and grouped evaluation before touching sparse structural targets

### Path C: mechanistic / statistical advanced path

Replace or augment Stage 6 with:

- mixed-effects longitudinal models
- Bayesian hierarchical degradation models
- monotone GAMs

This path is scientifically attractive for small longitudinal datasets, especially when uncertainty reporting matters more than raw predictive score.

## Validation Design

The evaluation must be built around grouped splitting.

### Primary split: GroupShuffleSplit

Use:

- `groups = specimen_id`

Reason:

- prevents specimen-level leakage across repeated time points
- supports repeated random grouped holdouts

Recommended usage:

- repeated `GroupShuffleSplit`
- same split manifest reused across model families

### Secondary split: leave-one-treatment-out

Use:

- treatment groups reconstructed from thesis-informed protocol / series, not the lossy workbook `Treatment` field alone

Recommended groups:

- `S1_MI`
- `S2_SA`
- `S3_PA_SA`
- `S4_SA_VF`
- `S5_VF`
- `D_NO`
- `E_SA_SPRAY`
- `F_SA_BRUSH`
- `G_PAINT`

Reason:

- tests generalization to unseen protective strategies
- avoids collapsing spray and brush variants into the same label

### Tertiary split: leave-one-campaign-out

Use:

- train on Campaign 1, test on Campaign 2
- train on Campaign 2, test on Campaign 1

Interpretation:

- this is not a primary model-selection split
- it is an out-of-domain stress test because campaign is confounded with mesh count, NaCl concentration, duration, and treatment design

### Nested rules

For every split:

- fit preprocessing on training data only
- fit feature normalization on training data only
- fit hyperparameter selection inside grouped CV only
- keep all observations from the same specimen in the same fold

### Metrics

Surface regression:

- MAE
- RMSE
- Spearman correlation
- optional R2

Surface ordinal classification:

- balanced accuracy
- macro F1
- weighted Cohen kappa

Hidden damage and ultimate load:

- MAE
- RMSE
- Spearman correlation
- bootstrap confidence intervals

Proxy-RUL:

- no direct supervised accuracy metric is available
- evaluate instead:
  - monotonicity
  - threshold-crossing plausibility
  - uncertainty width
  - ranking consistency with terminal damage severity

## Deployment Recommendation

Deploy this only as a research decision-support tool, not as a direct maintenance oracle.

Recommended deployment shape:

- offline batch pipeline
- specimen-level report generation
- outputs:
  - surface corrosion estimate
  - hidden damage estimate
  - uncertainty interval
  - threshold-based proxy-RUL under named threshold scenarios

Not recommended at this stage:

- real-world autonomous RUL claims
- one-number maintenance decisions
- deployment without campaign/domain checks

Minimum safeguards for any deployment:

- reject unreadable or misaligned images
- reject unseen image dimensions or failed preprocessing
- attach uncertainty and threshold scenario labels to every proxy-RUL output
- flag when the sample is outside observed campaign / treatment / cover ranges

## Final Recommendation

### Recommended baseline pipeline

Interpretable fusion pipeline:

- metadata + thesis-aligned engineered image features
- grouped surface regression
- terminal hidden-damage regression
- structural-capacity regression
- monotone degradation modelling
- threshold-based proxy-RUL

### Recommended advanced pipeline

Multi-view weakly supervised pipeline:

- interpretable corrosion features
- learned image embedding added only after the baseline
- fused hidden-damage estimation
- hierarchical degradation model with uncertainty-aware threshold crossing

This keeps the solution scientifically aligned with the actual supervision that exists in the dataset.

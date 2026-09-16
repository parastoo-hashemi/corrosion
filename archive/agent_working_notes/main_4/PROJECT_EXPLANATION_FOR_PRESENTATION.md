# Project Explanation For Presentation

## 1. The Project In One Sentence

This project builds an interpretable, leakage-safe baseline for corrosion image analysis, with the scientific goal of moving from visible surface corrosion to hidden damage estimation, then to degradation modelling, and finally to an exploratory proxy-RUL view based on threshold crossing.

## 2. What Problem The Project Is Trying To Solve

The long-term research question is:

surface corrosion analysis -> hidden damage estimation -> degradation modelling -> proxy remaining useful life

In simple language:

- We have images of corroding reinforced specimens over time.
- We want to measure what can be seen on the surface.
- We then ask whether those visible patterns tell us anything about hidden structural damage.
- If hidden damage can be estimated over time, we can build a simple time-to-threshold indicator.

This is not the same as true RUL prediction.

## 3. Why Direct RUL Prediction Is Not Valid Here

This is one of the most important points to explain clearly.

- The dataset has 791 usable aligned observations, but only 48 rows have structural labels.
- Those 48 structural rows are terminal rows: one labeled structural observation per specimen.
- There is no dense time-to-failure label for each image.
- There is no direct image-level RUL supervision.

So the project does **not** train "image -> RUL".

The scientifically valid formulation is:

1. measure visible corrosion progression from images
2. estimate hidden damage where possible
3. smooth that hidden-damage signal over time
4. derive an exploratory threshold-status or time-to-threshold view

That is why the project consistently calls the last stage **proxy-RUL** or **threshold-status analysis**, not true RUL prediction.

## 4. What The Dataset Looks Like

### Core dataset facts

- 792 image files were found in the image folder.
- 791 image-table rows are usable after alignment.
- 48 unique specimens are present.
- The grouped unit is `specimen_id`.
- There is 1 orphan/corrupted image: `E01-20240508-17W.png`.

### Longitudinal structure

- Each specimen is observed repeatedly over time.
- Campaign 1 ends at week 28.
- Campaign 2 ends at week 36.
- The same specimen appears at multiple weeks, so this is a longitudinal dataset, not an independent-image dataset.

### Label structure

Dense labels available on all usable rows:

- `surface_total_rust_pct`
- `peak_rust_pct`
- their corresponding categorical versions
- `peak_rust_location_cm`

Sparse structural labels available only on 48 terminal rows:

- `wire_area_loss_frac` derived from `Last_Wire_Area_Loss_(Faliure_Surface)_%`
- `ultimate_load_kn`

### Why this matters

- We can study visible corrosion progression well.
- We can study structural damage only weakly, because structural labels are sparse and terminal-only.
- Grouped splitting is mandatory, otherwise the same specimen could appear in both train and test sets and cause leakage.

## 5. What The Thesis And Documentation Contributed

The thesis and conference paper were important because they gave the scientific context that the raw workbook alone does not provide.

They contributed:

- the specimen naming logic
- the campaign structure
- the treatment-group interpretation
- the physical interpretation of the structural labels
- the image-analysis logic used in the original research
- the approximate RGB threshold logic for rust, black, and gray regions
- the strip-based corrosion analysis idea along the specimen length

Important limitation:

- the exact original GIMP preprocessing pipeline could not be fully reconstructed from the documents, so the implementation uses the provided PNGs directly and applies deterministic feature extraction on them

## 6. The Actual Pipeline Used In This Project

## Stage 1. Audit and validation

Purpose:

- verify that the workbook and image folder really match
- detect missing, orphan, or unreadable files
- create one canonical master dataset

What it produced:

- `outputs/data/master_table.csv`
- `outputs/data/terminal_structural_table.csv`
- `outputs/audit/issues_log.csv`
- `outputs/audit/verified_facts.json`

What we learned:

- the usable aligned dataset is 791 rows, not 792
- the specimen grouping is consistent
- one image is orphaned and unreadable
- the dataset is clean enough to support a baseline pipeline

Why this stage is strong:

- it gives a trustworthy starting point
- it prevents silent data problems

## Stage 2. Deterministic specimen mapping

Purpose:

- reconstruct campaign and treatment information in a reviewable way

Why this was needed:

- the workbook treatment labels are too coarse
- some labels merge distinct protocols

What it used:

- `configs/specimen_mapping.yaml`

What we learned:

- campaign and treatment assignment should not be hidden inside Python logic
- the YAML mapping is important scientific bookkeeping

## Stage 3. EDA and dataset understanding

Purpose:

- understand row counts, specimen counts, treatment composition, week distribution, and missingness

Most useful outputs:

- `outputs/eda/figures/missingness.png`
- `outputs/eda/figures/structural_target_sparsity.png`
- `outputs/eda/tables/specimen_summary.csv`

What we learned:

- structural labels are extremely sparse
- every specimen has longitudinal surface data, but only one structural row
- campaign structure is strong and must be respected during evaluation

## Stage 4. Interpretable image feature extraction

Purpose:

- turn each image into readable corrosion indicators instead of using a black-box deep model first

Main feature families:

- rust-mask area ratio
- brightness and color statistics
- grayscale histogram features
- texture features
- morphology of rust regions
- strip-wise spatial corrosion summaries

What we learned:

- the extracted rust-area feature matches the workbook `surface_total_rust_pct` almost exactly
- strip features are highly informative for visible corrosion severity
- some features are redundant or unstable and should not be trusted blindly

Important interpretation:

- this stage is strong for explainability
- it is also useful because it exposes when a target is almost the same as an engineered input

## Stage 5. Feature engineering

Purpose:

- combine metadata and image features into one modelling table

Main output:

- `outputs/data/full_feature_table.csv`

What we learned:

- the feature space is large and contains redundancy
- some features are near-constant, duplicated, or highly collinear

## Stage 6. Leakage-safe split design

Purpose:

- evaluate models without specimen leakage

Implemented split strategies:

- grouped holdout by specimen
- leave-one-treatment-out
- leave-one-campaign-out

Why this matters:

- the hardest and most scientifically meaningful stress test is leave-one-campaign-out
- it shows whether the model generalizes beyond a particular experimental campaign

## Stage 7. Surface modelling

Purpose:

- benchmark whether interpretable features can recover visible corrosion labels

Important nuance:

- `surface_total_rust_pct` is mostly a sanity-check target, not a strong scientific discovery target
- it is almost numerically identical to `img_rust_area_ratio_pct`

What we learned:

- the image-analysis pipeline is internally coherent
- `peak_rust_pct` is a more meaningful auxiliary surface benchmark than `surface_total_rust_pct`

What to say in a presentation:

- "The surface stage mainly validates that the extracted image features are consistent with the labeled surface corrosion measurements."

What not to say:

- do not claim this stage proves predictive hidden-damage modelling

## Stage 8. Hidden-damage modelling

Purpose:

- test whether the feature table can estimate sparse structural targets

What happened:

- the stage was benchmarked carefully under grouped, leave-one-treatment-out, and leave-one-campaign-out evaluation
- an improvement round reduced the feature space and selected more robust models

What we learned:

- hidden-damage prediction remains weak overall
- the strongest robust models became metadata-only models
- that means the current stable signal comes mainly from experimental design and time variables, not from image features
- cross-campaign generalization still fails badly

This is an important negative result.

What to say in a presentation:

- "The structural stage was useful mainly because it revealed how hard the problem is and how much campaign confounding remains."

## Stage 9. Degradation modelling

Purpose:

- convert per-observation hidden-damage estimates into specimen-level trajectories over time

What the code does:

- predicts hidden damage across all observations
- enforces a monotone proxy trajectory
- fits several simple trajectory families
- keeps the best family per specimen using a documented criterion

What we learned:

- the trajectories are descriptive smoothers, not validated physical laws
- this stage is useful for visualization and threshold-status analysis
- it is not strong evidence of predictive degradation modelling yet

## Stage 10. Proxy-RUL / threshold-status analysis

Purpose:

- summarize when estimated hidden damage crosses predefined thresholds

Important truth:

- the current outputs are mostly status summaries
- they are not forward-looking residual-life predictions
- there are no future threshold crossings within the current projection horizon

What we learned:

- the proxy stage is still exploratory
- it is useful mainly for showing why stronger structural supervision is needed

## Stage 11. Diagnostics and improvement layer

Purpose:

- explain the feature space
- expose redundancy and outliers
- compare robustness across split strategies
- make weak points visible instead of hiding them

What we learned:

- the feature space contains near-constant, duplicate, and highly collinear features
- the temporal plots show clear corrosion progression patterns
- benchmark robustness matters more than a single good mean score
- improvements made the structural stage more conservative and more interpretable, but not strongly image-driven

## 7. What The Project Has Achieved Well

These are the strongest points to present confidently.

### Strong point 1. The data foundation is trustworthy

- 791 aligned rows
- 48 grouped specimens
- one explicit orphan/corrupt file logged
- leakage-safe grouped splits implemented

### Strong point 2. The image features are interpretable

- the project did not jump directly to black-box deep models
- the rust mask, strip features, and morphology features are understandable

### Strong point 3. The temporal corrosion story is visible

- the dataset really does capture progression over time
- campaign and treatment differences appear in the progression plots

### Strong point 4. The diagnostics are honest

- redundancy was measured
- outliers were not hidden
- benchmark collapse across campaign was made explicit

### Strong point 5. The project gives meaningful negative findings

- cross-campaign structural prediction is weak
- image features do not yet show robust hidden-damage inference
- proxy-RUL is not decision-ready

Those are scientifically valuable findings.

## 8. What Is Weak Or Must Be Presented Carefully

### Weak point 1. Surface success should not be oversold

`surface_total_rust_pct` is almost the same as an engineered rust-area feature, so that result is mainly a sanity check.

### Weak point 2. Structural labels are sparse

Only 48 rows have structural labels, and they are terminal rows only.

### Weak point 3. Hidden-damage modelling is still unstable

The best robust models rely mostly on metadata, not image features.

### Weak point 4. Campaign confounding is strong

Leave-one-campaign-out remains a hard failure case for structural targets.

### Weak point 5. Proxy-RUL is exploratory only

It is better described as threshold-status analysis than as usable residual-life prediction.

## 9. What You Should Say In A Presentation

Safe presentation wording:

- "We built a scientifically conservative baseline rather than a black-box model."
- "The dataset is longitudinal and specimen-grouped, so leakage-safe grouped evaluation was essential."
- "Direct RUL prediction was not valid because structural labels exist only on terminal rows."
- "The surface stage mainly validates the image-analysis pipeline."
- "The most informative result is actually a negative one: hidden-damage generalization collapses across campaign."
- "The feature diagnostics showed strong redundancy and helped clean the feature space."
- "The current proxy-RUL output should be interpreted as exploratory threshold-status analysis, not decision-ready prognostics."

## 10. What You Should Not Say

- Do not say the project predicts real RUL.
- Do not say the hidden-damage stage is solved.
- Do not say image features robustly predict structural damage across campaigns.
- Do not present `surface_total_rust_pct` as a major predictive achievement.
- Do not present the proxy-RUL stage as deployment-ready.

## 11. A Good Presentation Narrative

If you need a simple story:

1. Start with the dataset and why it is longitudinal.
2. Explain why grouped splitting and careful audit were necessary.
3. Show the interpretable image features and temporal corrosion progression.
4. Explain the feature diagnostics and redundancy findings.
5. Show the benchmark robustness results, especially where structural performance collapses.
6. End with the honest conclusion: the project successfully built an interpretable baseline and clarified what is possible, what is not, and what needs improvement next.

## 12. Bottom Line

The project is strongest as:

- a trustworthy data audit
- an interpretable corrosion-image baseline
- a clear temporal corrosion progression study
- a feature-diagnostics and robustness study
- an honest assessment of why hidden-damage and proxy-RUL remain difficult

That is a valid and presentation-worthy contribution.

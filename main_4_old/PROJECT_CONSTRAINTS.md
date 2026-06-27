# Project Constraints

This file is the canonical single source of truth for the implementation in `main_4/`.

## Verified Dataset Facts

- Aligned usable row count: `791`
- Unique specimens: `48`
- Image files found in `Data/Images_dataset/`: `792`
- Corrupted / orphan image files:
  - `E01-20240508-17W.png`
- Rows with structural labels:
  - `48` rows with `Last_Wire_Area_Loss_(Faliure_Surface)_%`
  - `48` rows with `Ultimate_Load_[kN]`
- Grouped split key: `specimen_id`
- Workbook/image alignment policy:
  - use only the `791` workbook rows that align to readable images
  - log, do not silently discard, orphan or unreadable image issues

## Hard Scientific Constraints

- Direct supervised RUL prediction from images is invalid for this dataset.
- Structural supervision is sparse and terminal-stage:
  - one structural-label row per specimen
  - no true failure-time / censoring labels
- All evaluation must be leakage-safe.
- The grouped unit is always the specimen identifier, not the image observation.

## Approved Problem Formulation

```text
surface corrosion progression
-> hidden damage estimation
-> degradation modelling
-> proxy-RUL / time-to-threshold
```

## Explicitly Forbidden Formulation

```text
image -> direct supervised RUL
```

## Approved Proxy-RUL Formulation

Proxy-RUL is implemented as deterministic time-to-threshold on a modeled degradation trajectory.

Approved baseline logic:

1. estimate a hidden-damage proxy trajectory from interpretable image features plus metadata
2. fit a specimen-level degradation curve over time
3. estimate threshold-crossing time for explicitly configured hidden-damage thresholds
4. report:
   - threshold-crossing time
   - proxy-RUL relative to the latest observation
   - right-censoring when the threshold is not reached within the projection horizon

## Non-Negotiable Split Rules

- `GroupShuffleSplit` must use `specimen_id`
- leave-one-treatment-out must use deterministic treatment groups reconstructed from `configs/specimen_mapping.yaml`
- leave-one-campaign-out must use reconstructed campaign labels
- no split may place two observations from the same specimen in both train and test

## Canonical Interpretation Notes

- `Last_Wire_Area_Loss_(Faliure_Surface)_%` is numerically stored as a fraction in `[0, 1]`, despite the `%` suffix in the workbook.
- `Treatment` and `Label_Treatment` in the workbook are not sufficiently granular for scientific treatment reconstruction; code must use `configs/specimen_mapping.yaml`.
- The provided PNGs are treated as the analysis images. Exact GIMP preprocessing cannot be perfectly reconstructed from the PDFs, so image preprocessing must remain deterministic and explicitly documented.

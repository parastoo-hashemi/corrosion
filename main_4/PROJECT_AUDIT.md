# Project Audit

## Scope

This audit covers the assets currently present under `main_4/`, with emphasis on:

- repository structure
- dataset inventory
- workbook schema
- image/table alignment
- thesis-derived scientific assumptions
- leakage and modelling risks

The audit is based on direct inspection of:

- `Data/Images_Dataset_A-Z.xlsx`
- `Data/Images_dataset/`
- `Documentation/Thesis/s313940_Tesi_conv_msc_thesis_final_md_al_amin_hossain_s313940.pdf`
- `Documentation/Conferences/ARTISTE_2025___Conference_paper__10pg___Al_Driven_Corrosion_Quantification_in_Cementitious_Materials_for_SHM.pdf`

## Repository Structure

```text
main_4/
├── Data/
│   ├── Images_Dataset_A-Z.xlsx
│   ├── Images_dataset/
│   └── Images_dataset.zip
└── Documentation/
    ├── Conferences/
    │   └── ARTISTE_2025___Conference_paper__10pg___Al_Driven_Corrosion_Quantification_in_Cementitious_Materials_for_SHM.pdf
    └── Thesis/
        └── s313940_Tesi_conv_msc_thesis_final_md_al_amin_hossain_s313940.pdf
```

The repository is currently data-first. There is no existing Python package, no source tree, and no training pipeline yet.

## Dataset Inventory

### Raw assets

- Workbook file: `Data/Images_Dataset_A-Z.xlsx`
- Image folder: `Data/Images_dataset/`
- Archived image bundle: `Data/Images_dataset.zip`
- Thesis PDF: 209 pages
- Conference paper PDF: 10 pages

### Usable observations

- Image folder contains `792` files with `.png` names.
- Workbook contains `793` physical rows:
  - row 1: group header
  - row 2: actual field names
  - rows 3-793: data-like rows
- After parsing the two header rows, the workbook contains `791` usable observation rows.
- `791` workbook sample names match image filenames exactly after appending `.png`.
- There is `1` orphan image file not represented in the workbook:
  - `E01-20240508-17W.png`
- That orphan file is also unreadable as a PNG by PIL and `file` reports it as generic `data`.

### Effective aligned dataset

The practically usable paired dataset is:

- `791` aligned image-table observations
- `48` unique specimens
- `24` specimens in Campaign 1
- `24` specimens in Campaign 2

## Campaign And Longitudinal Structure

| Campaign | Specimens | Rows | Weeks present | Structural labels available at | Key thesis context |
| --- | ---: | ---: | --- | --- | --- |
| Campaign 1 | 24 | 360 | 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 15, 24, 25, 28 | week 28 / day 196 | 7 steel meshes, 3.5% NaCl |
| Campaign 2 | 24 | 431 | 0, 2, 4, 6, 8, 10, 12, 14, 17, 19, 20, 23, 24, 26, 28, 30, 33, 36 | week 36 / day 252 | 4 steel meshes, 5% NaCl |

Notes:

- Campaign 2 should have had `24 x 18 = 432` rows, but only `431` are present because `E01-20240508-17W` is missing from the workbook.
- Repeated measurements are specimen-grouped and time-ordered.
- `Ageing Days` is perfectly consistent with the week suffix in the filename.
- No duplicate `Sample Name` values and no duplicate `(ID, Ageing Days)` pairs were found.

## Sample Naming Logic

### Workbook observation naming

`Sample Name` follows:

```text
<specimen_id>-<YYYYMMDD>-<week>W
```

Examples:

- `S1MI02-20220623-5W`
- `D04-20240710-26W`

### Specimen-level ID logic

The workbook uses compressed specimen identifiers:

- Thesis `S1-MI-02` becomes workbook `S1MI02`
- Thesis `S4-SA-VF-03` becomes workbook `S4SAVF03`
- Thesis `D-CL-04` becomes workbook `D04`

### Campaign logic recovered from IDs and thesis

- Campaign 1 specimen IDs start with `S1`, `S2`, `S3`, `S4`, `S5`
- Campaign 2 specimen IDs start with `D`, `E`, `F`, `G`

### Treatment logic

Observed workbook `Treatment` values:

- `NO`
- `MI`
- `SA`
- `PA`
- `SA_PA`
- `SA_VF`
- `VF`

Observed workbook `Label_Treatment` values:

- `D`
- `MI`
- `SA`
- `G`
- `VF`

Important interpretation:

- `Treatment` is already lossy.
- `Label_Treatment` is even more lossy.
- `SA` merges at least three distinct scientific protocols:
  - Campaign 1 surface-applied inhibitor series `S2`
  - Campaign 2 spray-applied inhibitor series `E`
  - Campaign 2 brush-applied inhibitor series `F`
- `G` merges:
  - `PA` from painted series `G`
  - `SA_PA` from combined paint + inhibitor series `S3`
- `VF` merges:
  - `VF`
  - `SA_VF`

Conclusion: `ID` plus thesis mapping is required to reconstruct treatment protocol correctly. The workbook treatment columns alone are not sufficient.

## Workbook Schema Summary

The workbook uses a two-row header. The top row is a group label; the second row contains the actual field name.

### Column groups and fields

| Group | Field | Type | Missing | Role | Audit note |
| --- | --- | --- | ---: | --- | --- |
| Sample_level | `Sample Name` | string | 0 | observation identifier | unique per observation |
| Sample_level | `ID` | string | 0 | specimen identifier | group key for splitting |
| Sample_level | `N_Steel_Mesh` | int | 0 | specimen covariate | constant within specimen |
| Sample_level | `Treatment` | string | 0 | coarse treatment label | insufficiently granular |
| Sample_level | `Label_Treatment` | string | 0 | coarser label | not scientifically unique |
| Sample_level | `Ageing Days` | int | 0 | time variable | repeated longitudinal index |
| Surface | `A_Surface_Total_Rust_Percentage[%]` | float | 0 | dense target / feature | all rows present |
| Surface | `A_Total_Rust_Category_(1–4)` | ordinal int | 0 | dense ordinal target | likely binned from previous column |
| Surface | `B_Peak_Rust_Percentage_[%]` | float | 0 | dense target / feature | all rows present |
| Surface | `B_Peak_Rust_Category_(1–4)` | ordinal int | 0 | dense ordinal target | likely binned from previous column |
| Surface | `B_Location_of_Peak_Rus_ in_length_[cm]` | float | 0 | dense target / feature | only 9 discrete values in workbook |
| Internal | `Cover_(Faliure_Surface)_[mm]` | float | 0 | specimen covariate | constant within specimen |
| Internal | `Last_Wire_Area_Loss_(Faliure_Surface)_%` | float | 743 | sparse structural target | available for 48 terminal rows only |
| Internal | `Ultimate_Load_[kN]` | float | 743 | sparse structural target | available for 48 terminal rows only |

### Target candidates

Dense surface targets available on every usable row:

- `A_Surface_Total_Rust_Percentage[%]`
- `A_Total_Rust_Category_(1–4)`
- `B_Peak_Rust_Percentage_[%]`
- `B_Peak_Rust_Category_(1–4)`
- `B_Location_of_Peak_Rus_ in_length_[cm]`

Sparse structural targets available only on one terminal row per specimen:

- `Last_Wire_Area_Loss_(Faliure_Surface)_%`
- `Ultimate_Load_[kN]`

Proxy-RUL is not present as a ground-truth label and must be derived from a thresholded degradation model.

### Important schema finding: unit inconsistency

`Last_Wire_Area_Loss_(Faliure_Surface)_%` is numerically stored as a fraction in `[0, 1]`, despite the `%` suffix in the header.

Examples:

- workbook `0.21250` matches thesis `21.25%`
- workbook `0.56980` matches thesis `56.98%`

This column must be renamed internally or converted explicitly during preprocessing to avoid silent unit errors.

### Category binning appears deterministic

The ordinal surface categories look like deterministic bins of the continuous variables.

Empirically inferred bins from the workbook:

- `A_Total_Rust_Category_(1–4)` is approximately:
  - category 1: `< 5`
  - category 2: `5 to <15`
  - category 3: `15 to <25`
  - category 4: `>= 25`
- `B_Peak_Rust_Category_(1–4)` is approximately:
  - category 1: `< 5`
  - category 2: `5 to <12`
  - category 3: `12 to <22`
  - category 4: `>= 22`

These thresholds were inferred from observed min/max values, not directly documented in the inspected PDFs.

## Missing Data Summary

### Column-level missingness

- No missing values in:
  - specimen identifiers
  - time variables
  - treatment labels
  - surface corrosion variables
  - cover measurement
- `743 / 791` rows are missing:
  - `Last_Wire_Area_Loss_(Faliure_Surface)_%`
  - `Ultimate_Load_[kN]`

### Structural-label pattern

- Exactly `48` rows have structural labels.
- Every specimen has exactly one structural-label row.
- Structural labels occur only at terminal ages:
  - Campaign 1: day `196`, week `28`
  - Campaign 2: day `252`, week `36`

This is the central reason direct supervised RUL is invalid.

## Image-Table Alignment Findings

### Positive checks

- All `791` workbook observation names have a corresponding image filename.
- All aligned image filenames are unique.
- No duplicate specimen-time rows were found.
- All specimen-level covariates are stable within specimen:
  - `Treatment`
  - `Label_Treatment`
  - `N_Steel_Mesh`
  - `Cover_(Faliure_Surface)_[mm]`

### Quality findings

- `791` aligned rows map cleanly to `791` usable images.
- `1` additional file exists:
  - `E01-20240508-17W.png`
- That file is unreadable and absent from the workbook.
- Among readable files, most images have size `(2835, 650)`; the corrupted orphan file does not parse as an image.

### Practical implication

The master table should exclude the orphan unreadable file and treat the aligned dataset size as `791`, not `792`.

## Scientific Assumptions Extracted From The Thesis And Conference Paper

### Experimental specimen setup

- 48 ferrocement specimens were studied.
- Specimen size is approximately `30 x 7.5 x 3 cm`.
- Campaign 1 used `7` steel wire mesh layers and `3.5%` NaCl exposure.
- Campaign 2 used `4` steel wire mesh layers and `5%` NaCl exposure.
- Campaign 2 also included chamber upgrades and a different wetting schedule.

### Campaign structure from thesis

Campaign 1:

- `S1`: mixed-in corrosion inhibitor
- `S2`: surface-applied inhibitor
- `S3`: paint + surface-applied inhibitor
- `S4`: surface-applied inhibitor + glass-based compound
- `S5`: glass-based compound
- untreated controls exist as the `01` specimen in multiple series

Campaign 2:

- `D`: untreated
- `E`: surface-applied inhibitor by spray
- `F`: surface-applied inhibitor by brush
- `G`: paint

### Image acquisition and processing methodology

From the thesis and conference paper:

- photographs were taken under controlled conditions
- white paper background and standard lighting were used
- white balance correction and cropping were applied before analysis
- a MATLAB RGB-threshold pipeline was used to quantify corrosion
- reported RGB thresholds include:
  - rust: `[25, 0, 0]` to `[255, 100, 80]`
  - black pores: `[0, 0, 0]` to `[5, 5, 0]`
  - grey marks: `[60, 70, 35]` to `[120, 105, 95]`

### Strip-based localization

The documentation is not fully consistent:

- conference paper: specimen length divided into `0.5 cm` strips
- thesis: `1 cm` strips with `0.5 cm` overlap, about `47` overlapping segments over `24 cm`
- workbook: only one coarse peak-location variable is retained, with `9` discrete positions

Interpretation:

- the workbook stores summarized outputs of the image-analysis pipeline, not the full strip profile
- the exact derivation of the workbook peak-location column is not fully documented in the inspected files

### Structural targets and meaning

From thesis Chapter 5 and Chapter 7:

- `Ultimate_Load_[kN]` is the peak load from four-point bending tests.
- `Last_Wire_Area_Loss_(Faliure_Surface)_%` corresponds to loss of cross-sectional area of the outermost longitudinal mesh wires near the aged / treated failure surface, derived from microscopic cross-sections.
- `Cover_(Faliure_Surface)_[mm]` is the cover distance from the outer wire to the aged / treated surface, measured on the selected failure-side cross-section.

### Scientific conclusion directly relevant to ML

The thesis explicitly reports that surface corrosion and internal wire area loss are related only imperfectly and can diverge strongly.

Examples extracted from thesis discussion:

- visible surface corrosion can coexist with moderate or high internal loss
- severe wire loss can appear even where surface corrosion is weak or visually absent
- multiple cuts within the same specimen show heterogeneous internal damage

Therefore, hidden damage estimation from surface evidence is plausible only as an uncertain proxy problem, not as a deterministic direct mapping.

## Leakage Risks

### Mandatory specimen grouping

The same specimen appears at multiple time points. Any image-level random split will leak specimen identity, background, geometry, treatment, and part of the degradation trajectory across train and test.

Required rule:

- all train/validation/test splitting must group by specimen `ID`

### Longitudinal leakage

If one time point of a specimen is in train and another time point of the same specimen is in test, the model can exploit specimen-specific appearance rather than true generalization.

### Campaign confounding

Campaign is strongly confounded with:

- `N_Steel_Mesh`
- NaCl concentration
- exposure duration
- treatment design
- calendar year

This means:

- high performance on mixed campaign data can hide campaign memorization
- leave-one-campaign-out must be treated as a harsh external generalization test

### Structural-label leakage

Structural labels exist only on terminal rows. If earlier rows from the same specimen are allowed into training while the terminal row is in testing, hidden-damage models will leak specimen identity.

### Feature leakage from identifiers

Potentially leaky raw fields:

- `Sample Name` contains exact date and week
- `ID` encodes campaign and series

These fields are useful for indexing and grouping, but they must not be naively one-hot encoded without an explicit scientific reason.

### Published split risk

The conference paper reports train/validation/test counts in image units. The specimen-grouping details are not documented clearly enough to reuse that split safely for this project.

## Risk Notes

### Data and documentation inconsistencies

- Usable aligned data is `791`, not `792`, because one image is orphaned and unreadable.
- Conference paper mentions `760` prepared images in one section but later reports split counts summing to `792`.
- Thesis and conference paper describe slightly different strip-analysis resolutions.
- Thesis discussion text contains at least one likely treatment-label inconsistency for `E` versus `F`; treatment tables in Chapter 4 are more reliable than later narrative text.

### Modelling implications

- Surface corrosion trajectories are noisy and non-monotonic for every specimen.
- Structural labels are extremely sparse.
- `Treatment` and `Label_Treatment` cannot be used as authoritative treatment-protocol variables without ID-based reconstruction.
- Internal area-loss units must be normalized before any modelling or plotting.

## Audit Conclusion

This dataset supports a scientifically valid pipeline for:

1. surface corrosion quantification / forecasting
2. hidden damage estimation from surface evidence plus covariates
3. degradation-state modelling
4. threshold-based proxy-RUL estimation

This dataset does **not** support direct supervised RUL prediction from images, because:

- there is no true RUL label
- there are no failure times or censoring annotations
- structural targets are sparse end-point measurements only
- campaign effects are strong and confounded with key physical factors

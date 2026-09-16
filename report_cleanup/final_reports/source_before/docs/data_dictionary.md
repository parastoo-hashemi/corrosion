# Data dictionary and interpretation

## Assets and observation units

| Asset | Meaning |
|---|---|
| [Data/Images_dataset/](../Data/Images_dataset/) | Supplied analysis PNGs; exact earlier raw-to-PNG preprocessing is not fully recoverable |
| [Data/Images_Dataset_A-Z-1.xlsx](../Data/Images_Dataset_A-Z-1.xlsx) | Current four-class preparation workbook |
| [Data/Images_Dataset_A-Z.xlsx](../Data/Images_Dataset_A-Z.xlsx) | Historical modelling workbook; do not interchange with the classification revision |
| [structural_capacity/outputs/data/master_table.csv](../structural_capacity/outputs/data/master_table.csv) | 791 readable/aligned image observations across 48 specimens |
| [structural_capacity/outputs/data/terminal_structural_table.csv](../structural_capacity/outputs/data/terminal_structural_table.csv) | Terminal structural observations |
| [Data/Images_Dataset_A-Z-1_augmented.csv](../Data/Images_Dataset_A-Z-1_augmented.csv) | Original/augmented image metadata and transformation provenance |
| [Data/splits/](../Data/splits/) | Fixed train/validation/test classification manifests |
| [Data/augmentation_variants/](../Data/augmentation_variants/) | Additional controlled variants; each local README describes its data and whether images are referenced or stored |

A specimen is the independent grouping unit. A photograph is a repeated observation.
Augmentation produces variants of an observation, not new independent specimens.
The unreadable source image is `E01-20240508-17W.png`; its exclusion leaves 791 rows.

## Fields

| Field / term | Definition and units | Interpretation boundary |
|---|---|---|
| `specimen_id` | Physical specimen identifier | Keep all its observations in one partition |
| `sample_name`, image filename | Observation key, including specimen/date/week | A key, not a model feature |
| `week`, `ageing_days` | Exposure-time coordinates | They do not supply repeated measured structural targets |
| `surface_total_rust_pct` | Image-derived total visible rust, percentage points | Later main_4 image feature/label near-identity makes this a reconstruction check |
| `peak_rust_pct` | Image-derived maximum local rust, percentage points | Distinct from total visible rust |
| `peak_rust_location_cm` | Position of peak rust along the specimen, cm | A location target, not a rust fraction |
| `wire_area_loss_frac` | Terminal wire-area loss, fraction of area | Raw workbook field `Last_Wire_Area_Loss_(Faliure_Surface)_%` has a misleading percent suffix; multiply the stored fraction by 100 for percent |
| `wire_area_loss_pct` | Percent representation used in some older experiments | Do not compare MAEs directly with fraction-scale MAEs |
| `ultimate_load_kn` | Measured terminal ultimate load, kN | One outcome per specimen |
| `terminal_ultimate_load_kn_target` | Terminal outcome attached to historical rows in the refocused training table | Repetition of the endpoint label; not load measured at each photograph |
| `cover_mm` / failure-surface cover | Cover measurement at the failure surface, mm | Pre-test availability is not verified |
| `campaign_id`, `n_steel_mesh`, `nacl_pct` | Campaign, mesh family, chloride concentration | Perfectly aligned design factors here; coefficients do not isolate causes |
| `treatment_protocol`, `split_group_treatment` | Reconstructed treatment grouping | Config mapping is more detailed than raw workbook treatment fields; YAML coercion remains unresolved |
| `img_*` | Deterministic image descriptors | See saved feature dictionaries; visible appearance is not hidden damage |
| `predicted_wire_area_loss_frac` | Model-derived structural proxy along time | Not an observed longitudinal wire-loss series |
| `proxy_rul_days`, `threshold_status` | Model-curve threshold calculation | No observed lifetime or validated survival endpoint |
| OOF | Out-of-fold prediction, made while the specimen is held out | Repeated predictions/folds are dependent; full-fit diagnostics differ |

Image feature definitions are saved in
[the baseline dictionary](../structural_capacity/outputs/features/feature_dictionary.csv) and
[the refocused dictionary](../structural_capacity/outputs/ultimate_load_refocus/features/feature_dictionary.csv).

## Label versions and augmentation

The current classification task uses four severity categories. The older `condition_assessment`
five-class experiment and the predecessor three-class classification are separate
label systems. Their metrics cannot be assigned to the current untrained classifier.
The prepared full image package contains 791 originals and five variants each;
the fixed manifests retain training augmentations and exclude augmented validation/
test specimens. Thus 4,746 prepared images are not the 3,996 rows retained for training/
validation/test. Variant metadata must also respect the same specimen separation.

Original image bytes, labels, specimen identity, and transformation provenance are
retained. Label preservation under augmentation is a study assumption, not a
completed classifier robustness result.

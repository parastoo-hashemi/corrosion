# Four-class corrosion image preparation

**The main augmented dataset and fixed splits are prepared. Classifier training
and evaluation remain unfinished.** Optional controlled variants are also saved,
but need the metadata checks described below before a training comparison.

Formerly `augmentation/`, this is a separate classification workstream. It does
not inherit the accuracy of earlier three-band regression interpretations or the
historical five-class [condition-assessment experiment](../condition_assessment/README.md).

## Inputs and labels

- Images: [Data/Images_dataset/](../Data/Images_dataset/).
- Workbook: [Images_Dataset_A-Z-1.xlsx](../Data/Images_Dataset_A-Z-1.xlsx), distinct
  from the older modelling workbook without `-1`.
- Image identifier: `Sample Name`; specimen grouping: `ID`, preserved as `specimen_id`.
- Target: **`A_Total_Rust_Category_(1–4)`**, copied into `label` as integers 1–4.
  `B_Peak_Rust_Category_(1–4)` is retained metadata, not this task's target.

There are **791 readable originals from 48 specimens**. The unreadable
`E01-20240508-17W.png` has no row in this workbook and was excluded. Original class
counts are **658 / 99 / 20 / 14** for labels 1 / 2 / 3 / 4. Augmentation creates
additional views of these observations, not additional independent specimens.

## Saved dataset and actual training partitions

The [full metadata](../Data/Images_Dataset_A-Z-1_augmented.csv) describes **4,746 images**
in [the augmented collection](../Data/Images_dataset_augmented/): 791 originals plus
3,955 augmentations. The saved run uses **five copies per original and seed 20260630**;
the script default is four copies, so reproduction requires explicit `--copies 5`.

The full collection is not a training manifest. Use the fixed files below:

| Split | Specimens | Originals | Augmentations | Total rows | Class counts 1 / 2 / 3 / 4 |
|---|---:|---:|---:|---:|---|
| [Train](../Data/splits/train_manifest.csv) | 38 | 641 | 3,205 | 3,846 | 3,156 / 540 / 78 / 72 |
| [Validation](../Data/splits/val_manifest.csv) | 5 | 75 | 0 | 75 | 67 / 4 / 3 / 1 |
| [Test](../Data/splits/test_manifest.csv) | 5 | 75 | 0 | 75 | 65 / 5 / 4 / 1 |

The manifests retain **3,996 rows**. The remaining **750 augmented copies** belong
to validation/test specimens and are excluded from all three manifests. Specimens
and original-image identities do not overlap between splits. Assignments are
explicit lists in [make_splits.py](make_splits.py), not a new random split on each run.
Both held-out sets have only one class-4 image; future evaluation must report this
imbalance and cannot rely on overall accuracy alone.

## Augmentation and provenance

The five recipes are brightness/contrast, saturation/colour balance, blur/noise,
combined photometric changes, and horizontal flip with brightness adjustment.
Read the [saved preparation report](augmentation_dataset_report.md) for ranges
and source-audit details, and inspect the [contact sheet](augmentation_examples.png).
The [methodology PDF](augmentation_methodology_final.pdf) and
[LaTeX source](augmentation_methodology_final.tex) preserve the detailed study.

Each main-dataset row records `original_image_name`, `augmented_image_name`,
`specimen_id`, `label`, `is_augmented`, transformation type/parameters and paths.
Keep this provenance with the images. Label preservation is a study assumption;
photometric transforms do not automatically preserve colour-threshold regression
targets or structural outcomes.

### Optional controlled variants

[Data/augmentation_variants/](../Data/augmentation_variants/) contains:

- `size_plus50`, `size_plus100`, `size_plus150`: 1,187 / 1,582 / 1,978 metadata
  rows, referencing images in the main augmented collection.
- `sigma2_brightness`, `sigma3_brightness`: 2,373 rows each, with generated
  brighter/darker images in each variant's `images/` directory.
- `sigma2_noise`, `sigma3_noise`: saved Gaussian-noise variants. The current
  `sigma2_noise/metadata.csv` has **1,580 rows**, while its historical README states
  1,582; `sigma3_noise` has 1,582.

**These variants are not ready-made train/validation/test manifests.** The four
`sigma*` metadata files currently omit `specimen_id` and image-path fields. Recover
grouping by joining `original_image_name` to the main metadata, check image locations
and completeness, then apply the fixed specimen assignments. Use augmented rows
only for training. See [variant issues](../docs/known_issues.md#controlled-variant-metadata-needs-reconciliation)
for the two missing original rows in `sigma2_noise`. No variant demonstrates a
measured classifier improvement yet.

## Scripts and continuation

| Entry point | Role and outputs |
|---|---|
| [augment_dataset.py](augment_dataset.py) | Audits images/workbook, copies originals, creates augmentations, metadata, reports and contact sheet |
| [make_splits.py](make_splits.py) | Creates train/validation/test CSVs with fixed specimen assignments and excludes held-out augmentations |
| [create_dataset_variants.py](create_dataset_variants.py) | Creates controlled size, brightness and noise variants plus metadata/checksums and figures |
| [scripts/](scripts/) | Image-statistics and illustration utilities; [saved statistics](tables/image_statistics_full.csv) and [figures](figures/) support the methodology |

From the **repository root**, inspect interfaces without generating datasets:

```bash
python classification_data_preparation/augment_dataset.py --help
python classification_data_preparation/make_splits.py --help
python classification_data_preparation/create_dataset_variants.py --help
```

[Reproduction instructions](../docs/reproduction.md#3-classification-data-preparation-in-order)
give generation commands with new destinations in a separate copy. The old report's
`augmentation/... --overwrite` command is historical. Current scripts use the
descriptive folder name; do not overwrite the delivered package to check an installation.
Variant contact sheets still use a fixed phase directory even with a new `--output-dir`.

[Requirements](requirements.txt) specify minimum versions; split/variant scripts
also require pandas. Start future classifier work from the saved main manifests,
fit preprocessing on training data only, choose models using validation data, and
reserve test data for final evaluation. No classifier or new split is created by
this documentation cleanup.

See the [data dictionary](../docs/data_dictionary.md),
[historical code reference](../docs/reference/augmentation_code.md),
[experiment map](../docs/experiments.md) and [project overview](../README.md).

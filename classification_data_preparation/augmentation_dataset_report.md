# Augmented Corrosion Image Dataset Report

## Completion status

**Completed successfully: Yes.**

The offline dataset was generated for four-class corrosion image classification only. No ResNet50, ViT, structural prediction, ultimate-load, wire-loss, or RUL model was trained or reproduced.

## Inputs and column mapping

- Source images: `Data/Images_dataset`
- Source workbook: `Data/Images_Dataset_A-Z-1.xlsx`
- Worksheet: `Sheet1`
- Image filename column: `Sample Name`; extension-free values were matched to image stems.
- Four-class label column: `A_Total_Rust_Category_(1–4)`; values were validated as integers in `{1, 2, 3, 4}`.
- Specimen/group column: `ID`; preserved as `specimen_id` for leakage-safe downstream splitting.
- Workbook records inspected: 791
- Distinct matched specimens: 48

The workbook's `B_Peak_Rust_Category_(1–4)` column is preserved as original metadata but is not the classification target. The selected target is the surface-total rust category requested for this dataset.

## Source audit

- Files in the source image folder: 792
- Readable image files: 791
- Workbook rows with readable matching images: 791
- Workbook rows missing an image file: 0
- Corrupted/unreadable files: 1
- Image-folder files without a workbook row: 1
- Readable dimensions: 2835x630: 1, 2835x643: 1, 2835x650: 789
- Readable colour modes: RGB: 12, RGBA: 779

### Missing image files

None.

### Corrupted/unreadable image files

- `E01-20240508-17W.png — UnidentifiedImageError: cannot identify image file '/Users/parastoo/All_projects/Proj_corrosion/corrosion/Data/Images_dataset/E01-20240508-17W.png'`

### Image-folder files without a workbook row

- `E01-20240508-17W.png`

The known corrupted file `E01-20240508-17W.png` has no workbook row. It was recorded in the audit and excluded.

## Generated dataset

- Output image folder: `Data/Images_dataset_augmented`
- Output metadata: `Data/Images_Dataset_A-Z-1_augmented.csv`
- Original images copied byte-for-byte: 791
- Augmented images generated: 3955
- Total output images and metadata rows: 4746
- Expansion factor: 6x (`1 original + 5 augmented`)
- Random seed: `20260630`

| Label | Original readable images | Augmented images | Total output images |
|---:|---:|---:|---:|
| 1 | 658 | 3290 | 3948 |
| 2 | 99 | 495 | 594 |
| 3 | 20 | 100 | 120 |
| 4 | 14 | 70 | 84 |

Every output row preserves all original workbook columns. Provenance fields include `original_image_name`, `augmented_image_name`, `image_path`, `original_image_path`, `label`, `augmentation_id`, `augmentation_type`, `augmentation_parameters`, `is_augmented`, and `specimen_id`.

## Augmentation recipes

The five augmentation recipes use label-preserving transforms. Parameter ranges are
calibrated to the measured inter-image luminance variation in the source dataset
(luminance range 98–255; 5th–95th percentile ratio 1.75x; real-world brightest-to-
darkest ratio 2.60x). The previous conservative [0.85, 1.15] range covered only 1.35x
of that variation and was widened accordingly.

1. `brightness_contrast`: brightness sampled from `[0.75, 1.28]`, contrast from `[0.78, 1.25]`. Calibrated to the real inter-image brightness distribution.
2. `saturation_colour_balance`: saturation from `[0.78, 1.28]`; normalized per-channel RGB gains from `[0.94, 1.06]`. Simulates camera white-balance and surface-wetness variation.
3. `gaussian_blur_noise`: Gaussian blur sigma from `[0.3, 1.5]` pixels; Gaussian noise sigma from `[0.005, 0.035]` in normalized `[0, 1]` RGB space. Simulates focus variation and sensor noise.
4. `brightness_contrast_saturation`: brightness, contrast, and saturation each independently sampled from `[0.82, 1.18]`. Represents compound photometric effects.
5. `horizontal_flip_brightness`: image mirrored left-to-right (label-safe for total-rust-category classification, which is position-invariant), combined with brightness from `[0.85, 1.15]`. First geometric augmentation; adds spatial diversity without altering rust-coverage class.

Excluded: MixUp, CutMix, GAN/diffusion synthesis, elastic deformation, random erasing,
vertical flip, large rotation (>10°), and heavy hue shifts (>0.1). These were excluded
because they corrupt label integrity, are physically implausible for this imaging setup,
or require infrastructure (generative models) outside the scope of this dataset.

## Quality and leakage controls

- Original source files and the workbook were opened read-only and were not modified.
- Output originals are byte-for-byte copies; augmented images are separate PNG files.
- Labels were copied exactly from `A_Total_Rust_Category_(1–4)` and validated before generation.
- `original_image_name` and `specimen_id` are present on every row.
- Future train/validation/test splitting must be performed by `specimen_id` before selecting augmented rows. All rows sharing an `original_image_name` must remain in the same split.
- The contact sheet is `Documentation/augmentation_examples.png`. Its deterministic source examples are: `G03-20240124-2W.png`, `E02-20240522-19W.png`, `S2SA03-20221102-24W.png`, `D04-20240417-14W.png`.

## Reproduction

From the project root:

```bash
python augmentation/augment_dataset.py --copies 5 --seed 20260630 --overwrite
```

Use `--copies N` to change the number of augmented copies and `--seed N` to change the deterministic random stream. Existing generated outputs are protected unless `--overwrite` is supplied.

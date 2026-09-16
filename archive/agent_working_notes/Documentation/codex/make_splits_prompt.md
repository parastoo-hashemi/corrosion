# Codex Prompt: make_splits.py

Paste the entire block below into Codex without modification.

---

## Task

Create `augmentation/make_splits.py`.

This script reads the offline-augmented corrosion image dataset and produces
reproducible, leakage-free train / validation / test split manifests for a
four-class corrosion severity classification study.

---

## Background (read before writing any code)

The dataset has 48 ferrocement specimens, each photographed at multiple time
steps. There are 791 original images and 3,955 augmented copies (5 per original),
giving 4,746 total rows in the CSV.

The classification target is `A_Total_Rust_Category_(1–4)`, a four-class label
(1 = no rust, 4 = severe rust).

**Splitting rules that must not be violated:**

1. Splits are at the specimen level. All images from the same specimen must be in
   the same split. This is enforced by the `specimen_id` column.

2. Augmented images belong to the training split only. Validation and test splits
   contain only original images (`is_augmented == False`).

3. Augmented copies of validation and test specimens are excluded from all splits.
   They must not appear in train, val, or test. They are recorded in the report
   as excluded rows.

4. The split is stratified by each specimen's maximum severity label. The dataset
   has only 5 specimens that ever reach label 3 and 5 that ever reach label 4.
   A random split can produce a test set with no rare-class examples, making
   evaluation uninformative. Stratification prevents this.

5. The specimen assignment is deterministic and hardcoded (see Section SPECIMEN
   ASSIGNMENT below). No random seed is needed for the assignment itself.

---

## Input

```
Data/Images_Dataset_A-Z-1_augmented.csv
```

Relevant columns (exact names, copy these literally):

| Column | Description |
|---|---|
| `original_image_name` | Filename of the source image (same for a source and all its copies) |
| `augmented_image_name` | Filename of this row's image file |
| `image_path` | Relative path to this row's image file |
| `original_image_path` | Relative path to the source image |
| `label` | Integer in {1, 2, 3, 4} — same as `A_Total_Rust_Category_(1–4)` |
| `augmentation_id` | Integer 0 (original) or 1–5 (augmented copy index) |
| `augmentation_type` | String: `"original"` or a recipe name |
| `augmentation_parameters` | String: semicolon-separated key=value parameters |
| `is_augmented` | Boolean: `False` for originals, `True` for augmented copies |
| `specimen_id` | String specimen identifier, e.g. `"D01"`, `"S2SA03"` |
| `A_Total_Rust_Category_(1–4)` | Integer in {1, 2, 3, 4} — the classification target |

All other columns from the original workbook are also present and must be
forwarded to the output manifests unchanged.

---

## Specimen Assignment

The 48 specimens are stratified by the maximum label any of their original images
carries. The assignment below is hardcoded and must be reproduced exactly.

### Stratum 1 — specimens whose maximum label is 1 (16 specimens)

Sorted alphabetically:
D01, D02, D03, E01, E05, E06, F01, G01, G03, G04, G05, G06, S1MI07, S2SA02,
S3PA02, S3PA04

Assignment:
- **Test:** S3PA04
- **Val:** S3PA02
- **Train:** D01, D02, D03, E01, E05, E06, F01, G01, G03, G04, G05, G06, S1MI07, S2SA02

### Stratum 2 — specimens whose maximum label is 2 (22 specimens)

Sorted alphabetically:
E02, E03, E04, F02, F03, F04, F05, F06, G02, S1MI01, S1MI02, S1MI03, S1MI06,
S2SA01, S2SA04, S2SA05, S3PA01, S3PA03, S4SAVF01, S4SAVF02, S5VF01, S5VF03

Assignment:
- **Test:** S5VF01, S5VF03
- **Val:** S4SAVF01, S4SAVF02
- **Train:** E02, E03, E04, F02, F03, F04, F05, F06, G02, S1MI01, S1MI02, S1MI03,
  S1MI06, S2SA01, S2SA04, S2SA05, S3PA01, S3PA03

### Stratum 3 — specimens whose maximum label is 3 (5 specimens)

Sorted alphabetically:
D05, D06, S2SA06, S2SA07, S5VF02

Assignment:
- **Test:** S5VF02
- **Val:** S2SA07
- **Train:** D05, D06, S2SA06

### Stratum 4 — specimens whose maximum label is 4 (5 specimens)

Sorted alphabetically:
D04, S1MI04, S1MI05, S2SA03, S4SAVF03

Assignment:
- **Test:** S4SAVF03
- **Val:** S2SA03
- **Train:** D04, S1MI04, S1MI05

### Summary

| Split | Specimens | Stratum breakdown |
|---|---|---|
| Train | 38 | 14 from S1, 18 from S2, 3 from S3, 3 from S4 |
| Val | 5 | 1 from S1, 2 from S2, 1 from S3, 1 from S4 |
| Test | 5 | 1 from S1, 2 from S2, 1 from S3, 1 from S4 |

---

## Row Selection Rules Per Split

Given the specimen assignment above:

**Train manifest:**
- Include ALL rows (both `is_augmented == False` and `is_augmented == True`)
  for every specimen in the train set.
- Add a column `split` with value `"train"` to every row.

**Val manifest:**
- Include ONLY rows where `is_augmented == False` for every specimen in the
  val set.
- Add a column `split` with value `"val"` to every row.

**Test manifest:**
- Include ONLY rows where `is_augmented == False` for every specimen in the
  test set.
- Add a column `split` with value `"test"` to every row.

**Excluded rows:**
- Augmented rows (`is_augmented == True`) for val and test specimens.
- These rows must NOT appear in any output manifest.
- Count them and record the count in the report.

---

## Outputs

### Split manifests

Write three CSV files. The output directory is configurable (default:
`Data/splits/`). Create the directory if it does not exist.

```
Data/splits/train_manifest.csv
Data/splits/val_manifest.csv
Data/splits/test_manifest.csv
```

Each manifest contains all columns from the input CSV plus a new `split` column
(first column). Preserve column order: `split` first, then all original columns.

### Split report

Write a Markdown report to `Documentation/codex/split_report.md`.

The report must contain:

1. **Method:** One paragraph explaining that splits are specimen-level and
   stratified by maximum severity label.

2. **Specimen assignment table:** For each split, list the specimen_ids assigned
   to it, grouped by stratum.

3. **Row counts table:**

   | Split | Specimens | Original rows | Augmented rows | Total rows |
   |---|---|---|---|---|
   | Train | 38 | X | X | X |
   | Val | 5 | X | 0 | X |
   | Test | 5 | X | 0 | X |
   | Excluded (aug) | — | 0 | X | X |
   | **Total** | **48** | **791** | **3955** | **4746** |

4. **Per-class distribution in val and test:** For each of val and test, report
   how many rows of each label (1, 2, 3, 4) are present.

5. **Leakage statement:** One sentence confirming no specimen_id appears in more
   than one split.

6. **Reproduction command:** The exact command to regenerate the splits.

---

## Validation Checks

After writing all outputs, the script must run the following checks. If any check
fails, raise `RuntimeError` with a descriptive message and delete the partial
output files before exiting.

```
1. No specimen_id appears in more than one of {train, val, test} sets.

2. No augmented row (is_augmented == True) appears in the val or test manifest.

3. Every row where is_augmented == False (all 791 original rows) appears in
   exactly one of {train_manifest, val_manifest, test_manifest}.

4. The sum of rows across the three manifests plus excluded rows equals 4746.

5. The val manifest contains at least one row of each label {1, 2, 3, 4}.

6. The test manifest contains at least one row of each label {1, 2, 3, 4}.

7. Every specimen_id in the train manifest is a member of the hardcoded train set.
   Every specimen_id in the val manifest is a member of the hardcoded val set.
   Every specimen_id in the test manifest is a member of the hardcoded test set.
```

Print a summary line for each check that passes: `[OK] <check description>`.
Print all validation results before writing the report.

---

## Command-line Interface

```
python augmentation/make_splits.py [options]

Options:
  --input-csv PATH      Input augmented CSV
                        (default: Data/Images_Dataset_A-Z-1_augmented.csv)
  --output-dir PATH     Directory for split manifest CSVs
                        (default: Data/splits)
  --report PATH         Path for the Markdown report
                        (default: Documentation/codex/split_report.md)
  --overwrite           Allow overwriting existing output files.
                        Without this flag, exit with an error if any
                        output file already exists.
```

The script must be runnable from the repository root:

```bash
python augmentation/make_splits.py --overwrite
```

---

## Expected Console Output

When run successfully, the script must print lines matching this structure
(exact counts may differ if the CSV changes, but the structure is fixed):

```
Loading Data/Images_Dataset_A-Z-1_augmented.csv ... 4746 rows, 48 specimens.
Computing per-specimen maximum labels ...
Applying hardcoded stratified specimen assignment ...
  Train: 38 specimens
  Val:   5 specimens
  Test:  5 specimens

Building split manifests ...
  Train: 641 original + 3205 augmented = 3846 rows
  Val:   75 original + 0 augmented = 75 rows
  Test:  75 original + 0 augmented = 75 rows
  Excluded augmented rows: 750

Running validation checks ...
[OK] No specimen appears in more than one split
[OK] No augmented row in val or test
[OK] All 791 original rows assigned to exactly one split
[OK] Row totals sum to 4746 (3846 + 75 + 75 + 750)
[OK] Val manifest contains labels {1, 2, 3, 4}
[OK] Test manifest contains labels {1, 2, 3, 4}
[OK] Specimen assignments match hardcoded lists

Writing Data/splits/train_manifest.csv ... 3846 rows
Writing Data/splits/val_manifest.csv ... 75 rows
Writing Data/splits/test_manifest.csv ... 75 rows
Writing Documentation/codex/split_report.md ...

Done. Splits written successfully.
```

---

## Implementation Notes

- The specimen assignment is hardcoded. Do not compute it from the data at
  runtime — define it as three Python lists (or sets) at the top of the script,
  named `TRAIN_SPECIMENS`, `VAL_SPECIMENS`, `TEST_SPECIMENS`.

- Verify at startup that the union of `TRAIN_SPECIMENS ∪ VAL_SPECIMENS ∪
  TEST_SPECIMENS` equals the set of specimen_ids found in the input CSV, and
  that the three sets are disjoint. Raise `RuntimeError` if either check fails.
  This guards against CSV changes that would silently invalidate the split.

- Use `pandas` for all CSV I/O. Do not use `sklearn` — the split is fully
  determined by the hardcoded lists.

- Write CSV files with `index=False`. Use UTF-8 encoding throughout.

- The `split` column must be the first column in each output CSV.

- Do not modify the input CSV.

- Do not open the source image files. Only read the CSV.

---

## What NOT to do

- Do not use a random split. The assignment is hardcoded.
- Do not put augmented rows in val or test.
- Do not put augmented rows from val/test specimens into train.
- Do not write a Jupyter notebook. Write a plain Python script.
- Do not add dependencies beyond `pandas`, `pathlib`, `argparse`, `sys`,
  `hashlib`, `shutil`.
- Do not train any model.
- Do not modify `augment_dataset.py` or the augmented image files.

# CSV Schema Audit

## 1. Repository-wide summary

- Total CSV files found: **329**.
- Unique header sets found: **70**.
- Evidence used for this audit:
  - workbook source: `Data/Images_Dataset_A-Z.xlsx`
  - ingestion and validation: `run_audit_validation.py`, `src/corrosion_proxy_rul/data_loading.py`, `src/corrosion_proxy_rul/data_cleaning.py`, `src/corrosion_proxy_rul/schema_validation.py`, `src/corrosion_proxy_rul/specimen_mapping.py`
  - feature extraction: `run_extract_image_features.py`, `src/corrosion_proxy_rul/image_features.py`, `configs/features.yaml`
  - feature engineering and model stages: `train_surface_models.py`, `train_hidden_damage_models.py`, `train_degradation_models.py`, `train_rul_proxy_models.py`, `src/corrosion_proxy_rul/feature_engineering.py`, `src/corrosion_proxy_rul/evaluation.py`, `src/corrosion_proxy_rul/models_surface.py`, `src/corrosion_proxy_rul/models_hidden_damage.py`, `src/corrosion_proxy_rul/models_degradation.py`, `src/corrosion_proxy_rul/models_rul_proxy.py`, `src/corrosion_proxy_rul/splits.py`, `configs/modeling.yaml`, `configs/thresholds.yaml`
  - diagnostics and reporting: `src/corrosion_proxy_rul/eda.py`, `src/corrosion_proxy_rul/diagnostics.py`, `src/corrosion_proxy_rul/reporting.py`, `main.tex`, `CODEBASE_GUIDE.md`, `FEATURE_DIAGNOSTICS.md`, `OUTPUT_REVIEW.md`

### Major CSV families

- `outputs/audit/` (4 files): normalized workbook rows, image scan, specimen mapping, issue log.
- `outputs/data/` (3 files): canonical aligned observation table, terminal structural subset, merged full feature table.
- `outputs/features/` (3 files): deterministic image features, feature dictionary, extraction-failure log.
- `outputs/splits/` (6 files): master-table split manifests and split summaries.
- `outputs/eda/tables/` (7 files): EDA summaries derived from `master_table.csv`.
- `outputs/models/surface/` (32 files): surface-stage feature table, split manifests, evaluation outputs, best-model summary.
- `outputs/models/hidden_damage/` (186 files): structural feature table, experiment outputs, final selected-model outputs, split manifests, feature-selection tables, robustness tables.
- `outputs/models/degradation/` (5 files): hidden-damage proxy trajectories and fitted degradation curves.
- `outputs/models/proxy_rul/` (2 files): threshold-status specimen table and threshold summary.
- `outputs/diagnostics/tables/` (28 files): secondary diagnostic summaries and plotting-ready tables.
- `outputs/improvements/tables/` (9 files): baseline-vs-improved comparison tables.
- `outputs/improvements/baseline_snapshot/` (43 files): historical baseline exports used by `run_model_improvement_analysis.py`.
- `OUTPUT_INVENTORY.csv` (1 file): manual inventory / documentation table.

### Which files are raw, processed, model outputs, or historical

- Closest to raw:
  - `outputs/audit/metadata_loaded.csv`: direct workbook columns after renaming only.
  - `outputs/audit/image_scan.csv`: direct PNG scan metadata.
- Processed / engineered:
  - `outputs/data/master_table.csv`
  - `outputs/data/terminal_structural_table.csv`
  - `outputs/features/image_features.csv`
  - `outputs/data/full_feature_table.csv`
  - `outputs/models/surface/surface_feature_table.csv`
  - `outputs/models/hidden_damage/hidden_damage_feature_table.csv`
  - `outputs/eda/tables/*.csv`
  - `outputs/diagnostics/tables/*.csv`
- Model outputs:
  - all `outputs/models/surface/**/*.csv`
  - all `outputs/models/hidden_damage/**/*.csv`
  - all `outputs/models/degradation/*.csv`
  - all `outputs/models/proxy_rul/*.csv`
- Historical / comparison-only:
  - all `outputs/improvements/baseline_snapshot/**/*.csv`
  - all `outputs/improvements/tables/*.csv`

### Files that appear unused or only lightly used

- `OUTPUT_INVENTORY.csv` appears to be documentation-only. It is mentioned in `OUTPUT_REVIEW.md`, but no pipeline code reads it.
- `outputs/eda/tables/*.csv` are not model inputs; they support EDA and reporting only.
- `outputs/diagnostics/tables/figure_inventory.csv` and `outputs/diagnostics/tables/output_visualization_inventory.csv` are curation tables for figure planning, not model inputs.
- `*_feature_importance.csv`, `*_predictions.csv`, `*_fold_metrics.csv`, and many diagnostics tables are generated end products that are read later only by diagnostics/reporting, not by training.
- `outputs/improvements/baseline_snapshot/**/*.csv` are historical comparison artifacts used by `run_model_improvement_analysis.py`, not by the active modeling pipeline.

### Highest-priority schema issues found

- **`wire_area_loss_raw` is labeled as a percent in the Excel workbook but is treated as a fraction in code.**
  - Evidence: workbook column name is `Last_Wire_Area_Loss_(Faliure_Surface)_%`; `build_master_table()` copies it directly into `wire_area_loss_frac` and computes `wire_area_loss_pct = wire_area_loss_raw * 100.0`.
- **`treatment_coarse` is corrupted for the control condition because YAML parses `NO` as boolean `False`.**
  - Evidence: `configs/specimen_mapping.yaml` uses unquoted `NO`; `yaml.safe_load` in `src/corrosion_proxy_rul/config.py` converts it to boolean `False`; the resulting CSVs contain mixed values `False`, `MI`, `SA`, `PA`, etc.
- **`surface_total_rust_category` and `peak_rust_category` are preserved as ordinal labels, but the repository never decodes what category values `1`–`4` mean numerically.**
- **`peak_rust_location_cm` is clearly a length-axis location in centimeters, but the zero-reference direction is not documented in code.**

## 2. File-by-file analysis

Because the repository has 329 CSV files but only 70 unique header sets, repeated benchmark artifacts are audited by **schema family**. Every CSV path in the repository is covered by one of the file families below.

### File family: `OUTPUT_INVENTORY.csv`

**Purpose of this file**

- Manual inventory of output artifacts, their type, stage, and usefulness.
- Evidence: file contents; referenced in `OUTPUT_REVIEW.md`.

**Column dictionary**

- `file_path`
  - Meaning / interpretation: repository-relative path to an artifact.
  - Unit: none.
  - Data role: audit / inventory.
  - Evidence: row values are output paths.
  - Notes: documentation only; not consumed by pipeline code.
- `file_type`
  - Meaning / interpretation: artifact format such as `csv`, `png`, `md`.
  - Unit: none.
  - Data role: audit / inventory.
  - Evidence: row values.
- `stage_of_pipeline`
  - Meaning / interpretation: coarse stage label such as `audit`, `features`, `models`, `diagnostics`.
  - Unit: none.
  - Data role: audit / inventory.
  - Evidence: row values and stage names used elsewhere in repo.
- `brief_description`
  - Meaning / interpretation: free-text explanation of the artifact.
  - Unit: none.
  - Data role: audit / inventory.
- `status`
  - Meaning / interpretation: subjective usefulness label such as `useful`.
  - Unit: none.
  - Data role: audit / inventory.

**Important observations**

- This file documents outputs; it is not authoritative for schema semantics.
- It appears unused by the modeling code.

### File family: `outputs/audit/metadata_loaded.csv`

**Purpose of this file**

- Direct workbook export after column renaming through `EXCEL_COLUMN_MAP` in `src/corrosion_proxy_rul/data_loading.py`.
- This is the closest CSV to the source Excel sheet and has no parsed filename fields or mapping metadata yet.

**Column dictionary**

- `sample_name`
  - Meaning: workbook row key in `specimen-date-weekW` form.
  - Unit: none.
  - Data role: identifier.
  - Evidence: workbook column `Sample Name`; parsed later by `parse_sample_name()`.
- `specimen_id`
  - Meaning: specimen identifier from workbook `ID`.
  - Unit: none.
  - Data role: identifier.
  - Evidence: workbook `ID`; validated against parsed `sample_name`.
- `n_steel_mesh_raw`
  - Meaning: original mesh-count field from workbook.
  - Unit: count of steel meshes.
  - Data role: metadata / raw source.
  - Evidence: workbook `N_Steel_Mesh`; cast later to integer `n_steel_mesh`.
- `treatment_raw`
  - Meaning: original treatment code from workbook.
  - Unit: none.
  - Data role: metadata / raw source.
  - Evidence: workbook `Treatment`.
  - Notes: raw codes are not decoded further in code except alongside mapped treatment fields.
- `treatment_label_raw`
  - Meaning: original workbook label for treatment.
  - Unit: none.
  - Data role: metadata / raw source.
  - Evidence: workbook `Label_Treatment`.
  - Notes: exact semantics of each code are only partially recoverable from the repo.
- `ageing_days`
  - Meaning: exposure duration in days.
  - Unit: days.
  - Data role: temporal metadata / raw source.
  - Evidence: workbook `Ageing Days`; validated against `week * 7`.
- `surface_total_rust_pct`
  - Meaning: surface total rust percentage from workbook.
  - Unit: percent.
  - Data role: target / raw source.
  - Evidence: workbook `A_Surface_Total_Rust_Percentage[%]`.
- `surface_total_rust_category`
  - Meaning: ordinal category of total rust.
  - Unit: category code `1`–`4`.
  - Data role: target-related / raw source.
  - Evidence: workbook `A_Total_Rust_Category_(1–4)`.
  - Notes: category thresholds are not defined in code.
- `peak_rust_pct`
  - Meaning: peak local rust percentage from workbook.
  - Unit: percent.
  - Data role: target / raw source.
  - Evidence: workbook `B_Peak_Rust_Percentage_[%]`.
- `peak_rust_category`
  - Meaning: ordinal category of peak rust severity.
  - Unit: category code `1`–`4`.
  - Data role: target-related / raw source.
  - Evidence: workbook `B_Peak_Rust_Category_(1–4)`.
- `peak_rust_location_cm`
  - Meaning: location of peak rust along specimen length.
  - Unit: centimeters.
  - Data role: target / raw source.
  - Evidence: workbook `B_Location_of_Peak_Rus_ in_length_[cm]`.
  - Notes: code never documents which end is 0 cm.
- `cover_mm_raw`
  - Meaning: cover depth measured at failure surface.
  - Unit: millimeters.
  - Data role: metadata / raw source.
  - Evidence: workbook `Cover_(Faliure_Surface)_[mm]`.
- `wire_area_loss_raw`
  - Meaning: raw structural loss value from workbook.
  - Unit: **ambiguous**. Workbook label says percent, code treats it as fraction.
  - Data role: target / raw source.
  - Evidence: workbook `%` label; `build_master_table()` copies it to `wire_area_loss_frac` and multiplies by 100 for `wire_area_loss_pct`.
  - Notes: this is a critical unit inconsistency.
- `ultimate_load_kn`
  - Meaning: ultimate load from destructive / structural test.
  - Unit: kilonewtons.
  - Data role: target / raw source.
  - Evidence: workbook `Ultimate_Load_[kN]`.

**Important observations**

- This file preserves workbook semantics better than later merged tables.
- It is the best place to see the raw corrosion / structural labels before any parsing or mapping.

### File family: `outputs/audit/image_scan.csv`

**Purpose of this file**

- PNG-directory scan created by `scan_image_directory()` in `src/corrosion_proxy_rul/data_loading.py`.

**Column dictionary**

- `image_filename`: PNG filename including extension. Unit none. Role identifier / file metadata. Evidence: `path.name`.
- `sample_name`: filename stem used to match workbook rows. Unit none. Role identifier. Evidence: `path.stem`.
- `image_path`: repository-relative path to PNG. Unit none. Role file metadata. Evidence: `str(path)`.
- `image_readable`: whether `PIL.Image.open` succeeded. Unit boolean. Role audit / QA flag.
- `image_width`: pixel width of PNG. Unit pixels. Role audit / image metadata.
- `image_height`: pixel height of PNG. Unit pixels. Role audit / image metadata.
- `image_error`: exception text if the file could not be opened. Unit none. Role audit / QA log.

**Important observations**

- This file documents one unreadable orphan image, `E01-20240508-17W.png`.
- Width and height later flow into `master_table.csv`.

### File family: `outputs/audit/specimen_mapping_validated.csv`

**Purpose of this file**

- Flattened specimen-level mapping from `configs/specimen_mapping.yaml`, produced by `mapping_to_dataframe()` and validated by `validate_mapping()`.

**Column dictionary**

- `specimen_id`: canonical specimen key. Unit none. Role identifier.
- `campaign_id`: reconstructed campaign label such as `campaign_1` or `campaign_2`. Unit none. Role metadata.
- `series_id`: reconstructed series label such as `S1`, `D`, `E`. Unit none. Role metadata.
- `split_group_treatment`: treatment-group label used by leave-one-treatment-out splits. Unit none. Role split metadata.
- `treatment_protocol`: descriptive treatment protocol string. Unit none. Role metadata.
- `treatment_coarse`: coarse treatment code. Unit none. Role metadata.
  - Notes: control rows are stored as boolean `False` instead of string `NO` because of YAML coercion.
- `treatment_label_coarse`: coarser label used in thesis-style grouping. Unit none. Role metadata.
- `n_steel_mesh`: integer mesh count reconstructed from specimen mapping. Unit count. Role metadata.
- `nacl_pct`: chloride concentration for the campaign / specimen design. Unit percent.
- `terminal_week`: planned terminal week for the specimen design. Unit weeks.
- `terminal_days`: planned terminal exposure in days. Unit days.

**Important observations**

- This file is specimen-level, not observation-level.
- `treatment_coarse` mixed typing is a real data-quality issue inherited from YAML parsing.

### File family: `outputs/audit/issues_log.csv`

**Purpose of this file**

- Explicit validation issues emitted by `build_master_table()`, `parse_metadata_fields()`, and schema-validation helpers.

**Column dictionary**

- `issue_type`: machine-readable issue label such as `orphan_image`, `missing_image_for_workbook_row`, `week_ageing_day_mismatch`. Unit none. Role audit.
- `severity`: severity label such as `warning` or `error`. Unit none. Role audit.
- `sample_name`: affected sample, if applicable. Unit none. Role identifier / audit.
- `detail`: free-text explanation. Unit none. Role audit.

**Important observations**

- The current run shows one orphan unreadable image and no other fatal audit issues.
- Some issue rows may omit columns beyond the canonical four because helper functions in `schema_validation.py` sometimes add a `column` field before concatenation; downstream CSV currently materializes the four main columns.

### File family: `outputs/data/master_table.csv` and `outputs/data/terminal_structural_table.csv`

**Purpose of this file**

- `master_table.csv`: canonical aligned observation-level dataset after workbook parsing, specimen mapping, and image matching.
- `terminal_structural_table.csv`: filtered subset where `has_structural_label == True`, produced by `build_terminal_structural_subset()`.

**Column dictionary**

- `sample_name`: canonical observation key; also becomes `observation_id`. Unit none. Role identifier. Evidence: workbook + `build_master_table()`.
- `specimen_id`: specimen key from workbook. Unit none. Role identifier.
- `n_steel_mesh_raw`: raw workbook mesh count. Unit count. Role raw metadata.
- `treatment_raw`: raw workbook treatment code. Unit none. Role raw metadata.
- `treatment_label_raw`: raw workbook treatment label. Unit none. Role raw metadata.
- `ageing_days`: exposure duration. Unit days. Role temporal metadata.
- `surface_total_rust_pct`: total visible rust percentage. Unit percent. Role target.
- `surface_total_rust_category`: ordinal total-rust category from workbook. Unit category code. Role target-related.
- `peak_rust_pct`: peak local rust percentage. Unit percent. Role target.
- `peak_rust_category`: ordinal peak-rust category. Unit category code. Role target-related.
- `peak_rust_location_cm`: peak rust location along specimen length. Unit cm. Role target / spatial label.
- `cover_mm_raw`: raw cover depth. Unit mm. Role raw metadata.
- `wire_area_loss_raw`: raw internal-loss value from workbook. Unit ambiguous: workbook says percent; code treats it as fraction. Role raw target.
- `ultimate_load_kn`: structural ultimate load. Unit kN. Role target.
- `specimen_id_from_name`: specimen ID parsed from `sample_name`. Unit none. Role parsed identifier.
- `date`: date token extracted from `sample_name` in `YYYYMMDD` string form. Unit calendar date string. Role parsed temporal metadata.
- `week`: week token extracted from `sample_name`. Unit weeks. Role parsed temporal metadata.
- `calendar_date`: parsed timestamp from `date`. Unit date / datetime. Role parsed temporal metadata.
- `campaign_id`: mapped campaign. Unit none. Role derived metadata.
- `series_id`: mapped series. Unit none. Role derived metadata.
- `split_group_treatment`: mapped treatment grouping used for split generation. Unit none. Role split metadata.
- `treatment_protocol`: mapped descriptive treatment protocol. Unit none. Role derived metadata.
- `treatment_coarse`: mapped coarse treatment code. Unit none. Role derived metadata.
  - Notes: control rows are `False` instead of `NO`.
- `treatment_label_coarse`: mapped coarse treatment label. Unit none. Role derived metadata.
- `n_steel_mesh`: integer-cast mesh count used by modeling. Unit count. Role cleaned metadata.
- `nacl_pct`: mapped NaCl concentration. Unit percent. Role derived experimental-condition metadata.
- `terminal_week`: mapped terminal week for the specimen design. Unit weeks. Role derived metadata.
- `terminal_days`: mapped terminal days for the specimen design. Unit days. Role derived metadata.
- `image_filename`: matched PNG filename. Unit none. Role file metadata.
- `image_path`: matched PNG path. Unit none. Role file metadata.
- `image_readable`: whether matched PNG opened successfully. Unit boolean. Role audit / file metadata.
- `image_width`: matched PNG width. Unit pixels. Role file metadata.
- `image_height`: matched PNG height. Unit pixels. Role file metadata.
- `image_error`: image-open error text if any. Unit none. Role audit.
- `observation_id`: alias of `sample_name`. Unit none. Role identifier.
- `wire_area_loss_frac`: direct copy of `wire_area_loss_raw`. Unit fraction according to code. Role derived target.
- `wire_area_loss_pct`: `wire_area_loss_raw * 100.0`. Unit percent. Role derived target.
- `cover_mm`: direct copy of `cover_mm_raw`. Unit mm. Role cleaned metadata.
- `has_structural_label`: whether either `wire_area_loss_frac` or `ultimate_load_kn` is non-null. Unit boolean. Role flag / target availability.
- `is_terminal_structural_row`: currently equal to `has_structural_label`. Unit boolean. Role flag.

**Important observations**

- `terminal_structural_table.csv` does not introduce new columns; it is a row filter on this schema.
- The table mixes raw workbook fields, parsed filename fields, mapped design metadata, and image linkage metadata in one place.
- `wire_area_loss_raw` / `wire_area_loss_frac` / `wire_area_loss_pct` are the most important unit-risk trio in the repo.

### File family: split manifests and split summaries

**Files covered**

- `outputs/splits/master_*.csv`
- `outputs/splits/master_*_summary.csv`
- `outputs/models/surface/splits/*.csv`
- `outputs/models/surface/splits/*_summary.csv`
- `outputs/models/hidden_damage/splits/*.csv`
- `outputs/models/hidden_damage/splits/*_summary.csv`
- `outputs/improvements/baseline_snapshot/models/hidden_damage/splits/*.csv`
- `outputs/improvements/baseline_snapshot/models/hidden_damage/splits/*_summary.csv`

**Purpose of this file**

- Row-wise split membership manifests and derived split-size summaries created by `build_split_manifests()` and `split_summary()` in `src/corrosion_proxy_rul/splits.py`.
- `outputs/splits/master_*` are based on `master_table.csv`.
- `outputs/models/surface/splits/*` are based on the surface feature table.
- `outputs/models/hidden_damage/splits/*` are based on the hidden-damage subset.

**Column dictionary: manifests (`*.csv`)**

- `sample_name`: row key assigned to train or test. Unit none. Role identifier.
- `specimen_id`: specimen corresponding to `sample_name`. Unit none. Role identifier / leakage-check key.
- `group_value`: grouping value actually used for the split.
  - For `group_shuffle`, this is `specimen_id`.
  - For `leave_one_treatment_out`, this is `split_group_treatment`.
  - For `leave_one_campaign_out`, this is `campaign_id`.
- `strategy`: split strategy name. Unit none. Role split metadata.
- `split_id`: concrete fold identifier such as `gss_0` or `leave_one_campaign_out_1`. Unit none. Role split metadata.
- `membership`: `train` or `test`. Unit none. Role split metadata.

**Column dictionary: summaries (`*_summary.csv`)**

- `strategy`: split strategy name. Role split metadata.
- `split_id`: fold identifier. Role split metadata.
- `train_rows`: number of train rows. Unit count. Role audit / split summary.
- `test_rows`: number of test rows. Unit count. Role audit / split summary.
- `train_specimens`: number of unique train specimens. Unit count. Role audit / split summary.
- `test_specimens`: number of unique test specimens. Unit count. Role audit / split summary.
- `leakage_detected`: whether a specimen appears in both train and test. Unit boolean. Role QA flag.

**Important observations**

- The schema is identical across master, surface, hidden-damage, and baseline-snapshot split tables; only the source population differs.
- `group_value` is semantically overloaded by strategy and should always be read with `strategy`.

### File family: `outputs/features/feature_dictionary.csv`

**Purpose of this file**

- Human-readable dictionary for deterministic image features created by `feature_dictionary()` in `src/corrosion_proxy_rul/image_features.py`.

**Column dictionary**

- `feature_name`: exact image-feature column name. Unit none. Role documentation.
- `description`: one-line definition from extraction code. Unit none. Role documentation.

**Important observations**

- This file is the most authoritative source for image-feature names, but some descriptions are still short and do not state units explicitly.

### File family: `outputs/features/image_features.csv`

**Purpose of this file**

- Deterministic image-feature table built by `extract_image_feature_table()` from `master_table.csv` and PNGs.

**Column dictionary**

- Color / mask percentages:
  - `img_rust_area_ratio_pct`: percentage of pixels in rust mask. Unit percent. Role engineered feature. Evidence: `100.0 * rust_mask.mean()`.
  - `img_black_mask_ratio_pct`: percentage of pixels in black mask. Unit percent. Role engineered feature.
  - `img_gray_mask_ratio_pct`: percentage of pixels in gray mask. Unit percent. Role engineered feature.
- Grayscale intensity:
  - `img_brightness_mean`: mean grayscale intensity. Unit intensity level on 0–255 grayscale scale.
  - `img_brightness_std`: standard deviation of grayscale intensity. Unit intensity level.
  - `img_brightness_p10`: 10th percentile grayscale intensity. Unit intensity level.
  - `img_brightness_p90`: 90th percentile grayscale intensity. Unit intensity level.
  - `img_contrast`: exact duplicate of `img_brightness_std`. Unit intensity level.
- RGB channel moments:
  - `img_r_mean`, `img_g_mean`, `img_b_mean`: mean channel intensities. Unit 0–255 channel value.
  - `img_r_std`, `img_g_std`, `img_b_std`: channel standard deviations. Unit channel value.
- Histogram bins:
  - `img_gray_hist_bin_0` ... `img_gray_hist_bin_7`: normalized grayscale histogram densities across 8 equal-width bins from 0 to 256.
  - Unit: density / relative frequency, not percent.
  - Evidence: `np.histogram(..., density=True)`.
- Texture:
  - `img_glcm_contrast`: gray-level co-occurrence contrast on downsampled grayscale image. Unit unitless texture statistic.
  - `img_glcm_homogeneity`: GLCM homogeneity. Unit unitless.
  - `img_glcm_energy`: GLCM energy. Unit unitless.
  - `img_lbp_mean`: mean local binary pattern value. Unit unitless descriptor.
  - `img_lbp_std`: standard deviation of LBP values. Unit unitless descriptor.
- Rust-blob morphology:
  - `img_rust_blob_count`: number of connected rust components. Unit count.
  - `img_rust_blob_largest_ratio_pct`: largest rust component area divided by full image area, times 100. Unit percent of image area.
  - `img_rust_blob_mean_ratio_pct`: mean rust-component area divided by full image area, times 100. Unit percent.
  - `img_rust_blob_eccentricity_mean`: mean component eccentricity. Unit unitless, range 0–1.
  - `img_rust_blob_eccentricity_max`: maximum component eccentricity. Unit unitless.
- Strip-wise spatial summaries:
  - `img_strip_count`: number of overlapping longitudinal strips. Unit count.
  - `img_strip_rust_mean_pct`: mean rust percentage across strips. Unit percent.
  - `img_strip_rust_std_pct`: standard deviation of strip rust percentages. Unit percentage points.
  - `img_strip_rust_max_pct`: maximum strip rust percentage. Unit percent.
  - `img_strip_rust_p90_pct`: 90th percentile strip rust percentage. Unit percent.
  - `img_strip_high_count`: number of strips with rust percentage at or above `high_rust_strip_threshold_pct` (5.0). Unit count.
  - `img_strip_peak_location_cm`: center location of highest-rust strip. Unit cm along 24 cm nominal specimen length.
  - `img_rust_center_of_mass_cm`: center of mass of rust intensity along specimen length. Unit cm.
  - `img_edge_to_center_rust_ratio`: mean edge-strip rust divided by mean center-strip rust, with `1e-6` stabilization. Unit unitless ratio.
- Identifier carry-through:
  - `sample_name`: observation key inherited from `master_table.csv`.
  - `specimen_id`: specimen key inherited from `master_table.csv`.
  - `image_path`: PNG path inherited from `master_table.csv`.

**Important observations**

- The exact GIMP preprocessing from the thesis was not fully recovered; feature semantics are tied to the provided PNGs plus deterministic thresholds in `configs/features.yaml`.
- `img_strip_count` is constant by construction for current image geometry and is later excluded from modeling.
- `img_contrast` is a documented exact duplicate of `img_brightness_std`.

### File family: `outputs/features/image_feature_failures.csv`

**Purpose of this file**

- Failure log from image-feature extraction.

**Column dictionary**

- `sample_name`: affected observation key. Role identifier.
- `specimen_id`: affected specimen. Role identifier.
- `image_path`: path of failed PNG. Role file metadata.
- `error`: exception text. Role audit / QA.

**Important observations**

- The current file is empty, which means no image-feature extraction failures occurred on the aligned master table.

### File family: merged feature tables

**Files covered**

- `outputs/data/full_feature_table.csv`
- `outputs/models/surface/surface_feature_table.csv`
- `outputs/models/hidden_damage/hidden_damage_feature_table.csv`
- `outputs/improvements/baseline_snapshot/models/hidden_damage/hidden_damage_feature_table.csv`

**Purpose of this file**

- `full_feature_table.csv`: `master_table.csv` plus image features merged by `sample_name`.
- `surface_feature_table.csv`: same merged schema, saved for the surface stage.
- `hidden_damage_feature_table.csv`: same merged schema restricted to rows with structural labels (`has_structural_label == True`).

**Column dictionary**

- All columns from `master_table.csv` recur unchanged with the same meaning.
- All columns from `image_features.csv` recur unchanged with the same meaning.
- No additional columns are introduced in these four tables.

**Important observations**

- These files are stage-specific views over the same merged schema, not separate feature definitions.
- `hidden_damage_feature_table.csv` is the 48-row structural subset used by the hidden-damage stage.
- Leakage / shortcut risk exists because visible-corrosion targets and image rust-area features are extremely similar, and because mapped campaign / treatment metadata are present alongside image features.

### File family: `outputs/models/surface/best_models.csv`

**Purpose of this file**

- Per-target winner table from `run_surface_models()` in `src/corrosion_proxy_rul/models_surface.py`.

**Column dictionary**

- `target`: surface target name, either `surface_total_rust_pct` or `peak_rust_pct`. Role target metadata.
- `best_model_name`: selected winner under grouped benchmark summary. Role model-selection output.
- `benchmark_note`: hard-coded interpretation note from `SURFACE_TARGET_NOTES`.
  - `surface_total_rust_pct`: `label_reconstruction_sanity_check`
  - `peak_rust_pct`: `surface_benchmark_with_related_strip_features`

**Important observations**

- This file is intentionally interpretive, not just numeric.
- It is used by reporting scripts to frame the surface stage conservatively.

### File family: surface evaluation outputs

**Files covered**

- `outputs/models/surface/*/{group_shuffle,leave_one_treatment_out,leave_one_campaign_out}/*_fold_metrics.csv`
- `outputs/models/surface/*/{group_shuffle,leave_one_treatment_out,leave_one_campaign_out}/*_predictions.csv`
- `outputs/models/surface/*/{group_shuffle,leave_one_treatment_out,leave_one_campaign_out}/*_summary.csv`
- `outputs/models/surface/*/{group_shuffle,leave_one_treatment_out,leave_one_campaign_out}/*_feature_importance.csv`

**Purpose of this file**

- Benchmark outputs from `benchmark_models()` for the surface stage.

**Column dictionary: `*_fold_metrics.csv`**

- `target`: target variable name. Unit none. Role target metadata.
- `model_name`: regressor name (`RandomForest`, `GradientBoosting`, `XGBoost`, `CatBoost`). Role model metadata.
- `split_id`: fold identifier. Role split metadata.
- `mae`: mean absolute error on original target scale. Unit same as target.
- `rmse`: root mean squared error on original target scale. Unit same as target.
- `r2`: coefficient of determination. Unitless.
- `spearman`: Spearman rank correlation between truth and prediction. Unitless.

**Column dictionary: `*_predictions.csv`**

- `target`, `model_name`, `split_id`: as above.
- `sample_name`: held-out observation key. Role identifier.
- `y_true`: held-out target value on original scale.
- `y_pred`: held-out prediction on original scale.

**Column dictionary: `*_summary.csv`**

- `target`, `model_name`: as above.
- `mae_mean`, `mae_std`: mean and standard deviation of fold MAE.
- `rmse_mean`, `rmse_std`: mean and standard deviation of fold RMSE.
- `r2_mean`, `r2_std`: mean and standard deviation of fold R².
- `spearman_mean`, `spearman_std`: mean and standard deviation of fold Spearman.

**Column dictionary: `*_feature_importance.csv`**

- `feature`: one-hot encoded feature name used by the fitted winner model.
- `importance`: model-native importance score.

**Important observations**

- Surface outputs do **not** include `target_transform` because the surface stage does not transform targets.
- Feature-importance tables use dummy-encoded columns, so categorical variables may expand into multiple `feature` rows.
- `surface_total_rust_pct` is explicitly treated as a sanity-check target rather than a substantive hidden-damage result.

### File family: hidden-damage evaluation outputs

**Files covered**

- Current experiment and final files:
  - `outputs/models/hidden_damage/**/*.csv`
- Historical baseline snapshot with matching evaluation schemas:
  - `outputs/improvements/baseline_snapshot/models/hidden_damage/**/*.csv`

**Purpose of this file**

- Structural benchmark outputs from `benchmark_models()` for `wire_area_loss_frac` and `ultimate_load_kn`.

**Column dictionary: current `*_fold_metrics.csv`**

- `target`: structural target name.
- `model_name`: regressor name.
- `target_transform`: target transform used during training (`none` or `sqrt` for `wire_area_loss_frac`; `none` for `ultimate_load_kn`).
- `split_id`: fold identifier.
- `mae`, `rmse`, `r2`, `spearman`: fold metrics on the **inverse-transformed original scale**.
  - Evidence: `predict_model_bundle()` inverse-transforms predictions before metrics are computed.

**Column dictionary: current `*_predictions.csv`**

- `target`, `model_name`, `target_transform`, `split_id`: as above.
- `sample_name`: held-out observation.
- `y_true`: true target value on original scale.
- `y_pred`: predicted target value on original scale.

**Column dictionary: current `*_summary.csv`**

- `target`, `model_name`, `target_transform`: as above.
- `mae_mean`, `mae_std`, `rmse_mean`, `rmse_std`, `r2_mean`, `r2_std`, `spearman_mean`, `spearman_std`: aggregate metrics across folds.

**Column dictionary: `*_feature_importance.csv`**

- `feature`: one-hot encoded feature name used by fitted selected model.
- `importance`: model-native importance score.

**Important observations**

- The current hidden-damage family carries `target_transform`; baseline snapshot files often do not, because the baseline pre-dated the transform-aware comparison logic.
- Current selected models for both structural targets use `metadata_only` features, which is documented in `best_models.csv` and `*_selected_features.csv`.

### File family: hidden-damage selection and feature-space tables

**Files covered**

- `outputs/models/hidden_damage/hidden_damage_feature_table.csv`
- `outputs/models/hidden_damage/hidden_damage_experiment_summary.csv`
- `outputs/models/hidden_damage/hidden_damage_feature_inventory.csv`
- `outputs/models/hidden_damage/hidden_damage_feature_ablation_results.csv`
- `outputs/models/hidden_damage/hidden_damage_campaign_confounding.csv`
- `outputs/models/hidden_damage/hidden_damage_robustness_selection.csv`
- `outputs/models/hidden_damage/hidden_damage_selected_feature_list.csv`
- `outputs/models/hidden_damage/best_models.csv`
- `outputs/models/hidden_damage/*/*_feature_inventory.csv`
- `outputs/models/hidden_damage/*/*_selected_features.csv`

**Purpose of this file**

- These files document how the structural feature space was cleaned, compared, ranked, and finally selected.

**Column dictionary: `hidden_damage_experiment_summary.csv`**

- `target`: structural target.
- `model_name`: model family.
- `target_transform`: target transform.
- metric columns: `mae_mean`, `mae_std`, `rmse_mean`, `rmse_std`, `r2_mean`, `r2_std`, `spearman_mean`, `spearman_std`.
- `strategy`: split strategy.
- `feature_set_name`: one of `all_cleaned`, `image_time_only`, `image_only`, `metadata_only`.
- `feature_set_description`: human-readable explanation from `HIDDEN_DAMAGE_FEATURE_SETS`.
- `n_features`: number of selected features in that feature-set realization.
- `selection_candidate`: whether the feature set is allowed into final robustness selection.

**Column dictionary: `hidden_damage_feature_inventory.csv`**

- `target`: structural target.
- `n_selected_features`: count of features retained for that `target` and `feature_set_name`.
- `selection_candidate`: whether that feature set participates in deployment selection.
- `feature_set_name`: feature-set family.
- `source_family`: `temporal`, `tabular_metadata`, `image_mask`, `image_texture`, etc.
- `candidate_feature`: whether the feature belonged to the feature-set candidate pool before cleanup.
- `set_description`: feature-set description.
- `feature_name`: exact column name under consideration.
- `action`: `keep` or `exclude`.
- `reason`: cleanup reason such as constant, near-constant, duplicate, highly collinear, or retained.
- `reference_feature`: duplicate / collinearity reference feature if exclusion depends on another column.

**Column dictionary: target-specific `*_feature_inventory.csv`**

- Same meaning as `hidden_damage_feature_inventory.csv` but restricted to the single selected feature-set for one target.
- Columns: `feature_set_name`, `source_family`, `candidate_feature`, `set_description`, `feature_name`, `action`, `reason`, `reference_feature`, `target`.

**Column dictionary: `*_selected_features.csv` and `hidden_damage_selected_feature_list.csv`**

- `target`: structural target.
- `feature_name`: retained feature used by the final model.
- `feature_set_name`: selected feature-set family.
- `target_transform`: selected transform.
- `source_family`: feature family assigned by cleanup logic.

**Column dictionary: `hidden_damage_feature_ablation_results.csv`**

- Same metric fields as `hidden_damage_experiment_summary.csv`, but reduced to the best row per `target + feature_set_name + strategy`.
- Purpose: compare feature-set families rather than every model row.

**Column dictionary: `hidden_damage_campaign_confounding.csv`**

- All columns from `hidden_damage_feature_ablation_results.csv`, plus:
  - `all_cleaned_mae_mean`
  - `all_cleaned_spearman_mean`
  - `delta_mae_vs_all_cleaned`
  - `delta_spearman_vs_all_cleaned`
- Meaning: compare each feature-set family against the `all_cleaned` baseline for the same `target + strategy`.

**Column dictionary: `hidden_damage_robustness_selection.csv`**

- `target`, `feature_set_name`, `model_name`, `target_transform`, `n_features`: candidate configuration identity.
- `mae_mean_group_shuffle`, `mae_mean_leave_one_campaign_out`, `mae_mean_leave_one_treatment_out`: per-strategy MAE means.
- `r2_mean_*`, `rmse_mean_*`, `spearman_mean_*`: per-strategy aggregate metrics.
- `mae_rank_group_shuffle`, `mae_rank_leave_one_treatment_out`, `mae_rank_leave_one_campaign_out`: rank positions used in robustness score.
- `spearman_rank_group_shuffle`: grouped Spearman rank used in robustness score.
- `robustness_score`: weighted sum defined in `configs/modeling.yaml`.
- `selected_for_deployment`: final boolean winner flag.

**Column dictionary: `best_models.csv`**

- `target`: structural target.
- `best_model_name`: selected model family.
- `feature_set_name`: selected feature set.
- `target_transform`: selected transform.
- `n_features`: number of selected features.
- `robustness_score`: selection score from robustness table.
- `group_shuffle_mae_mean`, `leave_one_treatment_out_mae_mean`, `leave_one_campaign_out_mae_mean`: selected-model MAE means.
- `group_shuffle_spearman_mean`: grouped Spearman of selected model.

**Important observations**

- The hidden-damage stage is the richest source of feature-selection metadata in the repo.
- Target-specific selected-feature files prove that the final current structural models use only metadata columns, not image features.

### File family: degradation outputs

**Files covered**

- `outputs/models/degradation/full_feature_table_with_hidden_damage_proxy.csv`
- `outputs/models/degradation/degradation_fit_candidates.csv`
- `outputs/models/degradation/degradation_best_fits.csv`
- `outputs/models/degradation/degradation_trajectory_grid.csv`
- `outputs/models/degradation/degradation_raw_vs_monotone_proxy.csv`
- matching diagnostics copies under `outputs/diagnostics/tables/`
- baseline snapshot historical equivalents under `outputs/improvements/baseline_snapshot/models/degradation/`

**Purpose of this file**

- Downstream proxy-degradation stage built in `src/corrosion_proxy_rul/models_degradation.py`.

**Column dictionary: `full_feature_table_with_hidden_damage_proxy.csv`**

- All columns from `full_feature_table.csv` recur unchanged.
- Current file adds:
  - `raw_predicted_wire_area_loss_frac`: clipped row-level hidden-damage model prediction before monotone accumulation. Unit fraction.
  - `predicted_wire_area_loss_frac`: currently initialized equal to `raw_predicted_wire_area_loss_frac`; later used as observed proxy signal. Unit fraction.
- Historical baseline snapshot version only adds `predicted_wire_area_loss_frac`; it predates explicit `raw_predicted_wire_area_loss_frac`.

**Column dictionary: `degradation_fit_candidates.csv`**

- `specimen_id`: specimen being fitted.
- `family`: candidate curve family (`linear`, `log_time`, `logistic`, `gompertz`, `monotone_isotonic`).
- `criterion`: BIC-like selection criterion from `_bic_like()`.
- `rmse`: fit RMSE against monotone proxy.
- `fit_succeeded`: whether the family fit completed successfully.
- `params`: JSON-encoded fitted parameters or error payload.

**Column dictionary: `degradation_best_fits.csv`**

- `specimen_id`: specimen key.
- `best_family`: selected family with lowest finite criterion.
- `criterion`: winning criterion value.
- `best_model_name`: hidden-damage model used upstream to generate the proxy.
- `hidden_damage_feature_set_name`: upstream hidden-damage feature-set name.
- `hidden_damage_target_transform`: upstream target transform.
- `last_observed_day`: final observed ageing day for this specimen.
- `last_observed_predicted_wire_area_loss_frac`: final monotone proxy value at the last observed day.
- `params`: JSON-encoded parameters of the winning curve family.
- Historical baseline snapshot version lacks `hidden_damage_feature_set_name` and `hidden_damage_target_transform`.

**Column dictionary: `degradation_trajectory_grid.csv`**

- `specimen_id`: specimen key.
- `day`: grid day from 0 to 365 with step 1.
- `predicted_wire_area_loss_frac`: fitted degradation-curve value at that day.
- `best_family`: family used for that specimen's fitted curve.

**Column dictionary: `degradation_raw_vs_monotone_proxy.csv`**

- `specimen_id`: specimen key.
- `ageing_days`: observed day points only.
- `raw_predicted_wire_area_loss_frac`: row-level hidden-damage prediction before monotonicity enforcement.
- `monotone_proxy_wire_area_loss_frac`: cumulative-maximum version used for fitting.

**Important observations**

- Degradation uses model-predicted hidden damage, not directly observed structural sequences.
- Current schema explicitly separates raw and monotone proxy; historical baseline schema is thinner.

### File family: proxy-RUL outputs

**Files covered**

- `outputs/models/proxy_rul/proxy_rul_estimates.csv`
- `outputs/models/proxy_rul/proxy_rul_summary.csv`
- diagnostics copies under `outputs/diagnostics/tables/`
- baseline snapshot historical equivalents under `outputs/improvements/baseline_snapshot/models/proxy_rul/`

**Purpose of this file**

- Threshold-status analysis over fitted degradation curves, produced by `run_proxy_rul()` in `src/corrosion_proxy_rul/models_rul_proxy.py`.

**Column dictionary: `proxy_rul_estimates.csv`**

- `specimen_id`: specimen key.
- `best_family`: degradation family used upstream for that specimen.
- `threshold_wire_area_loss_frac`: threshold value evaluated, from `configs/thresholds.yaml` (`0.20`, `0.30`, `0.40`).
- `last_observed_day`: final observed day for specimen.
- `last_observed_predicted_wire_area_loss_frac`: proxy value at final observed day.
- `estimated_crossing_day`: first day in the fitted grid where threshold is reached, if any.
- `proxy_rul_days`: `estimated_crossing_day - last_observed_day` only when crossing occurs after observation window; otherwise null by design.
- `right_censored`: whether threshold is not reached within 365-day horizon.
- `threshold_reached_by_baseline`: whether threshold is already crossed at day 0.
- `threshold_reached_by_last_observation`: whether threshold is crossed by the last observed day.
- `threshold_crossed_during_observation`: crossed after day 0 but before or at last observed day.
- `future_crossing_within_horizon`: crossed after last observation but before 365-day horizon.
- `threshold_status`: categorical label derived from the previous booleans.
- `projection_horizon_days`: projection horizon, currently 365.

**Column dictionary: `proxy_rul_summary.csv`**

- `threshold_wire_area_loss_frac`: threshold value.
- `n_specimens`: number of specimens summarized.
- `n_crossed_by_baseline`, `n_crossed_during_observation`, `n_future_crossings_within_horizon`, `n_right_censored`: count summaries.
- `n_crossed_by_last_observation`: baseline + during-observation crossings.
- `frac_crossed_by_baseline`, `frac_crossed_during_observation`, `frac_crossed_by_last_observation`, `frac_future_crossings_within_horizon`, `frac_right_censored`: counts divided by `n_specimens`.
- Historical baseline snapshot summary has only count columns, not the derived fractions.

**Important observations**

- Current run yields null `proxy_rul_days` for all rows because there are no future threshold crossings within horizon.
- The column name `proxy_rul_days` should be read as a conditional future-crossing interval, not a universally available RUL label.

### File family: EDA tables

**Files covered**

- `outputs/eda/tables/row_counts.csv`
- `outputs/eda/tables/campaign_counts.csv`
- `outputs/eda/tables/treatment_counts.csv`
- `outputs/eda/tables/week_counts.csv`
- `outputs/eda/tables/missingness.csv`
- `outputs/eda/tables/specimen_summary.csv`
- `outputs/eda/tables/structural_target_sparsity.csv`

**Purpose of this file**

- Small descriptive summaries generated by `generate_eda()` in `src/corrosion_proxy_rul/eda.py`.

**Column dictionary**

- `row_counts.csv`
  - `entity`: one of `rows`, `unique_specimens`, `images_used`.
  - `count`: integer count.
- `campaign_counts.csv`
  - `campaign_id`: campaign label.
  - `count`: number of observations in that campaign.
- `treatment_counts.csv`
  - `split_group_treatment`: treatment-group label.
  - `count`: number of observations in that group.
- `week_counts.csv`
  - `week`: parsed exposure week.
  - `count`: number of observations at that week.
- `missingness.csv`
  - `column`: column name from `master_table.csv`.
  - `missing_count`: number of missing rows.
- `specimen_summary.csv`
  - `specimen_id`: specimen key.
  - `campaign_id`: first campaign value seen for that specimen.
  - `split_group_treatment`: first treatment-group value seen for specimen.
  - `min_day`, `max_day`: earliest and latest `ageing_days`.
  - `n_rows`: number of observations for specimen.
  - `has_structural_label`: whether any row for specimen has structural labels.
  - `final_surface_total_rust_pct`, `final_peak_rust_pct`: last observed values after sorting by `ageing_days`.
- `structural_target_sparsity.csv`
  - `target`: `wire_area_loss_frac` or `ultimate_load_kn`.
  - `non_null_rows`: number of non-null rows for that target in `master_table.csv`.

**Important observations**

- `specimen_summary.csv` uses `last` after sorting by day, so “final” means latest available row, not a mean.

### File family: diagnostics feature tables

**Files covered**

- `outputs/diagnostics/tables/feature_inventory_by_stage.csv`
- `outputs/diagnostics/tables/feature_missingness_summary.csv`
- `outputs/diagnostics/tables/feature_variance_summary.csv`
- `outputs/diagnostics/tables/near_constant_features.csv`
- `outputs/diagnostics/tables/duplicate_feature_pairs.csv`
- `outputs/diagnostics/tables/high_collinearity_pairs.csv`
- `outputs/diagnostics/tables/feature_target_correlation_summary.csv`
- matching baseline snapshot diagnostics copies where present

**Purpose of this file**

- Transparent feature-space audit built by `build_feature_diagnostic_tables()` in `src/corrosion_proxy_rul/diagnostics.py`.

**Column dictionary**

- `feature_inventory_by_stage.csv`
  - `stage`: `surface` or `hidden_damage`.
  - `feature_name`: column under review.
  - `source_family`: family label from `feature_family()`.
  - `data_type`: pandas dtype string.
  - `missing_count`, `missing_fraction`: missingness summary.
  - `nunique`: count of distinct non-null values.
  - `variance`: sample variance for numeric columns.
  - `top_value_fraction`: share occupied by most common value.
  - `included_in_stage`: whether modeling keeps this column.
  - `exclusion_reason`: reason if excluded.
- `feature_missingness_summary.csv`
  - `stage`, `feature_name`, `source_family`, `missing_count`, `missing_fraction`: subset of the inventory table.
- `feature_variance_summary.csv`
  - `stage`, `feature_name`, `source_family`, `data_type`, `variance`, `nunique`, `top_value_fraction`, `included_in_stage`.
- `near_constant_features.csv`
  - Same columns as `feature_variance_summary.csv`, but filtered to constant or near-constant rows.
- `duplicate_feature_pairs.csv`
  - `left_feature`, `right_feature`: exact duplicate numeric columns.
  - `duplicate_type`: currently `exact_duplicate`.
- `high_collinearity_pairs.csv`
  - `left_feature`, `right_feature`: highly correlated feature pair.
  - `spearman_abs_corr`: absolute Spearman correlation.
  - `spearman_corr`: signed Spearman correlation.
- `feature_target_correlation_summary.csv`
  - `target`: one of the four main targets.
  - `feature_name`: candidate numeric feature.
  - `source_family`: feature family.
  - `n_valid`: row count used for the correlation.
  - `spearman_corr`, `spearman_abs_corr`: target-feature Spearman correlation.

**Important observations**

- The diagnostics stage uses `full_feature_table.csv`, but for structural targets it drops rows with null targets before computing correlations.
- `treatment_coarse` appears as a metadata feature despite its `False` control-code inconsistency.

### File family: diagnostics distribution tables

**Files covered**

- `outputs/diagnostics/tables/variable_distribution_summary.csv`
- `outputs/diagnostics/tables/variable_percentile_summary.csv`
- `outputs/diagnostics/tables/outlier_summary.csv`
- `outputs/diagnostics/tables/exposure_band_summary.csv`

**Purpose of this file**

- Distribution and outlier diagnostics built from selected variables in `build_distribution_tables()` and `build_exposure_band_summary()`.

**Column dictionary**

- `variable_distribution_summary.csv`
  - `variable`: column name being summarized.
  - `label`: plotting label from `SELECTED_DISTRIBUTION_VARIABLES`.
  - `count`, `mean`, `std`, `min`, `q25`, `median`, `q75`, `p95`, `p99`, `max`: descriptive statistics on numeric values.
- `variable_percentile_summary.csv`
  - `variable`, `label`: as above.
  - `percentile`: numeric percentile in `[0.01, 0.99]`.
  - `value`: quantile value.
- `outlier_summary.csv`
  - `variable`, `label`: as above.
  - `iqr_upper_fence`: Tukey upper fence `q75 + 1.5 * IQR`.
  - `n_iqr_outliers`: count above that fence.
  - `n_above_p99`: count above the empirical 99th percentile.
  - `p99_value`: empirical 99th percentile.
  - `max_value`: maximum value.
- `exposure_band_summary.csv`
  - `exposure_band`: `early_exposure`, `mid_exposure`, `late_exposure`, based on tertiles of `ageing_days`.
  - For each of `surface_total_rust_pct`, `peak_rust_pct`, `img_rust_area_ratio_pct`, columns `{variable}_median`, `{variable}_mean`, `{variable}_count`.

**Important observations**

- Exposure bands are **data-driven tertiles**, not fixed week ranges.

### File family: diagnostics benchmark tables

**Files covered**

- `outputs/diagnostics/tables/benchmark_summary_long.csv`
- `outputs/diagnostics/tables/benchmark_fold_metrics_long.csv`
- `outputs/diagnostics/tables/split_summary_long.csv`
- `outputs/diagnostics/tables/benchmark_best_model_robustness.csv`
- matching baseline snapshot diagnostics copy of `benchmark_best_model_robustness.csv`

**Purpose of this file**

- Long-form benchmark tables built by `load_summary_long()` and `build_best_model_robustness()`.

**Column dictionary**

- `benchmark_summary_long.csv`
  - all columns from model `*_summary.csv`
  - plus `stage`, `strategy`, and for current hidden-damage rows `target_transform`
  - meaning: one row per stage + target + strategy + model summary.
- `benchmark_fold_metrics_long.csv`
  - all columns from model `*_fold_metrics.csv`
  - plus `stage`, `strategy`, and where present `target_transform`.
- `split_summary_long.csv`
  - split-summary columns (`strategy`, `split_id`, `train_rows`, `test_rows`, `train_specimens`, `test_specimens`, `leakage_detected`)
  - plus `stage` showing whether the split summary came from `master`, `surface`, or `hidden_damage`.
- `benchmark_best_model_robustness.csv`
  - `stage`: `surface` or `hidden_damage`.
  - `target`: target name.
  - `best_model_name`: best grouped model chosen as anchor.
  - `strategy`: evaluation strategy.
  - `mae_mean`, `mae_std`, `spearman_mean`, `spearman_std`: metrics for that best grouped model under each strategy.
  - `relative_mae_vs_group_shuffle`: `mae_mean / grouped_mae_mean` for same target and model.

**Important observations**

- `benchmark_best_model_robustness.csv` does not re-select a best model per strategy; it tracks the grouped winner across harder strategies.

### File family: diagnostics degradation tables

**Files covered**

- `outputs/diagnostics/tables/degradation_observed_vs_fitted.csv`
- `outputs/diagnostics/tables/degradation_fit_quality_summary.csv`
- `outputs/diagnostics/tables/degradation_grouped_by_campaign.csv`
- `outputs/diagnostics/tables/degradation_grouped_by_treatment.csv`
- `outputs/diagnostics/tables/degradation_best_fits.csv`
- `outputs/diagnostics/tables/degradation_candidates.csv`
- `outputs/diagnostics/tables/degradation_grid.csv`
- `outputs/diagnostics/tables/degradation_raw_vs_monotone_proxy.csv`

**Purpose of this file**

- Diagnostics copies and aggregations built from the current degradation outputs.

**Column dictionary**

- `degradation_observed_vs_fitted.csv`
  - `sample_name`, `specimen_id`, `campaign_id`, `split_group_treatment`, `ageing_days`: identifiers and grouping metadata.
  - `predicted_wire_area_loss_frac`: observed proxy at observed day.
  - `fitted_wire_area_loss_frac`: fitted curve value at the same day.
  - `best_family`: selected family for the specimen.
  - `residual`: observed proxy minus fitted curve.
- `degradation_fit_quality_summary.csv`
  - `family`: degradation family.
  - `n_success`: number of successful fits.
  - `rmse_mean`, `rmse_median`, `rmse_max`: RMSE summaries among successful fits.
  - `criterion_mean`: mean selection criterion among successful fits.
- `degradation_grouped_by_campaign.csv`
  - `campaign_id`: campaign label.
  - `day`: day on dense grid.
  - `predicted_wire_area_loss_frac`: median fitted curve value across specimens in that campaign.
- `degradation_grouped_by_treatment.csv`
  - `split_group_treatment`: treatment group.
  - `day`: day on dense grid.
  - `predicted_wire_area_loss_frac`: median fitted curve value across that group.
- `degradation_best_fits.csv`, `degradation_candidates.csv`, `degradation_grid.csv`, `degradation_raw_vs_monotone_proxy.csv`
  - Same meanings as the model-output counterparts described above.

**Important observations**

- Diagnostics tables are copies or derived summaries; the model outputs remain the authoritative source.

### File family: diagnostics proxy tables

**Files covered**

- `outputs/diagnostics/tables/proxy_estimates.csv`
- `outputs/diagnostics/tables/proxy_status_summary.csv`
- `outputs/diagnostics/tables/proxy_status_matrix.csv`

**Purpose of this file**

- Diagnostics copies and pivots built from current proxy outputs.

**Column dictionary**

- `proxy_estimates.csv`
  - Same schema and meaning as `outputs/models/proxy_rul/proxy_rul_estimates.csv`.
- `proxy_status_summary.csv`
  - Same schema and meaning as current `outputs/models/proxy_rul/proxy_rul_summary.csv`.
- `proxy_status_matrix.csv`
  - `specimen_id`: specimen key.
  - `0.2`, `0.3`, `0.4`: threshold-status strings for the corresponding thresholds.
  - Notes: these are wide pivoted columns whose names are threshold values represented as strings.

**Important observations**

- `proxy_status_matrix.csv` is convenient for heatmaps but awkward for general programmatic use because thresholds become column names.

### File family: diagnostics curation / inventory tables

**Files covered**

- `outputs/diagnostics/tables/figure_inventory.csv`
- `outputs/diagnostics/tables/output_visualization_inventory.csv`

**Purpose of this file**

- Manual or semi-manual curation tables used to evaluate figure quality and plotting needs.

**Column dictionary: `figure_inventory.csv`**

- `figure_path`: repository-relative figure path.
- `purpose`: short text on why the figure exists.
- `quality_assessment`: curation quality label.
- `action`: keep / discard / revise style action.
- `reason`: explanation for action.
- `replacement_or_companion`: suggested alternative or companion figure path.

**Column dictionary: `output_visualization_inventory.csv`**

- `file_path`: CSV or output artifact being reviewed.
- `contains`: plain-language description of file contents.
- `plot_needed`: yes / no flag.
- `recommended_plot_type`: preferred visualization family.
- `reason`: why a plot is or is not needed.
- `status_before`: previous plotting status.
- `companion_plots`: figure paths separated by semicolons.

**Important observations**

- These tables are about presentation planning, not scientific measurement.

### File family: improvement-comparison tables

**Files covered**

- `outputs/improvements/tables/baseline_vs_improved_benchmark_comparison.csv`
- `outputs/improvements/tables/before_after_feature_inventory_comparison.csv`
- `outputs/improvements/tables/split_strategy_robustness_comparison.csv`
- `outputs/improvements/tables/campaign_confounding_comparison.csv`
- `outputs/improvements/tables/feature_ablation_results.csv`
- `outputs/improvements/tables/hidden_damage_experiment_summary.csv`
- `outputs/improvements/tables/hidden_damage_robustness_selection.csv`
- `outputs/improvements/tables/improved_hidden_damage_feature_inventory.csv`
- `outputs/improvements/tables/improved_hidden_damage_selected_models.csv`

**Purpose of this file**

- Comparison layer generated by `run_model_improvement_analysis.py`.

**Column dictionary**

- `baseline_vs_improved_benchmark_comparison.csv`
  - `target`, `strategy`: comparison grain.
  - `baseline_*`: selected baseline model identity and metrics.
  - `improved_*`: selected improved model identity and metrics.
  - `delta_*`: improved minus baseline metric differences.
- `before_after_feature_inventory_comparison.csv`
  - `target`, `feature_name`, `source_family`.
  - `baseline_included`, `improved_included`: boolean inclusion flags.
  - `change_type`: retained / removed / new / neither.
  - `improved_reason`: reason from improved inventory.
  - `improved_feature_set_name`: final improved feature-set name for target.
- `split_strategy_robustness_comparison.csv`
  - `baseline_relative_mae_vs_group_shuffle`, `improved_relative_mae_vs_group_shuffle`, `delta_relative_mae_vs_group_shuffle`.
  - `baseline_spearman_mean`, `improved_spearman_mean`, `delta_spearman_mean`.
- `campaign_confounding_comparison.csv`, `feature_ablation_results.csv`, `hidden_damage_experiment_summary.csv`, `hidden_damage_robustness_selection.csv`, `improved_hidden_damage_feature_inventory.csv`, `improved_hidden_damage_selected_models.csv`
  - same semantics as the corresponding current `outputs/models/hidden_damage/*.csv` tables, but saved into the improvement-comparison folder for easier reporting.

**Important observations**

- These tables are comparison artifacts, not primary training outputs.
- Baseline rows can be less informative because baseline snapshot best-model files lack newer metadata such as feature-set name and transform.

### File family: baseline snapshot-only schemas

**Files covered**

- `outputs/improvements/baseline_snapshot/models/hidden_damage/best_models.csv`
- `outputs/improvements/baseline_snapshot/models/degradation/degradation_best_fits.csv`
- `outputs/improvements/baseline_snapshot/models/proxy_rul/proxy_rul_summary.csv`

**Purpose of this file**

- Historical exports predating the richer current schemas.

**Column dictionary**

- baseline hidden-damage `best_models.csv`
  - `target`: structural target.
  - `best_model_name`: selected winner.
  - Notes: lacks feature-set name, transform, feature count, and robustness score.
- baseline degradation `degradation_best_fits.csv`
  - `specimen_id`, `best_family`, `criterion`, `best_model_name`, `last_observed_day`, `last_observed_predicted_wire_area_loss_frac`, `params`.
  - Notes: lacks upstream feature-set and transform provenance.
- baseline proxy `proxy_rul_summary.csv`
  - `threshold_wire_area_loss_frac`, `n_specimens`, `n_crossed_by_baseline`, `n_crossed_during_observation`, `n_future_crossings_within_horizon`, `n_right_censored`.
  - Notes: lacks derived fractions and `n_crossed_by_last_observation`.

**Important observations**

- These files are still relevant because the improvement-analysis script compares them to the current outputs.

## 3. Cross-file mapping

### Raw-to-processed transformations

- Excel workbook columns in `Data/Images_Dataset_A-Z.xlsx`
  - renamed into `outputs/audit/metadata_loaded.csv`
  - parsed and validated into `outputs/data/master_table.csv`
  - filtered to structural rows in `outputs/data/terminal_structural_table.csv`
- `outputs/audit/image_scan.csv`
  - merged into `master_table.csv` on `sample_name`
- `outputs/features/image_features.csv`
  - merged with `master_table.csv` into `outputs/data/full_feature_table.csv`
- `outputs/data/full_feature_table.csv`
  - reused as `outputs/models/surface/surface_feature_table.csv`
  - filtered by `has_structural_label` into `outputs/models/hidden_damage/hidden_damage_feature_table.csv`
- hidden-damage predictions
  - inserted into `outputs/models/degradation/full_feature_table_with_hidden_damage_proxy.csv`
  - smoothed and fit into `degradation_*` CSVs
  - thresholded into `proxy_rul_estimates.csv` and `proxy_rul_summary.csv`
- diagnostics
  - create copies, pivots, and aggregates under `outputs/diagnostics/tables/`

### Same logical variable under different names

- `sample_name` and `observation_id`
  - same value in `master_table.csv`; `observation_id` is a direct alias.
- `wire_area_loss_raw`, `wire_area_loss_frac`, `wire_area_loss_pct`
  - same underlying measurement represented with conflicting unit conventions.
- `raw_predicted_wire_area_loss_frac`, `predicted_wire_area_loss_frac`, `monotone_proxy_wire_area_loss_frac`, `fitted_wire_area_loss_frac`
  - successive downstream representations of hidden-damage proxy:
    - raw row-level prediction
    - clipped current proxy column
    - cumulative-maximum monotone proxy
    - fitted curve evaluated on grid / observed days
- `treatment_raw`, `treatment_label_raw`, `treatment_protocol`, `treatment_coarse`, `treatment_label_coarse`
  - multiple treatment encodings coexist; raw workbook codes and mapped coarse labels should not be assumed interchangeable.

### Columns that are encoded, transformed, clipped, or aggregated

- `calendar_date`: parsed from `sample_name` date token.
- `week`: parsed from `sample_name`.
- `n_steel_mesh`: integer-cast version of `n_steel_mesh_raw`.
- `cover_mm`: direct alias of `cover_mm_raw`.
- hidden-damage `target_transform`
  - `sqrt` means training used square-root transformed targets but saved predictions and metrics on original scale.
- `predicted_wire_area_loss_frac`
  - clipped to `[0, 1]` in degradation stage.
- `proxy_rul_days`
  - intentionally null unless threshold crossing occurs after the observation window.
- `*_summary.csv`
  - aggregate per-fold metrics into mean/std summaries.
- `feature_inventory_by_stage.csv`
  - computed inventory, not original data.
- `exposure_band_summary.csv`
  - groups by tertiles of `ageing_days`.

### Targets and their upstream source columns

- Surface targets:
  - `surface_total_rust_pct`
  - `peak_rust_pct`
- Structural targets:
  - `wire_area_loss_frac` derived from workbook `wire_area_loss_raw`
  - `ultimate_load_kn`
- Downstream proxy target:
  - `predicted_wire_area_loss_frac` is not a measured target; it is model output used as a proxy signal.

## 4. Ambiguities and unresolved items

- `surface_total_rust_category` and `peak_rust_category`
  - Proven to be ordinal workbook categories, but the repo never defines what numeric thresholds correspond to categories `1`–`4`.
- `peak_rust_location_cm`
  - Proven to be a location in centimeters, but the origin / orientation convention is not documented in code.
- `treatment_label_raw`
  - Clearly a raw workbook label, but exact semantics of each label code are only partly reconstructable from the repo.
- `treatment_coarse`
  - The intended control code is almost certainly `"NO"`, but YAML coercion currently stores it as boolean `False`. Project owner confirmation is needed before any cleaned re-export.
- `wire_area_loss_raw`
  - The workbook label says percent; the code treats it as fraction. Manual confirmation from the project owner is needed to decide which representation is physically correct.
- Image-threshold feature semantics
  - Feature names are clear, but exact relation to thesis preprocessing is approximate because `configs/features.yaml` explicitly says exact GIMP white-balance parameters were not fully recovered.

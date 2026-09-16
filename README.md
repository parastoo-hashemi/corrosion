# Ferrocement corrosion research

This project studies what repeated photographs of surface corrosion can tell us
about ferrocement specimens and their terminal structural capacity. It includes
successive modelling experiments and a later four-class image-classification
preparation study.

**Main finding:** in the most mature terminal-load study, image features did not
establish a consistent improvement over specimen metadata. Campaign holdout
exposed weak transfer, and the exploratory degradation work does not validate
remaining-life prediction. See the [key results and evidence](docs/experiments.md#key-results-and-evidence).

## Start here

| Your goal | Reading path |
|---|---|
| Understand the scientific work | [Five-page article](final_reports/article.pdf), then the [40-page thesis](final_reports/thesis.pdf) |
| Inspect results and historical phases | [Experiment map](docs/experiments.md), with direct links to saved tables, figures and predictions |
| Browse the selected figures and papers | [Selected results](selected_results/README.md), organized by phase with interpretation notes and provenance |
| Continue or reproduce the work | [Known issues](docs/known_issues.md), then [reproduction instructions](docs/reproduction.md) |
| Understand the data and terminology | [Data dictionary](docs/data_dictionary.md) and [project history](docs/project_history.md) |

## Current status

| Workstream | What is available | What remains |
|---|---|---|
| Terminal structural capacity | Saved benchmarks, specimen splits, predictions and final manuscripts | Repair and validate the current modelling source before a new run |
| Four-class corrosion classification | Prepared images, augmentation records and fixed specimen partitions | Classifier training and evaluation have not been performed |
| Reproduction | Preservation checks, documented commands and recorded check environment | A verified historical training environment and complete end-to-end reruns |

Saved results are available for scientific review. Successful file checks or model
loading do not establish that the present source reproduces those results.

## Dataset and interpretation

The current dataset contains **48 specimens from two campaigns**, with 792 source
images and **791 readable, aligned observations**. Photographs repeat over time;
wire-area loss and ultimate load are each measured once per specimen, at the
terminal test. The independent structural sample is therefore 48 specimens.

Campaign, mesh family, chloride concentration and exposure schedule are aligned,
which limits generalization and causal interpretation. Some strong surface-model
results reconstruct a closely related image-derived label. Model-derived curves
and threshold crossings are exploratory, without observed lifetime outcomes.

[Data/](Data) holds local datasets and fixed classification splits. Historical
modelling and current four-class preparation use different workbook/label versions;
follow the [data dictionary](docs/data_dictionary.md) when selecting inputs.

## Where the work lives

| Location | Purpose |
|---|---|
| [structural_capacity/](structural_capacity) | Most mature structural study: robustness analysis and terminal-load refocus |
| [classification_data_preparation/](classification_data_preparation) | Current four-class preparation and specimen partitions |
| [exploratory_prototype/](exploratory_prototype) | Earliest exploratory work; no comparable held-out benchmark |
| [classical_corrosion/](classical_corrosion) | Historical classical corrosion models |
| [image_embeddings/](image_embeddings) | Historical frozen-image embeddings and tabular context |
| [condition_assessment/](condition_assessment) | Interpretable features, structural feasibility and first proxy-RUL pipeline |
| [final_reports/](final_reports) | Current v3 article/thesis, scientific figures, tables and retained analysis scripts |
| [docs/](docs) | Experiment map, history, data definitions, reproduction and known issues |
| [Data/](Data), [Documentation/](Documentation) | Local data and predecessor experimental documentation; excluded from Git |
| [archive/](archive) | Earlier structural snapshot and historical working records |
| [selected_results/](selected_results/README.md) | Curated collection of 28 figures and two historical papers, formerly `emiling/` |
| [out/](out) | Six preserved historical PDF exports |
| [report_cleanup/](report_cleanup) | Maintenance manifests, recovery information and preservation checks |

The [folder migration guide](docs/folder_migration.md) maps old names such as
`main_3` and `main_4` to these directories. Historical paths can be resolved with:

```bash
python research_paths.py "main_4/outputs/data/master_table.csv"
```

The final delivery reports are the v3 article and thesis linked above. A historical
70-page activity-report draft remains in `out/`; the [export audit](report_cleanup/out_audit/README.md)
explains its status and other document variants.

## Inspect the handoff

From the repository root:

```bash
python -B report_cleanup/renaming/verify_renaming.py --quick
```

This checks preservation records, source syntax, paths, links and saved validation
receipts. It does not train models. The `--full` option also hashes the remaining
baseline files, reading approximately 49 GB.

The [environment instructions](docs/reproduction.md#environment-and-dependencies)
list dependencies and installation gaps. The recorded check environment is not a
verified historical training environment. For a complete transfer, include the
local data/model bundle and preserve symbolic links.

The ignore rules now expose the three Python files in
`condition_assessment/src/data/`. They remain untracked until a later approved Git
update; include them in the local handoff bundle. Raw/generated data exclusions
remain in place.

## Continue the research

1. Review the article and the [saved evidence](docs/experiments.md#key-results-and-evidence).
2. Choose a workstream. The prepared four-class classifier is the clearest pending
   experiment; use its saved specimen-disjoint partitions and report class imbalance.
3. For structural reruns, recover intended source/configuration values and resolve
   the documented category and environment issues in a separate reproduction copy.
4. Give each new experiment its own output directory, configuration, environment
   record and comparison with the frozen results.

For stronger structural or lifetime claims, additional independent specimens,
crossed experimental factors and repeated structural measurements are needed.

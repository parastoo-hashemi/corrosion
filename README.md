# Ferrocement corrosion research

This project studies what repeated photographs of surface corrosion can tell us
about ferrocement specimens and their terminal structural capacity. It includes
successive modelling experiments and a later four-class image-classification
preparation study.

**Computational study and reports:** Parastoo Hashemi Alvar,
Politecnico di Torino (Turin, Italy).

**Documentation updated:** 16 September 2026. **Manuscripts:** Version 3.

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
| Four-class corrosion classification | Main augmented dataset and fixed specimen partitions | Classifier training/evaluation; optional variant metadata need reconciliation before use |
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
The physical specimens and experimental campaigns originate in predecessor work;
the [thesis](final_reports/thesis.pdf) documents that provenance and its citations.

## Where the work lives

| Location | Purpose |
|---|---|
| [structural_capacity/](structural_capacity/README.md) | Most mature structural study: robustness analysis and terminal-load refocus |
| [classification_data_preparation/](classification_data_preparation/README.md) | Current four-class preparation and specimen partitions |
| [exploratory_prototype/](exploratory_prototype/README.md) | Earliest exploratory work; no comparable held-out benchmark |
| [classical_corrosion/](classical_corrosion/README.md) | Historical classical corrosion models |
| [image_embeddings/](image_embeddings/README.md) | Historical frozen-image embeddings and tabular context |
| [condition_assessment/](condition_assessment/README.md) | Interpretable features, structural feasibility and first proxy-RUL pipeline |
| [final_reports/](final_reports) | Current v3 article/thesis, scientific figures, tables and retained analysis scripts |
| [docs/](docs) | Experiment map, history, data definitions, reproduction and known issues |
| [Data/](Data), [Documentation/](Documentation) | Local data and predecessor experimental documentation; excluded from Git |
| [archive/](archive) | Earlier structural snapshot and historical working records |
| [selected_results/](selected_results/README.md) | Curated collection of research figures and historical papers |
| [out/](out) | Historical PDF exports; see the [export guide](archive/repository_maintenance/out_audit/README.md) for the audited document history |
| [archive/repository_maintenance/](archive/repository_maintenance/README.md) | Maintenance manifests, recovery information and preservation checks |

## Reproducibility and transfer

Use the [reproduction guide](docs/reproduction.md) for dependencies, working
directories, verification commands and manuscript builds. Read the
[known issues](docs/known_issues.md) before attempting new experiments; the saved
results do not establish a verified end-to-end rerun of the current source.

For a complete transfer, include the local data and model bundle and preserve
symbolic links. Some research assets are excluded from Git, so a Git-only copy
is incomplete.

The [folder map](docs/folder_migration.md) explains historical names. Detailed
migration, recovery and preservation records are in the
[maintenance archive](archive/repository_maintenance/README.md).

## Continue the research

Preserve specimen-level split boundaries, target units, terminal evaluation scope,
and the distinction between observed and model-estimated quantities. Keep saved
data, metrics, predictions, models, figures and manuscript claims unchanged when
starting new work. Review code/configuration repairs in a separate reproduction
copy and give new experiments their own results directory.

1. Review the article and the [saved evidence](docs/experiments.md#key-results-and-evidence).
2. Choose a workstream. The prepared four-class classifier is the clearest pending
   experiment; start with its main saved specimen-disjoint partitions and report
   class imbalance. Optional variants need the documented metadata reconciliation first.
3. For structural reruns, recover intended source/configuration values and resolve
   the documented category and environment issues in a separate reproduction copy.
4. Give each new experiment its own output directory, configuration, environment
   record and comparison with the frozen results.

For stronger structural or lifetime claims, additional independent specimens,
crossed experimental factors and repeated structural measurements are needed.

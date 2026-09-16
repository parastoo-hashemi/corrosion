# Four-class corrosion image preparation

**Preparation is complete; classifier training and evaluation have not been done.**
This directory prepares images, controlled variants and specimen-level partitions.
It does not train a classifier. Saved manifests are in [Data/splits/](../Data/splits/).

From the repository root:

```bash
python classification_data_preparation/augment_dataset.py --help
python classification_data_preparation/make_splits.py --help
```

The saved package uses five copies per readable original, explicitly selected with
`--copies 5`, and seed 20260630. The script default remains four copies. Do not
regenerate over the saved package to check your installation.

[Reproduction](../docs/reproduction.md) gives commands with separate output paths.
[Data dictionary](../docs/data_dictionary.md) explains labels and provenance.
[Detailed code reference](../docs/reference/augmentation_code.md) retains the
original implementation explanation, including limitations. Its historical report
paths are interpreted relative to the repository root; current instructions are
in reproduction.md. Requirements are minimum versions, and the split/variant
scripts additionally import pandas.

All images of a specimen stay together; validation/test contain originals only.
Existing fixed assignments and output bytes are unchanged. Additional variants
are preparation assets, not completed evidence of model improvement.

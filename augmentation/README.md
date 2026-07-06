# Offline corrosion dataset augmentation

This directory contains dataset-preparation code only. It does not train a model.

From the project root:

```bash
python augmentation/augment_dataset.py
```

The default creates one byte-for-byte original copy plus four deterministic
augmented PNGs per readable workbook-linked image. Use `--help` for configurable
paths, `--copies`, `--seed`, column overrides, worker count, and overwrite
protection.

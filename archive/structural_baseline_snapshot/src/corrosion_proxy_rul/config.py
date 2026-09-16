from __future__ import annotations

from functools import lru_cache

import yaml

from .utils_paths import CONFIG_DIR


def load_yaml_config(path):
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@lru_cache(maxsize=1)
def load_configs():
    return {
        "dataset": load_yaml_config(CONFIG_DIR / "dataset.yaml"),
        "features": load_yaml_config(CONFIG_DIR / "features.yaml"),
        "modeling": load_yaml_config(CONFIG_DIR / "modeling.yaml"),
        "thresholds": load_yaml_config(CONFIG_DIR / "thresholds.yaml"),
        "specimen_mapping": load_yaml_config(CONFIG_DIR / "specimen_mapping.yaml"),
    }

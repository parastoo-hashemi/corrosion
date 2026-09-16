"""Load the preserved YAML configuration without repairing historical values.

Successful parsing is not semantic validation: unquoted NO becomes False with
the existing loader, and main_first substitutions remain in numeric fields.
See docs/known_issues.md before attempting a modelling rerun."""

from __future__ import annotations

from functools import lru_cache

import yaml

from .utils_paths import CONFIG_DIR


def load_yaml_config(path):
    """Preserve loader semantics; category/type repairs require a separate change."""
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@lru_cache(maxsize=1)
def load_configs():
    """Cache this generation's configs, including the terminal-load refocus settings."""
    return {
        "dataset": load_yaml_config(CONFIG_DIR / "dataset.yaml"),
        "features": load_yaml_config(CONFIG_DIR / "features.yaml"),
        "modeling": load_yaml_config(CONFIG_DIR / "modeling.yaml"),
        "thresholds": load_yaml_config(CONFIG_DIR / "thresholds.yaml"),
        "specimen_mapping": load_yaml_config(CONFIG_DIR / "specimen_mapping.yaml"),
        "ultimate_load_refocus": load_yaml_config(CONFIG_DIR / "ultimate_load_refocus.yaml"),
    }

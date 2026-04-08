from __future__ import annotations

import sys

import pandas as pd

sys.path.insert(0, "src")

from corrosion_proxy_rul.config import load_configs
from corrosion_proxy_rul.models_surface import run_surface_models
from corrosion_proxy_rul.utils_paths import OUTPUT_DIR, configure_logging


def main():
    logger = configure_logging("train_surface_models")
    configs = load_configs()
    master_df = pd.read_csv(OUTPUT_DIR / "data" / "master_table.csv", parse_dates=["calendar_date"])
    image_feature_df = pd.read_csv(OUTPUT_DIR / "features" / "image_features.csv")
    _, best_df = run_surface_models(
        master_df, image_feature_df, configs, OUTPUT_DIR / "models" / "surface"
    )
    logger.info("Surface modeling complete. Best models=%s", best_df.to_dict("records"))


if __name__ == "__main__":
    main()

from __future__ import annotations

import sys

import pandas as pd

sys.path.insert(0, "src")

from corrosion_proxy_rul.config import load_configs
from corrosion_proxy_rul.feature_engineering import build_full_feature_table
from corrosion_proxy_rul.models_hidden_damage import run_hidden_damage_models
from corrosion_proxy_rul.utils_paths import OUTPUT_DIR, configure_logging, save_dataframe_csv


def main():
    logger = configure_logging("train_hidden_damage_models")
    configs = load_configs()
    master_df = pd.read_csv(OUTPUT_DIR / "data" / "master_table.csv", parse_dates=["calendar_date"])
    image_feature_df = pd.read_csv(OUTPUT_DIR / "features" / "image_features.csv")
    full_feature_df = build_full_feature_table(master_df, image_feature_df)
    save_dataframe_csv(full_feature_df, OUTPUT_DIR / "data" / "full_feature_table.csv")
    _, best_df = run_hidden_damage_models(
        full_feature_df, configs, OUTPUT_DIR / "models" / "hidden_damage"
    )
    logger.info("Hidden damage modeling complete. Best models=%s", best_df.to_dict("records"))


if __name__ == "__main__":
    main()

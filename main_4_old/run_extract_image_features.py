from __future__ import annotations

import sys

import pandas as pd

sys.path.insert(0, "src")

from corrosion_proxy_rul.config import load_configs
from corrosion_proxy_rul.image_features import extract_image_feature_table, feature_dictionary
from corrosion_proxy_rul.utils_paths import OUTPUT_DIR, configure_logging, save_dataframe_csv


def main():
    logger = configure_logging("run_extract_image_features")
    configs = load_configs()
    master_df = pd.read_csv(OUTPUT_DIR / "data" / "master_table.csv", parse_dates=["calendar_date"])
    image_features_df, failures_df = extract_image_feature_table(
        master_df, configs["features"]["image_features"], logger
    )
    save_dataframe_csv(image_features_df, OUTPUT_DIR / "features" / "image_features.csv")
    save_dataframe_csv(failures_df, OUTPUT_DIR / "features" / "image_feature_failures.csv")
    save_dataframe_csv(feature_dictionary(), OUTPUT_DIR / "features" / "feature_dictionary.csv")
    logger.info(
        "Image feature extraction complete. features=%s failures=%s",
        len(image_features_df),
        len(failures_df),
    )


if __name__ == "__main__":
    main()

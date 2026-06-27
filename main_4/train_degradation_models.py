from __future__ import annotations

import sys

import pandas as pd

sys.path.insert(0, "src")

from corrosion_proxy_rul.config import load_configs
from corrosion_proxy_rul.models_degradation import run_degradation_modeling
from corrosion_proxy_rul.utils_paths import OUTPUT_DIR, configure_logging


def main():
    logger = configure_logging("train_degradation_models")
    configs = load_configs()
    feature_df = pd.read_csv(OUTPUT_DIR / "data" / "full_feature_table.csv", parse_dates=["calendar_date"])
    _, best_df, _ = run_degradation_modeling(
        feature_df,
        OUTPUT_DIR / "models" / "hidden_damage",
        configs,
        OUTPUT_DIR / "models" / "degradation",
    )
    logger.info("Degradation modeling complete. n_specimens=%s", len(best_df))


if __name__ == "__main__":
    main()

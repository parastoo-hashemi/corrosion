from __future__ import annotations

import sys

import pandas as pd

sys.path.insert(0, "src")

from corrosion_proxy_rul.config import load_configs
from corrosion_proxy_rul.models_rul_proxy import run_proxy_rul
from corrosion_proxy_rul.utils_paths import OUTPUT_DIR, configure_logging


def main():
    logger = configure_logging("train_rul_proxy_models")
    configs = load_configs()
    degradation_best_df = pd.read_csv(OUTPUT_DIR / "models" / "degradation" / "degradation_best_fits.csv")
    degradation_grid_df = pd.read_csv(OUTPUT_DIR / "models" / "degradation" / "degradation_trajectory_grid.csv")
    _, summary_df = run_proxy_rul(
        degradation_best_df,
        degradation_grid_df,
        configs,
        OUTPUT_DIR / "models" / "proxy_rul",
    )
    logger.info(
        "Exploratory threshold-status analysis complete. thresholds=%s",
        summary_df.to_dict("records"),
    )


if __name__ == "__main__":
    main()

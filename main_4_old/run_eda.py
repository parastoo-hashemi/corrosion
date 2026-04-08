from __future__ import annotations

import sys

import pandas as pd

sys.path.insert(0, "src")

from corrosion_proxy_rul.eda import generate_eda
from corrosion_proxy_rul.utils_paths import OUTPUT_DIR, configure_logging


def main():
    logger = configure_logging("run_eda")
    master_df = pd.read_csv(OUTPUT_DIR / "data" / "master_table.csv", parse_dates=["calendar_date"])
    generate_eda(master_df, OUTPUT_DIR / "eda")
    logger.info("EDA outputs saved under outputs/eda")


if __name__ == "__main__":
    main()

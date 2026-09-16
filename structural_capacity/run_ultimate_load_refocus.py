from __future__ import annotations

import sys

import pandas as pd

sys.path.insert(0, "src")

from corrosion_proxy_rul.config import load_configs
from corrosion_proxy_rul.ultimate_load_refocus import run_ultimate_load_refocus
from corrosion_proxy_rul.utils_paths import OUTPUT_DIR, configure_logging


def main() -> None:
    logger = configure_logging("run_ultimate_load_refocus")
    configs = load_configs()
    master_df = pd.read_csv(OUTPUT_DIR / "data" / "master_table.csv", parse_dates=["calendar_date"])
    outputs = run_ultimate_load_refocus(master_df=master_df, configs=configs, logger=logger)
    logger.info("Ultimate-load refocus complete: %s", outputs)


if __name__ == "__main__":
    main()

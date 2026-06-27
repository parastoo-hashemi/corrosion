from __future__ import annotations

import sys

sys.path.insert(0, "src")

from corrosion_proxy_rul.diagnostics import run_diagnostics
from corrosion_proxy_rul.utils_paths import configure_logging


def main() -> None:
    logger = configure_logging("run_diagnostics_visualizations")
    outputs = run_diagnostics()
    logger.info(
        "Diagnostics generation complete. figures=%d tables=%d",
        len(outputs["new_figures"]),
        len(outputs["new_tables"]),
    )


if __name__ == "__main__":
    main()

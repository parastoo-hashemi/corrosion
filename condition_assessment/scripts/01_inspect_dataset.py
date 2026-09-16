from __future__ import annotations

from _bootstrap import ROOT

from src.config import ensure_project_dirs, load_settings
from src.logging_utils import setup_logging
from src.orchestration import run_dataset_inspection


def main() -> None:
    settings = load_settings(ROOT / "configs" / "default.toml")
    ensure_project_dirs(settings)
    setup_logging(settings.paths.logs_dir / "01_inspect_dataset.log")
    run_dataset_inspection(settings)


if __name__ == "__main__":
    main()

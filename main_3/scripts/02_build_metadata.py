from __future__ import annotations

from _bootstrap import ROOT

from src.config import ensure_project_dirs, load_settings
from src.logging_utils import setup_logging
from src.orchestration import run_metadata_stage


def main() -> None:
    settings = load_settings(ROOT / "configs" / "default.toml")
    ensure_project_dirs(settings)
    setup_logging(settings.paths.logs_dir / "02_build_metadata.log")
    run_metadata_stage(settings)


if __name__ == "__main__":
    main()

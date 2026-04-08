from __future__ import annotations

from _bootstrap import ROOT

from src.config import ensure_project_dirs, load_settings
from src.logging_utils import setup_logging
from src.orchestration import (
    run_corrosion_stage,
    run_damage_stage,
    run_dataset_inspection,
    run_degradation_stage,
    run_feature_stage,
    run_metadata_stage,
    run_preprocessing_stage,
    run_report_stage,
    run_rul_stage,
)


def main() -> None:
    settings = load_settings(ROOT / "configs" / "default.toml")
    ensure_project_dirs(settings)
    setup_logging(settings.paths.logs_dir / "run_all.log")
    run_dataset_inspection(settings)
    run_metadata_stage(settings)
    run_preprocessing_stage(settings)
    run_feature_stage(settings)
    run_corrosion_stage(settings)
    run_damage_stage(settings)
    run_degradation_stage(settings)
    run_rul_stage(settings)
    run_report_stage(settings)


if __name__ == "__main__":
    main()

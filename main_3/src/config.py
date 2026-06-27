from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class PathSettings:
    data_dir: Path
    excel_path: Path
    image_dir: Path
    outputs_dir: Path
    reports_dir: Path
    figures_dir: Path
    logs_dir: Path
    models_dir: Path


@dataclass(frozen=True)
class FeatureSettings:
    longitudinal_segments: int
    crop_left_ratio: float
    crop_right_ratio: float
    crop_top_ratio: float
    crop_bottom_ratio: float
    diagnostic_preview_limit: int


@dataclass(frozen=True)
class ProjectSettings:
    seed: int
    test_size: float
    sample_length_cm: float
    max_rul_horizon_weeks: float
    future_step_weeks: float
    wire_loss_scale_to_percent_if_max_leq: float
    load_capacity_ratio_threshold: float
    health_index_threshold: float
    wire_loss_thresholds_pct: tuple[float, ...]


@dataclass(frozen=True)
class TargetSettings:
    corrosion_regression: tuple[str, ...]
    corrosion_classification: tuple[str, ...]
    damage_regression: tuple[str, ...]


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    project_root: Path
    paths: PathSettings
    features: FeatureSettings
    project: ProjectSettings
    targets: TargetSettings


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def repo_root() -> Path:
    return project_root().parent


def load_settings(config_path: Path | None = None) -> Settings:
    root = project_root()
    config_path = config_path or (root / "configs" / "default.toml")
    with config_path.open("rb") as handle:
        raw = tomllib.load(handle)

    def _resolve(path_str: str) -> Path:
        return (root / path_str).resolve()

    paths = PathSettings(
        data_dir=_resolve(raw["paths"]["data_dir"]),
        excel_path=_resolve(raw["paths"]["excel_path"]),
        image_dir=_resolve(raw["paths"]["image_dir"]),
        outputs_dir=_resolve(raw["paths"]["outputs_dir"]),
        reports_dir=_resolve(raw["paths"]["reports_dir"]),
        figures_dir=_resolve(raw["paths"]["figures_dir"]),
        logs_dir=_resolve(raw["paths"]["logs_dir"]),
        models_dir=_resolve(raw["paths"]["models_dir"]),
    )
    features = FeatureSettings(**raw["features"])
    project = ProjectSettings(
        seed=int(raw["project"]["seed"]),
        test_size=float(raw["project"]["test_size"]),
        sample_length_cm=float(raw["project"]["sample_length_cm"]),
        max_rul_horizon_weeks=float(raw["project"]["max_rul_horizon_weeks"]),
        future_step_weeks=float(raw["project"]["future_step_weeks"]),
        wire_loss_scale_to_percent_if_max_leq=float(
            raw["project"]["wire_loss_scale_to_percent_if_max_leq"]
        ),
        load_capacity_ratio_threshold=float(
            raw["project"]["load_capacity_ratio_threshold"]
        ),
        health_index_threshold=float(raw["project"]["health_index_threshold"]),
        wire_loss_thresholds_pct=tuple(
            float(v) for v in raw["project"]["wire_loss_thresholds_pct"]
        ),
    )
    targets = TargetSettings(
        corrosion_regression=tuple(raw["targets"]["corrosion_regression"]),
        corrosion_classification=tuple(raw["targets"]["corrosion_classification"]),
        damage_regression=tuple(raw["targets"]["damage_regression"]),
    )
    return Settings(
        repo_root=repo_root(),
        project_root=root,
        paths=paths,
        features=features,
        project=project,
        targets=targets,
    )


def ensure_project_dirs(settings: Settings) -> None:
    for path in (
        settings.paths.outputs_dir,
        settings.paths.reports_dir,
        settings.paths.figures_dir,
        settings.paths.logs_dir,
        settings.paths.models_dir,
    ):
        path.mkdir(parents=True, exist_ok=True)

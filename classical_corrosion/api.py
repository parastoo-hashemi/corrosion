from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from corrosion.classical_corrosion.inference import (
    Artifacts,
    load_artifacts,
    predict_current_corrosion,
    predict_progression_curve,
    predict_time_to_threshold,
)


def _default_artifacts_dir() -> Path:
    return Path(__file__).resolve().parent / "artifacts"


@lru_cache(maxsize=1)
def get_artifacts() -> Artifacts:
    artifacts_dir = _default_artifacts_dir()
    if not (artifacts_dir / "manifest.json").exists():
        raise RuntimeError(
            "Artifacts not found. Run training main_first: python3 -m corrosion.classical_corrosion.train_models"
        )
    return load_artifacts(artifacts_dir)


class MaterialMetadata(BaseModel):
    n_steel_mesh: float = Field(..., ge=0)
    treatment: str
    nacl_pct: float = Field(..., ge=0)
    ageing_days: float = Field(..., ge=0)
    cover_mm: float = Field(..., ge=0)
    series: str = "UNKNOWN"


class CurrentPredictionRequest(MaterialMetadata):
    image_path: str
    week: float = Field(..., ge=0)


class ProgressionRequest(MaterialMetadata):
    start_week: int = Field(0, ge=0)
    end_week: int = Field(36, ge=0)
    step: int = Field(1, ge=1)
    threshold_pct: Optional[float] = Field(default=None, ge=0)


class TimePredictionRequest(MaterialMetadata):
    week: float = Field(..., ge=0)
    current_peak_rust_pct: float = Field(..., ge=0)
    threshold_pct: Optional[float] = Field(default=None, ge=0)


app = FastAPI(
    title="Corrosion Prediction API",
    version="main_first.0.0",
    description="Predicts corrosion severity and expected time-to-threshold.",
)


@app.get("/health")
def health() -> dict:
    try:
        artifacts = get_artifacts()
        return {
            "status": "ok",
            "models_loaded": True,
            "threshold_pct": artifacts.manifest["threshold_pct"],
        }
    except Exception as exc:
        return {"status": "error", "models_loaded": False, "error": str(exc)}


@app.post("/predict/current")
def predict_current(req: CurrentPredictionRequest) -> dict:
    try:
        artifacts = get_artifacts()
        return predict_current_corrosion(
            artifacts=artifacts,
            image_path=Path(req.image_path),
            n_steel_mesh=req.n_steel_mesh,
            treatment=req.treatment,
            nacl_pct=req.nacl_pct,
            ageing_days=req.ageing_days,
            cover_mm=req.cover_mm,
            week=req.week,
            series=req.series,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/predict/progression")
def predict_progression(req: ProgressionRequest) -> dict:
    if req.end_week < req.start_week:
        raise HTTPException(status_code=400, detail="end_week must be >= start_week.")
    try:
        artifacts = get_artifacts()
        return predict_progression_curve(
            artifacts=artifacts,
            n_steel_mesh=req.n_steel_mesh,
            treatment=req.treatment,
            nacl_pct=req.nacl_pct,
            ageing_days=req.ageing_days,
            cover_mm=req.cover_mm,
            series=req.series,
            start_week=req.start_week,
            end_week=req.end_week,
            step=req.step,
            threshold_pct=req.threshold_pct,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/predict/time-to-threshold")
def predict_time(req: TimePredictionRequest) -> dict:
    try:
        artifacts = get_artifacts()
        return predict_time_to_threshold(
            artifacts=artifacts,
            current_peak_rust_pct=req.current_peak_rust_pct,
            n_steel_mesh=req.n_steel_mesh,
            treatment=req.treatment,
            nacl_pct=req.nacl_pct,
            ageing_days=req.ageing_days,
            cover_mm=req.cover_mm,
            week=req.week,
            series=req.series,
            threshold_pct=req.threshold_pct,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


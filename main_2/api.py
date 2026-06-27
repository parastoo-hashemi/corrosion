from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from corrosion.main_2.inference import Phase2Artifacts, load_phase2_artifacts, predict_current_corrosion


def _artifacts_dir() -> Path:
    return Path(__file__).resolve().parent / "artifacts"


@lru_cache(maxsize=1)
def get_artifacts() -> Phase2Artifacts:
    artifacts_dir = _artifacts_dir()
    if not (artifacts_dir / "run_info.json").exists():
        raise RuntimeError(
            "Phase 2 artifacts not found. Run: python -m main_2.train_phase2"
        )
    return load_phase2_artifacts(artifacts_dir)


class PredictRequest(BaseModel):
    image_path: str
    n_steel_mesh: float = Field(..., ge=0)
    treatment: str
    nacl_pct: float = Field(..., ge=0)
    ageing_days: float = Field(..., ge=0)
    cover_mm: float = Field(..., ge=0)
    week: float = Field(..., ge=0)
    series: str = "UNKNOWN"


app = FastAPI(
    title="Corrosion Phase 2 API",
    version="2.0.0",
    description="Multimodal deep-learning corrosion predictor.",
)


@app.get("/health")
def health() -> dict:
    try:
        artifacts = get_artifacts()
        return {
            "status": "ok",
            "best_model": artifacts.run_info["phase2_model"]["best_model"],
            "use_tabular": artifacts.run_info["phase2_model"]["use_tabular"],
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@app.post("/predict/current")
def predict_current(req: PredictRequest) -> dict:
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


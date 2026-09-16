from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd

from corrosion.classical_corrosion.image_features import extract_image_features
from corrosion.research_paths import resolve_artifact_path


@dataclass
class Artifacts:
    manifest: Dict
    current_model: object
    progression_model: object
    time_model: object


def load_artifacts(artifacts_dir: Path) -> Artifacts:
    manifest_path = artifacts_dir / "manifest.json"
    with manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    current_path = resolve_artifact_path(manifest["models"]["current_corrosion"]["model_path"], artifacts_dir)
    progression_path = resolve_artifact_path(manifest["models"]["progression"]["model_path"], artifacts_dir)
    time_path = resolve_artifact_path(manifest["models"]["time_to_threshold"]["model_path"], artifacts_dir)

    return Artifacts(
        manifest=manifest,
        current_model=joblib.load(current_path),
        progression_model=joblib.load(progression_path),
        time_model=joblib.load(time_path),
    )


def _base_row(
    n_steel_mesh: float,
    treatment: str,
    nacl_pct: float,
    ageing_days: float,
    cover_mm: float,
    week: float,
    series: str,
) -> Dict:
    return {
        "N_Steel_Mesh": n_steel_mesh,
        "Treatment": treatment,
        "NaCl%": nacl_pct,
        "Ageing_Days": ageing_days,
        "Cover_(Faliure_Surface)_[mm]": cover_mm,
        "week": week,
        "series": series,
    }


def predict_current_corrosion(
    artifacts: Artifacts,
    image_path: Path,
    n_steel_mesh: float,
    treatment: str,
    nacl_pct: float,
    ageing_days: float,
    cover_mm: float,
    week: float,
    series: str = "UNKNOWN",
) -> Dict[str, float | str | bool]:
    row = _base_row(
        n_steel_mesh=n_steel_mesh,
        treatment=treatment,
        nacl_pct=nacl_pct,
        ageing_days=ageing_days,
        cover_mm=cover_mm,
        week=week,
        series=series,
    )
    image_features, corrupted, err = extract_image_features(image_path)
    row.update(image_features)

    model_features = artifacts.manifest["features"]["current_model_features"]
    pred_df = pd.DataFrame([row], columns=model_features)
    pred = float(artifacts.current_model.predict(pred_df)[0])
    pred = float(np.clip(pred, 0.0, 100.0))

    if pred < 1.0:
        corrosion_class = "low"
    elif pred < 20.0:
        corrosion_class = "medium"
    else:
        corrosion_class = "high"

    return {
        "predicted_peak_rust_pct": pred,
        "predicted_corrosion_class_3level": corrosion_class,
        "image_corrupted": corrupted,
        "image_error": err,
    }


def predict_progression_curve(
    artifacts: Artifacts,
    n_steel_mesh: float,
    treatment: str,
    nacl_pct: float,
    ageing_days: float,
    cover_mm: float,
    series: str = "UNKNOWN",
    start_week: int = 0,
    end_week: int = 36,
    step: int = 1,
    threshold_pct: float | None = None,
) -> Dict[str, object]:
    if threshold_pct is None:
        threshold_pct = float(artifacts.manifest["threshold_pct"])

    weeks = list(range(int(start_week), int(end_week) + 1, int(step)))
    rows: List[Dict] = []
    for week in weeks:
        rows.append(
            _base_row(
                n_steel_mesh=n_steel_mesh,
                treatment=treatment,
                nacl_pct=nacl_pct,
                ageing_days=ageing_days,
                cover_mm=cover_mm,
                week=float(week),
                series=series,
            )
        )

    model_features = artifacts.manifest["features"]["progression_model_features"]
    pred_df = pd.DataFrame(rows, columns=model_features)
    preds = artifacts.progression_model.predict(pred_df)
    preds = np.clip(np.asarray(preds, dtype=float), 0.0, 100.0)

    threshold_week = None
    for week, pred in zip(weeks, preds):
        if pred >= threshold_pct:
            threshold_week = int(week)
            break

    curve = [
        {"week": int(w), "predicted_peak_rust_pct": float(v)}
        for w, v in zip(weeks, preds)
    ]
    return {
        "curve": curve,
        "threshold_pct": float(threshold_pct),
        "predicted_threshold_week": threshold_week,
    }


def predict_time_to_threshold(
    artifacts: Artifacts,
    current_peak_rust_pct: float,
    n_steel_mesh: float,
    treatment: str,
    nacl_pct: float,
    ageing_days: float,
    cover_mm: float,
    week: float,
    series: str = "UNKNOWN",
    threshold_pct: float | None = None,
) -> Dict[str, float | int | None]:
    if threshold_pct is None:
        threshold_pct = float(artifacts.manifest["threshold_pct"])

    row = _base_row(
        n_steel_mesh=n_steel_mesh,
        treatment=treatment,
        nacl_pct=nacl_pct,
        ageing_days=ageing_days,
        cover_mm=cover_mm,
        week=week,
        series=series,
    )
    row["B_Peak_Rust_Percentage_[%]"] = current_peak_rust_pct

    model_features = artifacts.manifest["features"]["time_model_features"]
    pred_df = pd.DataFrame([row], columns=model_features)

    if current_peak_rust_pct >= threshold_pct:
        remaining = 0.0
    else:
        remaining = float(max(0.0, artifacts.time_model.predict(pred_df)[0]))

    return {
        "predicted_remaining_weeks": remaining,
        "predicted_threshold_week": int(round(float(week) + remaining)),
        "threshold_pct": float(threshold_pct),
    }

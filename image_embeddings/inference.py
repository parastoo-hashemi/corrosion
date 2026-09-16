from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torchvision.models import ResNet18_Weights, resnet18
from PIL import Image

from corrosion.image_embeddings.models import RegressionMLP
from corrosion.research_paths import resolve_artifact_path


@dataclass
class Phase2Artifacts:
    run_info: Dict
    model: RegressionMLP
    preprocessor: object
    target_scaler: object
    image_backbone: nn.Module
    image_transform: object
    device: torch.device


def _pick_device() -> torch.device:
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def load_phase2_artifacts(artifacts_dir: Path) -> Phase2Artifacts:
    run_info_path = artifacts_dir / "run_info.json"
    run_info = json.loads(run_info_path.read_text(encoding="utf-8"))

    model_state_path = resolve_artifact_path(run_info["phase2_model"]["artifacts"]["model_state"], artifacts_dir)
    preprocessor_path = resolve_artifact_path(run_info["phase2_model"]["artifacts"]["tabular_preprocessor"], artifacts_dir)
    scaler_path = resolve_artifact_path(run_info["phase2_model"]["artifacts"]["target_scaler"], artifacts_dir)
    input_dim = int(run_info["phase2_model"]["input_dim"])

    device = _pick_device()
    model = RegressionMLP(input_dim=input_dim, dropout=0.0).to(device)
    try:
        state = torch.load(model_state_path, map_location=device, weights_only=True)
    except TypeError:
        state = torch.load(model_state_path, map_location=device)
    model.load_state_dict(state)
    model.eval()

    preprocessor = joblib.load(preprocessor_path)
    target_scaler = joblib.load(scaler_path)

    weights = ResNet18_Weights.IMAGENET1K_V1
    image_transform = weights.transforms()
    image_backbone = resnet18(weights=weights)
    image_backbone.fc = nn.Identity()
    image_backbone.to(device)
    image_backbone.eval()

    return Phase2Artifacts(
        run_info=run_info,
        model=model,
        preprocessor=preprocessor,
        target_scaler=target_scaler,
        image_backbone=image_backbone,
        image_transform=image_transform,
        device=device,
    )


def _extract_embedding(artifacts: Phase2Artifacts, image_path: Path) -> np.ndarray:
    with Image.open(image_path) as img:
        x = artifacts.image_transform(img.convert("RGB")).unsqueeze(0).to(artifacts.device)
    with torch.no_grad():
        emb = artifacts.image_backbone(x).detach().cpu().numpy().reshape(-1)
    return emb.astype(np.float32)


def _build_tab_row(
    n_steel_mesh: float,
    treatment: str,
    nacl_pct: float,
    ageing_days: float,
    cover_mm: float,
    week: float,
    series: str,
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "N_Steel_Mesh": n_steel_mesh,
                "Treatment": treatment,
                "NaCl%": nacl_pct,
                "Ageing_Days": ageing_days,
                "Cover_(Faliure_Surface)_[mm]": cover_mm,
                "week": week,
                "series": series,
            }
        ]
    )


def predict_current_corrosion(
    artifacts: Phase2Artifacts,
    image_path: Path,
    n_steel_mesh: float,
    treatment: str,
    nacl_pct: float,
    ageing_days: float,
    cover_mm: float,
    week: float,
    series: str = "UNKNOWN",
) -> Dict[str, float | str]:
    emb = _extract_embedding(artifacts, image_path=image_path)
    use_tabular = bool(artifacts.run_info["phase2_model"]["use_tabular"])

    if use_tabular:
        tab_df = _build_tab_row(
            n_steel_mesh=n_steel_mesh,
            treatment=treatment,
            nacl_pct=nacl_pct,
            ageing_days=ageing_days,
            cover_mm=cover_mm,
            week=week,
            series=series,
        )
        tab = artifacts.preprocessor.transform(tab_df)
        if hasattr(tab, "toarray"):
            tab = tab.toarray()
        x = np.concatenate([emb.reshape(1, -1), np.asarray(tab, dtype=np.float32)], axis=1)
    else:
        x = emb.reshape(1, -1)

    x_t = torch.tensor(x, dtype=torch.float32, device=artifacts.device)
    with torch.no_grad():
        pred_scaled = artifacts.model(x_t).detach().cpu().numpy().reshape(-1, 1)
    pred = float(artifacts.target_scaler.inverse_transform(pred_scaled).reshape(-1)[0])
    pred = float(np.clip(pred, 0.0, 100.0))

    if pred < 1.0:
        severity = "low"
    elif pred < 20.0:
        severity = "medium"
    else:
        severity = "high"

    return {
        "predicted_peak_rust_pct": pred,
        "predicted_severity_3level": severity,
        "model_used": str(artifacts.run_info["phase2_model"]["best_model"]),
    }

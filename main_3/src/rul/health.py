from __future__ import annotations

import numpy as np
import pandas as pd


def reference_loads_by_campaign(state_df: pd.DataFrame) -> dict[str, float]:
    observed = state_df[state_df["ultimate_load_kn"].notna()].copy()
    if observed.empty:
        fallback = float(state_df["estimated_ultimate_load_kn"].max())
        return {str(campaign): fallback for campaign in state_df["campaign_id"].dropna().unique()}
    grouped = observed.groupby("campaign_id")["ultimate_load_kn"].max()
    return {str(idx): float(val) for idx, val in grouped.items()}


def compute_health_index(
    surface_total_rust_pct: float,
    peak_rust_pct: float,
    wire_area_loss_pct: float,
    ultimate_load_kn: float,
    reference_load_kn: float,
) -> float:
    corrosion_term = 0.5 * np.clip(surface_total_rust_pct / 100.0, 0.0, 1.0) + 0.5 * np.clip(
        peak_rust_pct / 100.0, 0.0, 1.0
    )
    wire_term = np.clip(wire_area_loss_pct / 30.0, 0.0, 1.0)
    load_term = np.clip(1.0 - (ultimate_load_kn / max(reference_load_kn, 1e-6)), 0.0, 1.0)
    health = 1.0 - (0.30 * corrosion_term + 0.40 * wire_term + 0.30 * load_term)
    return float(np.clip(health, 0.0, 1.0))


def failure_probability_proxy(
    health_index: float,
    wire_area_loss_pct: float,
    ultimate_load_kn: float,
    reference_load_kn: float,
    estimated_rul_weeks: float | None,
) -> float:
    rul_component = 0.0
    if estimated_rul_weeks is not None and not np.isnan(estimated_rul_weeks):
        rul_component = float(1.0 / (1.0 + np.exp((estimated_rul_weeks - 12.0) / 3.5)))

    wire_component = float(np.clip(wire_area_loss_pct / 25.0, 0.0, 1.5) / 1.5)
    load_ratio = ultimate_load_kn / max(reference_load_kn, 1e-6)
    load_component = float(np.clip((0.8 - load_ratio) / 0.8, 0.0, 1.0))
    health_component = 1.0 - float(np.clip(health_index, 0.0, 1.0))
    score = 0.40 * rul_component + 0.25 * wire_component + 0.20 * load_component + 0.15 * health_component
    return float(np.clip(score, 0.0, 0.999))


def risk_class_from_probability(probability: float) -> str:
    if probability >= 0.80:
        return "Critical"
    if probability >= 0.60:
        return "High"
    if probability >= 0.35:
        return "Moderate"
    return "Low"


def corrosion_level_label(peak_rust_pct: float) -> str:
    if peak_rust_pct < 1.0:
        return "Trace"
    if peak_rust_pct < 10.0:
        return "Low"
    if peak_rust_pct < 25.0:
        return "Moderate"
    if peak_rust_pct < 50.0:
        return "High"
    return "Severe"

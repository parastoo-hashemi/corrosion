from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import Settings
from src.rul.health import (
    compute_health_index,
    corrosion_level_label,
    failure_probability_proxy,
    reference_loads_by_campaign,
    risk_class_from_probability,
)


def _crossing_week(
    weeks: np.ndarray,
    values: np.ndarray,
    threshold: float,
    direction: str,
    current_week: float,
) -> float:
    future_mask = weeks >= current_week
    weeks = weeks[future_mask]
    values = values[future_mask]
    if direction == "above":
        crossings = weeks[values >= threshold]
    elif direction == "below":
        crossings = weeks[values <= threshold]
    else:
        raise ValueError(f"Unsupported crossing direction: {direction}")
    if len(crossings) == 0:
        return float("nan")
    return float(crossings[0] - current_week)


def estimate_rul(
    state_df: pd.DataFrame,
    forecast_df: pd.DataFrame,
    settings: Settings,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    refs = reference_loads_by_campaign(state_df)
    latest = (
        state_df.sort_values(["specimen_id", "week"])
        .groupby("specimen_id", as_index=False)
        .tail(1)
        .reset_index(drop=True)
    )

    trajectory_rows: list[dict[str, object]] = []
    estimate_rows: list[dict[str, object]] = []

    for row in latest.itertuples(index=False):
        specimen_forecast = forecast_df[forecast_df["specimen_id"] == row.specimen_id].copy()
        pivot = (
            specimen_forecast.pivot_table(
                index="week", columns="target", values="forecast_value", aggfunc="main_first"
            )
            .sort_index()
            .reset_index()
        )
        if pivot.empty:
            continue

        ref_load = refs.get(str(row.campaign_id), float(latest["estimated_ultimate_load_kn"].max()))
        load_threshold = ref_load * settings.project.load_capacity_ratio_threshold
        pivot["health_index"] = pivot.apply(
            lambda x: compute_health_index(
                surface_total_rust_pct=float(x["surface_total_rust_pct"]),
                peak_rust_pct=float(x["peak_rust_pct"]),
                wire_area_loss_pct=float(x["estimated_wire_area_loss_pct"]),
                ultimate_load_kn=float(x["estimated_ultimate_load_kn"]),
                reference_load_kn=ref_load,
            ),
            axis=1,
        )
        pivot["specimen_id"] = row.specimen_id
        for record in pivot.to_dict(orient="records"):
            trajectory_rows.append(record)

        current_week = float(row.week)
        weeks = pivot["week"].to_numpy(dtype=float)
        wire_values = pivot["estimated_wire_area_loss_pct"].to_numpy(dtype=float)
        load_values = pivot["estimated_ultimate_load_kn"].to_numpy(dtype=float)
        health_values = pivot["health_index"].to_numpy(dtype=float)

        wire_crossings = {
            threshold: _crossing_week(
                weeks=weeks,
                values=wire_values,
                threshold=threshold,
                direction="above",
                current_week=current_week,
            )
            for threshold in settings.project.wire_loss_thresholds_pct
        }
        load_rul = _crossing_week(
            weeks=weeks,
            values=load_values,
            threshold=load_threshold,
            direction="below",
            current_week=current_week,
        )
        health_rul = _crossing_week(
            weeks=weeks,
            values=health_values,
            threshold=settings.project.health_index_threshold,
            direction="below",
            current_week=current_week,
        )
        candidates = [
            wire_crossings.get(25.0, float("nan")),
            load_rul,
            health_rul,
        ]
        valid_candidates = [value for value in candidates if not np.isnan(value)]
        estimated_rul = float(min(valid_candidates)) if valid_candidates else float("nan")
        current_health = float(pivot.loc[pivot["week"] == current_week, "health_index"].iloc[0])
        failure_probability = failure_probability_proxy(
            health_index=current_health,
            wire_area_loss_pct=float(row.estimated_wire_area_loss_pct),
            ultimate_load_kn=float(row.estimated_ultimate_load_kn),
            reference_load_kn=ref_load,
            estimated_rul_weeks=estimated_rul if not np.isnan(estimated_rul) else None,
        )
        estimate_rows.append(
            {
                "specimen_id": row.specimen_id,
                "campaign_id": row.campaign_id,
                "treatment_code": row.treatment_code,
                "current_week": current_week,
                "current_corrosion_level": corrosion_level_label(float(row.peak_rust_pct)),
                "current_surface_total_rust_pct": float(row.surface_total_rust_pct),
                "current_peak_rust_pct": float(row.peak_rust_pct),
                "predicted_internal_damage_pct": float(row.estimated_wire_area_loss_pct),
                "predicted_ultimate_load_kn": float(row.estimated_ultimate_load_kn),
                "health_index": current_health,
                "rul_wire_20_weeks": wire_crossings.get(20.0, float("nan")),
                "rul_wire_25_weeks": wire_crossings.get(25.0, float("nan")),
                "rul_wire_30_weeks": wire_crossings.get(30.0, float("nan")),
                "rul_load_threshold_weeks": load_rul,
                "rul_health_threshold_weeks": health_rul,
                "estimated_rul_weeks": estimated_rul,
                "failure_probability": failure_probability,
                "failure_probability_proxy": failure_probability,
                "risk_class": risk_class_from_probability(failure_probability),
                "reference_load_kn": ref_load,
                "load_threshold_kn": load_threshold,
            }
        )

    return pd.DataFrame(estimate_rows), pd.DataFrame(trajectory_rows)

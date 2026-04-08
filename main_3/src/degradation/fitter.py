from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.config import Settings
from src.degradation.curves import fit_best_curve, predict_curve
from src.logging_utils import get_logger


LOGGER = get_logger(__name__)

DEGRADATION_TARGETS = [
    "surface_total_rust_pct",
    "peak_rust_pct",
    "estimated_wire_area_loss_pct",
    "estimated_ultimate_load_kn",
]


def fit_degradation_curves(state_df: pd.DataFrame, settings: Settings) -> tuple[pd.DataFrame, pd.DataFrame]:
    fit_rows: list[dict[str, object]] = []
    forecast_rows: list[dict[str, object]] = []

    for specimen_id, group in state_df.groupby("specimen_id"):
        group = group.sort_values("week").copy()
        x_obs = group["week"].to_numpy(dtype=float)
        max_week = float(x_obs.max())
        future_weeks = np.arange(
            float(x_obs.min()),
            max_week + settings.project.max_rul_horizon_weeks + settings.project.future_step_weeks,
            settings.project.future_step_weeks,
        )

        for target in DEGRADATION_TARGETS:
            if target not in group.columns:
                continue
            y_obs = group[target].to_numpy(dtype=float)
            if np.isnan(y_obs).all():
                continue
            fit_result = fit_best_curve(x_obs, y_obs)
            y_forecast = predict_curve(fit_result, future_weeks)
            if target.endswith("_pct"):
                y_forecast = np.clip(y_forecast, 0.0, 100.0)
            if target.endswith("_kn"):
                y_forecast = np.clip(y_forecast, 0.0, None)

            rate = float(
                (y_forecast[-1] - y_forecast[-2]) / settings.project.future_step_weeks
            )
            fit_rows.append(
                {
                    "specimen_id": specimen_id,
                    "target": target,
                    "model_name": fit_result.model_name,
                    "params_json": fit_result.params_json,
                    "rmse": fit_result.rmse,
                    "r2": fit_result.r2,
                    "n_obs": fit_result.n_obs,
                    "current_week": max_week,
                    "current_value": float(y_obs[-1]),
                    "progression_rate_per_week": rate,
                }
            )
            observed_map = dict(zip(group["week"].to_list(), y_obs.tolist()))
            for week_value, forecast_value in zip(future_weeks, y_forecast):
                forecast_rows.append(
                    {
                        "specimen_id": specimen_id,
                        "target": target,
                        "week": float(week_value),
                        "forecast_value": float(forecast_value),
                        "observed_value": observed_map.get(float(week_value), np.nan),
                        "phase": "historical" if week_value <= max_week else "forecast",
                        "model_name": fit_result.model_name,
                    }
                )
        LOGGER.info("Fitted degradation curves for specimen %s", specimen_id)

    return pd.DataFrame(fit_rows), pd.DataFrame(forecast_rows)


def export_degradation_outputs(
    fits_df: pd.DataFrame,
    forecasts_df: pd.DataFrame,
    output_dir: Path,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    fits_path = output_dir / "degradation_curves.parquet"
    forecasts_path = output_dir / "degradation_forecasts.parquet"
    fits_df.to_parquet(fits_path, index=False)
    forecasts_df.to_parquet(forecasts_path, index=False)
    return {"fits": fits_path, "forecasts": forecasts_path}

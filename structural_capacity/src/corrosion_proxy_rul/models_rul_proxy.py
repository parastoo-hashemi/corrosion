"""Exploratory threshold status on model-estimated wire-loss trajectories.

The dataset has terminal structural measurements, not observed failure times.
The right_censored field means no model-curve crossing within the chosen grid;
it is not an observed survival-study censoring record."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .utils_paths import ensure_dir, save_dataframe_csv, write_json
from .visualization import save_barplot


def run_proxy_rul(degradation_best_df, degradation_grid_df, configs, output_dir: Path):
    """Distinguish past crossings from future model-curve crossings.

    Only the latter populate proxy_rul_days. Neither kind validates remaining
    life, because the longitudinal structural signal is model-derived."""
    ensure_dir(output_dir)
    proxy_cfg = configs["thresholds"]["proxy_rul"]
    thresholds = proxy_cfg["thresholds"]
    horizon = int(proxy_cfg["projection_horizon_days"])

    rows = []
    for record in degradation_best_df.itertuples(index=False):
        specimen_grid = degradation_grid_df.loc[
            degradation_grid_df["specimen_id"] == record.specimen_id
        ].sort_values("day")
        for threshold in thresholds:
            reached = specimen_grid["predicted_wire_area_loss_frac"] >= threshold
            if reached.any():
                crossing_day = float(specimen_grid.loc[reached, "day"].iloc[0])
                right_censored = False
            else:
                crossing_day = np.nan
                right_censored = True
            threshold_reached_by_baseline = bool(
                (not np.isnan(crossing_day)) and crossing_day <= 0.0
            )
            threshold_reached_by_last_observation = bool(
                (not np.isnan(crossing_day))
                and crossing_day <= float(record.last_observed_day)
            )
            threshold_crossed_during_observation = bool(
                (not np.isnan(crossing_day))
                and crossing_day > 0.0
                and crossing_day <= float(record.last_observed_day)
            )
            future_crossing_within_horizon = bool(
                (not np.isnan(crossing_day))
                and crossing_day > float(record.last_observed_day)
            )
            if threshold_reached_by_baseline:
                threshold_status = "crossed_by_baseline"
            elif threshold_crossed_during_observation:
                threshold_status = "crossed_during_observation"
            elif future_crossing_within_horizon:
                threshold_status = "future_crossing_within_horizon"
            else:
                threshold_status = "not_crossed_within_horizon"

            # Keep this column for backward compatibility, but only populate it when a
            # threshold crossing occurs after the observed window. Earlier crossings are
            # threshold-status information, not usable residual-life estimates.
            if future_crossing_within_horizon:
                proxy_rul_days = float(crossing_day - float(record.last_observed_day))
            else:
                proxy_rul_days = np.nan
            rows.append(
                {
                    "specimen_id": record.specimen_id,
                    "best_family": record.best_family,
                    "threshold_wire_area_loss_frac": threshold,
                    "last_observed_day": record.last_observed_day,
                    "last_observed_predicted_wire_area_loss_frac": record.last_observed_predicted_wire_area_loss_frac,
                    "estimated_crossing_day": crossing_day,
                    "proxy_rul_days": proxy_rul_days,
                    "right_censored": right_censored,
                    "threshold_reached_by_baseline": threshold_reached_by_baseline,
                    "threshold_reached_by_last_observation": threshold_reached_by_last_observation,
                    "threshold_crossed_during_observation": threshold_crossed_during_observation,
                    "future_crossing_within_horizon": future_crossing_within_horizon,
                    "threshold_status": threshold_status,
                    "projection_horizon_days": horizon,
                }
            )

    proxy_df = pd.DataFrame(rows)
    save_dataframe_csv(proxy_df, output_dir / "proxy_rul_estimates.csv")
    summary = (
        proxy_df.groupby("threshold_wire_area_loss_frac")[
            [
                "threshold_reached_by_baseline",
                "threshold_crossed_during_observation",
                "future_crossing_within_horizon",
                "right_censored",
            ]
        ]
        .agg(["sum"])
        .reset_index()
    )
    summary.columns = [
        "_".join(col).strip("_") if isinstance(col, tuple) else col for col in summary.columns
    ]
    summary = summary.rename(
        columns={
            "threshold_reached_by_baseline_sum": "n_crossed_by_baseline",
            "threshold_crossed_during_observation_sum": "n_crossed_during_observation",
            "future_crossing_within_horizon_sum": "n_future_crossings_within_horizon",
            "right_censored_sum": "n_right_censored",
        }
    )
    summary.insert(1, "n_specimens", proxy_df.groupby("threshold_wire_area_loss_frac").size().values)
    summary["n_crossed_by_last_observation"] = (
        summary["n_crossed_by_baseline"] + summary["n_crossed_during_observation"]
    )
    for count_col in [
        "n_crossed_by_baseline",
        "n_crossed_during_observation",
        "n_crossed_by_last_observation",
        "n_future_crossings_within_horizon",
        "n_right_censored",
    ]:
        summary[f"frac_{count_col[2:]}"] = summary[count_col] / summary["n_specimens"]
    save_dataframe_csv(summary, output_dir / "proxy_rul_summary.csv")
    save_barplot(
        summary,
        x="threshold_wire_area_loss_frac",
        y="n_right_censored",
        title="Right-censored specimens by threshold (exploratory threshold-status only)",
        path=output_dir / "proxy_rul_right_censored.png",
    )
    write_json(
        output_dir / "proxy_rul_summary.json",
        {
            "thresholds": thresholds,
            "n_specimens": int(proxy_df["specimen_id"].nunique()),
            "summary_records": summary.to_dict("records"),
        },
    )
    return proxy_df, summary

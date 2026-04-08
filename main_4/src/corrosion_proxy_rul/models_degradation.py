from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from sklearn.isotonic import IsotonicRegression

from .evaluation import predict_model_bundle
from .feature_engineering import get_model_feature_columns
from .utils_paths import ensure_dir, save_dataframe_csv, write_json
from .visualization import save_lineplot


def _logistic(x, a, b, c):
    return a / (1.0 + np.exp(-b * (x - c)))


def _gompertz(x, a, b, c):
    return a * np.exp(-b * np.exp(-c * x))


def _bic_like(y_true, y_pred, complexity):
    n = len(y_true)
    rss = float(np.sum((y_true - y_pred) ** 2) + 1e-12)
    return n * np.log(rss / n + 1e-12) + complexity * np.log(max(n, 2))


def _fit_family(x, y, family):
    if family == "linear":
        coeffs = np.polyfit(x, y, deg=1)
        predictor = lambda grid: np.polyval(coeffs, grid)
        params = {"coeffs": coeffs.tolist()}
        return predictor, params
    if family == "log_time":
        coeffs = np.polyfit(np.log1p(x), y, deg=1)
        predictor = lambda grid: np.polyval(coeffs, np.log1p(grid))
        params = {"coeffs": coeffs.tolist()}
        return predictor, params
    if family == "logistic":
        p0 = [max(y.max(), 1e-3), 0.02, float(np.median(x))]
        params, _ = curve_fit(_logistic, x, y, p0=p0, maxfev=20000)
        predictor = lambda grid: _logistic(grid, *params)
        return predictor, {"params": params.tolist()}
    if family == "gompertz":
        p0 = [max(y.max(), 1e-3), 1.0, 0.02]
        params, _ = curve_fit(_gompertz, x, y, p0=p0, maxfev=20000)
        predictor = lambda grid: _gompertz(grid, *params)
        return predictor, {"params": params.tolist()}
    if family == "monotone_isotonic":
        iso = IsotonicRegression(increasing=True, out_of_bounds="clip")
        iso.fit(x, y)
        predictor = lambda grid: iso.predict(grid)
        return predictor, {"x": x.tolist(), "y": iso.predict(x).tolist()}
    raise ValueError(f"Unsupported family: {family}")


def run_degradation_modeling(feature_df, hidden_model_dir: Path, configs, output_dir: Path):
    ensure_dir(output_dir)

    best_info = json.loads((hidden_model_dir / "wire_area_loss_frac" / "group_shuffle" / "wire_area_loss_frac_best_model.json").read_text())
    bundle = joblib.load(hidden_model_dir / "wire_area_loss_frac" / "group_shuffle" / "wire_area_loss_frac_best_model.joblib")
    target = "wire_area_loss_frac"
    feature_cols = get_model_feature_columns(feature_df, target)
    predictions = predict_model_bundle(bundle, feature_df[feature_cols])

    working_df = feature_df.copy()
    working_df["raw_predicted_wire_area_loss_frac"] = np.clip(predictions, 0.0, 1.0)
    working_df["predicted_wire_area_loss_frac"] = working_df["raw_predicted_wire_area_loss_frac"]
    save_dataframe_csv(working_df, output_dir / "full_feature_table_with_hidden_damage_proxy.csv")

    families = ["linear", "log_time", "logistic", "gompertz", "monotone_isotonic"]
    complexity_cfg = configs["modeling"]["degradation"]["family_complexity"]
    horizon = int(configs["thresholds"]["proxy_rul"]["projection_horizon_days"])
    grid_step = int(configs["modeling"]["degradation"]["curve_grid_step_days"])
    curve_grid = np.arange(0, horizon + 1, grid_step, dtype=float)

    candidate_rows = []
    best_rows = []
    grid_rows = []
    trajectory_rows = []

    for specimen_id, specimen_df in working_df.groupby("specimen_id"):
        specimen_df = specimen_df.sort_values("ageing_days")
        x = specimen_df["ageing_days"].to_numpy(dtype=float)
        raw_y = specimen_df["raw_predicted_wire_area_loss_frac"].to_numpy(dtype=float)
        y = np.maximum.accumulate(raw_y)
        if len(x) < configs["modeling"]["degradation"]["min_points_per_specimen"]:
            continue

        trajectory_rows.extend(
            {
                "specimen_id": specimen_id,
                "ageing_days": float(day),
                "raw_predicted_wire_area_loss_frac": float(raw_value),
                "monotone_proxy_wire_area_loss_frac": float(monotone_value),
            }
            for day, raw_value, monotone_value in zip(x, raw_y, y)
        )

        family_results = []
        for family in families:
            try:
                predictor, params = _fit_family(x, y, family)
                fitted = np.clip(predictor(x), 0.0, 1.0)
                criterion = _bic_like(y, fitted, complexity_cfg[family])
                family_results.append((family, criterion, predictor, params))
                candidate_rows.append(
                    {
                        "specimen_id": specimen_id,
                        "family": family,
                        "criterion": criterion,
                        "rmse": float(np.sqrt(np.mean((y - fitted) ** 2))),
                        "fit_succeeded": True,
                        "params": json.dumps(params),
                    }
                )
            except Exception as exc:
                candidate_rows.append(
                    {
                        "specimen_id": specimen_id,
                        "family": family,
                        "criterion": np.nan,
                        "rmse": np.nan,
                        "fit_succeeded": False,
                        "params": json.dumps({"error": str(exc)}),
                    }
                )

        valid = [row for row in family_results if np.isfinite(row[1])]
        if not valid:
            continue
        best_family, best_criterion, best_predictor, best_params = sorted(valid, key=lambda row: row[1])[0]
        best_rows.append(
            {
                "specimen_id": specimen_id,
                "best_family": best_family,
                "criterion": best_criterion,
                "best_model_name": best_info["best_model_name"],
                "hidden_damage_feature_set_name": best_info.get("feature_set_name", ""),
                "hidden_damage_target_transform": best_info.get("target_transform", "none"),
                "last_observed_day": float(x.max()),
                "last_observed_predicted_wire_area_loss_frac": float(y[-1]),
                "params": json.dumps(best_params),
            }
        )
        grid_pred = np.clip(best_predictor(curve_grid), 0.0, 1.0)
        grid_rows.extend(
            {
                "specimen_id": specimen_id,
                "day": float(day),
                "predicted_wire_area_loss_frac": float(pred),
                "best_family": best_family,
            }
            for day, pred in zip(curve_grid, grid_pred)
        )

    candidate_df = pd.DataFrame(candidate_rows)
    best_df = pd.DataFrame(best_rows)
    grid_df = pd.DataFrame(grid_rows)
    trajectory_df = pd.DataFrame(trajectory_rows)

    save_dataframe_csv(candidate_df, output_dir / "degradation_fit_candidates.csv")
    save_dataframe_csv(best_df, output_dir / "degradation_best_fits.csv")
    save_dataframe_csv(grid_df, output_dir / "degradation_trajectory_grid.csv")
    save_dataframe_csv(trajectory_df, output_dir / "degradation_raw_vs_monotone_proxy.csv")
    write_json(
        output_dir / "degradation_summary.json",
        {
            "n_specimens_fit": int(best_df["specimen_id"].nunique()),
            "family_counts": best_df["best_family"].value_counts().to_dict(),
            "hidden_damage_best_model_name": best_info["best_model_name"],
            "hidden_damage_feature_set_name": best_info.get("feature_set_name", ""),
            "hidden_damage_target_transform": best_info.get("target_transform", "none"),
        },
    )

    observed_for_plot = (
        working_df[["specimen_id", "ageing_days", "predicted_wire_area_loss_frac"]]
        .rename(columns={"ageing_days": "day"})
        .copy()
    )
    observed_for_plot["source"] = "observed_proxy"
    grid_for_plot = grid_df.rename(columns={"predicted_wire_area_loss_frac": "value", "day": "day"})
    grid_for_plot["source"] = "fitted_curve"
    observed_for_plot = observed_for_plot.rename(columns={"predicted_wire_area_loss_frac": "value"})
    plot_df = pd.concat([observed_for_plot, grid_for_plot], ignore_index=True, sort=False)
    plot_subset = plot_df.loc[plot_df["specimen_id"].isin(sorted(best_df["specimen_id"].tolist())[:12])]
    save_lineplot(
        plot_subset,
        x="day",
        y="value",
        hue="specimen_id",
        style="source",
        title="Predicted Hidden-Damage Trajectories (subset of specimens)",
        path=output_dir / "degradation_subset_trajectories.png",
    )
    return working_df, best_df, grid_df

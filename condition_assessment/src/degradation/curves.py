from __future__ import annotations

from dataclasses import dataclass
import json

import numpy as np
from scipy.optimize import curve_fit
from sklearn.metrics import mean_squared_error, r2_score


@dataclass(frozen=True)
class CurveFitResult:
    model_name: str
    params_json: str
    rmse: float
    r2: float
    n_obs: int


def linear_model(x: np.ndarray, a: float, b: float) -> np.ndarray:
    return a + b * x


def exponential_model(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    return a * np.exp(b * x) + c


def logarithmic_model(x: np.ndarray, a: float, b: float) -> np.ndarray:
    return a + b * np.log1p(x)


def piecewise_linear_predict(
    x: np.ndarray,
    breakpoint: float,
    a1: float,
    b1: float,
    a2: float,
    b2: float,
) -> np.ndarray:
    return np.where(x <= breakpoint, a1 + b1 * x, a2 + b2 * x)


def _summarize(model_name: str, params: list[float], y_true: np.ndarray, y_pred: np.ndarray) -> CurveFitResult:
    return CurveFitResult(
        model_name=model_name,
        params_json=json.dumps([float(v) for v in params]),
        rmse=float(np.sqrt(mean_squared_error(y_true, y_pred))),
        r2=float(r2_score(y_true, y_pred)),
        n_obs=int(len(y_true)),
    )


def fit_linear(x: np.ndarray, y: np.ndarray) -> CurveFitResult:
    slope, intercept = np.polyfit(x, y, deg=1)
    pred = linear_model(x, intercept, slope)
    return _summarize("linear", [intercept, slope], y, pred)


def fit_logarithmic(x: np.ndarray, y: np.ndarray) -> CurveFitResult:
    params, _ = curve_fit(logarithmic_model, x, y, maxfev=5000)
    pred = logarithmic_model(x, *params)
    return _summarize("logarithmic", list(params), y, pred)


def fit_exponential(x: np.ndarray, y: np.ndarray) -> CurveFitResult:
    init_a = float(max(y[0] - y[-1], 0.1))
    init_b = 0.02 if y[-1] >= y[0] else -0.02
    init_c = float(min(y.min(), y.max()))
    params, _ = curve_fit(
        exponential_model,
        x,
        y,
        p0=[init_a, init_b, init_c],
        maxfev=10000,
    )
    pred = exponential_model(x, *params)
    return _summarize("exponential", list(params), y, pred)


def fit_piecewise_linear(x: np.ndarray, y: np.ndarray) -> CurveFitResult:
    if len(x) < 6:
        raise ValueError("Piecewise linear fit requires at least 6 observations.")
    candidate_breaks = x[2:-2]
    best_result: CurveFitResult | None = None
    for breakpoint in candidate_breaks:
        left_mask = x <= breakpoint
        right_mask = x > breakpoint
        if left_mask.sum() < 2 or right_mask.sum() < 2:
            continue
        left_slope, left_intercept = np.polyfit(x[left_mask], y[left_mask], deg=1)
        right_slope, right_intercept = np.polyfit(x[right_mask], y[right_mask], deg=1)
        pred = piecewise_linear_predict(
            x,
            breakpoint=breakpoint,
            a1=left_intercept,
            b1=left_slope,
            a2=right_intercept,
            b2=right_slope,
        )
        result = _summarize(
            "piecewise_linear",
            [breakpoint, left_intercept, left_slope, right_intercept, right_slope],
            y,
            pred,
        )
        if best_result is None or result.rmse < best_result.rmse:
            best_result = result
    if best_result is None:
        raise ValueError("No valid piecewise breakpoint found.")
    return best_result


def fit_best_curve(x: np.ndarray, y: np.ndarray) -> CurveFitResult:
    candidates: list[CurveFitResult] = []
    for fitter in (fit_linear, fit_exponential, fit_logarithmic, fit_piecewise_linear):
        try:
            candidates.append(fitter(x, y))
        except Exception:
            continue
    if not candidates:
        raise ValueError("No degradation curve could be fitted.")
    return min(candidates, key=lambda item: item.rmse)


def predict_curve(result: CurveFitResult, x: np.ndarray) -> np.ndarray:
    params = json.loads(result.params_json)
    if result.model_name == "linear":
        return linear_model(x, *params)
    if result.model_name == "exponential":
        return exponential_model(x, *params)
    if result.model_name == "logarithmic":
        return logarithmic_model(x, *params)
    if result.model_name == "piecewise_linear":
        return piecewise_linear_predict(x, *params)
    raise ValueError(f"Unsupported curve model: {result.model_name}")

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from scipy.stats import spearmanr
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

from .utils_paths import ensure_dir, save_dataframe_csv, write_json


def regression_metrics(y_true, y_pred):
    spearman = spearmanr(y_true, y_pred).statistic
    if len(y_true) < 2:
        r2_value = float("nan")
    else:
        r2_value = float(r2_score(y_true, y_pred))
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": r2_value,
        "spearman": float(0.0 if np.isnan(spearman) else spearman),
    }


def build_regression_models(modeling_cfg: dict):
    random_state = modeling_cfg["random_state"]
    models_cfg = modeling_cfg["models"]
    return {
        "RandomForest": RandomForestRegressor(
            random_state=random_state, **models_cfg["random_forest"]
        ),
        "GradientBoosting": GradientBoostingRegressor(
            random_state=random_state, **models_cfg["gradient_boosting"]
        ),
        "XGBoost": XGBRegressor(
            random_state=random_state,
            objective="reg:squarederror",
            tree_method="hist",
            **models_cfg["xgboost"],
        ),
        "CatBoost": CatBoostRegressor(
            random_seed=random_state,
            verbose=False,
            **models_cfg["catboost"],
        ),
    }


def _transform_target(y_values, target_transform: str):
    values = np.asarray(y_values, dtype=float)
    if target_transform == "none":
        return values
    if target_transform == "sqrt":
        return np.sqrt(np.clip(values, 0.0, None))
    raise ValueError(f"Unsupported target transform: {target_transform}")


def _inverse_transform_target(y_values, target_transform: str):
    values = np.asarray(y_values, dtype=float)
    if target_transform == "none":
        return values
    if target_transform == "sqrt":
        return np.square(np.clip(values, 0.0, None))
    raise ValueError(f"Unsupported target transform: {target_transform}")


def fit_model_bundle(
    model,
    x_train: pd.DataFrame,
    y_train: pd.Series,
    target_transform: str = "none",
):
    train_encoded = pd.get_dummies(x_train, dummy_na=False).astype(float)
    fitted = deepcopy(model)
    transformed_y = _transform_target(y_train.to_numpy(dtype=float), target_transform)
    fitted.fit(train_encoded, transformed_y)
    return {
        "model": fitted,
        "columns": list(train_encoded.columns),
        "target_transform": target_transform,
    }


def predict_model_bundle(bundle, x_data: pd.DataFrame):
    encoded = pd.get_dummies(x_data, dummy_na=False).astype(float)
    encoded = encoded.reindex(columns=bundle["columns"], fill_value=0.0)
    raw_preds = bundle["model"].predict(encoded)
    return _inverse_transform_target(raw_preds, bundle.get("target_transform", "none"))


def extract_feature_importance(bundle):
    model = bundle["model"]
    columns = bundle["columns"]
    if hasattr(model, "feature_importances_"):
        values = model.feature_importances_
    elif hasattr(model, "get_feature_importance"):
        values = model.get_feature_importance()
    else:
        return pd.DataFrame(columns=["feature", "importance"])
    return (
        pd.DataFrame({"feature": columns, "importance": values})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )


def benchmark_models(
    df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
    manifest_df: pd.DataFrame,
    modeling_cfg: dict,
    output_dir: Path,
    model_names: list[str] | None = None,
    target_transform: str = "none",
    selected_model_name: str | None = None,
):
    ensure_dir(output_dir)
    models = build_regression_models(modeling_cfg)
    if model_names is not None:
        models = {name: models[name] for name in model_names}

    indexed = df.set_index("sample_name", drop=False)
    metric_rows = []
    prediction_rows = []

    for model_name, model in models.items():
        for split_id, split_df in manifest_df.groupby("split_id"):
            train_names = split_df.loc[split_df["membership"] == "train", "sample_name"]
            test_names = split_df.loc[split_df["membership"] == "test", "sample_name"]
            train_df = indexed.loc[train_names]
            test_df = indexed.loc[test_names]

            x_train = train_df[feature_cols]
            y_train = train_df[target_col]
            x_test = test_df[feature_cols]
            y_test = test_df[target_col]

            bundle = fit_model_bundle(model, x_train, y_train, target_transform=target_transform)
            preds = predict_model_bundle(bundle, x_test)
            metrics = regression_metrics(y_test, preds)
            metric_rows.append(
                {
                    "target": target_col,
                    "model_name": model_name,
                    "target_transform": target_transform,
                    "split_id": split_id,
                    **metrics,
                }
            )
            prediction_rows.extend(
                {
                    "target": target_col,
                    "model_name": model_name,
                    "target_transform": target_transform,
                    "split_id": split_id,
                    "sample_name": sample_name,
                    "y_true": y_true,
                    "y_pred": y_pred,
                }
                for sample_name, y_true, y_pred in zip(test_df["sample_name"], y_test, preds)
            )

    metrics_df = pd.DataFrame(metric_rows)
    predictions_df = pd.DataFrame(prediction_rows)
    summary_df = (
        metrics_df.groupby(["target", "model_name", "target_transform"])[["mae", "rmse", "r2", "spearman"]]
        .agg(["mean", "std"])
        .reset_index()
    )
    summary_df.columns = [
        "_".join(col).strip("_") if isinstance(col, tuple) else col for col in summary_df.columns
    ]
    summary_df = summary_df.sort_values("mae_mean").reset_index(drop=True)
    best_model_name = selected_model_name or summary_df.iloc[0]["model_name"]

    best_model = build_regression_models(modeling_cfg)[best_model_name]
    best_bundle = fit_model_bundle(
        best_model,
        df[feature_cols],
        df[target_col],
        target_transform=target_transform,
    )
    joblib.dump(best_bundle, output_dir / f"{target_col}_best_model.joblib")

    importance_df = extract_feature_importance(best_bundle)

    save_dataframe_csv(metrics_df, output_dir / f"{target_col}_fold_metrics.csv")
    save_dataframe_csv(predictions_df, output_dir / f"{target_col}_predictions.csv")
    save_dataframe_csv(summary_df, output_dir / f"{target_col}_summary.csv")
    save_dataframe_csv(importance_df, output_dir / f"{target_col}_feature_importance.csv")
    write_json(
        output_dir / f"{target_col}_best_model.json",
        {
            "target": target_col,
            "best_model_name": best_model_name,
            "target_transform": target_transform,
        },
    )

    return {
        "metrics": metrics_df,
        "summary": summary_df,
        "predictions": predictions_df,
        "importance": importance_df,
        "best_model_name": best_model_name,
        "best_bundle": best_bundle,
    }

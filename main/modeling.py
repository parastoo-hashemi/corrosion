from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


@dataclass
class BenchmarkOutput:
    metrics: pd.DataFrame
    best_model_name: str
    best_pipeline: Pipeline
    holdout_metrics: Dict[str, float]
    feature_names: np.ndarray


def get_model_candidates(random_state: int = 42) -> Dict[str, object]:
    models: Dict[str, object] = {
        "ElasticNet": ElasticNet(
            alpha=0.02, l1_ratio=0.2, random_state=random_state, max_iter=10000
        ),
        "RandomForest": RandomForestRegressor(
            n_estimators=500,
            random_state=random_state,
            n_jobs=-1,
            min_samples_leaf=2,
        ),
        "GradientBoosting": GradientBoostingRegressor(random_state=random_state),
    }
    try:
        from xgboost import XGBRegressor

        models["XGBoost"] = XGBRegressor(
            n_estimators=600,
            learning_rate=0.03,
            max_depth=6,
            subsample=0.9,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            random_state=random_state,
            n_jobs=8,
        )
    except Exception:
        pass
    return models


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    cat_cols = [c for c in X.columns if not is_numeric_dtype(X[c])]
    num_cols = [c for c in X.columns if c not in cat_cols]
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                num_cols,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        (
                            "onehot",
                            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                        ),
                    ]
                ),
                cat_cols,
            ),
        ]
    )
    return preprocessor


def evaluate_models(
    X: pd.DataFrame,
    y: pd.Series,
    groups: pd.Series,
    random_state: int = 42,
    holdout_size: float = 0.2,
) -> BenchmarkOutput:
    models = get_model_candidates(random_state=random_state)
    preprocessor = build_preprocessor(X)

    gss = GroupShuffleSplit(
        n_splits=1, test_size=holdout_size, random_state=random_state
    )
    train_idx, holdout_idx = next(gss.split(X, y, groups))

    X_train = X.iloc[train_idx]
    y_train = y.iloc[train_idx]
    g_train = groups.iloc[train_idx]
    X_holdout = X.iloc[holdout_idx]
    y_holdout = y.iloc[holdout_idx]

    n_splits = min(5, int(g_train.nunique()))
    if n_splits < 2:
        raise ValueError("Not enough unique groups for grouped cross-validation.")
    gkf = GroupKFold(n_splits=n_splits)

    rows = []
    fitted_holdout_models: Dict[str, Pipeline] = {}
    for model_name, model in models.items():
        pipeline = Pipeline(
            steps=[("preprocessor", preprocessor), ("regressor", model)]
        )
        cv_mae, cv_rmse, cv_r2 = [], [], []

        for tr_i, va_i in gkf.split(X_train, y_train, g_train):
            pipeline.fit(X_train.iloc[tr_i], y_train.iloc[tr_i])
            pred = pipeline.predict(X_train.iloc[va_i])
            cv_mae.append(mean_absolute_error(y_train.iloc[va_i], pred))
            cv_rmse.append(np.sqrt(mean_squared_error(y_train.iloc[va_i], pred)))
            cv_r2.append(r2_score(y_train.iloc[va_i], pred))

        pipeline.fit(X_train, y_train)
        holdout_pred = pipeline.predict(X_holdout)
        holdout_mae = mean_absolute_error(y_holdout, holdout_pred)
        holdout_rmse = np.sqrt(mean_squared_error(y_holdout, holdout_pred))
        holdout_r2 = r2_score(y_holdout, holdout_pred)

        rows.append(
            {
                "model": model_name,
                "cv_mae": float(np.mean(cv_mae)),
                "cv_rmse": float(np.mean(cv_rmse)),
                "cv_r2": float(np.mean(cv_r2)),
                "holdout_mae": float(holdout_mae),
                "holdout_rmse": float(holdout_rmse),
                "holdout_r2": float(holdout_r2),
            }
        )
        fitted_holdout_models[model_name] = pipeline

    metrics = pd.DataFrame(rows).sort_values(
        ["holdout_mae", "cv_mae", "holdout_rmse"], ascending=[True, True, True]
    )
    best_name = str(metrics.iloc[0]["model"])

    # Refit best model on full dataset for production usage.
    best_pipeline = Pipeline(
        steps=[("preprocessor", preprocessor), ("regressor", models[best_name])]
    )
    best_pipeline.fit(X, y)
    feature_names = best_pipeline.named_steps["preprocessor"].get_feature_names_out()

    holdout_row = (
        metrics.loc[metrics["model"] == best_name]
        .iloc[0][["holdout_mae", "holdout_rmse", "holdout_r2"]]
        .to_dict()
    )
    holdout_row = {k: float(v) for k, v in holdout_row.items()}

    return BenchmarkOutput(
        metrics=metrics,
        best_model_name=best_name,
        best_pipeline=best_pipeline,
        holdout_metrics=holdout_row,
        feature_names=feature_names,
    )


def get_feature_importance(
    fitted_pipeline: Pipeline, transformed_feature_names: np.ndarray, top_k: int = 25
) -> pd.DataFrame:
    regressor = fitted_pipeline.named_steps["regressor"]

    if hasattr(regressor, "feature_importances_"):
        values = np.asarray(regressor.feature_importances_, dtype=float)
    elif hasattr(regressor, "coef_"):
        values = np.abs(np.asarray(regressor.coef_, dtype=float)).ravel()
    else:
        return pd.DataFrame(columns=["feature", "importance"])

    out = pd.DataFrame(
        {"feature": transformed_feature_names, "importance": values}
    ).sort_values("importance", ascending=False)
    return out.head(top_k).reset_index(drop=True)


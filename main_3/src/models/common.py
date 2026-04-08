from __future__ import annotations

from dataclasses import dataclass
import importlib
from typing import Callable

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.cv.splits import SplitDefinition, build_splits
from src.evaluation.metrics import classification_metrics, regression_metrics


ModelFactory = Callable[[int], object]


@dataclass
class EvaluationResult:
    metrics: pd.DataFrame
    predictions: pd.DataFrame
    fitted_estimators: dict[str, Pipeline]


def available_optional_module(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def build_preprocessor(frame: pd.DataFrame, feature_cols: list[str]) -> ColumnTransformer:
    cat_cols = [col for col in feature_cols if frame[col].dtype == object]
    num_cols = [col for col in feature_cols if col not in cat_cols]
    return ColumnTransformer(
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


def build_pipeline(
    model: object,
    train_frame: pd.DataFrame,
    feature_cols: list[str],
) -> Pipeline:
    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor(train_frame, feature_cols=feature_cols)),
            ("model", clone(model)),
        ]
    )


def evaluate_models(
    dataset: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
    model_factories: dict[str, ModelFactory],
    strategies: list[str],
    task: str,
    random_state: int,
    test_size: float,
) -> EvaluationResult:
    metric_rows: list[dict[str, object]] = []
    prediction_rows: list[dict[str, object]] = []
    fitted_estimators: dict[str, Pipeline] = {}

    for strategy in strategies:
        splits = build_splits(
            dataset,
            strategy=strategy,
            random_state=random_state,
            test_size=test_size,
        )
        for model_name, factory in model_factories.items():
            for split in splits:
                train_df = dataset.iloc[split.train_idx].copy()
                test_df = dataset.iloc[split.test_idx].copy()

                y_train = train_df[target_col]
                y_test = test_df[target_col]
                if y_train.dropna().nunique() < 2:
                    continue

                estimator = build_pipeline(
                    model=factory(random_state),
                    train_frame=train_df[feature_cols],
                    feature_cols=feature_cols,
                )
                estimator.fit(train_df[feature_cols], y_train)
                y_pred = estimator.predict(test_df[feature_cols])

                if task == "regression":
                    fold_metrics = regression_metrics(
                        y_true=y_test.to_numpy(dtype=float),
                        y_pred=np.asarray(y_pred, dtype=float),
                    )
                    primary_metric = fold_metrics["mae"]
                elif task == "classification":
                    fold_metrics = classification_metrics(
                        y_true=y_test.to_numpy(),
                        y_pred=np.asarray(y_pred),
                    )
                    primary_metric = fold_metrics["macro_f1"]
                else:
                    raise ValueError(f"Unsupported task: {task}")

                metric_rows.append(
                    {
                        "strategy": strategy,
                        "fold_id": split.fold_id,
                        "holdout_group": split.holdout_group,
                        "model": model_name,
                        "target": target_col,
                        "task": task,
                        "n_train": len(train_df),
                        "n_test": len(test_df),
                        **fold_metrics,
                    }
                )
                for row_idx, (record_id, actual, predicted) in enumerate(
                    zip(test_df["record_id"], y_test, y_pred)
                ):
                    prediction_rows.append(
                        {
                            "strategy": strategy,
                            "fold_id": split.fold_id,
                            "holdout_group": split.holdout_group,
                            "model": model_name,
                            "target": target_col,
                            "record_id": record_id,
                            "y_true": actual,
                            "y_pred": predicted,
                        }
                    )

                if strategy == "group_shuffle":
                    key = f"{target_col}::{model_name}"
                    existing = fitted_estimators.get(key)
                    if existing is None:
                        fitted_estimators[key] = estimator
                    else:
                        existing_score = next(
                            (
                                row["mae"] if task == "regression" else -row["macro_f1"]
                                for row in metric_rows
                                if row["strategy"] == strategy
                                and row["model"] == model_name
                                and row["target"] == target_col
                            ),
                            None,
                        )
                        replace = False
                        if existing_score is None:
                            replace = True
                        elif task == "regression" and primary_metric < existing_score:
                            replace = True
                        elif task == "classification" and primary_metric > -existing_score:
                            replace = True
                        if replace:
                            fitted_estimators[key] = estimator

    return EvaluationResult(
        metrics=pd.DataFrame(metric_rows),
        predictions=pd.DataFrame(prediction_rows),
        fitted_estimators=fitted_estimators,
    )


def select_best_model(metrics_df: pd.DataFrame, target_col: str, task: str) -> str:
    subset = metrics_df[
        (metrics_df["strategy"] == "group_shuffle") & (metrics_df["target"] == target_col)
    ].copy()
    if subset.empty:
        raise ValueError(f"No metrics available for target: {target_col}")
    grouped = subset.groupby("model", as_index=False).mean(numeric_only=True)
    if task == "regression":
        return str(grouped.sort_values("mae").iloc[0]["model"])
    return str(grouped.sort_values("macro_f1", ascending=False).iloc[0]["model"])


def fit_full_pipeline(
    dataset: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
    model_factory: ModelFactory,
    random_state: int,
) -> Pipeline:
    estimator = build_pipeline(
        model=model_factory(random_state),
        train_frame=dataset[feature_cols],
        feature_cols=feature_cols,
    )
    estimator.fit(dataset[feature_cols], dataset[target_col])
    return estimator


def save_estimator(estimator: Pipeline, path: str) -> None:
    joblib.dump(estimator, path)

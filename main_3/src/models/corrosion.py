from __future__ import annotations

from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor, RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.neural_network import MLPClassifier, MLPRegressor


def corrosion_regressor_factories() -> dict[str, callable]:
    return {
        "linear_regression": lambda random_state: LinearRegression(),
        "random_forest": lambda random_state: RandomForestRegressor(
            n_estimators=400,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
        ),
        "hist_gradient_boosting": lambda random_state: HistGradientBoostingRegressor(
            learning_rate=0.05,
            max_depth=6,
            max_iter=400,
            random_state=random_state,
        ),
        "mlp_regressor": lambda random_state: MLPRegressor(
            hidden_layer_sizes=(128, 64),
            activation="relu",
            solver="adam",
            early_stopping=True,
            max_iter=600,
            random_state=random_state,
        ),
    }


def corrosion_classifier_factories() -> dict[str, callable]:
    return {
        "logistic_regression": lambda random_state: LogisticRegression(
            max_iter=2000,
        ),
        "random_forest": lambda random_state: RandomForestClassifier(
            n_estimators=400,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
        ),
        "hist_gradient_boosting": lambda random_state: HistGradientBoostingClassifier(
            learning_rate=0.05,
            max_depth=6,
            max_iter=300,
            random_state=random_state,
        ),
        "mlp_classifier": lambda random_state: MLPClassifier(
            hidden_layer_sizes=(128, 64),
            activation="relu",
            early_stopping=True,
            max_iter=600,
            random_state=random_state,
        ),
    }

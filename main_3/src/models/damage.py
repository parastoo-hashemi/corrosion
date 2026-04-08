from __future__ import annotations

import importlib.util

from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.neural_network import MLPRegressor


def damage_regressor_factories() -> dict[str, callable]:
    factories: dict[str, callable] = {
        "random_forest": lambda random_state: RandomForestRegressor(
            n_estimators=400,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
        ),
        "extra_trees": lambda random_state: ExtraTreesRegressor(
            n_estimators=500,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
        ),
        "hist_gradient_boosting": lambda random_state: HistGradientBoostingRegressor(
            learning_rate=0.05,
            max_depth=5,
            max_iter=300,
            random_state=random_state,
        ),
        "mlp_regressor": lambda random_state: MLPRegressor(
            hidden_layer_sizes=(64, 32),
            activation="relu",
            early_stopping=True,
            max_iter=600,
            random_state=random_state,
        ),
    }
    if importlib.util.find_spec("xgboost") is not None:
        from xgboost import XGBRegressor

        factories["xgboost"] = lambda random_state: XGBRegressor(
            n_estimators=500,
            max_depth=5,
            learning_rate=0.03,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="reg:squarederror",
            random_state=random_state,
            n_jobs=1,
        )
    if importlib.util.find_spec("catboost") is not None:
        from catboost import CatBoostRegressor

        factories["catboost"] = lambda random_state: CatBoostRegressor(
            iterations=500,
            depth=5,
            learning_rate=0.03,
            loss_function="RMSE",
            random_seed=random_state,
            verbose=False,
        )
    return factories

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from scipy.stats import pearsonr, spearmanr
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

from .feature_engineering import build_full_feature_table
from .image_features import extract_image_feature_table, feature_dictionary
from .utils_paths import OUTPUT_DIR, ensure_dir, save_dataframe_csv, write_json, write_text

os.environ.setdefault("MPLCONFIGDIR", str(ensure_dir(OUTPUT_DIR / ".matplotlib")))

import matplotlib.pyplot as plt
import seaborn as sns


sns.set_theme(style="whitegrid")


METADATA_FEATURE_COLUMNS = [
    "campaign_id",
    "series_id",
    "split_group_treatment",
    "treatment_protocol",
    "treatment_coarse",
    "treatment_label_coarse",
    "n_steel_mesh",
    "nacl_pct",
    "cover_mm",
    "week",
    "ageing_days",
]

NON_FEATURE_COLUMNS = {
    "observation_id",
    "sample_name",
    "specimen_id",
    "image_filename",
    "image_path",
    "image_readable",
    "image_width",
    "image_height",
    "image_error",
    "specimen_id_from_name",
    "date",
    "calendar_date",
    "surface_total_rust_pct",
    "surface_total_rust_category",
    "peak_rust_pct",
    "peak_rust_category",
    "peak_rust_location_cm",
    "wire_area_loss_raw",
    "wire_area_loss_frac",
    "wire_area_loss_pct",
    "ultimate_load_kn",
    "has_structural_label",
    "is_terminal_structural_row",
    "terminal_week",
    "terminal_days",
    "is_measured_ultimate_load",
    "is_measured_wire_area_loss",
    "terminal_ultimate_load_kn_target",
    "terminal_wire_area_loss_frac_target",
    "visible_corrosion_onset_week",
    "is_post_visible_corrosion_onset",
    "onset_threshold_column",
    "onset_threshold_pct",
}


def regression_metrics(y_true: pd.Series | np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    y_true_array = np.asarray(y_true, dtype=float)
    y_pred_array = np.asarray(y_pred, dtype=float)
    if y_true_array.size == 0:
        return {"mae": float("nan"), "rmse": float("nan"), "r2": float("nan"), "spearman": float("nan")}
    spearman_value = spearmanr(y_true_array, y_pred_array).statistic
    r2_value = float("nan") if y_true_array.size < 2 else float(r2_score(y_true_array, y_pred_array))
    return {
        "mae": float(mean_absolute_error(y_true_array, y_pred_array)),
        "rmse": float(np.sqrt(mean_squared_error(y_true_array, y_pred_array))),
        "r2": r2_value,
        "spearman": float(0.0 if np.isnan(spearman_value) else spearman_value),
    }


def _json_counts(series: pd.Series) -> str:
    counts = {str(key): int(value) for key, value in series.value_counts().sort_index().items()}
    return json.dumps(counts, sort_keys=True)


def _safe_corr(x_values: pd.Series, y_values: pd.Series) -> tuple[float, float, float, float]:
    valid = pd.concat([x_values, y_values], axis=1).dropna()
    if len(valid) < 3 or valid.iloc[:, 0].nunique() < 2 or valid.iloc[:, 1].nunique() < 2:
        return float("nan"), float("nan"), float("nan"), float("nan")
    pearson_r, pearson_p = pearsonr(valid.iloc[:, 0], valid.iloc[:, 1])
    spearman_rho, spearman_p = spearmanr(valid.iloc[:, 0], valid.iloc[:, 1])
    return float(pearson_r), float(pearson_p), float(spearman_rho), float(spearman_p)


def _one_hot_encoder() -> OneHotEncoder:
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:  # pragma: no cover - older sklearn fallback
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def _build_model(model_name: str, modeling_cfg: dict, refocus_cfg: dict):
    random_state = int(modeling_cfg["random_state"])
    models_cfg = modeling_cfg["models"]
    if model_name == "RandomForest":
        return RandomForestRegressor(random_state=random_state, **models_cfg["random_forest"])
    if model_name == "GradientBoosting":
        return GradientBoostingRegressor(random_state=random_state, **models_cfg["gradient_boosting"])
    if model_name == "XGBoost":
        return XGBRegressor(
            random_state=random_state,
            objective="reg:squarederror",
            tree_method="hist",
            **models_cfg["xgboost"],
        )
    if model_name == "CatBoost":
        return CatBoostRegressor(random_seed=random_state, verbose=False, **models_cfg["catboost"])
    if model_name == "Ridge":
        return Ridge(**refocus_cfg["models"]["ridge"])
    raise ValueError(f"Unsupported model name: {model_name}")


def _classify_feature_family(column: str) -> str:
    if column.startswith("img_hsv_"):
        return "hsv"
    if column.startswith("img_"):
        return "rgb"
    if column in METADATA_FEATURE_COLUMNS:
        return "metadata"
    return "excluded"


def build_feature_family_inventory(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in sorted(df.columns):
        family = _classify_feature_family(column)
        rows.append(
            {
                "column_name": column,
                "feature_family": family,
                "is_candidate_feature": family != "excluded" and column not in NON_FEATURE_COLUMNS,
                "dtype": str(df[column].dtype),
                "missing_count": int(df[column].isna().sum()),
                "n_unique": int(df[column].nunique(dropna=True)),
            }
        )
    return pd.DataFrame(rows)


def _build_refocus_table(master_df: pd.DataFrame, image_feature_df: pd.DataFrame, refocus_cfg: dict) -> pd.DataFrame:
    full_df = build_full_feature_table(master_df, image_feature_df)
    terminal_targets = (
        master_df.loc[master_df["ultimate_load_kn"].notna(), ["specimen_id", "ultimate_load_kn", "wire_area_loss_frac"]]
        .drop_duplicates(subset=["specimen_id"])
        .rename(
            columns={
                "ultimate_load_kn": "terminal_ultimate_load_kn_target",
                "wire_area_loss_frac": "terminal_wire_area_loss_frac_target",
            }
        )
    )
    if terminal_targets["specimen_id"].nunique() != master_df.loc[master_df["ultimate_load_kn"].notna(), "specimen_id"].nunique():
        raise ValueError("Expected one terminal structural target row per specimen.")

    refocus_df = full_df.merge(terminal_targets, on="specimen_id", how="left", validate="many_to_one")
    refocus_df["is_measured_ultimate_load"] = refocus_df["ultimate_load_kn"].notna()
    refocus_df["is_measured_wire_area_loss"] = refocus_df["wire_area_loss_frac"].notna()

    threshold_column = refocus_cfg["surface_onset"]["threshold_column"]
    threshold_pct = float(refocus_cfg["surface_onset"]["threshold_pct"])
    onset_df = (
        refocus_df.sort_values(["specimen_id", "week"])
        .loc[refocus_df[threshold_column] >= threshold_pct, ["specimen_id", "week"]]
        .groupby("specimen_id", as_index=False)["week"]
        .min()
        .rename(columns={"week": "visible_corrosion_onset_week"})
    )
    refocus_df = refocus_df.merge(onset_df, on="specimen_id", how="left", validate="many_to_one")
    refocus_df["is_post_visible_corrosion_onset"] = (
        refocus_df["visible_corrosion_onset_week"].notna()
        & (refocus_df["week"] >= refocus_df["visible_corrosion_onset_week"])
    )
    refocus_df["onset_threshold_column"] = threshold_column
    refocus_df["onset_threshold_pct"] = threshold_pct
    return refocus_df.sort_values(["specimen_id", "week"]).reset_index(drop=True)


def build_specimen_manifest(refocus_df: pd.DataFrame) -> pd.DataFrame:
    grouped = refocus_df.sort_values(["specimen_id", "week"]).groupby("specimen_id", as_index=False)
    specimen_df = grouped.agg(
        campaign_id=("campaign_id", "main_first"),
        series_id=("series_id", "main_first"),
        split_group_treatment=("split_group_treatment", "main_first"),
        treatment_protocol=("treatment_protocol", "main_first"),
        treatment_coarse=("treatment_coarse", "main_first"),
        treatment_label_coarse=("treatment_label_coarse", "main_first"),
        n_steel_mesh=("n_steel_mesh", "main_first"),
        nacl_pct=("nacl_pct", "main_first"),
        cover_mm=("cover_mm", "main_first"),
        terminal_week=("terminal_week", "main_first"),
        terminal_days=("terminal_days", "main_first"),
        visible_corrosion_onset_week=("visible_corrosion_onset_week", "main_first"),
        n_rows_all_weeks=("sample_name", "count"),
        n_rows_post_onset=("is_post_visible_corrosion_onset", "sum"),
        n_measured_ultimate_rows=("is_measured_ultimate_load", "sum"),
        terminal_ultimate_load_kn_target=("terminal_ultimate_load_kn_target", "main_first"),
        terminal_wire_area_loss_frac_target=("terminal_wire_area_loss_frac_target", "main_first"),
    )
    specimen_df["is_measured_ultimate_load"] = specimen_df["n_measured_ultimate_rows"] > 0
    return specimen_df.sort_values(["n_steel_mesh", "campaign_id", "specimen_id"]).reset_index(drop=True)


def _build_specimen_cv_manifest(
    specimen_df: pd.DataFrame,
    split_name: str,
    n_splits: int,
    n_repeats: int,
    random_state: int,
    stratify_col: str | None,
) -> pd.DataFrame:
    specimen_df = specimen_df.sort_values("specimen_id").reset_index(drop=True)
    rows: list[dict[str, object]] = []
    stratify_values = None
    if stratify_col and stratify_col in specimen_df.columns and specimen_df[stratify_col].nunique() > 1:
        stratify_values = specimen_df[stratify_col]

    for repeat_idx in range(n_repeats):
        if stratify_values is not None:
            splitter = StratifiedKFold(
                n_splits=n_splits,
                shuffle=True,
                random_state=random_state + repeat_idx,
            )
            split_iter = splitter.split(specimen_df, stratify_values)
        else:
            splitter = KFold(n_splits=n_splits, shuffle=True, random_state=random_state + repeat_idx)
            split_iter = splitter.split(specimen_df)

        for fold_idx, (train_idx, test_idx) in enumerate(split_iter):
            split_id = f"{split_name}_repeat{repeat_idx}_fold{fold_idx}"
            for membership, indices in [("train", train_idx), ("test", test_idx)]:
                subset = specimen_df.iloc[indices]
                for row in subset.itertuples(index=False):
                    rows.append(
                        {
                            "split_name": split_name,
                            "repeat_id": repeat_idx,
                            "fold_id": fold_idx,
                            "split_id": split_id,
                            "membership": membership,
                            "specimen_id": row.specimen_id,
                            "campaign_id": row.campaign_id,
                            "n_steel_mesh": row.n_steel_mesh,
                            "series_id": row.series_id,
                            "split_group_treatment": row.split_group_treatment,
                        }
                    )
    return pd.DataFrame(rows)


def _build_leave_one_campaign_out_manifest(specimen_df: pd.DataFrame, split_name: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    specimen_df = specimen_df.sort_values(["campaign_id", "specimen_id"]).reset_index(drop=True)
    for fold_idx, campaign_id in enumerate(sorted(specimen_df["campaign_id"].dropna().unique().tolist())):
        split_id = f"{split_name}_{campaign_id}"
        for membership, subset in [
            ("train", specimen_df.loc[specimen_df["campaign_id"] != campaign_id]),
            ("test", specimen_df.loc[specimen_df["campaign_id"] == campaign_id]),
        ]:
            for row in subset.itertuples(index=False):
                rows.append(
                    {
                        "split_name": split_name,
                        "repeat_id": 0,
                        "fold_id": fold_idx,
                        "split_id": split_id,
                        "membership": membership,
                        "specimen_id": row.specimen_id,
                        "campaign_id": row.campaign_id,
                        "n_steel_mesh": row.n_steel_mesh,
                        "series_id": row.series_id,
                        "split_group_treatment": row.split_group_treatment,
                    }
                )
    return pd.DataFrame(rows)


def expand_specimen_manifest_to_rows(data_df: pd.DataFrame, specimen_manifest_df: pd.DataFrame) -> pd.DataFrame:
    sample_index = data_df[
        ["sample_name", "specimen_id", "week", "campaign_id", "n_steel_mesh", "is_measured_ultimate_load"]
    ].copy()
    row_manifest = specimen_manifest_df.merge(sample_index, on=["specimen_id", "campaign_id", "n_steel_mesh"], how="left")
    return row_manifest.sort_values(["split_name", "repeat_id", "fold_id", "membership", "specimen_id", "week"]).reset_index(drop=True)


def summarize_split_balance(specimen_manifest_df: pd.DataFrame, row_manifest_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for split_id, split_df in specimen_manifest_df.groupby("split_id"):
        train_specimens = split_df.loc[split_df["membership"] == "train", "specimen_id"]
        test_specimens = split_df.loc[split_df["membership"] == "test", "specimen_id"]
        train_rows = row_manifest_df.loc[(row_manifest_df["split_id"] == split_id) & (row_manifest_df["membership"] == "train")]
        test_rows = row_manifest_df.loc[(row_manifest_df["split_id"] == split_id) & (row_manifest_df["membership"] == "test")]
        leakage_safe = set(train_specimens).isdisjoint(set(test_specimens))
        rows.append(
            {
                "split_name": split_df["split_name"].iloc[0],
                "repeat_id": int(split_df["repeat_id"].iloc[0]),
                "fold_id": int(split_df["fold_id"].iloc[0]),
                "split_id": split_id,
                "train_specimens": int(train_specimens.nunique()),
                "test_specimens": int(test_specimens.nunique()),
                "train_rows": int(len(train_rows)),
                "test_rows": int(len(test_rows)),
                "test_terminal_rows": int(test_rows["is_measured_ultimate_load"].sum()),
                "train_mesh_counts": _json_counts(split_df.loc[split_df["membership"] == "train", "n_steel_mesh"]),
                "test_mesh_counts": _json_counts(split_df.loc[split_df["membership"] == "test", "n_steel_mesh"]),
                "train_campaign_counts": _json_counts(split_df.loc[split_df["membership"] == "train", "campaign_id"]),
                "test_campaign_counts": _json_counts(split_df.loc[split_df["membership"] == "test", "campaign_id"]),
                "leakage_safe": bool(leakage_safe),
            }
        )
    return pd.DataFrame(rows).sort_values(["split_name", "repeat_id", "fold_id"]).reset_index(drop=True)


def save_split_balance_plot(summary_df: pd.DataFrame, path: Path, title: str) -> None:
    ensure_dir(path.parent)
    plot_df = summary_df.copy()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    sns.barplot(data=plot_df, x="split_id", y="test_specimens", color="#4C78A8", ax=axes[0])
    axes[0].set_title("Test specimens per split")
    axes[0].set_xlabel("Split id")
    axes[0].set_ylabel("Number of test specimens")
    axes[0].tick_params(axis="x", rotation=90)

    mesh_test_counts = []
    for row in plot_df.itertuples(index=False):
        for mesh_key, count in json.loads(row.test_mesh_counts).items():
            mesh_test_counts.append(
                {
                    "split_id": row.split_id,
                    "n_steel_mesh": mesh_key,
                    "count": count,
                }
            )
    mesh_df = pd.DataFrame(mesh_test_counts)
    sns.barplot(data=mesh_df, x="split_id", y="count", hue="n_steel_mesh", ax=axes[1])
    axes[1].set_title("Test split mesh balance")
    axes[1].set_xlabel("Split id")
    axes[1].set_ylabel("Number of test specimens")
    axes[1].tick_params(axis="x", rotation=90)
    axes[1].legend(title="n_steel_mesh")

    fig.suptitle(title, fontsize=14, y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def build_feature_sets(refocus_df: pd.DataFrame, refocus_cfg: dict) -> dict[str, list[str]]:
    rgb_columns = [
        column
        for column in refocus_df.columns
        if _classify_feature_family(column) == "rgb" and column not in NON_FEATURE_COLUMNS
    ]
    hsv_columns = [
        column
        for column in refocus_df.columns
        if _classify_feature_family(column) == "hsv" and column not in NON_FEATURE_COLUMNS
    ]
    metadata_columns = [
        column
        for column in METADATA_FEATURE_COLUMNS
        if column in refocus_df.columns and column not in NON_FEATURE_COLUMNS
    ]

    family_columns = {
        "metadata": metadata_columns,
        "rgb": rgb_columns,
        "hsv": hsv_columns,
    }

    feature_sets = {}
    for feature_set_name, spec in refocus_cfg["feature_sets"].items():
        columns: list[str] = []
        for family in spec["families"]:
            columns.extend(family_columns[family])
        # Preserve order and drop unsupported all-null columns.
        deduped = []
        for column in columns:
            if column in deduped:
                continue
            if refocus_df[column].notna().sum() == 0:
                continue
            deduped.append(column)
        feature_sets[feature_set_name] = deduped
    return feature_sets


def _build_preprocessor(feature_df: pd.DataFrame, feature_cols: list[str]) -> ColumnTransformer:
    numeric_cols = [column for column in feature_cols if pd.api.types.is_numeric_dtype(feature_df[column])]
    categorical_cols = [column for column in feature_cols if column not in numeric_cols]

    transformers = []
    if numeric_cols:
        transformers.append(
            (
                "num",
                Pipeline([("imputer", SimpleImputer(strategy="median"))]),
                numeric_cols,
            )
        )
    if categorical_cols:
        transformers.append(
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", _one_hot_encoder()),
                    ]
                ),
                categorical_cols,
            )
        )
    return ColumnTransformer(transformers=transformers, remainder="drop")


def fit_model_bundle(
    train_df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
    model_name: str,
    modeling_cfg: dict,
    refocus_cfg: dict,
) -> dict[str, object]:
    train_df = train_df.loc[train_df[target_col].notna()].copy()
    preprocessor = _build_preprocessor(train_df, feature_cols)
    x_train = preprocessor.fit_transform(train_df[feature_cols])
    if not isinstance(x_train, np.ndarray):
        x_train = x_train.toarray()
    scaler = None
    if model_name == "Ridge":
        scaler = StandardScaler()
        x_train = scaler.fit_transform(x_train)

    model = _build_model(model_name, modeling_cfg, refocus_cfg)
    y_train = train_df[target_col].to_numpy(dtype=float)
    if model_name == "CatBoost":
        model.fit(x_train, y_train, verbose=False)
    else:
        model.fit(x_train, y_train)

    return {
        "preprocessor": preprocessor,
        "scaler": scaler,
        "model": model,
        "feature_cols": feature_cols,
        "encoded_feature_names": list(preprocessor.get_feature_names_out()),
    }


def transform_features(bundle: dict[str, object], df: pd.DataFrame) -> np.ndarray:
    transformed = bundle["preprocessor"].transform(df[bundle["feature_cols"]])  # type: ignore[index]
    if not isinstance(transformed, np.ndarray):
        transformed = transformed.toarray()
    scaler = bundle["scaler"]
    if scaler is not None:
        transformed = scaler.transform(transformed)  # type: ignore[union-attr]
    return np.asarray(transformed, dtype=float)


def predict_model_bundle(bundle: dict[str, object], df: pd.DataFrame) -> np.ndarray:
    transformed = transform_features(bundle, df)
    model = bundle["model"]
    return np.asarray(model.predict(transformed), dtype=float)  # type: ignore[call-arg]


def _raw_feature_name(encoded_name: str, feature_cols: list[str]) -> str:
    clean = encoded_name.split("__", 1)[-1]
    for feature in feature_cols:
        if clean == feature or clean.startswith(f"{feature}_"):
            return feature
    return clean


def extract_feature_importance(bundle: dict[str, object]) -> pd.DataFrame:
    model = bundle["model"]
    feature_cols = bundle["feature_cols"]  # type: ignore[assignment]
    encoded_feature_names = bundle["encoded_feature_names"]  # type: ignore[assignment]
    if hasattr(model, "feature_importances_"):
        raw_values = np.asarray(model.feature_importances_, dtype=float)
        importance_kind = "feature_importance"
    elif hasattr(model, "coef_"):
        raw_values = np.asarray(model.coef_, dtype=float).ravel()
        importance_kind = "coefficient"
    else:
        return pd.DataFrame(
            columns=["feature", "importance", "importance_abs", "importance_kind", "direction"]
        )

    rows = []
    for encoded_name, value in zip(encoded_feature_names, raw_values):
        raw_feature = _raw_feature_name(encoded_name, feature_cols)
        rows.append(
            {
                "encoded_feature": encoded_name,
                "feature": raw_feature,
                "importance_raw": float(value),
                "importance_abs": float(abs(value)),
                "importance_kind": importance_kind,
            }
        )
    importance_df = pd.DataFrame(rows)
    aggregated = (
        importance_df.groupby("feature", as_index=False)
        .agg(
            importance=("importance_raw", "sum"),
            importance_abs=("importance_abs", "sum"),
            importance_kind=("importance_kind", "main_first"),
        )
        .sort_values("importance_abs", ascending=False)
        .reset_index(drop=True)
    )
    aggregated["direction"] = np.where(aggregated["importance"] >= 0.0, "positive", "negative")
    return aggregated


def evaluate_experiment(
    analysis_df: pd.DataFrame,
    row_manifest_df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
    measured_target_col: str,
    model_name: str,
    modeling_cfg: dict,
    refocus_cfg: dict,
    predict_all_rows: bool = False,
) -> dict[str, pd.DataFrame | dict[str, object]]:
    indexed = analysis_df.set_index("sample_name", drop=False)
    fold_rows: list[dict[str, object]] = []
    terminal_prediction_rows: list[dict[str, object]] = []
    all_row_prediction_rows: list[dict[str, object]] = []
    importance_rows: list[dict[str, object]] = []

    for split_id, split_df in row_manifest_df.groupby("split_id"):
        train_names = split_df.loc[split_df["membership"] == "train", "sample_name"].tolist()
        test_names = split_df.loc[split_df["membership"] == "test", "sample_name"].tolist()
        train_df = indexed.loc[train_names].copy()
        test_df = indexed.loc[test_names].copy()
        train_df = train_df.loc[train_df[target_col].notna()].copy()
        test_df = test_df.loc[test_df[target_col].notna()].copy()
        train_terminal_df = train_df.loc[train_df["is_measured_ultimate_load"]].copy()
        test_terminal_df = test_df.loc[test_df["is_measured_ultimate_load"]].copy()

        bundle = fit_model_bundle(train_df, feature_cols, target_col, model_name, modeling_cfg, refocus_cfg)
        train_pred = predict_model_bundle(bundle, train_terminal_df)
        test_pred = predict_model_bundle(bundle, test_terminal_df)
        train_metrics = regression_metrics(train_terminal_df[target_col], train_pred)
        test_metrics = regression_metrics(test_terminal_df[target_col], test_pred)

        split_meta = split_df.iloc[0]
        fold_rows.append(
            {
                "split_name": split_meta["split_name"],
                "repeat_id": int(split_meta["repeat_id"]),
                "fold_id": int(split_meta["fold_id"]),
                "split_id": split_id,
                "n_train_rows": int(len(train_df)),
                "n_test_rows": int(len(test_df)),
                "n_train_terminal_rows": int(len(train_terminal_df)),
                "n_test_terminal_rows": int(len(test_terminal_df)),
                "train_specimens": int(train_df["specimen_id"].nunique()),
                "test_specimens": int(test_df["specimen_id"].nunique()),
                "train_mae": train_metrics["mae"],
                "test_mae": test_metrics["mae"],
                "train_rmse": train_metrics["rmse"],
                "test_rmse": test_metrics["rmse"],
                "train_r2": train_metrics["r2"],
                "test_r2": test_metrics["r2"],
                "train_spearman": train_metrics["spearman"],
                "test_spearman": test_metrics["spearman"],
            }
        )

        for row, prediction in zip(test_terminal_df.itertuples(index=False), test_pred):
            terminal_prediction_rows.append(
                {
                    "split_name": split_meta["split_name"],
                    "repeat_id": int(split_meta["repeat_id"]),
                    "fold_id": int(split_meta["fold_id"]),
                    "split_id": split_id,
                    "sample_name": row.sample_name,
                    "specimen_id": row.specimen_id,
                    "campaign_id": row.campaign_id,
                    "series_id": row.series_id,
                    "n_steel_mesh": int(row.n_steel_mesh),
                    "week": int(row.week),
                    "ageing_days": int(row.ageing_days),
                    "ultimate_load_kn": float(getattr(row, measured_target_col)),
                    "terminal_ultimate_load_kn_target": float(getattr(row, target_col)),
                    "predicted_ultimate_load_kn": float(prediction),
                    "residual": float(prediction - getattr(row, target_col)),
                    "abs_error": float(abs(prediction - getattr(row, target_col))),
                    "is_measured_ultimate_load": True,
                }
            )

        if predict_all_rows:
            all_row_preds = predict_model_bundle(bundle, test_df)
            for row, prediction in zip(test_df.itertuples(index=False), all_row_preds):
                all_row_prediction_rows.append(
                    {
                        "split_name": split_meta["split_name"],
                        "repeat_id": int(split_meta["repeat_id"]),
                        "fold_id": int(split_meta["fold_id"]),
                        "split_id": split_id,
                        "sample_name": row.sample_name,
                        "specimen_id": row.specimen_id,
                        "campaign_id": row.campaign_id,
                        "series_id": row.series_id,
                        "n_steel_mesh": int(row.n_steel_mesh),
                        "week": int(row.week),
                        "ageing_days": int(row.ageing_days),
                        "ultimate_load_kn": float(row.ultimate_load_kn) if pd.notna(row.ultimate_load_kn) else np.nan,
                        "terminal_ultimate_load_kn_target": float(row.terminal_ultimate_load_kn_target)
                        if pd.notna(row.terminal_ultimate_load_kn_target)
                        else np.nan,
                        "predicted_ultimate_load_kn": float(prediction),
                        "is_measured_ultimate_load": bool(row.is_measured_ultimate_load),
                    }
                )

        fold_importance_df = extract_feature_importance(bundle)
        if not fold_importance_df.empty:
            fold_importance_df = fold_importance_df.assign(
                split_name=split_meta["split_name"],
                repeat_id=int(split_meta["repeat_id"]),
                fold_id=int(split_meta["fold_id"]),
                split_id=split_id,
            )
            importance_rows.extend(fold_importance_df.to_dict("records"))

    fold_metrics_df = pd.DataFrame(fold_rows)
    terminal_predictions_df = pd.DataFrame(terminal_prediction_rows)
    all_row_predictions_df = pd.DataFrame(all_row_prediction_rows)
    fold_importance_df = pd.DataFrame(importance_rows)

    summary_df = pd.DataFrame(
        [
            {
                "mae_mean": float(fold_metrics_df["test_mae"].mean()),
                "mae_std": float(fold_metrics_df["test_mae"].std(ddof=1)),
                "rmse_mean": float(fold_metrics_df["test_rmse"].mean()),
                "rmse_std": float(fold_metrics_df["test_rmse"].std(ddof=1)),
                "r2_mean": float(fold_metrics_df["test_r2"].mean()),
                "r2_std": float(fold_metrics_df["test_r2"].std(ddof=1)),
                "spearman_mean": float(fold_metrics_df["test_spearman"].mean()),
                "spearman_std": float(fold_metrics_df["test_spearman"].std(ddof=1)),
                "n_splits": int(fold_metrics_df["split_id"].nunique()),
                "n_terminal_specimens": int(terminal_predictions_df["specimen_id"].nunique()),
            }
        ]
    )

    terminal_oof_df = aggregate_prediction_rows(terminal_predictions_df)
    all_rows_oof_df = aggregate_prediction_rows(all_row_predictions_df) if not all_row_predictions_df.empty else pd.DataFrame()

    return {
        "fold_metrics": fold_metrics_df,
        "terminal_predictions": terminal_predictions_df,
        "terminal_oof": terminal_oof_df,
        "all_row_predictions": all_row_predictions_df,
        "all_row_oof": all_rows_oof_df,
        "fold_importance": fold_importance_df,
        "summary": summary_df,
    }


def aggregate_prediction_rows(predictions_df: pd.DataFrame) -> pd.DataFrame:
    if predictions_df.empty:
        return pd.DataFrame()
    grouped = predictions_df.groupby("sample_name", as_index=False)
    aggregated = grouped.agg(
        specimen_id=("specimen_id", "main_first"),
        campaign_id=("campaign_id", "main_first"),
        series_id=("series_id", "main_first"),
        n_steel_mesh=("n_steel_mesh", "main_first"),
        week=("week", "main_first"),
        ageing_days=("ageing_days", "main_first"),
        ultimate_load_kn=("ultimate_load_kn", "main_first"),
        terminal_ultimate_load_kn_target=("terminal_ultimate_load_kn_target", "main_first"),
        predicted_ultimate_load_kn=("predicted_ultimate_load_kn", "mean"),
        predicted_ultimate_load_kn_std=("predicted_ultimate_load_kn", "std"),
        prediction_count=("predicted_ultimate_load_kn", "count"),
        is_measured_ultimate_load=("is_measured_ultimate_load", "main_first"),
    )
    aggregated["predicted_ultimate_load_kn_std"] = aggregated["predicted_ultimate_load_kn_std"].fillna(0.0)
    aggregated["residual"] = (
        aggregated["predicted_ultimate_load_kn"] - aggregated["terminal_ultimate_load_kn_target"]
    )
    aggregated["abs_error"] = aggregated["residual"].abs()
    return aggregated.sort_values(["n_steel_mesh", "specimen_id", "week"]).reset_index(drop=True)


def _last_non_null(series: pd.Series):
    valid = series.dropna()
    if valid.empty:
        return np.nan
    return valid.iloc[-1]


def _safe_linear_slope(x_values: pd.Series, y_values: pd.Series) -> float:
    valid = pd.DataFrame({"x": x_values, "y": y_values}).dropna()
    if len(valid) < 2 or valid["x"].nunique() < 2:
        return float("nan")
    slope, _intercept = np.polyfit(valid["x"].astype(float).to_numpy(), valid["y"].astype(float).to_numpy(), deg=1)
    return float(slope)


def build_specimen_summary_table(refocus_df: pd.DataFrame, refocus_cfg: dict) -> pd.DataFrame:
    residual_cfg = refocus_cfg.get("residual_refinement", {})
    summary_columns = [column for column in residual_cfg.get("summary_columns", []) if column in refocus_df.columns]
    summary_statistics = list(residual_cfg.get("summary_statistics", []))
    if not summary_columns or not summary_statistics:
        return pd.DataFrame()

    base_manifest = build_specimen_manifest(refocus_df).set_index("specimen_id")
    rows: list[dict[str, object]] = []
    for specimen_id, group in refocus_df.sort_values(["specimen_id", "week"]).groupby("specimen_id"):
        base = base_manifest.loc[specimen_id].to_dict()
        row: dict[str, object] = {
            "sample_name": specimen_id,
            "specimen_id": specimen_id,
            "campaign_id": base["campaign_id"],
            "series_id": base["series_id"],
            "split_group_treatment": base["split_group_treatment"],
            "treatment_protocol": base["treatment_protocol"],
            "treatment_coarse": base["treatment_coarse"],
            "treatment_label_coarse": base["treatment_label_coarse"],
            "n_steel_mesh": int(base["n_steel_mesh"]),
            "nacl_pct": float(base["nacl_pct"]),
            "cover_mm": float(base["cover_mm"]),
            "week": int(base["terminal_week"]),
            "ageing_days": int(base["terminal_days"]),
            "terminal_week": int(base["terminal_week"]),
            "terminal_days": int(base["terminal_days"]),
            "visible_corrosion_onset_week": float(base["visible_corrosion_onset_week"])
            if pd.notna(base["visible_corrosion_onset_week"])
            else np.nan,
            "has_visible_corrosion_onset": int(pd.notna(base["visible_corrosion_onset_week"])),
            "weeks_after_onset_at_terminal": float(base["terminal_week"] - base["visible_corrosion_onset_week"])
            if pd.notna(base["visible_corrosion_onset_week"])
            else np.nan,
            "n_rows_all_weeks": int(base["n_rows_all_weeks"]),
            "n_rows_post_onset": int(base["n_rows_post_onset"]),
            "ultimate_load_kn": float(base["terminal_ultimate_load_kn_target"])
            if pd.notna(base["terminal_ultimate_load_kn_target"])
            else np.nan,
            "terminal_ultimate_load_kn_target": float(base["terminal_ultimate_load_kn_target"])
            if pd.notna(base["terminal_ultimate_load_kn_target"])
            else np.nan,
            "is_measured_ultimate_load": bool(base["is_measured_ultimate_load"]),
        }
        for column in summary_columns:
            series = group[column]
            for statistic in summary_statistics:
                feature_name = f"{column}_{statistic}"
                if statistic == "terminal":
                    row[feature_name] = _last_non_null(series)
                elif statistic == "max":
                    row[feature_name] = float(series.max()) if series.notna().any() else np.nan
                elif statistic == "mean":
                    row[feature_name] = float(series.mean()) if series.notna().any() else np.nan
                elif statistic == "slope":
                    row[feature_name] = _safe_linear_slope(group["week"], series)
                else:
                    raise ValueError(f"Unsupported specimen summary statistic: {statistic}")
        rows.append(row)

    return pd.DataFrame(rows).sort_values(["n_steel_mesh", "specimen_id"]).reset_index(drop=True)


def build_residual_summary_feature_cols(specimen_summary_df: pd.DataFrame, refocus_cfg: dict) -> list[str]:
    residual_cfg = refocus_cfg.get("residual_refinement", {})
    feature_cols = []
    for column in residual_cfg.get("summary_columns", []):
        for statistic in residual_cfg.get("summary_statistics", []):
            feature_name = f"{column}_{statistic}"
            if feature_name in specimen_summary_df.columns and specimen_summary_df[feature_name].notna().sum() > 0:
                feature_cols.append(feature_name)
    for column in [
        "visible_corrosion_onset_week",
        "has_visible_corrosion_onset",
        "weeks_after_onset_at_terminal",
        "n_rows_post_onset",
    ]:
        if column in specimen_summary_df.columns and specimen_summary_df[column].notna().sum() > 0:
            feature_cols.append(column)
    return feature_cols


def aggregate_refinement_prediction_rows(predictions_df: pd.DataFrame) -> pd.DataFrame:
    if predictions_df.empty:
        return pd.DataFrame()
    grouped = predictions_df.groupby("sample_name", as_index=False)
    aggregated = grouped.agg(
        specimen_id=("specimen_id", "main_first"),
        campaign_id=("campaign_id", "main_first"),
        series_id=("series_id", "main_first"),
        n_steel_mesh=("n_steel_mesh", "main_first"),
        week=("week", "main_first"),
        ageing_days=("ageing_days", "main_first"),
        ultimate_load_kn=("ultimate_load_kn", "main_first"),
        terminal_ultimate_load_kn_target=("terminal_ultimate_load_kn_target", "main_first"),
        baseline_pred=("baseline_pred", "mean"),
        baseline_pred_std=("baseline_pred", "std"),
        residual_correction=("residual_correction", "mean"),
        residual_correction_std=("residual_correction", "std"),
        predicted_ultimate_load_kn=("predicted_ultimate_load_kn", "mean"),
        predicted_ultimate_load_kn_std=("predicted_ultimate_load_kn", "std"),
        prediction_count=("predicted_ultimate_load_kn", "count"),
        is_measured_ultimate_load=("is_measured_ultimate_load", "main_first"),
    )
    for column in [
        "baseline_pred_std",
        "residual_correction_std",
        "predicted_ultimate_load_kn_std",
    ]:
        aggregated[column] = aggregated[column].fillna(0.0)
    aggregated["residual"] = aggregated["predicted_ultimate_load_kn"] - aggregated["terminal_ultimate_load_kn_target"]
    aggregated["abs_error"] = aggregated["residual"].abs()
    aggregated["baseline_abs_error"] = (aggregated["baseline_pred"] - aggregated["terminal_ultimate_load_kn_target"]).abs()
    return aggregated.sort_values(["n_steel_mesh", "specimen_id"]).reset_index(drop=True)


def _build_inner_cv_predictions(
    train_df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
    model_name: str,
    modeling_cfg: dict,
    refocus_cfg: dict,
    n_splits: int,
    random_state: int,
    stratify_col: str | None,
) -> np.ndarray:
    train_df = train_df.reset_index(drop=True).copy()
    if len(train_df) < 3:
        bundle = fit_model_bundle(train_df, feature_cols, target_col, model_name, modeling_cfg, refocus_cfg)
        return predict_model_bundle(bundle, train_df)

    effective_splits = min(n_splits, len(train_df))
    if stratify_col and stratify_col in train_df.columns and train_df[stratify_col].nunique() > 1:
        min_class_count = int(train_df[stratify_col].value_counts().min())
        effective_splits = min(effective_splits, min_class_count)
    if effective_splits < 2:
        bundle = fit_model_bundle(train_df, feature_cols, target_col, model_name, modeling_cfg, refocus_cfg)
        return predict_model_bundle(bundle, train_df)

    if stratify_col and stratify_col in train_df.columns and train_df[stratify_col].nunique() > 1:
        splitter = StratifiedKFold(
            n_splits=effective_splits,
            shuffle=True,
            random_state=random_state,
        )
        split_iter = splitter.split(train_df, train_df[stratify_col])
    else:
        splitter = KFold(n_splits=effective_splits, shuffle=True, random_state=random_state)
        split_iter = splitter.split(train_df)

    preds = np.full(len(train_df), np.nan, dtype=float)
    for inner_train_idx, inner_test_idx in split_iter:
        inner_train_df = train_df.iloc[inner_train_idx].copy()
        inner_test_df = train_df.iloc[inner_test_idx].copy()
        bundle = fit_model_bundle(inner_train_df, feature_cols, target_col, model_name, modeling_cfg, refocus_cfg)
        preds[inner_test_idx] = predict_model_bundle(bundle, inner_test_df)

    if np.isnan(preds).any():
        bundle = fit_model_bundle(train_df, feature_cols, target_col, model_name, modeling_cfg, refocus_cfg)
        preds[np.isnan(preds)] = predict_model_bundle(bundle, train_df.iloc[np.isnan(preds)].copy())
    return preds


def _fit_mesh_specific_residual_models(
    train_df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
    model_name: str,
    modeling_cfg: dict,
    refocus_cfg: dict,
) -> tuple[dict[int, dict[str, object]], pd.DataFrame]:
    fitted: dict[int, dict[str, object]] = {}
    importance_frames = []

    for mesh_value, mesh_df in train_df.groupby("n_steel_mesh"):
        mesh_df = mesh_df.loc[mesh_df[target_col].notna()].copy()
        if mesh_df.empty:
            continue
        if len(mesh_df) < 3 or mesh_df[target_col].nunique() < 2:
            fitted[int(mesh_value)] = {"kind": "constant", "value": float(mesh_df[target_col].mean())}
            continue
        bundle = fit_model_bundle(mesh_df, feature_cols, target_col, model_name, modeling_cfg, refocus_cfg)
        fitted[int(mesh_value)] = {"kind": "model", "bundle": bundle}
        importance_df = extract_feature_importance(bundle)
        if not importance_df.empty:
            importance_frames.append(importance_df.assign(n_steel_mesh=int(mesh_value)))

    if not importance_frames:
        return fitted, pd.DataFrame()
    return fitted, pd.concat(importance_frames, ignore_index=True)


def _predict_mesh_specific_residual_models(
    fitted: dict[int, dict[str, object]],
    test_df: pd.DataFrame,
) -> np.ndarray:
    preds = pd.Series(0.0, index=test_df.index, dtype=float)
    for mesh_value, sub_idx in test_df.groupby("n_steel_mesh").groups.items():
        fit_obj = fitted.get(int(mesh_value))
        if fit_obj is None:
            preds.loc[list(sub_idx)] = 0.0
        elif fit_obj["kind"] == "constant":
            preds.loc[list(sub_idx)] = float(fit_obj["value"])
        else:
            preds.loc[list(sub_idx)] = predict_model_bundle(fit_obj["bundle"], test_df.loc[list(sub_idx)].copy())  # type: ignore[arg-type]
    return preds.to_numpy(dtype=float)


def evaluate_residual_refinement(
    specimen_summary_df: pd.DataFrame,
    specimen_manifest_df: pd.DataFrame,
    stage1_feature_cols: list[str],
    stage2_feature_cols: list[str],
    stage1_model_name: str,
    stage2_model_name: str,
    modeling_cfg: dict,
    refocus_cfg: dict,
) -> dict[str, pd.DataFrame]:
    indexed = specimen_summary_df.set_index("sample_name", drop=False)
    fold_rows: list[dict[str, object]] = []
    prediction_rows: list[dict[str, object]] = []
    importance_rows: list[dict[str, object]] = []
    residual_cfg = refocus_cfg["residual_refinement"]

    for split_id, split_df in specimen_manifest_df.groupby("split_id"):
        train_names = split_df.loc[split_df["membership"] == "train", "specimen_id"].tolist()
        test_names = split_df.loc[split_df["membership"] == "test", "specimen_id"].tolist()
        train_df = indexed.loc[train_names].copy()
        test_df = indexed.loc[test_names].copy()

        baseline_bundle = fit_model_bundle(
            train_df,
            stage1_feature_cols,
            "terminal_ultimate_load_kn_target",
            stage1_model_name,
            modeling_cfg,
            refocus_cfg,
        )
        baseline_test_pred = predict_model_bundle(baseline_bundle, test_df)
        baseline_train_crossfit_pred = _build_inner_cv_predictions(
            train_df=train_df,
            feature_cols=stage1_feature_cols,
            target_col="terminal_ultimate_load_kn_target",
            model_name=stage1_model_name,
            modeling_cfg=modeling_cfg,
            refocus_cfg=refocus_cfg,
            n_splits=int(residual_cfg["inner_cv_splits"]),
            random_state=int(refocus_cfg["random_state"]) + int(split_df["fold_id"].iloc[0]),
            stratify_col="n_steel_mesh",
        )
        residual_train_df = train_df.copy()
        residual_train_df["metadata_baseline_crossfit_pred"] = baseline_train_crossfit_pred
        residual_train_df["residual_target"] = (
            residual_train_df["terminal_ultimate_load_kn_target"] - residual_train_df["metadata_baseline_crossfit_pred"]
        )
        residual_fitted, fold_importance_df = _fit_mesh_specific_residual_models(
            train_df=residual_train_df,
            feature_cols=stage2_feature_cols,
            target_col="residual_target",
            model_name=stage2_model_name,
            modeling_cfg=modeling_cfg,
            refocus_cfg=refocus_cfg,
        )
        residual_test_pred = _predict_mesh_specific_residual_models(residual_fitted, test_df)
        final_test_pred = baseline_test_pred + residual_test_pred

        baseline_metrics = regression_metrics(test_df["terminal_ultimate_load_kn_target"], baseline_test_pred)
        final_metrics = regression_metrics(test_df["terminal_ultimate_load_kn_target"], final_test_pred)
        split_meta = split_df.iloc[0]
        fold_rows.append(
            {
                "split_name": split_meta["split_name"],
                "repeat_id": int(split_meta["repeat_id"]),
                "fold_id": int(split_meta["fold_id"]),
                "split_id": split_id,
                "train_specimens": int(len(train_df)),
                "test_specimens": int(len(test_df)),
                "baseline_test_mae": baseline_metrics["mae"],
                "baseline_test_rmse": baseline_metrics["rmse"],
                "baseline_test_r2": baseline_metrics["r2"],
                "baseline_test_spearman": baseline_metrics["spearman"],
                "test_mae": final_metrics["mae"],
                "test_rmse": final_metrics["rmse"],
                "test_r2": final_metrics["r2"],
                "test_spearman": final_metrics["spearman"],
                "delta_mae_vs_baseline": final_metrics["mae"] - baseline_metrics["mae"],
                "delta_rmse_vs_baseline": final_metrics["rmse"] - baseline_metrics["rmse"],
                "delta_spearman_vs_baseline": final_metrics["spearman"] - baseline_metrics["spearman"],
            }
        )

        for row, base_pred, resid_pred, final_pred in zip(
            test_df.itertuples(index=False),
            baseline_test_pred,
            residual_test_pred,
            final_test_pred,
        ):
            prediction_rows.append(
                {
                    "split_name": split_meta["split_name"],
                    "repeat_id": int(split_meta["repeat_id"]),
                    "fold_id": int(split_meta["fold_id"]),
                    "split_id": split_id,
                    "sample_name": row.sample_name,
                    "specimen_id": row.specimen_id,
                    "campaign_id": row.campaign_id,
                    "series_id": row.series_id,
                    "n_steel_mesh": int(row.n_steel_mesh),
                    "week": int(row.week),
                    "ageing_days": int(row.ageing_days),
                    "ultimate_load_kn": float(row.ultimate_load_kn),
                    "terminal_ultimate_load_kn_target": float(row.terminal_ultimate_load_kn_target),
                    "baseline_pred": float(base_pred),
                    "residual_correction": float(resid_pred),
                    "predicted_ultimate_load_kn": float(final_pred),
                    "is_measured_ultimate_load": bool(row.is_measured_ultimate_load),
                }
            )

        if not fold_importance_df.empty:
            fold_importance_df = fold_importance_df.assign(
                split_name=split_meta["split_name"],
                repeat_id=int(split_meta["repeat_id"]),
                fold_id=int(split_meta["fold_id"]),
                split_id=split_id,
            )
            importance_rows.extend(fold_importance_df.to_dict("records"))

    fold_metrics_df = pd.DataFrame(fold_rows)
    prediction_df = pd.DataFrame(prediction_rows)
    oof_df = aggregate_refinement_prediction_rows(prediction_df)
    fold_importance_df = pd.DataFrame(importance_rows)
    summary_df = pd.DataFrame(
        [
            {
                "mae_mean": float(fold_metrics_df["test_mae"].mean()),
                "mae_std": float(fold_metrics_df["test_mae"].std(ddof=1)),
                "rmse_mean": float(fold_metrics_df["test_rmse"].mean()),
                "rmse_std": float(fold_metrics_df["test_rmse"].std(ddof=1)),
                "r2_mean": float(fold_metrics_df["test_r2"].mean()),
                "r2_std": float(fold_metrics_df["test_r2"].std(ddof=1)),
                "spearman_mean": float(fold_metrics_df["test_spearman"].mean()),
                "spearman_std": float(fold_metrics_df["test_spearman"].std(ddof=1)),
                "baseline_mae_mean": float(fold_metrics_df["baseline_test_mae"].mean()),
                "baseline_rmse_mean": float(fold_metrics_df["baseline_test_rmse"].mean()),
                "baseline_spearman_mean": float(fold_metrics_df["baseline_test_spearman"].mean()),
                "delta_mae_vs_baseline_mean": float(fold_metrics_df["delta_mae_vs_baseline"].mean()),
                "delta_rmse_vs_baseline_mean": float(fold_metrics_df["delta_rmse_vs_baseline"].mean()),
                "delta_spearman_vs_baseline_mean": float(fold_metrics_df["delta_spearman_vs_baseline"].mean()),
                "n_splits": int(fold_metrics_df["split_id"].nunique()),
                "n_terminal_specimens": int(oof_df["specimen_id"].nunique()),
            }
        ]
    )
    return {
        "fold_metrics": fold_metrics_df,
        "fold_predictions": prediction_df,
        "terminal_oof": oof_df,
        "fold_importance": fold_importance_df,
        "summary": summary_df,
    }


def build_best_feature_set_error_audit(
    grouped_output_dir: Path,
    best_by_feature_set_df: pd.DataFrame,
    refocus_cfg: dict,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    long_frames = []
    for row in best_by_feature_set_df.itertuples(index=False):
        prediction_path = grouped_output_dir / "experiments" / row.feature_set_name / row.model_name / "terminal_oof_predictions.csv"
        if not prediction_path.exists():
            continue
        pred_df = pd.read_csv(prediction_path)
        long_frames.append(
            pred_df.assign(
                feature_set_name=row.feature_set_name,
                feature_set_label=row.feature_set_label,
                model_name=row.model_name,
                feature_set_model_label=f"{row.feature_set_label} | {row.model_name}",
            )
        )
    if not long_frames:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    long_df = pd.concat(long_frames, ignore_index=True)
    hard_threshold = float(refocus_cfg["error_audit"]["hard_abs_error_kN"])
    persistent_min = int(refocus_cfg["error_audit"]["persistent_min_feature_sets"])
    approach_range = float(refocus_cfg["error_audit"]["approach_sensitive_range_kN"])

    summary_rows = []
    for (specimen_id, n_steel_mesh, ultimate_load_kn), sub in long_df.groupby(
        ["specimen_id", "n_steel_mesh", "ultimate_load_kn"],
        as_index=False,
    ):
        best_row = sub.sort_values("abs_error").iloc[0]
        worst_row = sub.sort_values("abs_error", ascending=False).iloc[0]
        min_abs_error = float(sub["abs_error"].min())
        max_abs_error = float(sub["abs_error"].max())
        n_over = int((sub["abs_error"] > hard_threshold).sum())
        if n_over >= persistent_min and min_abs_error >= hard_threshold:
            gap_class = "persistent_hard"
        elif (max_abs_error - min_abs_error) >= approach_range:
            gap_class = "approach_sensitive"
        elif n_over >= persistent_min:
            gap_class = "mostly_hard"
        else:
            gap_class = "stable"
        summary_rows.append(
            {
                "specimen_id": specimen_id,
                "n_steel_mesh": int(n_steel_mesh),
                "ultimate_load_kn": float(ultimate_load_kn),
                "mean_abs_error": float(sub["abs_error"].mean()),
                "min_abs_error": min_abs_error,
                "max_abs_error": max_abs_error,
                "error_range_kN": max_abs_error - min_abs_error,
                "n_feature_sets_over_hard_threshold": n_over,
                "best_feature_set_label": best_row["feature_set_label"],
                "best_model_name": best_row["model_name"],
                "best_abs_error": float(best_row["abs_error"]),
                "best_prediction": float(best_row["predicted_ultimate_load_kn"]),
                "worst_feature_set_label": worst_row["feature_set_label"],
                "worst_model_name": worst_row["model_name"],
                "worst_abs_error": float(worst_row["abs_error"]),
                "worst_prediction": float(worst_row["predicted_ultimate_load_kn"]),
                "gap_class": gap_class,
                "specimen_label": f"{specimen_id} | mesh {int(n_steel_mesh)} | actual {float(ultimate_load_kn):.2f} kN",
            }
        )
    summary_df = pd.DataFrame(summary_rows).sort_values(
        ["n_feature_sets_over_hard_threshold", "mean_abs_error", "max_abs_error"],
        ascending=[False, False, False],
    ).reset_index(drop=True)

    wide_df = long_df.pivot_table(
        index=["specimen_id", "n_steel_mesh", "ultimate_load_kn"],
        columns="feature_set_model_label",
        values="abs_error",
    ).reset_index()
    return long_df.sort_values(["specimen_id", "feature_set_label"]).reset_index(drop=True), summary_df, wide_df


def compute_learning_curve(
    analysis_df: pd.DataFrame,
    row_manifest_df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
    model_name: str,
    modeling_cfg: dict,
    refocus_cfg: dict,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    fractions = [float(value) for value in refocus_cfg["learning_curve"]["train_size_fractions"]]
    indexed = analysis_df.set_index("sample_name", drop=False)
    rows: list[dict[str, object]] = []
    random_state = int(refocus_cfg["random_state"])

    for split_idx, (split_id, split_df) in enumerate(row_manifest_df.groupby("split_id")):
        train_names = split_df.loc[split_df["membership"] == "train", "sample_name"].tolist()
        test_names = split_df.loc[split_df["membership"] == "test", "sample_name"].tolist()
        train_full = indexed.loc[train_names].copy()
        test_df = indexed.loc[test_names].copy()
        train_full = train_full.loc[train_full[target_col].notna()].copy()
        test_df = test_df.loc[test_df[target_col].notna()].copy()
        test_terminal_df = test_df.loc[test_df["is_measured_ultimate_load"]].copy()
        train_specimens = sorted(train_full["specimen_id"].dropna().unique().tolist())

        for fraction_idx, fraction in enumerate(fractions):
            n_select = min(len(train_specimens), max(2, int(round(len(train_specimens) * fraction))))
            rng = np.random.default_rng(random_state + split_idx * 100 + fraction_idx)
            selected_specimens = set(rng.choice(train_specimens, size=n_select, replace=False).tolist())
            sampled_train_df = train_full.loc[train_full["specimen_id"].isin(selected_specimens)].copy()
            sampled_train_terminal_df = sampled_train_df.loc[sampled_train_df["is_measured_ultimate_load"]].copy()

            bundle = fit_model_bundle(
                sampled_train_df,
                feature_cols,
                target_col,
                model_name,
                modeling_cfg,
                refocus_cfg,
            )
            train_pred = predict_model_bundle(bundle, sampled_train_terminal_df)
            test_pred = predict_model_bundle(bundle, test_terminal_df)
            train_metrics = regression_metrics(sampled_train_terminal_df[target_col], train_pred)
            test_metrics = regression_metrics(test_terminal_df[target_col], test_pred)
            split_meta = split_df.iloc[0]
            rows.append(
                {
                    "split_name": split_meta["split_name"],
                    "repeat_id": int(split_meta["repeat_id"]),
                    "fold_id": int(split_meta["fold_id"]),
                    "split_id": split_id,
                    "fraction": fraction,
                    "n_train_specimens": int(sampled_train_df["specimen_id"].nunique()),
                    "n_train_rows": int(len(sampled_train_df)),
                    "train_mae": train_metrics["mae"],
                    "test_mae": test_metrics["mae"],
                    "train_rmse": train_metrics["rmse"],
                    "test_rmse": test_metrics["rmse"],
                    "train_spearman": train_metrics["spearman"],
                    "test_spearman": test_metrics["spearman"],
                }
            )

    raw_df = pd.DataFrame(rows)
    summary_df = (
        raw_df.groupby("fraction", as_index=False)[
            [
                "n_train_specimens",
                "n_train_rows",
                "train_mae",
                "test_mae",
                "train_rmse",
                "test_rmse",
                "train_spearman",
                "test_spearman",
            ]
        ]
        .agg(["mean", "std"])
        .reset_index()
    )
    summary_df.columns = [
        "_".join(column).strip("_") if isinstance(column, tuple) else column for column in summary_df.columns
    ]
    return raw_df, summary_df


def fit_full_experiment_model(
    analysis_df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
    model_name: str,
    modeling_cfg: dict,
    refocus_cfg: dict,
) -> tuple[dict[str, object], pd.DataFrame]:
    bundle = fit_model_bundle(analysis_df, feature_cols, target_col, model_name, modeling_cfg, refocus_cfg)
    importance_df = extract_feature_importance(bundle)
    return bundle, importance_df


def compute_partial_dependence_data(
    bundle: dict[str, object],
    reference_df: pd.DataFrame,
    importance_df: pd.DataFrame,
    top_n: int,
) -> pd.DataFrame:
    if importance_df.empty:
        return pd.DataFrame()
    feature_cols = bundle["feature_cols"]  # type: ignore[assignment]
    base_x = reference_df[feature_cols].copy()
    rows: list[dict[str, object]] = []

    for feature in importance_df["feature"].head(top_n):
        series = base_x[feature]
        if pd.api.types.is_numeric_dtype(series):
            unique_values = np.sort(series.dropna().unique())
            if unique_values.size == 0:
                continue
            if unique_values.size <= 8:
                grid = unique_values.tolist()
            else:
                grid = np.quantile(unique_values, np.linspace(0.05, 0.95, 8)).tolist()
                grid = sorted({float(value) for value in grid})
            for value in grid:
                varied = base_x.copy()
                varied[feature] = value
                preds = predict_model_bundle(bundle, varied)
                rows.append(
                    {
                        "feature": feature,
                        "feature_value": float(value),
                        "feature_value_label": f"{float(value):.4g}",
                        "prediction_mean": float(np.mean(preds)),
                        "feature_kind": "numeric",
                    }
                )
        else:
            categories = sorted(series.dropna().astype(str).unique().tolist())
            if len(categories) > 8:
                continue
            for category in categories:
                varied = base_x.copy()
                varied[feature] = category
                preds = predict_model_bundle(bundle, varied)
                rows.append(
                    {
                        "feature": feature,
                        "feature_value": category,
                        "feature_value_label": category,
                        "prediction_mean": float(np.mean(preds)),
                        "feature_kind": "categorical",
                    }
                )
    return pd.DataFrame(rows)


def plot_prediction_vs_truth(pred_df: pd.DataFrame, path: Path, title: str) -> None:
    if pred_df.empty:
        return
    ensure_dir(path.parent)
    fig, ax = plt.subplots(figsize=(7.5, 6.2))
    lower = min(pred_df["ultimate_load_kn"].min(), pred_df["predicted_ultimate_load_kn"].min())
    upper = max(pred_df["ultimate_load_kn"].max(), pred_df["predicted_ultimate_load_kn"].max())
    ax.errorbar(
        pred_df["ultimate_load_kn"],
        pred_df["predicted_ultimate_load_kn"],
        yerr=pred_df["predicted_ultimate_load_kn_std"],
        fmt="o",
        alpha=0.8,
        color="#4C78A8",
        ecolor="#9ECAE1",
        capsize=3,
    )
    ax.plot([lower, upper], [lower, upper], linestyle="--", color="black", linewidth=1.2)
    ax.set_xlabel("Observed ultimate load (kN)")
    ax.set_ylabel("Predicted ultimate load (kN)")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_residuals(pred_df: pd.DataFrame, path: Path, title: str) -> None:
    if pred_df.empty:
        return
    ensure_dir(path.parent)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    sns.scatterplot(
        data=pred_df,
        x="predicted_ultimate_load_kn",
        y="residual",
        hue="n_steel_mesh",
        palette="Set2",
        s=70,
        ax=axes[0],
    )
    axes[0].axhline(0.0, linestyle="--", color="black", linewidth=1.2)
    axes[0].set_title("Residuals vs prediction")
    axes[0].set_xlabel("Predicted ultimate load (kN)")
    axes[0].set_ylabel("Prediction - observed (kN)")

    sns.boxplot(data=pred_df, x="n_steel_mesh", y="residual", color="#F28E2B", ax=axes[1])
    sns.stripplot(data=pred_df, x="n_steel_mesh", y="residual", color="black", alpha=0.45, size=4, ax=axes[1])
    axes[1].axhline(0.0, linestyle="--", color="black", linewidth=1.2)
    axes[1].set_title("Residuals by mesh family")
    axes[1].set_xlabel("n_steel_mesh")
    axes[1].set_ylabel("Prediction - observed (kN)")

    fig.suptitle(title, fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_error_histogram(pred_df: pd.DataFrame, path: Path, title: str) -> None:
    if pred_df.empty:
        return
    ensure_dir(path.parent)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    sns.histplot(pred_df["residual"], bins=12, kde=True, color="#4C78A8", ax=axes[0])
    axes[0].axvline(0.0, linestyle="--", color="black", linewidth=1.2)
    axes[0].set_title("Residual distribution")
    axes[0].set_xlabel("Prediction - observed (kN)")
    axes[0].set_ylabel("Count")

    sns.histplot(pred_df["abs_error"], bins=12, kde=True, color="#E15759", ax=axes[1])
    axes[1].set_title("Absolute error distribution")
    axes[1].set_xlabel("Absolute error (kN)")
    axes[1].set_ylabel("Count")

    fig.suptitle(title, fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_feature_importance(importance_df: pd.DataFrame, path: Path, title: str, top_n: int) -> None:
    if importance_df.empty:
        return
    ensure_dir(path.parent)
    plot_df = importance_df.head(top_n).iloc[::-1]
    colors = plot_df["direction"].map({"positive": "#4C78A8", "negative": "#E15759"}).tolist()
    fig, ax = plt.subplots(figsize=(10, max(4, 0.35 * len(plot_df))))
    ax.barh(plot_df["feature"], plot_df["importance_abs"], color=colors)
    ax.set_xlabel("Absolute importance")
    ax.set_ylabel("Feature")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_partial_dependence(pdp_df: pd.DataFrame, path: Path, title: str) -> None:
    if pdp_df.empty:
        return
    ensure_dir(path.parent)
    features = pdp_df["feature"].unique().tolist()
    n_cols = 3
    n_rows = int(np.ceil(len(features) / n_cols))
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 4.5 * n_rows))
    axes = np.array(axes).reshape(n_rows, n_cols)

    for idx, feature in enumerate(features):
        ax = axes.flat[idx]
        sub = pdp_df.loc[pdp_df["feature"] == feature].copy()
        if sub["feature_kind"].iloc[0] == "numeric":
            sub["feature_value_numeric"] = sub["feature_value"].astype(float)
            sns.lineplot(data=sub, x="feature_value_numeric", y="prediction_mean", marker="o", color="#4C78A8", ax=ax)
            ax.set_xlabel(feature)
        else:
            sns.barplot(data=sub, x="feature_value_label", y="prediction_mean", color="#F28E2B", ax=ax)
            ax.tick_params(axis="x", rotation=30)
            ax.set_xlabel(feature)
        ax.set_ylabel("Mean predicted ultimate load (kN)")
        ax.set_title(feature)

    for idx in range(len(features), axes.size):
        axes.flat[idx].axis("off")

    fig.suptitle(title, fontsize=13, y=1.01)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_cv_stability(fold_metrics_df: pd.DataFrame, path: Path, title: str) -> None:
    if fold_metrics_df.empty:
        return
    ensure_dir(path.parent)
    melt_df = fold_metrics_df.melt(
        id_vars=["split_id"],
        value_vars=["test_mae", "test_rmse", "test_spearman"],
        var_name="metric",
        value_name="value",
    )
    fig, ax = plt.subplots(figsize=(9.5, 5))
    sns.boxplot(data=melt_df, x="metric", y="value", color="#9C755F", ax=ax)
    sns.stripplot(data=melt_df, x="metric", y="value", color="black", alpha=0.45, size=4, ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Metric")
    ax.set_ylabel("Fold value")
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_uncertainty(pred_df: pd.DataFrame, path: Path, title: str) -> None:
    if pred_df.empty:
        return
    ensure_dir(path.parent)
    plot_df = pred_df.sort_values(["n_steel_mesh", "ultimate_load_kn", "specimen_id"]).reset_index(drop=True)
    plot_df["specimen_order"] = np.arange(len(plot_df))
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

    axes[0].errorbar(
        plot_df["specimen_order"],
        plot_df["predicted_ultimate_load_kn"],
        yerr=plot_df["predicted_ultimate_load_kn_std"],
        fmt="o",
        color="#4C78A8",
        ecolor="#9ECAE1",
        capsize=3,
    )
    axes[0].scatter(plot_df["specimen_order"], plot_df["ultimate_load_kn"], color="#E15759", marker="x", s=50)
    axes[0].set_title("Terminal specimen predictions with approximate uncertainty")
    axes[0].set_xlabel("Specimen rank")
    axes[0].set_ylabel("Ultimate load (kN)")

    sns.scatterplot(
        data=plot_df,
        x="predicted_ultimate_load_kn_std",
        y="abs_error",
        hue="n_steel_mesh",
        palette="Set2",
        s=70,
        ax=axes[1],
    )
    axes[1].set_title("Approximate uncertainty vs absolute error")
    axes[1].set_xlabel("Prediction std across held-out repeats (kN)")
    axes[1].set_ylabel("Absolute error (kN)")

    fig.suptitle(title, fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_learning_curve(summary_df: pd.DataFrame, path: Path, title: str) -> None:
    if summary_df.empty:
        return
    ensure_dir(path.parent)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for ax, metric_name, label in [
        (axes[0], "mae", "MAE"),
        (axes[1], "spearman", "Spearman"),
    ]:
        for split_name, color in [("train", "#4C78A8"), ("test", "#E15759")]:
            mean_col = f"{split_name}_{metric_name}_mean"
            std_col = f"{split_name}_{metric_name}_std"
            ax.plot(summary_df["fraction"], summary_df[mean_col], marker="o", color=color, label=split_name.title())
            lower = summary_df[mean_col] - summary_df[std_col].fillna(0.0)
            upper = summary_df[mean_col] + summary_df[std_col].fillna(0.0)
            ax.fill_between(summary_df["fraction"], lower, upper, color=color, alpha=0.15)
        ax.set_title(label)
        ax.set_xlabel("Fraction of available training specimens")
        ax.set_ylabel(label)
    axes[0].legend(loc="best")
    fig.suptitle(title, fontsize=13, y=1.03)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_model_metric_heatmap(summary_df: pd.DataFrame, path: Path, title: str) -> None:
    if summary_df.empty:
        return
    ensure_dir(path.parent)
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    for ax, value_col, cmap, label in [
        (axes[0], "mae_mean", "viridis_r", "MAE"),
        (axes[1], "rmse_mean", "magma_r", "RMSE"),
        (axes[2], "spearman_mean", "viridis", "Spearman"),
    ]:
        heatmap_df = summary_df.pivot(index="feature_set_label", columns="model_name", values=value_col)
        sns.heatmap(heatmap_df, annot=True, fmt=".3f", cmap=cmap, ax=ax)
        ax.set_title(label)
        ax.set_xlabel("Model")
        ax.set_ylabel("Feature set")
    fig.suptitle(title, fontsize=14, y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_best_feature_set_bars(best_df: pd.DataFrame, path: Path, title: str) -> None:
    if best_df.empty:
        return
    ensure_dir(path.parent)
    plot_df = best_df.sort_values("mae_mean").copy()
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.barplot(data=plot_df, x="feature_set_label", y="mae_mean", hue="model_name", ax=axes[0])
    axes[0].set_title("MAE by feature set")
    axes[0].set_xlabel("Feature set")
    axes[0].set_ylabel("MAE (kN)")
    axes[0].tick_params(axis="x", rotation=30)

    sns.barplot(data=plot_df, x="feature_set_label", y="spearman_mean", hue="model_name", ax=axes[1])
    axes[1].set_title("Spearman by feature set")
    axes[1].set_xlabel("Feature set")
    axes[1].set_ylabel("Spearman")
    axes[1].tick_params(axis="x", rotation=30)

    for ax in axes:
        ax.legend(title="Model", loc="best")
    fig.suptitle(title, fontsize=14, y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_all_specimen_trajectories(all_rows_oof_df: pd.DataFrame, path: Path, title: str) -> None:
    if all_rows_oof_df.empty:
        return
    ensure_dir(path.parent)
    specimens = all_rows_oof_df["specimen_id"].unique().tolist()
    n_cols = 4
    n_rows = int(np.ceil(len(specimens) / n_cols))
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 3.1 * n_rows), sharex=False, sharey=True)
    axes = np.array(axes).reshape(n_rows, n_cols)
    for idx, specimen_id in enumerate(specimens):
        ax = axes.flat[idx]
        sub = all_rows_oof_df.loc[all_rows_oof_df["specimen_id"] == specimen_id].sort_values("week")
        ax.plot(sub["week"], sub["predicted_ultimate_load_kn"], marker="o", color="#4C78A8", linewidth=1.6)
        ax.fill_between(
            sub["week"],
            sub["predicted_ultimate_load_kn"] - sub["predicted_ultimate_load_kn_std"],
            sub["predicted_ultimate_load_kn"] + sub["predicted_ultimate_load_kn_std"],
            color="#9ECAE1",
            alpha=0.3,
        )
        terminal_row = sub.loc[sub["is_measured_ultimate_load"]]
        if not terminal_row.empty:
            actual_value = terminal_row["ultimate_load_kn"].iloc[0]
            ax.axhline(actual_value, linestyle="--", color="#E15759", linewidth=1.2)
        ax.set_title(f"{specimen_id} | mesh {int(sub['n_steel_mesh'].iloc[0])}")
        ax.set_xlabel("Week")
        ax.set_ylabel("Predicted load (kN)")
    for idx in range(len(specimens), axes.size):
        axes.flat[idx].axis("off")
    fig.suptitle(title, fontsize=14, y=1.01)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_specimen_error_heatmap(
    long_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    path: Path,
    title: str,
    top_n: int,
) -> None:
    if long_df.empty or summary_df.empty:
        return
    ensure_dir(path.parent)
    top_summary = summary_df.head(top_n).copy()
    plot_df = long_df.loc[long_df["specimen_id"].isin(top_summary["specimen_id"])].copy()
    plot_df = plot_df.merge(
        top_summary[["specimen_id", "specimen_label"]],
        on="specimen_id",
        how="left",
        validate="many_to_one",
    )
    heatmap_df = plot_df.pivot_table(
        index="specimen_label",
        columns="feature_set_model_label",
        values="abs_error",
    )
    heatmap_df = heatmap_df.reindex(top_summary["specimen_label"].tolist())
    fig_height = max(4.5, 0.38 * len(heatmap_df))
    fig, ax = plt.subplots(figsize=(13, fig_height))
    sns.heatmap(heatmap_df, annot=True, fmt=".2f", cmap="magma_r", ax=ax)
    ax.set_xlabel("Best model within feature set")
    ax.set_ylabel("Specimen")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_specimen_error_span(
    summary_df: pd.DataFrame,
    path: Path,
    title: str,
    hard_threshold: float,
    top_n: int,
) -> None:
    if summary_df.empty:
        return
    ensure_dir(path.parent)
    plot_df = summary_df.head(top_n).copy().iloc[::-1]
    y_positions = np.arange(len(plot_df))
    fig_height = max(4.5, 0.42 * len(plot_df))
    fig, ax = plt.subplots(figsize=(12, fig_height))
    ax.hlines(
        y=y_positions,
        xmin=plot_df["min_abs_error"],
        xmax=plot_df["max_abs_error"],
        color="#9ECAE1",
        linewidth=5,
        alpha=0.85,
        label="Feature-set error span",
    )
    ax.scatter(plot_df["best_abs_error"], y_positions, color="#2CA02C", s=55, label="Best feature-set/model")
    ax.scatter(plot_df["worst_abs_error"], y_positions, color="#D62728", s=55, label="Worst feature-set/model")
    ax.axvline(hard_threshold, linestyle="--", color="black", linewidth=1.2, label="Hard-error threshold")
    ax.set_yticks(y_positions)
    ax.set_yticklabels(plot_df["specimen_label"])
    ax.set_xlabel("Absolute error (kN)")
    ax.set_ylabel("Specimen")
    ax.set_title(title)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_error_delta_vs_baseline(
    comparison_df: pd.DataFrame,
    path: Path,
    title: str,
    top_n: int,
) -> None:
    if comparison_df.empty:
        return
    ensure_dir(path.parent)
    plot_df = comparison_df.sort_values(["baseline_abs_error", "refined_abs_error"], ascending=[False, False]).head(top_n).copy()
    plot_df = plot_df.iloc[::-1]
    y_positions = np.arange(len(plot_df))
    fig_height = max(4.5, 0.42 * len(plot_df))
    fig, ax = plt.subplots(figsize=(12, fig_height))
    span_left = np.minimum(plot_df["baseline_abs_error"], plot_df["refined_abs_error"])
    span_right = np.maximum(plot_df["baseline_abs_error"], plot_df["refined_abs_error"])
    ax.hlines(y=y_positions, xmin=span_left, xmax=span_right, color="#D9D9D9", linewidth=4)
    ax.scatter(plot_df["baseline_abs_error"], y_positions, color="#E15759", s=60, label="Baseline abs error")
    ax.scatter(plot_df["refined_abs_error"], y_positions, color="#4C78A8", s=60, label="Refined abs error")
    ax.set_yticks(y_positions)
    ax.set_yticklabels(plot_df["specimen_label"])
    ax.set_xlabel("Absolute error (kN)")
    ax.set_ylabel("Specimen")
    ax.set_title(title)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def run_mesh_stratified_correlations(
    terminal_df: pd.DataFrame,
    correlation_columns: list[str],
    output_dir: Path,
) -> tuple[pd.DataFrame, Path]:
    ensure_dir(output_dir)
    rows = []
    mesh_panels = [(4, "4-mesh"), (7, "7-mesh"), ("pooled", "Pooled (confounded)")]
    fig, axes = plt.subplots(len(correlation_columns), len(mesh_panels), figsize=(16, 4.8 * len(correlation_columns)))
    axes = np.array(axes).reshape(len(correlation_columns), len(mesh_panels))

    for row_idx, column in enumerate(correlation_columns):
        for col_idx, (mesh_value, mesh_label) in enumerate(mesh_panels):
            ax = axes[row_idx, col_idx]
            if mesh_value == "pooled":
                subset = terminal_df.copy()
            else:
                subset = terminal_df.loc[terminal_df["n_steel_mesh"] == mesh_value].copy()
            pearson_r, pearson_p, spearman_rho, spearman_p = _safe_corr(subset[column], subset["ultimate_load_kn"])
            rows.append(
                {
                    "mesh_group": mesh_value,
                    "mesh_group_label": mesh_label,
                    "corrosion_variable": column,
                    "n_specimens": int(subset["specimen_id"].nunique()),
                    "pearson_r": pearson_r,
                    "pearson_pvalue": pearson_p,
                    "spearman_rho": spearman_rho,
                    "spearman_pvalue": spearman_p,
                }
            )
            sns.regplot(
                data=subset,
                x=column,
                y="ultimate_load_kn",
                ci=None,
                scatter_kws={"s": 65, "alpha": 0.85, "color": "#4C78A8"},
                line_kws={"color": "#222222", "linewidth": 1.5},
                ax=ax,
            )
            ax.set_title(f"{mesh_label}\n{column} vs ultimate_load_kn")
            ax.set_xlabel(column)
            ax.set_ylabel("Ultimate load (kN)")
            ax.text(
                0.03,
                0.97,
                f"n={subset['specimen_id'].nunique()}\nPearson={pearson_r:.3f}\nSpearman={spearman_rho:.3f}",
                transform=ax.transAxes,
                va="top",
                ha="left",
                fontsize=9,
                bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#CCCCCC"},
            )

    fig.suptitle(
        "Superficial corrosion versus terminal ultimate load\n"
        "Pooled panels are shown only as confounded references because campaign and mesh are aligned.",
        fontsize=14,
        y=1.01,
    )
    fig.tight_layout()
    figure_path = output_dir / "mesh_stratified_corrosion_vs_ultimate_load.png"
    fig.savefig(figure_path, dpi=180, bbox_inches="tight")
    plt.close(fig)

    summary_df = pd.DataFrame(rows)
    save_dataframe_csv(summary_df, output_dir / "mesh_stratified_corrosion_vs_ultimate_load.csv")
    return summary_df, figure_path


def summarise_experiment_summary(
    summary_df: pd.DataFrame,
    analysis_name: str,
    split_name: str,
    feature_set_name: str,
    feature_set_label: str,
    model_name: str,
    n_features: int,
) -> pd.DataFrame:
    out = summary_df.copy()
    out["analysis_name"] = analysis_name
    out["split_name"] = split_name
    out["feature_set_name"] = feature_set_name
    out["feature_set_label"] = feature_set_label
    out["model_name"] = model_name
    out["n_features"] = n_features
    return out


def select_best_by_feature_set(summary_df: pd.DataFrame) -> pd.DataFrame:
    if summary_df.empty:
        return pd.DataFrame()
    return (
        summary_df.sort_values(["feature_set_name", "mae_mean", "spearman_mean"], ascending=[True, True, False])
        .groupby("feature_set_name", as_index=False)
        .first()
        .sort_values("mae_mean")
        .reset_index(drop=True)
    )


def select_best_overall(summary_df: pd.DataFrame) -> pd.Series:
    if summary_df.empty:
        raise ValueError("Cannot select best overall from an empty summary.")
    return summary_df.sort_values(["mae_mean", "spearman_mean"], ascending=[True, False]).iloc[0]


def build_delta_vs_metadata_table(best_df: pd.DataFrame) -> pd.DataFrame:
    if best_df.empty:
        return pd.DataFrame()
    baseline_row = best_df.loc[best_df["feature_set_name"] == "metadata_only"].iloc[0]
    baseline_mae = float(baseline_row["mae_mean"])
    practical_threshold = max(0.01, 0.5 * float(baseline_row.get("mae_std", 0.0)))
    rows = []
    for row in best_df.itertuples(index=False):
        delta_mae = float(row.mae_mean - baseline_mae)
        if delta_mae <= -practical_threshold:
            status = "improved"
        elif delta_mae >= practical_threshold:
            status = "worsened"
        else:
            status = "no_meaningful_change"
        rows.append(
            {
                "feature_set_name": row.feature_set_name,
                "feature_set_label": row.feature_set_label,
                "model_name": row.model_name,
                "mae_mean": float(row.mae_mean),
                "rmse_mean": float(row.rmse_mean),
                "spearman_mean": float(row.spearman_mean),
                "delta_mae_vs_metadata_only": delta_mae,
                "delta_rmse_vs_metadata_only": float(row.rmse_mean - baseline_row["rmse_mean"]),
                "delta_spearman_vs_metadata_only": float(row.spearman_mean - baseline_row["spearman_mean"]),
                "baseline_comparison_status": status,
                "baseline_status_threshold_kN": practical_threshold,
            }
        )
    return pd.DataFrame(rows).sort_values("mae_mean").reset_index(drop=True)


def _experiment_output_dir(base_dir: Path, feature_set_name: str, model_name: str) -> Path:
    return ensure_dir(base_dir / feature_set_name / model_name)


def run_experiment_suite(
    analysis_df: pd.DataFrame,
    row_manifest_df: pd.DataFrame,
    feature_sets: dict[str, list[str]],
    feature_set_labels: dict[str, str],
    model_names: list[str],
    analysis_name: str,
    split_name: str,
    modeling_cfg: dict,
    refocus_cfg: dict,
    output_dir: Path,
    compute_learning_curves: bool,
    make_diagnostic_plots: bool,
) -> dict[str, pd.DataFrame]:
    ensure_dir(output_dir)
    summary_frames = []
    importance_frames = []

    for feature_set_name, feature_cols in feature_sets.items():
        for model_name in model_names:
            experiment_dir = _experiment_output_dir(output_dir / "experiments", feature_set_name, model_name)
            result = evaluate_experiment(
                analysis_df=analysis_df,
                row_manifest_df=row_manifest_df,
                feature_cols=feature_cols,
                target_col="terminal_ultimate_load_kn_target",
                measured_target_col="ultimate_load_kn",
                model_name=model_name,
                modeling_cfg=modeling_cfg,
                refocus_cfg=refocus_cfg,
                predict_all_rows=False,
            )
            summary_df = summarise_experiment_summary(
                result["summary"],  # type: ignore[arg-type]
                analysis_name=analysis_name,
                split_name=split_name,
                feature_set_name=feature_set_name,
                feature_set_label=feature_set_labels[feature_set_name],
                model_name=model_name,
                n_features=len(feature_cols),
            )
            summary_frames.append(summary_df)

            save_dataframe_csv(result["fold_metrics"], experiment_dir / "fold_metrics.csv")  # type: ignore[arg-type]
            save_dataframe_csv(result["terminal_predictions"], experiment_dir / "terminal_fold_predictions.csv")  # type: ignore[arg-type]
            save_dataframe_csv(result["terminal_oof"], experiment_dir / "terminal_oof_predictions.csv")  # type: ignore[arg-type]
            save_dataframe_csv(result["fold_importance"], experiment_dir / "fold_feature_importance.csv")  # type: ignore[arg-type]
            save_dataframe_csv(summary_df, experiment_dir / "summary_metrics.csv")

            if not result["fold_importance"].empty:  # type: ignore[union-attr]
                fold_importance_summary = (
                    result["fold_importance"]  # type: ignore[union-attr]
                    .groupby(["feature", "importance_kind"], as_index=False)
                    .agg(
                        importance=("importance", "mean"),
                        importance_abs=("importance_abs", "mean"),
                    )
                    .sort_values("importance_abs", ascending=False)
                    .reset_index(drop=True)
                )
            else:
                fold_importance_summary = pd.DataFrame()
            importance_frames.append(
                fold_importance_summary.assign(
                    analysis_name=analysis_name,
                    split_name=split_name,
                    feature_set_name=feature_set_name,
                    model_name=model_name,
                )
            )
            save_dataframe_csv(fold_importance_summary, experiment_dir / "feature_importance_summary.csv")

            if compute_learning_curves:
                learning_raw_df, learning_summary_df = compute_learning_curve(
                    analysis_df=analysis_df,
                    row_manifest_df=row_manifest_df,
                    feature_cols=feature_cols,
                    target_col="terminal_ultimate_load_kn_target",
                    model_name=model_name,
                    modeling_cfg=modeling_cfg,
                    refocus_cfg=refocus_cfg,
                )
                save_dataframe_csv(learning_raw_df, experiment_dir / "learning_curve_raw.csv")
                save_dataframe_csv(learning_summary_df, experiment_dir / "learning_curve_summary.csv")
            else:
                learning_summary_df = pd.DataFrame()

            full_bundle, full_importance_df = fit_full_experiment_model(
                analysis_df=analysis_df,
                feature_cols=feature_cols,
                target_col="terminal_ultimate_load_kn_target",
                model_name=model_name,
                modeling_cfg=modeling_cfg,
                refocus_cfg=refocus_cfg,
            )
            save_dataframe_csv(full_importance_df, experiment_dir / "feature_importance_full_fit.csv")
            pdp_df = compute_partial_dependence_data(
                full_bundle,
                analysis_df,
                full_importance_df,
                top_n=int(refocus_cfg["diagnostics"]["partial_dependence_top_n"]),
            )
            save_dataframe_csv(pdp_df, experiment_dir / "partial_dependence.csv")

            if make_diagnostic_plots:
                title_prefix = f"{analysis_name} | {feature_set_labels[feature_set_name]} | {model_name}"
                plot_prediction_vs_truth(
                    result["terminal_oof"],  # type: ignore[arg-type]
                    experiment_dir / "prediction_vs_ground_truth.png",
                    f"{title_prefix}\nPrediction vs ground truth",
                )
                plot_residuals(
                    result["terminal_oof"],  # type: ignore[arg-type]
                    experiment_dir / "residual_analysis.png",
                    f"{title_prefix}\nResidual analysis",
                )
                plot_error_histogram(
                    result["terminal_oof"],  # type: ignore[arg-type]
                    experiment_dir / "error_distribution.png",
                    f"{title_prefix}\nError distribution",
                )
                plot_feature_importance(
                    full_importance_df,
                    experiment_dir / "feature_importance.png",
                    f"{title_prefix}\nFeature importance",
                    top_n=int(refocus_cfg["diagnostics"]["importance_top_n"]),
                )
                plot_partial_dependence(
                    pdp_df,
                    experiment_dir / "partial_dependence.png",
                    f"{title_prefix}\nPartial dependence",
                )
                plot_cv_stability(
                    result["fold_metrics"],  # type: ignore[arg-type]
                    experiment_dir / "cv_stability.png",
                    f"{title_prefix}\nCross-validation stability",
                )
                plot_uncertainty(
                    result["terminal_oof"],  # type: ignore[arg-type]
                    experiment_dir / "uncertainty.png",
                    f"{title_prefix}\nApproximate uncertainty",
                )
                if not learning_summary_df.empty:
                    plot_learning_curve(
                        learning_summary_df,
                        experiment_dir / "learning_curve.png",
                        f"{title_prefix}\nLearning curve",
                    )

    full_summary_df = pd.concat(summary_frames, ignore_index=True).sort_values(
        ["mae_mean", "spearman_mean"], ascending=[True, False]
    )
    save_dataframe_csv(full_summary_df, output_dir / "model_comparison.csv")
    if importance_frames:
        save_dataframe_csv(pd.concat(importance_frames, ignore_index=True), output_dir / "feature_importance_inventory.csv")

    best_by_feature_set_df = select_best_by_feature_set(full_summary_df)
    delta_df = build_delta_vs_metadata_table(best_by_feature_set_df)
    save_dataframe_csv(best_by_feature_set_df, output_dir / "feature_set_comparison.csv")
    save_dataframe_csv(delta_df, output_dir / "feature_set_delta_vs_metadata_only.csv")
    plot_model_metric_heatmap(
        full_summary_df,
        output_dir / "model_metric_heatmap.png",
        f"{analysis_name} | {split_name} | Model and feature-set comparison",
    )
    plot_best_feature_set_bars(
        best_by_feature_set_df,
        output_dir / "feature_set_comparison_bars.png",
        f"{analysis_name} | {split_name} | Best model per feature set",
    )
    return {
        "full_summary": full_summary_df,
        "best_by_feature_set": best_by_feature_set_df,
        "delta_vs_metadata": delta_df,
    }


def rerun_best_model_with_all_rows(
    analysis_df: pd.DataFrame,
    row_manifest_df: pd.DataFrame,
    feature_cols: list[str],
    model_name: str,
    modeling_cfg: dict,
    refocus_cfg: dict,
    output_dir: Path,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    result = evaluate_experiment(
        analysis_df=analysis_df,
        row_manifest_df=row_manifest_df,
        feature_cols=feature_cols,
        target_col="terminal_ultimate_load_kn_target",
        measured_target_col="ultimate_load_kn",
        model_name=model_name,
        modeling_cfg=modeling_cfg,
        refocus_cfg=refocus_cfg,
        predict_all_rows=True,
    )
    save_dataframe_csv(result["all_row_predictions"], output_dir / "all_rows_fold_predictions.csv")  # type: ignore[arg-type]
    save_dataframe_csv(result["all_row_oof"], output_dir / "all_rows_oof_predictions.csv")  # type: ignore[arg-type]
    save_dataframe_csv(result["terminal_oof"], output_dir / "terminal_specimen_oof_predictions.csv")  # type: ignore[arg-type]
    plot_all_specimen_trajectories(
        result["all_row_oof"],  # type: ignore[arg-type]
        output_dir / "all_specimen_prediction_trajectories(metadata-only+Ridge).png",
        "Best grouped-CV model: predicted terminal load across all observations",
    )
    return result["all_row_oof"], result["terminal_oof"]  # type: ignore[return-value]


def run_residual_refinement_suite(
    specimen_summary_df: pd.DataFrame,
    grouped_specimen_manifest_df: pd.DataFrame,
    modeling_cfg: dict,
    refocus_cfg: dict,
    output_dir: Path,
) -> dict[str, pd.DataFrame]:
    ensure_dir(output_dir)
    stage1_model_name = str(refocus_cfg["residual_refinement"]["stage1_model"])
    stage2_model_names = [str(value) for value in refocus_cfg["residual_refinement"]["stage2_models"]]
    stage1_feature_set_name = str(refocus_cfg["residual_refinement"]["stage1_feature_set"])
    if stage1_feature_set_name != "metadata_only":
        raise ValueError("Residual refinement currently expects the stage-main_first baseline to be metadata_only.")

    stage1_feature_cols = [
        column
        for column in METADATA_FEATURE_COLUMNS
        if column in specimen_summary_df.columns and column not in NON_FEATURE_COLUMNS
    ]
    stage2_feature_cols = build_residual_summary_feature_cols(specimen_summary_df, refocus_cfg)
    row_manifest_df = expand_specimen_manifest_to_rows(specimen_summary_df, grouped_specimen_manifest_df)
    balance_df = summarize_split_balance(grouped_specimen_manifest_df, row_manifest_df)

    save_dataframe_csv(specimen_summary_df, output_dir / "specimen_summary_table.csv")
    save_dataframe_csv(grouped_specimen_manifest_df, output_dir / "specimen_manifest.csv")
    save_dataframe_csv(row_manifest_df, output_dir / "row_manifest.csv")
    save_dataframe_csv(balance_df, output_dir / "balance_summary.csv")
    save_split_balance_plot(
        balance_df,
        output_dir / "balance.png",
        "Specimen-summary grouped CV split balance and leakage check",
    )

    baseline_dir = output_dir / "baseline"
    baseline_result = evaluate_experiment(
        analysis_df=specimen_summary_df,
        row_manifest_df=row_manifest_df,
        feature_cols=stage1_feature_cols,
        target_col="terminal_ultimate_load_kn_target",
        measured_target_col="ultimate_load_kn",
        model_name=stage1_model_name,
        modeling_cfg=modeling_cfg,
        refocus_cfg=refocus_cfg,
        predict_all_rows=False,
    )
    baseline_summary = summarise_experiment_summary(
        baseline_result["summary"],  # type: ignore[arg-type]
        analysis_name="specimen_summary_residual_refinement",
        split_name="grouped_cv",
        feature_set_name="specimen_metadata_only",
        feature_set_label="specimen-summary metadata-only",
        model_name=stage1_model_name,
        n_features=len(stage1_feature_cols),
    )
    baseline_summary["pipeline_name"] = "specimen_summary_metadata_baseline"
    baseline_summary["stage1_model_name"] = stage1_model_name
    baseline_summary["stage2_model_name"] = "none"

    save_dataframe_csv(baseline_result["fold_metrics"], baseline_dir / "fold_metrics.csv")  # type: ignore[arg-type]
    save_dataframe_csv(baseline_result["terminal_oof"], baseline_dir / "terminal_oof_predictions.csv")  # type: ignore[arg-type]
    save_dataframe_csv(baseline_summary, baseline_dir / "summary_metrics.csv")
    plot_prediction_vs_truth(
        baseline_result["terminal_oof"],  # type: ignore[arg-type]
        baseline_dir / "prediction_vs_ground_truth.png",
        "Specimen-summary metadata-only baseline\nPrediction vs ground truth",
    )
    plot_residuals(
        baseline_result["terminal_oof"],  # type: ignore[arg-type]
        baseline_dir / "residual_analysis.png",
        "Specimen-summary metadata-only baseline\nResidual analysis",
    )
    plot_error_histogram(
        baseline_result["terminal_oof"],  # type: ignore[arg-type]
        baseline_dir / "error_distribution.png",
        "Specimen-summary metadata-only baseline\nError distribution",
    )
    plot_cv_stability(
        baseline_result["fold_metrics"],  # type: ignore[arg-type]
        baseline_dir / "cv_stability.png",
        "Specimen-summary metadata-only baseline\nCross-validation stability",
    )
    plot_uncertainty(
        baseline_result["terminal_oof"],  # type: ignore[arg-type]
        baseline_dir / "uncertainty.png",
        "Specimen-summary metadata-only baseline\nApproximate uncertainty",
    )

    comparison_frames = [baseline_summary]
    best_prediction_map = {
        "specimen_summary_metadata_baseline": baseline_result["terminal_oof"].copy(),  # type: ignore[union-attr]
    }
    per_model_specimen_frames = []

    for stage2_model_name in stage2_model_names:
        experiment_dir = _experiment_output_dir(output_dir / "residual_models", "mesh_residual_summary", stage2_model_name)
        result = evaluate_residual_refinement(
            specimen_summary_df=specimen_summary_df,
            specimen_manifest_df=grouped_specimen_manifest_df,
            stage1_feature_cols=stage1_feature_cols,
            stage2_feature_cols=stage2_feature_cols,
            stage1_model_name=stage1_model_name,
            stage2_model_name=stage2_model_name,
            modeling_cfg=modeling_cfg,
            refocus_cfg=refocus_cfg,
        )
        summary_df = summarise_experiment_summary(
            result["summary"],  # type: ignore[arg-type]
            analysis_name="specimen_summary_residual_refinement",
            split_name="grouped_cv",
            feature_set_name="mesh_residual_summary",
            feature_set_label="metadata baseline + mesh residual summaries",
            model_name=stage2_model_name,
            n_features=len(stage2_feature_cols),
        )
        summary_df["pipeline_name"] = f"metadata_baseline_plus_mesh_residual_{stage2_model_name}"
        summary_df["stage1_model_name"] = stage1_model_name
        summary_df["stage2_model_name"] = stage2_model_name
        comparison_frames.append(summary_df)
        best_prediction_map[str(summary_df["pipeline_name"].iloc[0])] = result["terminal_oof"].copy()

        save_dataframe_csv(result["fold_metrics"], experiment_dir / "fold_metrics.csv")  # type: ignore[arg-type]
        save_dataframe_csv(result["fold_predictions"], experiment_dir / "terminal_fold_predictions.csv")  # type: ignore[arg-type]
        save_dataframe_csv(result["terminal_oof"], experiment_dir / "terminal_oof_predictions.csv")  # type: ignore[arg-type]
        save_dataframe_csv(summary_df, experiment_dir / "summary_metrics.csv")
        if not result["fold_importance"].empty:  # type: ignore[union-attr]
            fold_importance_summary = (
                result["fold_importance"]  # type: ignore[union-attr]
                .groupby(["feature", "importance_kind"], as_index=False)
                .agg(
                    importance=("importance", "mean"),
                    importance_abs=("importance_abs", "mean"),
                )
                .sort_values("importance_abs", ascending=False)
                .reset_index(drop=True)
            )
            fold_importance_summary["direction"] = np.where(
                fold_importance_summary["importance"] >= 0.0,
                "positive",
                "negative",
            )
            save_dataframe_csv(result["fold_importance"], experiment_dir / "fold_feature_importance.csv")  # type: ignore[arg-type]
            save_dataframe_csv(fold_importance_summary, experiment_dir / "feature_importance_summary.csv")
            plot_feature_importance(
                fold_importance_summary,
                experiment_dir / "feature_importance.png",
                f"Mesh residual refinement | {stage2_model_name}\nResidual-stage feature importance",
                top_n=int(refocus_cfg["diagnostics"]["importance_top_n"]),
            )
        else:
            fold_importance_summary = pd.DataFrame()
            save_dataframe_csv(fold_importance_summary, experiment_dir / "feature_importance_summary.csv")

        plot_prediction_vs_truth(
            result["terminal_oof"],  # type: ignore[arg-type]
            experiment_dir / "prediction_vs_ground_truth.png",
            f"Mesh residual refinement | {stage2_model_name}\nPrediction vs ground truth",
        )
        plot_residuals(
            result["terminal_oof"],  # type: ignore[arg-type]
            experiment_dir / "residual_analysis.png",
            f"Mesh residual refinement | {stage2_model_name}\nResidual analysis",
        )
        plot_error_histogram(
            result["terminal_oof"],  # type: ignore[arg-type]
            experiment_dir / "error_distribution.png",
            f"Mesh residual refinement | {stage2_model_name}\nError distribution",
        )
        plot_cv_stability(
            result["fold_metrics"],  # type: ignore[arg-type]
            experiment_dir / "cv_stability.png",
            f"Mesh residual refinement | {stage2_model_name}\nCross-validation stability",
        )
        plot_uncertainty(
            result["terminal_oof"],  # type: ignore[arg-type]
            experiment_dir / "uncertainty.png",
            f"Mesh residual refinement | {stage2_model_name}\nApproximate uncertainty",
        )

        specimen_compare = baseline_result["terminal_oof"].merge(  # type: ignore[union-attr]
            result["terminal_oof"][
                [
                    "sample_name",
                    "predicted_ultimate_load_kn",
                    "predicted_ultimate_load_kn_std",
                    "abs_error",
                    "residual",
                ]
            ].rename(
                columns={
                    "predicted_ultimate_load_kn": "candidate_predicted_ultimate_load_kn",
                    "predicted_ultimate_load_kn_std": "candidate_predicted_ultimate_load_kn_std",
                    "abs_error": "candidate_abs_error",
                    "residual": "candidate_residual",
                }
            ),
            on="sample_name",
            how="left",
            validate="one_to_one",
        ).rename(
            columns={
                "predicted_ultimate_load_kn": "baseline_predicted_ultimate_load_kn",
                "predicted_ultimate_load_kn_std": "baseline_predicted_ultimate_load_kn_std",
                "abs_error": "baseline_abs_error",
                "residual": "baseline_residual",
            }
        )
        specimen_compare["stage2_model_name"] = stage2_model_name
        specimen_compare["delta_abs_error"] = (
            specimen_compare["candidate_abs_error"] - specimen_compare["baseline_abs_error"]
        )
        specimen_compare["specimen_label"] = specimen_compare.apply(
            lambda row: f"{row['specimen_id']} | mesh {int(row['n_steel_mesh'])} | actual {row['ultimate_load_kn']:.2f} kN",
            axis=1,
        )
        specimen_compare["specimen_change_status"] = np.where(
            specimen_compare["delta_abs_error"] <= -0.05,
            "improved",
            np.where(specimen_compare["delta_abs_error"] >= 0.05, "worsened", "no_meaningful_change"),
        )
        per_model_specimen_frames.append(specimen_compare)
        save_dataframe_csv(specimen_compare, experiment_dir / "specimen_error_vs_baseline.csv")
        plot_error_delta_vs_baseline(
            specimen_compare.rename(columns={"candidate_abs_error": "refined_abs_error"}),
            experiment_dir / "specimen_error_delta_vs_baseline.png",
            f"Mesh residual refinement | {stage2_model_name}\nAbsolute error vs specimen-summary baseline",
            top_n=int(refocus_cfg["error_audit"]["top_n_specimens"]),
        )

    comparison_df = pd.concat(comparison_frames, ignore_index=True).sort_values(["mae_mean", "spearman_mean"], ascending=[True, False]).reset_index(drop=True)
    baseline_row = comparison_df.loc[comparison_df["pipeline_name"] == "specimen_summary_metadata_baseline"].iloc[0]
    threshold = max(0.01, 0.5 * float(baseline_row.get("mae_std", 0.0)))
    comparison_df["delta_mae_vs_baseline"] = comparison_df["mae_mean"] - float(baseline_row["mae_mean"])
    comparison_df["delta_rmse_vs_baseline"] = comparison_df["rmse_mean"] - float(baseline_row["rmse_mean"])
    comparison_df["delta_spearman_vs_baseline"] = comparison_df["spearman_mean"] - float(baseline_row["spearman_mean"])
    comparison_df["baseline_status_threshold_kN"] = threshold
    comparison_df["baseline_comparison_status"] = np.where(
        comparison_df["delta_mae_vs_baseline"] <= -threshold,
        "improved",
        np.where(
            comparison_df["delta_mae_vs_baseline"] >= threshold,
            "worsened",
            "no_meaningful_change",
        ),
    )
    save_dataframe_csv(comparison_df, output_dir / "model_comparison.csv")
    if per_model_specimen_frames:
        save_dataframe_csv(
            pd.concat(per_model_specimen_frames, ignore_index=True),
            output_dir / "per_model_specimen_error_vs_baseline.csv",
        )

    best_row = comparison_df.sort_values(["mae_mean", "spearman_mean"], ascending=[True, False]).iloc[0]
    save_dataframe_csv(pd.DataFrame([best_row]), output_dir / "best_model.csv")

    baseline_oof_df = best_prediction_map["specimen_summary_metadata_baseline"].copy()
    refined_oof_df = best_prediction_map[str(best_row["pipeline_name"])].copy()
    specimen_compare_df = baseline_oof_df.merge(
        refined_oof_df[
            [
                "sample_name",
                "predicted_ultimate_load_kn",
                "predicted_ultimate_load_kn_std",
                "abs_error",
                "residual",
            ]
        ].rename(
            columns={
                "predicted_ultimate_load_kn": "refined_predicted_ultimate_load_kn",
                "predicted_ultimate_load_kn_std": "refined_predicted_ultimate_load_kn_std",
                "abs_error": "refined_abs_error",
                "residual": "refined_residual",
            }
        ),
        on="sample_name",
        how="left",
        validate="one_to_one",
    )
    specimen_compare_df = specimen_compare_df.rename(
        columns={
            "predicted_ultimate_load_kn": "baseline_predicted_ultimate_load_kn",
            "predicted_ultimate_load_kn_std": "baseline_predicted_ultimate_load_kn_std",
            "abs_error": "baseline_abs_error",
            "residual": "baseline_residual",
        }
    )
    specimen_compare_df["delta_abs_error"] = (
        specimen_compare_df["refined_abs_error"] - specimen_compare_df["baseline_abs_error"]
    )
    specimen_compare_df["delta_prediction"] = (
        specimen_compare_df["refined_predicted_ultimate_load_kn"] - specimen_compare_df["baseline_predicted_ultimate_load_kn"]
    )
    specimen_compare_df["specimen_label"] = specimen_compare_df.apply(
        lambda row: f"{row['specimen_id']} | mesh {int(row['n_steel_mesh'])} | actual {row['ultimate_load_kn']:.2f} kN",
        axis=1,
    )
    specimen_compare_df["specimen_change_status"] = np.where(
        specimen_compare_df["delta_abs_error"] <= -0.05,
        "improved",
        np.where(specimen_compare_df["delta_abs_error"] >= 0.05, "worsened", "no_meaningful_change"),
    )
    save_dataframe_csv(specimen_compare_df, output_dir / "specimen_error_comparison_vs_baseline.csv")
    save_dataframe_csv(
        specimen_compare_df.sort_values("baseline_abs_error", ascending=False).head(
            int(refocus_cfg["error_audit"]["top_n_specimens"])
        ),
        output_dir / "hard_specimen_error_comparison.csv",
    )
    plot_error_delta_vs_baseline(
        specimen_compare_df,
        output_dir / "hard_specimen_error_delta_vs_baseline.png",
        "Specimen-summary baseline vs residual-refined absolute error",
        top_n=int(refocus_cfg["error_audit"]["top_n_specimens"]),
    )

    return {
        "comparison": comparison_df,
        "baseline_oof": baseline_oof_df,
        "best_oof": refined_oof_df,
        "specimen_comparison": specimen_compare_df,
    }


def write_repo_audit_markdown(output_path: Path) -> None:
    text = """# Repo Audit For Ultimate-Load Refocus

## What already supports the refocused objective

- The canonical `master_table.csv` already preserves `ultimate_load_kn`, `wire_area_loss_frac`, specimen metadata, campaign labels, and the grouped leakage key `specimen_id`.
- The existing image-feature extractor is deterministic and interpretable, which is appropriate for a conservative thesis-style load-estimation study.
- The repo already contains grouped split utilities and a useful mesh-stratified correlation script for `ultimate_load_kn`.
- The current benchmark stack already supports `RandomForest`, `GradientBoosting`, `XGBoost`, and `CatBoost`, so the new workflow can reuse familiar model families.

## What conflicts with the refocused objective

- The repository README, reports, and top-level workflow still center hidden-damage inference, degradation modeling, and proxy-RUL rather than direct terminal-capacity estimation.
- The prior structural modeling stage uses only terminal rows, then immediately routes predictions into degradation and threshold logic, which is not the main research question here.
- The old output structure does not separate measured `ultimate_load_kn` from predicted load estimates for every observation.
- The previous evaluation bundle is leakage-safe but too minimal for the requested transparency package: it lacks specimen manifests, fold-balance summaries, uncertainty summaries, learning curves per experiment, and organized diagnostic outputs.
- HSV descriptors were not present in the original image characterization, so RGB-versus-HSV feature-family comparisons were not possible.

## Scientific cautions discovered during the audit

- `n_steel_mesh` is perfectly aligned with campaign in this dataset: all 7-mesh specimens are in `campaign_1`, and all 4-mesh specimens are in `campaign_2`.
- Because of that alignment, pooled leave-one-campaign-out is a harsh campaign-plus-mesh extrapolation stress test, not a clean within-mesh generalization estimate.
- For the central corrosion-versus-load question, mesh-stratified analyses are therefore scientifically preferred over pooled raw correlations.
- Visible surface corrosion remains only a superficial descriptor. It should not be described as a direct measurement of hidden/internal corrosion or as residual useful life.
"""
    write_text(output_path, text)


def write_summary_markdown(
    output_path: Path,
    refocus_cfg: dict,
    grouped_best_df: pd.DataFrame,
    grouped_delta_df: pd.DataFrame,
    loco_best_df: pd.DataFrame,
    mesh_best_df: pd.DataFrame,
) -> None:
    best_row = grouped_best_df.iloc[0]
    metadata_row = grouped_best_df.loc[grouped_best_df["feature_set_name"] == "metadata_only"].iloc[0]
    non_metadata_delta_df = grouped_delta_df.loc[grouped_delta_df["feature_set_name"] != "metadata_only"].copy()
    best_non_metadata_row = (
        non_metadata_delta_df.sort_values("mae_mean").iloc[0] if not non_metadata_delta_df.empty else None
    )
    summary_lines = [
        "# Ultimate-Load Refocus Summary",
        "",
        "## What was run",
        "",
        "- A new leakage-safe terminal-capacity workflow under `outputs/ultimate_load_refocus/`.",
        "- Pooled grouped cross-validation on all weeks retained.",
        "- Pooled leave-one-campaign-out as a stress test only.",
        f"- Post-onset sensitivity analysis using `{refocus_cfg['surface_onset']['threshold_column']} >= {float(refocus_cfg['surface_onset']['threshold_pct']):.3f}`.",
        "- Mesh-stratified grouped analyses for 4-mesh and 7-mesh specimens.",
        "- Feature-family comparisons across metadata, RGB, HSV, and combined descriptors.",
        "",
        "## Best grouped-CV result",
        "",
        f"- Best grouped-CV configuration: `{best_row['model_name']}` with `{best_row['feature_set_label']}`.",
        f"- Grouped-CV MAE: `{best_row['mae_mean']:.3f} +- {best_row['mae_std']:.3f}` kN.",
        f"- Grouped-CV RMSE: `{best_row['rmse_mean']:.3f} +- {best_row['rmse_std']:.3f}` kN.",
        f"- Grouped-CV Spearman: `{best_row['spearman_mean']:.3f} +- {best_row['spearman_std']:.3f}`.",
        "",
        "## Does superficial corrosion add value beyond metadata?",
        "",
        f"- Metadata-only grouped-CV baseline: `{metadata_row['model_name']}` with MAE `{metadata_row['mae_mean']:.3f}` kN and Spearman `{metadata_row['spearman_mean']:.3f}`.",
    ]
    if best_non_metadata_row is not None:
        summary_lines.extend(
            [
                f"- Best non-baseline feature set: `{best_non_metadata_row['feature_set_label']}` with "
                f"`{best_non_metadata_row['model_name']}`.",
                f"- Relative to metadata-only, this was classified as "
                f"`{best_non_metadata_row['baseline_comparison_status']}` "
                f"(delta MAE `{best_non_metadata_row['delta_mae_vs_metadata_only']:+.3f}` kN, "
                f"delta Spearman `{best_non_metadata_row['delta_spearman_vs_metadata_only']:+.3f}`).",
            ]
        )
    summary_lines.extend(
        [
            "- See `feature_set_delta_vs_metadata_only.csv` for the full baseline-relative comparison table.",
        ]
    )
    summary_lines.extend(
        [
        "",
        "## Stress-test interpretation",
        "",
        "- Leave-one-campaign-out is retained, but it should be interpreted conservatively because campaign and mesh family are perfectly aligned in this dataset.",
        "- Mesh-stratified grouped analyses are the preferred basis for the main scientific claim about superficial corrosion versus terminal load.",
        "",
        "## What should and should not be claimed",
        "",
        "- The project estimates terminal structural capacity (`ultimate_load_kn`) from metadata and image-derived superficial-corrosion descriptors.",
        "- The project does not measure hidden/internal corrosion directly.",
        "- The project does not produce true RUL or full-life prediction.",
        "- Any uncertainty reported here is approximate and comes from held-out prediction variability across repeated grouped folds.",
        ]
    )
    if not loco_best_df.empty:
        summary_lines.extend(
            [
                "",
                "## Leave-one-campaign-out best feature-set summary",
                "",
                *[
                    f"- `{row.feature_set_label}`: `{row.model_name}` with MAE `{row.mae_mean:.3f}` kN and Spearman `{row.spearman_mean:.3f}`."
                    for row in loco_best_df.itertuples(index=False)
                ],
            ]
        )
    if not mesh_best_df.empty:
        summary_lines.extend(
            [
                "",
                "## Mesh-stratified highlights",
                "",
                *[
                    f"- `{row.analysis_name}` / `{row.feature_set_label}`: `{row.model_name}` with MAE `{row.mae_mean:.3f}` kN and Spearman `{row.spearman_mean:.3f}`."
                    for row in mesh_best_df.itertuples(index=False)
                ],
            ]
        )
    if not grouped_delta_df.empty:
        summary_lines.extend(
            [
                "",
                "## Baseline-relative comparison labels",
                "",
                *[
                    f"- `{row.feature_set_label}`: `{row.baseline_comparison_status}` relative to metadata-only "
                    f"(delta MAE `{row.delta_mae_vs_metadata_only:+.3f}` kN, delta Spearman `{row.delta_spearman_vs_metadata_only:+.3f}`)."
                    for row in grouped_delta_df.itertuples(index=False)
                ],
            ]
    )
    write_text(output_path, "\n".join(summary_lines))


def write_gap_refinement_markdown(
    output_path: Path,
    error_summary_df: pd.DataFrame,
    residual_comparison_df: pd.DataFrame,
    specimen_compare_df: pd.DataFrame,
) -> None:
    lines = [
        "# Specimen Gap Refinement Summary",
        "",
        "## What was added",
        "",
        "- A specimen-level error audit across the best model from each main feature set.",
        "- A leakage-safe two-stage refinement that predicts terminal load from metadata main_first, then applies a within-mesh residual correction using compact superficial-corrosion summaries.",
        "",
    ]

    if not error_summary_df.empty:
        persistent_df = error_summary_df.loc[error_summary_df["gap_class"] == "persistent_hard"].copy()
        sensitive_df = error_summary_df.loc[error_summary_df["gap_class"] == "approach_sensitive"].copy()
        lines.extend(
            [
                "## Specimen-level gap audit",
                "",
                f"- Persistent hard specimens (large error across many best-per-feature-set models): `{', '.join(persistent_df['specimen_id'].head(8).tolist())}`."
                if not persistent_df.empty
                else "- No persistent hard specimens met the configured threshold.",
                f"- Approach-sensitive specimens (error changes materially by feature set/model): `{', '.join(sensitive_df['specimen_id'].head(8).tolist())}`."
                if not sensitive_df.empty
                else "- No strongly approach-sensitive specimens met the configured threshold.",
                "",
            ]
        )

    if not residual_comparison_df.empty:
        baseline_row = residual_comparison_df.loc[
            residual_comparison_df["pipeline_name"] == "specimen_summary_metadata_baseline"
        ].iloc[0]
        best_row = residual_comparison_df.sort_values(["mae_mean", "spearman_mean"], ascending=[True, False]).iloc[0]
        lines.extend(
            [
                "## Residual refinement result",
                "",
                f"- Specimen-summary metadata baseline: `{baseline_row['stage1_model_name']}` with MAE `{baseline_row['mae_mean']:.3f}` kN and Spearman `{baseline_row['spearman_mean']:.3f}`.",
                f"- Best residual-refinement pipeline: stage-main_first `{best_row['stage1_model_name']}` plus stage-2 `{best_row['stage2_model_name']}` with MAE `{best_row['mae_mean']:.3f}` kN and Spearman `{best_row['spearman_mean']:.3f}`.",
                f"- Relative to the specimen-summary metadata baseline, this was `{best_row['baseline_comparison_status']}` (delta MAE `{best_row['delta_mae_vs_baseline']:+.3f}` kN; delta Spearman `{best_row['delta_spearman_vs_baseline']:+.3f}`).",
                "",
            ]
        )

    if not specimen_compare_df.empty:
        improved = specimen_compare_df.loc[specimen_compare_df["specimen_change_status"] == "improved"].copy()
        worsened = specimen_compare_df.loc[specimen_compare_df["specimen_change_status"] == "worsened"].copy()
        improved = improved.sort_values("delta_abs_error")
        worsened = worsened.sort_values("delta_abs_error", ascending=False)
        lines.extend(
            [
                "## Specimen-level effect of the best refinement",
                "",
                f"- Largest specimen-level improvements: `{', '.join(improved['specimen_id'].head(6).tolist())}`."
                if not improved.empty
                else "- No specimen-level improvements exceeded the practical change threshold.",
                f"- Largest specimen-level worsenings: `{', '.join(worsened['specimen_id'].head(6).tolist())}`."
                if not worsened.empty
                else "- No specimen-level worsenings exceeded the practical change threshold.",
                "",
                "## Interpretation",
                "",
                "- If a specimen remains hard across the error audit and the residual-refinement stage, that gap is unlikely to be resolved by model swapping alone.",
                "- If a specimen improves only in some approaches, it is better described as model-sensitive than fundamentally unexplained.",
            ]
        )

    write_text(output_path, "\n".join(lines))


def save_output_inventory(output_root: Path) -> Path:
    rows = []
    for path in sorted(output_root.rglob("*")):
        if path.is_dir():
            continue
        rows.append(
            {
                "path": str(path),
                "relative_path": str(path.relative_to(output_root)),
                "suffix": path.suffix,
                "size_bytes": path.stat().st_size,
            }
        )
    inventory_df = pd.DataFrame(rows)
    inventory_path = output_root / "output_manifest.csv"
    save_dataframe_csv(inventory_df, inventory_path)
    return inventory_path


def run_ultimate_load_refocus(master_df: pd.DataFrame, configs: dict, logger) -> dict[str, str]:
    modeling_cfg = configs["modeling"]
    feature_cfg = configs["features"]["image_features"]
    refocus_cfg = configs["ultimate_load_refocus"]
    output_root = ensure_dir(OUTPUT_DIR / refocus_cfg["output_namespace"])

    logger.info("Extracting extended RGB+HSV image features for the refocused workflow.")
    image_feature_df, failures_df = extract_image_feature_table(master_df, feature_cfg, logger)
    save_dataframe_csv(image_feature_df, output_root / "features" / "image_features_rgb_hsv.csv")
    save_dataframe_csv(failures_df, output_root / "features" / "image_feature_failures.csv")
    save_dataframe_csv(feature_dictionary(), output_root / "features" / "feature_dictionary.csv")

    logger.info("Building refocused all-weeks modeling table.")
    refocus_df = _build_refocus_table(master_df, image_feature_df, refocus_cfg)
    specimen_df = build_specimen_manifest(refocus_df)
    specimen_summary_df = build_specimen_summary_table(refocus_df, refocus_cfg)
    terminal_df = refocus_df.loc[refocus_df["is_measured_ultimate_load"]].copy()
    feature_inventory_df = build_feature_family_inventory(refocus_df)
    feature_sets = build_feature_sets(refocus_df, refocus_cfg)
    feature_set_labels = {
        key: value["label"] for key, value in refocus_cfg["feature_sets"].items()
    }

    save_dataframe_csv(refocus_df, output_root / "data" / "ultimate_load_modeling_table_all_weeks.csv")
    save_dataframe_csv(
        refocus_df.loc[refocus_df["is_post_visible_corrosion_onset"]].copy(),
        output_root / "data" / "ultimate_load_modeling_table_post_onset.csv",
    )
    save_dataframe_csv(specimen_df, output_root / "data" / "specimen_manifest.csv")
    save_dataframe_csv(feature_inventory_df, output_root / "features" / "feature_family_inventory.csv")
    if not specimen_summary_df.empty:
        save_dataframe_csv(specimen_summary_df, output_root / "data" / "specimen_summary_table.csv")

    logger.info("Running mesh-stratified corrosion-to-load correlations.")
    correlation_df, _figure_path = run_mesh_stratified_correlations(
        terminal_df=terminal_df,
        correlation_columns=list(refocus_cfg["diagnostics"]["correlation_columns"]),
        output_dir=output_root / "correlations",
    )

    write_repo_audit_markdown(output_root / "audit" / "repo_audit.md")

    logger.info("Building split manifests with specimen-grouped leakage safety.")
    grouped_specimen_manifest_df = _build_specimen_cv_manifest(
        specimen_df=specimen_df,
        split_name="grouped_cv",
        n_splits=int(refocus_cfg["grouped_cv"]["n_splits"]),
        n_repeats=int(refocus_cfg["grouped_cv"]["n_repeats"]),
        random_state=int(refocus_cfg["random_state"]),
        stratify_col=refocus_cfg["grouped_cv"].get("stratify_by"),
    )
    grouped_row_manifest_df = expand_specimen_manifest_to_rows(refocus_df, grouped_specimen_manifest_df)
    grouped_balance_df = summarize_split_balance(grouped_specimen_manifest_df, grouped_row_manifest_df)
    save_dataframe_csv(grouped_specimen_manifest_df, output_root / "splits" / "grouped_cv_specimen_manifest.csv")
    save_dataframe_csv(grouped_row_manifest_df, output_root / "splits" / "grouped_cv_row_manifest.csv")
    save_dataframe_csv(grouped_balance_df, output_root / "splits" / "grouped_cv_balance_summary.csv")
    save_split_balance_plot(
        grouped_balance_df,
        output_root / "splits" / "grouped_cv_balance.png",
        "Grouped CV split balance and leakage check",
    )

    loco_specimen_manifest_df = _build_leave_one_campaign_out_manifest(specimen_df, "leave_one_campaign_out")
    loco_row_manifest_df = expand_specimen_manifest_to_rows(refocus_df, loco_specimen_manifest_df)
    loco_balance_df = summarize_split_balance(loco_specimen_manifest_df, loco_row_manifest_df)
    save_dataframe_csv(loco_specimen_manifest_df, output_root / "splits" / "leave_one_campaign_out_specimen_manifest.csv")
    save_dataframe_csv(loco_row_manifest_df, output_root / "splits" / "leave_one_campaign_out_row_manifest.csv")
    save_dataframe_csv(loco_balance_df, output_root / "splits" / "leave_one_campaign_out_balance_summary.csv")
    save_split_balance_plot(
        loco_balance_df,
        output_root / "splits" / "leave_one_campaign_out_balance.png",
        "Leave-one-campaign-out split balance and leakage check",
    )

    model_names = ["RandomForest", "CatBoost", "XGBoost", "GradientBoosting", "Ridge"]

    logger.info("Running pooled grouped-CV model sweep across all candidate models and feature sets.")
    grouped_results = run_experiment_suite(
        analysis_df=refocus_df,
        row_manifest_df=grouped_row_manifest_df,
        feature_sets=feature_sets,
        feature_set_labels=feature_set_labels,
        model_names=model_names,
        analysis_name="pooled_all_weeks",
        split_name="grouped_cv",
        modeling_cfg=modeling_cfg,
        refocus_cfg=refocus_cfg,
        output_dir=output_root / "pooled_all_weeks" / "grouped_cv",
        compute_learning_curves=True,
        make_diagnostic_plots=True,
    )
    logger.info("Building specimen-level error audit across the best model from each feature set.")
    error_audit_long_df, error_audit_summary_df, error_audit_wide_df = build_best_feature_set_error_audit(
        output_root / "pooled_all_weeks" / "grouped_cv",
        grouped_results["best_by_feature_set"],
        refocus_cfg,
    )
    save_dataframe_csv(error_audit_long_df, output_root / "error_audit" / "best_feature_set_specimen_errors_long.csv")
    save_dataframe_csv(error_audit_summary_df, output_root / "error_audit" / "specimen_error_summary.csv")
    save_dataframe_csv(error_audit_wide_df, output_root / "error_audit" / "best_feature_set_specimen_errors_wide.csv")
    if not error_audit_summary_df.empty:
        save_dataframe_csv(
            error_audit_summary_df.loc[
                error_audit_summary_df["gap_class"].isin(["persistent_hard", "mostly_hard", "approach_sensitive"])
            ].copy(),
            output_root / "error_audit" / "priority_specimens.csv",
        )
        plot_specimen_error_heatmap(
            error_audit_long_df,
            error_audit_summary_df,
            output_root / "error_audit" / "specimen_error_heatmap.png",
            "Specimen-level absolute error across best feature-set models",
            top_n=int(refocus_cfg["error_audit"]["top_n_specimens"]),
        )
        plot_specimen_error_span(
            error_audit_summary_df,
            output_root / "error_audit" / "specimen_error_span.png",
            "Best-to-worst specimen error span across best feature-set models",
            hard_threshold=float(refocus_cfg["error_audit"]["hard_abs_error_kN"]),
            top_n=int(refocus_cfg["error_audit"]["top_n_specimens"]),
        )

    logger.info("Running pooled leave-one-campaign-out stress-test sweep.")
    loco_results = run_experiment_suite(
        analysis_df=refocus_df,
        row_manifest_df=loco_row_manifest_df,
        feature_sets=feature_sets,
        feature_set_labels=feature_set_labels,
        model_names=model_names,
        analysis_name="pooled_all_weeks",
        split_name="leave_one_campaign_out",
        modeling_cfg=modeling_cfg,
        refocus_cfg=refocus_cfg,
        output_dir=output_root / "pooled_all_weeks" / "leave_one_campaign_out",
        compute_learning_curves=False,
        make_diagnostic_plots=False,
    )

    best_feature_set_grouped_df = grouped_results["best_by_feature_set"].copy()
    selected_model_map = {
        row.feature_set_name: row.model_name for row in best_feature_set_grouped_df.itertuples(index=False)
    }
    best_feature_sets_only = {
        feature_set_name: feature_sets[feature_set_name] for feature_set_name in best_feature_set_grouped_df["feature_set_name"]
    }

    logger.info("Running pooled post-onset sensitivity analysis with the grouped-CV-selected best model per feature set.")
    post_onset_df = refocus_df.loc[refocus_df["is_post_visible_corrosion_onset"]].copy()
    post_onset_specimens = build_specimen_manifest(post_onset_df)
    post_onset_grouped_specimen_manifest_df = _build_specimen_cv_manifest(
        specimen_df=post_onset_specimens,
        split_name="grouped_cv",
        n_splits=int(refocus_cfg["grouped_cv"]["n_splits"]),
        n_repeats=int(refocus_cfg["grouped_cv"]["n_repeats"]),
        random_state=int(refocus_cfg["random_state"]),
        stratify_col=refocus_cfg["grouped_cv"].get("stratify_by"),
    )
    post_onset_grouped_row_manifest_df = expand_specimen_manifest_to_rows(post_onset_df, post_onset_grouped_specimen_manifest_df)
    post_onset_grouped_balance_df = summarize_split_balance(
        post_onset_grouped_specimen_manifest_df,
        post_onset_grouped_row_manifest_df,
    )
    save_dataframe_csv(post_onset_grouped_specimen_manifest_df, output_root / "pooled_post_onset" / "grouped_cv" / "specimen_manifest.csv")
    save_dataframe_csv(post_onset_grouped_row_manifest_df, output_root / "pooled_post_onset" / "grouped_cv" / "row_manifest.csv")
    save_dataframe_csv(post_onset_grouped_balance_df, output_root / "pooled_post_onset" / "grouped_cv" / "balance_summary.csv")
    save_split_balance_plot(
        post_onset_grouped_balance_df,
        output_root / "pooled_post_onset" / "grouped_cv" / "balance.png",
        "Post-onset grouped CV split balance and leakage check",
    )
    post_onset_feature_sets = {
        feature_set_name: best_feature_sets_only[feature_set_name] for feature_set_name in best_feature_sets_only
    }

    # Re-run the grouped-selected best model only for each post-onset feature set.
    post_onset_rows = []
    for feature_set_name, feature_cols in post_onset_feature_sets.items():
        model_name = selected_model_map[feature_set_name]
        experiment_dir = _experiment_output_dir(
            output_root / "pooled_post_onset" / "grouped_cv" / "selected_best_models" / "experiments",
            feature_set_name,
            model_name,
        )
        result = evaluate_experiment(
            analysis_df=post_onset_df,
            row_manifest_df=post_onset_grouped_row_manifest_df,
            feature_cols=feature_cols,
            target_col="terminal_ultimate_load_kn_target",
            measured_target_col="ultimate_load_kn",
            model_name=model_name,
            modeling_cfg=modeling_cfg,
            refocus_cfg=refocus_cfg,
            predict_all_rows=False,
        )
        summary_df = summarise_experiment_summary(
            result["summary"],  # type: ignore[arg-type]
            analysis_name="pooled_post_onset",
            split_name="grouped_cv",
            feature_set_name=feature_set_name,
            feature_set_label=feature_set_labels[feature_set_name],
            model_name=model_name,
            n_features=len(feature_cols),
        )
        post_onset_rows.append(summary_df)
        save_dataframe_csv(result["fold_metrics"], experiment_dir / "fold_metrics.csv")  # type: ignore[arg-type]
        save_dataframe_csv(result["terminal_oof"], experiment_dir / "terminal_oof_predictions.csv")  # type: ignore[arg-type]
        save_dataframe_csv(summary_df, experiment_dir / "summary_metrics.csv")
    if post_onset_rows:
        post_onset_best_df = pd.concat(post_onset_rows, ignore_index=True).sort_values("mae_mean").reset_index(drop=True)
    else:
        post_onset_best_df = pd.DataFrame()
    save_dataframe_csv(post_onset_best_df, output_root / "pooled_post_onset" / "grouped_cv" / "selected_best_model_per_feature_set.csv")

    post_onset_loco_specimen_manifest_df = _build_leave_one_campaign_out_manifest(post_onset_specimens, "leave_one_campaign_out")
    post_onset_loco_row_manifest_df = expand_specimen_manifest_to_rows(post_onset_df, post_onset_loco_specimen_manifest_df)
    post_onset_loco_balance_df = summarize_split_balance(
        post_onset_loco_specimen_manifest_df,
        post_onset_loco_row_manifest_df,
    )
    save_dataframe_csv(post_onset_loco_specimen_manifest_df, output_root / "pooled_post_onset" / "leave_one_campaign_out" / "specimen_manifest.csv")
    save_dataframe_csv(post_onset_loco_row_manifest_df, output_root / "pooled_post_onset" / "leave_one_campaign_out" / "row_manifest.csv")
    save_dataframe_csv(post_onset_loco_balance_df, output_root / "pooled_post_onset" / "leave_one_campaign_out" / "balance_summary.csv")
    save_split_balance_plot(
        post_onset_loco_balance_df,
        output_root / "pooled_post_onset" / "leave_one_campaign_out" / "balance.png",
        "Post-onset leave-one-campaign-out split balance and leakage check",
    )
    post_onset_loco_rows = []
    for feature_set_name, feature_cols in post_onset_feature_sets.items():
        model_name = selected_model_map[feature_set_name]
        experiment_dir = _experiment_output_dir(
            output_root / "pooled_post_onset" / "leave_one_campaign_out" / "selected_best_models" / "experiments",
            feature_set_name,
            model_name,
        )
        result = evaluate_experiment(
            analysis_df=post_onset_df,
            row_manifest_df=post_onset_loco_row_manifest_df,
            feature_cols=feature_cols,
            target_col="terminal_ultimate_load_kn_target",
            measured_target_col="ultimate_load_kn",
            model_name=model_name,
            modeling_cfg=modeling_cfg,
            refocus_cfg=refocus_cfg,
            predict_all_rows=False,
        )
        summary_df = summarise_experiment_summary(
            result["summary"],  # type: ignore[arg-type]
            analysis_name="pooled_post_onset",
            split_name="leave_one_campaign_out",
            feature_set_name=feature_set_name,
            feature_set_label=feature_set_labels[feature_set_name],
            model_name=model_name,
            n_features=len(feature_cols),
        )
        post_onset_loco_rows.append(summary_df)
        save_dataframe_csv(result["fold_metrics"], experiment_dir / "fold_metrics.csv")  # type: ignore[arg-type]
        save_dataframe_csv(result["terminal_oof"], experiment_dir / "terminal_oof_predictions.csv")  # type: ignore[arg-type]
        save_dataframe_csv(summary_df, experiment_dir / "summary_metrics.csv")
    if post_onset_loco_rows:
        post_onset_loco_best_df = (
            pd.concat(post_onset_loco_rows, ignore_index=True).sort_values("mae_mean").reset_index(drop=True)
        )
    else:
        post_onset_loco_best_df = pd.DataFrame()
    save_dataframe_csv(
        post_onset_loco_best_df,
        output_root / "pooled_post_onset" / "leave_one_campaign_out" / "selected_best_model_per_feature_set.csv",
    )

    logger.info("Running mesh-stratified grouped analyses with grouped-CV-selected best models per feature set.")
    mesh_result_rows = []
    for mesh_value in [4, 7]:
        mesh_df = refocus_df.loc[refocus_df["n_steel_mesh"] == mesh_value].copy()
        mesh_specimens = build_specimen_manifest(mesh_df)
        mesh_specimen_manifest_df = _build_specimen_cv_manifest(
            specimen_df=mesh_specimens,
            split_name="grouped_cv",
            n_splits=int(refocus_cfg["mesh_grouped_cv"]["n_splits"]),
            n_repeats=int(refocus_cfg["mesh_grouped_cv"]["n_repeats"]),
            random_state=int(refocus_cfg["random_state"]),
            stratify_col=None,
        )
        mesh_row_manifest_df = expand_specimen_manifest_to_rows(mesh_df, mesh_specimen_manifest_df)
        mesh_output_root = output_root / "mesh_stratified" / f"mesh_{mesh_value}" / "grouped_cv"
        save_dataframe_csv(mesh_specimen_manifest_df, mesh_output_root / "specimen_manifest.csv")
        save_dataframe_csv(mesh_row_manifest_df, mesh_output_root / "row_manifest.csv")
        mesh_balance_df = summarize_split_balance(mesh_specimen_manifest_df, mesh_row_manifest_df)
        save_dataframe_csv(mesh_balance_df, mesh_output_root / "balance_summary.csv")
        save_split_balance_plot(
            mesh_balance_df,
            mesh_output_root / "balance.png",
            f"Mesh {mesh_value} grouped CV split balance and leakage check",
        )
        for feature_set_name, feature_cols in best_feature_sets_only.items():
            model_name = selected_model_map[feature_set_name]
            experiment_dir = _experiment_output_dir(mesh_output_root / "selected_best_models" / "experiments", feature_set_name, model_name)
            result = evaluate_experiment(
                analysis_df=mesh_df,
                row_manifest_df=mesh_row_manifest_df,
                feature_cols=feature_cols,
                target_col="terminal_ultimate_load_kn_target",
                measured_target_col="ultimate_load_kn",
                model_name=model_name,
                modeling_cfg=modeling_cfg,
                refocus_cfg=refocus_cfg,
                predict_all_rows=False,
            )
            summary_df = summarise_experiment_summary(
                result["summary"],  # type: ignore[arg-type]
                analysis_name=f"mesh_{mesh_value}",
                split_name="grouped_cv",
                feature_set_name=feature_set_name,
                feature_set_label=feature_set_labels[feature_set_name],
                model_name=model_name,
                n_features=len(feature_cols),
            )
            mesh_result_rows.append(summary_df)
            save_dataframe_csv(result["fold_metrics"], experiment_dir / "fold_metrics.csv")  # type: ignore[arg-type]
            save_dataframe_csv(result["terminal_oof"], experiment_dir / "terminal_oof_predictions.csv")  # type: ignore[arg-type]
            save_dataframe_csv(summary_df, experiment_dir / "summary_metrics.csv")
    mesh_best_df = pd.concat(mesh_result_rows, ignore_index=True).sort_values(["analysis_name", "mae_mean"]).reset_index(drop=True)
    save_dataframe_csv(mesh_best_df, output_root / "mesh_stratified" / "mesh_feature_set_comparison.csv")

    grouped_best_df = grouped_results["best_by_feature_set"]
    grouped_delta_df = grouped_results["delta_vs_metadata"]
    loco_best_df = loco_results["best_by_feature_set"]

    best_overall_row = select_best_overall(grouped_results["full_summary"])
    best_feature_cols = feature_sets[best_overall_row["feature_set_name"]]
    best_model_dir = output_root / "pooled_all_weeks" / "grouped_cv" / "best_model_package"
    save_dataframe_csv(pd.DataFrame([best_overall_row]), best_model_dir / "selected_best_model.csv")
    best_all_rows_oof_df, best_terminal_oof_df = rerun_best_model_with_all_rows(
        analysis_df=refocus_df,
        row_manifest_df=grouped_row_manifest_df,
        feature_cols=best_feature_cols,
        model_name=best_overall_row["model_name"],
        modeling_cfg=modeling_cfg,
        refocus_cfg=refocus_cfg,
        output_dir=best_model_dir,
    )

    if refocus_cfg.get("residual_refinement", {}).get("enabled", False) and not specimen_summary_df.empty:
        logger.info("Running specimen-summary residual refinement for hard specimen gaps.")
        residual_results = run_residual_refinement_suite(
            specimen_summary_df=specimen_summary_df,
            grouped_specimen_manifest_df=grouped_specimen_manifest_df,
            modeling_cfg=modeling_cfg,
            refocus_cfg=refocus_cfg,
            output_dir=output_root / "residual_refinement",
        )
    else:
        residual_results = {
            "comparison": pd.DataFrame(),
            "baseline_oof": pd.DataFrame(),
            "best_oof": pd.DataFrame(),
            "specimen_comparison": pd.DataFrame(),
        }

    comparison_rows = []
    for row in grouped_best_df.itertuples(index=False):
        comparison_rows.append(
            {
                "analysis_name": "pooled_all_weeks_grouped_cv",
                **row._asdict(),
            }
        )
    for row in loco_best_df.itertuples(index=False):
        comparison_rows.append(
            {
                "analysis_name": "pooled_all_weeks_leave_one_campaign_out",
                **row._asdict(),
            }
        )
    for row in post_onset_best_df.itertuples(index=False):
        comparison_rows.append(
            {
                "analysis_name": "pooled_post_onset_grouped_cv",
                **row._asdict(),
            }
        )
    for row in post_onset_loco_best_df.itertuples(index=False):
        comparison_rows.append(
            {
                "analysis_name": "pooled_post_onset_leave_one_campaign_out",
                **row._asdict(),
            }
        )
    for row in mesh_best_df.itertuples(index=False):
        comparison_rows.append(row._asdict())
    for row in residual_results["comparison"].itertuples(index=False):
        comparison_rows.append(row._asdict())
    final_leaderboard_df = pd.DataFrame(comparison_rows).sort_values(["analysis_name", "mae_mean"]).reset_index(drop=True)
    save_dataframe_csv(final_leaderboard_df, output_root / "comparisons" / "final_leaderboard.csv")

    write_summary_markdown(
        output_path=output_root / "summary" / "ultimate_load_refocus_summary.md",
        refocus_cfg=refocus_cfg,
        grouped_best_df=grouped_best_df,
        grouped_delta_df=grouped_delta_df,
        loco_best_df=loco_best_df,
        mesh_best_df=mesh_best_df,
    )
    write_gap_refinement_markdown(
        output_path=output_root / "summary" / "specimen_gap_refinement_summary.md",
        error_summary_df=error_audit_summary_df,
        residual_comparison_df=residual_results["comparison"],
        specimen_compare_df=residual_results["specimen_comparison"],
    )
    inventory_path = save_output_inventory(output_root)

    return {
        "output_root": str(output_root),
        "inventory_path": str(inventory_path),
        "grouped_comparison_path": str(output_root / "pooled_all_weeks" / "grouped_cv" / "model_comparison.csv"),
        "grouped_feature_set_path": str(output_root / "pooled_all_weeks" / "grouped_cv" / "feature_set_comparison.csv"),
        "summary_path": str(output_root / "summary" / "ultimate_load_refocus_summary.md"),
        "gap_refinement_summary_path": str(output_root / "summary" / "specimen_gap_refinement_summary.md"),
        "best_model_terminal_predictions": str(best_model_dir / "terminal_specimen_oof_predictions.csv"),
        "best_model_all_rows_predictions": str(best_model_dir / "all_rows_oof_predictions.csv"),
        "specimen_manifest_path": str(output_root / "data" / "specimen_manifest.csv"),
        "correlation_summary_path": str(output_root / "correlations" / "mesh_stratified_corrosion_vs_ultimate_load.csv"),
    }

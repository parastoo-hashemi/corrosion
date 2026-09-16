"""Join image descriptors and select historical modelling feature families.

Measured outcomes and observation identifiers are excluded to avoid direct
target or identity leakage. Campaign-linked metadata can still encode design
confounding; excluding identifiers does not establish causal interpretation."""

from __future__ import annotations

import numpy as np
import pandas as pd


MODELING_QC_EXCLUSIONS = {
    # Constant by construction for the current strip geometry.
    "img_strip_count": "constant feature for the current extraction pipeline",
    # This is exactly equal to img_brightness_std in the extracted feature table.
    "img_contrast": "duplicate of img_brightness_std",
    # Heavy-tailed ratio that explodes when center rust intensity is near zero.
    "img_edge_to_center_rust_ratio": "unstable ratio in low-rust images",
}


EXCLUDE_FOR_MODELING = {
    "observation_id",
    "sample_name",
    "specimen_id",
    "image_filename",
    "image_path",
    "image_readable",
    "image_error",
    "image_width",
    "image_height",
    "specimen_id_from_name",
    "calendar_date",
    "date",
    "wire_area_loss_raw",
    "wire_area_loss_frac",
    "wire_area_loss_pct",
    "ultimate_load_kn",
    "surface_total_rust_pct",
    "surface_total_rust_category",
    "peak_rust_pct",
    "peak_rust_category",
    "peak_rust_location_cm",
    "has_structural_label",
    "is_terminal_structural_row",
    "terminal_week",
    "terminal_days",
    *MODELING_QC_EXCLUSIONS.keys(),
}

CAMPAIGN_SENSITIVE_METADATA = {
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
}

TEMPORAL_FEATURES = {"ageing_days", "week"}

HIDDEN_DAMAGE_FEATURE_SETS = {
    "all_cleaned": "All cleaned metadata and image features after QC and collinearity pruning.",
    "image_time_only": "Image features plus ageing_days; excludes campaign/treatment shortcut metadata.",
    "image_only": "Image features only; diagnostic ablation for shortcut dependence.",
    "metadata_only": "Temporal and tabular metadata only; diagnostic ablation for campaign-confounding.",
}


def build_full_feature_table(master_df: pd.DataFrame, image_feature_df: pd.DataFrame) -> pd.DataFrame:
    """Require an observation-key join so image descriptors cannot multiply rows."""
    merged = master_df.merge(
        image_feature_df.drop(columns=["specimen_id", "image_path"], errors="ignore"),
        on="sample_name",
        how="left",
        validate="one_to_one",
    )
    return merged


def build_hidden_damage_feature_table(feature_df: pd.DataFrame) -> pd.DataFrame:
    """Use rows with observed structural supervision, not inferred time-series labels."""
    return feature_df.loc[feature_df["has_structural_label"]].copy().reset_index(drop=True)


def get_model_feature_columns(df: pd.DataFrame, target_col: str) -> list[str]:
    """Exclude outcomes and administrative fields before any model-specific processing."""
    exclude = set(EXCLUDE_FOR_MODELING)
    exclude.add(target_col)
    feature_cols = [
        column
        for column in df.columns
        if column not in exclude and not column.endswith("_raw")
    ]
    return sorted(feature_cols)


def feature_source_family(column: str) -> str:
    if column.startswith("img_hsv_"):
        return "image_hsv"
    if column.startswith("img_gray_hist_bin_"):
        return "image_histogram"
    if column.startswith("img_glcm_") or column.startswith("img_lbp_"):
        return "image_texture"
    if column.startswith("img_rust_blob_"):
        return "image_morphology"
    if column.startswith("img_strip_") or column.startswith("img_rust_center_of_mass"):
        return "image_spatial"
    if column.startswith("img_rust_area") or column.endswith("_mask_ratio_pct"):
        return "image_mask"
    if column.startswith("img_brightness") or column.startswith(("img_r_", "img_g_", "img_b_")):
        return "image_color"
    if column in TEMPORAL_FEATURES:
        return "temporal"
    if column in CAMPAIGN_SENSITIVE_METADATA:
        return "tabular_metadata"
    return "other"


def _series_top_value_fraction(series: pd.Series) -> float:
    if series.empty:
        return float("nan")
    return float(series.value_counts(dropna=False, normalize=True).iloc[0])


def _apply_stage_feature_cleanup(
    df: pd.DataFrame,
    feature_cols: list[str],
    near_constant_threshold: float,
    correlation_threshold: float,
) -> tuple[list[str], pd.DataFrame]:
    selected = list(feature_cols)
    rows = []

    filtered = []
    for feature in selected:
        series = df[feature]
        nunique = int(series.nunique(dropna=True))
        top_fraction = _series_top_value_fraction(series)
        if nunique <= 1:
            rows.append(
                {
                    "feature_name": feature,
                    "action": "exclude",
                    "reason": "constant within hidden-damage subset",
                    "reference_feature": "",
                }
            )
            continue
        if pd.notna(top_fraction) and top_fraction >= near_constant_threshold:
            rows.append(
                {
                    "feature_name": feature,
                    "action": "exclude",
                    "reason": f"near-constant within hidden-damage subset (top_value_fraction>={near_constant_threshold:.2f})",
                    "reference_feature": "",
                }
            )
            continue
        filtered.append(feature)

    selected = filtered
    deduped = []
    for feature in selected:
        duplicate_of = None
        for kept in deduped:
            if df[feature].equals(df[kept]):
                duplicate_of = kept
                break
        if duplicate_of is not None:
            rows.append(
                {
                    "feature_name": feature,
                    "action": "exclude",
                    "reason": "exact duplicate of an earlier selected feature",
                    "reference_feature": duplicate_of,
                }
            )
            continue
        deduped.append(feature)

    selected = deduped
    numeric_selected = [feature for feature in selected if pd.api.types.is_numeric_dtype(df[feature])]
    if len(numeric_selected) >= 2:
        corr = df[numeric_selected].corr(method="spearman").abs()
        dropped = set()
        for idx, left in enumerate(numeric_selected):
            if left in dropped:
                continue
            for right in numeric_selected[idx + 1 :]:
                if right in dropped:
                    continue
                value = corr.loc[left, right]
                if pd.notna(value) and value >= correlation_threshold:
                    dropped.add(right)
                    rows.append(
                        {
                            "feature_name": right,
                            "action": "exclude",
                            "reason": f"high absolute Spearman correlation >= {correlation_threshold:.2f}",
                            "reference_feature": left,
                        }
                    )
        selected = [feature for feature in selected if feature not in dropped]

    for feature in selected:
        rows.append(
            {
                "feature_name": feature,
                "action": "keep",
                "reason": "retained after QC and collinearity cleanup",
                "reference_feature": "",
            }
        )

    inventory_df = pd.DataFrame(rows).sort_values(["feature_name", "action"]).reset_index(drop=True)
    return sorted(selected), inventory_df


def build_hidden_damage_feature_set(
    df: pd.DataFrame,
    target_col: str,
    feature_set_name: str,
    near_constant_threshold: float,
    correlation_threshold: float,
) -> tuple[list[str], pd.DataFrame]:
    if feature_set_name not in HIDDEN_DAMAGE_FEATURE_SETS:
        raise ValueError(f"Unsupported hidden-damage feature set: {feature_set_name}")

    base_feature_cols = get_model_feature_columns(df, target_col)
    if feature_set_name == "all_cleaned":
        candidate_cols = base_feature_cols
    elif feature_set_name == "image_time_only":
        candidate_cols = [
            feature
            for feature in base_feature_cols
            if feature_source_family(feature).startswith("image_") or feature == "ageing_days"
        ]
    elif feature_set_name == "image_only":
        candidate_cols = [
            feature for feature in base_feature_cols if feature_source_family(feature).startswith("image_")
        ]
    elif feature_set_name == "metadata_only":
        candidate_cols = [
            feature
            for feature in base_feature_cols
            if feature_source_family(feature) in {"tabular_metadata", "temporal"}
        ]
    else:
        raise ValueError(f"Unhandled hidden-damage feature set: {feature_set_name}")

    cleaned_cols, cleanup_df = _apply_stage_feature_cleanup(
        df,
        sorted(candidate_cols),
        near_constant_threshold=near_constant_threshold,
        correlation_threshold=correlation_threshold,
    )
    cleanup_df.insert(0, "feature_set_name", feature_set_name)
    cleanup_df.insert(1, "source_family", cleanup_df["feature_name"].map(feature_source_family))
    cleanup_df.insert(2, "candidate_feature", cleanup_df["feature_name"].isin(candidate_cols))
    cleanup_df.insert(3, "set_description", HIDDEN_DAMAGE_FEATURE_SETS[feature_set_name])
    return cleaned_cols, cleanup_df

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from skimage import color, feature, filters, measure, transform

from src.config import Settings
from src.features.image_processing import preprocess_image
from src.logging_utils import get_logger


LOGGER = get_logger(__name__)


def _component_features(mask: np.ndarray) -> dict[str, float]:
    labeled = measure.label(mask)
    props = measure.regionprops(labeled)
    if not props:
        return {
            "rust_component_count": 0.0,
            "rust_component_largest_area_pct": 0.0,
            "rust_component_mean_area_pct": 0.0,
            "rust_component_mean_eccentricity": 0.0,
        }

    areas = np.array([p.area for p in props], dtype=float)
    total = float(mask.size)
    eccentricity = np.array([p.eccentricity for p in props], dtype=float)
    return {
        "rust_component_count": float(len(props)),
        "rust_component_largest_area_pct": float(100.0 * areas.max() / total),
        "rust_component_mean_area_pct": float(100.0 * areas.mean() / total),
        "rust_component_mean_eccentricity": float(eccentricity.mean()),
    }


def _histogram_features(values: np.ndarray, prefix: str, bins: int = 8) -> dict[str, float]:
    hist, _ = np.histogram(values, bins=bins, range=(0.0, 1.0), density=True)
    return {f"{prefix}_bin_{idx:02d}": float(value) for idx, value in enumerate(hist)}


def _texture_features(gray_small: np.ndarray) -> dict[str, float]:
    quantized = np.clip((gray_small * 15).astype(np.uint8), 0, 15)
    glcm = feature.graycomatrix(
        quantized,
        distances=[1, 4, 8],
        angles=[0, np.pi / 4, np.pi / 2],
        levels=16,
        symmetric=True,
        normed=True,
    )
    out: dict[str, float] = {}
    for prop in ("contrast", "dissimilarity", "homogeneity", "energy", "correlation"):
        values = feature.graycoprops(glcm, prop).astype(float)
        out[f"texture_{prop}_mean"] = float(values.mean())
        out[f"texture_{prop}_std"] = float(values.std())

    lbp_input = np.clip(gray_small * 255.0, 0, 255).astype(np.uint8)
    lbp = feature.local_binary_pattern(lbp_input, P=8, R=1, method="uniform")
    hist, _ = np.histogram(lbp, bins=np.arange(0, 11), density=True)
    for idx, value in enumerate(hist):
        out[f"texture_lbp_bin_{idx:02d}"] = float(value)
    return out


def extract_image_features(
    canonical_df: pd.DataFrame,
    settings: Settings,
    output_path: Path | None = None,
) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    n_segments = settings.features.longitudinal_segments

    for idx, row in enumerate(canonical_df.itertuples(index=False), start=1):
        image_path = Path(row.image_path)
        try:
            processed = preprocess_image(image_path=image_path, settings=settings)
        except Exception as exc:
            LOGGER.warning("Feature extraction failed for %s: %s", row.record_id, exc)
            rows.append({"record_id": row.record_id, "feature_extraction_failed": 1.0})
            continue
        roi = processed.normalized_rgb
        rust_mask = processed.rust_mask
        rust_score = processed.rust_score

        hsv = color.rgb2hsv(roi)
        lab = color.rgb2lab(roi)
        gray = color.rgb2gray(roi)
        gray_small = transform.resize(
            gray,
            output_shape=(96, 384),
            anti_aliasing=True,
            preserve_range=True,
        ).astype(np.float32)

        segment_edges = np.linspace(0, rust_mask.shape[1], n_segments + 1, dtype=int)
        segment_ratios = []
        for left, right in zip(segment_edges[:-1], segment_edges[1:]):
            segment = rust_mask[:, left:right]
            ratio = float(segment.mean()) if segment.size else 0.0
            segment_ratios.append(ratio)
        segment_ratios_arr = np.array(segment_ratios, dtype=float)
        peak_segment = int(segment_ratios_arr.argmax())
        peak_location_cm = (
            (peak_segment + 0.5) / n_segments * settings.project.sample_length_cm
        )

        edge_density = float((filters.sobel(gray) > 0.05).mean())
        row_features: dict[str, float | str] = {
            "record_id": row.record_id,
            "feature_extraction_failed": 0.0,
            "image_height_px": float(roi.shape[0]),
            "image_width_px": float(roi.shape[1]),
            "rust_area_pct_feature": float(100.0 * rust_mask.mean()),
            "peak_rust_pct_feature": float(100.0 * segment_ratios_arr.max()),
            "peak_rust_location_cm_feature": float(peak_location_cm),
            "rust_distribution_std": float(segment_ratios_arr.std() * 100.0),
            "rust_distribution_range": float(
                (segment_ratios_arr.max() - segment_ratios_arr.min()) * 100.0
            ),
            "rust_distribution_entropy": float(
                -np.sum(
                    np.where(
                        segment_ratios_arr > 0,
                        segment_ratios_arr * np.log(segment_ratios_arr + 1e-8),
                        0.0,
                    )
                )
            ),
            "rust_score_mean": float(rust_score.mean()),
            "rust_score_std": float(rust_score.std()),
            "rust_segmentation_threshold": float(processed.threshold),
            "edge_density": edge_density,
            "gray_mean": float(gray.mean()),
            "gray_std": float(gray.std()),
            "rgb_r_mean": float(roi[:, :, 0].mean()),
            "rgb_g_mean": float(roi[:, :, 1].mean()),
            "rgb_b_mean": float(roi[:, :, 2].mean()),
            "rgb_r_std": float(roi[:, :, 0].std()),
            "rgb_g_std": float(roi[:, :, 1].std()),
            "rgb_b_std": float(roi[:, :, 2].std()),
            "hsv_h_mean": float(hsv[:, :, 0].mean()),
            "hsv_s_mean": float(hsv[:, :, 1].mean()),
            "hsv_v_mean": float(hsv[:, :, 2].mean()),
            "hsv_s_std": float(hsv[:, :, 1].std()),
            "hsv_v_std": float(hsv[:, :, 2].std()),
            "lab_l_mean": float(lab[:, :, 0].mean()),
            "lab_a_mean": float(lab[:, :, 1].mean()),
            "lab_b_mean": float(lab[:, :, 2].mean()),
            "lab_a_std": float(lab[:, :, 1].std()),
            "lab_b_std": float(lab[:, :, 2].std()),
        }
        row_features.update(_component_features(rust_mask))
        row_features.update(_histogram_features(hsv[:, :, 0], prefix="hist_h", bins=8))
        row_features.update(_histogram_features(hsv[:, :, 1], prefix="hist_s", bins=8))
        row_features.update(_histogram_features(hsv[:, :, 2], prefix="hist_v", bins=8))
        row_features.update(_texture_features(gray_small))
        for seg_idx, value in enumerate(segment_ratios_arr):
            row_features[f"rust_segment_{seg_idx:02d}_pct"] = float(value * 100.0)

        rows.append(row_features)
        if idx % 100 == 0:
            LOGGER.info("Extracted image features for %s/%s records", idx, len(canonical_df))

    feature_df = pd.DataFrame(rows).sort_values("record_id").reset_index(drop=True)
    if "feature_extraction_failed" not in feature_df.columns:
        feature_df["feature_extraction_failed"] = 0.0
    numeric_cols = [
        column for column in feature_df.columns if column != "record_id" and pd.api.types.is_numeric_dtype(feature_df[column])
    ]
    for column in numeric_cols:
        median_value = feature_df[column].median()
        fill_value = 0.0 if pd.isna(median_value) else float(median_value)
        feature_df[column] = feature_df[column].fillna(fill_value)
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        feature_df.to_parquet(output_path, index=False)
    return feature_df

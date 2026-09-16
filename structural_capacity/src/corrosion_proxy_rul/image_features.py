from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import ndimage
from skimage.color import rgb2hsv
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern
from skimage.measure import label, regionprops_table

from .image_preprocessing import load_rgb_image, rgb_to_gray


def feature_dictionary() -> pd.DataFrame:
    rows = [
        ("img_rust_area_ratio_pct", "Percent of pixels in thesis-aligned rust mask."),
        ("img_black_mask_ratio_pct", "Percent of pixels in black-pore mask."),
        ("img_gray_mask_ratio_pct", "Percent of pixels in gray-mark mask."),
        ("img_brightness_mean", "Mean grayscale intensity."),
        ("img_brightness_std", "Standard deviation of grayscale intensity."),
        ("img_brightness_p10", "10th percentile grayscale intensity."),
        ("img_brightness_p90", "90th percentile grayscale intensity."),
        ("img_contrast", "Grayscale standard deviation as simple contrast."),
        ("img_r_mean", "Mean red channel."),
        ("img_g_mean", "Mean green channel."),
        ("img_b_mean", "Mean blue channel."),
        ("img_r_std", "Red-channel standard deviation."),
        ("img_g_std", "Green-channel standard deviation."),
        ("img_b_std", "Blue-channel standard deviation."),
        ("img_hsv_h_mean", "Mean hue value in HSV space."),
        ("img_hsv_s_mean", "Mean saturation value in HSV space."),
        ("img_hsv_v_mean", "Mean value channel in HSV space."),
        ("img_hsv_h_std", "Hue standard deviation in HSV space."),
        ("img_hsv_s_std", "Saturation standard deviation in HSV space."),
        ("img_hsv_v_std", "Value-channel standard deviation in HSV space."),
        ("img_hsv_h_p10", "10th percentile hue value in HSV space."),
        ("img_hsv_s_p10", "10th percentile saturation value in HSV space."),
        ("img_hsv_v_p10", "10th percentile value in HSV space."),
        ("img_hsv_h_p90", "90th percentile hue value in HSV space."),
        ("img_hsv_s_p90", "90th percentile saturation value in HSV space."),
        ("img_hsv_v_p90", "90th percentile value in HSV space."),
        ("img_glcm_contrast", "GLCM contrast on downsampled grayscale image."),
        ("img_glcm_homogeneity", "GLCM homogeneity on downsampled grayscale image."),
        ("img_glcm_energy", "GLCM energy on downsampled grayscale image."),
        ("img_lbp_mean", "Mean local binary pattern value on downsampled grayscale image."),
        ("img_lbp_std", "Standard deviation of local binary pattern values."),
        ("img_rust_blob_count", "Number of connected rust regions."),
        ("img_rust_blob_largest_ratio_pct", "Largest rust region area as image percent."),
        ("img_rust_blob_mean_ratio_pct", "Mean rust region area as image percent."),
        ("img_rust_blob_eccentricity_mean", "Mean eccentricity of rust regions."),
        ("img_rust_blob_eccentricity_max", "Maximum eccentricity of rust regions."),
        ("img_strip_count", "Number of overlapping longitudinal strips."),
        ("img_strip_rust_mean_pct", "Mean strip rust percentage."),
        ("img_strip_rust_std_pct", "Std of strip rust percentage."),
        ("img_strip_rust_max_pct", "Max strip rust percentage."),
        ("img_strip_rust_p90_pct", "90th percentile strip rust percentage."),
        ("img_strip_high_count", "Count of strips above high-rust threshold."),
        ("img_strip_peak_location_cm", "Center location of max-rust strip in cm."),
        ("img_rust_center_of_mass_cm", "Rust-mask center of mass along specimen length in cm."),
        ("img_edge_to_center_rust_ratio", "Edge rust intensity divided by center rust intensity."),
    ]
    for idx in range(8):
        rows.append((f"img_gray_hist_bin_{idx}", f"Normalized grayscale histogram bin {idx}."))
        rows.append((f"img_hsv_h_hist_bin_{idx}", f"Normalized hue histogram bin {idx}."))
        rows.append((f"img_hsv_s_hist_bin_{idx}", f"Normalized saturation histogram bin {idx}."))
        rows.append((f"img_hsv_v_hist_bin_{idx}", f"Normalized value histogram bin {idx}."))
    return pd.DataFrame(rows, columns=["feature_name", "description"])


def _threshold_mask(image_rgb: np.ndarray, lower: list[int], upper: list[int]) -> np.ndarray:
    lower_arr = np.asarray(lower, dtype=np.uint8)
    upper_arr = np.asarray(upper, dtype=np.uint8)
    return np.all(image_rgb >= lower_arr, axis=2) & np.all(image_rgb <= upper_arr, axis=2)


def _compute_masks(image_rgb: np.ndarray, cfg: dict):
    thresholds = cfg["rgb_thresholds"]
    rust = _threshold_mask(image_rgb, thresholds["rust_lower"], thresholds["rust_upper"])
    black = _threshold_mask(image_rgb, thresholds["black_lower"], thresholds["black_upper"])
    gray = _threshold_mask(image_rgb, thresholds["gray_lower"], thresholds["gray_upper"])
    rust_clean = rust & ~black & ~gray
    return rust_clean, black, gray


def _compute_histogram(gray: np.ndarray, bins: int) -> dict:
    hist, _ = np.histogram(gray, bins=bins, range=(0, 256), density=True)
    return {f"img_gray_hist_bin_{idx}": float(value) for idx, value in enumerate(hist)}


def _compute_hsv_features(image_rgb: np.ndarray, bins: int) -> dict:
    hsv = rgb2hsv(image_rgb.astype(np.float32) / 255.0)
    feature_row = {}
    channel_names = ["h", "s", "v"]
    for channel_idx, channel_name in enumerate(channel_names):
        channel = hsv[:, :, channel_idx]
        feature_row[f"img_hsv_{channel_name}_mean"] = float(np.mean(channel))
        feature_row[f"img_hsv_{channel_name}_std"] = float(np.std(channel))
        feature_row[f"img_hsv_{channel_name}_p10"] = float(np.percentile(channel, 10))
        feature_row[f"img_hsv_{channel_name}_p90"] = float(np.percentile(channel, 90))
        hist, _ = np.histogram(channel, bins=bins, range=(0.0, 1.0), density=True)
        for idx, value in enumerate(hist):
            feature_row[f"img_hsv_{channel_name}_hist_bin_{idx}"] = float(value)
    return feature_row


def _compute_texture_features(gray: np.ndarray, cfg: dict) -> dict:
    step = max(1, int(cfg.get("texture_downsample_step", 4)))
    downsample = gray[::step, ::step]
    quantized = np.floor_divide(downsample, 8).astype(np.uint8)
    glcm = graycomatrix(
        quantized,
        distances=cfg.get("glcm_distances", [1, 3]),
        angles=cfg.get("glcm_angles_rad", [0.0]),
        levels=32,
        symmetric=True,
        normed=True,
    )
    lbp = local_binary_pattern(downsample, P=8, R=1.0, method="uniform")
    return {
        "img_glcm_contrast": float(graycoprops(glcm, "contrast").mean()),
        "img_glcm_homogeneity": float(graycoprops(glcm, "homogeneity").mean()),
        "img_glcm_energy": float(graycoprops(glcm, "energy").mean()),
        "img_lbp_mean": float(np.mean(lbp)),
        "img_lbp_std": float(np.std(lbp)),
    }


def _compute_morphology_features(rust_mask: np.ndarray) -> dict:
    labeled = label(rust_mask, connectivity=2)
    count = int(labeled.max())
    if count == 0:
        return {
            "img_rust_blob_count": 0.0,
            "img_rust_blob_largest_ratio_pct": 0.0,
            "img_rust_blob_mean_ratio_pct": 0.0,
            "img_rust_blob_eccentricity_mean": 0.0,
            "img_rust_blob_eccentricity_max": 0.0,
        }
    props = regionprops_table(labeled, properties=("area", "eccentricity"))
    areas = np.asarray(props["area"], dtype=float)
    eccentricity = np.asarray(props["eccentricity"], dtype=float)
    total_pixels = float(rust_mask.size)
    return {
        "img_rust_blob_count": float(count),
        "img_rust_blob_largest_ratio_pct": float(100.0 * areas.max() / total_pixels),
        "img_rust_blob_mean_ratio_pct": float(100.0 * areas.mean() / total_pixels),
        "img_rust_blob_eccentricity_mean": float(np.mean(eccentricity)),
        "img_rust_blob_eccentricity_max": float(np.max(eccentricity)),
    }


def _compute_strip_features(rust_mask: np.ndarray, cfg: dict) -> dict:
    width = rust_mask.shape[1]
    length_cm = float(cfg["physical_length_cm"])
    px_per_cm = width / length_cm
    strip_width_px = max(1, int(round(cfg["strip_width_cm"] * px_per_cm)))
    strip_step_px = max(1, int(round(cfg["strip_step_cm"] * px_per_cm)))
    strip_values = []
    strip_centers = []

    for start in range(0, max(1, width - strip_width_px + 1), strip_step_px):
        window = rust_mask[:, start : start + strip_width_px]
        strip_values.append(float(100.0 * window.mean()))
        center_px = start + strip_width_px / 2.0
        strip_centers.append(float(center_px / px_per_cm))

    strip_array = np.asarray(strip_values, dtype=float)
    center_array = np.asarray(strip_centers, dtype=float)
    if strip_array.size == 0:
        strip_array = np.asarray([0.0])
        center_array = np.asarray([0.0])

    peak_idx = int(np.argmax(strip_array))
    edge_count = max(1, int(round(strip_array.size * 0.25)))
    edge_values = np.concatenate([strip_array[:edge_count], strip_array[-edge_count:]])
    center_values = strip_array[edge_count:-edge_count] if strip_array.size > 2 * edge_count else strip_array

    x_indices = np.arange(rust_mask.shape[1], dtype=float)
    column_intensity = rust_mask.mean(axis=0)
    if column_intensity.sum() > 0:
        com_px = float(ndimage.center_of_mass(column_intensity)[0])
        com_cm = com_px / px_per_cm
    else:
        com_cm = 0.0

    return {
        "img_strip_count": float(strip_array.size),
        "img_strip_rust_mean_pct": float(strip_array.mean()),
        "img_strip_rust_std_pct": float(strip_array.std()),
        "img_strip_rust_max_pct": float(strip_array.max()),
        "img_strip_rust_p90_pct": float(np.percentile(strip_array, 90)),
        "img_strip_high_count": float(np.sum(strip_array >= cfg["high_rust_strip_threshold_pct"])),
        "img_strip_peak_location_cm": float(center_array[peak_idx]),
        "img_rust_center_of_mass_cm": float(com_cm),
        "img_edge_to_center_rust_ratio": float(
            (edge_values.mean() + 1e-6) / (center_values.mean() + 1e-6)
        ),
    }


def extract_features_for_image(image_path: str | Path, features_cfg: dict) -> dict:
    image_rgb = load_rgb_image(image_path)
    gray = rgb_to_gray(image_rgb)
    rust_mask, black_mask, gray_mask = _compute_masks(image_rgb, features_cfg)
    histogram = _compute_histogram(gray, bins=int(features_cfg["histogram_bins"]))

    feature_row = {
        "img_rust_area_ratio_pct": float(100.0 * rust_mask.mean()),
        "img_black_mask_ratio_pct": float(100.0 * black_mask.mean()),
        "img_gray_mask_ratio_pct": float(100.0 * gray_mask.mean()),
        "img_brightness_mean": float(np.mean(gray)),
        "img_brightness_std": float(np.std(gray)),
        "img_brightness_p10": float(np.percentile(gray, 10)),
        "img_brightness_p90": float(np.percentile(gray, 90)),
        "img_contrast": float(np.std(gray)),
        "img_r_mean": float(np.mean(image_rgb[:, :, 0])),
        "img_g_mean": float(np.mean(image_rgb[:, :, 1])),
        "img_b_mean": float(np.mean(image_rgb[:, :, 2])),
        "img_r_std": float(np.std(image_rgb[:, :, 0])),
        "img_g_std": float(np.std(image_rgb[:, :, 1])),
        "img_b_std": float(np.std(image_rgb[:, :, 2])),
    }
    feature_row.update(_compute_hsv_features(image_rgb, bins=int(features_cfg["histogram_bins"])))
    feature_row.update(histogram)
    feature_row.update(_compute_texture_features(gray, features_cfg))
    feature_row.update(_compute_morphology_features(rust_mask))
    feature_row.update(_compute_strip_features(rust_mask, features_cfg))
    return feature_row


def extract_image_feature_table(master_df: pd.DataFrame, features_cfg: dict, logger) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    failures = []
    for idx, row in enumerate(master_df.itertuples(index=False), start=1):
        try:
            features = extract_features_for_image(row.image_path, features_cfg)
            features.update(
                {
                    "sample_name": row.sample_name,
                    "specimen_id": row.specimen_id,
                    "image_path": row.image_path,
                }
            )
            rows.append(features)
        except Exception as exc:  # pragma: no cover - runtime failure logging
            failures.append(
                {
                    "sample_name": row.sample_name,
                    "specimen_id": row.specimen_id,
                    "image_path": row.image_path,
                    "error": str(exc),
                }
            )
        if idx % 100 == 0:
            logger.info("Processed %s / %s images for feature extraction", idx, len(master_df))
    features_df = pd.DataFrame(rows)
    failures_df = pd.DataFrame(
        failures,
        columns=["sample_name", "specimen_id", "image_path", "error"],
    )
    return features_df, failures_df

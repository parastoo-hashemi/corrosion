from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image
from skimage import color, exposure, filters, morphology

from src.config import Settings


@dataclass
class ProcessedImage:
    image_rgb: np.ndarray
    roi_rgb: np.ndarray
    normalized_rgb: np.ndarray
    rust_score: np.ndarray
    rust_mask: np.ndarray
    threshold: float


def load_image_rgb(image_path: Path) -> np.ndarray:
    with Image.open(image_path) as img:
        rgba = img.convert("RGBA")
    background = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    rgb = Image.alpha_composite(background, rgba).convert("RGB")
    return np.asarray(rgb, dtype=np.uint8)


def crop_roi(image_rgb: np.ndarray, settings: Settings) -> np.ndarray:
    height, width = image_rgb.shape[:2]
    x0 = int(width * settings.features.crop_left_ratio)
    x1 = int(width * (1.0 - settings.features.crop_right_ratio))
    y0 = int(height * settings.features.crop_top_ratio)
    y1 = int(height * (1.0 - settings.features.crop_bottom_ratio))
    return image_rgb[y0:y1, x0:x1]


def normalize_illumination(roi_rgb: np.ndarray) -> np.ndarray:
    arr = roi_rgb.astype(np.float32) / 255.0
    balanced = np.empty_like(arr)
    for channel_idx in range(3):
        channel = arr[:, :, channel_idx]
        lo, hi = np.percentile(channel, [2, 98])
        balanced[:, :, channel_idx] = exposure.rescale_intensity(
            channel, in_range=(lo, hi), out_range=(0.0, 1.0)
        )

    hsv = color.rgb2hsv(np.clip(balanced, 0.0, 1.0))
    hsv[:, :, 2] = exposure.equalize_adapthist(
        hsv[:, :, 2], clip_limit=0.02, nbins=256
    )
    return np.clip(color.hsv2rgb(hsv), 0.0, 1.0)


def rust_likelihood(normalized_rgb: np.ndarray) -> np.ndarray:
    hsv = color.rgb2hsv(normalized_rgb)
    lab = color.rgb2lab(normalized_rgb)

    red_dom = np.clip(normalized_rgb[:, :, 0] - normalized_rgb[:, :, 1], 0.0, 1.0)
    warm_dom = np.clip(normalized_rgb[:, :, 0] - normalized_rgb[:, :, 2], 0.0, 1.0)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]

    a_chan = lab[:, :, 1]
    b_chan = lab[:, :, 2]
    a_lo, a_hi = np.percentile(a_chan, [5, 95])
    b_lo, b_hi = np.percentile(b_chan, [5, 95])
    a_norm = exposure.rescale_intensity(a_chan, in_range=(a_lo, a_hi), out_range=(0.0, 1.0))
    b_norm = exposure.rescale_intensity(b_chan, in_range=(b_lo, b_hi), out_range=(0.0, 1.0))

    hue_red = np.exp(-((hue - 0.03) ** 2) / 0.0025)
    hue_brown = np.exp(-((hue - 0.08) ** 2) / 0.0045)
    score = (
        0.24 * red_dom
        + 0.18 * warm_dom
        + 0.18 * a_norm
        + 0.14 * b_norm
        + 0.14 * sat
        + 0.07 * hue_red
        + 0.05 * hue_brown
    )
    score *= (val < 0.99).astype(np.float32)
    return np.clip(score, 0.0, 1.0)


def segment_rust(rust_score: np.ndarray) -> tuple[np.ndarray, float]:
    threshold_otsu = float(filters.threshold_otsu(rust_score))
    threshold_sigma = float(rust_score.mean() + 0.35 * rust_score.std())
    threshold = float(np.clip(max(threshold_otsu, threshold_sigma), 0.22, 0.82))
    mask = rust_score >= threshold

    min_size = max(64, int(mask.size * 0.0004))
    mask = morphology.remove_small_objects(mask, min_size=min_size)
    mask = morphology.remove_small_holes(mask, area_threshold=min_size)
    mask = morphology.binary_opening(mask, morphology.disk(1))
    mask = morphology.binary_closing(mask, morphology.disk(2))
    return mask.astype(bool), threshold


def preprocess_image(image_path: Path, settings: Settings) -> ProcessedImage:
    image_rgb = load_image_rgb(image_path)
    roi_rgb = crop_roi(image_rgb, settings=settings)
    normalized_rgb = normalize_illumination(roi_rgb)
    rust_score = rust_likelihood(normalized_rgb)
    rust_mask, threshold = segment_rust(rust_score)
    return ProcessedImage(
        image_rgb=image_rgb,
        roi_rgb=roi_rgb,
        normalized_rgb=normalized_rgb,
        rust_score=rust_score,
        rust_mask=rust_mask,
        threshold=threshold,
    )

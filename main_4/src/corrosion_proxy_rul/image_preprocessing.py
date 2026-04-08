from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


def load_rgb_image(path: str | Path) -> np.ndarray:
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        return np.asarray(rgb, dtype=np.uint8)


def rgb_to_gray(image_rgb: np.ndarray) -> np.ndarray:
    gray = (
        0.299 * image_rgb[:, :, 0]
        + 0.587 * image_rgb[:, :, 1]
        + 0.114 * image_rgb[:, :, 2]
    )
    return np.clip(gray, 0, 255).astype(np.uint8)

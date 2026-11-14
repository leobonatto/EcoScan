from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageOps
from skimage.color import rgb2gray, rgb2hsv
from skimage.feature import hog


IMAGE_SIZE = (64, 64)
COLOR_BINS = 16


def load_rgb_image(path_or_file) -> np.ndarray:
    """Carrega uma imagem, corrige a orientação e devolve RGB em [0, 1]."""
    with Image.open(path_or_file) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        image = image.resize(IMAGE_SIZE, Image.Resampling.LANCZOS)
        return np.asarray(image, dtype=np.float32) / 255.0


def extract_features_from_array(rgb: np.ndarray) -> np.ndarray:
    """Combina textura HOG e histogramas HSV em um vetor numérico."""
    grayscale = rgb2gray(rgb)
    texture = hog(
        grayscale,
        orientations=9,
        pixels_per_cell=(8, 8),
        cells_per_block=(2, 2),
        block_norm="L2-Hys",
        feature_vector=True,
    )
    hsv = rgb2hsv(rgb)
    color_parts = []
    for channel in range(3):
        hist, _ = np.histogram(
            hsv[:, :, channel], bins=COLOR_BINS, range=(0.0, 1.0), density=True
        )
        color_parts.append(hist.astype(np.float32))
    return np.concatenate([texture.astype(np.float32), *color_parts])


def extract_features(path_or_file) -> np.ndarray:
    return extract_features_from_array(load_rgb_image(path_or_file))


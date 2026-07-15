from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass(slots=True)
class ImageAsset:
    path: Path
    image: np.ndarray
    label: str


@dataclass(slots=True)
class ImageFeatures:
    keypoints: tuple[cv2.KeyPoint, ...]
    descriptors: np.ndarray | None


@dataclass(slots=True)
class Detection:
    reference_label: str
    polygon: np.ndarray
    center: tuple[float, float]
    width: float
    height: float
    good_matches: int
    ransac_inliers: int
    homography: np.ndarray
    reference_shape: tuple[int, int]

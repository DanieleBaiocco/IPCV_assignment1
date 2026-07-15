from __future__ import annotations

import cv2
import numpy as np

from ..models import ImageFeatures


class SiftFeatureExtractor:
    def __init__(self) -> None:
        self._sift = cv2.SIFT_create()

    def extract(self, image: np.ndarray) -> ImageFeatures:
        keypoints, descriptors = self._sift.detectAndCompute(image, None)
        return ImageFeatures(
            keypoints=tuple(keypoints),
            descriptors=descriptors,
        )

from __future__ import annotations

from abc import ABC, abstractmethod

import cv2
import numpy as np


class ScenePreprocessor(ABC):
    @abstractmethod
    def apply(self, image: np.ndarray) -> np.ndarray:
        raise NotImplementedError


class NoOpPreprocessor(ScenePreprocessor):
    def apply(self, image: np.ndarray) -> np.ndarray:
        return image.copy()


class ClahePreprocessor(ScenePreprocessor):
    def __init__(
        self,
        clip_limit: float = 2.0,
        tile_grid_size: tuple[int, int] = (8, 8),
    ) -> None:
        self._clahe = cv2.createCLAHE(
            clipLimit=clip_limit,
            tileGridSize=tile_grid_size,
        )

    def apply(self, image: np.ndarray) -> np.ndarray:
        lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        lightness, channel_a, channel_b = cv2.split(lab_image)
        enhanced_lightness = self._clahe.apply(lightness)
        enhanced_lab = cv2.merge(
            (enhanced_lightness, channel_a, channel_b)
        )
        return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

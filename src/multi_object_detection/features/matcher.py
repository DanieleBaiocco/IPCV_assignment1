from __future__ import annotations

import cv2
import numpy as np


class FlannMatcher:
    def __init__(
        self,
        ratio: float = 0.7,
        trees: int = 15,
        checks: int = 100,
        algorithm: int = 1,
    ) -> None:
        self._ratio = ratio
        self._flann = cv2.FlannBasedMatcher(
            {"algorithm": algorithm, "trees": trees},
            {"checks": checks},
        )

    def match(
        self,
        reference_descriptors: np.ndarray | None,
        scene_descriptors: np.ndarray | None,
    ) -> list[cv2.DMatch]:
        if reference_descriptors is None or scene_descriptors is None:
            return []
        if len(reference_descriptors) < 2 or len(scene_descriptors) < 2:
            return []

        reference_descriptors = np.asarray(
            reference_descriptors,
            dtype=np.float32,
        )
        scene_descriptors = np.asarray(
            scene_descriptors,
            dtype=np.float32,
        )

        try:
            pairs = self._flann.knnMatch(
                reference_descriptors,
                scene_descriptors,
                k=2,
            )
        except cv2.error:
            return []

        good_matches: list[cv2.DMatch] = []
        for pair in pairs:
            if len(pair) < 2:
                continue
            first, second = pair
            if first.distance < self._ratio * second.distance:
                good_matches.append(first)
        return good_matches

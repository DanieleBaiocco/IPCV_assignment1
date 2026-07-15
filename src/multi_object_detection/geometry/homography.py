from __future__ import annotations

from collections.abc import Sequence

import cv2
import numpy as np


class HomographyEstimator:
    def __init__(self, ransac_reprojection_threshold: float = 5.0) -> None:
        self._threshold = ransac_reprojection_threshold

    def estimate(
        self,
        matches: Sequence[cv2.DMatch],
        reference_keypoints: Sequence[cv2.KeyPoint],
        scene_keypoints: Sequence[cv2.KeyPoint],
    ) -> tuple[np.ndarray | None, int]:
        if len(matches) < 4:
            return None, 0

        source_points = np.float32(
            [reference_keypoints[match.queryIdx].pt for match in matches]
        ).reshape(-1, 1, 2)
        destination_points = np.float32(
            [scene_keypoints[match.trainIdx].pt for match in matches]
        ).reshape(-1, 1, 2)

        matrix, mask = cv2.findHomography(
            source_points,
            destination_points,
            cv2.RANSAC,
            self._threshold,
        )

        if (
            matrix is None
            or mask is None
            or np.asarray(matrix).shape != (3, 3)
            or not np.isfinite(matrix).all()
        ):
            return None, 0

        return matrix, int(mask.ravel().sum())

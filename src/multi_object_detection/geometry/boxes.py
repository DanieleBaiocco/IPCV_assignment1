from __future__ import annotations

import cv2
import numpy as np


class BoxGeometry:
    @staticmethod
    def project_reference(
        reference_shape: tuple[int, int],
        homography: np.ndarray,
    ) -> np.ndarray | None:
        height, width = reference_shape
        if (
            homography is None
            or np.asarray(homography).shape != (3, 3)
            or not np.isfinite(homography).all()
        ):
            return None

        corners = np.float32(
            [
                [0, 0],
                [0, height - 1],
                [width - 1, height - 1],
                [width - 1, 0],
            ]
        ).reshape(-1, 1, 2)

        try:
            polygon = cv2.perspectiveTransform(corners, homography)
        except cv2.error:
            return None

        if not np.isfinite(polygon).all():
            return None
        return polygon

    @staticmethod
    def describe(
        polygon: np.ndarray,
    ) -> tuple[tuple[float, float], float, float]:
        points = np.asarray(polygon, dtype=np.float32).reshape(-1, 2)
        x_values = points[:, 0]
        y_values = points[:, 1]
        center = (
            round(float(x_values.mean()), 3),
            round(float(y_values.mean()), 3),
        )
        width = round(float(x_values.max() - x_values.min()), 3)
        height = round(float(y_values.max() - y_values.min()), 3)
        return center, width, height

    @staticmethod
    def iou(first_polygon: np.ndarray, second_polygon: np.ndarray) -> float:
        first = BoxGeometry._axis_aligned(first_polygon)
        second = BoxGeometry._axis_aligned(second_polygon)

        intersection_x_min = max(first[0], second[0])
        intersection_y_min = max(first[1], second[1])
        intersection_x_max = min(first[2], second[2])
        intersection_y_max = min(first[3], second[3])

        intersection_width = max(0.0, intersection_x_max - intersection_x_min)
        intersection_height = max(0.0, intersection_y_max - intersection_y_min)
        intersection = intersection_width * intersection_height

        first_area = max(0.0, first[2] - first[0]) * max(0.0, first[3] - first[1])
        second_area = max(0.0, second[2] - second[0]) * max(0.0, second[3] - second[1])
        union = first_area + second_area - intersection
        return intersection / union if union > 0 else 0.0

    @staticmethod
    def _axis_aligned(polygon: np.ndarray) -> tuple[float, float, float, float]:
        points = np.asarray(polygon, dtype=np.float32).reshape(-1, 2)
        return (
            float(points[:, 0].min()),
            float(points[:, 1].min()),
            float(points[:, 0].max()),
            float(points[:, 1].max()),
        )

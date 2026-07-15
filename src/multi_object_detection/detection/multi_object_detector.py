from __future__ import annotations

from collections.abc import Sequence

import cv2
import numpy as np

from ..models import Detection, ImageAsset
from .single_pass_detector import SinglePassDetector


class MultiObjectDetector:
    """Equivalent to Track B: repeatedly invokes SinglePassDetector."""

    def __init__(
        self,
        single_pass_detector: SinglePassDetector,
        max_iterations: int,
    ) -> None:
        self._single_pass_detector = single_pass_detector
        self._max_iterations = max_iterations

    def prepare_references(self, references: Sequence[ImageAsset]) -> None:
        self._single_pass_detector.prepare_references(references)

    def detect(
        self,
        references: Sequence[ImageAsset],
        scene_image: np.ndarray,
    ) -> list[Detection]:
        working_scene = scene_image.copy()
        all_detections: list[Detection] = []

        for _ in range(self._max_iterations):
            current_detections = self._single_pass_detector.detect(
                references,
                working_scene,
            )
            if not current_detections:
                break

            all_detections.extend(current_detections)
            working_scene = self._mask_detections(
                working_scene,
                current_detections,
            )

        return all_detections

    @staticmethod
    def _mask_detections(
        scene_image: np.ndarray,
        detections: Sequence[Detection],
    ) -> np.ndarray:
        scene_height, scene_width = scene_image.shape[:2]
        masked_scene = scene_image.copy()

        for detection in detections:
            reference_height, reference_width = detection.reference_shape
            white_reference = np.full(
                (reference_height, reference_width, 3),
                255,
                dtype=np.uint8,
            )
            warped = cv2.warpPerspective(
                white_reference,
                detection.homography,
                (scene_width, scene_height),
            )
            outside_object = np.all(warped == 0, axis=2)
            warped[outside_object] = masked_scene[outside_object]
            masked_scene = warped

        return masked_scene

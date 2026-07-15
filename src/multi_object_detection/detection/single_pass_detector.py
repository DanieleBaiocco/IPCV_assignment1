from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from ..features.extractor import SiftFeatureExtractor
from ..features.matcher import FlannMatcher
from ..geometry.boxes import BoxGeometry
from ..geometry.homography import HomographyEstimator
from ..models import Detection, ImageAsset, ImageFeatures


class SinglePassDetector:
    """Equivalent to the original Track A helper."""

    def __init__(
        self,
        extractor: SiftFeatureExtractor,
        matcher: FlannMatcher,
        homography_estimator: HomographyEstimator,
        cutoff: int,
        iou_threshold: float,
    ) -> None:
        self._extractor = extractor
        self._matcher = matcher
        self._homography_estimator = homography_estimator
        self._cutoff = cutoff
        self._iou_threshold = iou_threshold
        self._reference_features: dict[str, ImageFeatures] = {}

    def prepare_references(self, references: Sequence[ImageAsset]) -> None:
        self._reference_features = {
            str(reference.path): self._extractor.extract(reference.image)
            for reference in references
        }

    def detect(
        self,
        references: Sequence[ImageAsset],
        scene_image: np.ndarray,
    ) -> list[Detection]:
        if not self._reference_features:
            self.prepare_references(references)

        scene_features = self._extractor.extract(scene_image)
        candidates: list[Detection] = []

        for reference in references:
            reference_features = self._reference_features[str(reference.path)]
            matches = self._matcher.match(
                reference_features.descriptors,
                scene_features.descriptors,
            )
            if len(matches) < self._cutoff:
                continue

            homography, inliers = self._homography_estimator.estimate(
                matches,
                reference_features.keypoints,
                scene_features.keypoints,
            )
            if homography is None:
                continue

            reference_shape = reference.image.shape[:2]
            polygon = BoxGeometry.project_reference(
                reference_shape,
                homography,
            )
            if polygon is None:
                continue

            center, width, height = BoxGeometry.describe(polygon)
            candidates.append(
                Detection(
                    reference_label=reference.label,
                    polygon=polygon,
                    center=center,
                    width=width,
                    height=height,
                    good_matches=len(matches),
                    ransac_inliers=inliers,
                    homography=homography,
                    reference_shape=reference_shape,
                )
            )

        return self._remove_overlaps(candidates)

    def debug_match_counts(
        self,
        references: Sequence[ImageAsset],
        scene_image: np.ndarray,
    ) -> list[dict[str, object]]:
        if not self._reference_features:
            self.prepare_references(references)

        scene_features = self._extractor.extract(scene_image)
        rows: list[dict[str, object]] = []

        for reference in references:
            reference_features = self._reference_features[str(reference.path)]
            matches = self._matcher.match(
                reference_features.descriptors,
                scene_features.descriptors,
            )
            rows.append(
                {
                    "reference": reference.label,
                    "reference_keypoints": len(reference_features.keypoints),
                    "scene_keypoints": len(scene_features.keypoints),
                    "good_matches": len(matches),
                    "passes_cutoff": len(matches) >= self._cutoff,
                }
            )
        return rows

    def _remove_overlaps(self, detections: Sequence[Detection]) -> list[Detection]:
        ordered = sorted(
            detections,
            key=lambda detection: (
                detection.good_matches,
                detection.ransac_inliers,
            ),
            reverse=True,
        )

        selected: list[Detection] = []
        for candidate in ordered:
            if all(
                BoxGeometry.iou(candidate.polygon, chosen.polygon)
                <= self._iou_threshold
                for chosen in selected
            ):
                selected.append(candidate)
        return selected

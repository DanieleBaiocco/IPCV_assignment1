from __future__ import annotations

from pathlib import Path

from .config import DetectionConfig
from .detection.multi_object_detector import MultiObjectDetector
from .detection.single_pass_detector import SinglePassDetector
from .features.extractor import SiftFeatureExtractor
from .features.matcher import FlannMatcher
from .geometry.homography import HomographyEstimator
from .io.image_loader import ImageLoader
from .output.annotator import SceneAnnotator
from .output.exporter_factory import SceneExporterFactory
from .output.report_writer import CsvReportWriter
from .preprocessing.factory import ScenePreprocessorFactory


class DetectionApplication:
    """Composition root and use-case orchestrator."""

    def __init__(self, config: DetectionConfig) -> None:
        config.validate()
        self._config = config
        self._loader = ImageLoader()
        self._preprocessor = ScenePreprocessorFactory.create(
            config.preprocessing
        )
        self._extractor = SiftFeatureExtractor()
        self._matcher = FlannMatcher(ratio=config.ratio)
        self._homography_estimator = HomographyEstimator(
            config.ransac_threshold
        )
        self._single_pass_detector = SinglePassDetector(
            extractor=self._extractor,
            matcher=self._matcher,
            homography_estimator=self._homography_estimator,
            cutoff=config.cutoff,
            iou_threshold=config.iou_threshold,
        )
        self._detector = MultiObjectDetector(
            single_pass_detector=self._single_pass_detector,
            max_iterations=config.max_iterations,
        )
        self._annotator = SceneAnnotator()
        self._exporter = SceneExporterFactory.create(
            render_mode=config.render_mode,
            figure_dpi=config.figure_dpi,
        )
        self._report_writer = CsvReportWriter()

    def run(self) -> None:
        references = self._load_directory(
            self._config.references_directory,
            "riferimento",
        )
        scenes = self._load_directory(
            self._config.scenes_directory,
            "scena",
        )
        self._config.output_directory.mkdir(parents=True, exist_ok=True)

        print(f"Riferimenti caricati: {len(references)}")
        print(f"Scene caricate: {len(scenes)}")
        print(f"Cutoff: {self._config.cutoff}")
        print(f"Preprocessing scene: {self._config.preprocessing}")
        print(f"Rendering output: {self._config.render_mode}")

        self._detector.prepare_references(references)
        detection_rows: list[dict[str, object]] = []
        debug_rows: list[dict[str, object]] = []

        for index, scene in enumerate(scenes, start=1):
            print(f"[{index}/{len(scenes)}] Elaborazione: {scene.path.name}")

            detection_image = self._preprocessor.apply(scene.image)

            if self._config.debug_matches:
                scene_debug_rows = self._single_pass_detector.debug_match_counts(
                    references,
                    detection_image,
                )
                for row in scene_debug_rows:
                    debug_rows.append({"scene": scene.path.name, **row})

            detections = self._detector.detect(
                references,
                detection_image,
            )
            annotated = self._annotator.annotate(
                scene.image,
                detections,
            )

            output_image_path = (
                self._config.output_directory
                / f"{scene.path.stem}_detected.png"
            )
            self._exporter.export(
                annotated,
                output_image_path,
                title=scene.path.stem,
            )

            detection_rows.extend(
                self._report_writer.detection_rows(
                    scene.path.name,
                    detections,
                )
            )
            print(
                f"    Rilevamenti: {len(detections)} | "
                f"Output: {output_image_path.name}"
            )

        detections_path = self._config.output_directory / "detections.csv"
        self._report_writer.write_detections(
            detections_path,
            detection_rows,
        )

        if self._config.debug_matches:
            debug_path = self._config.output_directory / "match_debug.csv"
            self._report_writer.write_debug_matches(debug_path, debug_rows)

        print("\nElaborazione completata.")
        print(f"Immagini annotate: {self._config.output_directory.resolve()}")
        print(f"Report: {detections_path.resolve()}")

    def _load_directory(self, directory: Path, kind: str):
        paths = self._loader.discover(directory)
        if not paths:
            raise ValueError(
                f"Nessuna immagine di {kind} valida in: {directory}"
            )
        return self._loader.load_many(paths)

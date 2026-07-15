from pathlib import Path

import cv2
import numpy as np

from multi_object_detection.output.exporters import (
    MatplotlibSceneExporter,
    RawImageExporter,
)


def test_raw_exporter_creates_image(tmp_path: Path) -> None:
    image = np.zeros((80, 120, 3), dtype=np.uint8)
    output = tmp_path / "raw.png"

    RawImageExporter().export(image, output)

    loaded = cv2.imread(str(output))
    assert output.exists()
    assert loaded is not None
    assert loaded.shape[:2] == (80, 120)


def test_matplotlib_exporter_creates_larger_figure(tmp_path: Path) -> None:
    image = np.zeros((80, 120, 3), dtype=np.uint8)
    output = tmp_path / "figure.png"

    MatplotlibSceneExporter(dpi=100).export(image, output)

    loaded = cv2.imread(str(output))
    assert output.exists()
    assert loaded is not None

    # La figura include margini e assi, perciò è più grande del raster.
    assert loaded.shape[0] > image.shape[0]
    assert loaded.shape[1] > image.shape[1]

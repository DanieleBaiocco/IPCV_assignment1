from __future__ import annotations

from pathlib import Path
from typing import Iterable

import cv2

from ..models import ImageAsset


class ImageLoader:
    VALID_EXTENSIONS = {
        ".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"
    }

    def discover(self, directory: Path) -> list[Path]:
        if not directory.is_dir():
            raise FileNotFoundError(f"La cartella non esiste: {directory}")

        paths = [
            path
            for path in directory.iterdir()
            if path.is_file() and path.suffix.lower() in self.VALID_EXTENSIONS
        ]
        return sorted(paths, key=lambda path: path.name.lower())

    def load(self, path: Path) -> ImageAsset:
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"OpenCV non riesce a leggere l'immagine: {path}")

        label = path.stem.replace("_", " ")
        return ImageAsset(path=path, image=image, label=label)

    def load_many(self, paths: Iterable[Path]) -> list[ImageAsset]:
        return [self.load(path) for path in paths]

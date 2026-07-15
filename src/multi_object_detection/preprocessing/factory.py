from __future__ import annotations

from .preprocessors import ClahePreprocessor, NoOpPreprocessor, ScenePreprocessor


class ScenePreprocessorFactory:
    @staticmethod
    def create(name: str) -> ScenePreprocessor:
        if name == "none":
            return NoOpPreprocessor()
        if name == "clahe":
            return ClahePreprocessor()
        raise ValueError(f"Preprocessing non supportato: {name}")

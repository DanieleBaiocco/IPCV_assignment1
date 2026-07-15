from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DetectionConfig:
    references_directory: Path
    scenes_directory: Path
    output_directory: Path
    cutoff: int = 40
    preprocessing: str = "none"
    ratio: float = 0.7
    ransac_threshold: float = 5.0
    iou_threshold: float = 0.5
    max_iterations: int = 50
    debug_matches: bool = False
    render_mode: str = "figure"
    figure_dpi: int = 150

    def validate(self) -> None:
        if self.cutoff <= 0:
            raise ValueError("Il cutoff deve essere maggiore di zero.")
        if self.preprocessing not in {"none", "clahe"}:
            raise ValueError(
                "Il preprocessing deve essere 'none' oppure 'clahe'."
            )
        if not 0.0 < self.ratio < 1.0:
            raise ValueError(
                "Il Lowe ratio deve essere compreso tra 0 e 1."
            )
        if self.ransac_threshold <= 0:
            raise ValueError(
                "La soglia RANSAC deve essere maggiore di zero."
            )
        if not 0.0 <= self.iou_threshold <= 1.0:
            raise ValueError(
                "La soglia IoU deve essere compresa tra 0 e 1."
            )
        if self.max_iterations <= 0:
            raise ValueError(
                "max_iterations deve essere maggiore di zero."
            )
        if self.render_mode not in {"figure", "image"}:
            raise ValueError(
                "render_mode deve essere 'figure' oppure 'image'."
            )
        if self.figure_dpi <= 0:
            raise ValueError(
                "figure_dpi deve essere maggiore di zero."
            )

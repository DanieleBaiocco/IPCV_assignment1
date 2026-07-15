from __future__ import annotations

import argparse
import sys
from pathlib import Path
from collections.abc import Sequence

import cv2

from .application import DetectionApplication
from .config import DetectionConfig


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("Il valore deve essere maggiore di zero.")
    return parsed


def positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("Il valore deve essere maggiore di zero.")
    return parsed


def ratio_value(value: str) -> float:
    parsed = float(value)
    if not 0.0 < parsed < 1.0:
        raise argparse.ArgumentTypeError("Il ratio deve essere compreso tra 0 e 1.")
    return parsed


def unit_interval(value: str) -> float:
    parsed = float(value)
    if not 0.0 <= parsed <= 1.0:
        raise argparse.ArgumentTypeError("Il valore deve essere compreso tra 0 e 1.")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Multi-object detection OOP con SIFT/FLANN. "
            "Elabora tutte le scene e salva le immagini annotate."
        )
    )
    parser.add_argument(
        "--references",
        required=True,
        type=Path,
        help="Cartella contenente le immagini di riferimento.",
    )
    parser.add_argument(
        "--scenes",
        required=True,
        type=Path,
        help="Cartella contenente le immagini di scena.",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Cartella in cui salvare immagini annotate e CSV.",
    )
    parser.add_argument(
        "--cutoff",
        type=positive_int,
        default=40,
        help="Numero minimo di good match SIFT richiesto (default: 40).",
    )
    parser.add_argument(
        "--preprocess",
        choices=("none", "clahe"),
        default="none",
        help="Preprocessing delle sole scene (default: none).",
    )
    parser.add_argument(
        "--ratio",
        type=ratio_value,
        default=0.7,
        help="Soglia del Lowe ratio test (default: 0.7).",
    )
    parser.add_argument(
        "--ransac-threshold",
        type=positive_float,
        default=5.0,
        help="Soglia di riproiezione RANSAC (default: 5.0).",
    )
    parser.add_argument(
        "--iou-threshold",
        type=unit_interval,
        default=0.5,
        help="Soglia IoU per eliminare box sovrapposti (default: 0.5).",
    )
    parser.add_argument(
        "--max-iterations",
        type=positive_int,
        default=50,
        help="Numero massimo di passaggi Track B per scena (default: 50).",
    )
    parser.add_argument(
        "--debug-matches",
        action="store_true",
        help="Salva match_debug.csv per ogni coppia riferimento-scena.",
    )
    parser.add_argument(
        "--render-mode",
        choices=("figure", "image"),
        default="figure",
        help=(
            "Formato delle scene annotate: 'figure' salva margini, assi "
            "e coordinate; 'image' salva il solo raster (default: figure)."
        ),
    )
    parser.add_argument(
        "--figure-dpi",
        type=positive_int,
        default=150,
        help="Risoluzione delle figure Matplotlib (default: 150).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = DetectionConfig(
        references_directory=args.references,
        scenes_directory=args.scenes,
        output_directory=args.output,
        cutoff=args.cutoff,
        preprocessing=args.preprocess,
        ratio=args.ratio,
        ransac_threshold=args.ransac_threshold,
        iou_threshold=args.iou_threshold,
        max_iterations=args.max_iterations,
        debug_matches=args.debug_matches,
        render_mode=args.render_mode,
        figure_dpi=args.figure_dpi,
    )

    try:
        DetectionApplication(config).run()
        return 0
    except (FileNotFoundError, ValueError, OSError, cv2.error) as error:
        print(f"Errore: {error}", file=sys.stderr)
        return 1

#!/usr/bin/env python3
"""Direct entry point for the object-oriented package."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIRECTORY = PROJECT_ROOT / "src"
if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SRC_DIRECTORY))

from multi_object_detection.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())

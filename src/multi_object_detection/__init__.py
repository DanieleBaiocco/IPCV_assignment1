"""Object-oriented multi-object detection package."""

from .config import DetectionConfig
from .models import Detection, ImageAsset

__all__ = ["DetectionConfig", "Detection", "ImageAsset"]

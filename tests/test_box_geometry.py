import numpy as np

from multi_object_detection.geometry.boxes import BoxGeometry


def test_iou_identical_boxes_is_one():
    box = np.float32([[[0, 0]], [[0, 10]], [[10, 10]], [[10, 0]]])
    assert BoxGeometry.iou(box, box) == 1.0


def test_describe_box():
    box = np.float32([[[0, 0]], [[0, 10]], [[20, 10]], [[20, 0]]])
    center, width, height = BoxGeometry.describe(box)
    assert center == (10.0, 5.0)
    assert width == 20.0
    assert height == 10.0

import numpy as np
import torch

from azureml.automl.dnn.vision.object_detection_yolo.utils.utils import clip_coords


def _check_boxes(boxes, image_shape, expected_boxes):
    # PyTorch clip_coords()
    boxes_pt = torch.tensor(boxes)
    expected_boxes_pt = torch.tensor(expected_boxes)
    clip_coords(boxes_pt, image_shape)
    assert (boxes_pt == expected_boxes_pt).all()

    # NumPy clip_coords()
    boxes_np = np.array(boxes)
    expected_boxes_np = np.array(expected_boxes)
    clip_coords(boxes_np, image_shape)
    assert (boxes_np == expected_boxes_np).all()


class TestYoloUtils:
    def test_clip_coords_single_box(self):
        boxes = [[230.0, 56.0, 493.4, 187.1]]
        image_shape = (480, 640)
        expected_boxes = [[230.0, 56.0, 493.4, 187.1]]

        _check_boxes(boxes, image_shape, expected_boxes)

    def test_clip_coords_single_box_oob(self):
        boxes = [[530.0, 56.0, 793.4, 187.1]]
        image_shape = (480, 640)
        expected_boxes = [[530.0, 56.0, 640.0, 187.1]]

        _check_boxes(boxes, image_shape, expected_boxes)

    def test_clip_coords_single_box_way_oob(self):
        boxes = [[-12345.0, 5439583.0, -1345.9, 7439583.65321]]
        image_shape = (960, 1280)
        expected_boxes = [[0.0, 960.0, 0.0, 960.0]]

        _check_boxes(boxes, image_shape, expected_boxes)

    def test_clip_coords_multiple_boxes(self):
        boxes = [[230.0, 56.0, 493.4, 187.1], [100.0, 100.0, 200.0, 200.0]]
        image_shape = (480, 640)
        expected_boxes = [[230.0, 56.0, 493.4, 187.1], [100.0, 100.0, 200.0, 200.0]]

        _check_boxes(boxes, image_shape, expected_boxes)

    def test_clip_coords_multiple_boxes_some_oob(self):
        boxes = [
            [-100.0, 200.0, 500.0, 300.0],
            [100.0, 100.0, 200.0, 200.0],
            [600.0, 400.0, 700.0, 500.0],
        ]
        image_shape = (480, 640)
        expected_boxes = [
            [0.0, 200.0, 500.0, 300.0],
            [100.0, 100.0, 200.0, 200.0],
            [600.0, 400.0, 640.0, 480.0],
        ]

        _check_boxes(boxes, image_shape, expected_boxes)

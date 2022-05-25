import numpy as np
import os
import pytest

from pytest import approx

from azureml.automl.dnn.vision.common.constants import MetricsLiterals
from azureml.automl.dnn.vision.object_detection.common import masktools
from azureml.automl.dnn.vision.object_detection.data.datasets import FileObjectDetectionDataset
from azureml.automl.dnn.vision.object_detection.data.dataset_wrappers import \
    CommonObjectDetectionDatasetWrapper, DatasetProcessingType
from azureml.automl.dnn.vision.object_detection.eval.incremental_voc_evaluator import IncrementalVocEvaluator, \
    _calculate_pr_metrics, _match_objects
from azureml.automl.dnn.vision.object_detection.eval.vocmap import VocMap


PRECISION, RECALL = MetricsLiterals.PRECISION, MetricsLiterals.RECALL
AVERAGE_PRECISION, MEAN_AVERAGE_PRECISION = MetricsLiterals.AVERAGE_PRECISION, MetricsLiterals.MEAN_AVERAGE_PRECISION
PER_LABEL_METRICS = MetricsLiterals.PER_LABEL_METRICS


def _check_metrics_keys(metrics):
    assert set(metrics.keys()) == {PER_LABEL_METRICS, MEAN_AVERAGE_PRECISION, PRECISION, RECALL}


def _check_valid_metric_value(metric_value):
    assert (metric_value is None) or ((metric_value >= 0.0) and (metric_value <= 1.0))


def _make_random_objects(width, height, num_classes, num_boxes, is_ground_truth):
    xs = np.random.randint(0, width, size=(num_boxes, 2))
    ys = np.random.randint(0, height, size=(num_boxes, 2))
    boxes = np.concatenate(
        (
            np.amin(xs, axis=1, keepdims=True), np.amin(ys, axis=1, keepdims=True),
            np.amax(xs, axis=1, keepdims=True), np.amax(ys, axis=1, keepdims=True),
        ),
        axis=1
    )

    classes = np.random.randint(num_classes, size=(len(boxes),))
    if is_ground_truth:
        return {"boxes": boxes, "masks": None, "classes": classes, "scores": None}

    scores = np.random.uniform(size=(len(boxes),))
    return {"boxes": boxes, "masks": None, "classes": classes, "scores": scores}


def xyxy2xywh(box):
    return [
        float(box[0]), float(box[1]), float(box[2]) - float(box[0]), float(box[3]) - float(box[1])
    ]


class TestIncrementalVocEvaluator:
    @staticmethod
    def _setup_vocmap_object(iou_threshold=0.5):
        # Note: this duplicates the functionality in object_detection_test\test_vocmap.py. Since we are planning to
        # delete the VocMap class and its tests in the very near future, duplication is ok.
        data_root = "object_detection_data"
        image_root = os.path.join(data_root, "images")
        annotation_file = os.path.join(data_root, "missing_image_annotations.json")
        dataset = FileObjectDetectionDataset(annotations_file=annotation_file,
                                             image_folder=image_root,
                                             ignore_data_errors=True)
        dataset_wrapper = CommonObjectDetectionDatasetWrapper(dataset, DatasetProcessingType.IMAGES)
        return VocMap(dataset_wrapper, iou_threshold)

    @staticmethod
    def _rle_mask_from_bbox(bbox, height, width):
        # Note: this duplicates the functionality in object_detection_test\test_vocmap.py. Since we are planning to
        # delete the VocMap class and its tests in the very near future, duplication is ok.
        x1, y1, x2, y2 = bbox
        polygon = [[x1, y1, x2, y1, x2, y2, x1, y2, x1, y1]]
        rle_masks = masktools.convert_polygon_to_rle_masks(polygon, height, width)
        return rle_masks[0]

    @staticmethod
    def _create_annotation(image_id, bbox, label, iscrowd):
        # Note: this duplicates the functionality in object_detection_test\test_vocmap.py. Since we are planning to
        # delete the VocMap class and its tests in the very near future, duplication is ok.
        result = {
            "image_id": image_id, "bbox": xyxy2xywh(bbox), "category_id": label, "iscrowd": iscrowd
        }
        return result

    @staticmethod
    def _create_prediction(image_id, bbox, label, score):
        # Note: this duplicates the functionality in object_detection_test\test_vocmap.py. Since we are planning to
        # delete the VocMap class and its tests in the very near future, duplication is ok.
        result = {
            "image_id": image_id, "bbox": xyxy2xywh(bbox), "category_id": label, "score": score
        }
        return result

    def test_match_boxes(self):
        gt_boxes = np.array([
            xyxy2xywh([20, 20, 80, 80])
        ])
        is_crowd = np.array([False, False])

        predicted_boxes = np.array([
            xyxy2xywh([25, 25, 75, 75]),
            xyxy2xywh([90, 90, 110, 110])
        ])
        predicted_scores = np.array([1.0, 1.0])

        tp_fp_labels = _match_objects(gt_boxes, is_crowd, predicted_boxes, predicted_scores, 0.5)

        assert (tp_fp_labels == np.array([1, 0])).all()

    def test_match_masks(self):
        width, height = 480, 640

        gt_masks = [self._rle_mask_from_bbox([20, 20, 80, 80], width, height)]
        is_crowd = np.array([False, False])

        predicted_masks = [
            self._rle_mask_from_bbox([25, 25, 75, 75], width, height),
            self._rle_mask_from_bbox([90, 90, 110, 110], width, height)
        ]
        predicted_scores = np.array([1.0, 1.0])

        tp_fp_labels = _match_objects(gt_masks, is_crowd, predicted_masks, predicted_scores, 0.5)

        assert (tp_fp_labels == np.array([1, 0])).all()

    def test_calculate_pr_metrics_no_gt_no_pred(self):
        num_gt_boxes = 0
        tp_fp_labels = np.array([])
        scores = np.array([])

        metrics = _calculate_pr_metrics(num_gt_boxes, tp_fp_labels, scores, False, -1.0)
        assert metrics[AVERAGE_PRECISION] == -1.0
        assert metrics[PRECISION] == -1.0
        assert metrics[RECALL] == -1.0

    def test_calculate_pr_metrics_two_gt_two_pred(self):
        num_gt_boxes = 2
        tp_fp_labels = np.array([1, 1])
        scores = np.array([0.3, 0.9])

        metrics = _calculate_pr_metrics(num_gt_boxes, tp_fp_labels, scores, False, -1.0)
        assert metrics[AVERAGE_PRECISION] == approx(1.0)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(1.0)

    def test_calculate_pr_metrics_four_gt_one_pred_other(self):
        num_gt_boxes = 4
        tp_fp_labels = np.array([0, 1, 1, 2])
        scores = np.array([0.4, 0.2, 0.8, 0.6])

        metrics = _calculate_pr_metrics(num_gt_boxes, tp_fp_labels, scores, False, -1.0)
        assert metrics[AVERAGE_PRECISION] == approx(0.25 * 1.0 + 0.25 * (2.0 / 3.0))
        assert metrics[PRECISION] == approx(2.0 / 3.0)
        assert metrics[RECALL] == approx(0.5)

    def test_calculate_pr_metrics_two_gt_two_pred_other(self):
        num_gt_boxes = 2
        tp_fp_labels = np.array([2, 2])
        scores = np.array([0.25, 0.75])

        metrics = _calculate_pr_metrics(num_gt_boxes, tp_fp_labels, scores, False, -1.0)
        assert metrics[AVERAGE_PRECISION] == approx(0.0)
        assert metrics[PRECISION] == approx(0.0)
        assert metrics[RECALL] == approx(0.0)

    def test_calculate_pr_metrics_11_point(self):
        num_gt_boxes = 3

        tp_fp_labels = np.array([1, 0, 1, 0, 1])
        scores = np.array([0.1, 0.2, 0.3, 0.4, 0.5])

        tp_fp_labels, scores = np.array(tp_fp_labels), np.array(scores)

        metrics = _calculate_pr_metrics(num_gt_boxes, tp_fp_labels, scores, True, -1.0)
        assert metrics[AVERAGE_PRECISION] == approx((4 * 1.0 + 3 * (2.0 / 3.0) + 4 * 0.6) / 11.0)
        assert metrics[PRECISION] == approx(0.6)
        assert metrics[RECALL] == approx(1.0)

    def test_single_image_no_gt_no_pred(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([], dtype=bool)}]
        gt_objects_per_image = [
            {"boxes": np.zeros((0, 4)), "masks": None, "classes": np.zeros((0,)), "scores": None}
        ]
        predicted_objects_per_image = [
            {"boxes": np.zeros((0, 4)), "masks": None, "classes": np.zeros((0,)), "scores": np.zeros((0,))}
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            1: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            2: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(0.0)
        assert metrics[PRECISION] == approx(0.0)
        assert metrics[RECALL] == approx(0.0)

    def test_single_image_no_gt_one_pred(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([], dtype=bool)}]
        gt_objects_per_image = [
            {"boxes": np.zeros((0, 4)), "masks": None, "classes": np.zeros((0,)), "scores": None}
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": np.array([0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            1: {AVERAGE_PRECISION: -1.0, PRECISION: 0.0, RECALL: -1.0},
            2: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(0.0)
        assert metrics[PRECISION] == approx(0.0)
        assert metrics[RECALL] == approx(0.0)

    def test_single_image_one_gt_no_pred1(self):
        # no predictions specified with empty prediction objects dictionary

        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [{}]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            1: {AVERAGE_PRECISION: approx(0.0), PRECISION: -1.0, RECALL: approx(0.0)},
            2: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(0.0)
        assert metrics[PRECISION] == approx(0.0)
        assert metrics[RECALL] == approx(0.0)

    def test_single_image_one_gt_no_pred2(self):
        # no predictions specified with prediction objects with empty boxes

        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.zeros((0, 4)), "masks": None,
                "classes": np.zeros((0,)), "scores": np.zeros((0,))
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            1: {AVERAGE_PRECISION: approx(0.0), PRECISION: -1.0, RECALL: approx(0.0)},
            2: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(0.0)
        assert metrics[PRECISION] == approx(0.0)
        assert metrics[RECALL] == approx(0.0)

    def test_single_image_one_gt_one_pred_perfect_overlap(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": np.array([0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            1: {AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0)},
            2: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(1.0)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(1.0)

    def test_single_image_one_gt_one_pred_crowd(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([True])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": np.array([0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            1: {AVERAGE_PRECISION: -1.0, PRECISION: 0.0, RECALL: -1.0},
            2: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(0.0)
        assert metrics[PRECISION] == approx(0.0)
        assert metrics[RECALL] == approx(0.0)

    def test_single_image_one_gt_one_pred_different_class(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([2]), "scores": np.array([1.0])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            1: {AVERAGE_PRECISION: 0.0, PRECISION: -1.0, RECALL: 0.0},
            2: {AVERAGE_PRECISION: -1.0, PRECISION: 0.0, RECALL: -1.0},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(0.0)
        assert metrics[PRECISION] == approx(0.0)
        assert metrics[RECALL] == approx(0.0)

    def test_single_image_one_gt_one_pred_insufficient_overlap(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 240, 180]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": np.array([0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            1: {AVERAGE_PRECISION: 0.0, PRECISION: 0.0, RECALL: 0.0},
            2: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(0.0)
        assert metrics[PRECISION] == approx(0.0)
        assert metrics[RECALL] == approx(0.0)

    def test_single_image_one_gt_one_pred_sufficient_overlap(self):
        # Like insufficient above, but with lower IOU threshold that makes the overlap sufficient.
        ive = IncrementalVocEvaluator(True, 3, 0.25)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 240, 180]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": np.array([0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            1: {AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0)},
            2: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(1.0)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(1.0)

    def test_single_image_one_gt_one_pred_masks_small_overlap(self):
        ive = IncrementalVocEvaluator(False, 3, 0.1)

        # Two polygons roughly along the diagonals of a square.
        p1 = [0, 0, 35, 0, 200, 165, 200, 200, 165, 200, 0, 35, 0, 0]
        p2 = [200, 0, 165, 0, 0, 165, 0, 200, 35, 200, 200, 35, 200, 0]
        m1 = masktools.convert_polygon_to_rle_masks([p1], 480, 640)[0]
        m2 = masktools.convert_polygon_to_rle_masks([p2], 480, 640)[0]

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": None, "masks": [m1], "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": None, "masks": [m2], "classes": np.array([1]), "scores": np.array([0.5])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            1: {AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0)},
            2: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(1.0)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(1.0)

    def test_single_image_one_gt_one_pred_masks_zero_overlap(self):
        ive = IncrementalVocEvaluator(False, 3, 0.1)

        # Two completely disjoint polygons, each consisting of two squares placed on a diagonal.
        # p1 p2
        # p2 p1
        p1 = [
            100, 100, 200, 100, 200, 200, 100, 200,
            100, 100, 100, 0, 0, 0, 0, 100, 100, 100
        ]
        p2 = [
            100, 100, 200, 100, 200, 0, 100, 0,
            100, 100, 100, 200, 0, 200, 0, 100, 100, 100
        ]
        m1 = masktools.convert_polygon_to_rle_masks([p1], 480, 640)[0]
        m2 = masktools.convert_polygon_to_rle_masks([p2], 480, 640)[0]

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": None, "masks": [m1], "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": None, "masks": [m2], "classes": np.array([1]), "scores": np.array([0.5])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            1: {AVERAGE_PRECISION: 0.0, PRECISION: 0.0, RECALL: 0.0},
            2: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(0.0)
        assert metrics[PRECISION] == approx(0.0)
        assert metrics[RECALL] == approx(0.0)

    def test_single_image_one_gt_one_pred_not_clipped(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 300, "height": 300, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[200, 200, 300, 300]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[200, 200, 400, 400]]), "masks": None,
                "classes": np.array([1]), "scores": np.array([0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            1: {AVERAGE_PRECISION: 0.0, PRECISION: 0.0, RECALL: 0.0},
            2: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(0.0)
        assert metrics[PRECISION] == approx(0.0)
        assert metrics[RECALL] == approx(0.0)

    def test_single_image_one_gt_one_pred_degenerate(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[1, 1, 2, 2]]), "masks": None,
                "classes": np.array([2]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[0, 0, 0, 0]]), "masks": None,
                "classes": np.array([2]), "scores": np.array([0.5])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            1: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            2: {AVERAGE_PRECISION: 0.0, PRECISION: 0.0, RECALL: 0.0},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(0.0)
        assert metrics[PRECISION] == approx(0.0)
        assert metrics[RECALL] == approx(0.0)

    def test_single_image_two_gt_two_pred_good_overlap(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False, False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [160, 120, 320, 240],
                    [320, 240, 480, 360],
                ]),
                "masks": None,
                "classes": np.array([0, 0]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([
                    [160, 120, 300, 220],
                    [320, 240, 460, 340],
                ]),
                "masks": None,
                "classes": np.array([0, 0]),
                "scores": np.array([0.999, 0.888])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0)},
            1: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            2: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(1.0)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(1.0)

    def test_single_image_two_gt_two_pred_good_overlap_different_class(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False, False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [160, 120, 320, 240],
                    [320, 240, 480, 360],
                ]),
                "masks": None,
                "classes": np.array([0, 0]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([
                    [160, 120, 300, 220],
                    [320, 240, 460, 340],
                ]),
                "masks": None,
                "classes": np.array([0, 1]),
                "scores": np.array([0.999, 0.888])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: approx(0.5), PRECISION: approx(1.0), RECALL: approx(0.5)},
            1: {AVERAGE_PRECISION: -1.0, PRECISION: 0.0, RECALL: -1.0},
            2: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(0.5)
        assert metrics[PRECISION] == approx(0.5)
        assert metrics[RECALL] == approx(0.5)

    def test_single_image_two_gt_two_pred_one_match(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False, False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200],
                    [150, 100, 250, 200],
                ]),
                "masks": None,
                "classes": np.array([2, 2]),
                "scores": None
            }
        ]
        pred_objects_per_image = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200],
                    [135, 100, 210, 200],
                ]),
                "masks": None,
                "classes": np.array([2, 2]),
                "scores": np.array([0.75, 0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, pred_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            1: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            2: {AVERAGE_PRECISION: approx(0.5), PRECISION: approx(0.5), RECALL: approx(0.5)},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(0.5)
        assert metrics[PRECISION] == approx(0.5)
        assert metrics[RECALL] == approx(0.5)

    def test_single_image_two_gt_two_pred_one_match_masks(self):
        ive = IncrementalVocEvaluator(False, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False, False])}]
        gt_objects_per_image = [
            {
                "boxes": None,
                "masks": [
                    self._rle_mask_from_bbox([100, 100, 200, 200], 480, 640),
                    self._rle_mask_from_bbox([150, 100, 250, 200], 480, 640),
                ],
                "classes": np.array([2, 2]),
                "scores": None
            }
        ]
        pred_objects_per_image = [
            {
                "boxes": None,
                "masks": [
                    self._rle_mask_from_bbox([100, 100, 200, 200], 480, 640),
                    self._rle_mask_from_bbox([135, 100, 210, 200], 480, 640),
                ],
                "classes": np.array([2, 2]),
                "scores": np.array([0.75, 0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, pred_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            1: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            2: {AVERAGE_PRECISION: approx(0.5), PRECISION: approx(0.5), RECALL: approx(0.5)},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(0.5)
        assert metrics[PRECISION] == approx(0.5)
        assert metrics[RECALL] == approx(0.5)

    def test_single_image_1K_gt_1K_pred_random(self):
        ive = IncrementalVocEvaluator(True, 10, 0.5)

        meta_info_per_image = [{"width": 1600, "height": 1600, "iscrowd": np.array([False] * 1000)}]

        xs, ys = np.random.randint(0, 1600, size=(1000, 2)), np.random.randint(0, 1600, size=(1000, 2))
        x1, x2 = np.amin(xs, axis=1, keepdims=True), np.amax(xs, axis=1, keepdims=True)
        y1, y2 = np.amin(ys, axis=1, keepdims=True), np.amax(ys, axis=1, keepdims=True)
        boxes = np.concatenate((x1, y1, x2, y2), axis=1)
        classes = np.random.randint(0, 10, size=(1000,))
        gt_objects_per_image = [{"boxes": boxes, "masks": None, "classes": classes, "scores": None}]

        xs, ys = np.random.randint(0, 1600, size=(1000, 2)), np.random.randint(0, 1600, size=(1000, 2))
        x1, x2 = np.amin(xs, axis=1, keepdims=True), np.amax(xs, axis=1, keepdims=True)
        y1, y2 = np.amin(ys, axis=1, keepdims=True), np.amax(ys, axis=1, keepdims=True)
        boxes = np.concatenate((x1, y1, x2, y2), axis=1)
        classes = np.random.randint(0, 10, size=(1000,))
        scores = np.random.uniform(size=(1000,))
        pred_objects_per_image = [{"boxes": boxes, "masks": None, "classes": classes, "scores": scores}]

        ive.evaluate_batch(gt_objects_per_image, pred_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        for i in range(10):
            assert i in metrics[PER_LABEL_METRICS]
            m = metrics[PER_LABEL_METRICS][i]

            _check_valid_metric_value(m[AVERAGE_PRECISION])
            _check_valid_metric_value(m[PRECISION])
            _check_valid_metric_value(m[RECALL])

        _check_valid_metric_value(metrics[MEAN_AVERAGE_PRECISION])
        _check_valid_metric_value(metrics[PRECISION])
        _check_valid_metric_value(metrics[RECALL])

    def test_multi_image_one_gt_one_pred_good_overlap(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [
            {"width": 640, "height": 480, "iscrowd": np.array([False])},
            {"width": 1280, "height": 960, "iscrowd": np.array([False])}
        ]
        gt_objects_per_image = [
            # first image
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([0]), "scores": None
            },
            # second image
            {
                "boxes": np.array([[320, 240, 640, 480]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            # first image
            {
                "boxes": np.array([
                    [160, 120, 300, 220],
                ]),
                "masks": None,
                "classes": np.array([0]),
                "scores": np.array([0.991])
            },
            # second image
            {
                "boxes": np.array([
                    [320, 240, 600, 440],
                ]),
                "masks": None,
                "classes": np.array([1]),
                "scores": np.array([0.995])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0)},
            1: {AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0)},
            2: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(1.0)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(1.0)

    def test_multi_image_one_gt_one_pred_different_class(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [
            {"width": 640, "height": 480, "iscrowd": np.array([False])},
            {"width": 1280, "height": 960, "iscrowd": np.array([False])}
        ]
        gt_objects_per_image = [
            # first image
            {
                "boxes": np.array([
                    [160, 120, 320, 240],
                ]),
                "masks": None,
                "classes": np.array([0]),
                "scores": None
            },
            # second image
            {
                "boxes": np.array([
                    [320, 240, 640, 480],
                ]),
                "masks": None,
                "classes": np.array([1]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            # first image
            {
                "boxes": np.array([
                    [160, 120, 300, 220],
                ]),
                "masks": None,
                "classes": np.array([1]),
                "scores": np.array([0.991])
            },
            # second image
            {
                "boxes": np.array([
                    [320, 240, 600, 440],
                ]),
                "masks": None,
                "classes": np.array([2]),
                "scores": np.array([0.995])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: 0.0, PRECISION: -1.0, RECALL: 0.0},
            1: {AVERAGE_PRECISION: approx(0.0), PRECISION: approx(0.0), RECALL: approx(0.0)},
            2: {AVERAGE_PRECISION: -1.0, PRECISION: 0.0, RECALL: -1.0},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(0.0)
        assert metrics[PRECISION] == approx(0.0)
        assert metrics[RECALL] == approx(0.0)

    def test_multi_image_two_gt_two_pred_perfect_match(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [
            {"width": 400, "height": 500, "iscrowd": np.array([False, False])},
            {"width": 200, "height": 300, "iscrowd": np.array([False, False])}
        ]
        gt_objects_per_image = [
            # first image
            {
                "boxes": np.array([
                    [100, 0, 200, 100],
                    [200, 0, 300, 100],
                ]),
                "masks": None,
                "classes": np.array([0, 1]),
                "scores": None
            },
            # second image
            {
                "boxes": np.array([
                    [10, 0, 20, 10],
                    [20, 0, 30, 10],
                ]),
                "masks": None,
                "classes": np.array([2, 1]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            # first image
            {
                "boxes": np.array([
                    [100, 0, 200, 100],
                    [200, 0, 300, 100],
                ]),
                "masks": None,
                "classes": np.array([0, 1]),
                "scores": np.array([0.8, 0.9])
            },
            # second image
            {
                "boxes": np.array([
                    [20, 0, 30, 10],
                    [10, 0, 20, 10],
                ]),
                "masks": None,
                "classes": np.array([1, 2]),
                "scores": np.array([0.9, 0.7])
            },
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0)},
            1: {AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0)},
            2: {AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0)},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(1.0)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(1.0)

    def test_multi_image_three_gt_three_pred_single_match(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [
            {"width": 640, "height": 640, "iscrowd": np.array([False, False, False])},
            {"width": 6400, "height": 6400, "iscrowd": np.array([False, False, False])},
            {"width": 64000, "height": 64000, "iscrowd": np.array([False, False, False])},
        ]
        gt_objects_per_image = [
            # first image
            {
                "boxes": np.array([
                    [1, 0, 2, 100],
                    [2, 0, 3, 100],
                    [3, 0, 4, 100],
                ]),
                "masks": None,
                "classes": np.array([0, 1, 2]),
                "scores": None
            },
            # second image
            {
                "boxes": np.array([
                    [10, 0, 20, 100],
                    [20, 0, 30, 100],
                    [30, 0, 40, 100],
                ]),
                "masks": None,
                "classes": np.array([0, 1, 2]),
                "scores": None
            },
            # third image
            {
                "boxes": np.array([
                    [100, 0, 200, 100],
                    [200, 0, 300, 100],
                    [300, 0, 400, 100],
                ]),
                "masks": None,
                "classes": np.array([0, 1, 2]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            # first image
            {
                "boxes": np.array([
                    [1, 0, 2, 100],
                ]),
                "masks": None,
                "classes": np.array([0]),
                "scores": np.array([0.5])
            },
            # second image
            {
                "boxes": np.array([
                    [20, 0, 30, 100],
                ]),
                "masks": None,
                "classes": np.array([1]),
                "scores": np.array([0.5])
            },
            # third image
            {
                "boxes": np.array([
                    [300, 0, 400, 100],
                ]),
                "masks": None,
                "classes": np.array([2]),
                "scores": np.array([0.5])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        _13 = 1.0 / 3.0
        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: approx(_13), PRECISION: approx(1.0), RECALL: approx(_13)},
            1: {AVERAGE_PRECISION: approx(_13), PRECISION: approx(1.0), RECALL: approx(_13)},
            2: {AVERAGE_PRECISION: approx(_13), PRECISION: approx(1.0), RECALL: approx(_13)},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(_13)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(_13)

    def test_multi_image_three_gt_three_pred_single_match_masks(self):
        ive = IncrementalVocEvaluator(False, 3, 0.5)

        meta_info_per_image = [
            {"width": 640, "height": 640, "iscrowd": np.array([False, False, False])},
            {"width": 6400, "height": 6400, "iscrowd": np.array([False, False, False])},
            {"width": 64000, "height": 64000, "iscrowd": np.array([False, False, False])},
        ]
        gt_objects_per_image = [
            # first image
            {
                "boxes": None,
                "masks": [
                    self._rle_mask_from_bbox([1, 0, 2, 100], 640, 640),
                    self._rle_mask_from_bbox([2, 0, 3, 100], 640, 640),
                    self._rle_mask_from_bbox([3, 0, 4, 100], 640, 640),
                ],
                "classes": np.array([0, 1, 2]),
                "scores": None
            },
            # second image
            {
                "boxes": None,
                "masks": [
                    self._rle_mask_from_bbox([10, 0, 20, 100], 6400, 6400),
                    self._rle_mask_from_bbox([20, 0, 30, 100], 6400, 6400),
                    self._rle_mask_from_bbox([30, 0, 40, 100], 6400, 6400),
                ],
                "classes": np.array([0, 1, 2]),
                "scores": None
            },
            # third image
            {
                "boxes": None,
                "masks": [
                    self._rle_mask_from_bbox([100, 0, 200, 100], 64000, 64000),
                    self._rle_mask_from_bbox([200, 0, 300, 100], 64000, 64000),
                    self._rle_mask_from_bbox([300, 0, 400, 100], 64000, 64000),
                ],
                "classes": np.array([0, 1, 2]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            # first image
            {
                "boxes": None,
                "masks": [
                    self._rle_mask_from_bbox([1, 0, 2, 100], 640, 640),
                ],
                "classes": np.array([0]),
                "scores": np.array([0.5])
            },
            # second image
            {
                "boxes": None,
                "masks": [
                    self._rle_mask_from_bbox([20, 0, 30, 100], 6400, 6400),
                ],
                "classes": np.array([1]),
                "scores": np.array([0.5])
            },
            # third image
            {
                "boxes": None,
                "masks": [
                    self._rle_mask_from_bbox([300, 0, 400, 100], 64000, 64000),
                ],
                "classes": np.array([2]),
                "scores": np.array([0.5])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        _13 = 1.0 / 3.0
        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: approx(_13), PRECISION: approx(1.0), RECALL: approx(_13)},
            1: {AVERAGE_PRECISION: approx(_13), PRECISION: approx(1.0), RECALL: approx(_13)},
            2: {AVERAGE_PRECISION: approx(_13), PRECISION: approx(1.0), RECALL: approx(_13)},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(_13)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(_13)

    def test_set_from_one_other(self):
        # First and only evaluator.
        ive1 = IncrementalVocEvaluator(True, 3, 0.5)
        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200],
                ]),
                "masks": None,
                "classes": np.array([0]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200]
                ]),
                "masks": None,
                "classes": np.array([0]),
                "scores": np.array([0.5])
            }
        ]
        ive1.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        # Combined evaluator.
        ive = IncrementalVocEvaluator(True, 3, 0.5)
        ive.set_from_others([ive1])
        metrics = ive.compute_metrics()

        # Check combined evaluator.
        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0)},
            1: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
            2: {AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0},
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(1.0)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(1.0)

    def test_set_from_two_others(self):
        # First evaluator.
        ive1 = IncrementalVocEvaluator(True, 3, 0.5)
        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200],
                ]),
                "masks": None,
                "classes": np.array([0]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200]
                ]),
                "masks": None,
                "classes": np.array([0]),
                "scores": np.array([0.5])
            }
        ]
        ive1.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        # Second evaluator. Note that the labels and predictions refer to different images in different evaluators.
        ive2 = IncrementalVocEvaluator(True, 3, 0.5)
        meta_info_per_image = [{"width": 512, "height": 384, "iscrowd": np.array([False, False, False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200],
                    [300, 300, 400, 400],
                    [400, 400, 450, 450],
                ]),
                "masks": None,
                "classes": np.array([0, 1, 2]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200],
                    [300, 300, 320, 320],
                    [300, 300, 380, 380],
                    [400, 400, 425, 425],
                ]),
                "masks": None,
                "classes": np.array([0, 1, 1, 2]),
                "scores": np.array([0.5, 0.25, 0.75, 1.0])
            }
        ]
        ive2.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        # Combined evaluator.
        ive = IncrementalVocEvaluator(True, 3, 0.5)
        ive.set_from_others([ive1, ive2])
        metrics = ive.compute_metrics()

        # Check combined evaluator.
        _check_metrics_keys(metrics)

        assert metrics[PER_LABEL_METRICS] == {
            0: {AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0)},
            1: {AVERAGE_PRECISION: approx(1.0), PRECISION: approx(0.5), RECALL: approx(1.0)},
            2: {AVERAGE_PRECISION: approx(0.0), PRECISION: approx(0.0), RECALL: approx(0.0)},
        }

        _23 = 2.0 / 3.0
        assert metrics[MEAN_AVERAGE_PRECISION] == approx(_23)
        assert metrics[PRECISION] == approx(0.5)
        assert metrics[RECALL] == approx(_23)

    @pytest.mark.usefixtures("new_clean_dir")
    @pytest.mark.parametrize("iou_threshold", [0.5, 0.2])
    def test_compare_random_against_vocmap(self, iou_threshold):
        # Set the number of images etc.
        num_images, num_boxes_per_image = 1000, 250
        num_classes = 10
        width, height = 900, 600
        eps = 1e-4

        # Make the incremental VOC evaluator object.
        ive = IncrementalVocEvaluator(True, num_classes, iou_threshold)

        # Make the original VOC evaluator object.
        vocmap = self._setup_vocmap_object(iou_threshold)

        # Hack image id and class related information into the original VOC evaluator object.
        image_ids = ["im{}".format(i) for i in range(num_images)]
        class_strs = ["c{}".format(c) for c in range(num_classes)]
        vocmap._image_id_to_index_map = {image_id: i for i, image_id in enumerate(image_ids)}
        vocmap._labels = class_strs
        vocmap._dataset_wrapper.dataset._class_to_index_map = {
            class_str: c for c, class_str in enumerate(class_strs)
        }

        # Make random ground truth objects (boxes, labels) and predicted objects (boxes, labels, scores).
        gt_objects_per_image, predicted_objects_per_image = [], []
        for i in range(num_images):
            gt_objects = _make_random_objects(
                width, height, num_classes, num_boxes_per_image, is_ground_truth=True
            )
            predicted_objects = _make_random_objects(
                width, height, num_classes, num_boxes_per_image, is_ground_truth=False
            )
            gt_objects_per_image.append(gt_objects)
            predicted_objects_per_image.append(predicted_objects)

        # Compute metrics with incremental VOC evaluator.
        # a. make meta info per image
        meta_info_per_image = [
            {"width": width, "height": height, "iscrowd": np.array([False] * num_boxes_per_image)}
        ] * num_images
        # run calculations
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)
        metrics = ive.compute_metrics()

        # Compute metrics with original VOC evaluator.
        # a. set the gt labels
        for class_index, class_str in enumerate(class_strs):
            vocmap._label_gts[class_str] = [
                self._create_annotation(image_ids[i], box, class_strs[class_], False)
                for i in range(num_images)
                for box, class_ in zip(gt_objects_per_image[i]["boxes"], gt_objects_per_image[i]["classes"])
                if class_ == class_index
            ]
        # b. make the predictions
        vocmap_predictions = [
            self._create_prediction(image_ids[i], box, class_strs[class_], score)
            for i in range(num_images)
            for box, class_, score in zip(
                predicted_objects_per_image[i]["boxes"],
                predicted_objects_per_image[i]["classes"],
                predicted_objects_per_image[i]["scores"]
            )
        ]
        # c. run calculations
        vocmap_metrics = vocmap.compute(vocmap_predictions, "bbox")

        # Check global metrics.
        assert approx(metrics[MEAN_AVERAGE_PRECISION], abs=eps) == approx(
            vocmap_metrics[MEAN_AVERAGE_PRECISION], abs=eps
        )
        assert approx(metrics[PRECISION], abs=eps) == approx(vocmap_metrics[PRECISION], abs=eps)
        assert approx(metrics[RECALL], abs=eps) == approx(vocmap_metrics[RECALL], abs=eps)

        # Check per-class metrics.
        for c in range(num_classes):
            m = metrics[PER_LABEL_METRICS][c]
            vm = vocmap_metrics[PER_LABEL_METRICS][c]
            assert approx(m[AVERAGE_PRECISION], abs=eps) == approx(vm[AVERAGE_PRECISION].item(), abs=eps)
            assert approx(m[PRECISION], abs=eps) == approx(vm[PRECISION].item(), abs=eps)
            assert approx(m[RECALL], abs=eps) == approx(vm[RECALL].item(), abs=eps)

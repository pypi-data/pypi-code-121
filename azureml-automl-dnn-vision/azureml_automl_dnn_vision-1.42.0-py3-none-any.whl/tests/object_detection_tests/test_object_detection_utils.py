import numpy as np
import os
import pytest
import tempfile
import torch
import unittest.mock as mock

import azureml.automl.dnn.vision.object_detection.common.object_detection_utils as od_utils

from azureml.automl.dnn.vision.common import utils
from azureml.automl.dnn.vision.common.constants import MetricsLiterals
from azureml.automl.dnn.vision.object_detection.common.constants import ValidationMetricType
from azureml.automl.dnn.vision.object_detection.data.datasets import AmlDatasetObjectDetection
from azureml.automl.dnn.vision.object_detection.data.dataset_wrappers import \
    CommonObjectDetectionDatasetWrapper, DatasetProcessingType
from azureml.automl.dnn.vision.object_detection.eval.vocmap import VocMap
from azureml.automl.dnn.vision.object_detection.eval.incremental_voc_evaluator import IncrementalVocEvaluator

from ..common.run_mock import DatasetMock, RunMock, ExperimentMock, DatastoreMock, WorkspaceMock
from .aml_dataset_mock import AmlDatasetMock
from .test_datasets import _build_aml_dataset_object_detection


def _convert_numbers_to_tensors(m):
    return {
        k: torch.tensor(v) if isinstance(v, float)
        else [torch.tensor(x) for x in v] if isinstance(v, list)
        else _convert_numbers_to_tensors(v)
        for k, v in m.items()
    }


@pytest.mark.usefixtures('new_clean_dir')
class TestObjectDetectionUtils:

    @staticmethod
    def _setup_wrapper(only_one_file=False):
        ws_mock, mock_dataset, _, _ = _build_aml_dataset_object_detection(only_one_file)
        AmlDatasetObjectDetection.download_image_files(mock_dataset)
        dataset_mock = AmlDatasetObjectDetection(mock_dataset)
        wrapper_mock = CommonObjectDetectionDatasetWrapper(dataset_mock, DatasetProcessingType.IMAGES)
        return ws_mock, mock_dataset, wrapper_mock

    @staticmethod
    def _write_output_file(output_file, only_one_file=False):
        with open(output_file, 'w') as f:
            line1 = '{"filename": "a7c014ec-474a-49f4-8ae3-09049c701913-1.txt", ' \
                    '"boxes": [{"box": {"topX": 0.1, "topY": 0.9, "bottomX": 0.2, "bottomY": 0.8}, ' \
                    '"label": "cat", "score": 0.7}]}'
            line2 = '{"filename": "a7c014ec-474a-49f4-8ae3-09049c701913-2", ' \
                    '"boxes": [{"box": {"topX": 0.5, "topY": 0.5, "bottomX": 0.6, "bottomY": 0.4}, '\
                    '"label": "dog", "score": 0.8}]}'
            f.write(line1 + '\n')
            f.write(line2 + '\n')

    @pytest.mark.parametrize("data_type", ["numbers", "tensors"])
    def test_update_with_voc_metrics_simple(self, data_type):
        current_metrics = {}
        cumulative_per_label_metrics = {}

        voc_metrics = {
            "precision": 0.35, "recall": 0.65, "mean_average_precision": 0.5,
            "per_label_metrics": {
                0: {"precision": 0.3, "recall": 0.7, "average_precision": 0.25},
                1: {"precision": 0.4, "recall": 0.6, "average_precision": 0.75},
            }
        }
        if data_type == "tensors":
            voc_metrics = _convert_numbers_to_tensors(voc_metrics)

        od_utils._update_with_voc_metrics(current_metrics, cumulative_per_label_metrics, voc_metrics)

        assert current_metrics == {
            "precision": 0.35, "recall": 0.65,
            "per_label_metrics": {
                0: {"precision": 0.3, "recall": 0.7, "average_precision": 0.25},
                1: {"precision": 0.4, "recall": 0.6, "average_precision": 0.75},
            }
        }

        assert cumulative_per_label_metrics == {
            0: {"precision": [0.3], "recall": [0.7], "average_precision": [0.25]},
            1: {"precision": [0.4], "recall": [0.6], "average_precision": [0.75]},
        }

    @pytest.mark.parametrize("data_type", ["numbers", "tensors"])
    def test_update_with_voc_metrics_complex(self, data_type):
        current_metrics = {}
        cumulative_per_label_metrics = {
            0: {"precision": [0.3], "recall": [0.7], "average_precision": [0.25]},
            1: {"precision": [0.4], "recall": [0.6], "average_precision": [0.75]},
        }
        if data_type == "tensors":
            cumulative_per_label_metrics = _convert_numbers_to_tensors(cumulative_per_label_metrics)

        voc_metrics = {
            "precision": 0.4287317322877335, "recall": 0.3727672265, "mean_average_precision": 0.609,
            "per_label_metrics": {
                1: {"precision": 0.12321, "recall": 0.456, "average_precision": 0.55},
                2: {"precision": 0.734253464575467, "recall": 0.289534453, "average_precision": 0.668},
            }
        }
        if data_type == "tensors":
            voc_metrics = _convert_numbers_to_tensors(voc_metrics)

        od_utils._update_with_voc_metrics(current_metrics, cumulative_per_label_metrics, voc_metrics)

        assert current_metrics == {
            "precision": 0.42873, "recall": 0.37277,
            "per_label_metrics": {
                1: {"precision": 0.12321, "recall": 0.456, "average_precision": 0.55},
                2: {"precision": 0.73425, "recall": 0.28953, "average_precision": 0.668},
            }
        }

        assert cumulative_per_label_metrics == {
            0: {"precision": [0.3], "recall": [0.7], "average_precision": [0.25]},
            1: {"precision": [0.4, 0.12321], "recall": [0.6, 0.456], "average_precision": [0.75, 0.55]},
            2: {"precision": [0.73425], "recall": [0.28953], "average_precision": [0.668]},
        }

    @mock.patch(od_utils.__name__ + '.CommonObjectDetectionDatasetWrapper')
    @mock.patch(od_utils.__name__ + '.AmlDatasetObjectDetection')
    @mock.patch(od_utils.__name__ + '.VocMap')
    @mock.patch(od_utils.__name__ + '.IncrementalVocEvaluator')
    @mock.patch(od_utils.__name__ + '._parse_bounding_boxes')
    @mock.patch(od_utils.__name__ + '._evaluate_predictions_incrementally')
    @mock.patch(od_utils.__name__ + '._evaluate_and_log')
    @pytest.mark.parametrize("val_metric_type", [ValidationMetricType.VOC, ValidationMetricType.INCREMENTAL_VOC])
    def test_validate_score_run(
        self, mock_eval, mock_eval_pred_inc, mock_parse, mock_incremental_voc_evaluator, mock_vocmap, mock_dataset,
        mock_wrapper, val_metric_type
    ):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            # Patch functions
            ws_mock, ds_mock, wrapper_mock = self._setup_wrapper()
            vocmap_obj = VocMap(wrapper_mock, 0.5)
            incremental_voc_evaluator_obj = IncrementalVocEvaluator(True, len(wrapper_mock.dataset.classes), 0.5)

            mock_dataset.return_value = wrapper_mock.dataset
            mock_wrapper.return_value = wrapper_mock
            mock_vocmap.return_value = vocmap_obj
            mock_incremental_voc_evaluator.return_value = incremental_voc_evaluator_obj
            mock_parse.return_value = 'mock_bounding_boxes'
            mock_eval_pred_inc.return_value = None
            mock_eval.return_value = None

            # Setup mock objects
            predictions_file = 'predictions_od.txt'
            output_file = os.path.join(tmp_output_dir, predictions_file)
            experiment_mock = ExperimentMock(ws_mock)
            mock_run = RunMock(experiment_mock)

            od_utils._validate_score_run(task_is_detection=True,
                                         input_dataset=ds_mock,
                                         use_bg_label=True,
                                         val_metric_type=val_metric_type,
                                         iou_threshold=0.5,
                                         output_file=output_file,
                                         score_run=mock_run)

            # Assert that expected methods were called
            mock_dataset.assert_called_once_with(dataset=ds_mock, is_train=False,
                                                 ignore_data_errors=True,
                                                 use_bg_label=True)
            mock_wrapper.assert_called_once_with(dataset=wrapper_mock.dataset,
                                                 dataset_processing_type=DatasetProcessingType.IMAGES)

            if val_metric_type == ValidationMetricType.VOC:
                mock_vocmap.assert_called_once_with(wrapper_mock, 0.5)
                mock_parse.assert_called_once_with(output_file, wrapper_mock.dataset, wrapper_mock.dataset.classes)
                mock_eval.assert_called_once_with(
                    mock_run, ValidationMetricType.VOC, vocmap_obj, None, 'mock_bounding_boxes'
                )

            elif val_metric_type == ValidationMetricType.INCREMENTAL_VOC:
                mock_incremental_voc_evaluator.assert_called_once_with(True, len(wrapper_mock.dataset.classes), 0.5)
                mock_eval_pred_inc.assert_called_once_with(
                    output_file, wrapper_mock.dataset, incremental_voc_evaluator_obj
                )
                mock_eval.assert_called_once_with(
                    mock_run, ValidationMetricType.INCREMENTAL_VOC, None, incremental_voc_evaluator_obj, []
                )

    def test_parse_bounding_boxes(self):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            # Setup output file
            predictions_file = 'predictions_od.txt'
            output_file = os.path.join(tmp_output_dir, predictions_file)
            self._write_output_file(output_file)

            _, _, wrapper_mock = self._setup_wrapper()
            eval_bounding_boxes = od_utils._parse_bounding_boxes(output_file=output_file,
                                                                 validation_dataset=wrapper_mock.dataset,
                                                                 val_index_map=wrapper_mock.dataset.classes)

            assert len(eval_bounding_boxes) == 2

            bbox1 = eval_bounding_boxes[0]
            assert 'a7c014ec-474a-49f4-8ae3-09049c701913-1' in bbox1['image_id']
            assert bbox1['category_id'] == 'cat'
            assert bbox1['score'] == 0.7
            assert len(bbox1['bbox']) == 4

            bbox2 = eval_bounding_boxes[1]
            assert 'a7c014ec-474a-49f4-8ae3-09049c701913-2' in bbox2['image_id']
            assert bbox2['category_id'] == 'dog'
            assert bbox2['score'] == 0.8
            assert len(bbox1['bbox']) == 4

    @mock.patch(utils.__name__ + '._read_image')
    def test_parse_bounding_boxes_invalid_img(self, mock_read_img):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            # Mock behavior for invalid images
            mock_read_img.return_value = None
            predictions_file = 'predictions_od.txt'
            output_file = os.path.join(tmp_output_dir, predictions_file)
            self._write_output_file(output_file, True)

            _, _, wrapper_mock = self._setup_wrapper()
            eval_bounding_boxes = od_utils._parse_bounding_boxes(output_file=output_file,
                                                                 validation_dataset=wrapper_mock.dataset,
                                                                 val_index_map=wrapper_mock.dataset.classes)
            # No boxes are returned for an invalid image
            assert len(eval_bounding_boxes) == 0

    @mock.patch(od_utils.__name__ + '.IncrementalVocEvaluator.evaluate_batch')
    def test_evaluate_predictions_incrementally(self, mock_evaluate_batch):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            # Set up predictions file.
            predictions_file_name = os.path.join(tmp_output_dir, "predictions_od.txt")
            self._write_output_file(predictions_file_name)

            # Set up dataset wrapper.
            _, _, wrapper_mock = self._setup_wrapper()

            # Set up incremental evaluator.
            incremental_voc_evaluator_obj = IncrementalVocEvaluator(True, len(wrapper_mock.dataset.classes), 0.5)

            # Call _evaluate_predictions_incrementally().
            od_utils._evaluate_predictions_incrementally(
                predictions_file_name=predictions_file_name, dataset=wrapper_mock.dataset,
                incremental_evaluator=incremental_voc_evaluator_obj
            )

            # Check that two calls to evaluate_batch() were made. (one call for a batch with the first image only and
            # one call for a batch with the second image only)
            assert len(mock_evaluate_batch.call_args_list) == 2

            # Get the evaluate_batch() arguments for the first and second image.
            first_call_args = mock_evaluate_batch.call_args_list[0][0]
            second_call_args = mock_evaluate_batch.call_args_list[1][0]

            # Check the ground truth objects for the first image.
            gt_objects = first_call_args[0][0]
            np.testing.assert_array_almost_equal(
                gt_objects["boxes"], [[76.8, 921.6, 153.6, 1024.0], [384.0, 512.0, 460.8, 614.4]], decimal=4
            )
            assert gt_objects["masks"] is None
            np.testing.assert_array_equal(gt_objects["classes"], [1, 2])

            # Check the predicted objects for the first image.
            predicted_objects = first_call_args[1][0]
            np.testing.assert_array_almost_equal(predicted_objects["boxes"], [[76.8, 921.6, 153.6, 819.2]], decimal=4)
            assert predicted_objects["masks"] is None
            np.testing.assert_array_equal(predicted_objects["classes"], [1])
            np.testing.assert_array_equal(predicted_objects["scores"], [0.7])

            # Check the image info for the first image.
            image_info = first_call_args[2][0]
            np.testing.assert_array_equal(image_info["iscrowd"], [0, 0])

            # Check the ground truth objects for the second image.
            gt_objects = second_call_args[0][0]
            np.testing.assert_array_almost_equal(gt_objects["boxes"], [[423.0, 544.0, 540.0, 677.0]], decimal=4)
            assert gt_objects["masks"] is None
            np.testing.assert_array_equal(gt_objects["classes"], [3])

            # Check the predicted objects for the second image.
            predicted_objects = second_call_args[1][0]
            np.testing.assert_array_almost_equal(predicted_objects["boxes"], [[384.0, 512.0, 460.8, 409.6]], decimal=4)
            assert predicted_objects["masks"] is None
            np.testing.assert_array_equal(predicted_objects["classes"], [2])
            np.testing.assert_array_equal(predicted_objects["scores"], [0.8])

            # Check the image info for the second image.
            image_info = second_call_args[2][0]
            np.testing.assert_array_equal(image_info["iscrowd"], [0])

    @mock.patch(od_utils.__name__ + '.VocMap.compute')
    @mock.patch(od_utils.__name__ + '.IncrementalVocEvaluator.compute_metrics')
    @pytest.mark.parametrize("val_metric_type", [ValidationMetricType.VOC, ValidationMetricType.INCREMENTAL_VOC])
    def test_evaluate_and_log(self, mock_incremental_voc_evaluator_compute, mock_vocmap_compute, val_metric_type):
        # Set up mock objects
        metrics = {
            MetricsLiterals.PER_LABEL_METRICS: {
                1: {'precision': 0.1, 'recall': 0.2, 'average_precision': 0.3},
                2: {'precision': 0.2, 'recall': 0.3, 'average_precision': 0.4},
                3: {'precision': 0.3, 'recall': 0.4, 'average_precision': 0.5},
            },
            MetricsLiterals.PRECISION: 0.7,
            MetricsLiterals.RECALL: 0.8,
            MetricsLiterals.MEAN_AVERAGE_PRECISION: 0.9
        }
        mock_vocmap_compute.return_value = metrics
        mock_incremental_voc_evaluator_compute.return_value = metrics

        mock_record = {
            'image_id': 'test_id',
            'bbox': 'test_value',
            'category_id': 'some_label',
            'score': 1.0
        }
        mock_bboxes = [mock_record]

        ws_mock, _, wrapper_mock = self._setup_wrapper()
        experiment_mock = ExperimentMock(ws_mock)
        mock_run = RunMock(experiment_mock)
        vocmap_obj = VocMap(wrapper_mock, 0.5)
        incremental_voc_evaluator_obj = IncrementalVocEvaluator(True, len(wrapper_mock.dataset.classes), 0.5)

        od_utils._evaluate_and_log(
            score_run=mock_run, val_metric_type=val_metric_type, val_vocmap=vocmap_obj,
            incremental_voc_evaluator=incremental_voc_evaluator_obj, eval_bounding_boxes=mock_bboxes
        )

        # Validate that the right compute method was called
        if val_metric_type == ValidationMetricType.VOC:
            mock_vocmap_compute.assert_called_once_with(mock_bboxes, "bbox")
        elif val_metric_type == ValidationMetricType.INCREMENTAL_VOC:
            mock_incremental_voc_evaluator_compute.assert_called_once_with()

        # Validate properties and metrics contain expected values
        properties = mock_run.properties
        assert properties[MetricsLiterals.PRECISION] == 0.7
        assert properties[MetricsLiterals.RECALL] == 0.8
        assert properties[MetricsLiterals.MEAN_AVERAGE_PRECISION] == 0.9

        metrics = mock_run.metrics
        assert metrics[MetricsLiterals.PRECISION] == 0.7
        assert metrics[MetricsLiterals.RECALL] == 0.8
        assert metrics[MetricsLiterals.MEAN_AVERAGE_PRECISION] == 0.9
        assert metrics[MetricsLiterals.PER_LABEL_METRICS] == {
            1: {'precision': 0.1, 'recall': 0.2, 'average_precision': 0.3},
            2: {'precision': 0.2, 'recall': 0.3, 'average_precision': 0.4},
            3: {'precision': 0.3, 'recall': 0.4, 'average_precision': 0.5},
        }


@pytest.mark.usefixtures('new_clean_dir')
def test_score_validation_data(monkeypatch):
    def mock_fetch_model(run_id, device, model_settings):
        assert run_id == 'mock_run_id'
        expected_model_settings = {"dummySetting": "dummyVal"}
        assert model_settings == expected_model_settings
        return 'mock_model'

    def mock_score(model_wrapper, run, target_path, device,
                   output_file, root_dir, image_list_file,
                   batch_size, ignore_data_errors, input_dataset,
                   num_workers, validate_score, log_output_file_info):
        assert model_wrapper == 'mock_model'
        assert target_path.startswith('automl/datasets/')
        assert batch_size == 20
        assert input_dataset.id == '123'
        assert num_workers == 8
        assert device == 'cpu'
        assert log_output_file_info

        data_folder = os.path.join(tmp_output_dir, 'dummyFolder')
        expected_root_dir = os.path.join(data_folder, '.')
        assert root_dir == expected_root_dir

        with open(image_list_file, 'w') as f:
            f.write('testcontent')

    with tempfile.TemporaryDirectory() as tmp_output_dir:
        ds_mock = DatastoreMock('datastore_mock')
        dataset_mock = DatasetMock('123')
        ws_mock = WorkspaceMock(ds_mock)
        experiment_mock = ExperimentMock(ws_mock)
        run_mock = RunMock(experiment_mock)
        model_settings = {"dummySetting": "dummyVal"}
        settings = {
            'validation_dataset_id': '123',
            'validation_batch_size': 20,
            'validation_labels_file': 'test.csv',
            'labels_file_root': tmp_output_dir,
            'data_folder': os.path.join(tmp_output_dir, 'dummyFolder'),
            'num_workers': 8,
            'validate_scoring': False,
            'images_folder': '.',
            'log_scoring_file_info': True
        }

        with monkeypatch.context() as m:
            m.setattr(od_utils, '_fetch_model_from_artifacts', mock_fetch_model)
            od_utils.score_validation_data(run=run_mock, model_settings=model_settings,
                                           settings=settings, device='cpu',
                                           score_with_model=mock_score, val_dataset=dataset_mock)
            expected_val_labels_file = os.path.join(tmp_output_dir, 'test.csv')
            assert os.path.exists(expected_val_labels_file)

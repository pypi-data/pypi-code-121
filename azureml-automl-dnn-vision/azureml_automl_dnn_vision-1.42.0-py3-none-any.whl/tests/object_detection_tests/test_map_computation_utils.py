import pytest

import numpy as np
import torch

from pytest import approx

from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionSystemException
from azureml.automl.dnn.vision.object_detection.eval.map_computation_utils import map_score_voc_11_point_metric, \
    map_score_voc_auc, map_score_voc_11_point_metric_np, map_score_voc_auc_np


class TestMapComputationUtils:
    def test_map11_different_size(self):
        # Precision list and recall list of different size.
        precision_list = torch.rand(10, dtype=torch.float)
        recall_list = torch.rand(5, dtype=torch.float)

        with pytest.raises(AutoMLVisionSystemException):
            map_score_voc_11_point_metric(precision_list, recall_list)

        with pytest.raises(AutoMLVisionSystemException):
            map_score_voc_11_point_metric_np(precision_list.numpy(), recall_list.numpy())

    def test_map11_empty_lists(self):
        # Empty lists.
        precision_list = torch.tensor([], dtype=torch.float)
        recall_list = torch.tensor([], dtype=torch.float)

        map_score_voc_11_point_metric(precision_list, recall_list)

        map_score_voc_11_point_metric_np(precision_list.numpy(), recall_list.numpy())

    def test_map11_random(self):
        # Random precision and recall values.
        precision_list = torch.rand(100, dtype=torch.float)
        recall_list, _ = torch.sort(torch.rand(100, dtype=torch.float))

        map_score = map_score_voc_11_point_metric(precision_list, recall_list)
        assert map_score.ndim == 0
        assert (map_score >= 0.0) and (map_score <= 1.0)

        map_score = map_score_voc_11_point_metric_np(precision_list.numpy(), recall_list.numpy())
        assert map_score.ndim == 0
        assert (map_score >= 0.0) and (map_score <= 1.0)

    def test_map11_three_points(self):
        # Three points on the PR curve: (0.15, 0.7), (0.5, 0.6), (0.85, 0.4).
        precision_list = torch.tensor([0.7, 0.6, 0.4])
        recall_list = torch.tensor([0.15, 0.5, 0.85])

        map_score = map_score_voc_11_point_metric(precision_list, recall_list)
        assert map_score == approx(5.0 / 11.0)

        map_score = map_score_voc_11_point_metric_np(precision_list.numpy(), recall_list.numpy())
        assert map_score == approx(5.0 / 11.0)

    def test_map11_lin_dec_prec(self):
        # Precision linearly decreasing from 1.0 to 0.0 over 20 steps.
        precision_list = torch.arange(1.0, -0.05, -0.05, dtype=torch.float)
        recall_list = torch.arange(0.0, 1.05, 0.05, dtype=torch.float)

        map_score = map_score_voc_11_point_metric(precision_list, recall_list)
        assert map_score == approx(0.5)

        map_score = map_score_voc_11_point_metric_np(precision_list.numpy(), recall_list.numpy())
        assert map_score == approx(0.5)

    def test_map11_duplicates(self):
        # Recall list with duplicate values.
        recall_list = torch.arange(0.0, 1.1, 0.1, dtype=torch.float)
        recall_list, _ = torch.sort(torch.cat((recall_list, recall_list, recall_list)))
        orig_precision_list = torch.rand(11, dtype=torch.float)
        precision_list, _ = torch.sort(torch.cat((orig_precision_list, orig_precision_list, orig_precision_list)),
                                       descending=True)

        # Since precision list is sorted, max precision at 11 recall points corresponding entry in orig_precision_list.
        # map score would be the average of the orig_precision_list.
        expected_map_score = orig_precision_list.sum() / orig_precision_list.nelement()
        expected_map_score = expected_map_score.item()

        map_score = map_score_voc_11_point_metric(precision_list, recall_list)
        assert round(map_score.item(), 3) == round(expected_map_score, 3)

        map_score = map_score_voc_11_point_metric_np(precision_list.numpy(), recall_list.numpy())
        assert round(map_score, 3) == round(expected_map_score, 3)

    def test_map_auc_different_size(self):
        # Precision list and recall list of different size.
        precision_list = torch.rand(10, dtype=torch.float)
        recall_list = torch.rand(5, dtype=torch.float)

        with pytest.raises(AutoMLVisionSystemException):
            map_score_voc_auc(precision_list, recall_list)

        with pytest.raises(AutoMLVisionSystemException):
            map_score_voc_auc_np(precision_list.numpy(), recall_list.numpy())

    def test_map_auc_recall_not_sorted(self):
        # Recall list not sorted.
        precision_list = torch.rand(10, dtype=torch.float)
        recall_list = torch.arange(1.0, 0.0, -0.1, dtype=torch.float)

        with pytest.raises(AutoMLVisionSystemException):
            map_score_voc_auc(precision_list, recall_list)

        with pytest.raises(AutoMLVisionSystemException):
            map_score_voc_auc_np(precision_list.numpy(), recall_list.numpy())

    def test_map_auc_empty_lists(self):
        # Empty lists.

        map_score_voc_auc(torch.tensor([]), torch.tensor([]))

        map_score_voc_auc_np(np.array([]), np.array([]))

    def test_map_auc_random(self):
        # Random precision and recall values.
        precision_list = torch.rand(10, dtype=torch.float)
        recall_list, _ = torch.sort(torch.rand(10, dtype=torch.float))

        map_score = map_score_voc_auc(precision_list, recall_list)
        assert map_score.ndim == 0
        assert (map_score >= 0.0) and (map_score <= 1.0)

        map_score = map_score_voc_auc_np(precision_list.numpy(), recall_list.numpy())
        assert map_score.ndim == 0
        assert (map_score >= 0.0) and (map_score <= 1.0)

    def test_map_auc_five_points(self):
        # Five points on the PR curve: (0.1, 0.8), (0.35, 0.9), (0.4, 0.5), (0.55, 0.6), (0.8, 0.65).
        precision_list = torch.tensor([0.8, 0.9, 0.5, 0.6, 0.65])
        recall_list = torch.tensor([0.1, 0.35, 0.4, 0.55, 0.8])

        expected_map_score = 0.1 * 0.9 + 0.25 * 0.9 + 0.05 * 0.65 + 0.15 * 0.65 + 0.25 * 0.65

        map_score = map_score_voc_auc(precision_list, recall_list)
        assert map_score == approx(expected_map_score)

        map_score = map_score_voc_auc_np(precision_list.numpy(), recall_list.numpy())
        assert map_score == approx(expected_map_score)

    def test_map_auc_five_points_one_duplicate(self):
        # Five points on the PR curve, duplicate recall: (0.1, 0.8), (0.4, 0.5), (0.4, 0.9), (0.55, 0.6), (0.8, 0.65).
        precision_list = torch.tensor([0.8, 0.5, 0.9, 0.6, 0.65])
        recall_list = torch.tensor([0.1, 0.4, 0.4, 0.55, 0.8])

        expected_map_score = 0.1 * 0.9 + 0.25 * 0.9 + 0.05 * 0.9 + 0.15 * 0.65 + 0.25 * 0.65

        map_score = map_score_voc_auc(precision_list, recall_list)
        assert map_score == approx(expected_map_score)

        map_score = map_score_voc_auc_np(precision_list.numpy(), recall_list.numpy())
        assert map_score == approx(expected_map_score)

    def test_map_auc_lin_dec_prec(self):
        # Precision linearly decreasing from 1.0 to 0.0 over 100 steps.
        precision_list = torch.arange(1.0, -0.01, -0.01, dtype=torch.float)
        recall_list = torch.arange(0.0, 1.01, 0.01, dtype=torch.float)

        map_score = map_score_voc_auc(precision_list, recall_list)
        assert map_score == approx(0.5, abs=0.01)

        map_score = map_score_voc_auc_np(precision_list.numpy(), recall_list.numpy())
        assert map_score == approx(0.5, abs=0.01)

    def test_map_auc_unique_recall_value(self):
        # Single recall value to verify unique recall list logic.
        precision_list = torch.rand(10, dtype=torch.float)
        recall_list = 0.5 * torch.ones(10, dtype=torch.float)

        map_score = map_score_voc_auc(precision_list, recall_list)
        assert map_score.ndim == 0
        assert (map_score >= 0.0) and (map_score <= 1.0)

        map_score = map_score_voc_auc_np(precision_list.numpy(), recall_list.numpy())
        assert map_score.ndim == 0
        assert (map_score >= 0.0) and (map_score <= 1.0)

    def test_map_auc_duplicates(self):
        # Recall list with duplicate values.
        recall_list = torch.arange(0.1, 1.1, 0.1, dtype=torch.float)
        recall_list, _ = torch.sort(torch.cat((recall_list, recall_list, recall_list)))
        orig_precision_list = torch.rand(10, dtype=torch.float)
        precision_list, _ = torch.sort(torch.cat((orig_precision_list, orig_precision_list, orig_precision_list)),
                                       descending=True)

        expected_map_score = (torch.sum(orig_precision_list) * 0.1).item()

        map_score = map_score_voc_auc(precision_list, recall_list)
        assert map_score.ndim == 0
        assert round(map_score.item(), 3) == round(expected_map_score, 3)

        map_score = map_score_voc_auc_np(precision_list.numpy(), recall_list.numpy())
        assert map_score.ndim == 0
        assert round(map_score.item(), 3) == round(expected_map_score, 3)

    def test_map_auc_random_large_many_duplicates(self):
        # Random precision and recall values.
        precision_list = np.random.randint(200, 801, size=(1000,)) / 1000.0
        recall_list = np.sort(np.random.randint(0, 1001, size=(1000,)) / 1000.0)

        map_score = map_score_voc_auc(torch.tensor(precision_list), torch.tensor(recall_list))
        map_score_np = map_score_voc_auc_np(precision_list, recall_list)
        assert round(map_score.item(), 6) == round(map_score_np.tolist(), 6)

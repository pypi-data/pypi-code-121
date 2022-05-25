# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for distributed_utils.py"""

import logging
import os
import pytest

from unittest.mock import patch

from azureml.automl.dnn.vision.common import distributed_utils
from azureml.automl.dnn.vision.common.constants import DistributedLiterals

import azureml.automl.dnn.vision.classification.runner as classification_runner
import azureml.automl.dnn.vision.object_detection.runner as od_runner
import azureml.automl.dnn.vision.object_detection_yolo.runner as od_yolo_runner


class TestDistributedUtils:

    @staticmethod
    def _mock_train_worker_fn_distributed_classification(rank, worker_settings, worker_mltable_data_json, multilabel):
        assert rank >= 0
        assert worker_settings[DistributedLiterals.DISTRIBUTED]
        assert worker_mltable_data_json == "dummy_mltable_data_json"
        assert not multilabel

    @staticmethod
    def _mock_train_worker_fn_distributed_od(rank, worker_settings, worker_mltable_data_json):
        assert rank >= 0
        assert worker_settings[DistributedLiterals.DISTRIBUTED]
        assert worker_mltable_data_json == "dummy_mltable_data_json"

    @pytest.mark.parametrize("runner_type", ("classification", "object_detection", "object_detection_yolo"))
    @patch("torch.cuda")
    def test_launch_single_or_distributed_training_non_distributed_scenario(self, torch_cuda_mock, runner_type):
        test_process_id = os.getpid()
        mltable_data_json = "dummy_mltable_data_json"
        multilabel = False
        device_count = 4
        logger = logging.getLogger("test_distributed_utils")

        if runner_type == "classification":
            expected_args = (0, {DistributedLiterals.DISTRIBUTED: False}, mltable_data_json, multilabel)
            additional_train_worker_args = (mltable_data_json, multilabel)
        else:
            expected_args = (0, {DistributedLiterals.DISTRIBUTED: False}, mltable_data_json)
            additional_train_worker_args = (mltable_data_json,)

        # Non distributed training scenario tests

        def _train_worker_fn_side_effect(*args, **kwargs):
            # train_worker function should be called in the same process in non-distributed training.
            assert os.getpid() == test_process_id

        train_worker_path = "azureml.automl.dnn.vision.{}.runner.train_worker".format(runner_type)
        with patch(train_worker_path) as mock_train_worker_fn:
            mock_train_worker_fn.side_effect = _train_worker_fn_side_effect

            if runner_type == "classification":
                train_worker_fn = classification_runner.train_worker
            else:
                if runner_type == "object_detection":
                    train_worker_fn = od_runner.train_worker
                else:
                    train_worker_fn = od_yolo_runner.train_worker

            non_distributed_scenarios = [
                # Distributed setting, cuda available, device count
                (True, False, 0),  # cuda not available
                (True, True, 1),  # cuda available, device count 1
                (False, True, device_count),  # cuda available, device count > 1, but settings["distributed"] is False
            ]

            for scenario in non_distributed_scenarios:
                settings = {DistributedLiterals.DISTRIBUTED: scenario[0]}
                torch_cuda_mock.is_available.return_value = scenario[1]
                torch_cuda_mock.device_count.return_value = scenario[2]
                distributed_utils.launch_single_or_distributed_training(settings, train_worker_fn,
                                                                        additional_train_worker_args, logger)
                assert not settings[DistributedLiterals.DISTRIBUTED]
                mock_train_worker_fn.assert_called_once()
                mock_train_worker_fn.assert_called_once_with(*expected_args)
                mock_train_worker_fn.reset_mock()

        # Distributed scenario tests
        def _update_settings_for_distributed_training_side_effect(fn_settings, fn_device_count):
            assert fn_device_count == device_count

        if runner_type == "classification":
            train_worker_fn = TestDistributedUtils._mock_train_worker_fn_distributed_classification
        else:
            train_worker_fn = TestDistributedUtils._mock_train_worker_fn_distributed_od

        with patch("azureml.automl.dnn.vision.common.distributed_utils.update_settings_for_distributed_training") \
                as mock_update_settings_fn:
            mock_update_settings_fn.side_effect = _update_settings_for_distributed_training_side_effect

            # cuda available, device count > 1 -> Distributed training.
            settings = {DistributedLiterals.DISTRIBUTED: True}
            torch_cuda_mock.is_available.return_value = True
            torch_cuda_mock.device_count.return_value = device_count
            distributed_utils.launch_single_or_distributed_training(settings, train_worker_fn,
                                                                    additional_train_worker_args, logger)
            assert settings[DistributedLiterals.DISTRIBUTED]
            mock_update_settings_fn.reset_mock()

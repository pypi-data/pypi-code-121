# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for common methods."""
import argparse
import os
import pytest
import sys
import tempfile
import pandas as pd
import numpy as np
import json

import torch.utils.data as data

from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock, patch
from _pytest.monkeypatch import MonkeyPatch

import azureml

from azureml.core import Run, Experiment
from azureml.automl.core.inference.inference import AutoMLInferenceArtifactIDs
from azureml.automl.core.shared.constants import MLTableDataLabel

from azureml.automl.dnn.vision.classification.runner import _parse_argument_settings as mc_parser
from azureml.automl.dnn.vision.object_detection.runner import _parse_argument_settings as od_parser
from azureml.automl.dnn.vision.object_detection_yolo.runner import _parse_argument_settings as od_yolo_parser

from azureml.automl.dnn.vision.common import utils
from azureml.automl.dnn.vision.common.dataloaders import RobustDataLoader, _RobustCollateFn
from azureml.automl.dnn.vision.common.data_utils import validate_labels_files_paths
from azureml.automl.dnn.vision.common.utils import _merge_settings_args_defaults, _exception_handler, \
    _read_image, is_aml_dataset_input, _set_train_run_properties, _save_image_df
from azureml.automl.dnn.vision.common.constants import SettingsLiterals, RunPropertyLiterals, TrainingLiterals, \
    TrainingCommonSettings
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionDataException, \
    AutoMLVisionValidationException
from azureml.automl.dnn.vision.common.dataset_helper import AmlDatasetHelper
from azureml.automl.dnn.vision.object_detection.common.constants import TilingLiterals

from azureml.data.dataset_factory import FileDatasetFactory

from .run_mock import RunMock, ExperimentMock, WorkspaceMock, DatastoreMock

_THIS_FILES_DIR = Path(os.path.dirname(__file__))
_PARENT_DIR = _THIS_FILES_DIR.parent
_VALID_PATH = "data/classification_data/multiclass.csv"
_INVALID_PATH = "invalid_path"


class MissingFilesDataset(data.Dataset):
    def __init__(self):
        self._labels = ['label_1', 'label_2', 'label_3']
        self._images = [1, None, 2]

    def __getitem__(self, index):
        return self._images[index], self._labels[index]

    def __len__(self):
        return len(self._labels)


class TestRobustDataLoader:
    def _test_data_loader(self, loader):
        all_data_len = 0
        for images, label in loader:
            all_data_len += images.shape[0]
        assert all_data_len == 2

    def _test_data_loader_with_exception_safe_iterator(self, loader):
        all_data_len = 0
        for images, label in utils._data_exception_safe_iterator(iter(loader)):
            all_data_len += images.shape[0]
        assert all_data_len == 2

    def test_robust_dataloader(self):
        dataset = MissingFilesDataset()
        dataloader = RobustDataLoader(dataset, batch_size=10, num_workers=0)
        self._test_data_loader(dataloader)
        self._test_data_loader_with_exception_safe_iterator(dataloader)

    def test_robust_dataloader_invalid_batch(self):
        dataset = MissingFilesDataset()
        dataloader = RobustDataLoader(dataset, batch_size=1, num_workers=0)
        with pytest.raises(AutoMLVisionDataException) as exc_info:
            self._test_data_loader(dataloader)
        assert exc_info.value.message == _RobustCollateFn.EMPTY_BATCH_ERROR_MESSAGE
        self._test_data_loader_with_exception_safe_iterator(dataloader)

        # Dataloader with multiple workers should raise the exception
        dataloader = RobustDataLoader(dataset, batch_size=1, num_workers=4)
        with pytest.raises(AutoMLVisionDataException) as exc_info:
            self._test_data_loader(dataloader)
        assert _RobustCollateFn.EMPTY_BATCH_ERROR_MESSAGE in exc_info.value.message
        self._test_data_loader_with_exception_safe_iterator(dataloader)


def test_config_merge():
    settings = {"a": "a_s", "b": 1, "c": "c_s"}

    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('--b')
    parser.add_argument('--d')
    parser.add_argument('--f')
    args = parser.parse_args(args=["--b", "b_a", "--d", "d_a", "--f", "f_a"])

    defaults = {"b": "b_d", "d": "d_d", "g": 10}

    merged_settings = _merge_settings_args_defaults(settings, vars(args), defaults)

    assert merged_settings["a"] == "a_s"
    assert merged_settings["b"] == 1
    assert merged_settings["c"] == "c_s"
    assert merged_settings["d"] == "d_a"
    assert merged_settings["f"] == "f_a"
    assert merged_settings["g"] == 10


@pytest.mark.parametrize(
    "passed_value,parsed_value",
    (["True", True],
     ["False", False],
     ["true", True],
     ["false", False],
     ["1", True],
     ["0", False]))
def test_boolean_args_parse(passed_value, parsed_value):
    args = ['early_stopping', 'nesterov', 'amsgrad']

    for arg in args:

        prefixed_arg = '--' + arg
        sys.argv = ['hd_image_classification_dnn_driver.py',
                    '--data-folder', '',
                    '--labels-file-root', '',
                    prefixed_arg, passed_value]

        settings, unknown = mc_parser(automl_settings={}, multilabel=False)
        assert settings[arg] == parsed_value
        assert not unknown

        settings, unknown = mc_parser(automl_settings={}, multilabel=True)
        assert settings[arg] == parsed_value
        assert not unknown

        settings, unknown = od_parser(automl_settings={})
        assert settings[arg] == parsed_value
        assert not unknown

        settings, unknown = od_yolo_parser(automl_settings={})
        assert settings[arg] == parsed_value
        assert not unknown

        sys.argv


def test_tmp_parser():
    # get model_name from argument SettingsLiterals.MODEL_NAME
    parser = argparse.ArgumentParser(allow_abbrev=False)
    utils.add_model_arguments(parser)
    input_mn = [f"--{SettingsLiterals.MODEL_NAME}", "model_a"]
    args_mn, _ = parser.parse_known_args(input_mn)
    args_dict_mn = utils.parse_model_conditional_space(vars(args_mn))
    model_name = args_dict_mn[SettingsLiterals.MODEL_NAME]
    assert model_name == "model_a"

    # get model_name from argument SettingsLiterals.MODEL
    input_m = [f"--{SettingsLiterals.MODEL}", f'{{"{SettingsLiterals.MODEL_NAME}": "model_b"}}']
    args_m, _ = parser.parse_known_args(input_m)
    args_dict_m = utils.parse_model_conditional_space(vars(args_m))
    model_name = args_dict_m[SettingsLiterals.MODEL_NAME]
    assert model_name == "model_b"


def test_labels_files_paths_val_not_aml_dataset_both_paths_valid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.LABELS_FILE: _VALID_PATH,
        SettingsLiterals.VALIDATION_LABELS_FILE: _VALID_PATH
    }

    validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_both_paths_invalid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.LABELS_FILE: _INVALID_PATH,
        SettingsLiterals.VALIDATION_LABELS_FILE: _INVALID_PATH
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_labels_valid_val_invalid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.LABELS_FILE: _VALID_PATH,
        SettingsLiterals.VALIDATION_LABELS_FILE: _INVALID_PATH
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_labels_invalid_val_valid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.LABELS_FILE: _INVALID_PATH,
        SettingsLiterals.VALIDATION_LABELS_FILE: _VALID_PATH
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_only_labels_valid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.LABELS_FILE: _VALID_PATH
    }

    validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_only_labels_invalid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.LABELS_FILE: _INVALID_PATH
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_only_val_valid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.VALIDATION_LABELS_FILE: _VALID_PATH
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_only_val_invalid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.VALIDATION_LABELS_FILE: _INVALID_PATH
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_with_no_paths():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: "",
        SettingsLiterals.LABELS_FILE: "",
        SettingsLiterals.VALIDATION_LABELS_FILE: ""
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)

    settings[SettingsLiterals.DATASET_ID] = ""

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)

    settings[SettingsLiterals.DATASET_ID] = None

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_aml_dataset_with_no_paths():
    settings = {
        SettingsLiterals.DATASET_ID: "some_dataset_id",
        SettingsLiterals.LABELS_FILE_ROOT: "",
        SettingsLiterals.LABELS_FILE: "",
        SettingsLiterals.VALIDATION_LABELS_FILE: ""
    }

    validate_labels_files_paths(settings)


def test_is_aml_dataset_input():
    assert not is_aml_dataset_input({})
    assert not is_aml_dataset_input({SettingsLiterals.DATASET_ID: ""})
    assert not is_aml_dataset_input({SettingsLiterals.DATASET_ID: None})
    assert is_aml_dataset_input({SettingsLiterals.DATASET_ID: "some_dataset_id"})


@mock.patch.object(azureml._restclient.JasmineClient, '__init__', lambda x, y, z, t, **kwargs: None)
@mock.patch.object(azureml._restclient.experiment_client.ExperimentClient, '__init__', lambda x, y, z, **kwargs: None)
@mock.patch('azureml._restclient.experiment_client.ExperimentClient', autospec=True)
@mock.patch('azureml._restclient.metrics_client.MetricsClient', autospec=True)
def test_exception_handler(mock_experiment_client, mock_metrics_client):
    mock_run = MagicMock(spec=Run)
    mock_workspace = MagicMock()
    mock_run.experiment = MagicMock(return_value=Experiment(mock_workspace, "test", _create_in_cloud=False))

    RANDOM_RUNTIME_ERROR = "random system error"
    DATA_RUNTIME_ERROR = "dataset issue"

    @_exception_handler
    def system_error_method(err):
        raise RuntimeError(err)

    @_exception_handler
    def user_error_method():
        raise AutoMLVisionDataException()

    @_exception_handler
    def shm_mem_error_method():
        raise Exception("This might be caused by insufficient shared memory")

    with patch.object(Run, 'get_context', return_value=mock_run):
        with pytest.raises(RuntimeError):
            system_error_method(RANDOM_RUNTIME_ERROR)
        mock_run.fail.assert_called_once()
        assert mock_run.fail.call_args[1]['error_details'].error_type == 'SystemError'
        assert mock_run.fail.call_args[1]['error_details'].error_code == 'AutoMLVisionInternal'
        assert "Additional information: [Hidden as it may contain PII]" not in \
               mock_run.fail.call_args[1]['error_details'].message

        with pytest.raises(RuntimeError):
            system_error_method(DATA_RUNTIME_ERROR)
        assert mock_run.fail.call_args[1]['error_details'].error_type == 'SystemError'
        assert mock_run.fail.call_args[1]['error_details'].error_code == 'AutoMLVisionInternal'
        assert "Additional information: [Hidden as it may contain PII]" in \
               mock_run.fail.call_args[1]['error_details'].message

        with pytest.raises(AutoMLVisionDataException):
            user_error_method()
        assert mock_run.fail.call_args[1]['error_details'].error_type == 'UserError'

        with pytest.raises(Exception):
            shm_mem_error_method()
        assert mock_run.fail.call_args[1]['error_details'].error_type == 'UserError'
        assert mock_run.fail.call_args[1]['error_details'].error_code == 'InvalidData'


@pytest.mark.parametrize('use_cv2', [False, True])
@pytest.mark.parametrize('image_url', ["../data/object_detection_data/images/invalid_image_file.jpg",
                                       "../data/object_detection_data/images/corrupt_image_file.png",
                                       "nonexistent_image_file.png",
                                       "../data/object_detection_data/images/000001679.png"])
def test_read_non_existing_image(use_cv2, image_url):
    image_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), image_url)
    img = _read_image(ignore_data_errors=True,
                      image_url=image_full_path,
                      use_cv2=use_cv2)
    if any(prefix in image_url for prefix in ['invalid', 'corrupt', 'nonexistent']):
        # PIL manages to load corrupt images
        if 'corrupt' in image_url and not use_cv2:
            return
        assert img is None, image_url
    else:
        assert img is not None, image_url


@mock.patch('azureml.automl.dnn.vision.common.utils._get_model_name')
def test_set_train_run_properties(mock_fun):
    ds_mock = DatastoreMock('some_ds')
    ws_mock = WorkspaceMock(ds_mock)
    exp_mock = ExperimentMock(ws_mock)
    run_mock = RunMock(exp_mock)
    model_name = "some_model_name"
    best_metric = 95
    _set_train_run_properties(run_mock, model_name, best_metric)

    run_properties = run_mock.properties

    mock_fun.assert_called_once_with(run_mock.id)
    assert run_properties['runTemplate'] == 'automl_child'
    assert run_properties['run_algorithm'] == model_name
    assert run_properties[RunPropertyLiterals.PIPELINE_SCORE] == best_metric
    assert run_properties[AutoMLInferenceArtifactIDs.ModelName] is not None
    assert AutoMLInferenceArtifactIDs.ModelName in run_properties


def test_round_numeric_values():
    assert utils.round_numeric_values({}, 3) == {}
    assert utils.round_numeric_values({"a": 1.11111}, 2)["a"] == 1.11
    assert utils.round_numeric_values({"a": 1.11111}, 3)["a"] == 1.111
    assert utils.round_numeric_values({"a": 1.11111}, 4)["a"] == 1.1111

    res_dict = utils.round_numeric_values({"a": 1.11111, "b": "val"}, 4)
    assert res_dict["a"] == 1.1111
    assert res_dict["b"] == "val"

    res_dict = utils.round_numeric_values({"a": "a", "b": "b"}, 1)
    assert res_dict["a"] == "a"
    assert res_dict["b"] == "b"


@patch('azureml.automl.dnn.vision.common.utils.get_dataset_from_mltable')
@patch('azureml.automl.dnn.vision.common.utils.get_dataset_from_id')
def test_get_scoring_dataset(mock_get_id, mock_get_mltable):
    datastore_name = "TestDatastoreName"
    datastore_mock = DatastoreMock(datastore_name)
    workspace_mock = WorkspaceMock(datastore_mock)
    experiment_mock = ExperimentMock(workspace_mock)
    run_mock = RunMock(experiment_mock)

    validation_id = 'validation_dataset_id'

    # MLTable
    mltable_json = 'dummy_mltable'

    with patch.object(Run, 'get_context', return_value=run_mock):

        # Call with dataset id
        expected_calls = [((validation_id, workspace_mock),)]
        dataset = utils.get_scoring_dataset(validation_id, mltable_json=None)
        assert dataset is not None
        assert mock_get_id.call_args_list == expected_calls

        # Call with both mltable and dataset id, mltable should be used
        mock_get_id.reset_mock()
        expected_calls = [
            ((mltable_json, workspace_mock, MLTableDataLabel.TestData),)]
        mock_get_mltable.return_value = dataset
        dataset = utils.get_scoring_dataset(
            validation_id, mltable_json=mltable_json)
        assert dataset is not None
        assert mock_get_mltable.call_args_list == expected_calls
        assert mock_get_id.call_args is None

        # Call with mltable TestData
        mock_get_id.reset_mock()
        mock_get_mltable.reset_mock()
        expected_calls = [
            ((mltable_json, workspace_mock, MLTableDataLabel.TestData),)]
        mock_get_mltable.return_value = dataset
        dataset = utils.get_scoring_dataset(None, mltable_json=mltable_json)
        assert dataset is not None
        assert mock_get_mltable.call_args_list == expected_calls
        assert mock_get_id.call_args is None

        # Call with mltable Valid Data
        mock_get_mltable.reset_mock()
        expected_calls = [
            ((mltable_json, workspace_mock, MLTableDataLabel.TestData),),
            ((mltable_json, workspace_mock, MLTableDataLabel.ValidData),)]
        mock_get_mltable.return_value = None
        dataset = utils.get_scoring_dataset(None, mltable_json=mltable_json)
        assert dataset is None
        assert mock_get_mltable.call_args_list == expected_calls
        assert mock_get_id.call_args is None


@patch('azureml.automl.dnn.vision.common.utils.get_dataset_from_mltable')
@patch('azureml.automl.dnn.vision.common.utils.get_dataset_from_id')
def test_get_tabular_dataset(mock_get_id, mock_get_mltable):

    datastore_name = "TestDatastoreName"
    datastore_mock = DatastoreMock(datastore_name)
    workspace_mock = WorkspaceMock(datastore_mock)
    experiment_mock = ExperimentMock(workspace_mock)
    run_mock = RunMock(experiment_mock)

    train_id = 'train_id'
    validation_id = 'validation_dataset_id'

    # Settings
    settings = {SettingsLiterals.DATASET_ID: train_id,
                SettingsLiterals.VALIDATION_DATASET_ID: validation_id}
    mltable_json = 'dummy_mltable'

    with patch.object(Run, 'get_context', return_value=run_mock):

        # Called with dataset ids in settings
        expected_calls = [((train_id, workspace_mock),),
                          ((validation_id, workspace_mock),)]
        train_ds, val_ds = utils.get_tabular_dataset(
            settings=settings, mltable_json=None)
        assert mock_get_id.call_args_list == expected_calls
        assert train_ds is not None
        assert val_ds is not None

        # Called with only train dataset id in settings
        mock_get_id.reset_mock()
        expected_calls = [((train_id, workspace_mock),),
                          ((None, workspace_mock),)]
        train_ds, valid_ds = utils.get_tabular_dataset(
            settings={SettingsLiterals.DATASET_ID: train_id}, mltable_json=None)
        assert train_ds is not None
        assert mock_get_id.call_args_list == expected_calls

        # Called with mltable
        mock_get_mltable.reset_mock()
        expected_calls = [((mltable_json, workspace_mock, MLTableDataLabel.TrainData),),
                          ((mltable_json, workspace_mock, MLTableDataLabel.ValidData),)]
        train_ds, valid_ds = utils.get_tabular_dataset(
            settings={}, mltable_json=mltable_json)
        assert mock_get_mltable.call_args_list == expected_calls

        # Called with both mltable and settings, mltable should be used
        mock_get_mltable.reset_mock()
        mock_get_id.reset_mock()
        expected_calls = [((mltable_json, workspace_mock, MLTableDataLabel.TrainData),),
                          ((mltable_json, workspace_mock, MLTableDataLabel.ValidData),)]
        train_ds, valid_ds = utils.get_tabular_dataset(
            settings={SettingsLiterals.DATASET_ID: train_id}, mltable_json=mltable_json)
        assert mock_get_mltable.call_args_list == expected_calls
        assert mock_get_id.call_args is None


def test_fix_tiling_settings_in_args_dict():
    # tile_grid_size not present in args_dict
    args_dict = {}
    utils.fix_tiling_settings_in_args_dict(args_dict)
    assert TilingLiterals.TILE_GRID_SIZE not in args_dict

    # tile_grid_size present in args_dict, but None
    args_dict = {TilingLiterals.TILE_GRID_SIZE: None}
    utils.fix_tiling_settings_in_args_dict(args_dict)
    assert args_dict[TilingLiterals.TILE_GRID_SIZE] is None

    # tile_grid_size present in args_dict and is a tuple
    args_dict = {TilingLiterals.TILE_GRID_SIZE: (3, 2)}
    utils.fix_tiling_settings_in_args_dict(args_dict)
    assert args_dict[TilingLiterals.TILE_GRID_SIZE] == (3, 2)

    # tile_grid_size present in args_dict and is a string
    args_dict = {TilingLiterals.TILE_GRID_SIZE: "(3, 2)"}
    utils.fix_tiling_settings_in_args_dict(args_dict)
    assert args_dict[TilingLiterals.TILE_GRID_SIZE] == (3, 2)

    # tile_grid_size present in args_dict and is in 3x2 format
    args_dict = {TilingLiterals.TILE_GRID_SIZE: "3x2"}
    utils.fix_tiling_settings_in_args_dict(args_dict)
    assert args_dict[TilingLiterals.TILE_GRID_SIZE] == (3, 2)

    # tile_grid_size present in args_dict and is in 3X2 format
    args_dict = {TilingLiterals.TILE_GRID_SIZE: "3X2"}
    utils.fix_tiling_settings_in_args_dict(args_dict)
    assert args_dict[TilingLiterals.TILE_GRID_SIZE] == (3, 2)


class TestAmlDatasetHelper():
    def setup(self):
        self.monkey_patch = MonkeyPatch()

    def test_labeled_dataset_create_file_upload_path(self):
        datastore_name = "TestDatastoreName"
        datastore_mock = DatastoreMock(datastore_name)
        workspace_mock = WorkspaceMock(datastore_mock)
        experiment_mock = ExperimentMock(workspace_mock)
        run_mock = RunMock(experiment_mock)

        test_target_path = "TestTargetPath"
        labeled_dataset_file_name = "labeled_dataset.json"

        def _test_file_upload_path(monkey_patch, labeled_dataset_file):
            Path(labeled_dataset_file).touch()

            def _upload_directory_mock(directory, data_path, overwrite):
                assert len(data_path) == 2
                assert data_path[0] == datastore_mock
                assert data_path[1] == test_target_path
                assert overwrite

                # Check that labeled_dataset_file is copied at root of directory
                dir_files = os.listdir(directory)
                assert len(dir_files) == 1
                file_0_path = os.path.join(directory, dir_files[0])
                assert os.path.isfile(file_0_path)
                assert dir_files[0] == os.path.basename(labeled_dataset_file)

            with monkey_patch.context() as m:
                m.setattr(FileDatasetFactory, "upload_directory", _upload_directory_mock)
                with patch("azureml.core.Dataset.Tabular.from_json_lines_files"):
                    AmlDatasetHelper.create(run_mock, datastore_mock, labeled_dataset_file,
                                            test_target_path, "TestTask")

        with tempfile.TemporaryDirectory() as tmp_output_dir:
            labeled_dataset_file = os.path.join(tmp_output_dir, labeled_dataset_file_name)
            _test_file_upload_path(self.monkey_patch, labeled_dataset_file)

            dir_path = os.path.join(tmp_output_dir, "dir1", "dir2")
            labeled_dataset_file = os.path.join(dir_path, labeled_dataset_file_name)
            os.makedirs(dir_path, exist_ok=True)
            _test_file_upload_path(self.monkey_patch, labeled_dataset_file)

            try:
                _test_file_upload_path(self.monkey_patch, labeled_dataset_file_name)
            finally:
                os.remove(labeled_dataset_file_name)


def compare_dataframes(df1, df2):
    assert len(df1) == len(df2)
    # comparing the image_url column
    assert df1.iloc[:, 0].to_list() == df2.iloc[:, 0].to_list()

    # comparing the labels column
    # since we are reading from csv, the data is stored as string and we need to convert string to json for comparison
    for i in df1.index:
        assert json.loads(df1.iloc[i, 1].replace("'", '"')) == df2.iloc[i, 1]


def test_save_image_df():
    train_annotations_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          '../data/object_detection_data/train_annotations.json')
    val_annotations_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        '../data/object_detection_data/valid_annotations.json')
    assert os.path.exists(train_annotations_path)
    assert os.path.exists(val_annotations_path)

    columns_to_save = ['image_url', 'label']
    train_df = pd.read_json(train_annotations_path, lines=True)
    val_df = pd.read_json(val_annotations_path, lines=True)
    train_df.rename(columns={'imageUrl': 'image_url'}, inplace=True)
    val_df.rename(columns={'imageUrl': 'image_url'}, inplace=True)

    with tempfile.TemporaryDirectory() as output_dir:
        train_csv = os.path.join(output_dir, 'train_df.csv')
        val_csv = os.path.join(output_dir, 'val_df.csv')

        # Test when both train_df and val_df is present
        _save_image_df(train_df=train_df, val_df=val_df, output_dir=output_dir)
        assert os.path.exists(train_csv)
        assert os.path.exists(val_csv)
        saved_train_df = pd.read_csv(train_csv, names=columns_to_save, sep='\t')
        saved_val_df = pd.read_csv(val_csv, names=columns_to_save, sep='\t')
        compare_dataframes(saved_train_df, train_df[columns_to_save])
        compare_dataframes(saved_val_df, val_df[columns_to_save])

    with tempfile.TemporaryDirectory() as output_dir:
        train_csv = os.path.join(output_dir, 'train_df.csv')
        val_csv = os.path.join(output_dir, 'val_df.csv')

        # Test when only train_df is present
        _save_image_df(train_df=train_df, output_dir=output_dir)
        assert os.path.exists(train_csv)
        assert not os.path.exists(val_csv)
        saved_train_df = pd.read_csv(train_csv, names=columns_to_save, sep='\t')
        compare_dataframes(saved_train_df, train_df[columns_to_save])

    with tempfile.TemporaryDirectory() as output_dir:
        train_csv = os.path.join(output_dir, 'train_df.csv')
        val_csv = os.path.join(output_dir, 'val_df.csv')

        # Test when only val_df is present
        _save_image_df(val_df=val_df, output_dir=output_dir)
        assert not os.path.exists(train_csv)
        assert os.path.exists(val_csv)
        saved_val_df = pd.read_csv(val_csv, names=columns_to_save, sep='\t')
        compare_dataframes(saved_val_df, val_df[columns_to_save])

    with tempfile.TemporaryDirectory() as output_dir:
        train_csv = os.path.join(output_dir, 'train_df.csv')
        val_csv = os.path.join(output_dir, 'val_df.csv')

        # Test with Train_indices and validation indices
        train_index = np.arange(0, 20)
        val_index = np.arange(20, 27)
        _save_image_df(train_df=train_df, train_index=train_index, val_index=val_index, output_dir=output_dir)
        assert os.path.exists(train_csv)
        assert os.path.exists(val_csv)
        saved_train_df = pd.read_csv(train_csv, names=columns_to_save, sep='\t')
        saved_val_df = pd.read_csv(val_csv, names=columns_to_save, sep='\t')
        train_df_split = train_df[0:20][columns_to_save]
        val_df_split = train_df[20:27][columns_to_save]
        compare_dataframes(saved_train_df, train_df_split)
        compare_dataframes(saved_val_df, val_df_split)


def test_set_validation_size_with_validation_size():
    automl_settings = {"validation_size": 0.15}
    args_dict = {"split_ratio": TrainingCommonSettings.DEFAULT_VALIDATION_SIZE}
    utils.set_validation_size(automl_settings, args_dict)
    assert automl_settings["validation_size"] == 0.15


def test_set_validation_size_with_split_ratio():
    automl_settings = {"validation_size": 0.0}
    args_dict = {"split_ratio": 0.15}
    utils.set_validation_size(automl_settings, args_dict)
    assert automl_settings["validation_size"] == 0.15

    automl_settings = {"validation_size": None}
    utils.set_validation_size(automl_settings, args_dict)
    assert automl_settings["validation_size"] == 0.15


def test_set_validation_size_with_default():
    automl_settings = {}
    args_dict = {"split_ratio": TrainingCommonSettings.DEFAULT_VALIDATION_SIZE}
    utils.set_validation_size(automl_settings, args_dict)
    assert automl_settings["validation_size"] == TrainingCommonSettings.DEFAULT_VALIDATION_SIZE

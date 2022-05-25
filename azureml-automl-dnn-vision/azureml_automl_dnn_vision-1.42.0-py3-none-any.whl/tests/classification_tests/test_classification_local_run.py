import os
import tempfile
import shutil
import pytest
import sys
import base64
import mlflow
import json
import torch
import pandas as pd
import numpy as np
from tempfile import NamedTemporaryFile
from logging import exception

import azureml.automl.core.shared.constants as shared_constants
import azureml.automl.dnn.vision.classification.common.classification_utils as cls_utils
import azureml.automl.dnn.vision.classification.runner as runner
import azureml.automl.dnn.vision.common.artifacts_utils as artifacts_utils

from azureml.automl.dnn.vision.common.constants import ArtifactLiterals, \
    TrainingLiterals as CommonTrainingLiterals, SettingsLiterals
from azureml.train.automl import constants
from tests.common.run_mock import RunMock, ExperimentMock, WorkspaceMock, DatastoreMock, DatasetMock
from tests.common.utils import mock_prepare_model_export
from unittest.mock import MagicMock


data_folder = 'classification_data/images'
labels_root = 'classification_data/'


def _get_settings(csv_file):
    return {
        SettingsLiterals.DATA_FOLDER: data_folder,
        SettingsLiterals.DETERMINISTIC: True,
        SettingsLiterals.IMAGE_FOLDER: '.',
        SettingsLiterals.LABELS_FILE: csv_file,
        SettingsLiterals.LABELS_FILE_ROOT: labels_root,
        SettingsLiterals.LOG_VERBOSE_METRICS: True,
        SettingsLiterals.NUM_WORKERS: 0,
        SettingsLiterals.OUTPUT_SCORING: True,
        SettingsLiterals.PRINT_LOCAL_PACKAGE_VERSIONS: True,
        SettingsLiterals.RANDOM_SEED: 47,
        SettingsLiterals.VALIDATION_LABELS_FILE: 'valid_labels.csv'
    }


@pytest.mark.usefixtures('new_clean_dir')
def test_score_validation_data(monkeypatch):
    def mock_load_model_from_artifacts(run_id, device, model_settings):
        assert run_id == 'mock_run_id'
        assert model_settings == {}
        return 'mock_model', {}

    def mock_score(model_wrapper, run, target_path, device,
                   output_file, root_dir, image_list_file,
                   batch_size, ignore_data_errors, input_dataset,
                   num_workers, log_output_file_info):
        assert target_path.startswith('automl/datasets/')
        assert batch_size == 20
        assert input_dataset.id == val_dataset_mock.id
        assert num_workers == 8
        assert device == 'cpu'
        assert log_output_file_info

        data_folder = os.path.join(tmp_output_dir, 'cracks')
        expected_root_dir = os.path.join(data_folder, '.')
        assert root_dir == expected_root_dir

        with open(image_list_file, 'w') as f:
            f.write('testcontent')

    with tempfile.TemporaryDirectory() as tmp_output_dir:
        ds_mock = DatastoreMock('datastore_mock')
        ws_mock = WorkspaceMock(ds_mock)
        experiment_mock = ExperimentMock(ws_mock)
        run_mock = RunMock(experiment_mock)

        val_dataset_id = '123'
        val_dataset_mock = DatasetMock(val_dataset_id)
        image_folder = '.'
        settings = {
            CommonTrainingLiterals.VALIDATION_BATCH_SIZE: 20,
            CommonTrainingLiterals.TRAINING_BATCH_SIZE: 40,
            SettingsLiterals.VALIDATION_LABELS_FILE: 'test.csv',
            SettingsLiterals.LABELS_FILE_ROOT: tmp_output_dir,
            SettingsLiterals.DATA_FOLDER: os.path.join(tmp_output_dir, 'cracks'),
            SettingsLiterals.NUM_WORKERS: 8,
            SettingsLiterals.LOG_SCORING_FILE_INFO: True
        }

        with monkeypatch.context() as m:
            m.setattr(cls_utils, 'load_model_from_artifacts', mock_load_model_from_artifacts)
            cls_utils.score_validation_data(azureml_run=run_mock,
                                            model_settings={},
                                            ignore_data_errors=True,
                                            val_dataset=val_dataset_mock,
                                            image_folder=image_folder,
                                            device='cpu',
                                            settings=settings,
                                            score_with_model=mock_score)
            expected_val_labels_file = os.path.join(tmp_output_dir, 'test.csv')
            assert os.path.exists(expected_val_labels_file)


@pytest.mark.usefixtures('new_clean_dir')
def test_binary_classification_local_run(monkeypatch):
    csv_file = 'binary_classification.csv'
    settings = _get_settings(csv_file)
    settings['task_type'] = constants.Tasks.IMAGE_CLASSIFICATION
    settings['multilabel'] = False
    settings['save_mlflow'] = True
    _test_classification_local_run(monkeypatch, csv_file, settings)


@pytest.mark.usefixtures('new_clean_dir')
def test_multiclassification_local_run(monkeypatch):
    csv_file = 'binary_classification.csv'
    settings = _get_settings(csv_file)
    settings['task_type'] = constants.Tasks.IMAGE_CLASSIFICATION
    settings['multilabel'] = False
    settings['save_mlflow'] = True
    _test_classification_local_run(monkeypatch, csv_file, settings)


@pytest.mark.usefixtures('new_clean_dir')
def test_multilabel_local_run(monkeypatch):
    csv_file = 'multilabel.csv'
    settings = _get_settings(csv_file)
    settings['task_type'] = constants.Tasks.IMAGE_MULTI_LABEL_CLASSIFICATION
    settings['multilabel'] = True
    settings['save_mlflow'] = True
    _test_classification_local_run(monkeypatch, csv_file, settings)


@pytest.mark.usefixtures('new_clean_dir')
def test_classification_local_run_invalid_images(monkeypatch):
    csv_file = 'multiclass_invalid_image.csv'
    settings = _get_settings(csv_file)
    settings.update({
        SettingsLiterals.VALIDATION_LABELS_FILE: 'valid_labels_invalid_image.csv',
        CommonTrainingLiterals.TRAINING_BATCH_SIZE: 1,
        CommonTrainingLiterals.VALIDATION_BATCH_SIZE: 1
    })
    settings['task_type'] = constants.Tasks.IMAGE_CLASSIFICATION
    settings['multilabel'] = False
    _test_classification_local_run(monkeypatch, csv_file, settings)


def _test_classification_local_run(monkeypatch, csv_file, settings=None):
    if settings is None:
        settings = _get_settings(csv_file)

    def mock_score_validation_data(azureml_run, model_settings, ignore_data_errors,
                                   val_dataset, image_folder, device, settings, score_with_model):
        # Ensures score_validation_data is called
        test_output_dir = settings['output_dir']
        predictions_file = os.path.join(test_output_dir, 'predictions.txt')
        with open(predictions_file, 'w') as f:
            f.write('test content')

    with monkeypatch.context() as m:
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            m.setattr(sys, 'argv', ['runner.py', '--data-folder', data_folder, '--labels-file-root', labels_root])
            # Due to a weird monkeypatch behavior where we need to patch from the file where the method is called
            # (even if it's imported from a different file)
            m.setattr(runner, 'score_validation_data', mock_score_validation_data)
            m.setattr(artifacts_utils, 'prepare_model_export', mock_prepare_model_export)

            settings['output_dir'] = tmp_output_dir
            settings['validation_output_file'] = os.path.join(tmp_output_dir, 'predictions.txt')

            runner.run(settings, multilabel=settings['multilabel'])

            expected_model_output = os.path.join(tmp_output_dir, shared_constants.PT_MODEL_FILENAME)
            expected_score_script_output = os.path.join(tmp_output_dir, ArtifactLiterals.SCORE_SCRIPT)
            expected_featurize_script_output = os.path.join(tmp_output_dir, ArtifactLiterals.FEATURIZE_SCRIPT)
            expected_validation_output = os.path.join(tmp_output_dir, 'predictions.txt')

            assert os.path.exists(expected_model_output)
            assert os.path.exists(expected_score_script_output)
            assert os.path.exists(expected_featurize_script_output)
            assert os.path.exists(expected_validation_output)

            # mlflow model export test
            expected_mlflow_model_dir = os.path.join(tmp_output_dir, shared_constants.MLFLOW_OUTPUT_PATH)
            expected_mlflow_model_artifacts_dir = os.path.join(expected_mlflow_model_dir,
                                                               shared_constants.LOCAL_OUTPUT_PATH)
            expected_mlflow_artifacts_pt_file = os.path.join(expected_mlflow_model_artifacts_dir,
                                                             "0",
                                                             shared_constants.PT_MODEL_FILENAME)
            expected_mlflow_artifacts_settings_file = \
                os.path.join(expected_mlflow_model_artifacts_dir,
                             "1",
                             shared_constants.MLFlowLiterals.MODEL_SETTINGS_FILENAME)
            expected_mlflow_model_conda_file = os.path.join(expected_mlflow_model_dir, 'conda.yaml')
            expected_mlflow_model_MLmodel_file = os.path.join(expected_mlflow_model_dir, 'MLmodel')
            expected_mlflow_model_python_model = os.path.join(expected_mlflow_model_dir, 'python_model.pkl')
            expected_mlflow_model_requirements = os.path.join(expected_mlflow_model_dir, 'requirements.txt')

            assert os.path.exists(expected_mlflow_model_dir)
            assert os.path.exists(expected_mlflow_model_artifacts_dir)
            assert os.path.exists(expected_mlflow_artifacts_pt_file)
            assert os.path.exists(expected_mlflow_artifacts_settings_file)
            assert os.path.exists(expected_mlflow_model_conda_file)
            assert os.path.exists(expected_mlflow_model_MLmodel_file)
            assert os.path.exists(expected_mlflow_model_python_model)
            assert os.path.exists(expected_mlflow_model_requirements)
            with open(expected_mlflow_artifacts_settings_file, 'r') as f:
                model_settings_used = json.load(f)
            mlflow_and_torch_parity_check(tmp_output_dir, settings['task_type'], expected_model_output,
                                          model_settings_used,
                                          data_folder,
                                          expected_mlflow_model_dir)


def mlflow_and_torch_parity_check(tmp_output_dir, task_type, model_file, model_settings, data_folder, mlflow_path):
    # torch model inference
    from azureml.automl.dnn.vision.common.model_export_utils import load_model, \
        run_inference_batch, _get_scoring_method

    torch_model = load_model(task_type, model_file, **model_settings)

    def read_image(x):
        with open(x, "rb") as f:
            return f.read()

    def write_img(b_img):
        model_file = NamedTemporaryFile(mode="wb", delete=False, dir=tmp_output_dir)
        model_file.write(b_img)
        return model_file.name

    # list for torch inference
    shutil.copy(os.path.join(data_folder, 'crack_1.jpg'), tmp_output_dir)
    sample_images_paths = [os.path.join(tmp_output_dir, 'crack_1.jpg')]
    # list for mlflow inference
    image_path_list = [write_img(read_image(img)) for img in sample_images_paths]

    # mlflow inference
    df_test = pd.DataFrame(data=[base64.encodebytes(read_image(x)) for x in sample_images_paths],
                           columns=["image"])
    mlflow_model = mlflow.pyfunc.load_model(mlflow_path)
    mlflow_result = json.loads(mlflow_model.predict(df_test).to_json(orient='records'))[0]
    print("mlflow result", mlflow_result)
    # torch model inference
    torch_model_result = json.loads(run_inference_batch(torch_model, image_path_list,
                                    _get_scoring_method(task_type))[0])
    print("torch_model_result", torch_model_result)

    try:
        torch.testing.assert_allclose(np.array(torch_model_result['probs']),
                                      np.array(mlflow_result['probs']),
                                      rtol=1e-05, atol=1e-08)
    except AssertionError:
        raise

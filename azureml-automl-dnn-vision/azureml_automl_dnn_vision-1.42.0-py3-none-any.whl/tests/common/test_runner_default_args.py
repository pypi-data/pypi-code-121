import pytest
import tempfile
from unittest.mock import patch, MagicMock, DEFAULT, ANY

from azureml.automl.dnn.vision.common.constants import SettingsLiterals
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionValidationException
from azureml.automl.dnn.vision.classification import runner as runner_classification
from azureml.automl.dnn.vision.object_detection import runner as runner_od
from azureml.core import Experiment
from azureml.core.run import _OfflineRun, Run
from azureml.automl.core.shared.exceptions import InvalidTypeException
from tests.common.run_mock import DatasetMock


@patch('azureml.automl.dnn.vision.classification.runner.utils.download_required_files')
@patch('azureml.automl.dnn.vision.classification.runner.train')
@patch('azureml.automl.dnn.vision.classification.runner.distributed_utils.master_process')
@patch('azureml.automl.dnn.vision.classification.runner.utils.get_tabular_dataset')
def test_classification_runner(mock_get_tabular_dataset,
                               mock_download,
                               mock_train_model,
                               mock_master_process):

    dataset_id = 'test_dataset_id'
    mock_dataset = DatasetMock(dataset_id)
    mock_get_tabular_dataset.return_value = mock_dataset, mock_dataset

    mock_download.return_value = None
    mock_master_process.return_value = False
    mock_run = get_mock_run()

    def side_effect(*args, **kwargs):
        assert kwargs[SettingsLiterals.IGNORE_DATA_ERRORS] is True
        return DEFAULT

    with patch.object(Run, 'get_context', return_value=mock_run):
        with patch('azureml.automl.dnn.vision.classification.io.read.utils.AmlDatasetWrapper',
                   autospec=True, create=True) as AmlDatasetWrapperMock:
            with tempfile.TemporaryDirectory() as tmp_output_dir:
                AmlDatasetWrapperMock.side_effect = side_effect

                # Test run with dataset id in settings
                settings = {'output_dir': tmp_output_dir,
                            SettingsLiterals.DATASET_ID: dataset_id,
                            SettingsLiterals.VALIDATION_DATASET_ID: dataset_id,
                            SettingsLiterals.TASK_TYPE: 'some_task_type'}
                runner_classification.run(settings)

                # Test run with MLTable
                settings = {'output_dir': tmp_output_dir,
                            SettingsLiterals.TASK_TYPE: 'some_task_type'}
                mltable_json = '{"Type":"MLTable","TrainData":{"Uri":"dummyuri"},' + \
                    '"TestData":null,"ValidData":{"Uri":"dummyuri"}}'
                runner_classification.run(settings, mltable_json)

                # Run with neither MLTable not dataset id, should raise an exception
                settings = {'output_dir': tmp_output_dir,
                            SettingsLiterals.TASK_TYPE: 'some_task_type'}
                with pytest.raises((AutoMLVisionValidationException, InvalidTypeException)):
                    runner_classification.run(settings, mltable_json=None)

    mock_get_tabular_dataset.assert_called_with(settings=ANY,
                                                mltable_json=mltable_json)
    assert(mock_get_tabular_dataset.call_count == 4)


@patch('azureml.automl.dnn.vision.object_detection.runner.utils.download_required_files')
@patch('azureml.automl.dnn.vision.object_detection.runner.read_aml_dataset')
@patch('azureml.automl.dnn.vision.common.utils.get_tabular_dataset')
def test_od_runner(mock_get_tabular_dataset, mock_read_aml_dataset, mock_download):
    dataset_id = 'test_dataset_id'
    mock_dataset = DatasetMock(dataset_id)
    mock_get_tabular_dataset.return_value = mock_dataset, mock_dataset

    mock_download.return_value = None
    mock_run = get_mock_run()
    side_effect_passed = False

    def side_effect(*args, **kwargs):
        nonlocal side_effect_passed
        assert kwargs[SettingsLiterals.IGNORE_DATA_ERRORS] is True
        side_effect_passed = True
        return DEFAULT

    mock_read_aml_dataset.side_effect = side_effect

    with patch.object(Run, 'get_context', return_value=mock_run):
        with tempfile.TemporaryDirectory() as tmp_output_dir:

            # Test run with dataset id passed into settings
            settings = {'output_dir': tmp_output_dir,
                        SettingsLiterals.DATASET_ID: dataset_id,
                        SettingsLiterals.TASK_TYPE: 'some_task_type'}
            try:
                runner_od.run(settings)
            except Exception:
                assert side_effect_passed

            # Test run with MLTable
            side_effect_passed = False
            settings = {'output_dir': tmp_output_dir,
                        SettingsLiterals.TASK_TYPE: 'some_task_type'}
            mltable_json = '{"Type":"MLTable","TrainData":{"Uri":"dummyuri"},' + \
                '"TestData":null,"ValidData":{"Uri":"dummyuri"}}'
            try:
                runner_od.run(settings, mltable_json)
            except Exception:
                assert side_effect_passed

    mock_get_tabular_dataset.assert_called_with(settings=ANY,
                                                mltable_json=mltable_json)
    assert(mock_get_tabular_dataset.call_count == 4)


def get_mock_run():
    mock_run = _OfflineRun()
    mock_workspace = MagicMock()
    mock_run.experiment = MagicMock(return_value=Experiment(
        mock_workspace, "test", _create_in_cloud=False))
    return mock_run

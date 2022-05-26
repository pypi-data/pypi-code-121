import unittest
from unittest.mock import MagicMock, patch

import pytest

from azureml.automl.core.shared.exceptions import ClientException, ValidationException
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import AutoNLPInternal
from azureml.automl.dnn.nlp.ner import runner
from ..mocks import (
    aml_label_dataset_mock,
    file_dataset_mock,
    get_ner_labeling_df,
    MockRun,
    ner_trainer_mock,
    open_ner_file,
    MockValidator
)


@pytest.mark.usefixtures('new_clean_dir')
class NERRunnerTests(unittest.TestCase):
    """Tests for NER trainer."""

    @patch("azureml.automl.dnn.nlp.ner.trainer.Trainer")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoConfig")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoModelForTokenClassification")
    @patch("azureml.automl.dnn.nlp.ner.runner.get_model_from_language")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.ner.runner.create_unique_dir")
    @patch("azureml.automl.dnn.nlp.ner.runner.initialize_log_server")
    @patch("azureml.automl.dnn.nlp.ner.runner.save_model_wrapper")
    @patch("azureml.automl.dnn.nlp.ner.runner.save_conda_yml")
    @patch("azureml.automl.dnn.nlp.ner.runner.AutoTokenizer")
    @patch("azureml.automl.dnn.nlp.ner.runner.prepare_post_run_properties")
    @patch("azureml.automl.dnn.nlp.ner.runner.Run")
    @patch("azureml.automl.dnn.nlp.ner.io.read.dataloader.NLPNERDataValidator")
    def test_runner(
            self,
            validator_mock,
            run_mock,
            post_run_mock,
            tokenizer_mock,
            conda_yml_mock,
            save_model_mock,
            initialize_log_server_mock,
            unique_dir_mock,
            get_by_id_mock,
            language_mock,
            model_mock,
            autoconfig_mock,
            trainer_mock
    ):
        # run mock
        mock_run = MockRun()
        run_mock.get_context.return_value = mock_run

        # settings mock
        automl_settings = {
            "task_type": "text-ner",
            "primary_metric": "accuracy",
            "dataset_id": "mock_dataset_id",
            "validation_dataset_id": "mock_validation_dataset_id"
        }
        mock_settings = MagicMock()
        mock_settings.dataset_id = "mock_dataset_id"
        mock_settings.validation_dataset_id = "mock_validation_dataset_id"
        mock_settings.primary_metric = "accuracy"
        mock_settings.save_mlflow = True
        initialize_log_server_mock.return_value = mock_settings
        unique_dir_mock.return_value = "ner_data"

        # dataset get_by_id mock
        mock_file_dataset = file_dataset_mock()
        get_by_id_mock.return_value = mock_file_dataset

        # data validation mock
        validator_mock.return_value = MockValidator()

        # language mock
        language_mock.return_value = "bert-base-cased", "some_path"

        # model mock
        model = MagicMock()
        model.from_pretrained.return_value = MagicMock()
        model_mock.return_value = model

        # config mock
        autoconfig = MagicMock()
        autoconfig_mock.return_value = autoconfig

        # trainer mock
        mock_trainer = ner_trainer_mock()
        trainer_mock.return_value = mock_trainer

        # Test runner
        runner.run(automl_settings)

        # Asserts
        mock_trainer.train.assert_called_once()
        mock_trainer.save_model.assert_called_once()
        mock_trainer.save_state.assert_called_once()
        self.assertEqual(model_mock.from_pretrained.call_args[0][0], "some_path")

    @patch("azureml.automl.dnn.nlp.ner.trainer.Trainer")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoConfig")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoModelForTokenClassification")
    @patch("azureml.automl.dnn.nlp.ner.io.read.dataloader.copyfile")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.ner.runner.get_model_from_language")
    @patch("azureml.automl.dnn.nlp.ner.runner.initialize_log_server")
    @patch("azureml.automl.dnn.nlp.ner.runner.save_model_wrapper")
    @patch("azureml.automl.dnn.nlp.ner.runner.save_conda_yml")
    @patch("azureml.automl.dnn.nlp.ner.runner.AutoTokenizer")
    @patch("azureml.automl.dnn.nlp.ner.runner.prepare_post_run_properties")
    @patch("azureml.automl.dnn.nlp.ner.runner.Run.get_context")
    @patch("azureml.automl.dnn.nlp.ner.io.read.dataloader.NLPNERDataValidator")
    def test_runner_labeling_service(
            self,
            validator_mock,
            run_mock,
            post_run_mock,
            tokenizer_mock,
            conda_yml_mock,
            save_model_mock,
            initialize_log_server_mock,
            language_mock,
            get_by_id_mock,
            copyfile_mock,
            model_mock,
            autoconfig_mock,
            trainer_mock
    ):
        # run mock
        mock_run = MockRun(
            run_source="Labeling"
        )
        run_mock.return_value = mock_run

        # settings mock
        automl_settings = {
            "task_type": "text-ner",
            "primary_metric": "accuracy",
            "dataset_id": "mock_dataset_id",
            "validation_dataset_id": "mock_validation_dataset_id"
        }
        mock_settings = MagicMock()
        mock_settings.dataset_id = "mock_dataset_id"
        mock_settings.validation_dataset_id = "mock_validation_dataset_id"
        mock_settings.primary_metric = "accuracy"
        mock_settings.save_mlflow = True
        initialize_log_server_mock.return_value = mock_settings
        language_mock.return_value = "bert-base-cased", "some_path"

        # dataset get_by_id mock
        mock_dataset = aml_label_dataset_mock('TextNamedEntityRecognition', data_df=get_ner_labeling_df())
        get_by_id_mock.return_value = mock_dataset

        # data validation mock
        validator_mock.return_value = MockValidator()

        # model mock
        model = MagicMock()
        model.from_pretrained.return_value = MagicMock()
        model_mock.return_value = model

        # config mock
        autoconfig = MagicMock()
        autoconfig_mock.return_value = autoconfig

        # trainer mock
        mock_trainer = ner_trainer_mock()
        trainer_mock.return_value = mock_trainer

        # Test runner
        open_mock = MagicMock(side_effect=open_ner_file)
        with patch("builtins.open", new=open_mock):
            runner.run(automl_settings)

        # Asserts
        mock_trainer.train.assert_called_once()
        mock_trainer.save_model.assert_called_once()
        mock_trainer.save_state.assert_called_once()

    @patch("azureml.automl.dnn.nlp.ner.runner.AutoTokenizer")
    @patch("azureml.automl.dnn.nlp.ner.runner.get_model_from_language")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.ner.runner.initialize_log_server")
    @patch("azureml.automl.dnn.nlp.ner.runner.Run")
    @patch("azureml.automl.dnn.nlp.ner.io.read.dataloader.NLPNERDataValidator")
    def test_runner_without_validation_data(
            self,
            validator_mock,
            run_mock,
            initialize_log_server_mock,
            get_by_id_mock,
            language_mock,
            tokenizer_mock
    ):
        # run mock
        mock_run = MockRun()
        run_mock.get_context.return_value = mock_run

        # settings mock
        automl_settings = {
            "task_type": "text-ner",
            "primary_metric": "accuracy",
            "dataset_id": "mock_dataset_id",
            "validation_dataset_id": None
        }
        mock_settings = MagicMock()
        mock_settings.dataset_id = "mock_dataset_id"
        mock_settings.validation_dataset_id = None
        mock_settings.primary_metric = "accuracy"
        mock_settings.save_mlflow = True
        initialize_log_server_mock.return_value = mock_settings

        # dataset get_by_id mock
        mock_file_dataset = file_dataset_mock()
        get_by_id_mock.return_value = mock_file_dataset

        # data validation mock
        validator_mock.return_value = MockValidator()

        # language mock
        language_mock.return_value = "bert-base-cased", "some_path"

        # Test runner
        with self.assertRaises(ValidationException):
            runner.run(automl_settings)

    @patch("azureml.automl.dnn.nlp.ner.trainer.Trainer")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoConfig")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoModelForTokenClassification")
    @patch("azureml.automl.dnn.nlp.ner.runner.get_model_from_language")
    @patch("azureml.data.abstract_dataset.AbstractDataset._load")
    @patch("azureml.automl.dnn.nlp.ner.runner.create_unique_dir")
    @patch("azureml.automl.dnn.nlp.ner.runner.initialize_log_server")
    @patch("azureml.automl.dnn.nlp.ner.runner.save_model_wrapper")
    @patch("azureml.automl.dnn.nlp.ner.runner.save_conda_yml")
    @patch("azureml.automl.dnn.nlp.ner.runner.AutoTokenizer")
    @patch("azureml.automl.dnn.nlp.ner.runner.prepare_post_run_properties")
    @patch("azureml.automl.dnn.nlp.ner.runner.Run")
    @patch("azureml.automl.dnn.nlp.ner.io.read.dataloader.NLPNERDataValidator")
    def test_runner_mltable_data_json(
            self,
            validator_mock,
            run_mock,
            post_run_mock,
            tokenizer_mock,
            conda_yml_mock,
            save_model_mock,
            initialize_log_server_mock,
            unique_dir_mock,
            dataset_load_mock,
            language_mock,
            model_mock,
            autoconfig_mock,
            trainer_mock
    ):
        # run mock
        mock_run = MockRun()
        run_mock.get_context.return_value = mock_run

        # settings mock
        automl_settings = {
            "task_type": "text-ner",
            "primary_metric": "accuracy"
        }
        mltable_data_json = '{"TrainData": {"Uri": "azuremluri", "ResolvedUri": "resolved_uri"}, ' \
                            '"ValidData": {"Uri": "azuremluri2", "ResolvedUri": "resolved_uri2"}}'
        mock_settings = MagicMock()
        mock_settings.primary_metric = "accuracy"
        mock_settings.save_mlflow = True
        initialize_log_server_mock.return_value = mock_settings
        unique_dir_mock.return_value = "ner_data"

        # dataset get_by_id mock
        mock_file_dataset = file_dataset_mock()
        dataset_load_mock.return_value = mock_file_dataset

        # data validation mock
        validator_mock.return_value = MockValidator()

        # language mock
        language_mock.return_value = "bert-base-cased", "some_path"

        # model mock
        model = MagicMock()
        model.from_pretrained.return_value = MagicMock()
        model_mock.return_value = model

        # config mock
        autoconfig = MagicMock()
        autoconfig_mock.return_value = autoconfig

        # trainer mock
        mock_trainer = ner_trainer_mock()
        trainer_mock.return_value = mock_trainer

        # Test runner
        runner.run(automl_settings, mltable_data_json)

        # Asserts
        mock_trainer.train.assert_called_once()
        mock_trainer.save_model.assert_called_once()
        mock_trainer.save_state.assert_called_once()
        self.assertEqual(model_mock.from_pretrained.call_args[0][0], "some_path")

    @patch("azureml.automl.dnn.nlp.ner.runner.run_lifecycle_utilities.fail_run")
    @patch("azureml.automl.dnn.nlp.ner.runner.Run.get_context")
    def test_runner_exception_scrubbing(self, run_mock, mock_fail_run):
        mock_run = MockRun()
        run_mock.return_value = mock_run

        automl_settings = {
            "task_type": "text-ner",
            "primary_metric": "accuracy"
        }

        with self.assertRaises(Exception):
            with patch("azureml.automl.dnn.nlp.ner.runner.is_data_labeling_run",
                       side_effect=Exception("It's a trap!")):
                runner.run(automl_settings)
        logged_exception = mock_fail_run.call_args[0][1]
        self.assertTrue(isinstance(logged_exception, ClientException))
        self.assertEqual(AutoNLPInternal.__name__, logged_exception.error_code)


if __name__ == "__main__":
    unittest.main()

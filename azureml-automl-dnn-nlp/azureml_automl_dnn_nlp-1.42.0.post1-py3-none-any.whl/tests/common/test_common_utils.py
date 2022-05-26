import builtins
import tempfile

import numpy as np
import pandas as pd
import os
import pickle
import pytest
import torch
import unittest

from unittest.mock import patch, mock_open, Mock

from azureml.automl.core.inference import inference
from azureml.automl.core.shared.constants import CONDA_ENV_FILE_PATH, SCORING_FILE_PATH
from azureml.automl.core.shared.exceptions import ClientException, ResourceException
from azureml.automl.dnn.nlp.classification.multilabel.model_wrapper import ModelWrapper as MultilabelModelWrapper
from azureml.automl.dnn.nlp.classification.multiclass.model_wrapper import ModelWrapper as MulticlassModelWrapper
from azureml.automl.dnn.nlp.ner.model_wrapper import ModelWrapper as NERModelWrapper
from azureml.automl.dnn.nlp.common._model_selector import get_model_from_language, get_path
from azureml.automl.dnn.nlp.common._utils import (is_data_labeling_run_with_file_dataset,
                                                  save_script,
                                                  prepare_run_properties,
                                                  prepare_post_run_properties,
                                                  save_conda_yml,
                                                  save_deploy_script,
                                                  _get_language_code,
                                                  _get_input_example_dictionary,
                                                  _get_output_example,
                                                  _convert_memory_exceptions)
from azureml.automl.dnn.nlp.common.constants import ModelNames
from azureml.automl.dnn.nlp.common.constants import SystemSettings
from azureml.automl.runtime.featurizer.transformer.data.word_embeddings_info import EmbeddingInfo
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.environment import Environment
from ..mocks import MockBertClass, MockRun

try:
    import mlflow
    has_mlflow = True
except ImportError:
    has_mlflow = False


class TestCommonFuncs:
    @pytest.mark.parametrize(
        'dataset_language, expected', [
            ('eng', ModelNames.BERT_BASE_CASED),
            ('deu', ModelNames.BERT_BASE_GERMAN_CASED),
            ('ita', ModelNames.BERT_BASE_MULTILINGUAL_CASED),
            ('ENG', ModelNames.BERT_BASE_CASED),
            ('english', ModelNames.BERT_BASE_MULTILINGUAL_CASED),
            ('', ModelNames.BERT_BASE_MULTILINGUAL_CASED),
            ('DEU', ModelNames.BERT_BASE_GERMAN_CASED),
            ('Deu', ModelNames.BERT_BASE_GERMAN_CASED)]
    )
    def test_model_retrieval(self, dataset_language, expected):
        model, _ = get_model_from_language(dataset_language)
        assert model == expected

    def test_no_cdn_throws_exception(self):
        with patch("azureml.automl.dnn.nlp.common._model_selector.get_path", return_value=None):
            with pytest.raises(ClientException):
                model, _ = get_model_from_language("some_lanugage", need_path=True)

    @pytest.mark.parametrize(
        'input_language, input_multilabel, expected', [
            ('eng', True, EmbeddingInfo.BERT_BASE_UNCASED_AUTONLP_3_1_0),
            ('eng', False, EmbeddingInfo.BERT_BASE_CASED),
            ('deu', False, EmbeddingInfo.BERT_BASE_GERMAN_CASED_AUTONLP_3_1_0),
            ('ita', False, EmbeddingInfo.BERT_BASE_MULTLINGUAL_CASED_AUTONLP_3_1_0)]
    )
    def test_get_path(self, input_language, input_multilabel, expected):
        mock_path = "azureml.automl.dnn.nlp.common._model_selector.AutoMLPretrainedDNNProvider"
        with patch(mock_path) as mock_provider:
            get_path(input_language, input_multilabel)
        assert mock_provider.call_args[0][0] == expected

    @pytest.mark.parametrize(
        'input,expected', [
            ('auto', 'eng'),
            ({"_dataset_language": "eng"}, 'eng'),
            ({"_dataset_language": "deu"}, 'deu'),
            ({"_dataset_language": "ita"}, 'ita')]
    )
    def test_language_recognition(self, input, expected):
        language = _get_language_code(input)
        assert language == expected

    @pytest.mark.parametrize(
        'file_to_save', ['some_file', 'score', 'score_script']
    )
    def test_save_script(self, file_to_save):
        mocked_file = mock_open(read_data='some file contents to write')
        with patch.object(builtins, 'open', mocked_file, create=True):
            save_script(file_to_save, "some_directory")

        assert mocked_file.call_count == 2
        mocked_file.assert_any_call(os.path.join("some_directory", file_to_save))
        mocked_file.assert_called_with(os.path.join("outputs", file_to_save), 'w')
        any('write(some file contents to write)' in str(call) for call in mocked_file()._mock_mock_calls)

    def test_prepare_run_properties(self):
        run = MockRun()
        prepare_run_properties(run, 'some_model')

        assert "runTemplate" in run.properties
        assert "run_algorithm" in run.properties
        assert run.properties['runTemplate'] == "automl_child"
        assert run.properties['run_algorithm'] == "some_model"

    def test_prepare_post_run_properties(self):
        run = MockRun()
        run.id = "some_run_id"
        with patch("azureml.automl.core.inference._get_model_name", return_value="some_model_id"):
            prepare_post_run_properties(run,
                                        "some_model_path",
                                        1234,
                                        "some_conda_file",
                                        'some_deploy_path',
                                        'accuracy',
                                        0.1234)

        artifact_path = "aml://artifact/ExperimentRun/dcid.some_run_id/"
        assert inference.AutoMLInferenceArtifactIDs.CondaEnvDataLocation in run.properties
        file_path = artifact_path + "some_conda_file"
        assert run.properties[inference.AutoMLInferenceArtifactIDs.CondaEnvDataLocation] == file_path

        assert inference.AutoMLInferenceArtifactIDs.ModelDataLocation in run.properties
        file_path = artifact_path + "some_model_path"
        assert run.properties[inference.AutoMLInferenceArtifactIDs.ModelDataLocation] == file_path

        assert inference.AutoMLInferenceArtifactIDs.ModelName in run.properties
        assert run.properties[inference.AutoMLInferenceArtifactIDs.ModelName] == "somerunid"

        assert inference.AutoMLInferenceArtifactIDs.ModelSizeOnDisk in run.properties
        assert run.properties[inference.AutoMLInferenceArtifactIDs.ModelSizeOnDisk] == 1234

        assert 'score' in run.properties
        assert run.properties['score'] == 0.1234

        assert 'primary_metric' in run.properties
        assert run.properties['primary_metric'] == "accuracy"

    def test_save_conda_yml(self):
        conda_deps = CondaDependencies()
        conda_deps.add_pip_package("horovod==0.1.2")
        conda_deps.add_pip_package("dummy_package==0.1.2")

        env = Environment(name="some_name")
        env.python.conda_dependencies = conda_deps

        mocked_file = mock_open()
        with patch.object(builtins, 'open', mocked_file, create=True):
            save_conda_yml(env)

        mocked_file.assert_called_once_with(CONDA_ENV_FILE_PATH, 'w')

        output_file_contents = str(mocked_file()._mock_mock_calls[1])

        assert 'dummy_package==0.1.2' in output_file_contents
        assert 'horovod==0.1.2' not in output_file_contents

    @pytest.mark.parametrize('run_source', ["automl", "Labeling"])
    @pytest.mark.parametrize('labeling_dataset_type', ["FileDataset", "TabularDataset", None])
    def test_is_data_labeling_run_with_file_dataset(self, run_source, labeling_dataset_type):
        mock_run = MockRun(
            run_source=run_source,
            label_column_name="label",
            labeling_dataset_type=labeling_dataset_type
        )
        result = is_data_labeling_run_with_file_dataset(mock_run)
        expected_result = True \
            if (run_source == SystemSettings.LABELING_RUNSOURCE
                and labeling_dataset_type == SystemSettings.LABELING_DATASET_TYPE_FILEDATSET) \
            else False
        assert result == expected_result

    def test_convert_memory_exception_decorator(self):
        error_msg = "CUDA out of memory. Tried to allocate 96.00 MiB " \
                    "(GPU 0; 7.94 GiB total capacity; 7.24 GiB already allocated; 83.50 MiB free; " \
                    "7.30 GiB reserved in total by PyTorch)"

        def dummy_train_mem():
            raise RuntimeError(error_msg)

        # Converted to ResourceException, a user error.
        try:
            _convert_memory_exceptions(dummy_train_mem)()
        except Exception as e:
            assert isinstance(e, ResourceException), \
                f"Incorrect exception type surfaced. Expected ResourceException, got {type(e)}"
            assert error_msg == str(e.inner_exception), "Original error message not preserved"
            assert "not enough memory on the machine" in e.message
        else:
            raise AssertionError("No exception raised when one was expected.")

        def dummy_train_gen():
            raise RuntimeError("Why does the Python live on land? Because it's above C-level.")

        # Not converted to resource exception, meaning it will be correctly surfaced as a SystemException.
        try:
            _convert_memory_exceptions(dummy_train_gen)()
        except Exception as e:
            assert isinstance(e, RuntimeError), \
                f"Incorrect exception type surfaced. Expected RuntimeError, got {type(e)}"
            assert str(e).endswith("C-level.")
        else:
            raise AssertionError("No exception raised when one was expected.")

    def _mlflow_round_trip(self, model):
        with tempfile.TemporaryDirectory() as td:
            model_path = os.path.join(td, "model.pkl")
            with open(os.path.join(td, model_path), 'wb') as f:
                pickle.dump(model, f)

            mlflow_path = os.path.join(td, "mlflow_model")
            mlflow.pyfunc.save_model(path=mlflow_path,
                                     loader_module='azureml.automl.dnn.nlp',
                                     data_path=model_path,
                                     pip_requirements=[])
            return mlflow.pyfunc.load_model(mlflow_path)

    def _compare_models_mlflow(self, wrapped_model, mlflow_model):
        assert isinstance(mlflow_model, mlflow.pyfunc.PyFuncModel), \
            "MLflow model not parsed correctly."
        # This test is technically a little more brittle because we're making assumptions about MLflow.
        assert isinstance(mlflow_model._model_impl, type(wrapped_model)), \
            "Model has wrong type after MLflow round trip conversion."

        source_dnn = wrapped_model.model
        processed_dnn = mlflow_model._model_impl.model
        assert torch.equal(source_dnn.l1.weight, processed_dnn.l1.weight), \
            "Underlying DNN weights not preserved across MLflow conversion."

    @unittest.skipIf(not has_mlflow, "MLflow not present in current environment.")
    def test_mlflow_round_trip_multiclass(self):
        mock_tokenizer = Mock()
        mock_tokenizer.__reduce__ = lambda slf: (Mock, ())

        expected_prediction = np.random.rand(10, 10)
        with patch.object(MulticlassModelWrapper, "predict", return_value=expected_prediction):
            wrapped_model = MulticlassModelWrapper(model=MockBertClass(num_labels=2),
                                                   train_label_list=np.array(["positive", "negative"]),
                                                   tokenizer=mock_tokenizer,
                                                   max_seq_length=128)

            mlflow_model = self._mlflow_round_trip(wrapped_model)
            self._compare_models_mlflow(wrapped_model, mlflow_model)

            np.testing.assert_array_equal(expected_prediction, mlflow_model.predict(np.empty(0)))

    @unittest.skipIf(not has_mlflow, "MLflow not present in current environment.")
    def test_mlflow_round_trip_multilabel(self):
        mock_component = Mock()
        mock_component.__reduce__ = lambda slf: (Mock, ())

        expected_prediction = np.random.rand(10, 10)
        with patch.object(MultilabelModelWrapper, "predict", return_value=expected_prediction):
            wrapped_model = MultilabelModelWrapper(model=MockBertClass(num_labels=2),
                                                   tokenizer=mock_component,
                                                   dataset_language="",
                                                   y_transformer=mock_component,
                                                   label_column_name="labels")

            mlflow_model = self._mlflow_round_trip(wrapped_model)
            self._compare_models_mlflow(wrapped_model, mlflow_model)

            np.testing.assert_array_equal(expected_prediction, mlflow_model.predict(np.empty(0)))

    @unittest.skipIf(not has_mlflow, "MLflow not present in current environment.")
    def test_mlflow_round_trip_ner(self):
        mock_tokenizer = Mock()
        mock_tokenizer.__reduce__ = lambda slf: (Mock, ())

        expected_prediction = np.random.rand(10, 10)
        with patch.object(NERModelWrapper, "predict", return_value=expected_prediction):
            wrapped_model = NERModelWrapper(model=MockBertClass(num_labels=2),
                                            label_list=["positive", "negative"],
                                            tokenizer=mock_tokenizer)

            mlflow_model = self._mlflow_round_trip(wrapped_model)
            self._compare_models_mlflow(wrapped_model, mlflow_model)

            np.testing.assert_array_equal(expected_prediction, mlflow_model.predict(np.empty(0)))

    def test_get_input_example_directory(self):
        test_df = pd.DataFrame({"text": ["example sentence"], "label": ["some_label"]})
        example = _get_input_example_dictionary(test_df, "label")
        expected = "pd.DataFrame({\"text\": pd.Series([\"example_value\"], dtype=\"object\")})"
        assert example == expected

    def test_get_input_example_directory_multicolumn(self):
        test_df = pd.DataFrame(
            {"text1": ["example sentence1"],
             "text2": ["example sentence2"],
             "label": ["some_label"]})
        example = _get_input_example_dictionary(test_df, "label")
        expected = "pd.DataFrame({\"text1\": pd.Series([\"example_value\"], dtype=\"object\"), " + \
                   "\"text2\": pd.Series([\"example_value\"], dtype=\"object\")})"
        assert example == expected

    def test_get_output_example(self):
        test_df = pd.DataFrame({"text": ["example sentence"], "label": ["some_label"]})
        example = _get_output_example(test_df, "label")
        expected = "np.array([\"example_value\"])"
        assert example == expected

    def test_save_deploy_file(self):
        mocked_file = mock_open()
        script = "score_nlp_multiclass_v2.txt"
        input_example = "test_input_example"
        output_example = "test_output_example"
        with patch.object(builtins, 'open', mocked_file, create=True):
            save_deploy_script(script, input_example, output_example)
        mocked_file.assert_called_with(SCORING_FILE_PATH, 'w')

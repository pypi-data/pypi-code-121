import builtins
import os
import unittest

from os.path import join
from unittest.mock import ANY, Mock, mock_open, patch

from azureml.automl.core.shared import constants
from azureml.automl.dnn.nlp.classification.io.write.save_utils import save_metrics, save_model_wrapper
from azureml.automl.dnn.nlp.common.constants import OutputLiterals, SystemSettings

from ...mocks import MockRun


class TestSaveFuncs(unittest.TestCase):
    """Tests for save functions."""
    def test_save_metrics(self):
        mocked_metrics_dict = {
            "accuracy": [0.5],
            "precision": [0.6],
            "recall": [0.7]
        }
        mocked_file = mock_open()

        with patch.object(builtins, 'open', mocked_file, create=True):
            save_metrics(mocked_metrics_dict)

        save_path = join(OutputLiterals.OUTPUT_DIR, "metrics.csv")
        mocked_file.assert_called_once_with(save_path, 'w', encoding='utf-8', errors='strict', newline='')

        self.assertTrue(any("accuracy,precision,recall" in str(call) for call in mocked_file()._mock_mock_calls))
        self.assertTrue(any("0.5,0.6,0.7" in str(call) for call in mocked_file()._mock_mock_calls))

    @patch('azureml.train.automl.runtime._azureautomlruncontext.AzureAutoMLRunContext.batch_save_artifacts')
    def test_save_model_wrapper_mlflow(self,
                                       mock_batch_save_artifacts):
        model = Mock()
        mock_run = MockRun()
        input_sample_str = "pd.DataFrame({\"text\": pd.Series([\"example_value\"], dtype=\"object\")})"
        output_sample_str = "np.array([\"example_value\"])"
        save_model_wrapper(run=mock_run, model=model, save_mlflow=True,
                           input_sample_str=input_sample_str, output_sample_str=output_sample_str)

        mock_batch_save_artifacts.assert_called_once_with(
            os.getcwd(),
            input_strs={constants.RUN_ID_OUTPUT_PATH: mock_run.id},
            model_outputs={os.path.join(OutputLiterals.OUTPUT_DIR, OutputLiterals.MODEL_FILE_NAME): model},
            save_as_mlflow=True,
            mlflow_options={constants.MLFlowLiterals.LOADER: SystemSettings.NAMESPACE,
                            constants.MLFlowLiterals.SCHEMA_SIGNATURE: ANY}
        )  # Correctly route request to batch save artifacts with necessary MLflow settings populated.

        self.assertEqual("inputs: \n  ['text': string]\noutputs: \n  [Tensor('str', (-1,))]\n",
                         str(mock_batch_save_artifacts.call_args[1]["mlflow_options"]["signature"]))

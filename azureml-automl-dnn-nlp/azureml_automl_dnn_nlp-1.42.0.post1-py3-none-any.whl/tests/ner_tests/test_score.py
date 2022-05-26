import pytest
import unittest
from unittest.mock import MagicMock, mock_open, patch

import numpy as np
import os

from azureml.automl.dnn.nlp.common.constants import (
    DataLabelingLiterals, DataLiterals, NERModelParameters, OutputLiterals
)
from azureml.automl.dnn.nlp.ner.inference.score import score
from azureml.data import FileDataset
from ..mocks import aml_label_dataset_mock, get_ner_labeling_df, MockRun, open_ner_file


@pytest.mark.usefixtures('new_clean_dir')
class NERScoreTests(unittest.TestCase):
    """Tests for NER scorer."""

    @patch("azureml.automl.dnn.nlp.ner.inference.score.Trainer")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.get_labels")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.get_model_from_language")
    @patch("json.loads")
    @patch("azureml.automl.dnn.nlp.ner.inference.score._get_language_code")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoModelForTokenClassification")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoTokenizer")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoConfig")
    @patch("azureml.automl.dnn.nlp.common._utils.Run")
    def test_score(
            self, run_mock, config_mock, tokenizer_mock, model_mock, get_by_id_mock,
            lang_fetch_mock, json_mock, lang_routing_mock, get_labels_mock, trainer_mock
    ):
        mock_run = MockRun()
        run_mock.get_context.return_value = mock_run
        run_mock.download_file.return_value = None
        config_mock.from_pretrained.return_value = MagicMock()
        tokenizer_mock.from_pretrained.return_value = MagicMock()
        model_mock.from_pretrained.return_value = MagicMock()
        dataset_mock = MagicMock(FileDataset)
        dataset_mock.download.return_value = MagicMock()
        dataset_mock.to_path.return_value = ["/sample_test.txt"]
        get_by_id_mock.return_value = dataset_mock
        lang_fetch_mock.return_value = "some_language"
        lang_routing_mock.return_value = "another_language", "some_path"
        json_mock.return_value = MagicMock()

        label_list = ["O", "B-MISC", "I-MISC", "B-PER"]
        get_labels_mock.return_value = label_list

        trainer = MagicMock()
        batch_size = 3
        seq_len = NERModelParameters.MAX_SEQ_LENGTH
        predictions = np.random.rand(batch_size, seq_len, len(label_list))
        label_ids = np.random.randint(0, high=len(label_list), size=(batch_size, seq_len))
        trainer.predict.return_value = predictions, label_ids, {"metrics": 0.5}
        trainer_mock.return_value = trainer

        open_mock = mock_open()
        with patch("builtins.open", open_mock):
            score(
                run_id=mock_run.id,
                input_dataset_id="mock_dataset_id",
                data_dir="ner_data",
                output_dir="output_dir",
            )
        self.assertEqual(open_mock.call_count, 3)
        self.assertEqual(tokenizer_mock.from_pretrained.call_args[0][0], "another_language")

    @patch("azureml.automl.dnn.nlp.ner.inference.score.Trainer")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.get_labels")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.get_model_from_language")
    @patch("json.loads")
    @patch("azureml.automl.dnn.nlp.ner.inference.score._get_language_code")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoModelForTokenClassification")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoTokenizer")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoConfig")
    @patch("azureml.automl.dnn.nlp.common._utils.Run")
    def test_score_no_metric(
            self, run_mock, config_mock, tokenizer_mock, model_mock, get_by_id_mock,
            lang_fetch_mock, json_mock, lang_routing_mock, get_labels_mock, trainer_mock
    ):
        mock_run = MockRun()
        run_mock.get_context.return_value = mock_run
        run_mock.download_file.return_value = None
        config_mock.from_pretrained.return_value = MagicMock()
        tokenizer_mock.from_pretrained.return_value = MagicMock()
        model_mock.from_pretrained.return_value = MagicMock()
        dataset_mock = MagicMock(FileDataset)
        dataset_mock.download.return_value = MagicMock()
        dataset_mock.to_path.return_value = ["/sample_test.txt"]
        get_by_id_mock.return_value = dataset_mock
        lang_fetch_mock.return_value = "some_language"
        lang_routing_mock.return_value = "another_language", "some_path"
        json_mock.return_value = MagicMock()

        label_list = ["O", "B-MISC", "I-MISC", "B-PER"]
        get_labels_mock.return_value = label_list

        trainer = MagicMock()
        batch_size = 3
        seq_len = NERModelParameters.MAX_SEQ_LENGTH
        predictions = np.random.rand(batch_size, seq_len, len(label_list))
        label_ids = np.random.randint(0, high=len(label_list), size=(batch_size, seq_len))
        trainer.predict.return_value = predictions, label_ids, None
        trainer_mock.return_value = trainer

        open_mock = mock_open()
        with patch("builtins.open", open_mock):
            score(
                run_id=mock_run.id,
                input_dataset_id="mock_dataset_id",
                data_dir="ner_data",
                output_dir="output_dir",
            )
        self.assertEqual(open_mock.call_count, 3)

    @patch("azureml.automl.dnn.nlp.ner.inference.score.Trainer")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoModelForTokenClassification")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoTokenizer")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoConfig")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.get_run_by_id")
    def test_score_labeling_service(
            self, run_mock, config_mock, tokenizer_mock, model_mock, get_by_id_mock,
            trainer_mock,  # generate_results_for_labeling_service_mock
    ):
        mock_run = MockRun(
            run_source="Labeling"
        )
        run_mock.return_value = mock_run

        config_mock.from_pretrained.return_value = MagicMock()
        tokenizer_mock.from_pretrained.return_value = MagicMock()
        model_mock.from_pretrained.return_value = MagicMock()

        data_df = get_ner_labeling_df().head(2)
        portable_paths = data_df[DataLabelingLiterals.PORTABLE_PATH_COLUMN_NAME]
        mock_dataset = aml_label_dataset_mock('TextNamedEntityRecognition', data_df=data_df)
        get_by_id_mock.return_value = mock_dataset

        trainer = MagicMock()
        batch_size = 2
        seq_len = NERModelParameters.MAX_SEQ_LENGTH
        # Create fake predictions
        label_list = ["B-LOC", "B-PER", "O"]
        predictions = np.random.rand(batch_size, seq_len, len(label_list))
        label_ids = np.random.randint(0, high=len(label_list), size=(batch_size, seq_len))
        trainer.predict.return_value = predictions, label_ids, {"metrics": 0.5}
        trainer_mock.return_value = trainer

        open_mock = MagicMock(side_effect=open_ner_file)
        with patch("azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper.os.remove"):
            with patch("builtins.open", new=open_mock):
                score(
                    run_id=mock_run.id,
                    input_dataset_id="mock_dataset_id",
                    data_dir="ner_data",
                    output_dir=OutputLiterals.OUTPUT_DIR,
                )

        self.assertEquals(trainer_mock.call_count, 1)
        self.assertEquals(trainer.predict.call_count, 1)
        # Check Text File to CoNLL text conversion
        self.assertEquals(
            open_mock.call_args_list[0][0][0],
            os.path.join(DataLiterals.NER_DATA_DIR, portable_paths[0].lstrip("/"))
        )
        self.assertEquals(
            open_mock.call_args_list[1][0][0],
            os.path.join(DataLiterals.NER_DATA_DIR, DataLiterals.TEST_TEXT_FILENAME)
        )
        self.assertEquals(
            open_mock.call_args_list[2][0][0],
            os.path.join(DataLiterals.NER_DATA_DIR, portable_paths[1].lstrip("/"))
        )
        self.assertEquals(
            open_mock.call_args_list[3][0][0],
            os.path.join(DataLiterals.NER_DATA_DIR, DataLiterals.TEST_TEXT_FILENAME)
        )
        # Check CoNLL predictions to jsonlines text conversion
        self.assertEquals(
            open_mock.call_args_list[8][0][0],
            os.path.join(OutputLiterals.OUTPUT_DIR, OutputLiterals.PREDICTIONS_TXT_FILE_NAME)
        )
        self.assertEquals(
            open_mock.call_args_list[9][0][0],
            os.path.join(DataLiterals.NER_DATA_DIR, portable_paths[0].lstrip("/"))
        )
        self.assertEquals(
            open_mock.call_args_list[10][0][0],
            os.path.join(OutputLiterals.OUTPUT_DIR, OutputLiterals.PREDICTIONS_TXT_FILE_NAME)
        )
        self.assertEquals(
            open_mock.call_args_list[11][0][0],
            os.path.join(DataLiterals.NER_DATA_DIR, portable_paths[1].lstrip("/"))
        )

    @patch("azureml.automl.dnn.nlp.ner.inference.score.Trainer")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.get_labels")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.get_model_from_language")
    @patch("json.loads")
    @patch("azureml.automl.dnn.nlp.ner.inference.score._get_language_code")
    @patch("azureml.data.abstract_dataset.AbstractDataset._load")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoModelForTokenClassification")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoTokenizer")
    @patch("azureml.automl.dnn.nlp.ner.inference.score.AutoConfig")
    @patch("azureml.automl.dnn.nlp.common._utils.Run")
    def test_score_mltable_uri(
            self, run_mock, config_mock, tokenizer_mock, model_mock, load_dataset_mock,
            lang_fetch_mock, json_mock, lang_routing_mock, get_labels_mock, trainer_mock
    ):
        mock_run = MockRun()
        run_mock.get_context.return_value = mock_run
        run_mock.download_file.return_value = None
        config_mock.from_pretrained.return_value = MagicMock()
        tokenizer_mock.from_pretrained.return_value = MagicMock()
        model_mock.from_pretrained.return_value = MagicMock()
        dataset_mock = MagicMock(FileDataset)
        dataset_mock.download.return_value = MagicMock()
        dataset_mock.to_path.return_value = ["/sample_test.txt"]
        load_dataset_mock.return_value = dataset_mock
        lang_fetch_mock.return_value = "some_language"
        lang_routing_mock.return_value = "another_language", "some_path"
        json_mock.return_value = MagicMock()

        label_list = ["O", "B-MISC", "I-MISC", "B-PER"]
        get_labels_mock.return_value = label_list

        trainer = MagicMock()
        batch_size = 3
        seq_len = NERModelParameters.MAX_SEQ_LENGTH
        predictions = np.random.rand(batch_size, seq_len, len(label_list))
        label_ids = np.random.randint(0, high=len(label_list), size=(batch_size, seq_len))
        trainer.predict.return_value = predictions, label_ids, {"metrics": 0.5}
        trainer_mock.return_value = trainer

        open_mock = mock_open()
        with patch("builtins.open", open_mock):
            score(
                run_id=mock_run.id,
                input_mltable_uri="mock_mltable_uri",
                data_dir="ner_data",
                output_dir="output_dir",
            )
        self.assertEqual(open_mock.call_count, 3)
        self.assertEqual(tokenizer_mock.from_pretrained.call_args[0][0], "another_language")


if __name__ == "__main__":
    unittest.main()

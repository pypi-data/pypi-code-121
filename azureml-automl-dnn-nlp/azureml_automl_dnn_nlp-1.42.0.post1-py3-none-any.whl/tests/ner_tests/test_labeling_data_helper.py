from unittest.mock import MagicMock, patch, mock_open

import ast
import numpy as np
import os
import pytest
import unittest

from azureml.automl.dnn.nlp.common.constants import DataLiterals, DataLabelingLiterals, OutputLiterals, Split
from azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper import (
    _convert_to_spans, generate_results_for_labeling_service,
    load_dataset_for_labeling_service, _convert_to_conll,
    _convert_to_conll_no_label
)
from ..mocks import (
    aml_label_dataset_mock, get_ner_labeling_df, open_ner_file
)


@pytest.mark.usefixtures('new_clean_dir')
class LabelingDataHelperTest(unittest.TestCase):
    """Tests for labeling data helper functions."""
    def __init__(self, *args, **kwargs):
        super(LabelingDataHelperTest, self).__init__(*args, **kwargs)

    def test_convert_to_conll_non_empty_file_at_beginning(self):
        open_mock = mock_open(read_data='')
        open_mock.return_value.__iter__.return_value = ''
        with patch("builtins.open", new=open_mock):
            empty_file_cnt = _convert_to_conll('test', '', '', True)

        self.assertEquals(empty_file_cnt, 0)
        self.assertEquals(len(open_mock.return_value.method_calls), 1)
        self.assertEquals(open_mock.return_value.method_calls[-1][0], 'writelines')
        self.assertEquals(open_mock.return_value.method_calls[-1][1][0][0], 'test O\n')

    def test_convert_to_conll_non_empty_file_not_at_beginning(self):
        open_mock = mock_open(read_data='')
        open_mock.return_value.__iter__.return_value = ''
        with patch("builtins.open", new=open_mock):
            empty_file_cnt = _convert_to_conll('test', '', '', False)

        self.assertEquals(empty_file_cnt, 0)
        self.assertEquals(len(open_mock.return_value.method_calls), 2)
        self.assertEquals(open_mock.return_value.method_calls[-1][0], 'writelines')
        self.assertEquals(open_mock.return_value.method_calls[-1][1][0][0], 'test O\n')
        self.assertEquals(open_mock.return_value.method_calls[-2][0], 'write')
        self.assertEquals(open_mock.return_value.method_calls[-2][1][0][0], '\n')

    def test_convert_to_conll_empty_file(self):
        for at_beginning in [True, False]:
            open_mock = mock_open(read_data='')
            open_mock.return_value.__iter__.return_value = ''
            with patch("builtins.open", new=open_mock):
                empty_file_cnt = _convert_to_conll('', '', '', at_beginning)

            self.assertEquals(empty_file_cnt, 1)
            self.assertEquals(len(open_mock.return_value.method_calls), 1)
            self.assertEquals(open_mock.return_value.method_calls[-1][0], 'writelines')
            self.assertEquals(open_mock.return_value.method_calls[-1][1][0], [])

    def test_convert_to_conll_no_label_non_empty_file_at_beginning(self):
        open_mock = mock_open(read_data='')
        open_mock.return_value.__iter__.return_value = ''
        with patch("builtins.open", new=open_mock):
            empty_file_cnt = _convert_to_conll_no_label('test', '', True)

        self.assertEquals(empty_file_cnt, 0)
        self.assertEquals(len(open_mock.return_value.method_calls), 1)
        self.assertEquals(open_mock.return_value.method_calls[-1][0], 'writelines')
        self.assertEquals(open_mock.return_value.method_calls[-1][1][0][0], 'test\n')

    def test_convert_to_conll_no_label_non_empty_file_not_at_beginning(self):
        open_mock = mock_open(read_data='')
        open_mock.return_value.__iter__.return_value = ''
        with patch("builtins.open", new=open_mock):
            empty_file_cnt = _convert_to_conll_no_label('test', '', False)

        self.assertEquals(empty_file_cnt, 0)
        self.assertEquals(len(open_mock.return_value.method_calls), 2)
        self.assertEquals(open_mock.return_value.method_calls[-1][0], 'writelines')
        self.assertEquals(open_mock.return_value.method_calls[-1][1][0][0], 'test\n')
        self.assertEquals(open_mock.return_value.method_calls[-2][0], 'write')
        self.assertEquals(open_mock.return_value.method_calls[-2][1][0][0], '\n')

    def test_convert_to_conll_no_label_empty_file(self):
        for at_beginning in [True, False]:
            open_mock = mock_open(read_data='')
            open_mock.return_value.__iter__.return_value = ''
            with patch("builtins.open", new=open_mock):
                empty_file_cnt = _convert_to_conll_no_label('', '', at_beginning)

            self.assertEquals(empty_file_cnt, 1)
            self.assertEquals(len(open_mock.return_value.method_calls), 1)
            self.assertEquals(open_mock.return_value.method_calls[-1][0], 'writelines')
            self.assertEquals(open_mock.return_value.method_calls[-1][1][0], [])

    def _load_dataset_for_labeling_service_test_helper(self, split):
        if split == Split.train:
            data_filename = DataLiterals.TRAIN_TEXT_FILENAME
        elif split == Split.test:
            data_filename = DataLiterals.TEST_TEXT_FILENAME
        else:
            raise ValueError(f"Encountered unexpected split value {str(split)}")

        mock_dataset = aml_label_dataset_mock("TextNamedEntityRecognition", data_df=get_ner_labeling_df())
        file_objects = []

        # To ensure we didn't introduce any validation errors in conversion,
        # let's save the file_objects to check what was written to them later.
        def tracked_ner_io(*args, **kwargs):
            ret = open_ner_file(*args, **kwargs)
            file_objects.append(ret)
            return ret

        open_mock = MagicMock(side_effect=tracked_ner_io)

        with patch("builtins.open", new=open_mock):
            output_filename, input_file_paths = \
                load_dataset_for_labeling_service(dataset=mock_dataset,
                                                  data_dir=DataLiterals.NER_DATA_DIR,
                                                  data_filename=data_filename,
                                                  data_split=split)

        # Get series containing NER text filepaths. Each entry should look something like "/datastore/sample1.txt".
        portable_paths = get_ner_labeling_df()[DataLabelingLiterals.PORTABLE_PATH_COLUMN_NAME]
        for i in range(portable_paths.shape[0]):
            # Did we read all the specified input file?
            self.assertTrue(os.path.join(DataLiterals.NER_DATA_DIR, portable_paths[i].lstrip("/"))
                            in open_mock.call_args_list[2 * i][0][0])
            # Do we have an open call to the output file for each one?
            self.assertTrue(os.path.join(DataLiterals.NER_DATA_DIR, data_filename)
                            in open_mock.call_args_list[2 * i + 1][0][0])
        # Did we return the right output file?
        self.assertEquals(data_filename, output_filename)
        # Did we return the right input files?
        self.assertEquals(input_file_paths, portable_paths.apply(lambda f: f.lstrip("/")).tolist())

        if split == Split.train:
            even_input = ['Nikolaus B-PER\n', 'is O\n', 'from O\n', 'America B-LOC\n', '. O\n']
            odd_input = ['Conference O\n', 'was O\n', 'held O\n', 'in O\n', 'Seattle B-LOC\n', '. O\n']
        else:
            even_input = ['Nikolaus\n', 'is\n', 'from\n', 'America\n', '.\n']
            odd_input = ['Conference\n', 'was\n', 'held\n', 'in\n', 'Seattle\n', '.\n']

        self.assertEqual(1, file_objects[0].read.call_count)
        # Don't prepend a newline because this is the first file.
        self.assertEqual(0, file_objects[1].write.call_count)
        file_objects[1].writelines.assert_called_once_with(even_input)

        for i in range(1, len(file_objects) // 2):
            self.assertEqual(1, file_objects[2 * i].read.call_count)
            file_objects[2 * i + 1].write.assert_called_once_with('\n')  # CoNLL format file separator.
            file_objects[2 * i + 1].writelines.assert_called_once_with(odd_input if i % 2 == 1 else even_input)

    def test_load_dataset_for_labeling_service_train_split(self):
        self._load_dataset_for_labeling_service_test_helper(Split.train)

    def test_load_dataset_for_labeling_service_test_split(self):
        self._load_dataset_for_labeling_service_test_helper(Split.test)

    def test_generate_labeling_results_newline_ending(self):
        pred_file_content = \
            "Microsoft B-ORG 0.9999\nis O 0.9923\na O 0.9997\ncompany O 0.9955\n. O 0.9999\n\n" \
            "Amazon B-ORG 0.9986\nis O 0.9964\nanother O 0.9986\ncompany O 0.9933\n. O 0.9912\n\n" \
            "But O 0.9963\nMicrosoft B-ORG 0.9999\nis O 0.9953\nbetter O 0.9963\n. O 0.9983\n"

        with patch('os.remove'):
            with patch('azureml.automl.dnn.nlp.ner.io.read'
                       '._labeling_data_helper._convert_to_spans') as mock_span_conversion:
                with patch("builtins.open", new=mock_open(read_data=pred_file_content)):
                    generate_results_for_labeling_service("creative filename", [""] * 3, "data_dir")

        for call in mock_span_conversion.mock_calls:
            self.assertTrue(all([token_label_pair and len(token_label_pair.split()) == 3
                                 for token_label_pair in call[1][0]]))

    def test_generate_results_for_labeling_service(self):
        predicted_labels = [['O', 'O', 'O', 'O', 'O'], ['O', 'O', 'B-PER', 'I-PER', 'O']]
        score_list = np.random.rand(2, 5)
        predictions_output_file_path = os.path.join(
            OutputLiterals.OUTPUT_DIR, OutputLiterals.PREDICTIONS_TXT_FILE_NAME
        )
        first_file_name = os.path.join("datastore", "sample1.txt")
        second_file_name = os.path.join("datastore", "sample2.txt")
        predictions_first_file = self.get_mock_prediction_list(
            predicted_labels[0], score_list[0]
        )
        predictions_second_file = self.get_mock_prediction_list(
            predicted_labels[1], score_list[1], ["a", "news", "briefing", "scientific", "study"]
        )
        mock_text = self.get_mock_predictions_text(predicted_labels, score_list)
        open_mock = mock_open(read_data=mock_text)
        mock_convert_to_spans = MagicMock()
        with patch("azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper.os.remove"):
            with patch("azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper.open", open_mock):
                with patch("azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper._convert_to_spans",
                           mock_convert_to_spans):
                    generate_results_for_labeling_service(
                        predictions_output_file_path,
                        [first_file_name, second_file_name],
                        DataLiterals.NER_DATA_DIR
                    )
        self.assertTrue(open_mock.call_count == 1)
        self.assertEquals(mock_convert_to_spans.call_args_list[0][0][0], predictions_first_file)
        self.assertEquals(mock_convert_to_spans.call_args_list[0][0][1], first_file_name)
        self.assertEquals(mock_convert_to_spans.call_args_list[0][0][2], predictions_output_file_path)
        self.assertEquals(mock_convert_to_spans.call_args_list[1][0][0], predictions_second_file)
        self.assertEquals(mock_convert_to_spans.call_args_list[1][0][1], second_file_name)
        self.assertEquals(mock_convert_to_spans.call_args_list[1][0][2], predictions_output_file_path)

    def test_convert_to_spans_all_O(self):
        predicted_labels = np.full(5, 'O')
        mock_prediction = self.get_mock_prediction_list(predicted_labels)
        mock_test_text = self.get_mock_test_file_text()
        open_mock = mock_open(read_data=mock_test_text)
        mock_file_name = 'ner_datastore/file1.txt'
        with patch("azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper.open", open_mock):
            _convert_to_spans(
                mock_prediction,
                mock_file_name,
                OutputLiterals.PREDICTIONS_TXT_FILE_NAME,
                DataLiterals.NER_DATA_DIR
            )
        self.assertTrue(open_mock.call_count == 2)
        self.assertTrue(open_mock.return_value.write.call_count == 2)
        written_msg = ast.literal_eval(open_mock.return_value.write.call_args_list[0][0][0])
        dataset_path = DataLiterals.DATASTORE_PREFIX + mock_file_name
        self.assertEquals(written_msg['image_url'], dataset_path)
        self.assertEquals(written_msg['label'], [])
        self.assertEquals(written_msg['label_confidence'], [])

    def test_convert_to_spans_one_B_I_set(self):
        predicted_labels = ['O', 'B-PER', 'I-PER', 'I-PER', 'O']
        score_list = np.random.rand(5)
        mock_prediction = self.get_mock_prediction_list(predicted_labels, score_list)
        mock_test_text = self.get_mock_test_file_text()
        open_mock = mock_open(read_data=mock_test_text)
        mock_file_name = 'ner_datastore/file1.txt'
        with patch("azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper.open", open_mock):
            _convert_to_spans(
                mock_prediction,
                mock_file_name,
                OutputLiterals.PREDICTIONS_TXT_FILE_NAME,
                DataLiterals.NER_DATA_DIR
            )
        self.assertTrue(open_mock.call_count == 2)
        self.assertTrue(open_mock.return_value.write.call_count == 2)
        written_msg = ast.literal_eval(open_mock.return_value.write.call_args_list[0][0][0])
        dataset_path = DataLiterals.DATASTORE_PREFIX + mock_file_name
        self.assertEquals(written_msg['image_url'], dataset_path)
        self.assertEquals(written_msg['label'], [{'label': 'PER', 'offsetStart': 9, 'offsetEnd': 20}])
        self.assertEquals(written_msg['label_confidence'], [score_list[1]])

    def test_convert_to_spans_multiple_B_I_set(self):
        predicted_labels = ['B-PER', 'B-PER', 'I-PER', 'I-PER', 'B-PER']
        score_list = np.random.rand(5)
        mock_prediction = self.get_mock_prediction_list(predicted_labels, score_list)
        mock_test_text = self.get_mock_test_file_text()
        open_mock = mock_open(read_data=mock_test_text)
        mock_file_name = 'ner_datastore/file1.txt'
        with patch("azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper.open", open_mock):
            _convert_to_spans(
                mock_prediction,
                mock_file_name,
                OutputLiterals.PREDICTIONS_TXT_FILE_NAME,
                DataLiterals.NER_DATA_DIR
            )
        self.assertTrue(open_mock.call_count == 2)
        self.assertTrue(open_mock.return_value.write.call_count == 2)
        written_msg = ast.literal_eval(open_mock.return_value.write.call_args_list[0][0][0])
        dataset_path = DataLiterals.DATASTORE_PREFIX + mock_file_name
        self.assertEquals(written_msg['image_url'], dataset_path)
        self.assertEquals(written_msg['label'][0], {'label': 'PER', 'offsetStart': 0, 'offsetEnd': 8})
        self.assertEquals(written_msg['label'][1], {'label': 'PER', 'offsetStart': 9, 'offsetEnd': 20})
        self.assertEquals(written_msg['label'][2], {'label': 'PER', 'offsetStart': 20, 'offsetEnd': 24})
        self.assertEquals(written_msg['label_confidence'], [score_list[0], score_list[1], score_list[4]])

    def test_convert_to_spans_I_before_B(self):
        predicted_labels = ['o', 'I-PER', 'B-PER', 'I-PER', 'o']
        score_list = np.random.rand(5)
        mock_prediction = self.get_mock_prediction_list(predicted_labels, score_list)
        mock_test_text = self.get_mock_test_file_text()
        open_mock = mock_open(read_data=mock_test_text)
        mock_file_name = 'ner_datastore/file1.txt'
        with patch("azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper.open", open_mock):
            _convert_to_spans(
                mock_prediction,
                mock_file_name,
                OutputLiterals.PREDICTIONS_TXT_FILE_NAME,
                DataLiterals.NER_DATA_DIR
            )
        self.assertTrue(open_mock.call_count == 2)
        self.assertTrue(open_mock.return_value.write.call_count == 2)
        written_msg = ast.literal_eval(open_mock.return_value.write.call_args_list[0][0][0])
        dataset_path = DataLiterals.DATASTORE_PREFIX + mock_file_name
        self.assertEquals(written_msg['image_url'], dataset_path)
        self.assertEquals(written_msg['label'][0], {'label': 'PER', 'offsetStart': 9, 'offsetEnd': 12})
        self.assertEquals(written_msg['label'][1], {'label': 'PER', 'offsetStart': 13, 'offsetEnd': 20})
        self.assertEquals(written_msg['label_confidence'], [score_list[1], score_list[2]])

    def test_convert_to_spans_labels_not_in_order(self):
        predicted_labels = ['B-PER', 'I-LOC', 'I-PER', 'B-LOC', 'I-LOC']
        score_list = np.random.rand(5)
        mock_prediction = self.get_mock_prediction_list(predicted_labels, score_list)
        mock_test_text = self.get_mock_test_file_text()
        open_mock = mock_open(read_data=mock_test_text)
        mock_file_name = 'ner_datastore/file1.txt'
        with patch("azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper.open", open_mock):
            _convert_to_spans(
                mock_prediction,
                mock_file_name,
                OutputLiterals.PREDICTIONS_TXT_FILE_NAME,
                DataLiterals.NER_DATA_DIR
            )
        self.assertTrue(open_mock.call_count == 2)
        self.assertTrue(open_mock.return_value.write.call_count == 2)
        written_msg = ast.literal_eval(open_mock.return_value.write.call_args_list[0][0][0])
        dataset_path = DataLiterals.DATASTORE_PREFIX + mock_file_name
        self.assertEquals(written_msg['image_url'], dataset_path)
        self.assertEquals(written_msg['label'][0], {'label': 'PER', 'offsetStart': 0, 'offsetEnd': 8})
        self.assertEquals(written_msg['label'][1], {'label': 'LOC', 'offsetStart': 9, 'offsetEnd': 12})
        self.assertEquals(written_msg['label'][2], {'label': 'PER', 'offsetStart': 13, 'offsetEnd': 16})
        self.assertEquals(written_msg['label'][3], {'label': 'LOC', 'offsetStart': 17, 'offsetEnd': 24})
        self.assertEquals(
            written_msg['label_confidence'], [score_list[0], score_list[1], score_list[2], score_list[3]]
        )

    def test_convert_to_spans_labels_not_in_order_with_special_token(self):
        predicted_labels = ['B-PER', 'I-LOC', 'I-PER', 'B-LOC', 'I-LOC']
        score_list = np.random.rand(5)
        mock_prediction = self.get_mock_prediction_list(predicted_labels, score_list, special_token=True)
        mock_test_text = self.get_mock_test_file_text(special_token=True)
        open_mock = mock_open(read_data=mock_test_text)
        mock_file_name = 'ner_datastore/file1.txt'
        with patch("azureml.automl.dnn.nlp.ner.io.read._labeling_data_helper.open", open_mock):
            _convert_to_spans(
                mock_prediction,
                mock_file_name,
                OutputLiterals.PREDICTIONS_TXT_FILE_NAME,
                DataLiterals.NER_DATA_DIR
            )
        self.assertTrue(open_mock.call_count == 2)
        self.assertTrue(open_mock.return_value.write.call_count == 2)
        written_msg = ast.literal_eval(open_mock.return_value.write.call_args_list[0][0][0])
        print(written_msg)
        dataset_path = DataLiterals.DATASTORE_PREFIX + mock_file_name
        self.assertEquals(written_msg['image_url'], dataset_path)
        self.assertEquals(written_msg['label'][0], {'label': 'PER', 'offsetStart': 0, 'offsetEnd': 9})
        self.assertEquals(written_msg['label'][1], {'label': 'LOC', 'offsetStart': 10, 'offsetEnd': 14})
        self.assertEquals(written_msg['label'][2], {'label': 'PER', 'offsetStart': 15, 'offsetEnd': 19})
        self.assertEquals(written_msg['label'][3], {'label': 'LOC', 'offsetStart': 20, 'offsetEnd': 29})
        self.assertEquals(
            written_msg['label_confidence'], [score_list[0], score_list[1], score_list[2], score_list[3]]
        )

    @staticmethod
    def get_mock_prediction_list(predicted_labels, score_list=None, text_list=None, special_token=False):
        # Return a prediction list containing a set of text + predicted label + score
        text_list = ["Nikolaus", "van", "der", "Pas", "told"] if text_list is None else text_list
        if special_token:
            text_list = [token + "\ufffd" for token in text_list]  # \ufffd is what appears by setting errors=replace
        score_list = np.random.rand(5) if score_list is None else score_list

        for i in range(len(text_list)):
            text_list[i] = text_list[i] + " " + predicted_labels[i] + " " + str(score_list[i])

        return text_list

    @staticmethod
    def get_mock_predictions_text(predicted_labels, score_list=None):
        # Return a set of predictions text where each text are separated by '\n'
        text_list = [["Nikolaus", "van", "der", "Pas", "told"], ["a", "news", "briefing", "scientific", "study"]]
        score_list = np.random.rand(2, 5) if score_list is None else score_list

        result_text = ""
        for i in range(len(text_list)):
            for j in range(len(text_list[i])):
                result_text += text_list[i][j] + " " + predicted_labels[i][j] + " " + str(score_list[i][j]) + "\n"
            result_text += "\n"

        return result_text

    @staticmethod
    def get_mock_test_file_text(special_token=False):
        # Return a prediction text containing a set of text
        text_list = ["Nikolaus", "van", "der", "Pas", "told"]
        if special_token:
            text_list = [token + "\ufffd" for token in text_list]
        text = '\n'.join([' '.join(text_list[:-1]), text_list[-1]])
        return text


if __name__ == "__main__":
    unittest.main()

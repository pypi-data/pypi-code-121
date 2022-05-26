# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains dataloader functions for NER."""
from typing import List, Tuple, Dict

import json
import logging
import os

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.automl.core.shared import constants, logging_utilities as log_utils
from azureml.automl.core.shared._diagnostics.automl_error_definitions import DataPathNotFound
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.common._data_utils import (
    load_labeling_data_df
)
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import LabelingDataConversionFailed
from azureml.automl.dnn.nlp.common.constants import DataLiterals, DataLabelingLiterals, Split
from azureml.data import TabularDataset

_logger = logging.getLogger(__name__)


def load_dataset_for_labeling_service(
        dataset: TabularDataset,
        data_dir: str,
        data_filename: str,
        data_split: Split,
) -> Tuple[str, List[str]]:
    """
    Load dataset from Labeling service span format input.

    Labeling service will pass in TabularDataset that includes list of the paths for the actual text files
    and its label in a span format. This spans format data will be converted into CoNLL format (for test dataset,
    we leave out the true labels if given).

    :param dataset: tabular labeled dataset containing paths to text files
    :param data_dir: directory where data should be downloaded
    :param data_filename: filename to save converted dataset
    :param data_split: dataset type label
    :return name of the converted test data file and list of files referenced
    """

    _logger.info(f"Loading {data_split.value} dataset for labeling service")
    text_df = load_labeling_data_df(dataset, data_dir, data_split)

    with log_utils.log_activity(
            _logger,
            activity_name=f"{constants.TelemetryConstants.LABELING_DATA_CONVERSION}_{data_split.value}"
    ):
        try:
            final_conll_path = os.path.join(data_dir, data_filename)
            original_file_paths = []
            processed_input_file_counter = 1

            empty_file_cnt = 0
            seen_non_empty_file = False
            for idx in text_df.index:
                portable_path = text_df[DataLabelingLiterals.PORTABLE_PATH_COLUMN_NAME][idx]
                portable_path = portable_path.lstrip('/')  # remove leading "/"
                original_file_paths.append(portable_path)

                # read the text content
                downloaded_path = os.path.join(data_dir, portable_path)
                with open(downloaded_path, encoding=DataLiterals.ENCODING, errors=DataLiterals.ERRORS) as f:
                    input_text_content = f.read()

                if data_split == Split.test:
                    file_was_empty = _convert_to_conll_no_label(input_text_content=input_text_content,
                                                                output_file_path=final_conll_path,
                                                                at_start=not seen_non_empty_file)
                    if file_was_empty:
                        empty_file_cnt += 1
                    seen_non_empty_file = seen_non_empty_file or not file_was_empty
                else:
                    label_span = text_df[DataLiterals.LABEL_COLUMN][idx]
                    file_was_empty = _convert_to_conll(input_text_content=input_text_content,
                                                       label_objects=label_span,
                                                       output_file_path=final_conll_path,
                                                       at_start=not seen_non_empty_file)
                    if file_was_empty:
                        empty_file_cnt += 1
                    seen_non_empty_file = seen_non_empty_file or not file_was_empty
                processed_input_file_counter += 1
        except Exception as e:
            _logger.warning(f"Error while processing file {processed_input_file_counter} "
                            f"of {len(text_df)} for {data_split.value} dataset.")
            raise DataException._with_error(
                AzureMLError.create(
                    LabelingDataConversionFailed, error_details=str(e), target=f"load_{data_split.value}_dataset")
            )
        _logger.info(f"Finished processing all {len(text_df)} files for {data_split.value} dataset.")
        if empty_file_cnt:
            _logger.warning(f"Found {empty_file_cnt} files being empty for {data_split.value} dataset.")

    return data_filename, original_file_paths


def generate_results_for_labeling_service(
        predictions_file_path: str,
        input_file_paths: List[str],
        data_dir: str
) -> None:
    """
    Generate spans format output from predictions for labeling service

    :param predictions_file_path: predictions file path
    :param input_file_paths: list of test file downloaded paths
    :param data_dir: directory where text data is downloaded
    """
    _logger.info("Generating output for labeling service")

    # Convert predictions in CoNLL format into spans format for labeling service
    with open(predictions_file_path, "r", encoding=DataLiterals.ENCODING, errors=DataLiterals.ERRORS) as f:
        labeled_conll = f.read()

    # Remove original predictions.txt
    os.remove(predictions_file_path)

    # Write converted entry to predictions.txt
    inferencing_results = labeled_conll.split('\n\n')
    # Our validated datasets end with a newline.
    # Strip this for the last line for inferencing scenarios to not create an empty example.
    if inferencing_results[-1].endswith('\n'):
        inferencing_results[-1] = inferencing_results[-1].rstrip('\n')

    for i in range(len(input_file_paths)):
        _logger.info("Processing file {} of {}".format(i + 1, len(input_file_paths)))
        input_conll = inferencing_results[i].split('\n')
        _convert_to_spans(input_conll, input_file_paths[i], predictions_file_path, data_dir)

    _logger.info(f"Finished converting {len(input_file_paths)} text file predictions back to jsonlines format.")


def _convert_to_conll(
    input_text_content: str,
    label_objects: List[Dict[str, int]],
    output_file_path: str,
    at_start: bool
) -> bool:
    """
    Convert input string with label spans into CONLL format with labels

    :param input_text_content: input string to be converted to CONLL format
    :param label_objects: list of label spans.
        Exact format [
            {'label':label1, 'offsetStart':start_index1, 'offsetEnd':end_index1},
            {'label':label2, 'offsetStart':start_index2, 'offsetEnd':end_index2},
            {'label':label3, 'offsetStart':start_index3, 'offsetEnd':end_index3},
            ...
        ]
    :param output_file_path: path of output file
    :param at_start: indicator, whether this file will be written at the start in the output file
    :return: whether the input string converted as an empty string
    """
    conll_output_list = []
    offset_dict = {}

    # map all the offsetStarts to another dict
    for label in label_objects:
        cur_key = label['offsetStart']
        offset_dict[int(cur_key)] = [int(label['offsetEnd']), label['label']]

    offset_dict_keys = list(offset_dict.keys())
    offset_dict_keys.sort()

    start_index = 0
    for offset in offset_dict_keys:
        _tokenize(
            start_index, offset, input_text_content, conll_output_list
        )
        _tokenize(
            offset, offset_dict[offset][0], input_text_content, conll_output_list, offset_dict[offset][1]
        )
        start_index = offset_dict[offset][0]

    # tokenize remaining text
    _tokenize(
        start_index, len(input_text_content), input_text_content, conll_output_list
    )

    # write conll to output file
    with open(output_file_path, "a") as f:
        if not at_start and len(conll_output_list):  # not first file and not empty file
            f.write('\n')
        f.writelines(conll_output_list)  # does not matter if it's empty here

    return len(conll_output_list) == 0


def _convert_to_conll_no_label(
    input_text_content: str,
    output_file_path: str,
    at_start: bool
) -> bool:
    """
    Convert input string to CONLL format without labels

    :param input_text_content: input string to be converted to CONLL format
    :param output_file_path: path of output file
    :param at_start: indicator, whether this file will be written at the start in the output file
    :return: whether the input string converted as an empty string
    """
    conll_output_list = []

    start_index = 0
    # tokenize the text
    _tokenize_exclude_label(start_index, len(input_text_content), input_text_content, conll_output_list)

    # write conll to output file
    with open(output_file_path, "a") as f:
        if not at_start and len(conll_output_list):  # not first file and not empty file
            f.write('\n')
        f.writelines(conll_output_list)  # does not matter if it's empty here

    return len(conll_output_list) == 0


def _convert_to_spans(input_conll, text_file_path, output_file_path, data_dir):
    try:
        input_file_path = os.path.join(data_dir, text_file_path)

        with open(input_file_path, "r", encoding=DataLiterals.ENCODING, errors=DataLiterals.ERRORS) as f:
            input_text = f.read()
    except Exception as e:
        raise DataException._with_error(
            AzureMLError.create(
                DataPathNotFound, target="input_text", dprep_error=e)
        )

    offset_dict = {}
    i = 0
    j = 0
    prev_offset_start = 0
    prev_label_suffix = ''

    for line in input_conll:
        tokens = line.split()
        word = tokens[0]
        label = tokens[1]
        confidence = tokens[2]
        label_prefix = label[0]
        label_suffix = label[2:]
        if label_prefix == 'B':
            offset_dict[i] = [i + len(word), label_suffix, confidence]
            prev_offset_start = i
            prev_confidence = confidence
        elif label_prefix == 'I':
            if prev_label_suffix == label_suffix:
                offset_dict[prev_offset_start] = [i + len(word), label_suffix, prev_confidence]
            else:
                offset_dict[i] = [i + len(word), label_suffix, confidence]
                prev_offset_start = i
                prev_confidence = confidence
        else:
            prev_confidence = None
        prev_label_suffix = label_suffix

        # move index forward by length of the word
        i = i + len(word)
        j = j + len(word)

        while j < len(input_text) and input_text[j] == ' ':
            i = i + 1
            j = j + 1

    label_list = []
    confidence_list = []

    for offset in offset_dict:
        label_list.append({
            'label': str(offset_dict[offset][1]),
            'offsetStart': int(offset),
            'offsetEnd': int(offset_dict[offset][0])
        })
        confidence_list.append(float(offset_dict[offset][2]))

    text_file_full_path = DataLiterals.DATASTORE_PREFIX + text_file_path
    final_result = {
        DataLabelingLiterals.IMAGE_URL: text_file_full_path,
        DataLiterals.LABEL_COLUMN: label_list,
        DataLiterals.LABEL_CONFIDENCE: confidence_list
    }

    with open(output_file_path, "a") as f:
        f.write(json.dumps(final_result))
        f.write('\n')


def _tokenize(start_index, end_index, input_text_content, conll_output_list, tag=None):
    if start_index == end_index:
        return

    # split into tokens based on space
    tokens = input_text_content[start_index:end_index].split()

    if tag is None:
        for token in tokens:
            if token.isalpha():
                conll_output_list.append(token + ' O' + '\n')
            else:
                cur_string = ''
                # special case to handle tokens starting with a digit to handle numbers or dates
                if token[0].isdigit():
                    # check whether the last char is something other than digit then it will be its own token
                    if not token[len(token) - 1].isdigit():
                        conll_output_list.append(token[0:len(token) - 1] + ' O' + '\n')
                        conll_output_list.append(token[len(token) - 1] + ' O' + '\n')
                    # else print the whole number/date together
                    else:
                        conll_output_list.append(token + ' O' + '\n')
                else:
                    index = 0
                    for ch in token:
                        if ('A' <= ch <= 'Z') or ('a' <= ch <= 'z'):
                            cur_string += ch
                        else:
                            # output the alphabetical token so far
                            if len(cur_string) > 0:
                                conll_output_list.append(cur_string + ' O' + '\n')
                                cur_string = ''
                            # special case to handle " ' "
                            if ch == "'":
                                conll_output_list.append(token[index:] + ' O' + '\n')
                                break
                            # every other special character is its own token
                            else:
                                conll_output_list.append(ch + ' O' + '\n')
                        index = index + 1

                    if len(cur_string) > 0:
                        conll_output_list.append(cur_string + ' O' + '\n')
    else:
        conll_output_list.append(tokens[0] + ' B-' + tag + '\n')
        for t_index in range(1, len(tokens)):
            conll_output_list.append(tokens[t_index] + ' I-' + tag + '\n')


def _tokenize_exclude_label(start_index, end_index, input_text_content, conll_output_list):
    if start_index == end_index:
        return

    # split into tokens based on space
    tokens = input_text_content[start_index:end_index].split()

    for token in tokens:
        if token.isalpha():
            conll_output_list.append(token + '\n')
        else:
            cur_string = ''
            # special case to handle tokens starting with a digit to handle numbers or dates
            if token[0].isdigit():
                # check whether the last char is something other than digit then it will be its own token
                if not token[len(token) - 1].isdigit():
                    conll_output_list.append(token[0:len(token) - 1] + '\n')
                    conll_output_list.append(token[len(token) - 1] + '\n')
                # else print the whole number/date together
                else:
                    conll_output_list.append(token + '\n')
            else:
                index = 0
                for ch in token:
                    if ('A' <= ch <= 'Z') or ('a' <= ch <= 'z'):
                        cur_string += ch
                    else:
                        # output the alphabetical token so far
                        if len(cur_string) > 0:
                            conll_output_list.append(cur_string + '\n')
                            cur_string = ''
                        # special case to handle " ' "
                        if ch == "'":
                            conll_output_list.append(token[index:] + '\n')
                            break
                        # every other special character is its own token
                        else:
                            conll_output_list.append(ch + '\n')
                    index = index + 1

                if len(cur_string) > 0:
                    conll_output_list.append(cur_string + '\n')

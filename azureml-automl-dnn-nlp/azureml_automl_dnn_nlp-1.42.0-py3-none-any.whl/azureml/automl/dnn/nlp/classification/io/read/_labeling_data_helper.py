# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Contains dataloader functions for NER."""

import json
import logging
import os
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.automl.core.shared import constants, logging_utilities as log_utils
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.common._data_utils import (
    load_labeling_data_df
)
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import LabelingDataConversionFailed
from azureml.automl.dnn.nlp.common.constants import DataLabelingLiterals, DataLiterals, OutputLiterals, Split
from azureml.data import TabularDataset

_logger = logging.getLogger(__name__)


def load_datasets_for_labeling_service(
        train_dataset: TabularDataset,
        validation_dataset: Optional[TabularDataset],
        data_dir: str,
        include_label: bool
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    """Load classification dataset from Labeling service.

    :param train_dataset: labeled tabular train dataset containing paths to text files
    :param validation_dataset: labeled tabular validation dataset containing paths to text files
    :param data_dir: Directory to download the text files into
    :param include_label: Whether to include label column
    :return: training dataframe, validation dataframe
    """
    train_df, _ = load_dataset_for_labeling_service(
        train_dataset,
        data_dir,
        include_label,
        Split.train
    )
    validation_df = None
    if validation_dataset:
        validation_df, _ = load_dataset_for_labeling_service(
            validation_dataset,
            data_dir,
            include_label,
            Split.valid
        )
    return train_df, validation_df


def load_dataset_for_labeling_service(
        dataset: TabularDataset,
        data_dir: str,
        include_label: bool,
        data_split: Split
) -> Tuple[str, List[str]]:
    """
    Load classification dataset from Labeling service.

    Labeling service will pass in TabularDataset that includes list of the paths for the actual text files
    and its label in a span format. This spans format data will be converted into tabular format that we support
    for our text classification tasks.

    :param dataset: tabular labeled dataset containing paths to text files
    :param data_dir: Directory to download the text files into
    :param include_label: Whether to include label column
    :param data_split: Label for data split
    :return name of the converted data file and list of files referenced
    """
    _logger.info(f"Loading {data_split.value} dataset for labeling service")
    text_df = load_labeling_data_df(dataset, data_dir, data_split)

    with log_utils.log_activity(
            _logger,
            activity_name=f"{constants.TelemetryConstants.LABELING_DATA_CONVERSION}_{data_split.value}"
    ):
        data_dict = dict()
        original_file_paths = []
        processed_input_file_counter = 1
        try:
            for i in text_df.index:
                portable_path = text_df[DataLabelingLiterals.PORTABLE_PATH_COLUMN_NAME][i]
                # portable path example: "/textcontainer/wnut17_ner/file1098.txt"
                portable_path = portable_path.lstrip('/')  # remove leading "/"
                original_file_paths.append(portable_path)

                if include_label:
                    label = text_df[DataLiterals.LABEL_COLUMN][i]
                else:
                    label = None

                # read the text content
                downloaded_path = os.path.join(data_dir, portable_path)
                data_dict[processed_input_file_counter - 1] = _convert_to_dict_entry(
                    downloaded_path, label, include_label
                )
                processed_input_file_counter += 1
        except Exception as e:
            _logger.warning(f"Error while processing file {processed_input_file_counter} "
                            f"of {len(text_df)} for {data_split.value} dataset.")
            raise DataException._with_error(
                AzureMLError.create(
                    LabelingDataConversionFailed, error_details=str(e), target=f"load_{data_split.value}_dataset")
            )

        data_df = pd.DataFrame.from_dict(data_dict, orient='index')
    return data_df, original_file_paths


def _convert_to_dict_entry(input_file_path, label_objects, include_label):
    # read the text content
    with open(input_file_path, encoding=DataLiterals.ENCODING, errors=DataLiterals.ERRORS) as f:
        input_text_content = f.read()

    # create dictionary entry
    dict_entry = dict()
    dict_entry[DataLiterals.TEXT_COLUMN] = input_text_content
    if include_label:
        dict_entry[DataLiterals.LABEL_COLUMN] = str(label_objects)
    return dict_entry


def format_multilabel_predicted_df(predicted_df: pd.DataFrame, label_column_name: str):
    # label column "a,b,c" to ["a", "b", "c"]
    # label confidence "0.1,0.2,0.3" to [0.1, 0.2, 0.3]
    predicted_df[label_column_name] = predicted_df[label_column_name].str.split(",")
    predicted_df[DataLiterals.LABEL_CONFIDENCE] = \
        predicted_df[DataLiterals.LABEL_CONFIDENCE].str.split(",").apply(lambda x: [float(i) for i in x])

    return predicted_df


def generate_predictions_output_for_labeling_service(
        predicted_df: pd.DataFrame,
        input_file_paths: List[str],
        output_file_name: str,
        label_column_name: str
) -> None:
    """
    Generate spans format output from predictions for labeling service

    :param predicted_df: predictions
    :param input_file_paths: list of test file downloaded paths
    :param output_file_name: name of the file to write the results to
    :param label_column_name: name of the label column from predicted_df
    """
    _logger.info("Generating output for labeling service")

    os.makedirs(OutputLiterals.OUTPUT_DIR, exist_ok=True)
    predictions_output_path = os.path.join(OutputLiterals.OUTPUT_DIR, output_file_name)

    # write converted entry to predictions.txt
    with open(predictions_output_path, "a") as f:
        for i in range(len(input_file_paths)):
            label_confidence = predicted_df[DataLiterals.LABEL_CONFIDENCE][i]
            if isinstance(label_confidence, np.floating):
                label_confidence = float(label_confidence)
            text_file_full_path = DataLiterals.DATASTORE_PREFIX + input_file_paths[i]
            result_entry = {
                DataLabelingLiterals.IMAGE_URL: text_file_full_path,
                DataLiterals.LABEL_COLUMN: predicted_df[label_column_name][i],
                DataLiterals.LABEL_CONFIDENCE: label_confidence
            }
            f.write(json.dumps(result_entry))
            f.write('\n')

    _logger.info("Successfully generated output for labeling service")

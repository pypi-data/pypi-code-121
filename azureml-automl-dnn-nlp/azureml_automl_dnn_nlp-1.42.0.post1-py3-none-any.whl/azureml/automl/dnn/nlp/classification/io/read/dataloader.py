# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Contains dataloader functions for the classification tasks."""

import logging
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from torch.utils.data import Dataset as PyTorchDataset
from transformers import AutoTokenizer

from azureml.automl.core.shared import constants, logging_utilities as log_utils
from azureml.automl.dnn.nlp.classification.io.read._labeling_data_helper import load_datasets_for_labeling_service
from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import (
    PyTorchDatasetWrapper,
    PyTorchMulticlassDatasetWrapper
)
from azureml.automl.dnn.nlp.classification.io.read.read_utils import get_y_transformer
from azureml.automl.dnn.nlp.classification.multiclass.utils import get_max_seq_length
from azureml.automl.dnn.nlp.common._data_utils import get_dataset
from azureml.automl.dnn.nlp.common.constants import DataLiterals, Split
from azureml.automl.dnn.nlp.validation.multiclass_validator import NLPMulticlassDataValidator
from azureml.automl.dnn.nlp.validation.multilabel_validator import NLPMultilabelDataValidator
from azureml.core.workspace import Workspace

_logger = logging.getLogger(__name__)


def load_and_validate_multiclass_dataset(
        workspace: Workspace,
        data_dir: str,
        label_column_name: str,
        tokenizer: AutoTokenizer,
        automl_settings: Dict[str, Any],
        mltable_data_json: Optional[str] = None,
        is_labeling_run: bool = False,
        enable_long_range_text: bool = True,
) -> Tuple[PyTorchDataset,
           PyTorchDataset,
           np.ndarray,
           np.ndarray,
           Optional[np.ndarray],
           int]:
    """To get the training_set, validation_set and various label lists to generate metrics

    :param workspace: workspace where dataset is stored in blob
    :param data_dir: Location to download file dataset into
    :param label_column_name: Name/title of the label column
    :param tokenizer: tokenizer to be used to tokenize the data
    :param automl_settings: dictionary with automl settings
    :param mltable_data_json: mltable data json containing location of data
    :param is_labeling_run: Whether the experiment is from labeling service
    :param enable_long_range_text: param to enable long range text calculation. True by default.

    :return: training dataset, validation dataset, all class labels, train labels, y-validation, max sequence length
    """
    with log_utils.log_activity(
            _logger,
            activity_name=constants.TelemetryConstants.DATA_PREPARATION
    ):
        train_df, validation_df = _load_dataframe(
            workspace, data_dir, automl_settings, mltable_data_json, is_labeling_run
        )

        # Data validation
        validator = NLPMulticlassDataValidator()
        validator.validate(label_column_name, train_df, validation_df)

        _logger.info(f"Input training dataset detected with shape {train_df.shape}.")
        max_seq_length = get_max_seq_length(train_df, tokenizer, label_column_name, enable_long_range_text)
        # Let's sort it for determinism
        train_label_list = np.sort(pd.unique(train_df[label_column_name]))
        label_list = train_label_list
        validation_set = None
        y_val = None
        if validation_df is not None:
            _logger.info(f"Input validation dataset detected with shape {validation_df.shape}.")
            y_val = validation_df[label_column_name].values
            validation_df.drop(columns=label_column_name, inplace=True)
            val_label_list = pd.unique(y_val)
            label_list = np.union1d(train_label_list, val_label_list)
            validation_set = PyTorchMulticlassDatasetWrapper(validation_df, train_label_list, tokenizer,
                                                             max_seq_length, label_column_name=None)
        training_set = PyTorchMulticlassDatasetWrapper(train_df, train_label_list, tokenizer,
                                                       max_seq_length, label_column_name=label_column_name)

    return training_set, validation_set, label_list, train_label_list, y_val, max_seq_length


def load_and_validate_multilabel_dataset(
        workspace: Workspace,
        data_dir: str,
        label_column_name: str,
        automl_settings: Dict[str, Any],
        mltable_data_json: Optional[str] = None,
        dataset_language: Optional[str] = 'eng',
        is_labeling_run: bool = False,
) -> Tuple[PyTorchDataset, PyTorchDataset, int, MultiLabelBinarizer]:
    """To get the training_set, validation_set and num_label_columns for multilabel scenario

    :param workspace: Workspace where dataset is stored in blob
    :param data_dir: Location to download text files into
    :param label_column_name: Name/title of the label column
    :param automl_settings: dictionary with automl settings
    :param mltable_data_json: mltable data json containing location of data
    :param dataset_language: language code of dataset
    :param is_labeling_run: Whether the experiment is from labeling service
    :return: training dataset, validation dataset, num of label columns, y_transformer
    """

    train_df, valid_df = _load_dataframe(
        workspace, data_dir, automl_settings, mltable_data_json, is_labeling_run
    )

    validator = NLPMultilabelDataValidator()
    validator.validate(label_col_name=label_column_name, train_data=train_df, valid_data=valid_df)

    # Fit a MultiLabelBinarizer on the label column so that we can transform labels column
    y_transformer = get_y_transformer(train_df, valid_df, label_column_name)
    num_label_cols = len(y_transformer.classes_)

    # Convert dataset into a format ingestible by model
    _logger.info(f"Input training dataset detected with shape {train_df.shape}.")
    training_set = PyTorchDatasetWrapper(train_df, dataset_language, label_column_name=label_column_name,
                                         y_transformer=y_transformer)
    validation_set = None
    if valid_df is not None:
        _logger.info(f"Input validation dataset detected with shape {valid_df.shape}.")
        validation_set = PyTorchDatasetWrapper(valid_df, dataset_language,
                                               label_column_name=label_column_name,
                                               y_transformer=y_transformer)
    return training_set, validation_set, num_label_cols, y_transformer


def _load_dataframe(
        workspace: Workspace,
        data_dir: str,
        automl_settings: Dict[str, Any],
        mltable_data_json: Optional[str] = None,
        is_labeling_run: bool = False,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    load train and valid dataframe from either dataset id or mltable data json
    """
    dataset_id = automl_settings.get(DataLiterals.DATASET_ID, None)
    validation_dataset_id = automl_settings.get(DataLiterals.VALIDATION_DATASET_ID, None)
    train_dataset = get_dataset(workspace, Split.train, dataset_id, mltable_data_json)
    validation_dataset = get_dataset(workspace, Split.valid, validation_dataset_id, mltable_data_json)

    if is_labeling_run:
        train_df, validation_df = load_datasets_for_labeling_service(
            train_dataset,
            validation_dataset,
            data_dir,
            include_label=True
        )
    else:
        train_df = train_dataset.to_pandas_dataframe()
        validation_df = None
        if validation_dataset:
            validation_df = validation_dataset.to_pandas_dataframe()

    return train_df, validation_df

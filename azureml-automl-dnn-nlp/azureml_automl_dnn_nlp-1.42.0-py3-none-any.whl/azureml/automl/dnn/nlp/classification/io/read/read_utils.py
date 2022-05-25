# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Utility functions to load the final model and y_transformer during inferencing"""

import logging
import ast
import os
import pandas as pd
import pickle
from sklearn.preprocessing import MultiLabelBinarizer
from typing import Optional

from azureml.automl.dnn.nlp.common.constants import OutputLiterals
from azureml.automl.dnn.nlp.classification.multilabel.model_wrapper import ModelWrapper
from azureml.core.run import Run


_logger = logging.getLogger(__name__)


def load_model_wrapper(run_object: Run, artifacts_dir: Optional[str] = None) -> ModelWrapper:
    """Function to load model (in form of model wrapper) from the training run

    :param run_object: Run object
    :param artifacts_dir: artifacts directory
    :return: model wrapper containing pytorch mode, tokenizer, y_transformer
    """
    _logger.info("Loading model from artifacts")

    if artifacts_dir is None:
        artifacts_dir = OutputLiterals.OUTPUT_DIR

    run_object.download_file(os.path.join(artifacts_dir, OutputLiterals.MODEL_FILE_NAME),
                             output_file_path=OutputLiterals.MODEL_FILE_NAME)

    _logger.info("Finished loading model from training output")

    with open(OutputLiterals.MODEL_FILE_NAME, "rb") as f:
        model = pickle.load(f)
    return model


def get_y_transformer(
    train_df: pd.DataFrame,
    val_df: Optional[pd.DataFrame],
    label_column_name: str
) -> MultiLabelBinarizer:
    """
    Obtain labels transformer

    :param train_df: Training DataFrame
    :param val_df: Validation DataFrame
    :param label_column_name: Name/title of the label column
    :return: label transformer
    """
    # Combine both dataframes if val_df exists
    if val_df is not None:
        combined_df = pd.concat([train_df, val_df])
    else:
        combined_df = train_df

    # Get combined label column
    combined_label_col = combined_df[label_column_name].apply(ast.literal_eval)
    combined_label_col = [[str(x) for x in item] for item in combined_label_col]

    y_transformer = MultiLabelBinarizer(sparse_output=True)
    y_transformer.fit(combined_label_col)

    return y_transformer

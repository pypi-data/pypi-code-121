# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Utils for reading input data."""

import json
import logging
import os
from typing import Optional

import azureml.dataprep as dprep
import pandas as pd
from azureml.dataprep.api.functions import get_portable_path

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml.automl.core.dataset_utilities import get_dataset_from_mltable_data_json
from azureml.automl.core.shared import constants, logging_utilities as log_utils
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import LabelingDataDownloadFailed, MissingDataset
from azureml.automl.dnn.nlp.common.constants import DataLabelingLiterals, Split, ValidationLiterals
from azureml.core import Dataset as AmlDataset
from azureml.core.workspace import Workspace
from azureml.data import TabularDataset
from azureml.data.abstract_dataset import AbstractDataset

_logger = logging.getLogger(__name__)


def get_dataset(
        workspace: Workspace,
        data_split: Split,
        dataset_id: str,
        mltable_data_json: Optional[str] = None,
        mltable_uri: Optional[str] = None
) -> AbstractDataset:
    """
    get dataset from either dataset id or mltable uri

    :param workspace: workspace to retrieve dataset from
    :param data_split: Label for data split
    :param dataset_id: dataset id to retrieve
    :param mltable_data_json: mltable data json containing location of data
    :param mltable_uri: mltable uri
    :return: dataset
    """
    if mltable_data_json is not None:
        return get_dataset_by_mltable_data_json(workspace, mltable_data_json, data_split)
    elif mltable_uri is not None:
        return AbstractDataset._load(mltable_uri, workspace)
    else:
        return get_dataset_by_id(workspace, dataset_id, data_split)


def get_dataset_by_id(workspace: Workspace, dataset_id: str, data_split: Split) -> AbstractDataset:
    """
    get dataset based on dataset id

    :param dataset_id: dataset id to retrieve
    :param data_split: Label for data split
    :param workspace: workspace to retrieve dataset from
    :return: dataset
    """
    if dataset_id is None or (hasattr(dataset_id, "__len__") and len(dataset_id) == 0):
        raise DataException._with_error(
            AzureMLError.create(
                MissingDataset,
                split_type=data_split.value.capitalize(),
                info_link=ValidationLiterals.DATA_PREPARATION_DOC_LINK,
                target=ValidationLiterals.DATA_EXCEPTION_TARGET
            )
        )

    with log_utils.log_activity(
            _logger,
            activity_name=f"{constants.TelemetryConstants.DATA_FETCH}_{data_split.value}"
    ):
        ds = AmlDataset.get_by_id(workspace, dataset_id)
        _logger.info("Fetched {} data. Type: {}".format(data_split.value, type(ds)))
    return ds


def get_dataset_by_mltable_data_json(
        workspace: Workspace,
        mltable_data_json: str,
        data_split: Split,
) -> AbstractDataset:
    """
    get dataset based on mltable data json

    :param workspace: workspace to retrieve dataset from
    :param mltable_data_json: MLTable data json containing data URI
    :param data_split: Label for data split
    :return: dataset
    """
    with log_utils.log_activity(
            _logger,
            activity_name=f"{constants.TelemetryConstants.DATA_FETCH}_{data_split.value}"
    ):
        data_obj = json.loads(mltable_data_json)
        dataset = None
        if data_split == Split.train:
            dataset = get_dataset_from_mltable_data_json(workspace, data_obj, constants.MLTableDataLabel.TrainData)
        elif data_split == Split.valid:
            dataset = get_dataset_from_mltable_data_json(workspace, data_obj, constants.MLTableDataLabel.ValidData)
        elif data_split == Split.test:
            dataset = get_dataset_from_mltable_data_json(workspace, data_obj, constants.MLTableDataLabel.TestData)
        if dataset is None:
            raise DataException._with_error(
                AzureMLError.create(
                    MissingDataset,
                    split_type=data_split.value.capitalize(),
                    info_link=ValidationLiterals.DATA_PREPARATION_DOC_LINK,
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )
        _logger.info("Fetched {} data. Type: {}".format(data_split.value, type(dataset)))
    return dataset


def get_dataframe_from_dataset_id(
        workspace: Workspace,
        dataset_id: str,
        data_split: Split
) -> pd.DataFrame:
    """
    Get the train and val dataframes using the train and val dataset ids and the user's workspace

    :param workspace: workspace where dataset is stored in blob
    :param dataset_id: Unique identifier to fetch dataset from datastore
    :param data_split: Label for data split
    :return: dataframe
    """
    ds = get_dataset_by_id(workspace, dataset_id, data_split)
    df = ds.to_pandas_dataframe()
    return df


def is_labeled_dataset(ds: AmlDataset) -> bool:
    """Check if the dataset is a labeled dataset. In the current approach, we rely on the presence of
    certain properties to check for labeled dataset.

    :param ds: Aml Dataset object
    :type ds: TabularDataset or TabularDataset (Labeled)
    :return: Labeled dataset or not
    :rtype: bool
    """
    return DataLabelingLiterals.IMAGE_COLUMN_PROPERTY in ds._properties


def load_labeling_data_df(
        dataset: TabularDataset,
        data_dir: str,
        data_split: Split,
) -> pd.DataFrame:
    """
    Get data frame from text url based TabularDataset

    Labeling service will pass in TabularDataset that includes list of the paths for the actual text files
    and its label. This spans format data will be converted into correct format for each task later.

    :param dataset: tabular labeled dataset containing paths to text files
    :param data_dir: directory where data should be downloaded
    :param data_split: dataset type label
    :return pandas dataframe
    """
    download_text_files_from_path_column(dataset, data_dir, data_split)

    # Adding a column that returns portable path
    # Example: "image_url":"AmlDatastore://textcontainer/wnut17_ner/file1098.txt"
    # portable path will be "/textcontainer/wnut17_ner/file1098.txt"
    # which is combination of datastore name and resource_identifier
    _logger.info(f"Convert to dataframe containing text path for {data_split.value} data")
    dflow = dataset._dataflow.add_column(
        get_portable_path(dprep.col(DataLabelingLiterals.IMAGE_URL)),
        DataLabelingLiterals.PORTABLE_PATH_COLUMN_NAME,
        DataLabelingLiterals.IMAGE_URL
    )
    text_df = dflow.to_pandas_dataframe(extended_types=True)
    return text_df


def download_file_dataset(dataset: TabularDataset, data_split: Split, data_dir: str, overwrite: bool = True) -> str:
    """
    load given dataset to data path and return the name of the file in reference

    :param dataset: file dataset containing text
    :param data_split: Label for data split
    :param data_dir: directory where data should be downloaded
    :param overwrite: whether existing file can be overwritten
    :return: file name related to the dataset
    """
    _logger.info(f"Downloading file dataset for: {data_split.value} dataset")

    # to_path() returns format ["/filename.txt"], need to strip the "/"
    file_name = dataset.to_path()[0][1:]

    # Download data to ner_dir
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    dataset.download(target_path=data_dir, overwrite=overwrite)

    return file_name


def download_text_files_from_path_column(
        ds: AmlDataset,
        data_dir: str,
        data_label: Split,
        file_path_column: str = DataLabelingLiterals.IMAGE_URL
) -> None:
    """Download text files for NLP tasks

    :param ds: AML Dataset object
    :param data_dir: directory where data should be downloaded
    :param data_label: Label for data split
    :param file_path_column: Column that contains file path to download
    """
    with log_utils.log_activity(
            _logger,
            activity_name=f"{constants.TelemetryConstants.LABELING_DATA_DOWNLOAD}_{data_label.value}"
    ):
        try:
            if is_labeled_dataset(ds):
                ds._dataflow.write_streams(file_path_column, dprep.LocalFileOutput(data_dir)).run_local()
            else:  # TabularDataset
                ds.download(file_path_column, data_dir, overwrite=True)
        except Exception as e:
            raise DataException._with_error(
                AzureMLError.create(
                    LabelingDataDownloadFailed, error_details=str(e), target=f"download_{data_label.value}_dataset")
            )

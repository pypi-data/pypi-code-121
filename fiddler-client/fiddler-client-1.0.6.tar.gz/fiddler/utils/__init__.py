import copy
import logging
from typing import Dict, List

import pandas as pd

from .. import constants
from ..core_objects import Column, DatasetInfo, DataType, ModelInfo
from .pandas import is_datetime, try_series_retype

LOG = logging.getLogger(__name__)
pd.set_option('mode.chained_assignment', None)


def df_from_json_rows(
    dataset_rows_json: List[dict],
    dataset_info: DatasetInfo,
    include_fiddler_id: bool = False,
) -> pd.DataFrame:
    """Converts deserialized JSON into a pandas DataFrame according to a
        DatasetInfo object.

    If `include_fiddler_id` is true, we assume there is an extra column at
    the zeroth position containing the fiddler ID.
    """
    column_names = dataset_info.get_column_names()
    if include_fiddler_id:
        column_names.insert(0, constants.DATASET_FIDDLER_ID)
    if include_fiddler_id:
        dataset_info = copy.deepcopy(dataset_info)
        dataset_info.columns.insert(
            0, Column(constants.DATASET_FIDDLER_ID, DataType.INTEGER)
        )
    df = pd.DataFrame(dataset_rows_json, columns=dataset_info.get_column_names())
    for column_name in df:
        dtype = dataset_info[column_name].get_pandas_dtype()
        df[column_name] = try_series_retype(df[column_name], dtype)
    return df


def retype_df_for_model(df: pd.DataFrame, model_info: ModelInfo) -> pd.DataFrame:
    all_columns = (
        model_info.inputs
        if model_info.targets is None
        else model_info.inputs + model_info.targets
    )
    for column in all_columns:
        if column.name in df:
            df[column.name] = try_series_retype(
                df[column.name], column.get_pandas_dtype()
            )
    return df


def cast_input_data(data, model_info, fast_fail=True):
    """
    :param data: dictionary or pandas dataframe. Data we will cast with respect to the model info types
    :param model_info: info for the model from ModelInfo.
    :param fast_fail: Bool determining if violations throw error, or are ignored

    :return:
    """
    columns = model_info.inputs + model_info.targets + model_info.outputs
    col_mapping = {col.name: col.data_type.value for col in columns}
    possible_values_mapping = {col.name: col.possible_values for col in columns}
    is_dic = False
    if isinstance(data, dict):
        # publish_event is a dictionary
        data = pd.DataFrame.from_dict([data])
        is_dic = True
    for col in data.columns:
        if col in col_mapping.keys():
            col_type = col_mapping[col]
            if col_type == DataType.INTEGER.value:
                cast_type = int
            elif col_type == DataType.FLOAT.value:
                cast_type = float
            elif col_type == DataType.BOOLEAN.value:
                cast_type = bool
            else:
                # for category and string
                cast_type = str
            try:
                data.loc[:, col] = data.loc[:, col].astype(cast_type)
            except ValueError:
                if fast_fail:
                    raise TypeError(
                        f'Type casting failed for variable {col}. '
                        f'Model requires values to be {cast_type}.'
                    )
            if fast_fail:
                if col_type in [DataType.CATEGORY.value, DataType.BOOLEAN.value]:
                    if not data[col].values[0] in possible_values_mapping[col]:
                        raise ValueError(
                            f'Type casting failed for variable {col}. '
                            f'Model requires values to be in {possible_values_mapping[col]}.'
                            f' But found "{data[col].values[0]}" of type {type(data[col].values[0])}'
                        )
    if is_dic:
        data = data.to_dict(orient='records')[0]
    return data


class ColorLogger:

    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    def _log(self, message, color):
        print(f'{color}{message}{self.WHITE}')

    def info(self, message):
        self._log(message, self.BLUE)

    def success(self, message):
        self._log(message, self.GREEN)

    def error(self, message):
        self._log(message, self.RED)

    def warn(self, message):
        self._log(message, self.YELLOW)

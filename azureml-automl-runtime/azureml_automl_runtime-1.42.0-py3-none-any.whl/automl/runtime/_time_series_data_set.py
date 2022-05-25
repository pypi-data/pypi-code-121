# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The class representing the lightweight data structure replacing TimeSeriesDataFrame."""
from typing import Any, Dict, List, Optional, Set, Union, cast

import copy
import uuid
import warnings

from math import floor
from warnings import warn

import numpy as np
import pandas as pd

from pandas.core.groupby import DataFrameGroupBy
from pandas.tseries import offsets
from pandas.tseries.frequencies import to_offset

from azureml._common._error_definition.azureml_error import AzureMLError
from azureml._common._error_definition.user_error import ArgumentBlankOrEmpty
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared._diagnostics.error_strings import AutoMLErrorStrings
from azureml.automl.core.shared._diagnostics.validation import Validation
from azureml.automl.core.shared.constants import (
    TimeSeries, TimeSeriesInternal, TimeSeriesWebLinks)
from azureml.automl.core.shared.exceptions import ClientException
from azureml.automl.core.shared.forecasting_exception import (
    ForecastingConfigException,
    ForecastingDataException)
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    BothYandTargetProvidedToTsdf,
    DictCanNotBeConvertedToDf,
    FreqByGrainWrongType,
    GrainContainsEmptyValues,
    IncompatibleColumnsError,
    IncompatibleIndexError,
    MissingColumnsInData,
    TargetAndExtractColumnsAreNone,
    TimeseriesDfColumnTypeNotSupported,
    TimeseriesDfColValueNotEqualAcrossOrigin,
    TimeseriesDfDuplicatedIndex,
    TimeseriesDfFrequencyNotConsistent,
    TimeseriesDfFrequencyNotConsistentGrain,
    TimeseriesDfInvalidValTmIdxWrongType,
    TimeseriesDfMissingColumn,
    TimeseriesDfWrongTypeOfTimeColumn,
    TimeseriesDfWrongTypeOfValueColumn
)
from azureml.automl.core.shared.types import GrainType
from azureml.automl.runtime.column_purpose_detection import _time_series_column_helper
from azureml.automl.runtime.shared.forecasting_utils import (
    _range,
    grain_level_to_dict)
from azureml.automl.runtime.shared.forecasting_verify import ALLOWED_TIME_COLUMN_TYPES,\
    is_datetime_like, is_iterable_but_not_string


class TimeSeriesDataSet(object):
    """
    The lightweight container class for the time series data sets.

    **Note:** This class will not copy the data frame, but will set its index to
    [time_column_name, time_series_id_column_names, origin_time_column_name].
    :param data: pandas data frame with the data.
    :type data: pd.DataFrame
    :param time_column_name: The name of a time column.
    :type time_column_name: str
    :param time_series_id_column_names: The time series ID columns names.
    :type time_series_id_column_names: str, list(str) or None
    :param origin_time_column_name: The origin time column name.
    :type origin_time_column_name: str or None
    :param target_column_name: The name of a target column.
    :type target_column_name: str or None
    :param group_column_names: The group column names.
    :type group_column_names: str, list(str) or None
    :param validate: Validate the data while cteating the time series data set.
    :type validate: bool
    :param copy: If set to true, the data frame will be copied.
    :type copy: bool
    """

    def __init__(self, data: Union[Dict[str, Any], pd.DataFrame],
                 time_column_name: str,
                 time_series_id_column_names: Optional[List[str]] = None,
                 origin_time_column_name: Optional[str] = None,
                 target_column_name: Optional[str] = None,
                 group_column_names: Optional[List[str]] = None,
                 validate: bool = False,
                 copy: bool = False) -> None:
        """
        The lightweight container class for the time series data sets.

        **Note:** This class will not copy the data frame, but will set its index to
        [time_column_name, time_series_id_column_names, origin_time_column_name] if
        copy is set to false. Data frame may be damaged if the exception was raised.
        :param data: pandas data frame with the data.
        :type data: pd.DataFrame
        :param time_column_name: The name of a time column.
        :type time_column_name: str
        :param time_series_id_column_names: The time series ID columns names.
        :type time_series_id_column_names: str, list(str) or None
        :param origin_time_column_name: The origin time column name.
        :type origin_time_column_name: str or None
        :param target_column_name: The name of a target column.
        :type target_column_name: str or None
        :param group_column_names: The group column names.
        :type group_column_names: str, list(str) or None
        :param validate: Validate the data while cteating the time series data set.
        :type validate: bool
        :param copy: If set to true, the data frame will be copied. This option does not change the
                     behavior if data is a dictionary.
        :type copy: bool
        """
        # Backward compatibility.
        if copy and isinstance(data, pd.DataFrame):
            data = data.copy(deep=True)
        time_series_id_column_names = self._to_list_safe(time_series_id_column_names)
        group_column_names = self._to_list_safe(group_column_names)
        if isinstance(data, dict):
            try:
                data = pd.DataFrame(data)
            except BaseException:
                raise ClientException._with_error(
                    AzureMLError.create(
                        DictCanNotBeConvertedToDf, target='data',
                        reference_code=ReferenceCodes._TSDS_DICT_NOT_CONVERTIBLE_TO_DF
                    ))
        # Obligatory pre validate the data
        self._pre_validate(
            data, time_column_name, time_series_id_column_names,
            origin_time_column_name, target_column_name,
            group_column_names)
        self._time_column_name = time_column_name
        self._time_series_id_column_names = time_series_id_column_names
        self._origin_time_column_name = origin_time_column_name
        self._target_column_name = target_column_name
        self._group_column_names = group_column_names
        index = [time_column_name] + self._time_series_id_column_names
        if self._origin_time_column_name:
            index.append(self._origin_time_column_name)

        self._data = self._reindex_dataframe(data, index, validate)
        if validate:
            self._validate()

    def _reindex_dataframe(self, data: pd.DataFrame, index: List[str], validate: bool) -> pd.DataFrame:
        """
        Set the correct index for the data frame.

        :param data: The input data frame.
        :param index: The time series index.
        :param validate: If set to false and the data frame has correct index,
                         it will not be dropped and converted to datetime.
        :return: The data frame with correct index.
        """
        if set(index) == set(data.index.names) and len(index) == len(data.index.names) and not validate:
            return data
        # Make sure, that we do not have special columns in the index.
        index_and_columns = set(data.index.names).intersection(set(data.columns))
        rename_back_dict = {}
        if data.index.names == [None] or len(index_and_columns):
            # Check if the index, which has the same name as a column will be present in
            # new index.
            if index_and_columns and index_and_columns.issubset(set(index)):
                # We can keep the columns, but we need to rename it temporary to avoid
                # conflict when we will call reset_index.
                reame_dict = {}
                for col in index_and_columns:
                    new_name = "{}_{}".format(str(col), uuid.uuid1())
                    reame_dict[col] = new_name
                    rename_back_dict[new_name] = col
                # Rename columns so it will be safe to reset index.
                data.rename(reame_dict, axis=1, inplace=True)
                data.reset_index(inplace=True, drop=False)
            else:
                # index has some columns, with conflicting names, which will not get to
                # new index.
                data.reset_index(inplace=True, drop=True)
        else:
            data.reset_index(inplace=True, drop=False)

        # Make sure that origin column names and time column names are
        # represented by date times.
        data = _time_series_column_helper.convert_to_datetime(data, self.time_column_name)
        if self.origin_time_column_name:
            data = _time_series_column_helper.convert_to_datetime(data, self.origin_time_column_name)
        if data[self.time_column_name].isnull().any():
            data = data.dropna(subset=[self.time_column_name], inplace=False)

        data.set_index(index, inplace=True)
        data.rename(rename_back_dict, axis=1, inplace=True)
        return data

    @property
    def time_column_name(self) -> str:
        """The name of a time column."""
        return self._time_column_name

    @property
    def time_series_id_column_names(self) -> List[str]:
        """The time series ID columns names."""
        return self._time_series_id_column_names

    @property
    def origin_time_column_name(self) -> Optional[str]:
        """The origin time column name."""
        return self._origin_time_column_name

    @property
    def target_column_name(self) -> Optional[str]:
        """The name of a target column."""
        return self._target_column_name

    @property
    def group_column_names(self) -> List[str]:
        """Return the group column names."""
        return self._group_column_names

    @property
    def data(self) -> pd.DataFrame:
        """Pandas data frame with the data."""
        return self._data

    @property
    def time_index(self) -> pd.DatetimeIndex:
        """Return the datetime index of a data frame."""
        return self.data.index.get_level_values(self.time_column_name)

    def _to_list_safe(self, val: Optional[Any]) -> List[Any]:
        """
        Convert value to a list, containig this value, if val is list, it is not changed.

        :param val: Val to be boxed to list.
        :return: The list of values or None.
        """
        if val is None:
            return []
        if not isinstance(val, list):
            return [val]
        return val

    def _pre_validate(
            self, data: pd.DataFrame,
            time_column_name: str,
            time_series_id_column_names: Optional[List[str]],
            origin_time_column_name: Optional[str] = None,
            target_column_name: Optional[str] = None,
            group_column_names: Optional[List[str]] = None) -> None:
        """
        Obligatory pre validation of data to show informative error messages to user.

        :param data: pandas data frame with the data.
        :param time_column_name: The name of a time column.
        :param time_series_id_column_names: The time series ID columns names.
        :param origin_time_column_name: The origin time column name.
        :param target_column_name: The name of a target column.
        :param group_column_names: The group column names.
        """
        columns_set = set(data.columns)
        if data.index.names != [None]:
            columns_set = columns_set.union(set(data.index.names))
        self._check_column_present(
            columns_set, time_column_name, TimeSeries.TIME_COLUMN_NAME,
            TimeseriesDfMissingColumn.TIME_COLUMN, ReferenceCodes._TSDS_NO_TIME_COLNAME_TSDF_CHK_TM_COL)
        if origin_time_column_name is not None:
            self._check_column_present(
                columns_set, origin_time_column_name, TimeSeriesInternal.ORIGIN_TIME_COLNAME,
                TimeseriesDfMissingColumn.ORIGIN_COLUMN, ReferenceCodes._TSDS_NO_ORIGIN_COLUMN)
        if time_series_id_column_names is not None:
            for ts_id in time_series_id_column_names:
                self._check_column_present(
                    columns_set, ts_id, TimeSeries.TIME_SERIES_ID_COLUMN_NAMES,
                    TimeseriesDfMissingColumn.GRAIN_COLUMN, ReferenceCodes._TSDS_NO_GRAIN_COLUMN)
        if group_column_names is not None:
            for group in group_column_names:
                self._check_column_present(
                    columns_set, group, TimeSeries.GROUP_COLUMN_NAMES,
                    TimeseriesDfMissingColumn.GROUP_COLUMN, ReferenceCodes._TSDS_NO_GROUP_COLUMN)
        if target_column_name is not None:
            self._check_column_present(
                columns_set, target_column_name, TimeSeriesInternal.DUMMY_TARGET_COLUMN,
                TimeseriesDfMissingColumn.VALUE_COLUMN, ReferenceCodes._TSDS_NO_TARGET_COLUMN)

    def _check_column_present(self, columns: Set[str], column: str,
                              column_type: str, target: str, ref_code: str) -> None:
        """
        Check if the column is present in the index or in the columns.

        :param columns: The columns expected to be present in the final TimeSeriesDataSet.
        :param column: the column to be checked for presence.
        :param column_type: The type of a column, to be checked.
        :param target: The target to be present in the error
        :param ref_code: The reference code for the error.
        :raises: ForecastingDataException
        """
        if column not in columns:
            raise ForecastingDataException._with_error(
                AzureMLError.create(
                    TimeseriesDfMissingColumn,
                    target=target,
                    reference_code=ref_code,
                    column_names='{}:{}'.format(column_type, column)
                ))

    def _validate(self) -> None:
        """
        Validate the data  and settings.

        Previously these checks were held by the TimeSeriesDataFrame class.
        :raises: ForecastingDataException, ForecastingConfigException
        """
        # Check the types of special column names
        if not isinstance(self.time_column_name, str):
            raise ForecastingConfigException._with_error(
                AzureMLError.create(TimeseriesDfColumnTypeNotSupported, target='time_column_name',
                                    reference_code=ReferenceCodes._TSDS_COL_TYPE_NOT_SUPPORTED_TM_COL,
                                    col_name='time',
                                    supported_type='string')
            )
        if self.time_series_id_column_names is not None and \
                any(not isinstance(gr, str) for gr in self.time_series_id_column_names):
            raise ForecastingConfigException._with_error(
                AzureMLError.create(TimeseriesDfColumnTypeNotSupported, target='time_series_id_column_names',
                                    reference_code=ReferenceCodes._TSDS_COL_TYPE_NOT_SUPPORTED_GRAIN_COLS,
                                    col_name='time series identifier',
                                    supported_type='string')
            )
        if self.target_column_name and not isinstance(self.target_column_name, str):
            raise ForecastingConfigException._with_error(
                AzureMLError.create(TimeseriesDfColumnTypeNotSupported, target='target_column_name',
                                    reference_code=ReferenceCodes._TSDS_COL_TYPE_NOT_SUPPORTED_TS_COL,
                                    col_name='target',
                                    supported_type='string')
            )
        if self.origin_time_column_name and not isinstance(self.origin_time_column_name, str):
            raise ForecastingConfigException._with_error(
                AzureMLError.create(TimeseriesDfColumnTypeNotSupported, target='origin_time_column_name',
                                    reference_code=ReferenceCodes._TSDS_COL_TYPE_NOT_SUPPORTED_ORI_COL,
                                    col_name='origin time',
                                    supported_type='string')
            )
        if self.group_column_names is not None and \
                any(not isinstance(gr, str) for gr in self.group_column_names):
            raise ForecastingConfigException._with_error(
                AzureMLError.create(TimeseriesDfColumnTypeNotSupported, target='group_column_names',
                                    reference_code=ReferenceCodes._TSDS_COL_TYPE_NOT_SUPPORTED_GROUP_COL,
                                    col_name='group',
                                    supported_type='string')
            )
        # Check that the time series id columns does not contain NaNs
        if self.time_series_id_column_names is not None:
            for ts_id in self.time_series_id_column_names:
                ts_id_values = self.data.index.get_level_values(ts_id)
                if any(pd.isnull(ts_id_values)):
                    raise ForecastingDataException._with_error(
                        AzureMLError.create(GrainContainsEmptyValues, target='time_series_id_values',
                                            reference_code=ReferenceCodes._TSDS_NANS_IN_GRAIN_COL,
                                            time_series_id=str(ts_id))
                    )
        # Check the type of a target column.
        if (self._target_column_name is not None) and \
            (isinstance(self.data[self._target_column_name].dtype, pd.CategoricalDtype) or
             (not all([isinstance(v, (int, float, np.number)) for v in self.data[self._target_column_name]]))):
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesDfWrongTypeOfValueColumn, target='target',
                                    reference_code=ReferenceCodes._TSDS_WRONG_TYPE_OF_VALUE_COL)
            )
        self._check_column_equal_across_origin()
        # Check for duplicated index.
        if self.data.index.to_frame().duplicated().sum() > 0:
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesDfDuplicatedIndex,
                                    target='index_keys',
                                    reference_code=ReferenceCodes._TSDS_DUPLICATED_INDEX)
            )

    def _check_column_equal_across_origin(self, colname=None):
        """
        Check whether the column value is consistent across origin times when the grain and time_index are the same.

        :param colname:
            The colname to check the origin time duplicates on.
        :type colname: str
        """
        if colname is None:
            colname = self.target_column_name

        if self.origin_time_column_name is None:
            return

        if colname is not None:
            time_and_ts_id = [self.time_column_name]
            if self.time_series_id_column_names:
                time_and_ts_id += self.time_series_id_column_names

            # check if the colname is a string
            Validation.validate_type(colname, "colname", str)
            # check if column is present in TSDF
            if colname not in self.data.columns:
                raise ForecastingDataException._with_error(
                    AzureMLError.create(TimeseriesDfMissingColumn,
                                        target=TimeseriesDfMissingColumn.REGULAR_COLUMN,
                                        reference_code=ReferenceCodes._TSDS_NO_REGULAR_COLNAME_DF,
                                        column_names=colname)
                )

            # Resetting index reduces groupby.apply computation time by 50%
            # Operating on X[colname].values instead of
            # X[colname] reduces computation time by 70%
            values = self.data[colname].reset_index(inplace=False, drop=False)
            all_equal = values.groupby(time_and_ts_id).apply(
                lambda X: (all(x == X[colname].values[0] for x in X[colname].values) or
                           all(pd.isnull(X[colname].values)))
            )

            # we expect that colname values will be the same across
            # origin_time_colname as long as the grain_colnames and time_colname
            #  are the same
            if not np.all(all_equal.values):
                safe_grains = self.time_series_id_column_names if self.time_series_id_column_names else []
                raise ForecastingDataException._with_error(
                    AzureMLError.create(TimeseriesDfColValueNotEqualAcrossOrigin,
                                        target='_check_column_equal_across_origin',
                                        reference_code=ReferenceCodes._TSDS_COL_VALUE_NOT_EQUAL_ACROSS_ORIGIN,
                                        grain_colnames=', '.join(safe_grains),
                                        time_colname=self.time_column_name,
                                        colname=colname,
                                        origin_time_colname=self.origin_time_column_name
                                        )
                )

    def _get_copy_or_none(self, lst: Optional[List[str]]) -> Optional[List[str]]:
        """
        Get the copy of the list or None, if initial list is None.

        :param lst: the initial list.
        :return: the copy of the list or None.
        """
        return None if lst is None else copy.deepcopy(lst)

    def from_data_frame_and_metadata(self,
                                     df: pd.DataFrame,
                                     validate: bool = False) -> 'TimeSeriesDataSet':
        """
        Copy the metadata from the existing time series data set to the new one.

        **Note:** This class will not copy the data frame, but will set its index to
        [time_column_name, time_series_id_column_names, origin_time_column_name].
        :param df: the new data frame.
        :param validate: Validate the data while cteating the time series data set.
        :return: The new time series data set, which contains metadata of an existing
                 object and data from the new data frame.
        """
        return TimeSeriesDataSet(
            df,
            time_column_name=self.time_column_name,
            time_series_id_column_names=self._get_copy_or_none(
                self.time_series_id_column_names),
            origin_time_column_name=self.origin_time_column_name,
            target_column_name=self.target_column_name,
            group_column_names=self._get_copy_or_none(
                self.group_column_names),
            validate=validate)

    def copy(self) -> 'TimeSeriesDataSet':
        """
        Return the deep copy of the given data frame.

        :return: The new TimeSeriesDataSet.
        """
        return self.from_data_frame_and_metadata(self.data.copy(deep=True))

    def concat(self, data_list: Optional[List[pd.DataFrame]], sort: bool = False,
               validate: bool = False) -> 'TimeSeriesDataSet':
        """
        Concatenate the list of time series data sets and set the same metadata.

        :param data_list: The list of data frame to concatenate.
        :return: New TimeSeriesDataSet obtained from the concatenated data frames.
        """
        # Check if data_list contains members.
        if data_list is None or len(data_list) == 0:
            return self.from_data_frame_and_metadata(self.data[:0], validate)
        # Check that all data frames contains correct index.
        ix = data_list[0].index
        names = set(ix.names)
        if any(set(df.index.names) != names for df in data_list[1:]):
            raise ClientException._with_error(
                AzureMLError.create(
                    IncompatibleIndexError,
                    reference_code=ReferenceCodes._TSDS_CONCAT_INDEX_ERROR,
                    target='index'))
        # Check that all data frame have the same columns.
        names = set(data_list[0].columns)
        if self.target_column_name:
            names.discard(self.target_column_name)
        if any(not names.issubset(set(df.columns)) for df in data_list[1:]):
            raise ClientException._with_error(
                AzureMLError.create(
                    IncompatibleColumnsError,
                    reference_code=ReferenceCodes._TSDS_CONCAT_COLUMNS_ERROR,
                    target='columns'))
        # If data frames have RangeIndex (default), its index.names will be
        # [None]. In this case we want to ignore index to avoid errors with
        # index duplications.
        ignore_index = ix.names == [None]
        df_new = pd.concat(data_list, sort=sort, ignore_index=ignore_index)
        return self.from_data_frame_and_metadata(df_new, validate)

    def extract_time_series(self, colnames: Optional[Union[str, List[str]]] = None) -> pd.DataFrame:
        """
        Extract a time series.

        This function firstly checks whether the columns provided have the
        same value across different origin time given the same grain and time
        values.
        Then for each column, it will extract the unique value for that
        specific column for each grain and time values and return the result
        data frame.

        :param colnames: columns names to extract time series on
        :return:
            A dataframe containing the unique column values of
            each grain and time combination.
        :rtype: pandas.DataFrame
        """
        if colnames is None:
            if not self.target_column_name:
                raise ClientException._with_error(
                    AzureMLError.create(
                        TargetAndExtractColumnsAreNone,
                        target='colnames',
                        reference_code=ReferenceCodes._TSDS_NOTGT_AND_COLUMNS_TO_EXTRACT))
            colnames = [self.target_column_name]
        elif is_iterable_but_not_string(colnames):
            for col in colnames:
                if not isinstance(col, str):
                    raise ForecastingConfigException._with_error(
                        AzureMLError.create(TimeseriesDfColumnTypeNotSupported, target='columns_array',
                                            reference_code=ReferenceCodes._TSDS_COL_TYPE_NOT_SUPPORTED_EXTRACT_COLS,
                                            col_name=str(col),
                                            supported_type='string')
                    )

        elif isinstance(colnames, str):
            colnames = [colnames]
        else:
            raise ForecastingConfigException._with_error(
                AzureMLError.create(TimeseriesDfColumnTypeNotSupported, target='colnames',
                                    reference_code=ReferenceCodes._TSDS_COL_TYPE_NOT_SUPPORTED_EXTRACT_COL,
                                    col_name=str(colnames),
                                    supported_type='string')
            )

        # check if columns are present in TSDF
        not_in_frame = [col for col in colnames
                        if col not in self.data.columns]
        if len(not_in_frame) > 0:
            raise ClientException._with_error(
                AzureMLError.create(MissingColumnsInData, target='colnames',
                                    reference_code=ReferenceCodes._TSDS_INV_VAL_COLUMNS_NOT_FOUND,
                                    columns=', '.join(not_in_frame),
                                    data_object_name='colnames')
            )

        # check if the columns satisfy extraction criteria
        for col in colnames:
            self._check_column_equal_across_origin(col)

        # Now that check is passed, extract the values
        # Cast to data frame since selection may not be a valid TSDF
        as_df = pd.DataFrame(self.data[colnames], copy=False)

        if self.origin_time_column_name is None:
            # No origin times, so just copy selection
            series_df = as_df.copy()

        else:
            time_and_ts_id = [self.time_column_name]
            if self.time_series_id_column_names:
                time_and_ts_id += self.time_series_id_column_names
            # Extract unique series from time/grain groups
            series_df = (as_df
                         .groupby(level=time_and_ts_id,
                                  group_keys=False)
                         .first())

        return series_df

    def groupby_time_series_id(self) -> DataFrameGroupBy:
        """
        The convenience method to get the groupby object of a underlying pandas DataFrame.

        :return: The groupby object of underlying data frame.
        """
        if not self.time_series_id_column_names:
            grouped = self.data.groupby(by=lambda axis_label: TimeSeriesInternal.DUMMY_GRAIN_COLUMN,
                                        group_keys=False)
        else:
            grouped = self.data.groupby(level=self.time_series_id_column_names,
                                        group_keys=False)
        return grouped

    @property
    def time_series_id_index(self) -> Optional[pd.Index]:
        """
        Return any requested subset of the TSDF index.

        :param index_names: names of index columns to return
        :type index_names: str or iterable of strings
        """
        if not self.time_series_id_column_names:
            return None
        elif len(self.time_series_id_column_names) > 1:
            index_indices = [self.data.index.get_level_values(
                col) for col in self.time_series_id_column_names]
            return pd.MultiIndex.from_arrays(index_indices)
        return self.data.index.get_level_values(self.time_series_id_column_names[0])

    @property
    def target_values(self) -> Optional[pd.Series]:
        """
        Get the target values as a pandas Series or None if there is no target.

        :return: target values or None.
        """
        if self.target_column_name is None:
            return None
        else:
            return self.extract_time_series()[self.target_column_name]

    def infer_single_freq(self) -> Optional[pd.DateOffset]:
        """
        Get frequency for TSDS where a single uniform frequency across all time series could be inferred.

        Otherwise, None will be returned.
        :return:
            None if no single uniform frequency is inferred. If frequency is
            inferred, return pandas.tseries.offsets.DateOffset by default.
        """
        freq_by_grain = self._infer_freq_by_ts_id()
        if freq_by_grain.shape[0] == 0:
            # There were several grains with no data points or with one daata point.
            # In this case freq_by_grain is a DataFrame.
            return None

        if not isinstance(freq_by_grain, pd.Series):
            raise ClientException._with_error(
                AzureMLError.create(FreqByGrainWrongType, target='TimeSeriesDataSet',
                                    type=str(type(freq_by_grain)),
                                    reference_code=ReferenceCodes._TSDS_FREQ_BY_GRAIN_WRONG_TYPE))

        if len(freq_by_grain) == 1:
            return freq_by_grain.values[0]

        # the grains that cannot be inferred frequency means the time series
        # have lenghth exactly 1, because for time series have unique time
        # stamps larger than 1, there will always be frequency inferred.
        # we will revisit these grains' data later.
        index_df = self.data.index.to_frame(index=False)

        index_df_with_freq = index_df.merge(freq_by_grain.reset_index(
            name='freq'), on=self.time_series_id_column_names, how='left')
        if index_df_with_freq['freq'].isnull().any():
            data_from_grains_with_null_freq = self.data.loc[
                index_df_with_freq['freq'].isnull().values]

        freq_by_grain = freq_by_grain.loc[freq_by_grain.notnull()]

        if len(freq_by_grain.unique()) == 1:
            return freq_by_grain.unique()[0]

        # the name attribute of DateOffset object can be viewed as the unit of
        #  the DateOffset object, e.g a DateOffSet object QuarterBegin(n=1,
        # startingMonth=2) and QuarterBegin(n=2, startingMonth=2), will both
        # have name attribute equal to 'QS-FEB'
        try:
            freq_name_by_grain = freq_by_grain.apply(lambda x: x.name)
            if len(freq_name_by_grain.unique()) != 1:
                # if the basic units are different, then no uniform single
                # frequency could be inferred
                return None
        except NotImplementedError:
            warn('For one of the time series frequency, '
                 'the name of the DateOffset obejct is '
                 'not implemented by Pandas. Single '
                 'frequency inference will be always return as None.')
            return None

        # the n attribute for DateOffset object indicates how many basic
        # units are contained in this object, this is usually also an input
        # argument when initializing the objects. e.g QuarterBegin(n=2,
        # startingMonth=2) will have a n equal to 2.
        freq_n_by_grain = freq_by_grain.apply(lambda x: x.n)
        freq_smallest_n = freq_n_by_grain.min()
        freq_n_mod_smallest_n = freq_n_by_grain.apply(
            lambda x: x % freq_smallest_n)

        # if the frequencies are not the multiples of the smallest frequency,
        #  then no single uniform frequency will be inferred.
        if len(freq_n_mod_smallest_n.unique()) > 1:
            return None

        data_size_by_grain = self.groupby_time_series_id().apply(
            lambda x: len(x.index.get_level_values(self.time_column_name).unique()))
        size_freq_and_n = pd.concat(
            [data_size_by_grain, freq_by_grain, freq_n_by_grain], axis=1)
        size_freq_and_n.columns = ['size', 'freq', 'n']

        # the inferred freq is the frequency satisfies:
        # (1) it is the mode frequency
        # (2) it has smallest number of the basic time unit (n)
        inferred_freq = size_freq_and_n.loc[
            (size_freq_and_n['freq'].isin(
                size_freq_and_n['freq'].mode().values)) &
            (size_freq_and_n['n'] == size_freq_and_n['n'].min()),
            'freq'].unique()

        if len(inferred_freq) == 0:
            # this means no such frequency is found.
            return None

        inferred_freq = inferred_freq[0]

        # we infer the single uniform frequency only when:
        # if all the time series, with different frequency than the
        # inferred_freq, have data size less than 3.
        # if there is any time series with different frequency with
        # length large or equal than 3, then we kind of think there is a
        # pattern showing the time series is "regularly" different than
        # the inferred frequency, thus no uniform single frequency can be
        #  inferred.
        ts_size_with_different_freq = size_freq_and_n.loc[
            size_freq_and_n['freq'] != inferred_freq, 'size']

        if ts_size_with_different_freq.max() >= 3:
            return None

        # check whether the data from grains with None frequency inferred
        # conform with the inferred single uniform frequency
        if index_df_with_freq['freq'].isnull().any():
            if not self.from_data_frame_and_metadata(
                    data_from_grains_with_null_freq)._check_regularity(freq=inferred_freq):
                return None

        return inferred_freq

    def _check_regularity(self, freq: Optional[pd.DateOffset] = None) -> bool:
        """
        Check the regularity of the whole data frame.

        The data frame is regular if every series in the
        data frame is regular

        :param freq:
            The frequency of the time series in the data frame.
        :type freq: pandas.tseries.offsets.DateOffset

        :return:
            True if all series in the frame are regular.
        :rtype: bool
        """
        if freq is None:
            freq = self.infer_freq()
        tsds_bygrain = self.groupby_time_series_id()

        if len(tsds_bygrain) > 1:
            reg_results_bygrain = tsds_bygrain.apply(lambda x: pd.Series(
                self.from_data_frame_and_metadata(x)._check_regularity_single_grain(freq=freq)))

        else:
            grain_name, grain_df = [(name, group) for name, group in
                                    tsds_bygrain][0]
            reg_results_bygrain = pd.DataFrame(
                [self.from_data_frame_and_metadata(grain_df)._check_regularity_single_grain(freq=freq)],
                index=[grain_name])

        return cast(bool, reg_results_bygrain['regular'].all())

    def _check_regularity_single_grain(self, freq: pd.DateOffset
                                       ) -> Dict[str, Union[bool, List[str]]]:
        """
        Check the time index regularity for data from a single series grain.

        :param freq: the supposed frequency of a timeseries data set.
        :return: dict
            {'regular': bool, 'problems': list}
            A time index is defined as regular for a single grain if this time
            index:
            (1) there is no duplicate entries
            (2) there is no NA/empty entries
            (3) there is no datetime gap
        """
        #  origin_time_colname will be replaced by forecast grain

        problems_list = []

        columns_to_check_duplicates = [self.time_column_name]
        if self.origin_time_column_name:
            columns_to_check_duplicates = columns_to_check_duplicates + [self.origin_time_column_name]

        resetted_data = self.data.reset_index(drop=False, inplace=False)
        if resetted_data.duplicated(subset=columns_to_check_duplicates, keep=False).sum() > 0:
            problems_list.append('Duplicate datetime entries exist')

        time_index_column = self.time_index

        if time_index_column.isnull().any():
            problems_list.append('NA datetime entries exist')

        if time_index_column.duplicated(keep=False).any():
            # if there are duplicate entries in the time index, drop the duplicates
            time_index_column = time_index_column.drop_duplicates()

        if time_index_column.isnull().any():
            # if there are NAs in the time index, drop the NAs
            time_index_column = time_index_column.dropna()

        # sort the time_index_column first
        time_index_column = time_index_column.sort_values()

        try:
            # if the time_index_column can pass the frequency check
            # in the DatetimeIndex initializer
            # we claim this is a time index with regular frequency
            time_index_column = pd.DatetimeIndex(time_index_column, freq=freq)
            is_regular = True
        except ValueError:
            is_regular = False

        if not is_regular:
            problems_list.append('Irregular datetime gaps exist')
        if len(problems_list) == 0:
            regular = True
        else:
            regular = False

        return {'regular': regular, 'problems': problems_list}

    def infer_freq(self) -> Optional[pd.DateOffset]:
        """
        Infer the frequency of the TimeSeriesDataSet.

        If there are multiple frequencies found, this method
        returns the most common frequency and prints a warning.

        .. _offset-alias: https://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases

        :return:
            None if no frequency is inferred. If frequency is
            inferred, return pandas.tseries.offsets.DateOffset by default.
            Will return an offset alias (frequency string)
            if return_freq_string=True.
        """
        freq_by_grain = self._infer_freq_by_ts_id()

        freq_by_grain = freq_by_grain[freq_by_grain.notnull()]

        if len(freq_by_grain) == 0:
            warn('there is no frequency inferred. ', UserWarning)
            freq = None
        elif len(freq_by_grain.unique()) > 1:
            freq = freq_by_grain.value_counts().sort_values(ascending=False).index[0]
            print('Expected only one distinct datetime frequency from all grain column(s) in the '
                  'data, with {0} distinct datetime frequencies ({1}) inferred.'.format(len(freq_by_grain.unique()),
                                                                                        freq_by_grain.unique()))
        else:
            freq = freq_by_grain.unique()[0]

        return freq

    def fill_datetime_gap(self, freq: Optional[pd.DateOffset] = None,
                          origin: Optional[str] = None,
                          end: Optional[str] = None) -> 'TimeSeriesDataSet':
        """
        Fill the datetime gaps in the TimeSeriesDataSet.

        :param freq:
            If the frequency string is provided, the function will fill
            the datetime gaps according to the provided string.
            Otherwise, it will infer the frequency string and
            fill the time index accordingly.
            See offset-alias.
        :param origin:
            If provided, the datetime will be filled back to origin for
            all grains.
        :param end:
            If provided, the datetime will be filled up to end for all grains.

        :return:
            A TimeSeriesDataSet with the datetime properly filled.
        :example:
        >>> data1 = pd.DataFrame(
        ...   {'store': ['a', 'a', 'a', 'b', 'b'],
        ...    'brand': ['a', 'a', 'a', 'b', 'b'],
        ...    'date': pd.to_datetime(
        ...      ['2017-01-01', '2017-01-03', '2017-01-04',
        ...       '2017-01-01', '2017-01-02']),
        ...    'sales': [1, np.nan, 5, 2, np.nan],
        ...    'price': [np.nan, 2, 3, np.nan, 4]})
        >>> df1 = TimeSeriesDataSet(data1, grain_colnames=['store', 'brand'],
        ...                           time_colname='date',
        ...                           ts_value_colname='sales')
        >>> df1.data
                                price  sales
        date       store brand
        2017-01-01 a     a        nan   1.00
        2017-01-03 a     a       2.00    nan
        2017-01-04 a     a       3.00   5.00
        2017-01-01 b     b        nan   2.00
        2017-01-02 b     b       4.00    nan
        >>> df1.fill_datetime_gap(freq='D')
          brand       date  price  sales store
        0     a 2017-01-01    NaN    1.0     a
        1     a 2017-01-02    NaN    NaN     a
        2     a 2017-01-03    2.0    NaN     a
        3     a 2017-01-04    3.0    5.0     a
        4     b 2017-01-01    NaN    2.0     b
        5     b 2017-01-02    4.0    NaN     b
        """
        if freq is None:
            freq = self.infer_freq()
        slice_keys = copy.deepcopy(self.time_series_id_column_names) if self.time_series_id_column_names else []
        if self.origin_time_column_name:
            slice_keys.append(self.origin_time_column_name)
        if slice_keys:
            tsdf_filled = self.data.groupby(slice_keys, group_keys=False, as_index=False).apply(
                lambda x: self._fill_datetime_gap_single_slice_key(
                    x, slice_keys,
                    x.name, freq=freq, origin=origin, end=end))
        else:
            tsdf_filled = self._fill_datetime_gap_single_slice_key(
                self.data, None, slice_keys,
                freq=freq, origin=origin, end=end)

        return TimeSeriesDataSet(
            tsdf_filled,
            time_column_name=self.time_column_name,
            time_series_id_column_names=self.time_series_id_column_names,
            origin_time_column_name=self.origin_time_column_name,
            target_column_name=self.target_column_name,
            group_column_names=self.group_column_names)

    # fill the datetime gap for TimeSeriesDataSet for a single slice_key

    def _fill_datetime_gap_single_slice_key(self, df: pd.DataFrame,
                                            slice_keys: Optional[List[str]],
                                            grain_level: Optional[GrainType],
                                            freq: pd.DateOffset,
                                            origin: Optional[str] = None,
                                            end: Optional[str] = None) -> pd.DataFrame:
        """
        Fill the datetime gap in one grain.

        :param grain_level: The name of a grain to fill datetime gap for.
        :param freq: The data frequency.
        :param origin: If provided, the datetime will be filled back to origin
        :param end: If provided, the datetime will be filled up to end.
        :return: The data frame with filled datetime gaps.
        """
        if df.shape[0] == 0:
            return df
        time_index = df.index.get_level_values(self.time_column_name)
        if origin is not None:
            min_time = origin
        else:
            min_time = time_index.min()

        if end is not None:
            max_time = end
        else:
            max_time = time_index.max()

        if (origin is not None) or (end is not None):
            time_index = time_index[(time_index >= min_time) &
                                    (time_index <= max_time)]

        if isinstance(time_index[0], pd.Period):
            onfreq_time = pd.period_range(start=min_time, end=max_time, freq=freq)
        elif isinstance(time_index[0], pd.Timestamp):
            onfreq_time = pd.date_range(start=min_time, end=max_time, freq=freq)
        else:
            raise ClientException._with_error(
                AzureMLError.create(TimeseriesDfInvalidValTmIdxWrongType, target='time_index',
                                    reference_code=ReferenceCodes._TSDF_INV_VAL_TM_IDX_WRONG_TYPE)
            )

        # Check for misalignment with input freq
        # i.e. is the time index a subset of the regular frequency grid?
        if not set(time_index).issubset(onfreq_time):
            if slice_keys == [TimeSeriesInternal.DUMMY_GRAIN_COLUMN] or slice_keys is None:
                raise ForecastingDataException._with_error(
                    AzureMLError.create(
                        TimeseriesDfFrequencyNotConsistent,
                        target='_fill_datetime_gap_single_slice_key.time_index',
                        reference_code=ReferenceCodes._TSDF_FREQUENCY_NOT_CONSISTENT_FILL_DATETIME_GAP,
                        freq=str(freq),
                        forecasting_config=TimeSeriesWebLinks.FORECAST_CONFIG_DOC)
                )
            else:
                raise ForecastingDataException._with_error(
                    AzureMLError.create(
                        TimeseriesDfFrequencyNotConsistentGrain,
                        target='_fill_datetime_gap_single_slice_key.time_index',
                        reference_code=ReferenceCodes._TSDF_FREQUENCY_NOT_CONSISTENT_FILL_DATETIME_GAP_GRAIN,
                        grain_level=str(grain_level),
                        freq=str(freq),
                        forecasting_config=TimeSeriesWebLinks.FORECAST_CONFIG_DOC)
                )

        # Check if the time index has gaps. Use fast comparison on int8 np arrays
        if not np.array_equal(time_index.sort_values().asi8, onfreq_time.asi8):
            # If there are gaps, create a plain data frame with the filled datetimes (no gaps)
            # If there's a grain in the input, put in grain columns too
            df_filled = pd.DataFrame({self.time_column_name: onfreq_time})
            if slice_keys:
                grain_assign_dict = grain_level_to_dict(
                    slice_keys, grain_level)
                df_filled = df_filled.assign(**grain_assign_dict)
            # Right merge the input with the filled data frame to get a filled tsdf
            ix = df.index.names
            # We can not guarantee that index names are not present in columns.
            overlap = set(ix).intersection(set(df.columns))
            rename = {}
            rev_rename = {}
            for name in overlap:
                new_name = '{}_{}'.format(str(name), uuid.uuid1())
                rename[name] = new_name
                rev_rename[new_name] = name
            df.rename(rename, axis=1, inplace=True)
            df.reset_index(inplace=True, drop=False)
            result = df.merge(df_filled, how='right')
            result.set_index(ix, inplace=True)
            result.rename(rev_rename, axis=1, inplace=True)
            result.sort_index(inplace=True)
        else:
            result = df

        return result

    def _infer_freq_by_ts_id(self) -> pd.Series:
        """
        Infer frequency for each grain.

        :return: Inferred frequencies by grain.
        :rtype: pandas.core.series.Series
        """
        # Can't infer the frequency without a time_colname
        Contract.assert_true(
            self.time_column_name is not None,
            AutoMLErrorStrings.TIMESERIES_DF_CANNOT_INFER_FREQ_WITHOUT_TIME_IDX,
            log_safe=True
        )
        # Set the index corresponding to the time series data frame
        if self.time_series_id_column_names:
            freq_by_grain = self.data.groupby(
                self.time_series_id_column_names, as_index=True, group_keys=False).apply(
                lambda d: self._infer_freq_single_ts_id(
                    d.index.get_level_values(self.time_column_name)))
            if not isinstance(freq_by_grain, pd.Series):
                return pd.Series(dtype=np.dtype('object'))
            return freq_by_grain
        else:
            return pd.Series([self._infer_freq_single_ts_id(self.time_index)])

    def _infer_freq_single_ts_id(self, time_index_column: pd.DatetimeIndex) -> Optional[pd.DateOffset]:
        """
        Infer the frequency from a time index column.

        :param time_index_column: pandas.core.indexes.datetimes.DatetimeIndex
        :param return_freq_string: boolean
            Whether to return the frequency string instead of pandas.tseries.offsets.DateOffset.
        :return: pandas.tseries.offsets.DateOffset or string 'None' if no frequency is inferred.
        """
        time_index_column = self._ts_single_grain_clean(time_index_column)

        if len(time_index_column) == 0:
            # if no input entries in the input time index, None will be returned.
            return None

        if len(time_index_column) == 1:
            return None
        elif len(time_index_column) == 2:
            freq = self._infer_freq_single_grain_special_cases(time_index_column)
            if freq is None:
                time_delta = time_index_column[1] - time_index_column[0]
                freq = to_offset(time_delta)
        else:
            # Note: pd.infer_freq can only infer frequency with time index having
            # length>=3.
            freq = pd.infer_freq(time_index_column)
            if freq is not None:
                freq = to_offset(freq)
            else:
                freq = self._infer_freq_single_grain_special_cases(time_index_column)
                if freq is None:
                    # infer with the shortest time gap
                    time_gap = time_index_column[1:] - time_index_column[:-1]
                    freq = to_offset(time_gap.min())

        return freq

    def _ts_single_grain_clean(self, time_index_column: pd.DatetimeIndex) -> pd.DatetimeIndex:
        if time_index_column.duplicated(keep=False).any():
            # if there are duplicate entries in the time index, drop the duplicates
            time_index_column = time_index_column.drop_duplicates()

        if time_index_column.isnull().any():
            # if there are NAs in the time index, drop the NAs
            time_index_column = time_index_column.dropna()

        # sort the time_index_column first
        time_index_column = time_index_column.sort_values()

        return time_index_column

    def _infer_freq_single_grain_special_cases(self, time_index_column: pd.DatetimeIndex) -> Optional[pd.DateOffset]:
        """
        Infer frequency for some special cases where pandas.infer_freq() fails.

        e.g the time index have only 2 values or the time
        index have some gaps in the data however under some scenarios the
        frequency can be properly inferred.

        Currently, the cases handled in this function are all with granularity
        larger than a day, e.g weekly, monthly, quarterly and yearly. If in future,
        more special cases are discovered, feel free to add those cases to this
        function here.

        :param time_index_column: The datetime index used to determine the frequency.
        :return: A DateOffset with the frequency or None.
        """
        # only infer on time index with more than or equal to 2 entries
        if len(time_index_column) < 2:
            return None

        if _range((time_index_column - time_index_column.normalize()).values).astype(int) == 0:
            # if there is no hour, minute and second parts in any of the entries,
            # mean all the entries are at least at date granularity

            # yearly
            if time_index_column.is_year_end.all():
                n = self._get_smallest_gap(time_index_column.year)
                return offsets.YearEnd(n=n, month=12)
            elif time_index_column.is_year_start.all():
                # YS is new in pandas 0.21.
                n = self._get_smallest_gap(time_index_column.year)
                return offsets.YearBegin(n=n, month=1)
            elif len(time_index_column.month.unique()) == 1 \
                    and len(time_index_column.day.unique()) == 1:
                n = self._get_smallest_gap(time_index_column.year)
                return offsets.DateOffset(years=n)

            # quarterly
            elif time_index_column.is_quarter_end.all():
                n = self._get_smallest_gap(time_index_column.year *
                                           4 + time_index_column.quarter)
                return offsets.QuarterEnd(n=n, startingMonth=12)
            elif time_index_column.is_quarter_start.all():
                n = self._get_smallest_gap(time_index_column.year * 4 +
                                           time_index_column.quarter)
                return offsets.QuarterBegin(n=n, startingMonth=1)

            # monthly
            elif time_index_column.is_month_end.all():
                n = self._get_smallest_gap(time_index_column.year * 12 +
                                           time_index_column.month)
                return offsets.MonthEnd(n=n)
            elif time_index_column.is_month_start.all():
                n = self._get_smallest_gap(time_index_column.year * 12 +
                                           time_index_column.month)
                return offsets.MonthBegin(n=n)
            elif len(time_index_column.day.unique()) == 1:
                n = self._get_smallest_gap(time_index_column.year * 12 +
                                           time_index_column.month)
                return offsets.DateOffset(months=n)

            # weekly
            elif len(time_index_column.weekday.unique()) == 1:
                # We have to convert np.int64 to the plain int.
                weekday = int(time_index_column.weekday.unique()[0])
                n = np.int64(floor(((time_index_column[1:] - time_index_column[:-1]) /
                                    np.timedelta64(7, 'D')).min()))
                return offsets.Week(weekday=weekday, n=n)

        return None

    def _get_smallest_gap(self, input_array: np.ndarray) -> np.int64:
        """
        Get the smallest gap from array-like variable l.

        :param input_array: The array of dates represented as a number.
        :return: The minimal period between dates.
        """
        input_array = np.array(input_array)
        input_array = np.sort(input_array)
        return cast(np.int64, np.min(input_array[1:] - input_array[:-1]))

    @staticmethod
    def create_tsds_safe(
            X: pd.DataFrame,
            y: Optional[np.ndarray],
            target_column_name: Optional[str],
            time_column_name: str,
            origin_column_name: Optional[str],
            grain_column_names: Optional[Union[str, List[str]]],
            boolean_column_names: Optional[List[str]] = None) -> 'TimeSeriesDataSet':
        """
        Construct time series data set.

        :param X: The dataset to be wrapped to tsds.
        :type X: DataInputType
        :param y: The target column to be converted to tsdf. This can be excluded by the caller.
        :type y: DataSingleColumnInputType
        :param target_column_name: The desired name of the target column.
        :type target_column_name: str
        :param time_column_name: The name of the time column within X.
        :type time_column_name: str
        :param origin_column_name: The desired name of the origin column.
        :type origin_column_name: str
        :param grain_column_names: The column(s) which collectively make up the grain(s) within X.
        :type grain_column_names: List[str]
        :param boolean_column_names: The column(s) which are of type boolean within X.
        :type boolean_column_names: List[str]
        :return: The new time series data set with the copy of input data and grain column names.
        """
        if target_column_name in X.columns and y is not None:
            raise ClientException._with_error(
                AzureMLError.create(
                    BothYandTargetProvidedToTsdf,
                    reference_code=ReferenceCodes._TSDS_BOTH_Y_AND_TGT_COL_PROVIDED,
                    target='target_column'))

        # Drop index and make a copy of data.
        data = X.reset_index(drop=True, inplace=False)
        data = data.infer_objects()
        # As we are working on data copy, we can create additional columns.
        if target_column_name is not None and target_column_name not in data.columns:
            data[target_column_name] = y if y is not None else np.NaN
        # Ensure that grain_column_names is always list.
        if isinstance(grain_column_names, str):
            grain_column_names = [grain_column_names]
        if grain_column_names is None or len(grain_column_names) == 0 or \
            (TimeSeriesInternal.DUMMY_GRAIN_COLUMN not in data.columns and
             TimeSeriesInternal.DUMMY_GRAIN_COLUMN == grain_column_names[0]):
            data[TimeSeriesInternal.DUMMY_GRAIN_COLUMN] = TimeSeriesInternal.DUMMY_GRAIN_COLUMN
            grain_column_names = [TimeSeriesInternal.DUMMY_GRAIN_COLUMN]
        # Check if data has the designated origin column/index
        # If not, don't try to set it since this will trigger an exception in TSDF
        origin_present = \
            origin_column_name is not None and origin_column_name in data.columns
        origin_setting = origin_column_name if origin_present else None
        if boolean_column_names:
            for col in boolean_column_names:
                if col in data.columns:
                    try:
                        data[col] = data[col].astype('float')
                    except BaseException:
                        warnings.warn(
                            'One of columns contains boolean values, '
                            'but not all of them are able to be converted to float type.'
                        )
        return TimeSeriesDataSet(
            data, time_column_name=time_column_name,
            target_column_name=target_column_name,
            origin_time_column_name=origin_setting,
            time_series_id_column_names=grain_column_names,
            validate=True
        )

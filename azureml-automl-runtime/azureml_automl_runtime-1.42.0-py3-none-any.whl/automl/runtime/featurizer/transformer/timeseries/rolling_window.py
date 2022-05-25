# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Create features as aggregates (e.g. average or maximum) of values from a rolling window."""
from typing import Any, cast, DefaultDict, Dict, List, Optional, Tuple, Union
import logging

import re
import warnings
from collections import defaultdict

import numpy as np
import pandas as pd
from azureml._common._error_definition import AzureMLError
from azureml._common._error_definition.user_error import ArgumentOutOfRange
from azureml.automl.core import _codegen_utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    InvalidArgumentType,
    NonUniqueNamesOfNewColumns,
    TimeseriesDfDuplicatedIndex,
    TimeseriesFeaturizerFitNotCalled,
    TimeseriesInputIsNotTimeseriesDs)
from azureml.automl.core.shared.constants import TimeSeries, TimeSeriesInternal
from azureml.automl.core.shared.exceptions import ConfigException, \
    ClientException
from azureml.automl.core.shared._diagnostics.contract import Contract
from azureml.automl.core.shared.forecasting_exception import ForecastingDataException
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.runtime.featurizer.transformer.timeseries.missingdummies_transformer import \
    MissingDummiesTransformer
from azureml.automl.runtime._automl_forecast_freq import AutoMLForecastFreq
from azureml.automl.runtime._time_series_data_set import TimeSeriesDataSet
from azureml.automl.runtime.frequency_fixer import str_to_offset_safe
from azureml.automl.runtime.shared.forecasting_verify import is_iterable_but_not_string, check_cols_exist

from azureml.automl.runtime.shared.types import DataFrameApplyFunction
from pandas.core.series import Series
from pandas.tseries.frequencies import to_offset
from pandas.tseries.offsets import DateOffset

from .forecasting_base_estimator import AzureMLForecastTransformerBase, _GrainBasedStatefulTransformer
from .forecasting_constants import ORIGIN_TIME_COLNAME_DEFAULT
from .time_series_imputer import TimeSeriesImputer
from .transform_utils import OriginTimeMixin


class RollingWindow(AzureMLForecastTransformerBase, OriginTimeMixin, _GrainBasedStatefulTransformer):
    """
    A transformation class for creating rolling window features.

    .. py:class:: RollingWindow

    Rolling windows are temporally defined with respect to origin times
    in the TimeSeriesDataSet. The origin time in a data frame row
    indicates the right date/time boundary of a window.

    If the input data frame does not contain origin times, they
    will be created based on the ```max_horizon``` parameter.

    :param window_size:
         Size of the moving window.
         Either the number of observations in each window
         or a time-span specified as a pandas.tseries.offsets.DateOffset.
         Note that when the size is given as a DateOffset,
         the window may contain a variable number of observations.
    :type window_size: int, pandas.tseries.offsets.DateOffset

    :param transform_dictionary:
        A dictionary specifying the rolling window transformations
        to apply on the columns. The keys are functions
        or names of pre-defined Pandas rolling window methods.
        See https://pandas.pydata.org/pandas-docs/stable/computation.html#method-summary.
        The dict values are columns on which to apply the functions.
        Each value can be a single column name or a list
        of column names.
    :type transform_dictionary: dict

    :param window_options:
        A dictionary of keyword window options.
        These will be passed on to the pandas.Rolling
        constructor as **kwargs.
        See pandas.DataFrame.rolling for details.

        To avoid target leakage, the ```center``` option
        setting here is ignored and always set to False.

        The ```closed``` option is also ignored.
        For integer window size, it is set to `both`.
        For DateOffset window size, it is set to `right`.
    :type window_options: dict

    :param transform_options:
        A dictionary of aggregation function options. The keys are aggregation
        function names. The value is again a dictionary with two keys: args
        and kwargs, the value of the 'args' key is the positional arguments
        passed to the aggregation function and the value of the 'kwargs' key
        is the keyword arguments passed to the aggregation function.
    :type transform_opts: dict

    :param transform_options:
        Integer horizons defining the origin times to create.
        Parameter can be a single integer - which indicates a maximum
        horizon to create for all grains - or a dictionary where the keys
        are grain levels and each value is an integer maximum horizon.
    :type max_horizon: int, dict

    :param origin_time_column_name:
        Name of origin time column to create in case origin times
        are not already contained in the input data frame.
        The `origin_time_colunm_name` property of the transform output
        will be set to this parameter value in that case.
        This parameter is ignored if the input data frame contains
        origin times.
    :type origin_time_column_name: str

    :param dropna:
        Should missing values from rolling window feature creation be dropped?
        Defaults to False.
        Note that the missing values from the test data are not dropped but
        are instead 'filled in' with values from training data.
    :type dropna: bool

    :param check_max_horizon:
                         If set to True, max horizon will be figured out from the origin column.
                         Setting this parameter to False dramatically increases the speed and memory
                         consumption.
    :type check_max_horizon: bool

    :param backfill_cache:
                         Back fill the chache to avoid NaNs to prevent the output data
                         frame shape degradation.
    :type backfill_cache: bool
    Examples:
    >>> data = {'store': [1] * 10 + [2] * 10 + [3] * 10,
                'sales': [250, 150, 300, 200, 400, 300, 150, 200, 350, 100,
                          400, 300, 200, 450, 200, 350, 450, 150, 250, 500,
                          150, 400, 500, 300, 350, 250, 200, 400, 500, 450],
                'customers': [28, 15, 30, 24, 47, 33, 15, 20, 36, 13,
                              38, 30, 25, 43, 20, 35, 46, 17, 28, 44,
                              15, 47, 50, 30, 35, 29, 25, 40, 48, 42],
                'date': pd.to_datetime(
                ['2017-01-01', '2017-01-02', '2017-01-03', '2017-01-04',
                '2017-01-05', '2017-01-06', '2017-01-07', '2017-01-08',
                '2017-01-09', '2017-01-10'] * 3)}
    >>> tsds = TimeSeriesDataSet(
    data, time_series_id_column_names='store',
    time_column_name='date', target_column_name='sales')
    >>> window_size = 3
    >>> transform_dict = {'sum': ['sales', 'customers'], 'quantile': 'sales'}
    >>> window_opts = {'min_periods': 2}
    >>> transform_opts = {'quantile': {'args': [0.25],
    'kwargs': {'interpolation': 'lower'}}}
    >>> rolling_window_transformer = RollingWindow(window_size,
    transform_dict, window_opts, transform_opts)
    >>> rolling_window_transformer.fit_transform(tsds).data.head(10)
                                 customers  sales  customers_sum_window3
    date       store origin
    2017-01-01 1     2016-12-31         28    250                    nan
    2017-01-02 1     2017-01-01         15    150                    nan
    2017-01-03 1     2017-01-02         30    300                  43.00
    2017-01-04 1     2017-01-03         24    200                  73.00
    2017-01-05 1     2017-01-04         47    400                  69.00
    2017-01-06 1     2017-01-05         33    300                 101.00
    2017-01-07 1     2017-01-06         15    150                 104.00
    2017-01-08 1     2017-01-07         20    200                  95.00
    2017-01-09 1     2017-01-08         36    350                  68.00
    2017-01-10 1     2017-01-09         13    100                  71.00

                                 sales_sum_window3  sales_quantile_window3
    date       store origin
    2017-01-01 1     2016-12-31                nan                     nan
    2017-01-02 1     2017-01-01                nan                     nan
    2017-01-03 1     2017-01-02             400.00                  150.00
    2017-01-04 1     2017-01-03             700.00                  150.00
    2017-01-05 1     2017-01-04             650.00                  150.00
    2017-01-06 1     2017-01-05             900.00                  200.00
    2017-01-07 1     2017-01-06             900.00                  200.00
    2017-01-08 1     2017-01-07             850.00                  150.00
    2017-01-09 1     2017-01-08             650.00                  150.00
    2017-01-10 1     2017-01-09             700.00                  150.00

    """
    POSTFIX_SEP = '_'
    RW_BY_TIME = 'rw_by_time'
    RW_BY_OCCURRENCE = 'rw_by_occurrence'
    RW_POSTFIX = 'window'

    def __init__(self, window_size: Union[int, str, pd.DateOffset],
                 transform_dictionary: Dict[DataFrameApplyFunction, Union[str, List[str]]],
                 window_options: Optional[Dict[str, Any]] = None,
                 transform_options: Dict[DataFrameApplyFunction, Dict[str, Any]] = {},
                 max_horizon: int = 1,
                 origin_time_column_name: str = ORIGIN_TIME_COLNAME_DEFAULT,
                 dropna: bool = False, check_max_horizon: bool = True,
                 backfill_cache: bool = False,
                 freq: Optional[Union[str, pd.DateOffset]] = None) -> None:
        """Create a RollingWindow Transformer."""
        self.window_size = window_size
        self.transform_dict = transform_dictionary
        self.window_opts = {} if window_options is None else window_options  # type: Dict[str, Any]
        self.transform_opts = transform_options
        self.max_horizon = max_horizon  # type: Union[int, Dict[Union[str, Tuple[str]], int]]
        self.origin_time_colname = origin_time_column_name
        self.dropna = dropna
        self.backfill_cache = backfill_cache

        self._is_fit = False
        self._cache = None  # type: Optional[TimeSeriesDataSet]
        self.freq = freq  # type: Optional[pd.Offset]
        self._check_max_horizon = check_max_horizon
        self._feature_name_map = {}  # type: Dict[Tuple[str, DataFrameApplyFunction], str]
        self._agg_func_map = {}  # type: Dict[str, List[DataFrameApplyFunction]]
        self._func_name_to_func_map = {}  # type: Dict[str, DataFrameApplyFunction]
        # Save column names generated from rolling_windows operator to be added to timeseries_param_dict later
        # down the pipeline in _featurization_execution_timeseries.py, so that those columns can be removed
        # later for classical forecasting models and Prophet in _multi_grain_forecast_base.py,
        # since those learners doesn't need those columns, and in fact need to remove them in order
        # to elimitate duplex time index generated from lookback features (lags/rolling windows).
        self._rolling_window_columns = []   # type: List[Union[str, Any]]

        self._rw_option = RollingWindow.RW_BY_TIME
        self._target_column_name = TimeSeriesInternal.DUMMY_TARGET_COLUMN
        super().__init__()

    def _get_imports(self):
        imports = []
        for k in self.transform_dict:
            if callable(k):
                imports.append(_codegen_utilities.get_import(k))
        for k in self.transform_opts:
            if callable(k):
                imports.append(_codegen_utilities.get_import(k))
        return imports

    def get_params(self, deep=True):
        return {
            # self.window_size could be an int or a pd.DateOffset
            "window_size": getattr(self.window_size, "freqstr", None) or self.window_size,
            "transform_dictionary": self.transform_dict,
            "window_options": self.window_opts,
            "transform_options": self.transform_opts,
            "max_horizon": self.max_horizon,
            "origin_time_column_name": self.origin_time_colname,
            "dropna": self.dropna,
            "check_max_horizon": self._check_max_horizon,
            "backfill_cache": self.backfill_cache,
            "freq": AutoMLForecastFreq._get_freqstr_safe(self)
        }

    def _get_freq_name(self) -> str:
        """Get the name for frequency."""
        if self.freq:
            try:
                return cast(str, self.freq.name)
            except NotImplementedError:
                return cast(str, self.freq.freqstr)
        return ""

    def __repr__(self):
        params = self.get_params()
        transform_dict = params.pop("transform_dictionary")
        transform_opts = params.pop("transform_options")

        transform_dict_repr = repr(transform_dict)
        transform_opts_repr = repr(transform_opts)

        for k in transform_dict:
            if callable(k):
                transform_dict_repr = transform_dict_repr.replace(repr(k), k.__name__)

        for k in transform_opts:
            if callable(k):
                transform_opts_repr = transform_opts_repr.replace(repr(k), k.__name__)

        transform_opts_params = []
        for k in transform_opts:
            if callable(k):
                transform_opts_params.append("    {}: {}".format(
                    k.__name__,
                    _codegen_utilities.indent_multiline_string(repr(transform_opts[k])))
                )
            else:
                transform_opts_params.append("    {}: {}".format(
                    k,
                    _codegen_utilities.indent_multiline_string(repr(transform_opts[k])))
                )

        return _codegen_utilities.generate_repr_str(
            self.__class__, params, transform_dictionary=transform_dict_repr, transform_options=transform_opts_repr)

    @property
    def rw_option(self) -> str:
        return self._rw_option if hasattr(self, '_rw_option') else RollingWindow.RW_BY_TIME

    @property
    def target_column_name(self) -> str:
        return self._target_column_name if hasattr(self, '_target_column_name') \
            else TimeSeriesInternal.DUMMY_TARGET_COLUMN

    @property
    def window_size(self) -> pd.DateOffset:
        """See `window_size` parameter."""
        return self._window_size

    @window_size.setter
    def window_size(self, val: Union[int, str, pd.DateOffset]) -> None:
        if not np.issubdtype(type(val), np.signedinteger) and not isinstance(val, DateOffset):
            try:
                val = to_offset(val)
            except ValueError:
                raise ConfigException._with_error(
                    AzureMLError.create(
                        InvalidArgumentType, target="window_size",
                        argument="window_size", actual_type=type(val), expected_types="int, pandas.DateOffset",
                        reference_code=ReferenceCodes._TS_RW_BAD_WINDOW)
                )
        if np.issubdtype(type(val), np.signedinteger) and cast(int, val) < 2:
            raise ConfigException._with_error(
                AzureMLError.create(
                    ArgumentOutOfRange, target=TimeSeries.TARGET_ROLLING_WINDOW_SIZE,
                    argument_name="target_rolling_window_size", min=2, max="inf",
                    reference_code=ReferenceCodes._TARGET_ROLLING_WINDOW_SMALL_CLIENT
                )
            )
        self._window_size = val

    @property
    def transform_dict(self) -> Dict[DataFrameApplyFunction, Union[str, List[str]]]:
        """See `transform_dict` parameters."""
        return self._transform_dict

    @transform_dict.setter
    def transform_dict(self, val: Dict[DataFrameApplyFunction, Union[str, List[str]]]) -> None:
        if not isinstance(val, dict):
            raise ClientException._with_error(
                AzureMLError.create(InvalidArgumentType,
                                    target='transform_dict',
                                    reference_code=ReferenceCodes._TS_RW_BAD_TRANSFORM_DICT,
                                    argument='transform_dict',
                                    actual_type=str(type(val)),
                                    expected_types='dict'
                                    ))
        self._transform_dict = val

    @property
    def window_opts(self) -> Dict[str, Any]:
        """See `window_opts` parameters."""
        return self._window_opts

    @window_opts.setter
    def window_opts(self, val: Dict[str, Any]) -> None:
        if not isinstance(val, dict):
            raise ClientException._with_error(
                AzureMLError.create(InvalidArgumentType,
                                    target='window_opts',
                                    reference_code=ReferenceCodes._TS_RW_BAD_WINDOW_OPTS,
                                    argument='window_opts',
                                    actual_type=str(type(val)),
                                    expected_types='dict'
                                    ))

        # Some window options are not supported.
        # Force default values and warn user
        not_configurable = ['center', 'closed']
        for opt in not_configurable:
            if opt in val:
                warnings.warn(('RollingWindow: "{0}" is not ').format(opt) +
                              'a configurable window option.')
                val.pop(opt)

        self._window_opts = val

    @property
    def transform_opts(self) -> Dict[DataFrameApplyFunction, Dict[str, Any]]:
        """See `transform_opts` parameters."""
        return self._transform_opts

    @transform_opts.setter
    def transform_opts(self, val: Dict[DataFrameApplyFunction, Dict[str, Any]]) -> None:
        if not isinstance(val, dict):
            raise ClientException._with_error(
                AzureMLError.create(InvalidArgumentType,
                                    target='transform_opts',
                                    reference_code=ReferenceCodes._TS_RW_BAD_TRANSFORM_OPTS,
                                    argument='transform_opts',
                                    actual_type=str(type(val)),
                                    expected_types='dict'
                                    ))
        self._transform_opts = val

    @property
    def freq(self) -> Optional[pd.DateOffset]:
        """Return the frequency of a transform."""
        return self._ts_freq.freq

    @freq.setter
    def freq(self, val: Optional[Union[str, pd.DateOffset]]) -> None:
        """Set the frequency."""
        if val is not None and not isinstance(val, pd.DateOffset) and not isinstance(val, str):
            raise ClientException._with_error(
                AzureMLError.create(
                    InvalidArgumentType, target="freq",
                    argument="freq", actual_type=type(val), expected_types="pd.DateOffset",
                    reference_code=ReferenceCodes._TS_RW_BAD_FREQ
                ))
        self._ts_freq = AutoMLForecastFreq(val)
        if isinstance(val, str) and self._ts_freq.freq is None:
            # Raise the exception if we were not able to convert string to frequency.
            str_to_offset_safe(val, ReferenceCodes._TS_RW_BAD_FREQ_LITERAL)

    def _make_func_name_to_func_map(self) -> Dict[str, DataFrameApplyFunction]:
        """
        Create a map, function name -> function.

        Used for the functions in the transform_dict property.

        This method is used when we need to lookup a *possibly* callable
        function from a column name in pandas.Rolling.agg output
        """
        func_map = {(func.__name__ if callable(func) else func): func
                    for func in self.transform_dict}

        return func_map

    def _make_feature_name(self, col: str, func: DataFrameApplyFunction) -> str:
        """
        Get the name of the rolling window feature associated with column.

        'func' can be a callable function or a string.
        """
        window_sz_str = (self.window_size.freqstr
                         if isinstance(self.window_size, pd.DateOffset)
                         else str(self.window_size))
        func_name = func.__name__ if callable(func) else func
        safe_seasonality = self._get_freq_name()
        feat_name = col + RollingWindow.POSTFIX_SEP + func_name
        feat_name += RollingWindow.POSTFIX_SEP + RollingWindow.RW_POSTFIX + window_sz_str + safe_seasonality

        return feat_name

    def _make_feature_name_map(self,
                               X: pd.DataFrame,
                               quiet: bool = False) -> Dict[Tuple[str, DataFrameApplyFunction], str]:
        """
        Make a mapping from (column, func) pairs to feature names from the transform_dict property.

        'func' can be a callable function or a string.

        Column names must exist in the data frame, X.
        :param quiet: If false (default) chaeck for column presence.
        :type quiet: bool
        """
        new_feature_dict = {}
        for func, cols in self.transform_dict.items():
            if not quiet:
                check_cols_exist(X.data, cols)
            if is_iterable_but_not_string(cols):
                for c in cols:
                    new_feature_dict[(c, func)] = \
                        self._make_feature_name(c, func)
            elif isinstance(cols, str):
                new_feature_dict[(cols, func)] = \
                    self._make_feature_name(cols, func)
            else:
                pass

        return new_feature_dict

    def _make_agg_func_map(self,
                           feature_name_map: Dict[Tuple[str, DataFrameApplyFunction], str]) -> \
            Dict[str, List[DataFrameApplyFunction]]:
        """
        Start from a feature name map, create a map: column -> list of functions to apply to column.

        This method creates a dictionary compatible with
        the Pandas "agg" function input.
        """
        agg_func_map = defaultdict(list)  # type: DefaultDict[str, List[DataFrameApplyFunction]]
        for col, func in feature_name_map:
            agg_func_map[col].append(func)

        return agg_func_map

    def preview_column_names(self, X: TimeSeriesDataSet) -> List[str]:
        """
        Get a list of new columns that would be created by this transform.

        This method does not add any columns to X, it just previews what
        the transform would add if it were applied.

        :param X: Input data for the transform
        :type X: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet

        :return: List of new column names
        :rtype: list
        """
        if self.freq is None:
            self.freq = X.infer_freq()
        name_map = self._make_feature_name_map(X.data, quiet=True)
        self._rolling_window_columns = list(name_map.values())

        return list(name_map.values())

    def _cache_training_data(self, X_train: TimeSeriesDataSet) -> None:
        """
        Cache training data.

        Cache an appropriate amount of training data so that a
        test set can be featurized without unnecessarily dropping
        observations.
        :param X: The training data set.
        """

        if self.rw_option == RollingWindow.RW_BY_OCCURRENCE:
            target_dummies_name = MissingDummiesTransformer.get_column_name(cast(str, X_train.target_column_name))
            Contract.assert_true(target_dummies_name in X_train.data.columns,
                                 'RW-by-occurrence cache expected a missing indicator for the target',
                                 log_safe=True)
            # For generating by_occurrence features, we need to
            # remove imputed rows before generating cache data
            not_imputed_val = MissingDummiesTransformer.MARKER_VALUE_NOT_MISSING
            X_train = X_train.from_data_frame_and_metadata(
                X_train.data[X_train.data[target_dummies_name].notna() &
                             X_train.data[target_dummies_name] == not_imputed_val])

        def get_tail_by_grain(gr, df):

            tsds = X_train.from_data_frame_and_metadata(df)
            # Need grab an extra period for each horizon
            #  past 1
            h_max = self.max_horizon_from_key_safe(gr, self.max_horizon)
            extra_tail_for_horizon = h_max - 1

            if isinstance(self.window_size, pd.DateOffset):
                # Figure out the date boundaries of the window
                tail_start = \
                    tsds.time_index.max() - self.window_size - extra_tail_for_horizon * cast(int, self.freq)
            else:
                # Get the last 'window_size' periods.
                # Some complication here because there may
                #  be duplicate dates if the feature set is multi-horizon.
                # To handle this case, extract the last window from
                #  the underlying time-series and find the start date
                #  of the window from there
                val_series = cast(pd.Index, tsds.target_values).sort_index(level=tsds.time_column_name)
                tail_periods = self.window_size + extra_tail_for_horizon
                tail_series = val_series.iloc[-tail_periods:]
                tail_start = (tail_series.index
                              .get_level_values(tsds.time_column_name).min())

            return tsds.data[tsds.time_index >= tail_start]

        if not X_train.time_series_id_column_names:
            df_cache = get_tail_by_grain('', X_train.data)
        else:
            df_cache = X_train.data.groupby(X_train.time_series_id_column_names, group_keys=False).apply(
                lambda Xgr: get_tail_by_grain(Xgr.name, Xgr))
        self._cache = X_train.from_data_frame_and_metadata(df_cache)
        # If cache contains the missing value, it will result in the
        # degradation of a shape of transformed data on the
        # data set missing y values.
        # We backfill these values if backfill_cache is true.
        if self._cache is not None and self.backfill_cache:
            ts_imputer = TimeSeriesImputer(input_column=cast(str, self._cache.target_column_name),
                                           option='fillna',
                                           method='bfill',
                                           freq=self.freq)
            self._cache = ts_imputer.transform(self._cache)

    def _apply_rolling_agg_to_single_series(self,
                                            X_single: pd.DataFrame) -> \
            pd.DataFrame:
        """
        Apply Pandas rolling window aggregation to a single timeseries.

        X_single:
            pandas.DataFrame with *one index level* (the time index).
            Data frame columns are the columns that will be transformed.

        Returns a pandas.DataFrame with the transformed columns.
        """
        # Sort by ascending time
        X_single.sort_index(inplace=True, ascending=True)

        # Create some shortcuts
        window_opts = self.window_opts
        feature_name_map = self._feature_name_map
        agg_func_map = self._agg_func_map
        func_name_to_func = self._func_name_to_func_map

        X_rolling = X_single.rolling(self.window_size,
                                     **window_opts)

        result_all = []
        if not self.transform_opts:
            # Most aggregation functions don't take arguments and we can
            # simply apply multiple functions to each column in one line of
            # code.
            result_tmp = X_rolling.agg(agg_func_map)

            # If the result after transformation is a Series, convert it to
            # DataFrame to rename columns.
            if isinstance(result_tmp, Series):
                result_tmp = result_tmp.to_frame()

            if result_tmp.columns.nlevels > 1:
                # When multiple column and function combinations are applied,
                # the result column index has multiple levels.
                # The 'values' property should retrieve a list of 2-tuple
                #  objects. Each tuple is arranged as (column name, function).
                result_tmp.columns = \
                    [feature_name_map[(col, func_name_to_func[func_name])]
                     for col, func_name in
                     result_tmp.columns.values]
            else:
                # For single level column index, we expect that only
                #  one function was applied to each column
                # Check to make sure this is the case
                nonunique_by_col = {col: agg_func_map[col]
                                    for col in result_tmp.columns
                                    if len(agg_func_map[col]) > 1}
                if len(nonunique_by_col) > 0:
                    raise ClientException._with_error(
                        AzureMLError.create(
                            NonUniqueNamesOfNewColumns,
                            target='transform_function',
                            reference_code=ReferenceCodes._TS_RW_NON_UNIQ_COLUMNS_AFTER_TRANSFORM))

                result_tmp.columns = \
                    [feature_name_map[(col, agg_func_map[col][0])]
                     for col in result_tmp.columns]

            result_all.append(result_tmp)
        else:
            # When transform_opts is not empty, we need to pass some function
            # arguments.
            for col, funcs in agg_func_map.items():
                # Check if any function in the current (column, functions)
                # pair is a key in transform_opts. If yes, go through the
                # functions in col_func one by one. When a function is a key
                # in transform_opts, parse the value of the key to extract
                # args and kwargs and pass them to pd.rolling.agg().
                if any(func in self.transform_opts for func in funcs):
                    for func in funcs:
                        if func in self.transform_opts:
                            func_opts = self.transform_opts[func]
                            if 'args' in func_opts:
                                args = func_opts['args']
                            else:
                                args = {}
                            if 'kwargs' in func_opts:
                                kwargs = func_opts['kwargs']
                            else:
                                kwargs = {}
                        else:
                            args = {}
                            kwargs = {}

                        result_tmp = X_rolling[col].agg(func, *args, **kwargs)
                        result_tmp = result_tmp.to_frame()

                        result_tmp.columns = [feature_name_map[(col, func)]]
                        result_all.append(result_tmp)

                else:
                    # If none of the functions in the current
                    # (column, functions) pair is a key in transform_opts,
                    # simply apply all the functions to the current column at
                    # one time.
                    result_tmp = X_rolling.agg({col: funcs})
                    if isinstance(result_tmp, Series):
                        result_tmp = result_tmp.to_frame()

                    if result_tmp.columns.nlevels > 1:
                        result_tmp.columns = \
                            [feature_name_map[(col,
                                               func_name_to_func[func_name])]
                             for col, func_name in result_tmp.columns.values]
                    else:
                        # Check that there is one function applied to col
                        if len(funcs) > 1:
                            # TODO: write the unit test for that.
                            raise ClientException._with_error(
                                AzureMLError.create(
                                    NonUniqueNamesOfNewColumns,
                                    target='transform_function',
                                    reference_code=ReferenceCodes._TS_RW_NON_UNIQ_COLUMNS_AFTER_TRANSFORM_OPTS))

                        result_tmp.columns = \
                            [feature_name_map[(col, funcs[0])]
                             for col in result_tmp.columns]

                    result_all.append(result_tmp)

        # Concat along columns ('cbind' in R)
        return pd.concat(result_all, axis=1)

    def _transform_single_grain(self,
                                gr: Union[str, Tuple[str]],
                                X_gr: TimeSeriesDataSet) -> pd.DataFrame:
        """
        Apply all the transformations in col_func_dict to the data of a single grain.

        :param X_gr:
            A TimeSeriesDataSet containing the data of a single
            grain.
        :type X_single: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet

        :return:
            A data frame with the transformation result
            columns added to X_single.
        """
        # Get the list of columns on which to apply rolling window
        xform_cols = list(self._agg_func_map.keys())

        X_temp = X_gr
        if self.rw_option == RollingWindow.RW_BY_OCCURRENCE:
            target_dummies_name = MissingDummiesTransformer.get_column_name(self.target_column_name)
            # For generating by_occurrence features, we need to remove imputed rows
            Contract.assert_true(target_dummies_name in X_gr.data.columns,
                                 'RW-by-occurrence expected a missing indicator for the target',
                                 log_safe=True)
            not_imputed_val = MissingDummiesTransformer.MARKER_VALUE_NOT_MISSING
            X_temp = X_gr.from_data_frame_and_metadata(X_gr.data[X_gr.data[target_dummies_name] == not_imputed_val])

        # Get unique time series for requested columns
        #  as a plain data frame
        X_sub = X_temp.extract_time_series(xform_cols)

        all_but_time = [lv for lv in X_sub.index.names
                        if lv != X_gr.time_column_name]
        if len(all_but_time) > 0:
            X_sub.reset_index(level=all_but_time,
                              drop=True, inplace=True)

        # Perform pandas rolling window op
        rolled_df = \
            self._apply_rolling_agg_to_single_series(X_sub)

        # Pandas computes window function values at the right end of the window
        # Hence, the dates in rolled_df are actually the origin times of the window features
        if self.rw_option == RollingWindow.RW_BY_OCCURRENCE:
            # For by-occurrence join on the occurrence origin times
            Contract.assert_true(TimeSeriesInternal.ORIGIN_TIME_OCCURRENCE_COLUMN_NAME in X_gr.data.columns,
                                 'RW-by-occurrence expected an origin by occurrence column',
                                 log_safe=True)
            rolled_df.index.names = [TimeSeriesInternal.ORIGIN_TIME_OCCURRENCE_COLUMN_NAME]
            rolled_df.reset_index(inplace=True)
            grain_df = X_gr.data.reset_index(drop=False, inplace=False)
            grain_df = grain_df.merge(
                rolled_df, how='left', on=[
                    TimeSeriesInternal.ORIGIN_TIME_OCCURRENCE_COLUMN_NAME])
            grain_df.set_index(X_gr.data.index.names, inplace=True)
            return grain_df
        else:
            rolled_df.index.names = [X_gr.origin_time_column_name]
            return X_gr.data.merge(rolled_df, how='left',
                                   left_index=True, right_index=True)

    @function_debug_log_wrapped(logging.INFO)
    def fit(self, X: TimeSeriesDataSet, y: Optional[Any] = None) -> 'RollingWindow':
        """
        Fit the rolling window.

        Cache the last window of training data.

        :param X: Data frame of training data
        :type X: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet

        :param y: Ignored. Included for pipeline compatibility

        :return: self
        :rtype: azureml.automl.runtime.featurizer.transformer.timeseries.rolling_window.RollingWindow
        """
        # Get time series frequency.
        # Needed for creating origin dates and window shifting.
        # Assume the freq is the same for train/test sets .
        if self.freq is None:
            self.freq = X.infer_freq()

        # Save the name of the target column
        self._target_column_name = cast(str, X.target_column_name)

        # Make maps for translating data frame column names and
        #  aggregation functions to feature names in the transformed
        #  data frame
        self._func_name_to_func_map = self._make_func_name_to_func_map()
        self._feature_name_map = self._make_feature_name_map(X)
        self._agg_func_map = self._make_agg_func_map(self._feature_name_map)

        if X.origin_time_column_name is not None:
            # If origin times are set in the input,
            #  detect the maximum horizons to use for
            #  rolling window features
            if self._check_max_horizon:
                self.max_horizon = \
                    cast(Union[Dict[Union[Tuple[str], str], int], int],
                         self.detect_max_horizons_by_grain(X, freq=self.freq))

            # Assume that if origins are set in train set, they'll
            #  be set in test set too.
            self.origin_time_colname = X.origin_time_column_name

        # We need to check if we should compute the window features by occurrence
        # Determine this by checking if occurrence origins are in the input
        # The lag operator sets the occurrence lag if it detects enough sparsity to lag-by-occurrence
        if TimeSeriesInternal.ORIGIN_TIME_OCCURRENCE_COLUMN_NAME in X.data.columns:
            self._rw_option = RollingWindow.RW_BY_OCCURRENCE

        self._cache_training_data(X)
        self._is_fit = True

        return self

    @function_debug_log_wrapped(logging.INFO)
    def transform(self, X: TimeSeriesDataSet) -> TimeSeriesDataSet:
        """
        Apply a rolling window transformations to the input.

        :param X: Data frame to transform
        :type X: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet

        :return:
            A new TimeSeriesDataSet with the transformation result
            columns added to X.
        :rtype: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet

        :raises: ForecastingDataException
        """
        if not self._is_fit or self._cache is None:
            raise ClientException._with_error(
                AzureMLError.create(
                    TimeseriesFeaturizerFitNotCalled, target='fit',
                    reference_code=ReferenceCodes._TS_RW_FIT_NOT_CALLED))

        if not isinstance(X, TimeSeriesDataSet):
            raise ClientException._with_error(
                AzureMLError.create(TimeseriesInputIsNotTimeseriesDs, target='X',
                                    reference_code=ReferenceCodes._TS_INPUT_IS_NOT_TSDF_ROLL_WIN)
            )
        # Force center and closed window options
        self._window_opts['center'] = False

        if isinstance(self.window_size, int):
            self._window_opts['closed'] = None
        else:
            self._window_opts['closed'] = 'right'

        # pre-pend cached training data
        try:
            if self._cache is not None:
                # We are taking self._cache.data here, because it may contain target column,
                # missing in X.
                tsds_full = self._cache.concat([self._cache.data, X.data], sort=True, validate=True)
            else:
                tsds_full = X
        except ForecastingDataException as ex:
            if ex.error_code == TimeseriesDfDuplicatedIndex().code:
                # Check if the error code is TimeseriesDfDuplicatedIndex.
                tsds_full = X
            else:
                # Otherwise raise the exception.
                raise

        # Add origin times up to the max horizon
        #  if the input doesn't already have any origin times
        if tsds_full.origin_time_column_name is None:
            tsds_full = self.create_origin_times(
                tsds_full, self.max_horizon,
                freq=self.freq,
                origin_time_colname=self.origin_time_colname)

        if not tsds_full.time_series_id_column_names:
            warnings.warn('The TimeSeriesDataSet does not have any '
                          'time_series_id_column_names or origin_time_column_name set, '
                          'Assuming a single time series.')
            df_trans = self._transform_single_grain('', tsds_full)  # type: pd.DataFrame

            # df_trans may have rows from the cache - remove any rows that
            # aren't in the original input by selecting on the time index
            df_trans = df_trans[df_trans.index.get_level_values(X.time_column_name).isin(X.time_index)]
        else:
            df_trans = (tsds_full.data.groupby(tsds_full.time_series_id_column_names, group_keys=False)
                        .apply(lambda Xgr:
                               self._transform_single_grain(
                                   Xgr.name, tsds_full.from_data_frame_and_metadata(Xgr))))
            # df_trans may have rows from the cache - remove any rows that
            # aren't in the original input by selecting on the time index
            # here we have to do it by grain to support ragged data frames.
            grain_start = {}
            for grain, df in X.data.groupby(X.time_series_id_column_names, group_keys=False):
                grain_start[grain] = df.index.get_level_values(X.time_column_name).min()
            df_trans = df_trans.groupby(
                tsds_full.time_series_id_column_names, group_keys=False).apply(
                    lambda Xgr: Xgr[Xgr.index.get_level_values(
                        tsds_full.time_column_name) >= grain_start[Xgr.name]]
                    if Xgr.name in grain_start.keys() else None)

        if self.dropna:
            # Need to do a little more work if dropna is True.
            # Don't want to drop rows where NaNs are not caused
            #   by the RollingWindow
            feature_cols = list(self._feature_name_map.values())

            # Get a binary mask indicating which rows to drop.
            # Cast to data frame to avoid TSDF finalize checks.
            notnull_by_column = df_trans[feature_cols].notnull().values
            not_null_all_cols = np.apply_along_axis(all, 1, notnull_by_column)
            df_trans = df_trans[not_null_all_cols]

        target_column_name = X.target_column_name
        traning_target = self._cache.target_column_name if self._cache is not None else None
        if target_column_name is None and traning_target is not None and \
                traning_target in df_trans.columns is not None and traning_target not in X.data.columns:
            # If X does not contain the target value column, merging
            # it with self._cache will create the column with the NaNs.
            # If we will retain this column, it will cause some estimators to break.
            df_trans.drop(self._cache.target_column_name, axis=1, inplace=True)
        return TimeSeriesDataSet(
            df_trans,
            time_column_name=X.time_column_name,
            time_series_id_column_names=X.time_series_id_column_names,
            target_column_name=target_column_name,
            origin_time_column_name=self.origin_time_colname,
            group_column_names=X.group_column_names)

    @staticmethod
    def get_col_internal_type(col_name: str) -> Optional[str]:
        """
        Get the type of a column if it is generated by rolling window transformer.

        :param col_name: The column name.
        :return: If column is generated by rolling window transformer, return 'window', else None.
        """
        rw_col_pattern = RollingWindow.POSTFIX_SEP + RollingWindow.RW_POSTFIX + "[0-9a-zA-Z-]+$"
        if re.search(rw_col_pattern, col_name) is not None:
            return RollingWindow.RW_POSTFIX
        else:
            return None

    def __setstate__(self, state: Dict[Any, Any]) -> None:
        if not isinstance(state['_ts_freq'], AutoMLForecastFreq):
            state['_ts_freq'] = AutoMLForecastFreq(state['_ts_freq'])
        AzureMLForecastTransformerBase.__setstate__(self, state)

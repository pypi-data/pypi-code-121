# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Create lags and leads (negative lags) of target and features."""
import logging
import re

# TODO: Fix experimental attribute
from typing import Any, Dict, Iterable, List, Optional, Union, cast
from warnings import filterwarnings, warn

import numpy as np
import pandas as pd

from ..._constants import TimeSeriesInternal
from ..._diagnostics.azureml_error import AzureMLError, AzureMLException
from ..._diagnostics.contract import Contract
from ..._diagnostics.debug_logging import function_debug_log_wrapped
from ..._diagnostics.error_definitions import (
    EmptyLagsForColumns,
    FitNotCalled,
    InvalidArgumentType,
    TimeseriesColumnNamesOverlap,
    TimeseriesDfColumnTypeNotSupported,
    TimeseriesDfDuplicatedIndex,
    TimeseriesHorizonAbsent,
    TimeseriesInputIsNotTimeseriesDs,
    TimeseriesOriginAbsent,
    TimeseriesWrongDropnaParam,
)
from ..._diagnostics.reference_codes import ReferenceCodes
from ...timeseries._automl_forecast_freq import AutoMLForecastFreq
from ...timeseries._frequency_fixer import str_to_offset_safe
from ...timeseries._time_series_data_set import TimeSeriesDataSet
from ...timeseries.forecasting_utilities import invert_dict_of_lists
from ...timeseries.forecasting_verify import is_iterable_but_not_string, is_list_oftype
from .._azureml_transformer import AzureMLTransformer
from ._grain_based_stateful_transformer import _GrainBasedStatefulTransformer
from .forecasting_constants import ORIGIN_TIME_COLNAME_DEFAULT
from .max_horizon_featurizer import MaxHorizonFeaturizer
from .missingdummies_transformer import MissingDummiesTransformer
from .time_series_imputer import TimeSeriesImputer
from .transform_utils import OriginTimeMixin


class LagLeadOperator(AzureMLTransformer, OriginTimeMixin, _GrainBasedStatefulTransformer):
    """
    A transformation class for computing lags and leads for values.
    Work for general time series data sets, sparse or non-sparse.
    Has two lag options: "lag_by_time" or "lag_by_occurrence"
    default: "lag_by_occurrence"
    "lag_by_time" is good for (almost) evenly spaced time series data, while
    "lag_by_occurrence" is a better option for non-evenly spaced data
    This module will automatically select the right one by checking
    data sparsity.

    .. py:class:: LagLeadOperator

    .. _pandas.Series.shift: https://pandas.pydata.org/pandas-docs/stable/
                            generated/pandas.Series.shift.html

    This will be used as a featurization step inside the forecast pipeline.

    :param lags:
        dictionary of the form {'column_to_lag' : [lag_order1, lag_order2]}.
        Dictionary keys must be names of columns in the data frame to which
        the transform is applied. Dictionary values are either integers or
        lists of integers indicating what lags must be constructed.
        Negative values are allowed, and indicate 'leads' i.e. moving into
        the future values of time series.
    :type lags: dict

    :param max_horizon:
        how many steps ahead do you intend to predict the series later. This
        is used to construct a full grid of `time` and `origin_time` to make
        sure that output is compatible with multi-step forecasting featurizers
        downstream. This argument is ignored if the input data has
        `origin_time_column_name` set, because it is assumed that the job of
        setting up multi-horizon data structure had already been performed.
        Defaults to 1 to produce expected behavior for most users.
    :type max_horizon: int

    :param dropna:
        should missing values from lag creation be dropped? Defaults to False.
        Note that the missing values from the test data are not dropped but
        are instead 'filled in' with values from training data.
    :type dropna: bool

    :param origin_time_column_name:
        how to name the `origin_time` column when the input does not contain
        one. Must be a single string. This argument is ignored if the input
        data has `origin_time_column_name` set, because it is assumed that the job
        of setting up multi-horizon data structure had already been performed.
        Defaults to "origin".
    :type origin_time_column_name: str

    :param overwrite_columns:
        Flag that permits the transform to overwrite existing columns in the
        input DataFrame for features that are already present in it.
        If True, prints a warning and overwrites columns.
        If False, throws a RuntimeError.
        Defaults to False to protect user data.
    :type overwrite_columns: bool

    :param backfill_cache:
                         Back fill the chache to avoid NaNs to prevent the output data
                         frame shape degradation.
    :type backfill_cache: bool

    Example 1 (Evenly Spaced Time Series Data, Will Use Lag_By_Time):
    Construct a small DataFrame:

    >>> raw_data = {'store': ['storeA'] * 3 + ['storeB'] * 4,
    ...             'date' : pd.to_datetime(
    ...                 ['2017-01-01', '2017-02-01', '2017-03-01'] * 2 +
    ...                 ['2017-04-01'] ),
    ...             'sales': range(8, 15)}
    >>> tsds = TimeSeriesDataSet(
    ...    data=pd.DataFrame(raw_data),
    ...    time_series_id_column_names=['store'], time_column_name=['date'],
    ...    target_column_name='sales')
    >>> tsds = tsdf.data.sort_index()
    >>> tsds.data
                            sales
    store      date
    storeA     2017-01-01      8
               2017-02-01      9
               2017-03-01     10
    storeB     2017-01-01     11
               2017-02-01     12
               2017-03-01     13
               2017-04-01     14
    >>> tsds=MaxHorizonFeaturizer(1).fit_transform(tsds)
                                     sales  horizon_origin
    store      date       origin
    storeA     2017-01-01 2016-12-01     8               1
               2017-02-01 2017-01-01     9               1
               2017-03-01 2017-02-01    10               1
    storeB     2017-01-01 2016-12-01    11               1
               2017-02-01 2017-01-01    12               1
               2017-03-01 2017-02-01    13               1
               2017-04-01 2017-03-01    14               1
    >>> make_lags = LagLeadOperator(
    ...                 lags_to_construct={'sales': [-1, 1]})
    >>> make_lags.fit(tsds)
    >>> result = make_lags.transform(tsds)
    >>> result.data
                                     sales  horizon_origin  sales_lead1  sales_lag1
    store      date       origin
    storeA     2017-01-01 2016-12-01     8               1         9.00         nan
               2017-02-01 2017-01-01     9               1        10.00        8.00
               2017-03-01 2017-02-01    10               1          nan        9.00
    storeB     2017-01-01 2016-12-01    11               1        12.00         nan
               2017-02-01 2017-01-01    12               1        13.00       11.00
               2017-03-01 2017-02-01    13               1        14.00       12.00
               2017-04-01 2017-03-01    14               1          nan       13.00

    Example 2 (Non-evenly Spaced Time Series Data, Will Use Lag_By_Occurrence):
    Construct a small TimeSeriesDataSet:

    >>> raw_data = {'store': ['storeA'] * 3 + ['storeB'] * 4,
    ...             'date' : pd.to_datetime(
    ...                 ['2017-01-01', '2017-02-01', '2017-04-01'] * 2 +
    ...                 ['2017-07-01'] ),
    ...             'sales': range(8, 15)}
    >>> tsds = TimeSeriesDataSet(
    ...    data=pd.DataFrame(raw_data),
    ...    time_series_id_column_names=['store'], time_column_name=['date'],
    ...    target_column_name='sales')
    >>> tsds = tsds.data.sort_index()
    >>> tsds.data
                            sales
    store      date
    storeA     2017-01-01      8
               2017-02-01      9
               2017-04-01     10
    storeB     2017-01-01     11
               2017-02-01     12
               2017-04-01     13
               2017-07-01     14
    >>> tsds=MaxHorizonFeaturizer(1).fit_transform(tsds)
    >>> tsds
                                     sales  horizon_origin
    store      date       origin
    storeA     2017-01-01 2016-12-01     8               1
               2017-02-01 2017-01-01     9               1
               2017-04-01 2017-03-01    10               1
    storeB     2017-01-01 2016-12-01    11               1
               2017-02-01 2017-01-01    12               1
               2017-04-01 2017-03-01    13               1
               2017-07-01 2017-06-01    14               1
    >>> make_lags = LagLeadOperator(
    ...                 lags_to_construct={'sales': [1]})
    >>> make_lags.fit(tsds)
    >>> result = make_lags.transform(tsds)
    >>> result.data
                                     sales  horizon_origin   sales_occurrence_lag1  date_occurrence_lag1_timeDiffDays
    store      date       origin
    storeA     2017-01-01 2016-12-01     8               1                     nan                                nan
               2017-02-01 2017-01-01     9               1                    8.00                                 31
               2017-04-01 2017-03-01    10               1                    9.00                                 59
    storeB     2017-01-01 2016-12-01    11               1                     nan                                nan
               2017-02-01 2017-01-01    12               1                   11.00                                 31
               2017-04-01 2017-03-01    13               1                   12.00                                 59
               2017-07-01 2017-06-01    14               1                   13.00                                 91
    """

    LAG_BY_TIME = "lag_by_time"
    LAG_BY_OCCURRENCE = "lag_by_occurrence"
    LAG_POSTFIX = "lag"
    LEAD_POSTFIX = "lead"
    OCCURRENCE_POSTFIX = "occurrence"
    POSTFIX_SEP = "_"
    SPARSITY_THRESHOLD = 0.02  # threshold parameter to decide between lag by time and occurrence options

    def __init__(
            self,
            lags: Dict[str, Union[int, List[int]]],
            max_horizon: int = 1,
            dropna: bool = False,
            origin_time_column_name: str = ORIGIN_TIME_COLNAME_DEFAULT,
            overwrite_columns: bool = False,
            backfill_cache: bool = False,
            freq: Optional[Union[str, pd.DateOffset]] = None) -> None:
        """Create a LagLeadOperator."""
        self.lags_to_construct = lags
        self.max_horizon = max_horizon
        self.dropna = dropna
        self.origin_time_colname = origin_time_column_name
        self.overwrite_columns = overwrite_columns
        self.backfill_cache = backfill_cache

        # lag options: "lag_by_time" or "lag_by_occurrence"
        # default: "lag_by_occurrence"
        # "lag_by_time" is good for (almost) evenly spaced time series data, while
        # "lag_by_occurrence" is a better option for non-evenly spaced data
        self.lag_option = LagLeadOperator.LAG_BY_OCCURRENCE

        # iniitialize fitted status - to False, obviously
        self._is_fit = False
        self._cache = None  # type: Optional[TimeSeriesDataSet]
        self.freq = freq
        # set the flag for train and test set
        self._in_fit_transform = False

        # feature flag for inclusion of order column in input dataframe
        # This flag is used to preserve compatibility between SDK versions
        self._no_original_order_column = True

        # feature flag for addition of occurrence origin column to output dataframe
        # This flag is used to preserve compatibility between SDK versions
        self._add_occurrence_origin_column = True
        super().__init__()

        # Save column names generated from lag_lead operator to be added to timeseries_param_dict later
        # down the pipeline in _featurization_execution_timeseries.py, so that those columns can be removed
        # later for classical forecasting models and Prophet in _multi_grain_forecast_base.py,
        # since those learners doesn't need those columns, and in fact need to remove them in order
        # to elimitate duplex time index generated from lookback features (lags/rolling windows).
        self._lag_columns = []  # type: List[Union[str, Any]]

    def get_params(self, deep=True):
        params = super().get_params(deep)
        params.update(
            {
                "lags": self.lags_to_construct,
                "origin_time_column_name": self.origin_time_colname,
                "freq": AutoMLForecastFreq._get_freqstr_safe(self)
            }
        )
        return params

    def _get_freq_name(self) -> str:
        """Get the name for frequency."""
        if self.freq:
            try:
                return cast(str, self.freq.name)
            except NotImplementedError:
                return cast(str, self.freq.freqstr)
        return ""

    ############################################################################
    # Housekeeping - use properties to rule out incorrect inputs from users
    ############################################################################
    @property
    def lags_to_construct(self) -> Dict[str, Union[int, List[int]]]:
        """Get the dictionary of column names to lists of lags/leads to construct."""
        return self._lags_to_construct

    # set value of _lags_to_constuct, and check for incorrect user input
    @lags_to_construct.setter
    def lags_to_construct(self, value: Dict[str, Union[int, List[int]]]) -> None:
        # check if input value is a dict
        if not isinstance(value, dict):
            raise AzureMLError.create(
                InvalidArgumentType,
                target="lags_to_construct",
                argument="lags_to_construct",
                actual_type=type(value),
                expected_types="dict",
                reference_code=ReferenceCodes._LAG_LEAD_LAG_TYPE,
            )
        # check if all keys are strings
        try:
            is_list_oftype(list(value.keys()), str)
        except AzureMLException:
            raise AzureMLError.create(
                TimeseriesDfColumnTypeNotSupported,
                target="value",
                reference_code=ReferenceCodes._LAG_LEAD_COLUMN_TYPE,
                col_name="list of columns",
                supported_type="string",
            )
        # check if every value is either list of ints or an int
        for v in value.values():
            if np.issubdtype(type(v), np.signedinteger):
                pass
            elif is_iterable_but_not_string(v):
                # This assert is to pass through mypy check, the condition above handles it.
                Contract.assert_true(isinstance(v, Iterable), "The value should be an iterable.", log_safe=True)
                v = cast(List[int], v)
                if len(v) == 0:
                    raise AzureMLError.create(
                        EmptyLagsForColumns, target="target_lags", reference_code=ReferenceCodes._LAG_LEAD_LAG_EMPTY
                    )
                for val in v:
                    if not np.issubdtype(type(val), np.signedinteger):
                        raise AzureMLError.create(
                            InvalidArgumentType,
                            target="lags_to_construct",
                            argument="lags_to_construct",
                            actual_type=type(val),
                            expected_types="int",
                            reference_code=ReferenceCodes._LAG_LEAD_LAG_TYPE_INT_LIST,
                        )
            else:
                raise AzureMLError.create(
                    InvalidArgumentType,
                    target="lags_to_construct",
                    argument="lags_to_construct",
                    actual_type=type(v),
                    expected_types="int, List[int]",
                    reference_code=ReferenceCodes._LAG_LEAD_LAG_TYPE_INT,
                )
        # all checks passed, can assign
        self._lags_to_construct = value

    @property
    def dropna(self) -> bool:
        """See `dropna` parameter."""
        return self._dropna

    @dropna.setter
    def dropna(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise AzureMLError.create(
                TimeseriesWrongDropnaParam, target="dropna", reference_code=ReferenceCodes._LAG_LEAD_DROPNA
            )
        self._dropna = value

    @property
    def max_horizon(self) -> int:
        """See `max_horizon` parameter."""
        return self._max_horizon

    @max_horizon.setter
    def max_horizon(self, value: int) -> None:
        self.verify_max_horizon_input(value)
        self._max_horizon = value

    @property
    def origin_time_colname(self) -> str:
        """See `origin_time_column_name` parameter."""
        return self._origin_time_colname

    @origin_time_colname.setter
    def origin_time_colname(self, value: str) -> None:
        if not isinstance(value, str):
            raise AzureMLError.create(
                TimeseriesDfColumnTypeNotSupported,
                target="value",
                reference_code=ReferenceCodes._LAG_LEAD_ORIGIN,
                col_name="origin_time_column_name",
                supported_type="string",
            )
        self._origin_time_colname = value

    @property
    def overwrite_columns(self) -> bool:
        """See `overwrite_columns` parameter."""
        return self._overwrite_columns

    @overwrite_columns.setter
    def overwrite_columns(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise AzureMLError.create(
                InvalidArgumentType,
                target="overwrite_columns",
                argument="overwrite_columns",
                actual_type=type(value),
                expected_types="bool",
                reference_code=ReferenceCodes._LAG_LEAD_OVERWRITE_COL,
            )
        self._overwrite_columns = value

    @property
    def freq(self) -> Optional[pd.DateOffset]:
        """Return the frequency of a transform."""
        return self._ts_freq.freq

    @freq.setter
    def freq(self, val: pd.DateOffset) -> None:
        """Set the frequency."""
        if val is not None and not isinstance(val, pd.DateOffset) and not isinstance(val, str):
            raise AzureMLError.create(
                InvalidArgumentType,
                target="freq",
                argument="freq",
                actual_type=type(val),
                expected_types="pd.DateOffset",
                reference_code=ReferenceCodes._LAG_LEAD_FREQ,
            )
        self._ts_freq = AutoMLForecastFreq(val)
        if isinstance(val, str) and self._ts_freq.freq is None:
            # Raise the exception if we were not able to convert string to frequency.
            str_to_offset_safe(val, ReferenceCodes._LAG_LEAD_FREQ_BAD_STR)

    ############################################################################
    # Private methods: all the work is done through them
    ############################################################################

    def _no_original_order_column_safe(self):
        return hasattr(self, "_no_original_order_column") and self._no_original_order_column

    def _add_occurrence_origin_column_safe(self):
        return hasattr(self, "_add_occurrence_origin_column") and self._add_occurrence_origin_column

    def _check_columns_to_lag(self, X: TimeSeriesDataSet) -> Dict[str, List[int]]:
        """
        Check from which columns user wants to construct lags.

        Exclude columns that are not in X or are properties of X.

        :param X: is a TimeSeriesDataSet

        :return: list of valid column labels which will be lagged.
        """
        # get a list of TSDF property columns, except ts_value_colname
        property_cols = set(X.data.index.names)
        if X.group_column_names is not None:
            property_cols = property_cols.union(X.group_column_names)

        # if asked to lag system cols, refuse and warn
        columns_to_lag = set(self.lags_to_construct.keys())
        columns_not_to_lag = columns_to_lag.intersection(property_cols)
        if len(columns_not_to_lag) > 0:
            warning_message = (
                "Some of the requested columns will not be "
                "lagged, since they are internal to TimeSeriesDataSet! "
                "Will not lag: {}".format(columns_not_to_lag)
            )
            columns_to_lag = columns_to_lag - columns_not_to_lag
            warn(warning_message, UserWarning)
        # if asked to lag columns that are not in TSDF, refuse and warn
        columns_not_in_df = columns_to_lag.difference(set(X.data.columns))
        if len(columns_not_in_df) > 0:
            warning_message = (
                "Some of the requested columns will not be "
                "lagged, since they are not present in the input "
                "TimeSeriesDataSet.! Will not lag: {}".format(columns_not_in_df)
            )
            columns_to_lag = columns_to_lag - columns_not_in_df
            warn(warning_message, UserWarning)
        # clean up the dict of arguments by turning values of ints into
        # a singleton list of ints
        lags_to_construct_safe = dict()
        for column, lag_orders in self.lags_to_construct.items():
            if column in columns_to_lag:
                lag_orders_list = lag_orders if isinstance(lag_orders, list) else [lag_orders]
                lags_to_construct_safe[column] = lag_orders_list
        return lags_to_construct_safe

    def _generate_new_column_names(self) -> List[str]:
        """Generate all new column names from a dictionary of inputs."""
        new_colnames = []
        for colname, lag_orders in self.lags_to_construct.items():
            if isinstance(lag_orders, int):
                lag_orders = [lag_orders]
            for order in lag_orders:
                # append "occurrence" to lag name to match names in "_construct_one_lag..." functions
                post_fix = LagLeadOperator._get_lag_col_common_postfix(
                    order, self.lag_option == self.LAG_BY_OCCURRENCE
                )
                post_fix += str(abs(order))
                post_fix += self._get_freq_name()
                new_colname = colname + post_fix
                new_colnames.append(new_colname)
        return new_colnames

    def _check_for_column_overwrites(self, X: TimeSeriesDataSet) -> None:
        """
        Check for whether existing TSDF columns are getting overwritten.

        Either a warning is printed or an exception is
        raised, depending on settings.
        """
        new_colnames = set(self._generate_new_column_names())
        input_colnames = set(X.data.columns)
        columns_to_overwrite = input_colnames.intersection(new_colnames)
        if len(columns_to_overwrite) > 0:
            warning_message = (
                "Some of the columns that are about to be "
                "created by LagLeadOperator already exist in the input "
                "TimeSeriesDataSet: {}. "
            )
            if self.overwrite_columns:
                warning_message = warning_message.format(columns_to_overwrite)
                warning_message += "They will be overwritten!"
                warn(warning_message, UserWarning)
            else:
                raise AzureMLError.create(
                    TimeseriesColumnNamesOverlap,
                    target="TimeSeriesDataSet",
                    class_name="LagLeadOperator",
                    column_names=", ".join(columns_to_overwrite),
                    reference_code=ReferenceCodes._LAG_LEAD_COLUMN_EXISTS,
                )

    ############################################################################
    # And the below logic handles lag_by_time features on inputs
    # with origin_time
    ############################################################################

    def _check_one_lag_inputs(self, X: TimeSeriesDataSet, lag_var: str, lag_order: int) -> None:
        """
        Validate that data frame, lag variable and lag order are valid.

        :param X: The data frame to generate lag on.
        :param lag_var: The name of lagging variable.
        :lag_order: the order of a lag.
        :raises: ForecastingConfigException,
                 ForecastingDataException
        """
        if not isinstance(lag_var, str):
            raise AzureMLError.create(
                TimeseriesDfColumnTypeNotSupported,
                target="lag_var",
                reference_code=ReferenceCodes._LAG_LEAD_COLUMN_TYPE_CONSTRUCT,
                col_name="lag_var",
                supported_type="string",
            )
        if not isinstance(lag_order, int):
            raise AzureMLError.create(
                InvalidArgumentType,
                target="lag_order",
                argument="lag_order",
                actual_type=type(lag_order),
                expected_types="int",
                reference_code=ReferenceCodes._LAG_LEAD_LAG_TYPE_CONSTRUCT,
            )
        if not isinstance(X, TimeSeriesDataSet):
            raise AzureMLError.create(
                TimeseriesInputIsNotTimeseriesDs, target="X", reference_code=ReferenceCodes._LAG_LEAD_NOT_TSDF
            )

    def _get_index_columns(self, tsds: TimeSeriesDataSet) -> List[str]:
        """
        Return time and grain index of a TimeSeriesDataSet.

        The origin column is omitted.
        :param tsds: The tinme series data set to get index from.
        :return: The list, representing index.
        """
        index = [tsds.time_column_name]
        if tsds.time_series_id_column_names:
            index += tsds.time_series_id_column_names
        return index

    def _construct_one_lag_by_time_with_origin(
        self, X: TimeSeriesDataSet, lag_var: str, lag_order: int
    ) -> pd.DataFrame:
        """
        Construct a single lag of a single variable.

        Should only be used on an argument with origin_time set.
        Returns a unindexed pandas DataFrame with a single column.
        :param X: The input data set.
        :param lag_var: The column name to construct lag for.
        :param lag_order: the order of a lag.
        :return: The data frame with single column with no index.
        """
        # check inputs
        self._check_one_lag_inputs(X, lag_var, lag_order)
        if X.origin_time_column_name is None:
            raise AzureMLError.create(
                TimeseriesOriginAbsent, reference_code=ReferenceCodes._LAG_LEAD_NO_ORIGIN, target="X"
            )
        # prepare pretty lag endings: foo_lagX
        lag_postfix = LagLeadOperator._get_lag_col_common_postfix(lag_order)
        lag_postfix += str(abs(lag_order))
        lag_postfix += self._get_freq_name()
        # when origin_time is not present, we have to artificially create one
        temp_df = X.data.reset_index()
        if lag_order == 1:
            # pandas bug: https://github.com/pandas-dev/pandas/issues/33683
            # may result in weird behavior when freq * 0 is applied. For that reason,
            # we will rely directly on the lagged origin column and not subtract
            # multiply by freq * 0.
            temp_df["lag_time"] = temp_df[X.origin_time_column_name]
        else:
            temp_df["lag_time"] = temp_df[X.origin_time_column_name] - cast(pd.DateOffset, self.freq) * (lag_order - 1)
        index_cols = self._get_index_columns(X)
        # now turn tdsf into a time series
        ts = X.extract_time_series(lag_var).reset_index()
        left_join_keys = ["lag_time"]
        if X.time_series_id_column_names:
            left_join_keys += X.time_series_id_column_names
        right_join_keys = index_cols
        # join creates all the lags and NaNs in the appropriate places
        temp_df = temp_df[left_join_keys]
        result = temp_df.merge(ts, how="left", left_on=left_join_keys, right_on=right_join_keys)
        df_with_lags = result[[lag_var]]
        df_with_lags.rename({lag_var: lag_var + lag_postfix}, axis=1, inplace=True)
        return df_with_lags

    def _pre_check_data(self, X: TimeSeriesDataSet) -> None:
        """
        Pre check data prior to generating lags for all columns.

        :param X: The time series data frame to be checked.
        :raises: ForecastingDataException, DataException
        """
        if not isinstance(X, TimeSeriesDataSet):
            raise AzureMLError.create(
                TimeseriesInputIsNotTimeseriesDs, target="X", reference_code=ReferenceCodes._LAG_LEAD_NOT_TSDF_ALL
            )

    def _construct_all_lags_by_time_with_origin(self, X: TimeSeriesDataSet) -> TimeSeriesDataSet:
        """Call _construct_one_lag in a loop over lags_to_construct."""
        # quick check that X is indeed a tsdf
        self._pre_check_data(X)
        if X.origin_time_column_name is None:
            raise AzureMLError.create(
                TimeseriesOriginAbsent, target="X", reference_code=ReferenceCodes._LAG_LEAD_NO_ORIGIN_ALL
            )
        df_with_lags = X.data.copy()
        # make sure we are not lagging columns that should not be lagged
        lags_to_construct_safe = self._check_columns_to_lag(X)
        columns_to_keep = []
        for lag_var, all_lag_orders in lags_to_construct_safe.items():
            for lag_order in all_lag_orders:
                lag = self._construct_one_lag_by_time_with_origin(X, lag_var, lag_order)
                lag_name = lag.columns[0]
                df_with_lags[lag_name] = lag[lag_name].values
                columns_to_keep.append(lag_name)
        # we need to return only lag columns to unify processing
        return TimeSeriesDataSet(
            df_with_lags[columns_to_keep],
            time_column_name=X.time_column_name,
            time_series_id_column_names=X.time_series_id_column_names,
            origin_time_column_name=X.origin_time_column_name,
        )

    ############################################################################
    # And the below logic handles lag_by_occurrence features generation
    # on inputs with horizon_origin
    ############################################################################

    def _construct_one_lag_by_occurrence_with_horizon_origin(
        self, X: TimeSeriesDataSet, lag_var: str, lag_order: int
    ) -> pd.DataFrame:
        """
        Construct a single lag_by_occurrence of a single variable.

        Returns a unindexed pandas DataFrame with a single column.
        :param X: The input data set.
        :param lag_var: The column name to construct lag for.
        :param lag_order: the order of a lag.
        :return: The data frame with single column with no index.
        """
        # check inputs
        self._check_one_lag_inputs(X, lag_var, lag_order)
        if TimeSeriesInternal.HORIZON_NAME not in X.data.columns:
            raise AzureMLError.create(
                TimeseriesHorizonAbsent, target="X", reference_code=ReferenceCodes._LAG_LEAD_NO_HORIZON
            )

        # prepare pretty lag endings: foo_occurrence_lagX
        lag_postfix = LagLeadOperator._get_lag_col_common_postfix(lag_order, True)
        lag_postfix += str(abs(lag_order))
        lag_postfix += self._get_freq_name()

        temp_df = X.data.reset_index()

        index_cols = self._get_index_columns(X)

        not_imputed_val = MissingDummiesTransformer.MARKER_VALUE_NOT_MISSING
        if not self._no_original_order_column_safe():
            # When TimeSeriesInternal.DUMMY_ORDER_COLUMN column is available,
            # we will rely on this column to remove imputed rows before
            # generating lag_by_occurrence features.
            # This is deprecated behavior and is only included for backwards compatibility
            if TimeSeriesInternal.DUMMY_ORDER_COLUMN in X.data.columns:
                if self._in_fit_transform:
                    target_dummies_name = MissingDummiesTransformer.get_column_name(cast(str, X.target_column_name))
                    X = X.from_data_frame_and_metadata(
                        X.data[
                            X.data[TimeSeriesInternal.DUMMY_ORDER_COLUMN].notnull() |
                            (X.data[target_dummies_name] == not_imputed_val)
                        ]
                    )
                else:
                    X = X.from_data_frame_and_metadata(X.data[X.data[TimeSeriesInternal.DUMMY_ORDER_COLUMN].notnull()])
        else:
            dummies_name = MissingDummiesTransformer.get_column_name(lag_var)
            if dummies_name in X.data.columns:
                X = X.from_data_frame_and_metadata(X.data[X.data[dummies_name] == not_imputed_val])

        # We will produce the occurrence lags from a version of the data where missing/imputed
        # values are removed - call this "ts"
        ts_cols = [lag_var, TimeSeriesInternal.HORIZON_NAME]
        ts = X.data[ts_cols].copy()
        # We will recompute the origin times anyway, so these can be dropped entirely
        ts.reset_index(level=X.origin_time_column_name, drop=True, inplace=True)
        ts.reset_index(inplace=True)

        # Enumerate the rows of ts in each time-sorted grain-horizon group
        # This sequence index will be a join key that  forms the lags
        if X.time_series_id_column_names:
            true_grain = X.time_series_id_column_names + [TimeSeriesInternal.HORIZON_NAME]
        else:
            true_grain = [TimeSeriesInternal.HORIZON_NAME]
        index_cols = [X.time_column_name] + true_grain
        ts.sort_values(by=[X.time_column_name], inplace=True, ascending=True)
        ts["temp_seq_record_index"] = ts.groupby(true_grain).cumcount() + 1

        # Left join ts's sequence index into the original input data by grain-horizon
        temp_df = temp_df.merge(
            ts[["temp_seq_record_index"] + index_cols], how="left", left_on=index_cols, right_on=index_cols
        )

        # Missing/imputed rows will not have a filled sequence index
        # If not filled, they will have missing values for lag features and be dropped from the data altogether
        # In order to maintain the data contract, try to impute sequence indices for these rows
        if temp_df["temp_seq_record_index"].isnull().values.any():
            # The correct filling strategy for the sequence index is to sort by time
            # within each grain-horizon group and then backfill missing values.
            # The backfill ensures that imputed rows receive the same index as the next
            # valid row - which will eventually lag back to the *previous* valid row
            max_index_by_grain = {
                tsid_h: ts_one["temp_seq_record_index"].max() + 1 for tsid_h, ts_one in ts.groupby(true_grain)
            }
            df_list = []
            for tsid_h, temp_df_one in temp_df.groupby(true_grain):
                temp_df_one_sorted = temp_df_one.sort_values(by=[X.time_column_name])
                if pd.isnull(temp_df_one_sorted["temp_seq_record_index"].iloc[-1]):
                    # Due to the backfill, need to manually fill the latest value in temp_df_one if
                    # it is missing/imputed
                    temp_df_one_sorted["temp_seq_record_index"].values[-1] = max_index_by_grain.get(tsid_h, np.nan)
                temp_df_one_sorted["temp_seq_record_index"].fillna(method="bfill", inplace=True)
                df_list.append(temp_df_one_sorted)

            temp_df = pd.concat(df_list, sort=False)
            # temp_df rows could be shuffled - put them back in their original order
            temp_df.sort_index(inplace=True)

        # Backward shift the sequence index in temp_df - after this operation, the sequence index
        # is part of a join key that will bring in lagged values
        temp_df["temp_seq_record_index"] = (
            temp_df["temp_seq_record_index"] - (temp_df[TimeSeriesInternal.HORIZON_NAME] - 1) - lag_order
        )
        left_join_keys = ["temp_seq_record_index"] + true_grain
        right_join_keys = ["temp_seq_record_index"] + true_grain

        # join creates all the lags and NaNs in the appropriate places
        temp_df = temp_df[left_join_keys]
        result = temp_df.merge(ts, how="left", left_on=left_join_keys, right_on=right_join_keys)
        # The dates in the result DataFrame are the dates corresponding to the lagged values
        # Return these dates since they can be useful i.e. as by-occurrence origin times
        df_with_lags = result[[lag_var, X.time_column_name]]
        df_with_lags.rename(columns={lag_var: lag_var + lag_postfix}, inplace=True)

        return df_with_lags

    def _construct_all_lags_by_occurrence_with_horizon_origin(self, X: TimeSeriesDataSet) -> TimeSeriesDataSet:
        """Call _construct_one_lag in a loop over lags_to_construct."""
        # quick check that X is indeed a tsdf
        self._pre_check_data(X)
        if TimeSeriesInternal.HORIZON_NAME not in X.data.columns:
            raise AzureMLError.create(
                TimeseriesHorizonAbsent, target="X", reference_code=ReferenceCodes._LAG_LEAD_NO_HORIZON_ALL
            )
        df_with_lags = X.data.copy()

        # make sure we are not lagging columns that should not be lagged
        lags_to_construct_safe = self._check_columns_to_lag(X)
        columns_to_keep = []
        new_origins = None
        for lag_var, all_lag_orders in lags_to_construct_safe.items():
            for lag_order in all_lag_orders:
                lag = self._construct_one_lag_by_occurrence_with_horizon_origin(X, lag_var, lag_order)
                if lag_var == X.target_column_name and lag_order == 1:
                    new_origins = pd.DatetimeIndex(lag[X.time_column_name])
                lag_name = lag.columns[0]
                df_with_lags[lag_name] = lag[lag_name].values
                columns_to_keep.append(lag_name)

        if self._add_occurrence_origin_column_safe():
            if new_origins is None:
                # If we need new origin times compute them from the lag-1 on the target column
                lag = self._construct_one_lag_by_occurrence_with_horizon_origin(X, cast(str, X.target_column_name), 1)
                new_origins = pd.DatetimeIndex(lag[X.time_column_name])
            df_with_lags[TimeSeriesInternal.ORIGIN_TIME_OCCURRENCE_COLUMN_NAME] = new_origins
            columns_to_keep.append(TimeSeriesInternal.ORIGIN_TIME_OCCURRENCE_COLUMN_NAME)

        # we need to return only lag columns to unify processing
        return TimeSeriesDataSet(
            df_with_lags[columns_to_keep],
            time_column_name=X.time_column_name,
            time_series_id_column_names=X.time_series_id_column_names,
            origin_time_column_name=X.origin_time_column_name,
        )

    def _set_lag_option(self, X: TimeSeriesDataSet) -> None:
        """
        Set lag option such that it is determined in the fit()
        """
        lags_to_construct_safe = self._check_columns_to_lag(X)
        if len(lags_to_construct_safe) > 0:
            for lag_col in self.lags_to_construct.keys():
                target_dummies_name = MissingDummiesTransformer.get_column_name(lag_col)
                is_imputed_val = MissingDummiesTransformer.MARKER_VALUE_MISSING
                if target_dummies_name not in X.data.columns:
                    num_missing_values = 0
                else:
                    num_missing_values = (
                        X.data[target_dummies_name].isna() | X.data[target_dummies_name] == is_imputed_val
                    ).sum()
                if num_missing_values / X.data.shape[0] < self.SPARSITY_THRESHOLD:
                    # Data is (almost) evenly spaced, we will do lag_by_time
                    self.lag_option = LagLeadOperator.LAG_BY_TIME
                else:
                    # Data is not evenly spaced, we will do lag_by_occurrence
                    self.lag_option = LagLeadOperator.LAG_BY_OCCURRENCE
                    break

    def _cache_trailing_training_data(self, X: TimeSeriesDataSet) -> "LagLeadOperator":
        """
        Cache the tail end of the training data.

        When transforming test data, we should not have NaNs at the start
        because we can use tail bits of training data to obtain them.
        """
        # quick check that X is indeed a tsdf
        if not isinstance(X, TimeSeriesDataSet):
            raise AzureMLError.create(
                TimeseriesInputIsNotTimeseriesDs, target="X", reference_code=ReferenceCodes._LAG_LEAD_NOT_TSDF_CACHE
            )

        # find largest lag value that needs to be constructed
        lags_to_construct_safe = self._check_columns_to_lag(X)
        if len(lags_to_construct_safe) > 0:
            lags_inverse_dict = invert_dict_of_lists(lags_to_construct_safe)
            max_lag_order = max(lags_inverse_dict.keys())

            # Internal function to get trailing data for a single grain
            def get_trailing_by_grain(gr, Xgr):
                tsds_one = X.from_data_frame_and_metadata(Xgr, False)
                h_max = self.max_horizon_from_key_safe(gr, self.max_horizon)
                last_obs_for_cache = max_lag_order + h_max + 1
                val_series = cast(pd.Series, tsds_one.target_values).sort_index(level=X.time_column_name)
                tail_series = val_series.iloc[-last_obs_for_cache:]
                tail_start = tail_series.index.get_level_values(X.time_column_name).min()
                return Xgr[Xgr.index.get_level_values(X.time_column_name) >= tail_start]

            # ------------------------------------------------------------
            if self.lag_option == LagLeadOperator.LAG_BY_OCCURRENCE:
                # Find a selection of rows for which at least one of the variables to be lagged is not imputed
                sel_not_imputed = pd.Series(False, index=X.data.index)
                not_imputed_val = MissingDummiesTransformer.MARKER_VALUE_NOT_MISSING
                for lag_col in lags_to_construct_safe.keys():
                    missing_dummies_name = MissingDummiesTransformer.get_column_name(lag_col)
                    if missing_dummies_name in X.data.columns:
                        # Turn on the selection for rows marked as not imputed
                        sel_not_imputed |= X.data[missing_dummies_name] == not_imputed_val
                    else:
                        # In this case, assume nothing is imputed
                        sel_not_imputed |= True
                        break

                # Remove rows where all variables to be lagged are imputed
                # No reason to keep these in the cache for lag-by-occurrence
                X = X.from_data_frame_and_metadata(X.data[sel_not_imputed])

            # take last max_lag_order obs per grain
            if X.time_series_id_column_names:
                df_cache = X.groupby_time_series_id().apply(
                    lambda Xgr: get_trailing_by_grain(Xgr.name, Xgr)
                )  # type: pd.DataFrame
            else:
                df_cache = get_trailing_by_grain("", X.data)
            self._cache = X.from_data_frame_and_metadata(df_cache)
            # For generating lag_by_time features, if cache contains the
            # missing value, it will result in the degradation of
            # a shape of transformed data on the data set
            # missing y values.
            # We backfill these values if backfill_cache is true.
            if self.lag_option == LagLeadOperator.LAG_BY_TIME:
                if self._cache is not None and self.backfill_cache:
                    ts_imputer = TimeSeriesImputer(
                        input_column=cast(str, self._cache.target_column_name),
                        option="fillna",
                        method="bfill",
                        freq=self.freq,
                    )
                    self._cache = ts_imputer.transform(self._cache)
        else:
            self._cache = None

        return self

    ############################################################################
    # Last, we have publicly facing fit and predict methods
    ############################################################################

    # fit method performs caching of tail bits of training data, this way
    # lags on test data are populated with non-missing values from train
    @function_debug_log_wrapped(logging.INFO)
    def fit(self, X: TimeSeriesDataSet, y: Optional[Any] = None) -> "LagLeadOperator":
        """
        Fit the lag/lead transform.

        This method performs caching of tail bits of training data, this way
        lags on test data are populated with non-missing values from train

        :param X: Input data
        :type X: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet

        :param y: Ignored. Included for pipeline compatibility

        :return: Fitted transform
        :rtype: azureml.automl.runtime.featurizer.transformer.timeseries.lag_lead_operator.LagLeadOperator
        """
        # TODO: write unit test for setting freq.
        if self.freq is None:
            self.freq = X.infer_freq()
        self._set_lag_option(X)
        self._check_for_column_overwrites(X)
        self._cache_trailing_training_data(X)
        self._is_fit = True

        return self

    @function_debug_log_wrapped(logging.INFO)
    def transform(self, X: TimeSeriesDataSet) -> TimeSeriesDataSet:
        """
        Construct lag columns in TimeSeriesDataSet X.

        :param X: Input data
        :type X: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet

        :return: Data frame with lag/lead columns
        :rtype: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        """
        if not self._is_fit:
            raise AzureMLError.create(FitNotCalled, target="fit", reference_code=ReferenceCodes._LAG_LEAD_NO_FIT)

        # logic:
        #   1) create copy of input data
        #   2) attempt to prepend the cache to it (will fail for training data)
        #   3) call method to do lags in a loop
        #   4) left join back to original data to trim off the early rows

        output = X.data.copy()
        # this should work without errors when applied to test data
        # under the assumption that test comes after train :)
        if (
            self._no_original_order_column_safe() and
            self.lag_option == LagLeadOperator.LAG_BY_OCCURRENCE and
            self._cache is not None
        ):
            # If we're not using the order column and we're lagging by occurrence,
            # make sure we have missing indicator columns for every column we're lagging
            # Otherwise, the concat call could add a missing indicator to X and fill it with NaN
            # this can have unwanted consequences
            lags_to_construct_safe = self._check_columns_to_lag(X)
            for lag_col in lags_to_construct_safe.keys():
                missing_dummies_name = MissingDummiesTransformer.get_column_name(lag_col)
                if missing_dummies_name in self._cache.data.columns:
                    Contract.assert_true(
                        missing_dummies_name in X.data.columns,
                        "Cache contains a missing value indicator, but input data does not",
                        log_safe=True,
                    )
        try:
            # Default behavior when axis isn't provided was to sort in pandas 0.23.
            # In order to preserve this behavior and upgrade to pandas 0.25, this sort
            # was added to suppress warnings and keep behavior.
            if self._cache is not None:
                # We are taking self._cache.data here, because it may contain target column,
                # missing in X.
                temp_output = self._cache.concat([self._cache.data, output], sort=True, validate=True)
            else:
                temp_output = X.from_data_frame_and_metadata(output)
        # exception will be thrown when applied to train data since TSDF
        # will not allow to prepend a part of it to itself
        except AzureMLException as ex:
            if ex._azureml_error._error_definition.__class__ == TimeseriesDfDuplicatedIndex:
                # Check if the error code is TimeseriesDfDuplicatedIndex.
                temp_output = X.from_data_frame_and_metadata(output.copy())
            else:
                # Otherwise raise the exception.
                raise

        if self.lag_option == LagLeadOperator.LAG_BY_OCCURRENCE:
            if TimeSeriesInternal.HORIZON_NAME not in X.data.columns:
                temp_output = MaxHorizonFeaturizer(
                    self.max_horizon, origin_time_colname=self.origin_time_colname
                ).fit_transform(temp_output)
            # actual lags implemented in a separate internal method
            interim_output = self._construct_all_lags_by_occurrence_with_horizon_origin(temp_output)

            # this join makes sure that all rows that were not in the input TSDF
            # get eliminated by left join semantics
            # small step: avoiding duplicating columns
            # must take feature columns from right
            feature_columns = interim_output.data.columns
            non_feature_columns = output.columns.difference(feature_columns)
            # also suppress warnings from joins
            filterwarnings("ignore")
            result = output[non_feature_columns].merge(
                interim_output.data[feature_columns], how="left", left_index=True, right_index=True
            )
            filterwarnings("default")

            # we need to do a little more work if dropna is True
            # don't want to drop rows where NaNs are not caused by the LagOperator
            if self.dropna:
                notnull_by_column = result[feature_columns].notnull().values
                not_null_all_cols = np.apply_along_axis(all, 1, notnull_by_column)
                result = result[not_null_all_cols]

        if self.lag_option == LagLeadOperator.LAG_BY_TIME:
            if X.origin_time_column_name is None:
                temp_output = self.create_origin_times(
                    temp_output, self.max_horizon, freq=self.freq, origin_time_colname=self.origin_time_colname
                )
            # Set the flag for train and test set for backwards compatibility only
            # Can be safely deleted after the next stable SDK is rolled out.
            IN_FIT_TRANSFORM = "_in_fit_transform"
            if not hasattr(self, IN_FIT_TRANSFORM):
                setattr(self, IN_FIT_TRANSFORM, False)

            # actual lags implemented in a separate internal method
            interim_output = self._construct_all_lags_by_time_with_origin(temp_output)

            # this join makes sure that all rows that were not in the input TSDF
            # get eliminated by left join semantics
            # small step: avoiding duplicating columns
            # must take feature columns from right
            feature_columns = interim_output.data.columns
            non_feature_columns = output.columns.difference(feature_columns)
            # also suppress warnings from joins
            filterwarnings("ignore")
            result = output[non_feature_columns].merge(
                interim_output.data[feature_columns], how="left", left_index=True, right_index=True
            )
            filterwarnings("default")

            # we need to do a little more work if dropna is True
            # don't want to drop rows where NaNs are not caused by the LagOperator
            if self.dropna:
                notnull_by_column = result[feature_columns].notnull().values
                not_null_all_cols = np.apply_along_axis(all, 1, notnull_by_column)
                result = result[not_null_all_cols]

        target_column_name = None
        if temp_output.target_column_name and temp_output.target_column_name in result.columns:
            target_column_name = temp_output.target_column_name
        return TimeSeriesDataSet(
            result,
            X.time_column_name,
            X.time_series_id_column_names,
            temp_output.origin_time_column_name,
            target_column_name=target_column_name,
            group_column_names=X.group_column_names,
        )

    @function_debug_log_wrapped(logging.INFO)
    def fit_transform(
        self, X: TimeSeriesDataSet, y: Optional[np.ndarray] = None, **fit_params: Any
    ) -> TimeSeriesDataSet:
        """When fit_transform() is called, perform it and set the '_in_fit_transform' flag to False.
        This flag signals that we are in the test set. This is needed for generating lags by occurrence.
        """
        self._in_fit_transform = True
        rv = super(LagLeadOperator, self).fit_transform(X, y, **fit_params)  # type: TimeSeriesDataSet
        self._in_fit_transform = False
        return rv

    def preview_column_names(self, tsds: TimeSeriesDataSet, with_origin: bool = False) -> List[str]:
        """
        Get the lag lead features names that would be made if the transform were applied to X.

        :param tsds: The TimeSeriesDataSet to generate column names for.
        :type tsds: azureml.automl.runtime._time_series_data_set.TimeSeriesDataSet
        :param with_origin: Return 'origin' column name if it was created.
        :type with_origin: bool

        :return: lag lead feature names
        :rtype: list[str]

        """
        if self.freq is None:
            self.freq = tsds.infer_freq()
        # set appropriate lag_by option if the function is called directly
        if not self._is_fit:
            self._set_lag_option(tsds)
        new_cols = self._generate_new_column_names()
        if with_origin:
            new_cols.append(self.origin_time_colname)
        self._lag_columns = new_cols
        return new_cols

    @staticmethod
    def _get_lag_col_common_postfix(lag_order: int, has_occurrence: Optional[bool] = False) -> str:
        """Get the common part in the postfix of the columns generated by LagLeadOperator."""
        post_fix = LagLeadOperator.LAG_POSTFIX if lag_order > 0 else LagLeadOperator.LEAD_POSTFIX
        post_fix = LagLeadOperator.POSTFIX_SEP + post_fix
        if has_occurrence:
            post_fix = LagLeadOperator.POSTFIX_SEP + LagLeadOperator.OCCURRENCE_POSTFIX + post_fix
        return post_fix

    @staticmethod
    def get_col_internal_type(col_name: str) -> Optional[str]:
        """
        Get the type of a column if it is generated by lag lead operator.

        :param col_name: The column name.
        :return: If column is generated by lag lead operator, return lag/lead/occurrence_lag/occurrence_lead,
                 else None.
        """
        for has_occurrence in [True, False]:
            for order in [-1, 1]:
                lag_postfix = LagLeadOperator._get_lag_col_common_postfix(order, has_occurrence)
                if re.search("{}[0-9a-zA-Z-]+$".format(lag_postfix), col_name) is not None:
                    return lag_postfix[1:]
        return None

    def __setstate__(self, state: Dict[Any, Any]) -> None:
        if not isinstance(state['_ts_freq'], AutoMLForecastFreq):
            state['_ts_freq'] = AutoMLForecastFreq(state['_ts_freq'])
        super().__setstate__(state)

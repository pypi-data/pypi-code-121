# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import math
import uuid
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import nimbusml
import numpy as np
import pandas as pd
from pandas.tseries.frequencies import to_offset
from scipy.stats import norm
from sklearn.pipeline import Pipeline as SKPipeline

from .._constants import TimeSeries, TimeSeriesInternal
from .._diagnostics.azureml_error import AzureMLError, AzureMLException
from .._diagnostics.contract import Contract
from .._diagnostics.error_definitions import (
    AutoMLInternal,
    DataShapeMismatch,
    ErrorDefinition,
    ForecastHorizonExceeded,
    ForecastingEmptyDataAfterAggregation,
    ForecastPredictNotSupported,
    GenericFitError,
    InvalidArgumentType,
    MissingColumnsInData,
    PandasDatetimeConversion,
    QuantileRange,
    TimeseriesContextAtEndOfY,
    TimeseriesDfContainsNaN,
    TimeseriesDfInvalidArgFcPipeYOnly,
    TimeseriesDfInvalidArgOnlyOneArgRequired,
    TimeseriesGrainAbsentNoDataContext,
    TimeseriesGrainAbsentNoGrainInTrain,
    TimeseriesGrainAbsentNoLastDate,
    TimeseriesInsufficientDataForecast,
    TimeseriesMissingValuesInY,
    TimeseriesNoDataContext,
    TimeseriesNonContiguousTargetColumn,
    TimeseriesNothingToPredict,
    TimeseriesNoUsableGrains,
    TimeseriesWrongShapeDataEarlyDest,
    TimeseriesWrongShapeDataSizeMismatch,
)
from .._diagnostics.error_strings import _generic_fit_error_message, _generic_prediction_error_message
from .._diagnostics.errors import PredictionException
from .._diagnostics.reference_codes import ReferenceCodes
from .._types import GrainType
from ..featurization.timeseries.timeseries_transformer import TimeSeriesTransformer
from ..featurization.utilities import get_min_points
from ..timeseries import _freq_aggregator, forecasting_utilities
from ..timeseries._frequency_fixer import fix_data_set_regularity_may_be
from ..timeseries._time_series_column_helper import convert_check_grain_value_types
from ..timeseries._time_series_data_config import TimeSeriesDataConfig
from ..timeseries._time_series_data_set import TimeSeriesDataSet

logger = logging.getLogger(__name__)


class RegressionPipeline(SKPipeline):
    """
    A pipeline with quantile predictions.

    This pipeline is a wrapper on the sklearn.pipeline.Pipeline to
    provide methods related to quantile estimation on predictions.
    """

    def __init__(self, pipeline: Union[SKPipeline, nimbusml.Pipeline], stddev: Union[float, List[float]]) -> None:
        """
        Create a pipeline.

        :param pipeline: The pipeline to wrap.
        :param stddev:
            The standard deviation of the residuals from validation fold(s).
        """
        # We have to initiate the parameters from the constructor to avoid warnings.
        self.pipeline = pipeline
        if not isinstance(stddev, list):
            stddev = [stddev]
        self._stddev = stddev  # type: List[float]
        if isinstance(pipeline, nimbusml.Pipeline):
            super().__init__([("nimbusml_pipeline", pipeline)])
        else:
            super().__init__(pipeline.steps, memory=pipeline.memory)
        self._quantiles = [0.5]

    @property
    def stddev(self) -> List[float]:
        """The standard deviation of the residuals from validation fold(s)."""
        return self._stddev

    @property
    def quantiles(self) -> List[float]:
        """Quantiles for the pipeline to predict."""
        return self._quantiles

    @quantiles.setter
    def quantiles(self, quantiles: Union[float, List[float]]) -> None:
        if not isinstance(quantiles, list):
            quantiles = [quantiles]

        for quant in quantiles:
            if quant <= 0 or quant >= 1:
                raise AzureMLError.create(QuantileRange, target="quantiles", quantile=str(quant))

        self._quantiles = quantiles

    def predict_quantiles(self, X: Any, **predict_params: Any) -> pd.DataFrame:
        """
        Get the prediction and quantiles from the fitted pipeline.

        :param X: The data to predict on.
        :return: The requested quantiles from prediction.
        :rtype: pandas.DataFrame
        """
        try:
            pred = self.predict(X, **predict_params)
        except Exception as e:
            raise PredictionException.from_exception(e, has_pii=True, target="RegressionPipeline").with_generic_msg(
                _generic_prediction_error_message.format(self.__class__.__name__)
            )
        return self._get_ci(pred, np.full(len(pred), self._stddev[0]), self._quantiles)

    def _get_ci(self, y_pred: np.ndarray, stddev: np.ndarray, quantiles: List[float]) -> pd.DataFrame:
        """
        Get Confidence intervales for predictions.

        :param y_pred: The predicted values.
        :param stddev: The standard deviations.
        :param quantiles: The desired quantiles.
        """
        res = pd.DataFrame()
        for quantile in quantiles:
            ci_bound = 0.0
            if quantile != 0.5:
                z_score = norm.ppf(quantile)
                ci_bound = z_score * stddev
            res[quantile] = pd.Series(y_pred + ci_bound)
        return res


class ForecastingPipelineWrapper(RegressionPipeline):
    """A pipeline for forecasting."""

    # Constants for errors and warnings
    # Non recoverable errors.
    FATAL_WRONG_DESTINATION_TYPE = (
        "The forecast_destination argument has wrong type, " "it is a {}. We expected a datetime."
    )
    FATAL_DATA_SIZE_MISMATCH = "The length of y_pred is different from the X_pred"
    FATAL_WRONG_X_TYPE = "X_pred has unsupported type, x should be pandas.DataFrame, " "but it is a {}."
    FATAL_WRONG_Y_TYPE = "y_pred has unsupported type, y should be numpy.array or pandas.DataFrame, " "but it is a {}."
    FATAL_NO_DATA_CONTEXT = (
        "No y values were provided for one of time series. "
        "We expected non-null target values as prediction context because there "
        "is a gap between train and test and the forecaster "
        "depends on previous values of target. "
    )
    FATAL_NO_DESTINATION_OR_X_PRED = (
        "Input prediction data X_pred and forecast_destination are both None. " +
        "Please provide either X_pred or a forecast_destination date, but not both."
    )
    FATAL_DESTINATION_AND_X_PRED = (
        "Input prediction data X_pred and forecast_destination are both set. " +
        "Please provide either X_pred or a forecast_destination date, but not both."
    )
    FATAL_DESTINATION_AND_Y_PRED = (
        "Input prediction data y_pred and forecast_destination are both set. " +
        "Please provide either y_pred or a forecast_destination date, but not both."
    )
    FATAL_Y_ONLY = "If y_pred is provided X_pred should not be None."
    FATAL_NO_LAST_DATE = (
        "The last training date was not provided." "One of time series in scoring set was not present in training set."
    )
    FATAL_EARLY_DESTINATION = (
        "Input prediction data X_pred or input forecast_destination contains dates " +
        "prior to the latest date in the training data. " +
        "Please remove prediction rows with datetimes in the training date range " +
        "or adjust the forecast_destination date."
    )
    FATAL_NO_TARGET_IN_Y_DF = "The y_pred is a data frame, " "but it does not contain the target value column"
    FATAL_WRONG_QUANTILE = "Quantile should be a number between 0 and 1 (not inclusive)."

    FATAL_NO_GRAIN_IN_TRAIN = (
        "One of time series was not present in the training data set. "
        "Please remove it from the prediction data set to proceed."
    )
    FATAL_NO_TARGET_IMPUTER = "No target imputers were found in TimeSeriesTransformer."
    FATAL_NONPOSITIVE_HORIZON = "Forecast horizon must be a positive integer."

    # Constants
    TEMP_PRED_COLNAME = "__predicted"

    def __init__(self, pipeline: SKPipeline, stddev: List[float]) -> None:
        """
        Create a pipeline.

        :param pipeline: The pipeline to wrap.
        :type pipeline: sklearn.pipeline.Pipeline
        :param stddev:
            The standard deviation of the residuals from validation fold(s).
        """
        super().__init__(pipeline, stddev)
        for _, transformer in pipeline.steps:
            # FIXME: Work item #400231
            if type(transformer).__name__ == "TimeSeriesTransformer":
                ts_transformer = transformer

        if "ts_transformer" not in vars() or ts_transformer is None:
            raise AzureMLError.create(
                AutoMLInternal,
                target="ForecastingPipelineWrapper",
                error_details="Failed to initialize ForecastingPipelineWrapper: {}".format(
                    ForecastingPipelineWrapper.FATAL_NO_TS_TRANSFORM
                ),
            )
        y_transformer = None
        if hasattr(self.pipeline, "y_transformer"):
            y_transformer = self.pipeline.y_transformer

        self._ts_transformer = ts_transformer
        self._y_transformer = y_transformer
        self._origin_col_name = ts_transformer.origin_column_name
        self._time_col_name = ts_transformer.time_column_name
        self._quantiles = [0.5]
        self._horizon_idx = None  # type: Optional[int]
        self.grain_column_names = ts_transformer.grain_column_names
        self.target_column_name = ts_transformer.target_column_name
        self.data_frequency = ts_transformer.freq_offset
        self.forecast_origin = {}  # type: Dict[GrainType, pd.Timestamp]

    def __setstate__(self, state):
        if "_y_transformer" not in state:
            state["_y_transformer"] = None
        self.__dict__.update(state)

    @property
    def time_column_name(self) -> str:
        """Return the name of the time column."""
        return cast(str, self._time_col_name)

    @property
    def origin_col_name(self) -> str:
        """Return the origin column name."""
        # Note this method will return origin column name,
        # which is only used for reconstruction of a TimeSeriesDataSet.
        # If origin column was introduced during transformation it is still None
        # on ts_transformer.
        if self._origin_col_name is None:
            self._origin_col_name = self._ts_transformer.origin_column_name
        # TODO: Double check type: Union[str, List[str]]
        ret = self._origin_col_name if self._origin_col_name else TimeSeriesInternal.ORIGIN_TIME_COLNAME_DEFAULT
        return cast(str, ret)

    def _check_data(
        self, X_pred: pd.DataFrame, y_pred: Union[pd.DataFrame, np.ndarray], forecast_destination: pd.Timestamp
    ) -> None:
        """
        Check the user input.

        :param X_pred: the prediction dataframe combining X_past and X_future in a time-contiguous manner.
                       Empty values in X_pred will be imputed.
        :param y_pred: the target value combining definite values for y_past and missing values for Y_future.
        :param forecast_destination: Forecast_destination: a time-stamp value.
                                     Forecasts will be made all the way to the forecast_destination time,
                                     for all grains. Dictionary input { grain -> timestamp } will not be accepted.
                                     If forecast_destination is not given, it will be imputed as the last time
                                     occurring in X_pred for every grain.
        :raises: DataException

        """
        # Check types
        # types are not PII
        if X_pred is not None and not isinstance(X_pred, pd.DataFrame):
            raise AzureMLError.create(
                InvalidArgumentType,
                target="X_pred",
                reference_code=ReferenceCodes._TSDF_INVALID_ARG_FC_PIPELINE_X_PRED,
                argument="X_pred",
                expected_types="pandas.DataFrame",
                actual_type=str(type(X_pred)),
            )
        if y_pred is not None and not isinstance(y_pred, pd.DataFrame) and not isinstance(y_pred, np.ndarray):
            raise AzureMLError.create(
                InvalidArgumentType,
                target="y_pred",
                reference_code=ReferenceCodes._TSDF_INVALID_ARG_FC_PIPELINE_Y_PRED,
                argument="y_pred",
                expected_types="numpy.array or pandas.DataFrame",
                actual_type=str(type(y_pred)),
            )
        if (
            forecast_destination is not None and
            not isinstance(forecast_destination, pd.Timestamp) and
            not isinstance(forecast_destination, np.datetime64)
        ):
            raise AzureMLError.create(
                InvalidArgumentType,
                target="forecast_destination",
                reference_code=ReferenceCodes._TSDF_INVALID_ARG_FC_PIPELINE_FC_DES,
                argument="forecast_destination",
                expected_types="pandas.Timestamp, numpy.datetime64",
                actual_type=str(type(forecast_destination)),
            )
        # Check wrong parameter combinations.
        if (forecast_destination is None) and (X_pred is None):
            raise AzureMLError.create(
                TimeseriesDfInvalidArgOnlyOneArgRequired,
                target="forecast_destination, X_pred",
                reference_code=ReferenceCodes._TSDF_INVALID_ARG_FC_PIPELINE_NO_DESTINATION_OR_X_PRED,
                arg1="X_pred",
                arg2="forecast_destination",
            )
        if (forecast_destination is not None) and (X_pred is not None):
            raise AzureMLError.create(
                TimeseriesDfInvalidArgOnlyOneArgRequired,
                target="forecast_destination, X_pred",
                reference_code=ReferenceCodes._TSDF_INVALID_ARG_FC_PIPELINE_DESTINATION_AND_X_PRED,
                arg1="X_pred",
                arg2="forecast_destination",
            )
        if (forecast_destination is not None) and (y_pred is not None):
            raise AzureMLError.create(
                TimeseriesDfInvalidArgOnlyOneArgRequired,
                target="forecast_destination, y_pred",
                reference_code=ReferenceCodes._TSDF_INVALID_ARG_FC_PIPELINE_DESTINATION_AND_Y_PRED,
                arg1="y_pred",
                arg2="forecast_destination",
            )
        if X_pred is None and y_pred is not None:
            # If user provided only y_pred raise the error.
            raise AzureMLError.create(
                TimeseriesDfInvalidArgFcPipeYOnly,
                target="X_pred, y_pred",
                reference_code=ReferenceCodes._TSDF_INVALID_ARG_FC_PIPELINE_Y_ONLY,
            )

    def _check_convert_grain_types(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Check that the grains have the correct type.

        :param X: The test data frame.
        :return: The same data frame with grain columns converted.
        """
        effective_grain = self.grain_column_names  # type: Optional[List[str]]
        if (
            self.grain_column_names == [TimeSeriesInternal.DUMMY_GRAIN_COLUMN] and
            self.grain_column_names[0] not in X.columns
        ):
            effective_grain = None
        # Try to convert the grain type if TS transformer has learned it first.
        X = self._ts_transformer._convert_grain_type_safe(X)
        X, _ = convert_check_grain_value_types(
            X,
            None,
            effective_grain,
            self._ts_transformer._featurization_config.__dict__,
            ReferenceCodes._TS_VALIDATION_GRAIN_TYPE_INFERENCE,
        )
        return X

    def short_grain_handling(self) -> bool:
        """Return true if short or absent grains handling is enabled for the model."""
        return (
            forecasting_utilities.get_pipeline_step(
                self._ts_transformer.pipeline, TimeSeriesInternal.SHORT_SERIES_DROPPEER
            )
            is not None
        )

    def is_grain_dropped(self, grain: GrainType) -> bool:
        """
        Return true if the grain is going to be dropped.

        :param grain: The grain to test if it will be dropped.
        :return: True if the grain will be dropped.
        """
        dropper = forecasting_utilities.get_pipeline_step(
            self._ts_transformer.pipeline, TimeSeriesInternal.SHORT_SERIES_DROPPEER
        )
        return dropper is not None and grain not in dropper.grains_to_keep

    def _check_max_horizon_and_grain(self, grain: GrainType, df_one: pd.DataFrame, ignore_data_errors: bool) -> None:
        """
        Raise error if the prediction data frame dates exceeds the max_horizon.

        :param grain: The tuple, designating grain.
        :param df_one: The data frame corresponding to a single grain.

        """
        last_train = self._ts_transformer.dict_latest_date.get(grain)
        # The grain was not met in the train data set. Throw the error.
        if last_train is None:
            if self.short_grain_handling():
                # We return here from this function, because this grain has to be dropped
                # during transform.
                return
            else:
                raise AzureMLError.create(
                    TimeseriesGrainAbsentNoGrainInTrain,
                    target="grain",
                    reference_code=ReferenceCodes._TS_GRAIN_ABSENT_MDL_WRP_CHK_GRAIN,
                    grain=grain,
                )
        if self._lag_or_rw_enabled():
            last_known = self._get_last_y_one_grain(df_one, grain, ignore_data_errors)
            if last_known is not None:
                last_known = max(self._ts_transformer.dict_latest_date[grain], last_known)
            else:
                last_known = last_train
                # If there is a gap between train and test, then the last known date will be one
                # period before the test set.
                if ignore_data_errors:
                    last_known = max(last_known, df_one[self.time_column_name].min() - self.data_frequency)
            horizon = (len(pd.date_range(start=last_known,
                                         end=df_one[self.time_column_name].max(),
                                         freq=self.data_frequency)) - 1)
            if horizon > self._ts_transformer.max_horizon:
                raise AzureMLError.create(ForecastHorizonExceeded, target="horizon")

    def _do_check_max_horizon(self, grain: GrainType, df_one: pd.DataFrame, ignore_data_errors: bool) -> bool:
        """
        Check whether the prediction data frame dates exceeds the max_horizon.

        :param grain: The tuple, designating grain.
        :param df_one: The data frame corresponding to a single grain.
        :param ignore_data_errors: Ignore errors in user data.
        :returns: True/False whether max_horizon is exceeded.

        """
        try:
            self._check_max_horizon_and_grain(grain, df_one, ignore_data_errors)
        # Exceeding maximum horizon is no longer an error.
        except AzureMLException as ex:
            if ex._azureml_error._error_definition == ForecastHorizonExceeded:
                return True
            raise
        return False

    def _create_prediction_data_frame(
        self,
        X_pred: pd.DataFrame,
        y_pred: Union[pd.DataFrame, np.ndarray],
        forecast_destination: pd.Timestamp,
        ignore_data_errors: bool,
    ) -> pd.DataFrame:
        """
        Create the data frame which will be used for prediction purposes.

        :param X_pred: the prediction dataframe combining X_past and X_future in a time-contiguous manner.
                       Empty values in X_pred will be imputed.
        :param y_pred: the target value combining definite values for y_past and missing values for Y_future.
        :param forecast_destination: Forecast_destination: a time-stamp value.
                                     Forecasts will be made all the way to the forecast_destination time,
                                     for all grains. Dictionary input { grain -> timestamp } will not be accepted.
                                     If forecast_destination is not given, it will be imputed as the last time
                                     occurring in X_pred for every grain.
        :param ignore_data_errors: Ignore errors in user data.
        :returns: The clean data frame.
        :raises: DataException

        """
        if X_pred is not None:
            X_copy = X_pred.copy()
            X_copy.reset_index(inplace=True, drop=True)
            if (
                self.grain_column_names[0] == TimeSeriesInternal.DUMMY_GRAIN_COLUMN and
                self.grain_column_names[0] not in X_copy.columns
            ):
                X_copy[TimeSeriesInternal.DUMMY_GRAIN_COLUMN] = TimeSeriesInternal.DUMMY_GRAIN_COLUMN
            # Remember the forecast origins for each grain.
            # We will trim the data frame by these values at the end.
            # Also do the sanity check if there is at least one known grain.
            has_known_grain = False
            for grain, df_one in X_copy.groupby(self.grain_column_names):
                self.forecast_origin[grain] = df_one[self._time_col_name].min()
                has_known_grain = has_known_grain or grain in self._ts_transformer.dict_latest_date
            if not has_known_grain:
                raise AzureMLError.create(
                    TimeseriesNoUsableGrains, target="X_test", reference_code=ReferenceCodes._TS_NO_USABLE_GRAINS
                )
            special_columns = self.grain_column_names.copy()
            special_columns.append(self._ts_transformer.time_column_name)
            if self.origin_col_name in X_copy.columns:
                special_columns.append(self.origin_col_name)
            if self._ts_transformer.group_column in X_copy.columns:
                special_columns.append(self._ts_transformer.group_column)
            if self._ts_transformer.drop_column_names:
                dropping_columns = self._ts_transformer.drop_column_names
            else:
                dropping_columns = []
            categorical_columns = []
            dtypes_transformer = forecasting_utilities.get_pipeline_step(
                self._ts_transformer.pipeline, TimeSeriesInternal.RESTORE_DTYPES
            )
            if dtypes_transformer is not None:
                categorical_columns = dtypes_transformer.get_non_numeric_columns()
            for column in X_copy.columns:
                if (
                    column not in special_columns and
                    column not in dropping_columns and
                    column not in categorical_columns and
                    column in X_copy.select_dtypes(include=[np.number]).columns and
                    all(np.isnan(float(var)) for var in X_copy[column].values)
                ):
                    self._warn_or_raise(
                        TimeseriesDfContainsNaN, ReferenceCodes._FORECASTING_COLUMN_IS_NAN, ignore_data_errors
                    )
                    break

            if y_pred is None:
                y_pred = np.repeat(np.NaN, len(X_pred))
            if y_pred.shape[0] != X_pred.shape[0]:
                # May be we need to revisit this assertion.
                raise AzureMLError.create(
                    TimeseriesWrongShapeDataSizeMismatch,
                    target="y_pred.shape[0] != X_pred.shape[0]",
                    reference_code=ReferenceCodes._TS_WRONG_SHAPE_CREATE_PRED_DF,
                    var1_name="X_pred",
                    var1_len=X_pred.shape[0],
                    var2_name="y_pred",
                    var2_len=y_pred.shape[0],
                )
            if isinstance(y_pred, pd.DataFrame):
                if self._ts_transformer.target_column_name not in y_pred.columns:
                    raise AzureMLError.create(
                        MissingColumnsInData,
                        target="y_pred",
                        reference_code=ReferenceCodes._TSDF_INVALID_ARG_FC_PIPELINE_NO_TARGET_IN_Y_DF,
                        columns="target value column",
                        data_object_name="y_pred",
                    )
                X_copy = pd.merge(left=X_copy, right=y_pred, how="left", left_index=True, right_index=True)
                if X_copy.shape[0] != X_pred.shape[0]:
                    raise AzureMLError.create(
                        TimeseriesWrongShapeDataSizeMismatch,
                        target="X_copy.shape[0] != X_pred.shape[0]",
                        reference_code=ReferenceCodes._TS_WRONG_SHAPE_CREATE_PRED_DF_XCPY_XPRED,
                        var1_name="X_copy",
                        var1_len=X_copy.shape[0],
                        var2_name="X_pred",
                        var2_len=X_pred.shape[0],
                    )
            elif isinstance(y_pred, np.ndarray) and X_copy.shape[0] == y_pred.shape[0]:
                X_copy[self._ts_transformer.target_column_name] = y_pred
            # y_pred may be pd.DataFrame or np.ndarray only, we are checking it in _check_data.
            # At that point we have generated the data frame which contains Target value column
            # filled with y_pred. The part which will need to be should be
            # filled with np.NaNs.
        else:
            # Create the empty data frame from the last date in the training set for each grain
            # and fill it with NaNs. Impute these data.
            if self._ts_transformer.dict_latest_date == {}:
                raise AzureMLError.create(
                    TimeseriesGrainAbsentNoLastDate,
                    target="self._ts_transformer.dict_latest_date",
                    reference_code=ReferenceCodes._TS_GRAIN_ABSENT_MDL_WRP_NO_LAST_DATE,
                )
            dfs = []
            for grain_tuple in self._ts_transformer.dict_latest_date.keys():
                if pd.Timestamp(forecast_destination) <= self._ts_transformer.dict_latest_date[grain_tuple]:
                    raise AzureMLError.create(
                        TimeseriesWrongShapeDataEarlyDest,
                        target="forecast_destination",
                        reference_code=ReferenceCodes._TS_WRONG_SHAPE_FATAL_EARLY_DESTINATION,
                    )
                # Start with the next date after the last seen date.
                start_date = self._ts_transformer.dict_latest_date[grain_tuple] + to_offset(self._ts_transformer.freq)
                df_dict = {
                    self._time_col_name: pd.date_range(
                        start=start_date, end=forecast_destination, freq=self._ts_transformer.freq
                    )
                }
                if not isinstance(grain_tuple, tuple):
                    df_dict[self.grain_column_names[0]] = grain_tuple
                else:
                    for i in range(len(self.grain_column_names)):
                        df_dict[self.grain_column_names[i]] = grain_tuple[i]
                for col in cast(List[Any], self._ts_transformer.columns):
                    if col not in df_dict.keys():
                        df_dict[col] = np.NaN
                # target_column_name is not in the data frame columns by
                # default.
                df_dict[self._ts_transformer.target_column_name] = np.NaN
                dfs.append(pd.DataFrame(df_dict))
            X_copy = pd.concat(dfs)
            # At that point we have generated the data frame which contains target value column.
            # The data frame is filled with imputed data. Only target column is filled with np.NaNs,
            # because all gap between training data and forecast_destination
            # should be predicted.
        return X_copy

    def _infer_missing_data(
        self, X: pd.DataFrame, ignore_data_errors: bool, ignore_errors_and_warnings: bool
    ) -> pd.DataFrame:
        """
        Infer missing data in the data frame X.

        :param X: The data frame used for the inference.
        :param ignore_data_errors: Ignore errors in user data.
        :param ignore_errors_and_warnings : Ignore the y-related errors and warnings.
        :returns: the data frame with no NaNs
        :raises: DataException
        """
        df_inferred = []
        is_reported = False
        for grain, df_one in X.groupby(self.grain_column_names):
            # If the grain is categorical, groupby may result in the empty
            # data frame. If it is the case, skip it.
            if df_one.shape[0] == 0:
                continue
            last_known_y_date = self._get_last_y_one_grain(
                df_one, grain, ignore_data_errors, ignore_errors_and_warnings
            )
            if last_known_y_date is None:
                first_unknown_y_date = min(df_one[self._time_col_name])
            else:
                first_unknown_y_date = last_known_y_date + self.data_frequency
            # If the look back features are enabled, we have to check if window size or lag size are
            # larger then max_horizon.
            lookback_horizon = max([self.max_horizon, max(self.target_lags), self.target_rolling_window_size])
            if self._ts_transformer.dict_latest_date.get(grain) is None:
                # If the grain is not present in the training set and short grains should be dropped
                # we do not want to infer missing data, because this grain will be dropped during
                # transformation.
                expected_start = min(df_one[self._time_col_name])
            else:
                expected_start = max(
                    self._ts_transformer.dict_latest_date.get(grain) + self.data_frequency,
                    first_unknown_y_date - self.data_frequency * lookback_horizon,
                )
            hasgap = min(df_one[self._time_col_name]) > expected_start
            if (
                all(pd.isnull(y) for y in df_one[TimeSeriesInternal.DUMMY_TARGET_COLUMN]) and
                not is_reported and
                hasgap and
                self._lag_or_rw_enabled() and
                not self.is_grain_dropped(grain)
            ):
                # Do not warn user multiple times.
                self._warn_or_raise(
                    TimeseriesNoDataContext, ReferenceCodes._FORECASTING_NO_DATA_CONTEXT, ignore_data_errors
                )
                is_reported = True
            if self._ts_transformer.dict_latest_date.get(grain) is None:
                if not self.short_grain_handling():
                    # Throw absent grain error only if short grains are not handled.
                    raise AzureMLError.create(
                        TimeseriesGrainAbsentNoDataContext,
                        target="grain",
                        grain=grain,
                        reference_code=ReferenceCodes._TS_GRAIN_ABSENT_MDL_WRP_NO_DATA_CONTEXT,
                    )
            else:
                if min(df_one[self._time_col_name]) <= self._ts_transformer.dict_latest_date[grain]:
                    raise AzureMLError.create(
                        TimeseriesWrongShapeDataEarlyDest,
                        target="self._ts_transformer",
                        reference_code=ReferenceCodes._TS_WRONG_SHAPE_FATAL_EARLY_DESTINATION2,
                    )
            # If we are given a data context, we need to mark missing values in the context
            # so that it will be featurized correctly e.g. with lag-by-occurrence
            if self._ts_transformer._keep_missing_dummies_on_target:
                missing_target_dummy_transform = self._ts_transformer._init_missing_y()
                tsds_data = TimeSeriesDataSet(
                    df_one, time_column_name=self.time_column_name, time_series_id_column_names=self.grain_column_names
                )
                tsds_data = missing_target_dummy_transform.fit_transform(tsds_data)
                df_one = tsds_data.data
                df_one.reset_index(inplace=True, drop=False)
                not_imputed_val = missing_target_dummy_transform.MARKER_VALUE_NOT_MISSING
                if last_known_y_date is None:
                    # There's no data context, mark all rows as not-missing
                    df_one[self._ts_transformer.target_imputation_marker_column_name] = not_imputed_val
                else:
                    # Mark targets with dates in the prediction range as not-missing
                    sel_prediction_dates = df_one[self._time_col_name] > last_known_y_date
                    df_one.loc[
                        sel_prediction_dates, self._ts_transformer.target_imputation_marker_column_name
                    ] = not_imputed_val

            # If we have a gap between train and predict data set, we need to extend the test set.
            # If there is no last known date, nothing can be done.
            if self._ts_transformer.dict_latest_date.get(grain) is not None:
                # If we know the last date, we can evaluate and fill the gap.
                if hasgap and self._lag_or_rw_enabled():
                    # If there is a gap between train and test data for the
                    # given grain, extend the test data frame.
                    ext_dates = pd.date_range(
                        start=expected_start,
                        end=df_one[self._time_col_name].min() - self.data_frequency,
                        freq=self.data_frequency,
                    )
                    if len(ext_dates) == 0:  # end - start < self.data_frequency
                        # In this case we will just create one row.
                        ext_dates = pd.date_range(start=expected_start, periods=1, freq=self.data_frequency)
                    extension = pd.DataFrame(np.nan, index=np.arange(len(ext_dates)), columns=df_one.columns.values)
                    extension[self._time_col_name] = ext_dates
                    if not isinstance(grain, tuple):
                        extension[self.grain_column_names[0]] = grain
                    else:
                        for i in range(len(self.grain_column_names)):
                            extension[self.grain_column_names[i]] = grain[i]
                    # Make a temporary time series data frame to apply
                    # imputers.
                    tsds_ext = TimeSeriesDataSet(
                        extension,
                        time_column_name=self._ts_transformer.time_column_name,
                        time_series_id_column_names=self._ts_transformer.grain_column_names,
                        target_column_name=self._ts_transformer.target_column_name,
                    )
                    # Mark the gap with missing target dummy indicators
                    if self._ts_transformer._keep_missing_dummies_on_target:
                        tsds_ext = self._ts_transformer._init_missing_y().fit_transform(tsds_ext)
                    # Replace np.NaNs by imputed values.
                    tsds_ext = forecasting_utilities.get_pipeline_step(
                        self._ts_transformer.pipeline, TimeSeriesInternal.IMPUTE_NA_NUMERIC_DATETIME
                    ).transform(tsds_ext)
                    # Replace np.NaNs in y column.
                    imputer = self._ts_transformer.y_imputers.get(grain)
                    # Should not happen on fitted time series transformer.
                    Contract.assert_true(
                        imputer is not None,
                        message=ForecastingPipelineWrapper.FATAL_NO_TARGET_IMPUTER,
                        target="imputer",
                        reference_code=ReferenceCodes._FORECASTING_PIPELINE_NO_TARGET_IMPUTER,
                    )
                    tsds_ext = imputer.transform(tsds_ext)
                    # Return the regular data frame.
                    extension = tsds_ext.data
                    extension.reset_index(drop=False, inplace=True)
                    df_one = pd.concat([extension, df_one], sort=True)
            # Make sure we do not have a gaps in the y.
            # We are actually doing it only if ignore_data_errors is set to True,
            # or we do not have non contiguous NaNs and code have no effect.
            df_one = self._impute_missing_y_one_grain(df_one)
            df_inferred.append(df_one)
        X = pd.concat(df_inferred, sort=True)
        return X

    def _impute_missing_y_one_grain(self, df_one: pd.DataFrame, is_sorted: bool = True) -> pd.DataFrame:
        """
        Do the imputation to remove the potential gap inside y values.

        :param df_one: The data frame with potential gaps in target values.
        :param is_sorted:
        :return: The same data frame with the gaps filled in.
        """
        # TODO: Unify this imputation method with self._ts_transformer.y_imputers
        if not is_sorted:
            # Because we have already ran _get_last_y_one_grain before, we know
            # that df_one is sorted by time column.
            # This sorting is needed only for bfill method.
            df_one.sort_values(by=self.time_column_name)
        df_one[self._ts_transformer.target_column_name].fillna(None, "bfill", axis=0, inplace=True)
        return df_one

    def _regular_forecast(
        self, X_copy: pd.DataFrame, ignore_data_errors: bool, is_rolling_forecast: bool = False
    ) -> pd.DataFrame:
        """
        Do the forecast on the data frame X_pred.

        DataError is thrown if neither X_pred and y_pred nor
        :param X_copy: the prediction dataframe.
        :param ignore_data_errors: Ignore errors in user data.
        :param is_rolling_forecast: Flag to indicate rolling forecast which may need special handling.
        :returns: the subframe corresponding to Y_future filled in with the respective forecasts.
                  Any missing values in Y_past will be filled by imputer.
        :rtype: pandas.DataFrame
        """
        # Set/Reset forecast origin state
        self.forecast_origin = {}
        # We need to make sure that we have a context. If train set is followed by a test/predict set,
        # there should be no error. otherwise we will need to infer missing data.
        # The part of the data frame, for which y_pred is known will be
        # removed.
        X_copy = self._infer_missing_data(X_copy, ignore_data_errors, is_rolling_forecast)
        last_step = self.pipeline.steps[len(self.pipeline.steps) - 1][1]
        # Pre processing.
        test_feats = None  # type: Optional[pd.DataFrame]
        y_known_series = None  # type: Optional[pd.Series]
        for i in range(len(self.pipeline.steps) - 1):
            # FIXME: Work item #400231
            if type(self.pipeline.steps[i][1]).__name__ == "TimeSeriesTransformer":
                test_feats = self.pipeline.steps[i][1].transform(X_copy)
                # We do not need the target column now.
                # The target column is deleted by the rolling window during transform.
                # If there is no rolling window we need to make sure the column was dropped.
                if self._ts_transformer.target_column_name in test_feats.columns:
                    # We want to store the y_known_series for future use.
                    y_known_series = test_feats[self._ts_transformer.target_column_name]
                    test_feats.drop(self._ts_transformer.target_column_name, inplace=True, axis=1)
                # If origin times are present, remove nans from look-back features and select the latest origins
                if self.origin_col_name in test_feats.index.names:
                    y = np.zeros(test_feats.shape[0])
                    test_feats, _ = self._ts_transformer._remove_nans_from_look_back_features(test_feats, y)
                    test_feats = self._ts_transformer._select_latest_origin_dates(test_feats)
                X_copy = test_feats.copy()
            else:
                X_copy = self.pipeline.steps[i][1].transform(X_copy)

        try:
            y_preds = last_step.predict(X_copy)
        except Exception as e:
            raise PredictionException.from_exception(
                e, has_pii=True, target="ForecastingPipelineWrapper"
            ).with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))
        # We know that test_feats is not None, but we have to put this assertion here
        # to ensure mypy test is passing.
        # We are raising the exception if we have no time series transformer on the stage
        # of tst creation.
        assert test_feats is not None
        test_feats[TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y_preds

        test_feats = self._postprocess_output(test_feats, y_known_series)
        return test_feats

    def _recursive_forecast(self, X_copy: pd.DataFrame, ignore_data_errors: bool) -> pd.DataFrame:
        """
        Produce forecasts recursively on a rolling origin.

        Each iteration makes a forecast for the next 'max_horizon' periods
        with respect to the current origin, then advances the origin by the
        horizon time duration. The prediction context for each forecast is set so
        that the forecaster uses forecasted target values for times prior to the current
        origin time for constructing lag features.

        This function returns a vector of forecasted target values and a concatenated DataFrame
        of rolling forecasts.

        :param X_copy: the prediction dataframe generated from _create_prediction_data_frame.
        :param ignore_data_errors: Ignore errors in user data.
        :returns: the subframe corresponding to Y_future filled in with the respective forecasts.
                  Any missing values in Y_past will be filled by imputer.
        :rtype: pandas.DataFrame
        """
        X_rlt = []
        dfs = []
        start_dates = {}
        # In this code we need to split data into batches,
        # so that each of batches is less then max horizon.
        # First we will determine the forecasting origin for each of grain.
        # We will keep these data in start_dates dictionary.
        # We will impute missing target here.
        for grp, df_one in X_copy.groupby(self.grain_column_names):
            if self.is_grain_dropped(grp):
                continue
            # Do not use the output but run the validation for df_one.
            self._get_last_y_one_grain(df_one, grp, ignore_data_errors)
            # Populate the start dates dictionary.
            start_dates[grp] = df_one[self.time_column_name].min()
            # After the validation is done, fill the gaps in y.
            df_one = self._impute_missing_y_one_grain(df_one)
            dfs.append(df_one)
        X_copy = pd.concat(dfs)
        groupby_ob = X_copy.groupby(self.grain_column_names)
        previous_batch = None  # type: Optional[pd.DataFrame]
        merge_index = [self._time_col_name]
        if self.grain_column_names:
            merge_index.extend(self.grain_column_names)
        # After knowing the start dates, we can start forecasting.
        while start_dates:
            batch, new_start_dates = self._get_next_batch(groupby_ob, previous_batch, start_dates.copy())
            fcst = self._regular_forecast(batch, ignore_data_errors, is_rolling_forecast=True)
            batch.drop(TimeSeriesInternal.DUMMY_TARGET_COLUMN, axis=1, inplace=True)
            batch = batch.merge(fcst[TimeSeriesInternal.DUMMY_TARGET_COLUMN], how="left", on=merge_index, sort=False)
            # If we have added the old values to the data set, we need to cut it.
            if previous_batch is not None:
                # The data missing from start_dates were not used for this iteration of
                # forecasting and need to be cut.
                batch = batch.groupby(self.grain_column_names, group_keys=False).apply(
                    lambda df: df[df[self._time_col_name] >= start_dates[df.name]]
                    if df.name in start_dates
                    else pd.DataFrame()
                )
                fcst = fcst.groupby(self.grain_column_names, group_keys=False).apply(
                    lambda df: df[df.index.get_level_values(self._time_col_name) >= start_dates[df.name]]
                    if df.name in start_dates
                    else pd.DataFrame()
                )
            X_rlt.append(fcst)
            previous_batch = batch
            start_dates = new_start_dates
        return pd.concat(X_rlt, sort=False, ignore_index=False)

    def _get_next_batch(
        self, groupby_ob: Any, previous_df: Optional[pd.DataFrame], start_dates: Dict[GrainType, pd.Timestamp]
    ) -> Tuple[pd.DataFrame, Dict[GrainType, pd.Timestamp]]:
        """
        Get the next batch of the data frame.

        :param groupby_ob: The groupby object to get the batches from.
        :param start_dates: the start_dates.
        :return: The tuple of new data frame and next start times.
        """
        new_batch_list = []
        for grain_one, df_one in groupby_ob:
            # If grain is not in start dates, we do not need to do
            # the forecast.
            if grain_one not in start_dates:
                continue
            origin_time = start_dates[grain_one]
            next_valid_point = df_one[df_one[self.time_column_name] >= origin_time][self.time_column_name].min()
            # Set the horizon time - end date of the forecast
            horizon_time = next_valid_point + self.max_horizon * self.data_frequency
            # Extract test data from an expanding window up-to the horizon
            expand_wind = (df_one[self.time_column_name] >= origin_time) & (
                df_one[self.time_column_name] < horizon_time
            )
            df_pred_expand = df_one[expand_wind]
            if previous_df is not None and next_valid_point != origin_time:
                # If we have the gap inside test set, we need to impute it.
                X_gap = pd.concat([
                    previous_df, df_pred_expand[df_pred_expand[self.time_column_name] <= next_valid_point]])
                X_gap = self._infer_y(X_gap, grain_one, fill_datetime_gap=True)
                # Drop the context, as we will add it later and first valid data point.
                X_gap = X_gap[(X_gap[self.time_column_name] > previous_df[self.time_column_name].max()) &
                              (X_gap[self.time_column_name] < next_valid_point)]
                # Glue the imputed data to the existing data frame.
                df_pred_expand = pd.concat([
                    X_gap,
                    df_pred_expand[df_pred_expand[self.time_column_name] >= next_valid_point]
                ], sort=False, ignore_index=True)

            # If the max time of given grain is less then horizon, we remove it from start times.
            if df_one[self.time_column_name].max() < horizon_time:
                del start_dates[grain_one]
            else:
                start_dates[grain_one] = horizon_time
            new_batch_list.append(df_pred_expand)
        X_new = pd.concat(new_batch_list, sort=False, ignore_index=True)
        if previous_df is not None:
            X_new = X_new.append(previous_df, sort=False, ignore_index=True)
        return X_new, start_dates

    def _use_recursive_forecast(self, X_copy: pd.DataFrame, ignore_data_errors: bool = False) -> bool:
        """
        Describe conditions for using recursive forecast method.
        Recursive forecast is invoked when the prediction length is greater than the max_horizon
        and lookback features are enables. This function returns a True/False for
        whether recursive forecast method should be invoked.

        :param X_copy: the prediction dataframe generated from _create_prediction_data_frame.
        :param X_pred: the prediction dataframe combining X_past and X_future in a time-contiguous manner.
                       Empty values in X_pred will be imputed.
        :param y_pred: the target value combining definite values for y_past and missing values for Y_future.
                       If None the predictions will be made for every X_pred.
        :param forecast_destination: Forecast_destination: a time-stamp value.
                                     Forecasts will be made all the way to the forecast_destination time,
                                     for all grains. Dictionary input { grain -> timestamp } will not be accepted.
                                     If forecast_destination is not given, it will be imputed as the last time
                                     occurring in X_pred for every grain.
        :type forecast_destination: pandas.Timestamp
        :param ignore_data_errors: Ignore errors in user data.
        :type ignore_data_errors: bool
        :returns: True/False for whether recursive forecast method should be invoked.
        :rtype: bool
        """
        if not self._lag_or_rw_enabled():
            return False
        else:
            for grain, df_one in X_copy.groupby(self.grain_column_names):
                if not self.is_grain_dropped(grain):
                    if self._do_check_max_horizon(grain, df_one, ignore_data_errors):
                        return True
            return False

    def _convert_time_column_name_safe(self, X: pd.DataFrame, reference_code: str) -> pd.DataFrame:
        """
        Convert the time column name to date time.

        :param X: The prediction data frame.
        :param reference_code: The reference code to be given to error.
        :return: The modified data frame.
        :raises: DataException
        """
        try:
            X[self.time_column_name] = pd.to_datetime(X[self.time_column_name])
        except Exception:
            raise AzureMLError.create(
                PandasDatetimeConversion,
                column=self.time_column_name,
                column_type=X[self.time_column_name].dtype,
                target=TimeSeries.TIME_COLUMN_NAME,
                reference_code=reference_code,
            )
        return X

    def forecast(
        self,
        X_pred: Optional[pd.DataFrame] = None,
        y_pred: Optional[Union[pd.DataFrame, np.ndarray]] = None,
        forecast_destination: Optional[pd.Timestamp] = None,
        ignore_data_errors: bool = False,
    ) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Do the forecast on the data frame X_pred.

        :param X_pred: the prediction dataframe combining X_past and X_future in a time-contiguous manner.
                       Empty values in X_pred will be imputed.
        :param y_pred: the target value combining definite values for y_past and missing values for Y_future.
                       If None the predictions will be made for every X_pred.
        :param forecast_destination: Forecast_destination: a time-stamp value.
                                     Forecasts will be made all the way to the forecast_destination time,
                                     for all grains. Dictionary input { grain -> timestamp } will not be accepted.
                                     If forecast_destination is not given, it will be imputed as the last time
                                     occurring in X_pred for every grain.
        :type forecast_destination: pandas.Timestamp
        :param ignore_data_errors: Ignore errors in user data.
        :type ignore_data_errors: bool
        :returns: Y_pred, with the subframe corresponding to Y_future filled in with the respective forecasts.
                  Any missing values in Y_past will be filled by imputer.
        :rtype: tuple
        """
        # check the format of input
        self._check_data(X_pred, y_pred, forecast_destination)

        # Check that the grains have correct types.
        if X_pred is not None:
            X_pred = self._check_convert_grain_types(X_pred)
        # Handle the case where both an index and column have the same name. Merge/groupby both
        # cannot handle cases where column name is also in index above version 0.23. In addition,
        # index is only accepted as a kwarg in versions >= 0.24
        dict_rename = {}
        dict_rename_back = {}
        pd_compatible = pd.__version__ >= "0.24.0"
        if pd_compatible and X_pred is not None:
            for ix_name in X_pred.index.names:
                if ix_name in X_pred.columns:
                    temp_name = "temp_{}".format(uuid.uuid4())
                    dict_rename[ix_name] = temp_name
                    dict_rename_back[temp_name] = ix_name
            if len(dict_rename) > 0:
                X_pred.rename_axis(index=dict_rename, inplace=True)
        # If the data had to be aggregated, we have to do it here.

        if X_pred is not None:
            X_pred = self._convert_time_column_name_safe(X_pred, ReferenceCodes._FORECASTING_CONVERT_INVALID_VALUE)
            X_pred, y_pred = self.preaggregate_data_set(X_pred, y_pred)
        # create the prediction data frame
        X_copy = self._create_prediction_data_frame(X_pred, y_pred, forecast_destination, ignore_data_errors)
        if self._use_recursive_forecast(X_copy=X_copy, ignore_data_errors=ignore_data_errors):
            test_feats = self._recursive_forecast(X_copy, ignore_data_errors)
        else:
            test_feats = self._regular_forecast(X_copy, ignore_data_errors)
        # Order the time series data frame as it was encountered as in initial input.
        if X_pred is not None:
            test_feats = self.align_output_to_input(X_pred, test_feats)
        else:
            test_feats.sort_index(inplace=True)
        y_pred = test_feats[TimeSeriesInternal.DUMMY_TARGET_COLUMN].values

        if self._y_transformer is not None:
            y_pred = self._y_transformer.inverse_transform(y_pred)

        # name index columns back as needed.
        if len(dict_rename_back) > 0:
            test_feats.rename_axis(index=dict_rename_back, inplace=True)
            X_pred.rename_axis(index=dict_rename_back, inplace=True)
        return y_pred, test_feats

    def _check_data_rolling_evaluation(
        self, X_pred: pd.DataFrame, y_pred: Union[pd.DataFrame, np.ndarray], ignore_data_errors: bool
    ) -> None:
        """
        Check the inputs for rolling evaluation function.
        Rolling evaluation is invoked when all the entries of y_pred are definite, look_back features are enabled
        and the test length is greater than the max horizon.

        :param X_pred: the prediction dataframe combining X_past and X_future in a time-contiguous manner.
                       Empty values in X_pred will be imputed.
        :param y_pred: the target value corresponding to X_pred.
        :param ignore_data_errors: Ignore errors in user data.

        :raises: DataException
        """
        # if none of y value is definite, raise errors.
        if y_pred is None:
            y_pred_unknown = True
        elif isinstance(y_pred, np.ndarray):
            y_pred_unknown = pd.isna(y_pred).all()
        else:
            y_pred_unknown = y_pred.isnull().values.all()
        if y_pred_unknown:
            # this is a fatal error, hence not ignoring data errors
            self._warn_or_raise(
                TimeseriesMissingValuesInY, ReferenceCodes._ROLLING_EVALUATION_NO_Y, ignore_data_errors=False
            )

    def _infer_y(self, X: pd.DataFrame,
                 grain: GrainType,
                 fill_datetime_gap: bool = False) -> pd.DataFrame:
        """
        The convenience method to call the imputer on target column.

        **Note:** This method is not grain-aware.
        :param X: One grain of the data frame.
        :param grain: The grain key.
        :param fill_datetime_gap: To we need to call fill_datetime_gap on data set.
        :return: The data frame with imputed values.
        """
        y_imputer = self._ts_transformer.y_imputers.get(grain)
        tsds_X = TimeSeriesDataSet(
            X,
            time_column_name=self._ts_transformer.time_column_name,
            time_series_id_column_names=self._ts_transformer.grain_column_names,
            target_column_name=self._ts_transformer.target_column_name,
        )
        if fill_datetime_gap:
            tsds_X = tsds_X.fill_datetime_gap(freq=self.data_frequency)
        X = y_imputer.transform(tsds_X).data
        X.reset_index(inplace=True, drop=False)
        return X

    def rolling_evaluation(
        self, X_pred: pd.DataFrame, y_pred: Union[pd.DataFrame, np.ndarray], ignore_data_errors: bool = False
    ) -> Tuple[np.ndarray, pd.DataFrame]:
        """ "
        Produce forecasts on a rolling origin over the given test set.

        Each iteration makes a forecast for the next 'max_horizon' periods
        with respect to the current origin, then advances the origin by the
        horizon time duration. The prediction context for each forecast is set so
        that the forecaster uses the actual target values prior to the current
        origin time for constructing lag features.

        This function returns a concatenated DataFrame of rolling forecasts joined
        with the actuals from the test set.

        :param X_pred: the prediction dataframe combining X_past and X_future in a time-contiguous manner.
                       Empty values in X_pred will be imputed.
        :param y_pred: the target value corresponding to X_pred.
        :param ignore_data_errors: Ignore errors in user data.

        :returns: Y_pred, with the subframe corresponding to Y_future filled in with the respective forecasts.
                  Any missing values in Y_past will be filled by imputer.
        :rtype: tuple
        """
        # check data satisfying the requiring information. If not, raise relevant error messages.
        self._check_data(X_pred, y_pred, None)
        self._check_data_rolling_evaluation(X_pred, y_pred, ignore_data_errors)
        # create the prediction dataframe

        X_pred = self._convert_time_column_name_safe(X_pred, ReferenceCodes._FORECASTING_CONVERT_INVALID_VALUE_EV)
        X_pred, y_pred = self.preaggregate_data_set(X_pred, y_pred)
        X_copy = self._create_prediction_data_frame(X_pred, y_pred, None, ignore_data_errors)
        X_rlt = []
        for grain_one, df_one in X_copy.groupby(self.grain_column_names):
            if self.is_grain_dropped(grain_one):
                continue
            if pd.isna(df_one[self.target_column_name]).any():
                df_one = self._infer_y(df_one, grain_one)
            y_pred_one = df_one[self.target_column_name].copy()
            df_one[self.target_column_name] = np.nan
            X_tmp = self._rolling_evaluation_one_grain(df_one, y_pred_one, ignore_data_errors, grain_one)
            X_rlt.append(X_tmp)
        test_feats = pd.concat(X_rlt)
        test_feats = self.align_output_to_input(X_pred, test_feats)
        y_pred = test_feats[TimeSeriesInternal.DUMMY_TARGET_COLUMN].values

        if self._y_transformer is not None:
            y_pred = self._y_transformer.inverse_transform(y_pred)

        return y_pred, test_feats

    def _rolling_evaluation_one_grain(
            self, df_pred: pd.DataFrame,
            y_pred: pd.Series,
            ignore_data_errors: bool,
            grain_name: GrainType) -> pd.DataFrame:
        """ "
        Implement rolling_evaluation for each grain.

        :param df_pred: the prediction dataframe generated from _create_prediction_data_frame.
        :param y_pred: the target value corresponding to X_pred.
        :param ignore_data_errors: Ignore errors in user data.
        :param grain_name: The name of the grain to evaluate.
        :returns: Y_pred, with the subframe corresponding to Y_future filled in with the respective forecasts.
                  Any missing values in Y_past will be filled by imputer.
        :rtype: pandas.DataFrame
        """
        df_list = []
        X_trans = pd.DataFrame()
        start_time = df_pred[self.time_column_name].min()
        origin_time = start_time
        while origin_time <= df_pred[self.time_column_name].max():
            # Set the horizon time - end date of the forecast
            next_valid_point = df_pred[df_pred[self.time_column_name] >= origin_time][self.time_column_name].min()
            horizon_time = next_valid_point + self.max_horizon * self.data_frequency
            # Extract test data from an expanding window up-to the horizon
            expand_wind = df_pred[self.time_column_name] < horizon_time
            df_pred_expand = df_pred[expand_wind]
            if origin_time != start_time:
                # Set the context by including actuals up-to the origin time
                test_context_expand_wind = df_pred[self.time_column_name] < origin_time
                context_expand_wind = df_pred_expand[self.time_column_name] < origin_time
                # add the y_pred information into the df_pred_expand dataframe.
                y_tmp = X_trans.reset_index()[TimeSeriesInternal.DUMMY_TARGET_COLUMN]
                df_pred_expand[self.target_column_name][context_expand_wind] = y_pred[
                    test_context_expand_wind].combine_first(y_tmp)
                if horizon_time != origin_time:
                    # We will include first valid test point to the gapped part to fill the
                    # datetime gap. We will infer y and remove this data point.
                    X_gap = df_pred_expand[df_pred_expand[self.time_column_name] <= next_valid_point]
                    # The part, where we do not need to infer.
                    X_nogap = df_pred_expand[df_pred_expand[self.time_column_name] >= next_valid_point]
                    X_gap = self._infer_y(X_gap, grain_name, fill_datetime_gap=True)
                    # Remove the last data point
                    X_gap = X_gap[X_gap[self.time_column_name] < next_valid_point]
                    # Glue the imputed data to the existing data frame.
                    df_pred_expand = pd.concat([X_gap, X_nogap], sort=False, ignore_index=True)

            # Make a forecast out to the maximum horizon
            X_trans = self._regular_forecast(df_pred_expand, ignore_data_errors)
            trans_tindex = X_trans.index.get_level_values(self.time_column_name)
            trans_roll_wind = (trans_tindex >= origin_time) & (trans_tindex < horizon_time)
            df_list.append(X_trans[trans_roll_wind])
            # Advance the origin time
            origin_time = horizon_time
        X_fcst_all = pd.concat(df_list)
        return X_fcst_all

    def align_output_to_input(self, X_input: pd.DataFrame, transformed: pd.DataFrame) -> pd.DataFrame:
        """
        Align the transformed output data frame to the input data frame.

        *Note:* transformed will be modified by reference, no copy is being created.
        :param X_input: The input data frame.
        :param transformed: The data frame after transformation.
        :returns: The transfotmed data frame with its original index, but sorted as in X_input.
        """
        index = transformed.index.names
        # Before dropping index, we need to make sure that
        # we do not have features named as index columns.
        # we will temporary rename them.
        dict_rename = {}
        dict_rename_back = {}
        for ix_name in transformed.index.names:
            if ix_name in transformed.columns:
                temp_name = "temp_{}".format(uuid.uuid4())
                dict_rename[ix_name] = temp_name
                dict_rename_back[temp_name] = ix_name
        if len(dict_rename) > 0:
            transformed.rename(dict_rename, axis=1, inplace=True)
        transformed.reset_index(drop=False, inplace=True)
        merge_ix = [self.time_column_name]
        # We add grain column to index only if it is non dummy.
        if self.grain_column_names != [TimeSeriesInternal.DUMMY_GRAIN_COLUMN]:
            merge_ix += self.grain_column_names
        X_merge = X_input[merge_ix]
        # Make sure, we have a correct dtype.
        for col in X_merge.columns:
            X_merge[col] = X_merge[col].astype(transformed[col].dtype)
        transformed = X_merge.merge(transformed, how="left", on=merge_ix)
        # return old index back
        transformed.set_index(index, inplace=True, drop=True)
        # If we have renamed any columns, we need to set it back.
        if len(dict_rename_back) > 0:
            transformed.rename(dict_rename_back, axis=1, inplace=True)
        return transformed

    def apply_time_series_transform(self, X: pd.DataFrame, y: Optional[np.ndarray] = None) -> pd.DataFrame:
        """
        Apply all time series transforms to the data frame X.

        :param X: The data frame to be transformed.
        :type X: pandas.DataFrame
        :returns: The transformed data frame, having date, grain and origin
                  columns as indexes.
        :rtype: pandas.DataFrame

        """
        X_copy = X.copy()
        if y is not None:
            X_copy[self.target_column_name] = y
        for i in range(len(self.pipeline.steps) - 1):
            # FIXME: Work item #400231
            if type(self.pipeline.steps[i][1]).__name__ == "TimeSeriesTransformer":
                X_copy = self.pipeline.steps[i][1].transform(X_copy)
                # When we made a time series transformation we need to break and return X.
                if self.origin_col_name in X_copy.index.names:
                    X_copy = self._ts_transformer._select_latest_origin_dates(X_copy)
                X_copy.sort_index(inplace=True)
                # If the target column was created by featurizers, drop it.
                if self.target_column_name in X_copy:
                    X_copy.drop(self.target_column_name, axis=1, inplace=True)
                return X_copy
            else:
                X_copy = self.pipeline.steps[i][1].transform(X_copy)

    def _lag_or_rw_enabled(self) -> bool:
        if forecasting_utilities.get_pipeline_step(
            self._ts_transformer.pipeline, TimeSeriesInternal.LAG_LEAD_OPERATOR
        ):
            return True
        elif forecasting_utilities.get_pipeline_step(
            self._ts_transformer.pipeline, TimeSeriesInternal.ROLLING_WINDOW_OPERATOR
        ):
            return True
        else:
            return False

    def _get_last_known_y(self, X: pd.DataFrame, ignore_data_errors: bool) -> Dict[str, pd.Timestamp]:
        """
        Return the value of date for the last known y.

        If no y is known for given grain, corresponding date is not returned.
        If y contains non contiguous numbers or NaNs the DataException is raised.
        :param X: The data frame. We need to make sure that y values
                  does not contain gaps.
        :param ignore_data_errors: Ignore errors in user data.
        :returns: dict containing grain->latest date for which y is known.
        :raises: DataException

        """
        dict_data = {}  # type: Dict[str, pd.Timestamp]
        if self.grain_column_names[0] == TimeSeriesInternal.DUMMY_GRAIN_COLUMN:
            self._add_to_dict_maybe(
                dict_data,
                self._get_last_y_one_grain(X, TimeSeriesInternal.DUMMY_GRAIN_COLUMN, ignore_data_errors),
                self.grain_column_names[0],
            )
        else:
            for grain, df_one in X.groupby(self.grain_column_names, as_index=False):
                self._add_to_dict_maybe(
                    dict_data, self._get_last_y_one_grain(df_one, grain, ignore_data_errors), grain
                )
        for grain in self._ts_transformer.dict_latest_date.keys():
            data = dict_data.get(grain)
            if data is not None and data < self._ts_transformer.dict_latest_date.get(grain):
                dict_data[grain] = self._ts_transformer.dict_latest_date.get(grain)
        return dict_data

    def _add_to_dict_maybe(self, dt, date, grain):
        """Add date to dict if it is not None."""
        if date is not None:
            dt[grain] = date

    def _get_last_y_one_grain(
        self,
        df_grain: pd.DataFrame,
        grain: GrainType,
        ignore_data_errors: bool,
        ignore_errors_and_warnings: bool = False,
    ) -> Optional[pd.Timestamp]:
        """
        Get the date for the last known y.

        This y will be used in transformation, but will not be used
        in prediction (the data frame will be trimmed).
        :param df_grain: The data frame corresponding to single grain.
        :param ignore_data_errors: Ignore errors in user data.
        :param ignore_errors_and_warnings : Ignore the y-related errors and warnings.
        :returns: The date corresponding to the last known y or None.
        """
        # We do not want to show errors for the grains which will be dropped.
        is_absent_grain = self.short_grain_handling() and grain not in self._ts_transformer.dict_latest_date.keys()
        # Make sure that frame is sorted by the time index.
        df_grain.sort_values(by=[self._time_col_name], inplace=True)
        y = df_grain[TimeSeriesInternal.DUMMY_TARGET_COLUMN].values
        sel_null_y = pd.isnull(y)
        num_null_y = sel_null_y.sum()
        if num_null_y == 0:
            # All y are known - nothing to forecast
            if not is_absent_grain and not ignore_errors_and_warnings:
                self._warn_or_raise(
                    TimeseriesNothingToPredict, ReferenceCodes._FORECASTING_NOTHING_TO_PREDICT, ignore_data_errors
                )
            return df_grain[self._time_col_name].max()
        elif num_null_y == y.shape[0]:
            # We do not have any known y
            return None
        elif not sel_null_y[-1]:
            # There is context at the end of the y vector.
            # This could lead to unexpected behavior, so consider that this case means there is nothing to forecast
            if not is_absent_grain and not ignore_errors_and_warnings:
                self._warn_or_raise(
                    TimeseriesContextAtEndOfY, ReferenceCodes._FORECASTING_CONTEXT_AT_END_OF_Y, ignore_data_errors
                )

        # Some y are known, some are not.
        # Are the data continguous - i.e. are there gaps in the context?
        non_nan_indices = np.flatnonzero(~sel_null_y)
        if not is_absent_grain and not ignore_errors_and_warnings and not np.array_equiv(np.diff(non_nan_indices), 1):
            self._warn_or_raise(
                TimeseriesNonContiguousTargetColumn,
                ReferenceCodes._FORECASTING_DATA_NOT_CONTIGUOUS,
                ignore_data_errors,
            )
        last_date = df_grain[self._time_col_name].iloc[non_nan_indices.max()]

        return pd.Timestamp(last_date)

    def _warn_or_raise(
        self, error_definition_class: "ErrorDefinition", ref_code: str, ignore_data_errors: bool
    ) -> None:
        """
        Raise DataException if the ignore_data_errors is False.

        :param warning_text: The text of error or warning.
        :param ignore_data_errors: if True raise the error, warn otherwise.
        """
        # All error definitions currently being passed to this function don't need any message_params.
        # Pass in error message_parameters via kwargs on `_warn_or_raise` and plumb them below, should we need to
        # create errors below with message_parameters
        error = AzureMLError.create(error_definition_class, reference_code=ref_code)
        if ignore_data_errors:
            warnings.warn(error.error_message)
        else:
            raise error

    def forecast_quantiles(
        self,
        X_pred: Optional[pd.DataFrame] = None,
        y_pred: Optional[Union[pd.DataFrame, np.ndarray]] = None,
        forecast_destination: Optional[pd.Timestamp] = None,
        ignore_data_errors: bool = False,
    ) -> pd.DataFrame:
        """
        Get the prediction and quantiles from the fitted pipeline.

        :param X_pred: the prediction dataframe combining X_past and X_future in a time-contiguous manner.
                       Empty values in X_pred will be imputed.
        :param y_pred: the target value combining definite values for y_past and missing values for Y_future.
                       If None the predictions will be made for every X_pred.
        :param forecast_destination: Forecast_destination: a time-stamp value.
                                     Forecasts will be made all the way to the forecast_destination time,
                                     for all grains. Dictionary input { grain -> timestamp } will not be accepted.
                                     If forecast_destination is not given, it will be imputed as the last time
                                     occurring in X_pred for every grain.
        :type forecast_destination: pandas.Timestamp
        :param ignore_data_errors: Ignore errors in user data.
        :type ignore_data_errors: bool
        :return: A dataframe containing time, grain, and corresponding quantiles for requested prediction.
        """
        # If the data were aggregated, we have to also aggregate the input.
        if X_pred is not None:
            X_pred = self._convert_time_column_name_safe(
                X_pred, ReferenceCodes._FORECASTING_QUANTILES_CONVERT_INVALID_VALUE
            )
            X_pred, y_pred = self.preaggregate_data_set(X_pred, y_pred)
        pred, transformed_data = self.forecast(X_pred, y_pred, forecast_destination, ignore_data_errors)
        NOT_KNOWN_Y = "y_not_known"

        max_horizon_featurizer = forecasting_utilities.get_pipeline_step(
            self._ts_transformer.pipeline, TimeSeriesInternal.MAX_HORIZON_FEATURIZER
        )
        horizon_column = None if max_horizon_featurizer is None else max_horizon_featurizer.horizon_colname

        dict_latest_date = self._ts_transformer.dict_latest_date
        freq = self._ts_transformer.freq

        if X_pred is not None:
            # Figure out last known y for each grain.
            X_copy = X_pred.copy()
            if y_pred is not None:
                X_copy[self.target_column_name] = y_pred
            else:
                X_copy[self.target_column_name] = np.NaN

            # add dummy grain if needed to df
            if (
                self.grain_column_names[0] == TimeSeriesInternal.DUMMY_GRAIN_COLUMN and
                self.grain_column_names[0] not in X_copy.columns
            ):
                X_copy[TimeSeriesInternal.DUMMY_GRAIN_COLUMN] = TimeSeriesInternal.DUMMY_GRAIN_COLUMN
            # We already have shown user warnings or have thrown errors during forecast() call.
            # At this stage we can
            X_copy = self._infer_missing_data(X_copy, ignore_data_errors, ignore_errors_and_warnings=True)
            # We ignore user errors, because if desired it was already rose.
            dict_known = self._get_last_known_y(X_copy, True)
            dfs = []
            for grain, df_one in transformed_data.groupby(self.grain_column_names):
                if grain in dict_known.keys():
                    # Index levels are always sorted, but it is not guaranteed for data frame.
                    df_one.sort_index(inplace=True)
                    # Some y values are known for the given grain.
                    df_one[NOT_KNOWN_Y] = df_one.index.get_level_values(self.time_column_name) > dict_known[grain]
                else:
                    # Nothing is known. All data represent forecast.
                    df_one[NOT_KNOWN_Y] = True
                dfs.append(df_one)
            transformed_data = pd.concat(dfs)
            # Make sure data sorted in the same order as input.
            transformed_data = self.align_output_to_input(X_pred, transformed_data)
            # Some of our values in NOT_KNOWN_Y will be NaN, we need to say, that we "know" this y
            # and replace it with NaN.
            transformed_data[NOT_KNOWN_Y] = transformed_data.apply(
                lambda x: x[NOT_KNOWN_Y] if not pd.isnull(x[NOT_KNOWN_Y]) else False, axis=1
            )
            if horizon_column is not None and horizon_column in transformed_data.columns:
                # We also need to set horizons to make sure that horizons column
                # can be converted to integer.
                transformed_data[horizon_column] = transformed_data.apply(
                    lambda x: x[horizon_column] if not pd.isnull(x[horizon_column]) else 1, axis=1
                )
            # Make sure y is aligned to data frame.
            pred = transformed_data[TimeSeriesInternal.DUMMY_TARGET_COLUMN].values
        else:
            # If we have only destination date no y is known.
            transformed_data[NOT_KNOWN_Y] = True
        horizon_stddevs = np.zeros(len(pred))
        horizon_stddevs.fill(np.NaN)
        try:
            if self._horizon_idx is None and horizon_column is not None:
                self._horizon_idx = cast(
                    int, self._ts_transformer.get_engineered_feature_names().index(horizon_column)
                )
        except ValueError:
            self._horizon_idx = None

        is_not_known = transformed_data[NOT_KNOWN_Y].values.astype(int)
        MOD_TIME_COLUMN_CONSTANT = "mod_time"
        # Retrieve horizon, if available, otherwise calculate it.
        # We also need to find the time difference from the origin to include it as a factor in our uncertainty
        # calculation. This is represented by mod_time and for horizon aware models will reprsent number of
        # max horizons from the original origin, otherwise number steps from origin.
        if self._horizon_idx is not None:
            X_copy_tmp = self._create_prediction_data_frame(X_pred, y_pred, forecast_destination, ignore_data_errors)
            horizons = transformed_data.values[:, self._horizon_idx].astype(int)

            if self._use_recursive_forecast(X_copy_tmp, ignore_data_errors):

                def add_horizon_counter(grp):
                    """
                    Get the modulo time column.

                    This method is used to calculate the number of times the horizon has "rolled". In the case of the
                    rolling/recursive forecast, each time delta that is beyond our max horizon is a forecast from the
                    previous time delta's forecast used as input to the lookback features. Since the estimation is
                    growing each time we recurse, we want to calculate the quantile with some added
                    uncertainty (growing with time). We use the modulo column from this method to do so. We also apply
                    this strategy on a per-grain basis.
                    """
                    grains = grp.name
                    if grains in dict_latest_date:
                        last_known_single_grain = dict_latest_date[grains]
                        forecast_times = grp.index.get_level_values(self.time_column_name)
                        date_grid = pd.date_range(last_known_single_grain, forecast_times.max(), freq=freq)
                        # anything forecast beyond the max horizon will need a time delta to increase uncertainty
                        grp[MOD_TIME_COLUMN_CONSTANT] = [
                            math.ceil(date_grid.get_loc(forecast_times[i]) / self.max_horizon) for i in range(len(grp))
                        ]
                    else:
                        # If we have encountered grain not present in the training set, we will set mod_time to 1
                        # as finally we will get NaN as a prediction.
                        grp[MOD_TIME_COLUMN_CONSTANT] = 1

                    return grp

                mod_time = (
                    transformed_data.groupby(self.grain_column_names)
                    .apply(add_horizon_counter)[MOD_TIME_COLUMN_CONSTANT]
                    .values
                )
            else:
                mod_time = [1] * len(horizons)
        else:
            # If no horizon is present we are doing a forecast with no lookback features.
            # The last known timestamp can be used to calculate the horizon. We can then apply
            # an increase in uncertainty as horizon increases.
            def add_horizon(grp):
                grains = grp.name
                last_known_single_grain = dict_latest_date[grains]
                forecast_times = grp.index.get_level_values(self.time_column_name)
                date_grid = pd.date_range(last_known_single_grain, forecast_times.max(), freq=freq)

                grp[MOD_TIME_COLUMN_CONSTANT] = [date_grid.get_loc(forecast_times[i]) for i in range(len(grp))]
                return grp

            # We can groupby grain and then apply the horizon based on the time index within the grain
            # and the last known timestamps. We still need to know the horizons, but in this case the model
            # is not horizon aware, so there should only be one stddev and any forecast will use that value
            # with horizon (mod_time) used to increase uncertainty.
            mod_time = (
                transformed_data.groupby(self.grain_column_names).apply(add_horizon)[MOD_TIME_COLUMN_CONSTANT].values
            )
            horizons = [1] * len(mod_time)

        for idx, horizon in enumerate(horizons):
            horizon = horizon - 1  # horizon needs to be 1 indexed
            try:
                horizon_stddevs[idx] = self._stddev[horizon] * is_not_known[idx] * math.sqrt(mod_time[idx])
            except IndexError:
                # In case of short training set cv may have nor estimated
                # stdev for highest horizon(s). Fix it by returning np.NaN
                horizon_stddevs[idx] = np.NaN

        # Get the prediction quantiles
        pred_quantiles = self._get_ci(pred, horizon_stddevs, self._quantiles)

        # Get time and grain columns from transformed data
        transformed_data = transformed_data.reset_index()
        time_column = transformed_data[self.time_column_name]
        grain_df = None
        if (self.grain_column_names is not None) and (
            self.grain_column_names[0] != TimeSeriesInternal.DUMMY_GRAIN_COLUMN
        ):
            grain_df = transformed_data[self.grain_column_names]

        return pd.concat((time_column, grain_df, pred_quantiles), axis=1)

    def _postprocess_output(self, X: pd.DataFrame, known_y: Optional[pd.Series]) -> pd.DataFrame:
        """
        Postprocess the data before returning it to user.

        Trim the data frame to the size of input.
        :param X: The data frame to be trimmed.
        :param known_y: The known or inferred y values.
                        We need to replace the existing values by them
        :returns: The data frame with the gap removed.

        """
        # If user have provided known y values, replace forecast by them even
        # if these values were imputed.
        if known_y is not None and any(not pd.isnull(val) for val in known_y):
            PRED_TARGET = "forecast"
            known_df = known_y.rename(TimeSeriesInternal.DUMMY_TARGET_COLUMN).to_frame()
            X.rename({TimeSeriesInternal.DUMMY_TARGET_COLUMN: PRED_TARGET}, axis=1, inplace=True)
            # Align known y and X with merge on indices
            X_merged = X.merge(known_df, left_index=True, right_index=True, how="inner")
            assert X_merged.shape[0] == X.shape[0]

            # Replace all NaNs in the known y column by forecast.

            def swap(x):
                return (
                    x[PRED_TARGET]
                    if pd.isnull(x[TimeSeriesInternal.DUMMY_TARGET_COLUMN])
                    else x[TimeSeriesInternal.DUMMY_TARGET_COLUMN]
                )

            X_merged[TimeSeriesInternal.DUMMY_TARGET_COLUMN] = X_merged.apply(lambda x: swap(x), axis=1)
            X = X_merged.drop(PRED_TARGET, axis=1)
        # If user provided X_pred, make sure returned data frame does not contain the inferred
        # gap between train and test.
        if self.forecast_origin:  # Filter only if we were provided by data frame.
            X = X.groupby(self.grain_column_names, group_keys=False).apply(
                lambda df: df[df.index.get_level_values(self._time_col_name) >= self.forecast_origin.get(df.name)]
                if df.name in self.forecast_origin.keys()
                else df
            )
        # self.forecast_origin dictionary is empty, no trimming required.
        return X

    def predict(self, X: pd.DataFrame) -> None:
        logger.error("The API predict is not supported for a forecast model.")
        raise AzureMLError.create(
            ForecastPredictNotSupported,
            target="predict",
            reference_code=ReferenceCodes._FORECASTING_PREDICT_NOT_SUPPORT,
        )

    def preaggregate_data_set(
        self, df: pd.DataFrame, y: Optional[np.ndarray] = None, is_training_set: bool = False
    ) -> Tuple[pd.DataFrame, Optional[np.ndarray]]:
        """
        Aggregate the prediction data set.

        **Note:** This method does not guarantee that the data set will be aggregated.
        This will happen only if the data set contains the duplicated time stamps or out of grid dates.
        :param df: The data set to be aggregated.
        :patam y: The target values.
        :param is_training_set: If true, the data represent training set.
        :return: The aggregated or intact data set if no aggregation is required.
        """
        return ForecastingPipelineWrapper.static_preaggregate_data_set(
            self._ts_transformer, self.time_column_name, self.grain_column_names, df, y, is_training_set
        )

    def _raise_insufficient_data_maybe(
        self, X: pd.DataFrame, grain: Optional[str], min_points: int, operation: str
    ) -> None:
        """
        Raise the exception about insufficient grain size.

        :param X: The grain to be checked.
        :param grain: The grain name.
        :param min_points: The minimal number of points needed.
        :param operation: The name of an operation for which the validation
                          is being performed.
        :raises: DataException
        """
        if X.shape[0] < min_points:
            raise AzureMLError.create(
                TimeseriesInsufficientDataForecast,
                target="X",
                grains=grain,
                operation=operation,
                max_horizon=self._ts_transformer.max_horizon,
                lags=str(self._ts_transformer.get_target_lags()),
                window_size=self._ts_transformer.get_target_rolling_window_size(),
                reference_code=ReferenceCodes._FORECASTING_INSUFFICIENT_DATA,
            )

    def _preprocess_check(
        self, X: pd.DataFrame, y: np.ndarray, operation: str, pad_short_grains: bool
    ) -> Tuple[pd.DataFrame, np.ndarray]:
        """
        Do the simple preprocessing and check for model retraining and in sample forecasting.

        :param X: The prediction data frame.
        :param y: The array of target values.
        :param operation: The name of an operation for which the preprocessing
                          is being performed.
        :param pad_short_grains: If true the short grains will be padded.
        :return: The tuple of sanitized data.
        """
        # Data checks.
        self._check_data(X, y, None)
        if X.shape[0] != y.shape[0]:
            raise AzureMLError.create(
                DataShapeMismatch, target="X_and_y", reference_code=ReferenceCodes._FORECASTING_DATA_SHAPE_MISMATCH
            )

        # Ensure the type of a time and grain columns.
        X = self._check_convert_grain_types(X)
        X = self._convert_time_column_name_safe(X, ReferenceCodes._FORECASTING_PREPROCESS_INVALID_VALUE)

        grains = self._ts_transformer.grain_column_names
        if grains == [TimeSeriesInternal.DUMMY_GRAIN_COLUMN]:
            grains = []

        freq_str = self._ts_transformer.freq
        # If the frequency can not be converted to a pd.DateOffset,
        # then we need to set it to None.
        try:
            to_offset(freq_str)
        except BaseException:
            freq_str = None

        # Fix the data set frequency and aggregate data.
        fixed_ds = fix_data_set_regularity_may_be(
            X,
            y,
            time_column_name=self._ts_transformer.time_column_name,
            grain_column_names=grains,
            freq=freq_str,
            target_aggregation_function=self._ts_transformer.parameters.get(
                TimeSeries.TARGET_AGG_FUN, TimeSeriesInternal.TARGET_AGG_FUN_DEFAULT
            ),
            featurization_config=self._ts_transformer._featurization_config,
            # We do not set the reference code here, because we check that freq can be
            # convertible to string or None in AutoMLTimeSeriesSettings.
            freq_ref_code="",
        )
        # If short grain padding is disabled, we need to check if the short grain
        # are present.
        short_series_handling_configuration = self._ts_transformer.parameters.get(
            TimeSeries.SHORT_SERIES_HANDLING_CONFIG, TimeSeriesInternal.SHORT_SERIES_HANDLING_CONFIG_DEFAULT
        )
        if short_series_handling_configuration is None:
            min_points = get_min_points(
                window_size=self._ts_transformer.get_target_rolling_window_size(),
                lags=self._ts_transformer.get_target_lags(),
                max_horizon=self._ts_transformer.max_horizon,
                cv=None,
                n_step=None,
            )
            if self._ts_transformer.grain_column_names == [TimeSeriesInternal.DUMMY_GRAIN_COLUMN]:
                self._raise_insufficient_data_maybe(fixed_ds.data_x, None, min_points, operation)
            else:
                for grain, df in fixed_ds.data_x.groupby(self._ts_transformer.grain_column_names):
                    self._raise_insufficient_data_maybe(df, grain, min_points, operation)
        # Pad the short series if needed
        # We have to import short_grain_padding here because importing it at the top causes the cyclic
        # import while importing ml_engine.
        from ..timeseries import _short_grain_padding

        if pad_short_grains:
            X, y = _short_grain_padding.pad_short_grains_or_raise(
                fixed_ds.data_x,
                cast(np.ndarray, fixed_ds.data_y),
                freq=self._ts_transformer.freq_offset,
                time_column_name=self._ts_transformer.time_column_name,
                grain_column_names=grains,
                short_series_handling_configuration=short_series_handling_configuration,
                window_size=self._ts_transformer.get_target_rolling_window_size(),
                lags=self._ts_transformer.get_target_lags(),
                max_horizon=self._ts_transformer.max_horizon,
                n_cross_validations=None,
                cv_step_size=None,
                featurization=self._ts_transformer._featurization_config,
                ref_code="",
            )
            return X, y
        return fixed_ds.data_x, cast(np.ndarray, fixed_ds.data_y)

    def _in_sample_fit(self, X: pd.DataFrame, y: np.ndarray) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Predict the data from the training set.

        :param X: The prediction data frame.
        :param y: The array of target values.
        :return: The array and the data frame with predictions.
        """
        X_copy = X.copy()
        X_agg, _ = self.preaggregate_data_set(X, y, is_training_set=False)
        was_aggregated = False
        if X_agg.shape != X.shape:
            was_aggregated = True
        X_copy, y = self._preprocess_check(X_copy, y, "in-sample forecasting", False)
        X_copy = self._create_prediction_data_frame(X_copy, y, forecast_destination=None, ignore_data_errors=True)
        y = X_copy.pop(TimeSeriesInternal.DUMMY_TARGET_COLUMN).values
        test_feats = None  # type: Optional[pd.DataFrame]
        for i in range(len(self.pipeline.steps) - 1):
            # FIXME: Work item #400231
            if type(self.pipeline.steps[i][1]).__name__ == "TimeSeriesTransformer":
                test_feats = self.pipeline.steps[i][1].transform(X_copy, y)
                # We do not need the target column now.
                # The target column is deleted by the rolling window during transform.
                # If there is no rolling window we need to make sure the column was dropped.
                if self._ts_transformer.target_column_name in test_feats.columns:
                    # We want to store the y_known_series for future use.
                    test_feats.drop(self._ts_transformer.target_column_name, inplace=True, axis=1)
                # If origin times are present, remove nans from look-back features and select the latest origins
                if self.origin_col_name in test_feats.index.names:
                    y = np.zeros(test_feats.shape[0])
                    test_feats, _ = self._ts_transformer._remove_nans_from_look_back_features(test_feats, y)
                    test_feats = self._ts_transformer._select_latest_origin_dates(test_feats)
                X_copy = test_feats.copy()
            else:
                X_copy = self.pipeline.steps[i][1].transform(X_copy)
        # TODO: refactor prediction in the separate method and make AML style error.
        try:
            y_preds = self.pipeline.steps[-1][1].predict(X_copy)
        except Exception as e:
            raise PredictionException.from_exception(
                e, has_pii=True, target="ForecastingPipelineWrapper"
            ).with_generic_msg(_generic_prediction_error_message.format(self.__class__.__name__))

        cast(pd.DataFrame, test_feats)[TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y_preds
        test_feats = self._postprocess_output(test_feats, known_y=None)
        # Order the time series data frame as it was encountered as in initial input.
        if not was_aggregated:
            test_feats = self.align_output_to_input(X, test_feats)
        y_pred = test_feats[TimeSeriesInternal.DUMMY_TARGET_COLUMN].values
        return y_pred, test_feats

    def fit(self, X: pd.DataFrame, y: np.ndarray) -> "ForecastingPipelineWrapper":
        """
        Train the model on different data.

        :param X: The prediction data frame.
        :param y: The array of target values.
        :return: The instance of ForecastingPipelineWrapper trained on X and y.
        """
        X.reset_index(drop=True, inplace=True)
        # Drop rows, containing NaN in timestamps or in y.

        if any(np.isnan(y_one) for y_one in y) or X[self.time_column_name].isnull().any():
            X[TimeSeriesInternal.DUMMY_TARGET_COLUMN] = y
            X = X.dropna(subset=[self.time_column_name, TimeSeriesInternal.DUMMY_TARGET_COLUMN], inplace=False, axis=0)
            y = X.pop(TimeSeriesInternal.DUMMY_TARGET_COLUMN).values
        X, y = self._preprocess_check(X, y, "fitting", True)
        for i in range(len(self.pipeline.steps) - 1):
            # FIXME: Work item #400231
            if type(self.pipeline.steps[i][1]).__name__ == "TimeSeriesTransformer":
                X = self.pipeline.steps[i][1].fit_transform(X, y)
                y = X.pop(TimeSeriesInternal.DUMMY_TARGET_COLUMN).values
                # If origin times are present, remove nans from look-back features and select the latest origins
                if self.origin_col_name in X.index.names:
                    X, y = self._ts_transformer._remove_nans_from_look_back_features(X, y)
            else:
                if hasattr(self.pipeline.steps[i][1], "fit_transform"):
                    X = self.pipeline.steps[i][1].fit_transform(X, y)
                else:
                    X = self.pipeline.steps[i][1].fit(X, y).transform(X)
        # TODO: refactor prediction in the separate method and make AML style error.
        try:
            self.pipeline.steps[-1][1].fit(X, y)
        except Exception as e:
            raise AzureMLError.create(
                GenericFitError,
                reference_code=ReferenceCodes._FORECASTING_PIPELINE_FIT_FAILURE,
                transformer_name=self.__class__.__name__,
            ) from e
        return self

    @property
    def max_horizon(self) -> int:
        """Return max hiorizon used in the model."""
        return cast(int, self._ts_transformer.max_horizon)

    @property
    def target_lags(self) -> List[int]:
        """Return target lags if any."""
        return cast(List[int], self._ts_transformer.get_target_lags())

    @property
    def target_rolling_window_size(self) -> int:
        """Return the size of rolling window."""
        return cast(int, self._ts_transformer.get_target_rolling_window_size())

    @staticmethod
    def static_preaggregate_data_set(
        ts_transformer: "TimeSeriesTransformer",
        time_column_name: str,
        grain_column_names: List[str],
        df: pd.DataFrame,
        y: Optional[np.ndarray] = None,
        is_training_set: bool = False,
    ) -> Tuple[pd.DataFrame, Optional[np.ndarray]]:
        """
        Aggregate the prediction data set.

        **Note:** This method does not guarantee that the data set will be aggregated.
        This will happen only if the data set contains the duplicated time stamps or out of grid dates.
        :param ts_transformer: The timeseries tranformer used for training.
        :param time_column_name: name of the time column.
        :param grain_column_names: List of grain column names.
        :param df: The data set to be aggregated.
        :patam y: The target values.
        :param is_training_set: If true, the data represent training set.
        :return: The aggregated or intact data set if no aggregation is required.
        """
        agg_fun = ts_transformer.parameters.get(TimeSeries.TARGET_AGG_FUN)
        set_columns = set(ts_transformer.columns) if ts_transformer.columns is not None else set()
        ext_resgressors = set(df.columns)
        ext_resgressors.discard(time_column_name)
        for grain in grain_column_names:
            ext_resgressors.discard(grain)
        diff_col = set_columns.symmetric_difference(set(df.columns))
        # We  do not have the TimeSeriesInternal.DUMMY_ORDER_COLUMN during inference time.
        diff_col.discard(TimeSeriesInternal.DUMMY_ORDER_COLUMN)
        diff_col.discard(TimeSeriesInternal.DUMMY_GRAIN_COLUMN)
        detected_types = None
        if (
            agg_fun and
            ts_transformer.parameters.get(TimeSeries.FREQUENCY) is not None and
            (diff_col or (not diff_col and not ext_resgressors))
        ):
            # If we have all the data for aggregation and input data set contains columns different
            # from the transformer was fit on, we need to check if the input data set needs to be aggregated.
            detected_types = _freq_aggregator.get_column_types(
                columns_train=list(ts_transformer.columns) if ts_transformer.columns is not None else [],
                columns_test=list(df.columns),
                time_column_name=time_column_name,
                grain_column_names=grain_column_names,
            )

        if detected_types is None or detected_types.detection_failed:
            return df, y

        ts_data = TimeSeriesDataConfig(
            df,
            y,
            time_column_name=time_column_name,
            time_series_id_column_names=grain_column_names,
            freq=ts_transformer.freq_offset,
            target_aggregation_function=agg_fun,
            featurization_config=ts_transformer._featurization_config,
        )
        # At this point we do not detect the data set frequency
        # and set it to None to perform the aggregation anyways.
        # If numeric columns are not empty we have to aggregate as
        # the training data have different columns then testing data.
        # If there is no numeric columns, we will aggregate only if
        # the data do not fit into the grid.
        # In the forecast time we also have to assume that the data frequency is the same
        # as forecast frequency.
        df_fixed, y_pred = _freq_aggregator.aggregate_dataset(
            ts_data,
            dataset_freq=ts_transformer.freq_offset,
            force_aggregation=ext_resgressors != set(),
            start_times=None if is_training_set else ts_transformer.dict_latest_date,
            column_types=detected_types,
        )
        if df_fixed.shape[0] == 0:
            raise AzureMLError.create(
                ForecastingEmptyDataAfterAggregation,
                target="X_pred",
                reference_code=ReferenceCodes._FORECASTING_EMPTY_AGGREGATION,
            )
        return df_fixed, y_pred

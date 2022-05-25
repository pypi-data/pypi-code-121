# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, cast, Dict, List, Optional, Tuple, Union
from typing import TYPE_CHECKING
from abc import abstractmethod, ABC
import numpy as np
import pandas as pd
from pandas.tseries.frequencies import to_offset
from sklearn.pipeline import Pipeline as SKPipeline
import uuid
import warnings

from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared import constants
from azureml.automl.core.shared.types import GrainType
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.exceptions import DataException, ValidationException
from azureml.automl.core.shared.constants import TimeSeriesInternal
from azureml.automl.runtime import _freq_aggregator
from azureml.automl.runtime.shared import forecasting_utils
from azureml.automl.runtime._time_series_data_set import TimeSeriesDataSet
from azureml.automl.runtime._time_series_data_config import TimeSeriesDataConfig

from azureml.automl.core.shared.forecasting_exception import (
    ForecastingDataException, ForecastingConfigException
)
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    AutoMLInternal,
    ForecastingEmptyDataAfterAggregation,
    MissingColumnsInData,
    PandasDatetimeConversion,
    TimeseriesDfContainsNaN,
    TimeseriesGrainAbsentNoLastDate,
    TimeseriesMissingValuesInY,
    TimeseriesNoUsableGrains,
    TimeseriesWrongShapeDataSizeMismatch,
    TimeseriesWrongShapeDataEarlyDest,
)

# NOTE:
# Here we import type checking only for type checking time.
# during runtime TYPE_CHECKING is set to False.
if TYPE_CHECKING:
    from azureml._common._error_definition.error_definition import ErrorDefinition
    from azureml.automl.runtime.featurizer.transformer.timeseries.timeseries_transformer import TimeSeriesTransformer


class ForecastModelWrapperBase(ABC):
    """Base class for forecast model wrapper."""
    FATAL_NO_TS_TRANSFORM = "The time series transform is absent. " "Please try training model again."

    def __init__(
            self,
            ts_transformer: Optional['TimeSeriesTransformer'] = None,
            y_transformer: Optional[SKPipeline] = None
    ):
        self._y_transformer = y_transformer
        self._quantiles = [.5]
        self._horizon_idx = None  # type: Optional[int]
        self.forecast_origin = {}  # type: Dict[GrainType, pd.Timestamp]
        self._ts_transformer = None  # type: Optional['TimeSeriesTransformer']
        self._time_col_name = None  # type: Optional[str]
        self._origin_col_name = None  # type: Optional[str]
        self.grain_column_names = None  # type: Optional[GrainType]
        self.target_column_name = None  # type: Optional[str]
        self._ts_transformer = cast('TimeSeriesTransformer', self._ts_transformer)
        self.grain_column_names = cast(List[str], self.grain_column_names)
        if ts_transformer is not None:
            self._update_params(ts_transformer)

    def _update_params(self, ts_transformer: 'TimeSeriesTransformer') -> None:
        self._ts_transformer = ts_transformer
        self._origin_col_name = ts_transformer.origin_column_name
        self._time_col_name = ts_transformer.time_column_name
        self.grain_column_names = ts_transformer.grain_column_names
        self.target_column_name = ts_transformer.target_column_name
        self.data_frequency = cast(pd.DateOffset, ts_transformer.freq_offset)

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
            self._origin_col_name = self._get_not_none_ts_transformer().origin_column_name
        # TODO: Double check type: Union[str, List[str]]
        ret = self._origin_col_name if self._origin_col_name \
            else constants.TimeSeriesInternal.ORIGIN_TIME_COLNAME_DEFAULT
        return cast(str, ret)

    @property
    def max_horizon(self) -> int:
        """Return max hiorizon used in the model."""
        return self._get_not_none_ts_transformer().max_horizon

    @property
    def target_lags(self) -> List[int]:
        """Return target lags if any."""
        return self._get_not_none_ts_transformer().get_target_lags()

    @property
    def target_rolling_window_size(self) -> int:
        """Return the size of rolling window."""
        return self._get_not_none_ts_transformer().get_target_rolling_window_size()

    @abstractmethod
    def _regular_forecast(
            self,
            X_copy: pd.DataFrame,
            ignore_data_errors: bool,
            is_rolling_forecast: bool = False) -> pd.DataFrame:
        raise NotImplementedError()

    @abstractmethod
    def _check_data(self, X_pred: pd.DataFrame,
                    y_pred: Union[pd.DataFrame, np.ndarray],
                    forecast_destination: pd.Timestamp) -> None:
        raise NotImplementedError()

    @abstractmethod
    def is_grain_dropped(self, grain: GrainType) -> bool:
        """
        Return true if the grain is going to be dropped.

        :param grain: The grain to test if it will be dropped.
        :return: True if the grain will be dropped.
        """
        raise NotImplementedError()

    def rolling_evaluation(self,
                           X_pred: pd.DataFrame,
                           y_pred: Union[pd.DataFrame,
                                         np.ndarray],
                           ignore_data_errors: bool = False) -> Tuple[np.ndarray, pd.DataFrame]:
        """"
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
        y_pred = test_feats[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN].values

        if self._y_transformer is not None:
            y_pred = self._y_transformer.inverse_transform(y_pred)

        return y_pred, test_feats

    def _rolling_evaluation_one_grain(self,
                                      df_pred: pd.DataFrame,
                                      y_pred: pd.Series,
                                      ignore_data_errors: bool,
                                      grain_name: GrainType) -> pd.DataFrame:
        """"
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
            expand_wind = (df_pred[self.time_column_name] < horizon_time)
            df_pred_expand = df_pred[expand_wind]
            if origin_time != start_time:
                # Set the context by including actuals up-to the origin time
                test_context_expand_wind = (df_pred[self.time_column_name] < origin_time)
                context_expand_wind = (df_pred_expand[self.time_column_name] < origin_time)
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
                temp_name = 'temp_{}'.format(uuid.uuid4())
                dict_rename[ix_name] = temp_name
                dict_rename_back[temp_name] = ix_name
        if len(dict_rename) > 0:
            transformed.rename(dict_rename, axis=1, inplace=True)
        transformed.reset_index(drop=False, inplace=True)
        merge_ix = [self.time_column_name]
        # We add grain column to index only if it is non dummy.
        if self.grain_column_list != [constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN]:
            merge_ix += self.grain_column_list
        X_merge = X_input[merge_ix]
        # Make sure, we have a correct dtype.
        for col in X_merge.columns:
            X_merge[col] = X_merge[col].astype(transformed[col].dtype)
        transformed = X_merge.merge(transformed, how='left', on=merge_ix)
        # return old index back
        transformed.set_index(index, inplace=True, drop=True)
        # If we have renamed any columns, we need to set it back.
        if len(dict_rename_back) > 0:
            transformed.rename(dict_rename_back, axis=1, inplace=True)
        return transformed

    def _infer_y(self,
                 X: pd.DataFrame,
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
        ts_transformer = self._get_not_none_ts_transformer()
        y_imputer = ts_transformer.y_imputers[grain]
        tsds_X = TimeSeriesDataSet(
            X,
            time_column_name=ts_transformer.time_column_name,
            time_series_id_column_names=ts_transformer.grain_column_names,
            target_column_name=ts_transformer.target_column_name)
        if fill_datetime_gap:
            tsds_X = tsds_X.fill_datetime_gap(freq=self.data_frequency)
        X = y_imputer.transform(tsds_X).data
        X.reset_index(inplace=True, drop=False)
        return X

    def _check_data_rolling_evaluation(self,
                                       X_pred: pd.DataFrame,
                                       y_pred: Union[pd.DataFrame,
                                                     np.ndarray],
                                       ignore_data_errors: bool) -> None:
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
            self._warn_or_raise(TimeseriesMissingValuesInY,
                                ReferenceCodes._ROLLING_EVALUATION_NO_Y,
                                ignore_data_errors=False)

    def _warn_or_raise(
            self,
            error_definition_class: 'ErrorDefinition',
            ref_code: str,
            ignore_data_errors: bool) -> None:
        """
        Raise DataException if the ignore_data_errors is False.

        :param warning_text: The text of error or warning.
        :param ignore_data_errors: if True raise the error, warn otherwise.
        """
        # All error definitions currently being passed to this function don't need any message_params.
        # Pass in error message_parameters via kwargs on `_warn_or_raise` and plumb them below, should we need to
        # create errors below with message_parameters
        error = AzureMLError.create(error_definition_class,
                                    reference_code=ref_code)
        if ignore_data_errors:
            warnings.warn(error.error_message)
        else:
            raise DataException._with_error(error)

    def preaggregate_data_set(
            self,
            df: pd.DataFrame,
            y: Optional[np.ndarray] = None,
            is_training_set: bool = False) -> Tuple[pd.DataFrame, Optional[np.ndarray]]:
        """
        Aggregate the prediction data set.

        **Note:** This method does not guarantee that the data set will be aggregated.
        This will happen only if the data set contains the duplicated time stamps or out of grid dates.
        :param df: The data set to be aggregated.
        :patam y: The target values.
        :param is_training_set: If true, the data represent training set.
        :return: The aggregated or intact data set if no aggregation is required.
        """
        return ForecastModelWrapperBase.static_preaggregate_data_set(
            self._get_not_none_ts_transformer(),
            self.time_column_name,
            self.grain_column_list,
            df, y, is_training_set)

    @staticmethod
    def static_preaggregate_data_set(
            ts_transformer: 'TimeSeriesTransformer',
            time_column_name: str,
            grain_column_names: List[str],
            df: pd.DataFrame,
            y: Optional[np.ndarray] = None,
            is_training_set: bool = False) -> Tuple[pd.DataFrame, Optional[np.ndarray]]:
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
        agg_fun = ts_transformer.parameters.get(constants.TimeSeries.TARGET_AGG_FUN)
        set_columns = set(ts_transformer.columns) if ts_transformer.columns is not None else set()
        ext_resgressors = set(df.columns)
        ext_resgressors.discard(time_column_name)
        for grain in grain_column_names:
            ext_resgressors.discard(grain)
        diff_col = set_columns.symmetric_difference(set(df.columns))
        # We  do not have the TimeSeriesInternal.DUMMY_ORDER_COLUMN during inference time.
        diff_col.discard(constants.TimeSeriesInternal.DUMMY_ORDER_COLUMN)
        diff_col.discard(constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN)
        detected_types = None
        if agg_fun and ts_transformer.parameters.get(
                constants.TimeSeries.FREQUENCY) is not None and (
                diff_col or (
                not diff_col and not ext_resgressors)):
            # If we have all the data for aggregation and input data set contains columns different
            # from the transformer was fit on, we need to check if the input data set needs to be aggregated.
            detected_types = _freq_aggregator.get_column_types(
                columns_train=list(ts_transformer.columns) if ts_transformer.columns is not None else [],
                columns_test=list(df.columns),
                time_column_name=time_column_name,
                grain_column_names=grain_column_names)

        if detected_types is None or detected_types.detection_failed:
            return df, y

        ts_data = TimeSeriesDataConfig(
            df, y, time_column_name=time_column_name,
            time_series_id_column_names=grain_column_names,
            freq=ts_transformer.freq_offset, target_aggregation_function=agg_fun,
            featurization_config=ts_transformer._featurization_config)
        # At this point we do not detect the data set frequency
        # and set it to None to perform the aggregation anyways.
        # If numeric columns are not empty we have to aggregate as
        # the training data have different columns then testing data.
        # If there is no numeric columns, we will aggregate only if
        # the data do not fit into the grid.
        # In the forecast time we also have to assume that the data frequency is the same
        # as forecast frequency.
        df_fixed, y_pred = _freq_aggregator.aggregate_dataset(
            ts_data, dataset_freq=ts_transformer.freq_offset,
            force_aggregation=ext_resgressors != set(),
            start_times=None if is_training_set else ts_transformer.dict_latest_date,
            column_types=detected_types)
        if df_fixed.shape[0] == 0:
            raise DataException._with_error(
                AzureMLError.create(
                    ForecastingEmptyDataAfterAggregation, target="X_pred",
                    reference_code=ReferenceCodes._FORECASTING_EMPTY_AGGREGATION
                )
            )
        return df_fixed, y_pred

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
        except Exception as e:
            raise DataException._with_error(
                AzureMLError.create(PandasDatetimeConversion, column=self.time_column_name,
                                    column_type=X[self.time_column_name].dtype,
                                    target=constants.TimeSeries.TIME_COLUMN_NAME,
                                    reference_code=reference_code),
                inner_exception=e
            ) from e
        return X

    def _create_prediction_data_frame(self,
                                      X_pred: pd.DataFrame,
                                      y_pred: Union[pd.DataFrame, np.ndarray],
                                      forecast_destination: pd.Timestamp,
                                      ignore_data_errors: bool) -> pd.DataFrame:
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
        ts_transformer = self._get_not_none_ts_transformer()
        if X_pred is not None:
            X_copy = X_pred.copy()
            X_copy.reset_index(inplace=True, drop=True)
            if self.grain_column_list[0] == constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN and \
                    self.grain_column_list[0] not in X_copy.columns:
                X_copy[constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN] = \
                    constants.TimeSeriesInternal.DUMMY_GRAIN_COLUMN
            # Remember the forecast origins for each grain.
            # We will trim the data frame by these values at the end.
            # Also do the sanity check if there is at least one known grain.
            has_known_grain = False
            for grain, df_one in X_copy.groupby(self.grain_column_list):
                self.forecast_origin[grain] = df_one[self._time_col_name].min()
                has_known_grain = has_known_grain or grain in ts_transformer.dict_latest_date
            if not has_known_grain:
                raise ForecastingDataException._with_error(
                    AzureMLError.create(TimeseriesNoUsableGrains,
                                        target='X_test',
                                        reference_code=ReferenceCodes._TS_NO_USABLE_GRAINS))
            special_columns = self.grain_column_list.copy()
            special_columns.append(ts_transformer.time_column_name)
            if self.origin_col_name in X_copy.columns:
                special_columns.append(self.origin_col_name)
            if ts_transformer.group_column in X_copy.columns:
                special_columns.append(ts_transformer.group_column)
            if ts_transformer.drop_column_names:
                dropping_columns = ts_transformer.drop_column_names
            else:
                dropping_columns = []
            categorical_columns = []
            dtypes_transformer = forecasting_utils.get_pipeline_step(
                ts_transformer.pipeline, constants.TimeSeriesInternal.RESTORE_DTYPES)
            if dtypes_transformer is not None:
                categorical_columns = dtypes_transformer.get_non_numeric_columns()
            for column in X_copy.columns:
                if column not in special_columns and \
                        column not in dropping_columns and \
                        column not in categorical_columns and \
                        column in X_copy.select_dtypes(include=[np.number]).columns and \
                        all(np.isnan(float(var)) for var in X_copy[column].values):
                    self._warn_or_raise(TimeseriesDfContainsNaN,
                                        ReferenceCodes._FORECASTING_COLUMN_IS_NAN,
                                        ignore_data_errors)
                    break

            if y_pred is None:
                y_pred = np.repeat(np.NaN, len(X_pred))
            if y_pred.shape[0] != X_pred.shape[0]:
                # May be we need to revisit this assertion.
                raise ForecastingDataException._with_error(
                    AzureMLError.create(
                        TimeseriesWrongShapeDataSizeMismatch,
                        target='y_pred.shape[0] != X_pred.shape[0]',
                        reference_code=ReferenceCodes._TS_WRONG_SHAPE_CREATE_PRED_DF,
                        var1_name='X_pred',
                        var1_len=X_pred.shape[0],
                        var2_name='y_pred',
                        var2_len=y_pred.shape[0]
                    )
                )
            if isinstance(y_pred, pd.DataFrame):
                if ts_transformer.target_column_name not in y_pred.columns:
                    raise ForecastingConfigException._with_error(
                        AzureMLError.create(
                            MissingColumnsInData,
                            target='y_pred',
                            reference_code=ReferenceCodes._TSDF_INVALID_ARG_FC_PIPELINE_NO_TARGET_IN_Y_DF,
                            columns='target value column',
                            data_object_name='y_pred'
                        )
                    )
                X_copy = pd.merge(
                    left=X_copy,
                    right=y_pred,
                    how='left',
                    left_index=True,
                    right_index=True)
                if X_copy.shape[0] != X_pred.shape[0]:
                    raise ForecastingDataException._with_error(
                        AzureMLError.create(
                            TimeseriesWrongShapeDataSizeMismatch,
                            target='X_copy.shape[0] != X_pred.shape[0]',
                            reference_code=ReferenceCodes._TS_WRONG_SHAPE_CREATE_PRED_DF_XCPY_XPRED,
                            var1_name='X_copy',
                            var1_len=X_copy.shape[0],
                            var2_name='X_pred',
                            var2_len=X_pred.shape[0]
                        )
                    )
            elif isinstance(y_pred, np.ndarray) and X_copy.shape[0] == y_pred.shape[0]:
                X_copy[ts_transformer.target_column_name] = y_pred
            # y_pred may be pd.DataFrame or np.ndarray only, we are checking it in _check_data.
            # At that point we have generated the data frame which contains Target value column
            # filled with y_pred. The part which will need to be should be
            # filled with np.NaNs.
        else:
            # Create the empty data frame from the last date in the training set for each grain
            # and fill it with NaNs. Impute these data.
            if ts_transformer.dict_latest_date == {}:
                raise ForecastingDataException._with_error(
                    AzureMLError.create(TimeseriesGrainAbsentNoLastDate,
                                        target='ts_transformer.dict_latest_date',
                                        reference_code=ReferenceCodes._TS_GRAIN_ABSENT_MDL_WRP_NO_LAST_DATE)
                )
            dfs = []
            for grain_tuple in ts_transformer.dict_latest_date.keys():
                if pd.Timestamp(forecast_destination) <= ts_transformer.dict_latest_date[grain_tuple]:
                    raise ForecastingDataException._with_error(
                        AzureMLError.create(
                            TimeseriesWrongShapeDataEarlyDest,
                            target='forecast_destination',
                            reference_code=ReferenceCodes._TS_WRONG_SHAPE_FATAL_EARLY_DESTINATION
                        )
                    )
                # Start with the next date after the last seen date.
                start_date = ts_transformer.dict_latest_date[grain_tuple] + to_offset(ts_transformer.freq)
                df_dict = {
                    self._time_col_name: pd.date_range(
                        start=start_date,
                        end=forecast_destination,
                        freq=ts_transformer.freq)}
                if not isinstance(grain_tuple, tuple):
                    df_dict[self.grain_column_list[0]] = grain_tuple
                else:
                    for i in range(len(self.grain_column_list)):
                        df_dict[self.grain_column_list[i]] = grain_tuple[i]
                for col in cast(List[Any], ts_transformer.columns):
                    if col not in df_dict.keys():
                        df_dict[col] = np.NaN
                # target_column_name is not in the data frame columns by
                # default.
                df_dict[ts_transformer.target_column_name] = np.NaN
                dfs.append(pd.DataFrame(df_dict))
            X_copy = pd.concat(dfs)
            # At that point we have generated the data frame which contains target value column.
            # The data frame is filled with imputed data. Only target column is filled with np.NaNs,
            # because all gap between training data and forecast_destination
            # should be predicted.
        return X_copy

    def _get_not_none_ts_transformer(self) -> 'TimeSeriesTransformer':
        if self._ts_transformer is None:
            raise ValidationException._with_error(AzureMLError.create(
                AutoMLInternal, target="ForecastingPipelineWrapper",
                error_details='Failed to initialize ForecastingPipelineWrapper: {}'.format(
                    ForecastModelWrapperBase.FATAL_NO_TS_TRANSFORM))
            )
        return self._ts_transformer

    @property
    def grain_column_list(self) -> List[str]:
        if self.grain_column_names is None:
            return []
        elif isinstance(self.grain_column_names, str):
            return [self.grain_column_names]
        elif isinstance(self.grain_column_names, tuple):
            return [g for g in self.grain_column_names]
        else:
            return self.grain_column_names

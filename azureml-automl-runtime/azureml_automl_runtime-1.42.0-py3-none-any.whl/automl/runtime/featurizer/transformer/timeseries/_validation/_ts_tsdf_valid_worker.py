# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Classes for TimeseriesDataFrameValidationWorker."""
import logging
from typing import Dict, cast, List, Optional, Set, Union

import pandas as pd
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.automl_base_settings import AutoMLBaseSettings
from azureml.automl.core.shared import constants
from azureml.automl.core.shared import utilities
from azureml.automl.core.shared._diagnostics.automl_error_definitions import (
    TimeseriesInvalidTimestamp,
    TimeseriesDfFrequencyNotConsistentGrain,
    TimeseriesDfCannotInferFrequencyFromTSId,
    TimeseriesDfFrequencyGenericError,
    TimeseriesDfMultiFrequenciesDiff,
    TimeseriesDfUniqueTargetValueGrain,
    TimeseriesMaxHorizonWithTimeColumnValueOutOfRange,
    TimeseriesDfFrequencyChanged,
    TimeseriesDfTrainingValidDataNotContiguous,
    TimeseriesInsufficientData,
    TimeseriesInsufficientDataForTCN,
    TimeseriesGrainAbsentValidateTrainValidData)
from azureml.automl.core.shared.constants import (
    ShortSeriesHandlingValues,
    TimeSeries,
    TimeSeriesInternal,
    TimeSeriesWebLinks,
)
from azureml.automl.core.shared.exceptions import DataException, ValidationException
from azureml.automl.core.shared.forecasting_exception import ForecastingDataException
from azureml.automl.core.shared.logging_utilities import function_debug_log_wrapped
from azureml.automl.core.shared.reference_codes import ReferenceCodes
from azureml.automl.core.shared.types import GrainType
from pandas.tseries.frequencies import to_offset

from azureml.automl.runtime._time_series_data_set import TimeSeriesDataSet
from azureml.automl.runtime.featurizer.transformer.timeseries import timeseries_transformer
from azureml.automl.runtime.shared.types import DataInputType
from ._timeseries_validator import TimeseriesValidationParamName
from ._timeseries_validator import TimeseriesValidationParameter
from ._timeseries_validator import TimeseriesValidationWorkerBase


logger = logging.getLogger(__name__)


class TimeseriesDataFrameValidationWorker(TimeseriesValidationWorkerBase):
    """Validation worker for the generated tsdf after the post auto parameter gen."""

    TCN_SINGLE_SERIES_MIN_POINTS = 500
    TCN_MULTI_SERIES_MIN_POINTS = 1000

    def __init__(self) -> None:
        pass

    @function_debug_log_wrapped(logging.INFO)
    def validate(self, param: TimeseriesValidationParameter) -> None:
        """
        Abstract method that validate the auto gen parameter and the train/valid pair.
        """
        automl_settings = param.params[TimeseriesValidationParamName.AUTOML_SETTINGS]
        X = param.params[TimeseriesValidationParamName.X]
        y = param.params[TimeseriesValidationParamName.Y]
        X_valid = param.params[TimeseriesValidationParamName.X_VALID]
        y_valid = param.params[TimeseriesValidationParamName.Y_VALID]
        min_points = param.params[TimeseriesValidationParamName.MIN_POINTS]

        lags = param.params[TimeseriesValidationParamName.LAGS]
        window_size = param.params[TimeseriesValidationParamName.WINDOW_SIZE]
        forecast_horizon = param.params[TimeseriesValidationParamName.FORECAST_HORIZON]
        n_cross_validations = param.params[TimeseriesValidationParamName.N_CROSS_VALIDATIONS]

        tsds = TimeseriesDataFrameValidationWorker._get_and_validate_tsds(
            X, y, automl_settings, forecast_horizon, n_cross_validations, min_points, is_validation_data=False)
        tsdf_valid = None
        if X_valid is not None:
            tsdf_valid = TimeseriesDataFrameValidationWorker._get_and_validate_tsds(
                X_valid,
                y_valid,
                automl_settings,
                forecast_horizon,
                n_cross_validations,
                min_points=0,
                is_validation_data=True)
            TimeseriesDataFrameValidationWorker._validate_timeseries_train_valid_tsds(
                tsds, tsdf_valid, bool(window_size + max(lags)))

    @staticmethod
    def _get_and_validate_tsds(
            X: pd.DataFrame,
            y: DataInputType,
            automl_settings: AutoMLBaseSettings,
            forecast_horizon: int,
            n_cross_validations: int,
            min_points: int = 0,
            is_validation_data: bool = False
    ) -> TimeSeriesDataSet:
        """
        Generate the TimeSeriesDataSet and run validations on it.

        :param X: The data frame with features.
        :param y: The array with targets/labels.
        :param automl_settings: The settings to be used.
        :param forecast_horizon : The max horizon used (after the heuristics were applied).
        :param min_points: The minimal number of points necessary to train the model.
        :param is_validation_data: True if this is a validation data set.
        :return: TimeSeriesDataSet with the data from the X and y.

        """
        # We cast timeseries_param_dict to dictionary, because we have already checked that it is not None
        # before in the _check_timeseries_input method.
        timeseries_param_dict = cast(Dict[str, str], utilities._get_ts_params_dict(automl_settings))
        grains = timeseries_param_dict.get(TimeSeries.GRAIN_COLUMN_NAMES)
        tsds = TimeSeriesDataSet.create_tsds_safe(
            X,
            y,
            TimeSeriesInternal.DUMMY_TARGET_COLUMN,
            timeseries_param_dict.get(TimeSeries.TIME_COLUMN_NAME),  # type: ignore
            timeseries_param_dict.get(
                TimeSeriesInternal.ORIGIN_TIME_COLUMN_NAME,
                TimeSeriesInternal.ORIGIN_TIME_COLNAME_DEFAULT),
            grains,
            timeseries_transformer.get_boolean_col_names(X)
        )
        tsds.data.sort_index(inplace=True)
        frequencies_grain_names = {}  # type: Dict[pd.DateOffset, List[GrainType]]
        short_grains = set()
        all_grains_are_short = True
        if automl_settings.grain_column_names is not None:
            # to deal the problem that user has no input grain
            try:
                freq_by_grain = None  # type: pd.Series
                if automl_settings.freq is None:
                    freq_by_grain = tsds._infer_freq_by_ts_id()
                for data_tuple in tsds.data.groupby(tsds.time_series_id_column_names):
                    grain_name_str = data_tuple[0]
                    df_grain = data_tuple[1]
                    data_points = df_grain.shape[0]

                    if not is_validation_data or df_grain.shape[0] > 1:
                        tsds_grain = tsds.from_data_frame_and_metadata(
                            df_grain, False)
                        # if validation data is only one data point, no need to check freq.
                        # If frequency is provided, check if it is consistent.
                        if automl_settings.freq is None:
                            freq = freq_by_grain[grain_name_str]
                        else:
                            freq = to_offset(automl_settings.freq)
                        if df_grain.shape[0] != 1:
                            # We can not establish the frequency only if df_grain has only one value.
                            if freq is None:
                                raise ForecastingDataException._with_error(
                                    AzureMLError.create(
                                        TimeseriesDfCannotInferFrequencyFromTSId, target='df_grain',
                                        reference_code=ReferenceCodes._TSDF_CANNOT_INFER_FREQ_FROM_TS_ID,
                                        grain_name_str=grain_name_str)
                                )
                            # Check alignment with the inferred frequency
                            TimeseriesDataFrameValidationWorker._check_timeseries_alignment_single_grain(
                                grain_name_str, tsds_grain, freq)

                            if freq in frequencies_grain_names:
                                frequencies_grain_names[freq].append(grain_name_str)
                            else:
                                frequencies_grain_names[freq] = [grain_name_str]
                        # check min data points for train and forecast_horizon  for validation
                        data_points = df_grain[tsds.target_column_name].count()
                        if not is_validation_data:
                            if data_points < min_points:
                                short_grains.add(grain_name_str)
                            else:
                                all_grains_are_short = False
                            TimeseriesDataFrameValidationWorker._check_grain_min_points(
                                data_points, min_points, automl_settings, grain_name=grain_name_str)
                            if df_grain.shape[0] != 1:
                                TimeseriesDataFrameValidationWorker._check_cv_gap_exist(
                                    tsds_grain,
                                    forecast_horizon,
                                    n_cross_validations,
                                    grain_name_str, freq)
                            # check if individual grain has more than 1 unique observation
                            if (not automl_settings.short_series_handling or grain_name_str not in short_grains) and \
                                    (df_grain[tsds.target_column_name].nunique(dropna=True) <= 1):
                                raise ForecastingDataException._with_error(
                                    AzureMLError.create(
                                        TimeseriesDfUniqueTargetValueGrain,
                                        target="grain_target",
                                        grain=grain_name_str,
                                        reference_code=ReferenceCodes._TSDF_UNIQUE_VALUE_IN_GRAIN)
                                )

                    if is_validation_data:
                        if data_points < forecast_horizon:
                            print(("WARNING: Validation set has fewer data points ({}) "
                                   "than forecast_horizon  ({}) for one of time series identifiers. "
                                   "We will be unable to estimate error and predictive quantiles at some horizons. "
                                   "Please consider increasing the validation data to the length of max horizon.").
                                  format(data_points, forecast_horizon))
                        elif data_points > forecast_horizon:
                            print(("WARNING: Validation set has more data points {} "
                                   "than forecast_horizon  {} for one of time series identifiers. "
                                   "Not all validation data will be used in the training. "
                                   "Please consider decreasing the validation data to the length of max horizon.").
                                  format(data_points, forecast_horizon))

            except DataException:
                # If we already have a descriptive Exception, raise it.
                raise
            except Exception as me:
                # If not, raise generic exception.
                raise ForecastingDataException._with_error(
                    AzureMLError.create(
                        TimeseriesDfFrequencyGenericError, target='ts_freq_generic',
                        reference_code=ReferenceCodes._TSDF_FREQUENCY_GENERIC_ERROR
                    ), inner_exception=me
                ) from me

            TimeseriesDataFrameValidationWorker._check_tsdf_frequencies(frequencies_grain_names, short_grains)

        # check all the tsds at the end.
        if not is_validation_data:
            if automl_settings.freq is None:
                tsdf_freq = tsds.infer_freq()
            else:
                tsdf_freq = to_offset(automl_settings.freq)
            number_of_data_points = tsds.data[tsds.target_column_name].count()
            if number_of_data_points >= min_points and automl_settings.grain_column_names is None:
                # All grains can not be false if there is only one grain and it is longer then
                # min_points.
                all_grains_are_short = False
            TimeseriesDataFrameValidationWorker._check_grain_min_points(number_of_data_points, min_points,
                                                                        automl_settings)
            TimeseriesDataFrameValidationWorker._check_tcn_min_points(tsds, number_of_data_points, automl_settings)
            TimeseriesDataFrameValidationWorker._check_cv_gap_exist(tsds, forecast_horizon,
                                                                    n_cross_validations,
                                                                    freq=tsdf_freq)
            # We do not have to check short grain handling options here as we have already padded grains
            # at this point if it was desired. If we are dropping short grains, we should raise the error
            # if all grains are short.
            if all_grains_are_short:
                # We are handling the automl_settings.short_series_handling_configuration being None
                # when we go grain-by-grain.
                window_size = TimeseriesDataFrameValidationWorker._get_window_safe(automl_settings.window_size)
                lags = TimeseriesDataFrameValidationWorker._get_lags_safe(automl_settings.lags)
                raise DataException._with_error(AzureMLError.create(
                    TimeseriesInsufficientData, target="X", grains=str(list(short_grains)),
                    num_cv=automl_settings.n_cross_validations,
                    max_horizon=automl_settings.max_horizon, lags=str(lags), window_size=window_size,
                    cv_step_size=automl_settings.cv_step_size,
                    reference_code=ReferenceCodes._TS_SHORT_GRAINS_ALL_SHORT_FIT)
                )

        return tsds

    @staticmethod
    def _validate_timeseries_train_valid_tsds(tsds_train: TimeSeriesDataSet,
                                              tsds_valid: TimeSeriesDataSet,
                                              has_lookback_features: bool) -> None:
        """
        Validate train-valid pair in the time series task.

        :param tsds_train: The training data set.
        :param tsds_valid: The validation data set.
        :param has_lookback_features: True if rolling window or lag lead is switched on.
        """
        train_grain_data_dict = {grain: tsds_train.from_data_frame_and_metadata(
            df, False) for grain, df in tsds_train.data.groupby(tsds_train.time_series_id_column_names)}
        valid_grain_data_dict = {grain: tsds_valid.from_data_frame_and_metadata(
            df, False) for grain, df in tsds_valid.data.groupby(tsds_train.time_series_id_column_names)}
        train_grain = set(train_grain_data_dict.keys())
        valid_grain = set(valid_grain_data_dict.keys())
        # check grain is the same for train and valid.
        grain_difference = train_grain.symmetric_difference(valid_grain)
        if len(grain_difference) > 0:
            grain_in_train_not_in_valid = train_grain.intersection(grain_difference)
            grain_in_valid_not_in_train = valid_grain.intersection(grain_difference)
            if len(grain_in_train_not_in_valid) > 0:
                grains = ",".join(["[{}]".format(grain) for grain in grain_in_train_not_in_valid])
                dataset_contain = "training"
                dataset_not_contain = "validation"
            if len(grain_in_valid_not_in_train) > 0:
                grains = ",".join(["[{}]".format(grain) for grain in grain_in_valid_not_in_train])
                dataset_contain = "validation"
                dataset_not_contain = "training"
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesGrainAbsentValidateTrainValidData, target='grain_difference',
                                    reference_code=ReferenceCodes._TS_GRAIN_ABSENT_VALIDATE_TRAIN_VALID,
                                    grains=grains,
                                    dataset_contain=dataset_contain,
                                    dataset_not_contain=dataset_not_contain)
            )
        # check per grain contiguous and frequency.
        for grain, tsds_train in train_grain_data_dict.items():
            tsds_valid = valid_grain_data_dict[grain]
            train_freq = tsds_train.infer_freq()
            if train_freq is None:
                # The only reason we cannot determine the frequency is because we have a grain'
                # with one value, or two values, one of which is pd.NaT.
                # In this case we have a short grain, which should be dropped, or we should raise the exception later.
                continue
            if has_lookback_features and tsds_train.time_index.max(
            ) + train_freq != tsds_valid.time_index.min():
                raise ForecastingDataException._with_error(
                    AzureMLError.create(TimeseriesDfTrainingValidDataNotContiguous, target='tsds_valid',
                                        reference_code=ReferenceCodes._TSDF_TRAINING_VALID_DATA_NOT_CONTIGUOUS,
                                        grain=str(grain))
                )
            if tsds_valid.data.shape[0] > 1:
                valid_freq = tsds_valid.infer_freq()
                if train_freq != valid_freq:
                    # Check if frequencies are compatible.
                    first_date = tsds_train.time_index.max() + train_freq
                    grid = set(pd.date_range(
                        start=first_date, end=tsds_valid.time_index.max(), freq=train_freq))
                    if not set(tsds_valid.time_index).issubset(grid):
                        raise ForecastingDataException._with_error(
                            AzureMLError.create(TimeseriesDfFrequencyChanged, target='train_freq',
                                                reference_code=ReferenceCodes._TSDF_FREQUENCY_CHANGED,
                                                grain=str(grain),
                                                train_freq=train_freq,
                                                valid_freq=valid_freq)
                        )

    @staticmethod
    def _check_grain_min_points(number_of_data_points: int,
                                min_points: int,
                                automl_settings: AutoMLBaseSettings,
                                grain_name: Optional[GrainType] = None) -> None:
        """
        Check if each of the grain(series) contains minimal number of the data points.

        :param number_of_data_points: The number of data points in one grain.
        :param min_points: The minimal number of points required for training.
        :param automl_settings: The autoML settings.
        :param grain_name: The name of a grain being checked.
        :raises: DataException
        """
        # First check if we have the short series handling configuration and then fall back
        # to the legacy mechanism.
        has_config = hasattr(automl_settings,
                             TimeSeries.SHORT_SERIES_HANDLING_CONFIG)
        config_val = automl_settings.short_series_handling_configuration if has_config else None
        if (has_config and
                config_val == ShortSeriesHandlingValues.SHORT_SERIES_HANDLING_AUTO or
                config_val == ShortSeriesHandlingValues.SHORT_SERIES_HANDLING_DROP):
            # If we are going to remove short series, do not validate for it.
            # If all series are too short, grain dropper will throw an error.
            return
        if (not has_config and
                hasattr(automl_settings, TimeSeries.SHORT_SERIES_HANDLING) and
                getattr(automl_settings, TimeSeries.SHORT_SERIES_HANDLING)):
            # If we are going to remove short series, do not validate for it.
            # If all series are too short, grain dropper will throw an error.
            return

        if number_of_data_points < min_points:
            window_size = TimeseriesDataFrameValidationWorker._get_window_safe(automl_settings.window_size)
            lags = TimeseriesDataFrameValidationWorker._get_lags_safe(automl_settings.lags)
            if grain_name is None:
                raise DataException._with_error(AzureMLError.create(
                    TimeseriesInsufficientData, target="X", grains=grain_name,
                    num_cv=automl_settings.n_cross_validations,
                    max_horizon=automl_settings.max_horizon, lags=str(lags), window_size=window_size,
                    cv_step_size=automl_settings.cv_step_size)
                )
            if not isinstance(grain_name, list) and not isinstance(grain_name, tuple):
                grain_name = [grain_name]

            raise DataException._with_error(AzureMLError.create(
                TimeseriesInsufficientData, target="X", grains=str(grain_name),
                num_cv=automl_settings.n_cross_validations, max_horizon=automl_settings.max_horizon, lags=str(lags),
                window_size=window_size, cv_step_size=automl_settings.cv_step_size)
            )

    @staticmethod
    def _check_timeseries_alignment_single_grain(
            grain_level: GrainType, df: TimeSeriesDataSet,
            freq: pd.DateOffset) -> None:
        """
        Check if single timeseries (single grain) is aligned to the given frequency.

        :param grain_level: The name of a grain.
        :param df: The dataframe to be tested.
        :param freq: Frequency to check alignment against.
        """
        time_index = df.time_index
        if not isinstance(time_index[0], pd.Timestamp):
            raise ValidationException._with_error(AzureMLError.create(TimeseriesInvalidTimestamp, target="X"))

        onfreq_time = pd.date_range(start=time_index.min(), end=time_index.max(), freq=freq)
        if not set(time_index).issubset(onfreq_time):
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesDfFrequencyNotConsistentGrain,
                                    target='_check_timeseries_alignment_single_grain.time_index',
                                    reference_code=ReferenceCodes._TSDF_FREQUENCY_NOT_CONSISTENT_SINGLE_GRAIN,
                                    grain_level=str(grain_level),
                                    freq=str(freq),
                                    forecasting_config=TimeSeriesWebLinks.FORECAST_CONFIG_DOC))

    @staticmethod
    def _check_cv_gap_exist(tsds: TimeSeriesDataSet,
                            max_horizon: int,
                            n_cross_validations: Optional[int] = None,
                            grain_name: Optional[str] = None,
                            freq: Optional[pd.DateOffset] = None) -> None:
        """
        Check if one of the cross validation splits lacks the data.

        :param tsds: The time series data set with one grain.
        :param max_horizon: The maximal horizon, used for prediction.
        :param n_cross_validations: The number of cross validations.
        :param grain_name: The grain being analyzed if any.
        :param freq: The frequency of the data in the time series data frame.
        """
        if n_cross_validations is not None:
            if freq is None:
                # We have already checked the data for minimal number of points,
                # so we know that infer_freq() will not return None.
                freq = cast(pd.DateOffset, tsds.infer_freq())
            for i in range(n_cross_validations):
                # In this code we are estimating the number of missing values in the cross
                # validation fold.
                # if this amount is bigger then some arbitrary number, currently 25%
                # the validation is considered to be failed.
                max_time = tsds.time_index.max()
                # pandas bug: https://github.com/pandas-dev/pandas/issues/33683
                # may result in weird behavior when freq * 0 is applied. For that reason,
                # end time will have special handling. Start time will always have multiplier
                # of at least one since max_horizon must be >= 1
                end_time = max_time if i != 0 else max_time - i * freq
                try:
                    expected_dates = pd.date_range(start=max_time - (i + max_horizon) * freq,
                                                   end=end_time,
                                                   freq=freq)
                except pd.errors.OutOfBoundsDatetime as e:
                    raise ForecastingDataException._with_error(
                        AzureMLError.create(
                            TimeseriesMaxHorizonWithTimeColumnValueOutOfRange,
                            target="max_horizon",
                            max_horizon=str(max_horizon),
                            reference_code=ReferenceCodes._FORECASTING_HORIZON_INVALID_WITH_TIMECOLUMN_VALUES,
                            inner_exception=e
                        )
                    ) from e
                # Compare the expected dates with the real dates.
                missing_dates = sorted([str(val) for val in set(expected_dates).difference(set(tsds.time_index))])
                n_absent_in_cv = len(missing_dates)
                # Currently we have commented out the exceptions, because the check is strict.
                # In future we want to replace the exceptions by guard rails.
                if n_absent_in_cv == max_horizon:
                    missing_dates_str = ", ".join(missing_dates)
                    if grain_name is None:
                        exception_msg = (
                            "Missing timestamp(s) {} in data. "
                            "One of the validation folds will be empty "
                            "because the data at the end of time series are missing")
                        exception_msg = exception_msg.format(missing_dates_str)
                        # deEx = DataException(
                        #    exception_msg.format(missing_dates_str)).with_generic_msg(
                        #        exception_msg.format(MASKED))
                    else:
                        exception_msg = ("Missing timestamp(s) {} in data in series {}. "
                                         "One of the validation folds will be empty "
                                         "because the data at the end of time series are missing")
                        exception_msg = exception_msg.format(missing_dates_str, grain_name)
                        # deEx = DataException(
                        #    exception_msg.format(missing_dates_str, grain_name)).with_generic_msg(
                        #        exception_msg.format(MASKED, MASKED))
                    # raise deEx
                    # Warning is commented, because the warning text may be logged.
                    # warnings.warn(exception_msg)

    @staticmethod
    def _check_tsdf_frequencies(frequencies_grain_names: Dict[pd.DateOffset, List[GrainType]],
                                short_grains: Set[GrainType]) -> None:
        """
        Check if all series in the training set have only one frequency.

        :param frequencies_grain_names: The dictionary, containing frequencies and grain names.
        :param short_grains: The grains, which should not be used in this analysis as they
                             will be dropped.
        """
        # pd.DateOffset can not compare directly. need a start time.
        if len(frequencies_grain_names) == 0:
            return
        date_offsets = set()
        for k, v in frequencies_grain_names.items():
            if len(set(v) - short_grains) > 0:
                date_offsets.add(k)
        if len(date_offsets) > 1:
            raise ForecastingDataException._with_error(
                AzureMLError.create(TimeseriesDfMultiFrequenciesDiff, target='date_offsets',
                                    reference_code=ReferenceCodes._TSDF_MULTI_FREQUENCIES_DIFF)
            )

    @staticmethod
    def _check_tcn_min_points(
            tsds: Optional[TimeSeriesDataSet],
            number_of_data_points: int,
            automl_settings: AutoMLBaseSettings) -> None:
        """Check the minimal data points for a TCN tasks."""
        if not automl_settings.enable_dnn:
            return

        is_multi_grain = automl_settings.grain_column_names is not None
        if tsds is not None:
            is_multi_grain = False
            grain_column_names = automl_settings.grain_column_names
            if isinstance(grain_column_names, str):
                grain_column_names = [grain_column_names]
            # Check if the column is actually multy grain as even if the grain_column_names are set, we still
            # may have only one grain.
            if grain_column_names:
                for ts_id in grain_column_names:
                    if len(tsds.data.index.get_level_values(ts_id).unique()) > 1:
                        is_multi_grain = True
                        break
            # Do not do the validation if we have grain set and it is a single grain.
            # This means we are in the distributed mode as we remove grain columns during grain detection
            # in non distributed path.
            if automl_settings.has_multiple_series and not is_multi_grain:
                return

        tcn_minimal_points = TimeseriesDataFrameValidationWorker.TCN_MULTI_SERIES_MIN_POINTS if is_multi_grain \
            else TimeseriesDataFrameValidationWorker.TCN_SINGLE_SERIES_MIN_POINTS

        if number_of_data_points < tcn_minimal_points:
            only_tcn = automl_settings.whitelist_models is not None and len(automl_settings.whitelist_models) == 1 \
                and automl_settings.whitelist_models[0] == constants.SupportedModels.Forecasting.TCNForecaster
            if only_tcn:
                raise DataException._with_error(AzureMLError.create(
                    TimeseriesInsufficientDataForTCN, target="X",
                    single_minimal=TimeseriesDataFrameValidationWorker.TCN_SINGLE_SERIES_MIN_POINTS,
                    multi_minimal=TimeseriesDataFrameValidationWorker.TCN_MULTI_SERIES_MIN_POINTS,
                    n_samples=number_of_data_points, series_type="multi" if is_multi_grain else "single",
                    reference_code=ReferenceCodes._TCN_INSUFFICIENT_DATA)
                )
            else:
                logger.warning(
                    "Forecast TCN will not be enabled for the single series dataset with less than {} samples and "
                    "multi series with less than {} samples, "
                    "while traditional AutoML models will still be enabled.".format(
                        TimeseriesDataFrameValidationWorker.TCN_SINGLE_SERIES_MIN_POINTS,
                        TimeseriesDataFrameValidationWorker.TCN_MULTI_SERIES_MIN_POINTS
                    ))

    @staticmethod
    def _get_lags_safe(lags: Optional[Dict[str, List[Union[int, str]]]]) -> List[Union[int, str]]:
        """
        Get the lags value if any.

        :param lags: lags value from AutomlBaseSettings.
        :return: target lag or zero
        """
        return lags[constants.TimeSeriesInternal.DUMMY_TARGET_COLUMN] \
            if lags is not None else [0]

    @staticmethod
    def _get_window_safe(window_size: Optional[Union[int, str]]) -> Union[int, str]:
        """
        Get window size value if any.

        :param: window size from AutomlBaseSettings.
        """
        return window_size if window_size is not None else 0

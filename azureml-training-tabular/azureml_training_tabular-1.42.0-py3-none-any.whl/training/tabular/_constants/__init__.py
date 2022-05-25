# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from collections import OrderedDict

# Hashing seed value for murmurhash
hashing_seed_value = 314489979


class LanguageUnicodeRanges:
    """Class storing nons-spaced languages' unicode ranges. Chinese is an example of a non-spaced language."""

    nonspaced_language_unicode_ranges = [
        (0x4E00, 0x9FFF),
        (0x3400, 0x4DBF),  # Japanese and Chinese shared
        (0x300, 0x30FF),
        (0xFF00, 0xFFEF),  # Japanese
        (0x20000, 0x2A6DF),
        (0x2A700, 0x2B73F),  # Chinese
        (0x2B740, 0x2B81F),
        (0x2B820, 0x2CEAF),
        (0xF900, 0xFAFF),
        (0x2F800, 0x2FA1F),
        (0x1000, 0x109F),
        (0xAA60, 0xAA7F),
        (0xA9E0, 0xA9FF),  # Burmese
    ]


class NumericalDtype:
    """Defines supported numerical datatypes.

    Names correspond to the output of pandas.api.types.infer_dtype().
    """

    Integer = "integer"
    Floating = "floating"
    MixedIntegerFloat = "mixed-integer-float"
    Decimal = "decimal"
    Empty = "empty"

    FULL_SET = {Integer, Floating, MixedIntegerFloat, Decimal, Empty}
    CONVERTIBLE = {Integer, Floating, MixedIntegerFloat, Decimal}


class DatetimeDtype:
    """Defines supported datetime datatypes.

    Names correspond to the output of pandas.api.types.infer_dtype().
    """

    Date = "date"
    Datetime = "datetime"
    Datetime64 = "datetime64"

    FULL_SET = {Date, Datetime, Datetime64}


class TextOrCategoricalDtype:
    """Defines supported categorical datatypes."""

    String = "string"
    Categorical = "categorical"

    FULL_SET = {String, Categorical}


class AggregationFunctions:
    """Define the aggregation functions for numeric columns."""

    SUM = "sum"
    MAX = "max"
    MIN = "min"
    MEAN = "mean"

    DATETIME = [MAX, MIN]
    ALL = [SUM, MAX, MIN, MEAN]


class Tasks:
    CLASSIFICATION = "classification"
    REGRESSION = "regression"


class TimeSeries:
    """Defines parameters used for timeseries."""

    AUTO = "auto"
    COUNTRY = "country"
    COUNTRY_OR_REGION = "country_or_region"
    COUNTRY_OR_REGION_FOR_HOLIDAYS = "country_or_region_for_holidays"
    CV_STEP_SIZE = "cv_step_size"
    DROP_COLUMN_NAMES = "drop_column_names"
    FEATURE_LAGS = "feature_lags"
    FORECASTING_PARAMETERS = "forecasting_parameters"
    FORECAST_HORIZON = "forecast_horizon"
    FREQUENCY = "freq"
    GRAIN_COLUMN_NAMES = "grain_column_names"

    GROUP_COLUMN = "group"
    GROUP_COLUMN_NAMES = "group_column_names"
    HOLIDAY_COUNTRY = "holiday_country"
    MAX_CORES_PER_ITERATION = "max_cores_per_iteration"
    ITERATION_TIMEOUT_MINUTES = "iteration_timeout_minutes"
    MAX_HORIZON = "max_horizon"
    SEASONALITY = "seasonality"
    SERIES_COLUMN_COUNT = "series_column_count"
    SERIES_COUNT = "series_count"
    SERIES_LEN_AVG = "series_len_avg"
    SERIES_LEN_MIN = "series_len_min"
    SERIES_LEN_MAX = "series_len_max"
    SERIES_LEN_PERC_25 = "series_len_perc_25"
    SERIES_LEN_PERC_50 = "series_len_perc_50"
    SERIES_LEN_PERC_75 = "series_len_perc_75"
    SHORT_SERIES_HANDLING = "short_series_handling"
    SHORT_SERIES_HANDLING_CONFIG = "short_series_handling_configuration"
    STL_OPTION_SEASON = "season"
    STL_OPTION_SEASON_TREND = "season_trend"
    TARGET_LAGS = "target_lags"
    TARGET_ROLLING_WINDOW_SIZE = "target_rolling_window_size"
    TIME_COLUMN_NAME = "time_column_name"
    TIME_SERIES_ID_COLUMN_NAMES = "time_series_id_column_names"
    USE_STL = "use_stl"
    TARGET_AGG_FUN = "target_aggregation_function"
    ALL_FORECASTING_PARAMETERS = {
        TIME_COLUMN_NAME,
        GRAIN_COLUMN_NAMES,
        TIME_SERIES_ID_COLUMN_NAMES,
        GROUP_COLUMN_NAMES,
        TARGET_LAGS,
        FEATURE_LAGS,
        TARGET_ROLLING_WINDOW_SIZE,
        MAX_HORIZON,
        FORECAST_HORIZON,
        COUNTRY_OR_REGION,
        HOLIDAY_COUNTRY,
        SEASONALITY,
        USE_STL,
        SHORT_SERIES_HANDLING,
        DROP_COLUMN_NAMES,
        COUNTRY,
        FREQUENCY,
        COUNTRY_OR_REGION_FOR_HOLIDAYS,
        SHORT_SERIES_HANDLING_CONFIG,
        CV_STEP_SIZE,
    }


class ShortSeriesHandlingValues:
    """Define the possible values of ShortSeriesHandling config."""

    SHORT_SERIES_HANDLING_AUTO = TimeSeries.AUTO
    SHORT_SERIES_HANDLING_PAD = "pad"
    SHORT_SERIES_HANDLING_DROP = "drop"

    ALL = [SHORT_SERIES_HANDLING_AUTO, SHORT_SERIES_HANDLING_PAD, SHORT_SERIES_HANDLING_DROP]


class TimeSeriesInternal:
    """Defines non user-facing TimeSeries constants."""

    ARIMA_TRIGGER_CSS_TRAINING_LENGTH = 101
    ARIMAX_RAW_COLUMNS = "arimax_raw_columns"
    CROSS_VALIDATIONS = "n_cross_validations"
    CV_STEP_SIZE_DEFAULT = None
    DROP_IRRELEVANT_COLUMNS = "drop_irrelevant_columns"
    DROP_NA = "dropna"  # dropna parameter of LagLeadOperator and RollingWindow. Currently set to DROP_NA_DEFAULT.
    DROP_NA_DEFAULT = False
    DUMMY_GRAIN_COLUMN = "_automl_dummy_grain_col"
    MAX_TIME_SERIES_ID_COLUMN_NUMBER = 10
    DUMMY_GROUP_COLUMN = "_automl_dummy_group_col"
    DUMMY_ORDER_COLUMN = "_automl_original_order_col"
    DUMMY_PREDICT_COLUMN = "_automl_predict_col"
    DUMMY_TARGET_COLUMN = "_automl_target_col"
    FEATURE_LAGS_DEFAULT = None
    FORCE_TIME_INDEX_FEATURES_DEFAULT = None
    FORCE_TIME_INDEX_FEATURES_NAME = "force_time_index_features"
    FREQUENCY_DEFAULT = None
    GRANGER_CRITICAL_PVAL = 0.05
    GRANGER_DEFAULT_TEST = "ssr_ftest"
    # The column name reserved for holiday feature
    HOLIDAY_COLUMN_NAME = "_automl_Holiday"
    HOLIDAY_COLUMN_NAME_DEPRECATED = "_Holiday"
    HORIZON_NAME = "horizon_origin"
    IMPUTE_NA_NUMERIC_DATETIME = "impute_na_numeric_datetime"
    LAGGING_COLUMNS = "lagging_columns"  # The features generated from LAG_LEAD_OPERATOR
    LAGS_TO_CONSTRUCT = "lags"  # The internal lags dictionary
    LAG_LEAD_OPERATOR = "lag_lead_operator"
    MAKE_CATEGORICALS_NUMERIC = "make_categoricals_numeric"
    MAKE_CATEGORICALS_ONEHOT = "make_categoricals_onehot"
    MAKE_DATETIME_COLUMN_FEATURES = "make_datetime_column_features"
    MAKE_GRAIN_FEATURES = "make_grain_features"
    MAKE_NUMERIC_NA_DUMMIES = "make_numeric_na_dummies"
    MAKE_SEASONALITY_AND_TREND = "make_seasonality_and_trend"
    MAKE_TIME_INDEX_FEATURES = "make_time_index_featuers"
    MAX_HORIZON_DEFAULT = 1
    MAX_HORIZON_FEATURIZER = "max_horizon_featurizer"
    # The amount of memory occupied by perspective data frame
    # at which we decide to switch off lag leads and rolling windows.
    MEMORY_FRACTION_FOR_DF = 0.7
    ORIGIN_TIME_COLNAME = "origin_time_column_name"
    ORIGIN_TIME_COLNAME_DEFAULT = "origin"
    ORIGIN_TIME_COLUMN_NAME = "origin_time_colname"
    ORIGIN_TIME_OCCURRENCE_COLUMN_NAME = "_automl_origin_by_occurrence"
    # overwrite_columns parameter of LagLeadOperator and RollingWindow. Currently set to OVERWRITE_COLUMNS_DEFAULT.
    OVERWRITE_COLUMNS = "overwrite_columns"
    OVERWRITE_COLUMNS_DEFAULT = True
    PAID_TIMEOFF_COLUMN_NAME = "_automl_IsPaidTimeOff"
    PAID_TIMEOFF_COLUMN_NAME_DEPRECATED = "_IsPaidTimeOff"
    PERTURBATION_NOISE_CV = 1e-6
    PREFIX_FOR_GRAIN_FEATURIZATION = "grain"
    PREFIX_SEPERATOR_FOR_GRAIN_FEATURIZATION = "_"
    PROPHET_PARAM_DICT = "prophet_param_dict"
    RESTORE_DTYPES = "restore_dtypes_transform"
    ROLLING_WINDOW_OPERATOR = "rolling_window_operator"
    ROW_IMPUTED_COLUMN_NAME = "_automl_row_imputed"
    RUN_MAX_HORIZON = "forecasting_max_horizon"
    RUN_TARGET_LAGS = "forecasting_target_lags"
    RUN_WINDOW_SIZE = "forecasting_target_rolling_window_size"
    RUN_FREQUENCY = "forecasting_freq"
    ROLLING_WINDOW_COLUMNS = "rolling_window_columns"  # The features generated from ROLLING_WINDOW_OPERATOR.
    SEASONALITY_VALUE_DETECT = TimeSeries.AUTO
    SEASONALITY_VALUE_DEFAULT = SEASONALITY_VALUE_DETECT
    SEASONALITY_VALUE_NONSEASONAL = 1
    SHORT_SERIES_DROPPEER = "grain_dropper"
    SHORT_SERIES_HANDLING_DEFAULT = True
    STL_SEASON_SUFFIX = "_season"
    STL_TREND_SUFFIX = "_trend"
    TARGET_LAGS_DEFAULT = None
    TIMESERIES_PARAM_DICT = "timeseries_param_dict"
    # The rolling window transform dictionary, currently not publicly available.
    TRANSFORM_DICT = "transform_dictionary"
    TRANSFORM_OPTS = "transform_options"  # The options for rolling window transform.
    USE_STL_DEFAULT = None
    WINDOW_OPTS = "window_options"  # The internal window options (Currently is not used).
    WINDOW_SIZE = "window_size"  # The internal window_size variable
    WINDOW_SIZE_DEFDAULT = None
    WINDOW_SIZE_DEFAULT = WINDOW_SIZE_DEFDAULT

    RESERVED_COLUMN_NAMES = {DUMMY_GROUP_COLUMN, DUMMY_ORDER_COLUMN, DUMMY_GRAIN_COLUMN, DUMMY_TARGET_COLUMN}
    STL_VALID_OPTIONS = {TimeSeries.STL_OPTION_SEASON_TREND, TimeSeries.STL_OPTION_SEASON}
    TRANSFORM_DICT_DEFAULT = {"min": DUMMY_TARGET_COLUMN, "max": DUMMY_TARGET_COLUMN, "mean": DUMMY_TARGET_COLUMN}
    SHORT_SERIES_HANDLING_CONFIG_DEFAULT = ShortSeriesHandlingValues.SHORT_SERIES_HANDLING_AUTO

    # Features derived from the time index
    TIME_INDEX_FEATURE_ID_YEAR = 0
    TIME_INDEX_FEATURE_ID_YEAR_ISO = 1
    TIME_INDEX_FEATURE_ID_HALF = 2
    TIME_INDEX_FEATURE_ID_QUARTER = 3
    TIME_INDEX_FEATURE_ID_MONTH = 4
    TIME_INDEX_FEATURE_ID_MONTH_LBL = 5
    TIME_INDEX_FEATURE_ID_DAY = 6
    TIME_INDEX_FEATURE_ID_HOUR = 7
    TIME_INDEX_FEATURE_ID_MINUTE = 8
    TIME_INDEX_FEATURE_ID_SECOND = 9
    TIME_INDEX_FEATURE_ID_AM_PM = 10
    TIME_INDEX_FEATURE_ID_AM_PM_LBL = 11
    TIME_INDEX_FEATURE_ID_HOUR12 = 12
    TIME_INDEX_FEATURE_ID_WDAY = 13
    TIME_INDEX_FEATURE_ID_WDAY_LBL = 14
    TIME_INDEX_FEATURE_ID_QDAY = 15
    TIME_INDEX_FEATURE_ID_YDAY = 16
    TIME_INDEX_FEATURE_ID_WEEK = 17

    TIME_INDEX_FEATURE_IDS = [
        TIME_INDEX_FEATURE_ID_YEAR,
        TIME_INDEX_FEATURE_ID_YEAR_ISO,
        TIME_INDEX_FEATURE_ID_HALF,
        TIME_INDEX_FEATURE_ID_QUARTER,
        TIME_INDEX_FEATURE_ID_MONTH,
        TIME_INDEX_FEATURE_ID_MONTH_LBL,
        TIME_INDEX_FEATURE_ID_DAY,
        TIME_INDEX_FEATURE_ID_HOUR,
        TIME_INDEX_FEATURE_ID_MINUTE,
        TIME_INDEX_FEATURE_ID_SECOND,
        TIME_INDEX_FEATURE_ID_AM_PM,
        TIME_INDEX_FEATURE_ID_AM_PM_LBL,
        TIME_INDEX_FEATURE_ID_HOUR12,
        TIME_INDEX_FEATURE_ID_WDAY,
        TIME_INDEX_FEATURE_ID_WDAY_LBL,
        TIME_INDEX_FEATURE_ID_QDAY,
        TIME_INDEX_FEATURE_ID_YDAY,
        TIME_INDEX_FEATURE_ID_WEEK,
    ]

    TIME_INDEX_FEATURE_NAMES_DEPRECATED = [
        "year",
        "year_iso",
        "half",
        "quarter",
        "month",
        "month_lbl",
        "day",
        "hour",
        "minute",
        "second",
        "am_pm",
        "am_pm_lbl",
        "hour12",
        "wday",
        "wday_lbl",
        "qday",
        "yday",
        "week",
    ]
    TIME_INDEX_FEATURE_NAMES = [
        "_automl_year",
        "_automl_year_iso",
        "_automl_half",
        "_automl_quarter",
        "_automl_month",
        "_automl_month_lbl",
        "_automl_day",
        "_automl_hour",
        "_automl_minute",
        "_automl_second",
        "_automl_am_pm",
        "_automl_am_pm_lbl",
        "_automl_hour12",
        "_automl_wday",
        "_automl_wday_lbl",
        "_automl_qday",
        "_automl_yday",
        "_automl_week",
    ]
    TIME_INDEX_FEATURE_NAME_MAP_DEPRECATED = OrderedDict(
        zip(TIME_INDEX_FEATURE_IDS, TIME_INDEX_FEATURE_NAMES_DEPRECATED)
    )
    TIME_INDEX_FEATURE_NAME_MAP = OrderedDict(zip(TIME_INDEX_FEATURE_IDS, TIME_INDEX_FEATURE_NAMES))
    TARGET_AGG_FUN_DEFAULT = None
    USER_FRIENDLY_DEFAULT_GRAIN = "default"
    FORECASTER_ESTIMATOR_TYPE = "regressor"


class TimeSeriesWebLinks:
    """Define the web links for the time series documentation."""

    PANDAS_DO_URL = "https://pandas.pydata.org/pandas-docs/stable/timeseries.html#dateoffset-objects"
    FORECAST_PARAM_DOCS = (
        "https://docs.microsoft.com/en-us/python/api/azureml-automl-core/"
        "azureml.automl.core.forecasting_parameters.forecastingparameters"
        "?view=azure-ml-py"
    )
    FORECAST_CONFIG_DOC = (
        "https://docs.microsoft.com/azure/machine-learning/" "how-to-auto-train-forecast#configuration-settings"
    )


class TrainingResultsType:
    """Defines potential results from runners class."""

    # Metrics
    TRAIN_METRICS = "train"
    VALIDATION_METRICS = "validation"
    TEST_METRICS = "test"
    TRAIN_FROM_FULL_METRICS = "train from full"
    TEST_FROM_FULL_METRICS = "test from full"
    CV_METRICS = "CV"
    CV_MEAN_METRICS = "CV mean"

    # Other useful things
    TRAIN_TIME = "train time"
    FIT_TIME = "fit_time"
    PREDICT_TIME = "predict_time"
    BLOB_TIME = "blob_time"
    ALL_TIME = {TRAIN_TIME, FIT_TIME, PREDICT_TIME}
    TRAIN_PERCENT = "train_percent"
    MODELS = "models"

    # Status:
    TRAIN_VALIDATE_STATUS = "train validate status"
    TRAIN_FULL_STATUS = "train full status"
    CV_STATUS = "CV status"


class MetricExtrasConstants:
    """Defines internal values of Confidence Intervals"""

    UPPER_95_PERCENTILE = "upper_ci_95"
    LOWER_95_PERCENTILE = "lower_ci_95"
    VALUE = "value"

    # Confidence Interval metric name format
    MetricExtrasFormat = "{}_extras"


class Metric:
    """Defines all metrics supported by classification and regression."""

    # Classification
    AUCBinary = "AUC_binary"
    AUCMacro = "AUC_macro"
    AUCMicro = "AUC_micro"
    AUCWeighted = "AUC_weighted"
    Accuracy = "accuracy"
    WeightedAccuracy = "weighted_accuracy"
    BalancedAccuracy = "balanced_accuracy"
    NormMacroRecall = "norm_macro_recall"
    LogLoss = "log_loss"
    F1Binary = "f1_score_binary"
    F1Micro = "f1_score_micro"
    F1Macro = "f1_score_macro"
    F1Weighted = "f1_score_weighted"
    PrecisionBinary = "precision_score_binary"
    PrecisionMicro = "precision_score_micro"
    PrecisionMacro = "precision_score_macro"
    PrecisionWeighted = "precision_score_weighted"
    RecallBinary = "recall_score_binary"
    RecallMicro = "recall_score_micro"
    RecallMacro = "recall_score_macro"
    RecallWeighted = "recall_score_weighted"
    AvgPrecisionBinary = "average_precision_score_binary"
    AvgPrecisionMicro = "average_precision_score_micro"
    AvgPrecisionMacro = "average_precision_score_macro"
    AvgPrecisionWeighted = "average_precision_score_weighted"
    AccuracyTable = "accuracy_table"
    ConfusionMatrix = "confusion_matrix"
    MatthewsCorrelation = "matthews_correlation"

    # Regression
    ExplainedVariance = "explained_variance"
    R2Score = "r2_score"
    Spearman = "spearman_correlation"
    MAPE = "mean_absolute_percentage_error"
    SMAPE = "symmetric_mean_absolute_percentage_error"
    MeanAbsError = "mean_absolute_error"
    MedianAbsError = "median_absolute_error"
    RMSE = "root_mean_squared_error"
    RMSLE = "root_mean_squared_log_error"
    NormMeanAbsError = "normalized_mean_absolute_error"
    NormMedianAbsError = "normalized_median_absolute_error"
    NormRMSE = "normalized_root_mean_squared_error"
    NormRMSLE = "normalized_root_mean_squared_log_error"
    Residuals = "residuals"
    PredictedTrue = "predicted_true"

    # Forecast
    ForecastMAPE = "forecast_mean_absolute_percentage_error"
    ForecastSMAPE = "forecast_symmetric_mean_absolute_percentage_error"
    ForecastResiduals = "forecast_residuals"
    ForecastTable = 'forecast_table'

    # Image Multi Label Classification
    IOU = "iou"  # Intersection Over Union

    # Image Object Detection
    MeanAveragePrecision = "mean_average_precision"

    SCALAR_CLASSIFICATION_SET = {
        AUCBinary,
        AUCMacro,
        AUCMicro,
        AUCWeighted,
        Accuracy,
        WeightedAccuracy,
        NormMacroRecall,
        BalancedAccuracy,
        LogLoss,
        F1Binary,
        F1Micro,
        F1Macro,
        F1Weighted,
        PrecisionBinary,
        PrecisionMicro,
        PrecisionMacro,
        PrecisionWeighted,
        RecallBinary,
        RecallMicro,
        RecallMacro,
        RecallWeighted,
        AvgPrecisionBinary,
        AvgPrecisionMicro,
        AvgPrecisionMacro,
        AvgPrecisionWeighted,
        MatthewsCorrelation,
    }

    NONSCALAR_CLASSIFICATION_SET = {AccuracyTable, ConfusionMatrix}

    CLASSIFICATION_BINARY_SET = {AUCBinary, F1Binary, PrecisionBinary, RecallBinary, AvgPrecisionBinary}

    CLASSIFICATION_SET = SCALAR_CLASSIFICATION_SET | NONSCALAR_CLASSIFICATION_SET

    SCALAR_REGRESSION_SET = {
        ExplainedVariance,
        R2Score,
        Spearman,
        MAPE,
        MeanAbsError,
        MedianAbsError,
        RMSE,
        RMSLE,
        NormMeanAbsError,
        NormMedianAbsError,
        NormRMSE,
        NormRMSLE,
    }

    NONSCALAR_REGRESSION_SET = {Residuals, PredictedTrue}

    REGRESSION_SET = SCALAR_REGRESSION_SET | NONSCALAR_REGRESSION_SET

    NONSCALAR_FORECAST_SET = {ForecastMAPE, ForecastResiduals, ForecastTable}

    FORECAST_SET = NONSCALAR_FORECAST_SET

    CLASSIFICATION_PRIMARY_SET = {Accuracy, AUCWeighted, NormMacroRecall, AvgPrecisionWeighted, PrecisionWeighted}

    CLASSIFICATION_BALANCED_SET = {
        # this is for metrics where we would recommend using class_weights
        BalancedAccuracy,
        AUCMacro,
        NormMacroRecall,
        AvgPrecisionMacro,
        PrecisionMacro,
        F1Macro,
        RecallMacro,
    }

    REGRESSION_PRIMARY_SET = {Spearman, NormRMSE, R2Score, NormMeanAbsError}

    IMAGE_CLASSIFICATION_PRIMARY_SET = {Accuracy}

    IMAGE_CLASSIFICATION_MULTILABEL_PRIMARY_SET = {IOU}

    IMAGE_OBJECT_DETECTION_PRIMARY_SET = {
        MeanAveragePrecision,
    }

    IMAGE_OBJECT_DETECTION_SET = {
        MeanAveragePrecision,
    }

    SAMPLE_WEIGHTS_UNSUPPORTED_SET = {WeightedAccuracy, Spearman, MedianAbsError, NormMedianAbsError}

    TEXT_CLASSIFICATION_PRIMARY_SET = {Accuracy, AUCWeighted, PrecisionWeighted}

    TEXT_CLASSIFICATION_MULTILABEL_PRIMARY_SET = {Accuracy}

    TEXT_NER_PRIMARY_SET = {Accuracy}

    FULL_SET = CLASSIFICATION_SET | REGRESSION_SET | FORECAST_SET | IMAGE_OBJECT_DETECTION_SET
    NONSCALAR_FULL_SET = NONSCALAR_CLASSIFICATION_SET | NONSCALAR_REGRESSION_SET | NONSCALAR_FORECAST_SET
    SCALAR_FULL_SET = SCALAR_CLASSIFICATION_SET | SCALAR_REGRESSION_SET
    SCALAR_FULL_SET_TIME = SCALAR_FULL_SET | TrainingResultsType.ALL_TIME

    # TODO: These types will be removed when the artifact-backed
    # metrics are defined with protobuf
    # Do not use these constants except in artifact-backed metrics
    SCHEMA_TYPE_ACCURACY_TABLE = "accuracy_table"
    SCHEMA_TYPE_CONFUSION_MATRIX = "confusion_matrix"
    SCHEMA_TYPE_RESIDUALS = "residuals"
    SCHEMA_TYPE_PREDICTIONS = "predictions"
    SCHEMA_TYPE_MAPE = "mape_table"
    SCHEMA_TYPE_SMAPE = "smape_table"

    @classmethod
    def pretty(cls, metric):
        """Verbose names for metrics."""
        return {
            cls.AUCBinary: "Binary Area Under The Curve",
            cls.AUCMacro: "Macro Area Under The Curve",
            cls.AUCMicro: "Micro Area Under The Curve",
            cls.AUCWeighted: "Weighted Area Under The Curve",
            cls.Accuracy: "Accuracy",
            cls.WeightedAccuracy: "Weighted Accuracy",
            cls.NormMacroRecall: "Normed Macro Recall",
            cls.BalancedAccuracy: "Balanced Accuracy",
            cls.LogLoss: "Log Loss",
            cls.F1Binary: "Binary F1 Score",
            cls.F1Macro: "Macro F1 Score",
            cls.F1Micro: "Micro F1 Score",
            cls.F1Weighted: "Weighted F1 Score",
            cls.PrecisionBinary: "Binary Precision",
            cls.PrecisionMacro: "Macro Precision",
            cls.PrecisionMicro: "Micro Precision",
            cls.PrecisionWeighted: "Weighted Precision",
            cls.RecallBinary: "Binary Recall",
            cls.RecallMacro: "Macro Recall",
            cls.RecallMicro: "Micro Recall",
            cls.RecallWeighted: "Weighted Recall",
            cls.AvgPrecisionBinary: "Binary Average Precision",
            cls.AvgPrecisionMacro: "Macro Average Precision",
            cls.AvgPrecisionMicro: "Micro Average Precision",
            cls.AvgPrecisionWeighted: "Weighted Average Precision",
            cls.ExplainedVariance: "Explained Variance",
            cls.R2Score: "R2 Score",
            cls.Spearman: "Spearman Correlation",
            cls.MeanAbsError: "Mean Absolute Error",
            cls.MedianAbsError: "Median Absolute Error",
            cls.RMSE: "Root Mean Squared Error",
            cls.RMSLE: "Root Mean Squared Log Error",
            cls.NormMeanAbsError: "Normalized Mean Absolute Error",
            cls.NormMedianAbsError: "Normalized Median Absolute Error",
            cls.NormRMSE: "Normalized Root Mean Squared Error",
            cls.NormRMSLE: "Normalized Root Mean Squared Log Error",
            cls.MeanAveragePrecision: "Mean Average Precision (mAP)",
        }[metric]

    CLIPS_POS = {
        # TODO: If we are no longer transforming by default reconsider these
        # it is probably not necessary for them to be over 1
        LogLoss: 1,
        NormMeanAbsError: 1,
        NormMedianAbsError: 1,
        NormRMSE: 1,
        NormRMSLE: 1,
        # current timeout value but there is a long time
        TrainingResultsType.TRAIN_TIME: 10 * 60 * 2,
    }

    CLIPS_NEG = {
        # TODO: If we are no longer transforming by default reconsider these
        # it is probably not necessary for them to be over 1
        # spearman is naturally limited to this range but necessary for transform_y to work
        # otherwise spearmen is getting clipped to 0 by default
        Spearman: -1,
        ExplainedVariance: -1,
        R2Score: -1,
    }


class FeatureType:
    """Defines names of feature types that are recognized for feature engineering in AutoML.

    In typical use cases, you use FeatureType attributes for customizing featuration with the
    :class:`azureml.train.automl.automlconfig.AutoMLConfig` class and the ``featurization`` parameter.

    .. remarks::

        FeatureType attributes are used when customizing featurization. For example, to update a
        column type, use the :class:`azureml.automl.core.featurization.featurizationconfig.FeaturizationConfig`
        class as shown in the example.

        .. code-block:: python

            featurization_config = FeaturizationConfig()
            featurization_config.add_column_purpose('column1', 'Numeric')
            featurization_config.add_column_purpose('column2', 'CategoricalHash')

        For more information, see `Configure automated ML experiments
        <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train>`_.
    """

    Numeric = "Numeric"
    DateTime = "DateTime"
    Categorical = "Categorical"
    CategoricalHash = "CategoricalHash"
    Text = "Text"
    Hashes = "Hashes"
    Ignore = "Ignore"
    AllNan = "AllNan"

    FULL_SET = {Numeric, DateTime, Categorical, CategoricalHash, Text, Hashes, Ignore, AllNan}

    # List of features types that are dropped and not featurized
    DROP_SET = {Hashes, Ignore, AllNan}


class PredictionTransformTypes:
    """Names for prediction transform types"""

    INTEGER = "Integer"

    FULL_SET = {INTEGER}


class TransformerParams:
    """Defines parameters used by all transformers in AutoML."""

    class Imputer:
        """Defines how missing values are determined in imputer transformers in AutoML.

        The following example shows customizing featurization with the
        :class:`azureml.automl.core.featurization.featurizationconfig.FeaturizationConfig` class
        and using one of the Imputer values.

        .. code-block:: python

            featurization_config = FeaturizationConfig()
            featurization_config.add_transformer_params('Imputer', ['columnName'], {"strategy": "median"})

        For more information, see `Configure automated ML experiments
        <https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-train>`_.
        """

        Strategy = "strategy"
        Constant = "constant"
        Mean = "mean"
        Median = "median"
        Mode = "most_frequent"
        Ffill = "ffill"
        FillValue = "fill_value"

        NumericalImputerStrategies = {Mean, Median}
        # Forecasting tasks specific parameters.
        ForecastingEnabledStrategies = {Mean, Median, Mode, Constant, Ffill}
        ForecastingTargetEnabledStrategies = {Constant, Ffill}

    class Nimbus:
        """Defines parameters used by nimbus in AutoML."""

        Mean = "Mean"
        Min = "Minimum"
        Max = "Maximum"
        DefaultValue = "DefaultValue"


class TextDNNLanguages:
    """Class storing supported text dnn languages."""

    default = "eng"
    cpu_supported = {"eng": "English"}
    supported = {
        "afr": "Afrikaans",
        "ara": "Arabic",
        "arg": "Aragonese",
        "ast": "Asturian",
        "azb": "South Azerbaijani",
        "aze": "Azerbaijani",
        "bak": "Bashkir",
        "bar": "Bavarian",
        "bel": "Belarusian",
        "ben": "Bengali",
        "bos": "Bosnian",
        "bpy": "Bishnupriya",
        "bre": "Breton",
        "bul": "Bulgarian",
        "cat": "Catalan",
        "ceb": "Cebuano",
        "ces": "Czech",
        "che": "Chechen",
        "chv": "Chuvash",
        "cym": "Welsh",
        "dan": "Danish",
        "deu": "German",
        "ell": "Greek",
        "eng": "English",
        "est": "Estonian",
        "eus": "Basque",
        "fas": "Persian",
        "fin": "Finnish",
        "fra": "French",
        "fry": "Western Frisian",
        "gle": "Irish",
        "glg": "Galician",
        "guj": "Gujarati",
        "hat": "Haitian",
        "hbs": "Serbo-Croatian",
        "heb": "Hebrew",
        "hin": "Hindi",
        "hrv": "Croatian",
        "hun": "Hungarian",
        "hye": "Armenian",
        "ido": "Ido",
        "ind": "Indonesian",
        "isl": "Icelandic",
        "ita": "Italian",
        "jav": "Javanese",
        "jpn": "Japanese",
        "kan": "Kannada",
        "kat": "Georgian",
        "kaz": "Kazakh",
        "kir": "Kirghiz",
        "kor": "Korean",
        "lah": "Western Punjabi",
        "lat": "Latin",
        "lav": "Latvian",
        "lit": "Lithuanian",
        "lmo": "Lombard",
        "ltz": "Luxembourgish",
        "mal": "Malayalam",
        "mar": "Marathi",
        "min": "Minangkabau",
        "mkd": "Macedonian",
        "mlg": "Malagasy",
        "mon": "Mongolian",
        "msa": "Malay",
        "mul": "Multilingual - collection of all supporting languages",
        "mya": "Burmese",
        "nds": "Low Saxon",
        "nep": "Nepali",
        "new": "Newar",
        "nld": "Dutch",
        "nno": "Norwegian Nynorsk",
        "nob": "Norwegian Bokmål",
        "oci": "Occitan",
        "pan": "Punjabi",
        "pms": "Piedmontese",
        "pol": "Polish",
        "por": "Portuguese",
        "ron": "Romanian",
        "rus": "Russian",
        "scn": "Sicilian",
        "sco": "Scots",
        "slk": "Slovak",
        "slv": "Slovenian",
        "spa": "Spanish",
        "sqi": "Albanian",
        "srp": "Serbian",
        "sun": "Sundanese",
        "swa": "Swahili",
        "swe": "Swedish",
        "tam": "Tamil",
        "tat": "Tatar",
        "tel": "Telugu",
        "tgk": "Tajik",
        "tgl": "Tagalog",
        "tha": "Thai",
        "tur": "Turkish",
        "ukr": "Ukrainian",
        "urd": "Urdu",
        "uzb": "Uzbek",
        "vie": "Vietnamese",
        "vol": "Volapük",
        "war": "Waray-Waray",
        "yor": "Yoruba",
        "zho": "Chinese",
    }

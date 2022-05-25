# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml._common._error_definition import error_decorator
from azureml._common._error_definition.error_definition import ErrorDefinition
from azureml._common._error_definition.system_error import ClientError
from azureml._common._error_definition.user_error import (
    ArgumentBlankOrEmpty,
    ArgumentInvalid,
    ArgumentMismatch,
    ArgumentOutOfRange,
    Authentication,
    BadArgument,
    BadData,
    Conflict,
    ConnectionFailure,
    EmptyData,
    InvalidDimension,
    MalformedArgument,
    Memory,
    MissingData,
    NotFound,
    NotReady,
    NotSupported,
    ResourceExhausted,
    Timeout,
    UserError,
)

from .error_strings import ErrorStrings


@error_decorator(use_parent_error_code=True)
class ARIMAXOLSFitException(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.ARIMAX_OLS_FIT_EXCEPTION


@error_decorator(use_parent_error_code=True)
class ARIMAXOLSLinAlgError(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.ARIMAX_OLS_LINALG_ERROR


# region UserError
class ExecutionFailure(UserError):
    """A generic error encountered during execution of an operation due to invalid user provided data/configuration."""

    @property
    def message_format(self) -> str:
        return ErrorStrings.EXECUTION_FAILURE


# endregion


# region ArgumentBlankOrEmpty
@error_decorator(use_parent_error_code=True)
class FeaturizationConfigEmptyFillValue(ArgumentBlankOrEmpty):
    @property
    def message_format(self) -> str:
        return ErrorStrings.FEATURIZATION_CONFIG_EMPTY_FILL_VALUE


@error_decorator(use_parent_error_code=True)
class ImageParameterSpaceEmpty(ArgumentBlankOrEmpty):
    @property
    def message_format(self) -> str:
        return ErrorStrings.IMAGE_PARAMETER_SPACE_EMPTY


class TargetAndExtractColumnsAreNone(ArgumentBlankOrEmpty):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DS_TGT_AND_COLUMNS_EMPTY


# endregion


# region ArgumentInvalid
@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/AutoMLConfig")
class InvalidArgumentType(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_ARGUMENT_TYPE


@error_decorator(use_parent_error_code=True)
class InvalidArgumentTypeWithCondition(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_ARGUMENT_TYPE_WITH_CONDITION


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/AutoMLConfig")
class InvalidArgumentWithSupportedValues(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_ARGUMENT_WITH_SUPPORTED_VALUES


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/AutoMLConfig")
class InvalidArgumentWithSupportedValuesForTask(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_ARGUMENT_WITH_SUPPORTED_VALUES_FOR_TASK


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/AutoMLConfig")
class InvalidArgumentForTask(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_ARGUMENT_FOR_TASK


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/AutoMLConfig")
class TensorflowAlgosAllowedButDisabled(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TENSORFLOW_ALGOS_ALLOWED_BUT_DISABLED


@error_decorator(use_parent_error_code=True)
class XGBoostAlgosAllowedButNotInstalled(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.XGBOOST_ALGOS_ALLOWED_BUT_NOT_INSTALLED


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/AutoMLConfig")
class InvalidCVSplits(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_CV_SPLITS


@error_decorator(details_uri="https://aka.ms/AutoMLConfig")
class InvalidInputDatatype(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_INPUT_DATATYPE


class InvalidInputDatatypeFeaturizatonConfig(InvalidInputDatatype):
    @property
    def message_format(self) -> str:
        return ErrorStrings.FEATURIZATION_CONFIG_INVALID_TYPE


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/AutoMLConfig")
class InputDataWithMixedType(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INPUT_DATA_WITH_MIXED_TYPE


@error_decorator(use_parent_error_code=True)
class InvalidParameterSelection(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_PARAMETER_SELECTION


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/AutoMLConfig")
class AllAlgorithmsAreBlocked(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.ALL_ALGORITHMS_ARE_BLOCKED


@error_decorator(details_uri="https://aka.ms/AutoMLConfig")
class InvalidComputeTargetForDatabricks(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_COMPUTE_TARGET_FOR_DATABRICKS


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/AutoMLConfig")
class EmptyLagsForColumns(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.EMPTY_LAGS_FOR_COLUMNS


@error_decorator(use_parent_error_code=True)
class TimeseriesInvalidDateOffsetType(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_INVALID_DATE_OFFSET_TYPE


class TimeseriesInvalidTimestamp(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_INVALID_TIMESTAMP


class TimeseriesDfColumnTypeNotSupported(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_COL_TYPE_NOT_SUPPORTED


class TimeseriesCannotDropSpecialColumn(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_CANNOT_DROP_SPECIAL_COL


@error_decorator(use_parent_error_code=True)
class TimeseriesDfInvalidArgParamIncompatible(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_INVALID_ARG_PARAM_INCOMPATIBLE


@error_decorator(use_parent_error_code=True)
class TimeseriesDfInvalidArgForecastHorizon(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_INVALID_ARG_FORECAST_HORIZON


@error_decorator(use_parent_error_code=True)
class TimeseriesDfInvalidArgOnlyOneArgRequired(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_INVALID_ARG_ONLY_ONE_ARG_REQUIRED


@error_decorator(use_parent_error_code=True)
class TimeseriesDfInvalidArgFcPipeYOnly(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_INVALID_ARG_FC_PIPE_Y_ONLY


@error_decorator(use_parent_error_code=True)
class TimeseriesDsFreqLessThenFcFreq(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_FREQUENCY_LESS_THEN_FC


@error_decorator(use_parent_error_code=True)
class TimeseriesAggNoFreq(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_AGG_WITHOUT_FREQ


@error_decorator(use_parent_error_code=True)
class OnnxNotEnabled(ArgumentInvalid):
    @property
    def message_format(self):
        return ErrorStrings.ONNX_NOT_ENABLED


@error_decorator(use_parent_error_code=True)
class OnnxSplitsNotEnabled(ArgumentInvalid):
    @property
    def message_format(self):
        return ErrorStrings.ONNX_SPLITS_NOT_ENABLED


@error_decorator(use_parent_error_code=True)
class OnnxUnsupportedDatatype(ArgumentInvalid):
    @property
    def message_format(self):
        return ErrorStrings.ONNX_UNSUPPORTED_DATATYPE


@error_decorator(details_uri="https://docs.microsoft.com/azure/machine-learning/how-to-configure-auto-features")
class FeaturizationRequired(ArgumentInvalid):
    @property
    def message_format(self):
        return ErrorStrings.FEATURIZATION_REQUIRED


class FeatureTypeUnsupported(ArgumentInvalid):
    @property
    def message_format(self):
        return ErrorStrings.FEATURE_TYPE_UNSUPPORTED


class TimeseriesTimeColNameOverlapIdColNames(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_TIME_COL_NAME_OVERLAP_ID_COL_NAMES


@error_decorator(use_parent_error_code=True)
class FeaturizationConfigInvalidFillValue(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.FEATURIZATION_CONFIG_WRONG_IMPUTATION_VALUE


@error_decorator(use_parent_error_code=True)
class ImageDuplicateParameters(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.IMAGE_DUPLICATE_PARAMETERS


@error_decorator(use_parent_error_code=True)
class ImageOddNumArguments(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.IMAGE_ODD_NUM_ARGUMENTS


# endregion


# region ArgumentMismatch
@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/AutoMLConfig")
class AllowedModelsSubsetOfBlockedModels(ArgumentMismatch):
    @property
    def message_format(self) -> str:
        return ErrorStrings.ALLOWED_MODELS_SUBSET_OF_BLOCKED_MODELS


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/AutoMLConfig")
class AllowedModelsNonExplainable(ArgumentMismatch):
    @property
    def message_format(self) -> str:
        return ErrorStrings.ALLOWED_MODELS_NON_EXPLAINABLE


@error_decorator(details_uri="https://aka.ms/AutoMLConfig")
class ConflictingValueForArguments(ArgumentMismatch):
    @property
    def message_format(self) -> str:
        return ErrorStrings.CONFLICTING_VALUE_FOR_ARGUMENTS


@error_decorator(use_parent_error_code=True)
class InvalidDampingSettings(ConflictingValueForArguments):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_DAMPING_SETTINGS


@error_decorator(use_parent_error_code=True)
class ConflictingFeaturizationConfigDroppedColumns(ConflictingValueForArguments):
    @property
    def message_format(self) -> str:
        return ErrorStrings.CONFLICTING_FEATURIZATION_CONFIG_DROPPED_COLUMNS


@error_decorator(use_parent_error_code=True)
class ConflictingFeaturizationConfigReservedColumns(ConflictingValueForArguments):
    @property
    def message_format(self) -> str:
        return ErrorStrings.CONFLICTING_FEATURIZATION_CONFIG_RESERVED_COLUMNS


class ConflictingTimeoutError(ConflictingValueForArguments):
    @property
    def message_format(self) -> str:
        return ErrorStrings.CONFLICTING_TIMEOUT_IN_ARGUMENTS


# endregion

# region BadArgument
@error_decorator(use_parent_error_code=True)
class InaccessibleDataStore(BadArgument):
    @property
    def message_format(self) -> str:
        return ErrorStrings.DATA_AUTH_BAD


@error_decorator(use_parent_error_code=True)
class OtherDataStoreException(BadArgument):
    @property
    def message_format(self) -> str:
        return ErrorStrings.DATA_OTHER_NON_AUTH_ERROR


@error_decorator(details_uri="https://aka.ms/AutoMLConfig")
class InvalidFeaturizer(BadArgument):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_FEATURIZER


@error_decorator(use_parent_error_code=True)
class InvalidSTLFeaturizerForMultiplicativeModel(InvalidFeaturizer):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_STL_FEATURIZER_FOR_MULTIPLICATIVE_MODEL


@error_decorator(use_parent_error_code=True)
class GrainColumnsAndGrainNameMismatch(BadArgument):
    @property
    def message_format(self) -> str:
        return ErrorStrings.GRAIN_COLUMNS_AND_GRAIN_NAME_MISMATCH


class FeaturizationConfigParamOverridden(BadArgument):
    @property
    def message_format(self) -> str:
        return ErrorStrings.FEATURIZATION_CONFIG_PARAM_OVERRIDDEN


@error_decorator(use_parent_error_code=True)
class FeaturizationConfigMultipleImputers(BadArgument):
    @property
    def message_format(self) -> str:
        return ErrorStrings.FEATURIZATION_CONFIG_MULTIPLE_IMPUTERS


class MissingColumnsInData(BadArgument):
    @property
    def message_format(self) -> str:
        return ErrorStrings.MISSING_COLUMNS_IN_DATA


class ArimaxEmptyDataFrame(BadArgument):
    @property
    def message_format(self) -> str:
        return ErrorStrings.ARIMAX_EMPTY_DATA_FRAME


class ArimaBadMaxHorizon(BadArgument):
    @property
    def message_format(self) -> str:
        return ErrorStrings.ARIMA_BAD_MAX_HORIZON


@error_decorator(use_parent_error_code=True)
class NonOverlappingColumnsInTrainValid(MissingColumnsInData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.NON_OVERLAPPING_COLUMNS_IN_TRAIN_VALID


@error_decorator(use_parent_error_code=True)
class FeaturizationConfigColumnMissing(MissingColumnsInData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.FEATURIZATION_CONFIG_COLUMN_MISSING


# endregion


# region ArgumentOutOfRange
@error_decorator(use_parent_error_code=True)
class NCrossValidationsExceedsTrainingRows(ArgumentOutOfRange):
    @property
    def message_format(self) -> str:
        return ErrorStrings.N_CROSS_VALIDATIONS_EXCEEDS_TRAINING_ROWS


@error_decorator(use_parent_error_code=True)
class ExperimentTimeoutForDataSize(ArgumentOutOfRange):
    @property
    def message_format(self) -> str:
        return ErrorStrings.EXPERIMENT_TIMEOUT_FOR_DATA_SIZE


@error_decorator(use_parent_error_code=True)
class QuantileRange(ArgumentOutOfRange):
    @property
    def message_format(self) -> str:
        return ErrorStrings.QUANTILE_RANGE


@error_decorator(use_parent_error_code=True)
class DateOutOfRangeDuringPadding(ArgumentOutOfRange):
    @property
    def message_format(self):
        return ErrorStrings.DATE_OUT_OF_RANGE_DURING_PADDING


@error_decorator(use_parent_error_code=True)
class DateOutOfRangeDuringPaddingGrain(ArgumentOutOfRange):
    @property
    def message_format(self):
        return ErrorStrings.DATE_OUT_OF_RANGE_DURING_PADDING_GRAIN


class CorrelationCutoffOutOfRange(ArgumentOutOfRange):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_TIME_FT_BAD_CORRELATION_CUTOFF


class InvalidMetricSpecified(ArgumentOutOfRange):
    @property
    def message_format(self):
        return ErrorStrings.INVALID_METRIC_SPECIFIED


# endregion


# region MalformedArgument
class MalformedJsonString(MalformedArgument):
    @property
    def message_format(self):
        return ErrorStrings.MALFORMED_JSON_STRING


# endregion


# region NotReady
class ComputeNotReady(NotReady):
    @property
    def message_format(self) -> str:
        return ErrorStrings.COMPUTE_NOT_READY


# endregion


# region NotFound
class MethodNotFound(NotFound):
    @property
    def message_format(self) -> str:
        return ErrorStrings.METHOD_NOT_FOUND


class DatastoreNotFound(NotFound):
    @property
    def message_format(self) -> str:
        return ErrorStrings.DATASTORE_NOT_FOUND


class DataPathNotFound(NotFound):
    @property
    def message_format(self):
        return ErrorStrings.DATA_PATH_NOT_FOUND


class MissingSecrets(NotFound):
    @property
    def message_format(self):
        return ErrorStrings.MISSING_SECRETS


@error_decorator(
    details_uri="https://docs.microsoft.com/azure/machine-learning/"
    "how-to-configure-auto-train#train-and-validation-data"
)
class MissingValidationConfig(NotFound):
    @property
    def message_format(self):
        return ErrorStrings.MISSING_VALIDATION_CONFIG


@error_decorator(use_parent_error_code=True)
class TimeseriesDfInvalidArgNoValidationData(MissingValidationConfig):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_INVALID_ARG_NO_VALIDATION


@error_decorator(use_parent_error_code=True)
class NoMetricsData(NotFound):
    @property
    def message_format(self):
        return ErrorStrings.NO_METRICS_DATA


@error_decorator(use_parent_error_code=True)
class InvalidIteration(NotFound):
    @property
    def message_format(self):
        return ErrorStrings.INVALID_ITERATION


class ModelMissing(NotFound):
    @property
    def message_format(self):
        return ErrorStrings.MODEL_MISSING


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/AutoMLConfig")
class DataScriptNotFound(NotFound):
    @property
    def message_format(self):
        return ErrorStrings.DATA_SCRIPT_NOT_FOUND


# endregion


# region NotSupported
@error_decorator(use_parent_error_code=True)
class CredentiallessDatastoreNotSupported(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.CREDENTIALLESS_DATASTORE_NOT_SUPPORTED


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/AutoMLConfig")
class LargeDataAlgorithmsWithUnsupportedArguments(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.LARGE_DATA_ALGORITHMS_WITH_UNSUPPORTED_ARGUMENTS


@error_decorator(use_parent_error_code=True)
class ForecastFitNotSupported(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.FORECAST_FIT_NOT_SUPPORT


@error_decorator(use_parent_error_code=True)
class ForecastPredictNotSupported(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.FORECAST_PREDICT_NOT_SUPPORT


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/AutoMLConfig")
class FeatureUnsupportedForIncompatibleArguments(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.FEATURE_UNSUPPORTED_FOR_INCOMPATIBLE_ARGUMENTS


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/AutoMLConfig")
class NonDnnTextFeaturizationUnsupported(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.NON_DNN_TEXT_FEATURIZATION_UNSUPPORTED


class InvalidOperationOnRunState(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_OPERATION_ON_RUN_STATE


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/AutoMLConfig")
class FeaturizationConfigForecastingStrategy(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.FEATURIZATION_CONFIG_FORECASTING_STRATEGY


class RemoteInferenceUnsupported(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.REMOTE_INFERENCE_UNSUPPORTED


class LocalInferenceUnsupported(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.LOCAL_INFERENCE_UNSUPPORTED


class IncompatibleDependency(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INCOMPATIBLE_DEPENDENCY


class IncompatibleOrMissingDependency(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INCOMPATIBLE_OR_MISSING_DEPENDENCY


@error_decorator(
    use_parent_error_code=True,
    details_uri="https://docs.microsoft.com/azure/machine-learning/"
    "how-to-configure-environment?#sdk-for-databricks-with-automated-machine-learning",
)
class IncompatibleOrMissingDependencyDatabricks(IncompatibleOrMissingDependency):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INCOMPATIBLE_OR_MISSING_DEPENDENCY_DATABRICKS


@error_decorator(use_parent_error_code=True)
class RuntimeModuleDependencyMissing(IncompatibleOrMissingDependency):
    @property
    def message_format(self) -> str:
        return ErrorStrings.RUNTIME_MODULE_DEPENDENCY_MISSING


@error_decorator(use_parent_error_code=True)
class DependencyWrongVersion(IncompatibleOrMissingDependency):
    @property
    def message_format(self) -> str:
        return ErrorStrings.DEPENDENCY_WRONG_VERSION


@error_decorator(use_parent_error_code=True)
class LoadModelDependencyMissing(IncompatibleOrMissingDependency):
    @property
    def message_format(self) -> str:
        return ErrorStrings.LOAD_MODEL_DEPENDENCY_MISSING


@error_decorator(use_parent_error_code=True)
class ExplainabilityPackageMissing(IncompatibleOrMissingDependency):
    @property
    def message_format(self) -> str:
        return ErrorStrings.EXPLAINABILITY_PACKAGE_MISSING


@error_decorator(use_parent_error_code=False, details_uri="https://aka.ms/aml-largefiles")
class SnapshotLimitExceeded(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.SNAPSHOT_LIMIT_EXCEED


@error_decorator(use_parent_error_code=True)
class ContinueRunUnsupportedForAdb(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.CONTINUE_RUN_UNSUPPORTED_FOR_ADB


@error_decorator(use_parent_error_code=True)
class ContinueRunUnsupportedForImageRuns(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.CONTINUE_RUN_UNSUPPORTED_FOR_IMAGE_RUNS


@error_decorator(use_parent_error_code=True)
class ContinueRunUnsupportedForUntrackedRuns(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.CONTINUE_RUN_UNSUPPORTED_FOR_UNTRACKED_RUNS


@error_decorator(use_parent_error_code=True)
class CancelUnsupportedForLocalRuns(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.CANCEL_UNSUPPORTED_FOR_LOCAL_RUNS


@error_decorator(use_parent_error_code=True)
class SampleWeightsUnsupported(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.SAMPLE_WEIGHTS_UNSUPPORTED


@error_decorator(use_parent_error_code=True)
class ModelExplanationsUnsupportedForAlgorithm(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.MODEL_EXPLANATIONS_UNSUPPORTED_FOR_ALGORITHM


class ModelNotSupported(NotSupported):
    @property
    def message_format(self):
        return ErrorStrings.MODEL_NOT_SUPPORTED


# endregion


# region MissingData
class InsufficientSampleSize(MissingData):
    @property
    def message_format(self):
        return ErrorStrings.INSUFFICIENT_SAMPLE_SIZE


@error_decorator(use_parent_error_code=True)
class PositiveLabelMissing(MissingData):
    @property
    def message_format(self):
        return ErrorStrings.MISSING_POSITIVE_LABEL


@error_decorator(use_parent_error_code=True)
class TimeseriesInsufficientData(InsufficientSampleSize):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_INSUFFICIENT_DATA


@error_decorator(use_parent_error_code=True)
class TimeseriesInsufficientDataForecast(InsufficientSampleSize):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_INSUFFICIENT_DATA_FORECAST


@error_decorator(use_parent_error_code=True)
class TimeseriesInsufficientDataForCVOrHorizon(InsufficientSampleSize):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_INSUFFICIENT_DATA_FOR_CV_OR_HORIZON


@error_decorator(use_parent_error_code=True)
class TimeseriesInsufficientDataValidateTrainData(InsufficientSampleSize):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_INSUFFICIENT_DATA_VALIDATE_TRAIN_DATA


@error_decorator(use_parent_error_code=True)
class TimeseriesInsufficientDataForAllGrains(InsufficientSampleSize):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_INSUFFICIENT_DATA_FOR_ALL_GRAINS


@error_decorator(use_parent_error_code=True)
class StlFeaturizerInsufficientData(InsufficientSampleSize):
    @property
    def message_format(self):
        return ErrorStrings.STL_FEATURIZER_INSUFFICIENT_DATA


@error_decorator(use_parent_error_code=True)
class TimeseriesInsufficientDataForAggregation(InsufficientSampleSize):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_INSUFFICIENT_DATA_AGG


# endregion


# region InvalidDimension
class DataShapeMismatch(InvalidDimension):
    @property
    def message_format(self) -> str:
        return ErrorStrings.DATA_SHAPE_MISMATCH


@error_decorator(use_parent_error_code=True)
class DatasetsFeatureCountMismatch(DataShapeMismatch):
    @property
    def message_format(self) -> str:
        return ErrorStrings.DATASETS_FEATURE_COUNT_MISMATCH


@error_decorator(use_parent_error_code=True)
class SampleCountMismatch(DataShapeMismatch):
    @property
    def message_format(self) -> str:
        return ErrorStrings.SAMPLE_COUNT_MISMATCH


@error_decorator(use_parent_error_code=True)
class StreamingInconsistentFeatures(DataShapeMismatch):
    @property
    def message_format(self) -> str:
        return ErrorStrings.STREAMING_INCONSISTENT_FEATURES


@error_decorator(use_parent_error_code=True)
class ModelExplanationsDataMetadataDimensionMismatch(InvalidDimension):
    @property
    def message_format(self) -> str:
        return ErrorStrings.MODEL_EXPLANATIONS_DATA_METADATA_DIMENSION_MISMATCH


@error_decorator(use_parent_error_code=True)
class ModelExplanationsFeatureNameLengthMismatch(InvalidDimension):
    @property
    def message_format(self) -> str:
        return ErrorStrings.MODEL_EXPLANATIONS_FEATURE_NAME_LENGTH_MISMATCH


# endregion


# region BadData
class AllTargetsUnique(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.ALL_TARGETS_UNIQUE


class AllTargetsOverlapping(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.ALL_TARGETS_OVERLAPPING


@error_decorator(use_parent_error_code=True)
class OverlappingYminYmax(AllTargetsOverlapping):
    @property
    def message_format(self) -> str:
        return ErrorStrings.OVERLAPPING_YMIN_YMAX


@error_decorator(details_uri="https://aka.ms/datasetfromdelimitedfiles")
class InconsistentNumberOfSamples(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INCONSISTENT_NUMBER_OF_SAMPLES


class PandasDatetimeConversion(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.PANDAS_DATETIME_CONVERSION_ERROR


class NumericConversion(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.NUMBER_COLUMN_CONVERSION_ERROR


class TimeseriesColumnNamesOverlap(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_COLUMN_NAMES_OVERLAP


class TimeseriesTypeMismatchFullCV(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_TYPE_MISMATCH_FULL_CV


class TimeseriesTypeMismatchDropFullCV(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_TYPE_MISMATCH_DROP_FULL_CV


class ForecastHorizonExceeded(BadData):
    @property
    def message_format(self):
        return ErrorStrings.FORECAST_HORIZON_EXCEEDED


class TimeColumnValueOutOfRange(BadData):
    @property
    def message_format(self):
        return ErrorStrings.TIME_COLUMN_VALUE_OUT_OF_RANGE


class TimeseriesMaxHorizonWithTimeColumnValueOutOfRange(BadData):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_MAX_HORIZON_WITH_TIMECOLUMN_VAL_OUTOFRANGE


@error_decorator(use_parent_error_code=True)
class TimeseriesCustomFeatureTypeConversion(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_CUSTOM_FEATURE_TYPE_CONVERSION


class TimeseriesDfContainsNaN(BadData):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_DF_CONTAINS_NAN


# Base class of timeseries dataframe type errors.
class TimeseriesDfWrongTypeError(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_WRONG_TYPE_ERROR


class UnpartitionedData(BadData):
    @property
    def message_format(self):
        return ErrorStrings.DATA_NOT_PARTITIONED


@error_decorator(use_parent_error_code=True)
class TimeseriesDfWrongTypeOfValueColumn(TimeseriesDfWrongTypeError):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_WRONG_TYPE_OF_VALUE_COLUMN


@error_decorator(use_parent_error_code=True)
class TimeseriesDfWrongTypeOfTimeColumn(TimeseriesDfWrongTypeError):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_WRONG_TYPE_OF_TIME_COLUMN


@error_decorator(use_parent_error_code=True)
class TimeseriesDfWrongTypeOfGrainColumn(TimeseriesDfWrongTypeError):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_WRONG_TYPE_OF_GRAIN_COLUMN


@error_decorator(use_parent_error_code=True)
class TimeseriesDfWrongTypeOfLevelValues(TimeseriesDfWrongTypeError):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_WRONG_TYPE_OF_LEVEL_VALUES


@error_decorator(use_parent_error_code=True)
class TimeseriesDfUnsupportedTypeOfLevel(TimeseriesDfWrongTypeError):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_UNSUPPORTED_TYPE_OF_LEVEL


# Base class of timeseries dataframe frequency errors.
class TimeseriesDfFrequencyError(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_FREQUENCY_ERROR


@error_decorator(use_parent_error_code=True)
class TimeseriesDfFrequencyGenericError(TimeseriesDfFrequencyError):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_FREQUENCY_GENERIC_ERROR


class TimeseriesDfFrequencyNotConsistent(TimeseriesDfFrequencyError):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_FREQUENCY_NOT_CONSISTENT


class TimeseriesDfFrequencyNotConsistentGrain(TimeseriesDfFrequencyError):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_FREQUENCY_NOT_CONSISTENT_GRAIN


@error_decorator(use_parent_error_code=True)
class TimeseriesDfMultiFrequenciesDiff(TimeseriesDfFrequencyError):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_MULTI_FREQUENCIES_DIFF


@error_decorator(use_parent_error_code=True)
class TimeseriesDfMultiFrequenciesDiffData(TimeseriesDfFrequencyError):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_MULTI_FREQUENCIES_DIFF_DATA


@error_decorator(use_parent_error_code=True)
class TimeseriesDfCannotInferFrequencyFromTSId(TimeseriesDfFrequencyError):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_CANNOT_INFER_FREQ_FROM_TS_ID


@error_decorator(use_parent_error_code=True)
class TimeseriesCannotInferFrequencyFromTimeIdx(TimeseriesDfFrequencyError):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_CANNOT_INFER_FREQ_FROM_TIME_IDX


@error_decorator(use_parent_error_code=True)
class TimeseriesCannotInferSingleFrequencyForAllTS(TimeseriesDfFrequencyError):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_CANNOT_INFER_SINGLE_FREQ_FOR_ALL_TS


class TimeseriesFrequencyNotSupported(TimeseriesDfFrequencyError):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_FREQUENCY_NOT_SUPPORTED


class TimeseriesReferenceDatesMisaligned(TimeseriesDfFrequencyError):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_REFERENCE_DATES_MISALIGNED


class TimeseriesTimeIndexDatesMisaligned(TimeseriesDfFrequencyError):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_TIME_IDX_DATES_MISALIGNED


class TimeseriesDateTimeColumnBadData(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.BAD_DATA_IN_DATETIME_COLUMN


class TimeseriesDfIncorrectFormat(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_INCORRECT_FORMAT


@error_decorator(use_parent_error_code=True)
class TimeseriesDfColValueNotEqualAcrossOrigin(TimeseriesDfIncorrectFormat):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_COL_VALUE_NOT_EQUAL_ACROSS_ORIGIN


@error_decorator(use_parent_error_code=True)
class TimeseriesDfIndexValuesNotMatch(TimeseriesDfIncorrectFormat):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_INDEX_VALUES_NOT_MATCH


class TimeseriesContextAtEndOfY(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_CONTEXT_AT_END_OF_Y


class TimeseriesDfUniqueTargetValueGrain(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_UNIQUE_TARGET_VALUE_GRAIN


@error_decorator(details_uri="https://aka.ms/ForecastingConfigurations")
class TimeseriesDfDuplicatedIndexTimeColTimeIndexNaT(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_CONTAINS_NAT


@error_decorator(details_uri="https://aka.ms/ForecastingConfigurations")
class TimeseriesDfDuplicatedIndex(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_DUPLICATED_INDEX


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/ForecastingConfigurations")
class TimeseriesDfDuplicatedIndexTimeColTimeIndexColName(TimeseriesDfDuplicatedIndex):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_DUPLICATED_INDEX_TM_COL_TM_IDX_COL_NAME


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/ForecastingConfigurations")
class TimeseriesDfDuplicatedIndexAutoTimeSeriesIDDetection(TimeseriesDfDuplicatedIndex):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_DUPLICATED_INDEX_WITH_AUTO_TIMESERIES_ID_DETECTION


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/ForecastingConfigurations")
class TimeseriesDfDuplicatedIndexTimeColName(TimeseriesDfDuplicatedIndex):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_DUPLICATED_INDEX_TM_COL_NAME


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/ForecastingConfigurations")
class TimeseriesDfDatesOutOfPhase(TimeseriesDfFrequencyError):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_OUT_OF_PHASE


class TimeseriesInvalidPipeline(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_INVALID_PIPELINE


@error_decorator(use_parent_error_code=True)
class TimeseriesInvalidTypeInPipeline(TimeseriesInvalidPipeline):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_INVALID_TYPE_IN_PIPELINE


@error_decorator(use_parent_error_code=True)
class TimeseriesInvalidValueInPipeline(TimeseriesInvalidPipeline):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_INVALID_VALUE_IN_PIPELINE


@error_decorator(use_parent_error_code=True)
class TimeseriesInvalidPipelineExecutionType(TimeseriesInvalidPipeline):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_INVALID_PIPELINE_EXECUTION_TYPE


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/AutoMLConfig")
class TimeseriesTransCannotInferFreq(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_TRANS_CANNOT_INFER_FREQ


class TimeseriesInputIsNotTimeseriesDs(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_INPUT_IS_NOT_TSDS


class TimeseriesInputIsNotTimeseriesDf(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_INPUT_IS_NOT_TSDF


@error_decorator(use_parent_error_code=True)
class TimeseriesDfInvalidValAllGrainsContainSingleVal(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_INV_VAL_ALL_GRAINS_CONTAIN_SINGLE_VAL


@error_decorator(use_parent_error_code=True)
class TimeseriesDfInvalidValTmIdxWrongType(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_INV_VAL_TM_IDX_WRONG_TYPE


@error_decorator(use_parent_error_code=True)
class TimeseriesDfInvalidValOfNumberTypeInTestData(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_INV_VAL_OF_NUMBER_TYPE_IN_TEST_DATA


@error_decorator(use_parent_error_code=True)
class TimeseriesDfInvalidValColOfGroupNameInTmIdx(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_INV_VAL_COL_OF_GRP_NAME_IN_TM_IDX


@error_decorator(use_parent_error_code=True)
class TimeseriesDfInvalidValCannotConvertToPandasTimeIdx(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_INV_VAL_CANNOT_CONVERT_TO_PD_TIME_IDX


class TimeseriesDfFrequencyChanged(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_FREQUENCY_CHANGED


class TimeseriesDfTrainingValidDataNotContiguous(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_TRAINING_VALID_DATA_NOT_CONTIGUOUS


@error_decorator(use_parent_error_code=True)
class TimeseriesWrongShapeDataSizeMismatch(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_WRONG_SHAPE_DATA_SIZE_MISMATCH


@error_decorator(use_parent_error_code=True)
class TimeseriesWrongShapeDataEarlyDest(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_WRONG_SHAPE_DATA_EARLY_DESTINATION


class TimeseriesNoDataContext(BadData):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_NO_DATA_CONTEXT


class TimeseriesNothingToPredict(BadData):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_NOTHING_TO_PREDICT


class TimeseriesNonContiguousTargetColumn(BadData):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_NON_CONTIGUOUS_TARGET_COLUMN


class TimeseriesMissingValuesInY(BadData):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_MISSING_VALUES_IN_Y


class TimeseriesOnePointPerGrain(BadData):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_ONE_POINT_PER_GRAIN


class TimeSeriesReservedColumn(BadData):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_RESERVED_COLUMN


class TransformerYMinGreater(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TRANSFORMER_Y_MIN_GREATER


class InvalidLabelColumnValues(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INVALID_LABEL_COLUMN_VALUES


class BadDataInWeightColumn(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.BAD_DATA_IN_WEIGHT_COLUMN


class UnhashableValueInData(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.UNHASHABLE_VALUE_IN_DATA


@error_decorator(use_parent_error_code=True)
class DatasetContainsInf(BadData):
    @property
    def message_format(self):
        return ErrorStrings.DATASET_CONTAINS_INF


@error_decorator(use_parent_error_code=True)
class IndistinctLabelColumn(BadData):
    @property
    def message_format(self):
        return ErrorStrings.INDISTINCT_LABEL_COLUMN


@error_decorator(use_parent_error_code=True)
class InconsistentColumnTypeInTrainValid(BadData):
    @property
    def message_format(self):
        return ErrorStrings.INCONSISTENT_COLUMN_TYPE_IN_TRAIN_VALID


@error_decorator(use_parent_error_code=True)
class InvalidOnnxData(BadData):
    @property
    def message_format(self):
        return ErrorStrings.INVALID_ONNX_DATA


class AllFeaturesAreExcluded(BadData):
    @property
    def message_format(self):
        return ErrorStrings.ALL_FEATURES_ARE_EXCLUDED


class UnrecognizedFeatures(BadData):
    @property
    def message_format(self):
        return ErrorStrings.UNRECOGNIZED_FEATURES


@error_decorator(use_parent_error_code=True)
class TimeseriesEmptySeries(BadData):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_EMPTY_SERIES


@error_decorator(use_parent_error_code=True)
class TimeseriesWrongTestColumnSet(BadData):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_WRONG_COLUMNS_IN_TEST_SET


@error_decorator(use_parent_error_code=True)
class InvalidForecastDate(BadData):
    @property
    def message_format(self):
        return ErrorStrings.INVALID_FORECAST_DATE


@error_decorator(use_parent_error_code=True)
class InvalidForecastDateForGrain(BadData):
    @property
    def message_format(self):
        return ErrorStrings.INVALID_FORECAST_DATE_FOR_GRAIN


@error_decorator(use_parent_error_code=True)
class InvalidMetricForSingleValuedColumn(BadData):
    @property
    def message_format(self):
        return ErrorStrings.INVALID_METRIC_FOR_SINGLE_VALUED_COLUMN


@error_decorator(use_parent_error_code=True)
class DuplicateColumns(BadData):
    @property
    def message_format(self):
        return ErrorStrings.DUPLICATE_COLUMNS


@error_decorator(
    use_parent_error_code=True,
    details_uri="https://docs.microsoft.com/azure/machine-learning/how-to-configure-cross-"
    "validation-data-splits#specify-custom-cross-validation-data-folds",
)
class InvalidValuesInCVSplitColumn(BadData):
    @property
    def message_format(self):
        return ErrorStrings.INVALID_VALUES_IN_CV_SPLIT_COLUMN


class NoFeatureTransformationsAdded(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.NO_FEATURE_TRANSFORMATIONS_ADDED


@error_decorator(use_parent_error_code=True)
class PowerTransformerInverseTransform(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.POWER_TRANSFORMER_INVERSE_TRANSFORM


class ContentModified(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.CONTENT_MODIFIED


@error_decorator(use_parent_error_code=True)
class DataprepValidation(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.DATAPREP_VALIDATION


@error_decorator(use_parent_error_code=True)
class DatabaseQuery(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.DATABASE_QUERY


@error_decorator(use_parent_error_code=True)
class DataprepScriptExecution(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.DATAPREP_SCRIPT_EXECUTION


@error_decorator(use_parent_error_code=True)
class DataprepStepTranslation(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.DATAPREP_STEP_TRANSLATION


@error_decorator(use_parent_error_code=True)
class AllTargetsNan(BadData):
    @property
    def message_format(self):
        return ErrorStrings.ALL_TARGETS_NAN


@error_decorator(use_parent_error_code=True)
class InvalidSeriesForStl(BadData):
    @property
    def message_format(self):
        return ErrorStrings.INVALID_SERIES_FOR_STL


@error_decorator(use_parent_error_code=True)
class InvalidValuesInData(BadData):
    @property
    def message_format(self):
        return ErrorStrings.INVALID_VALUES_IN_DATA


@error_decorator(use_parent_error_code=True)
class TextDnnBadData(BadData):
    """Class for all AutoML NLP DNN errors related to bad data."""

    @property
    def message_format(self):
        return ErrorStrings.TEXTDNN_BAD_DATA


class DataContainOriginColumn(BadData):
    @property
    def message_format(self):
        return ErrorStrings.DATA_CONTAIN_ORIGIN


@error_decorator(use_parent_error_code=True)
class TimeseriesUnableToDetermineHorizon(BadData):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_UNDETECTED_HORIZON


# endregion


# region MissingData
@error_decorator(use_parent_error_code=True)
class GrainShorterThanTestSize(MissingData):
    @property
    def message_format(self):
        return ErrorStrings.GRAIN_SHORTER_THAN_TEST_SIZE


@error_decorator(use_parent_error_code=True)
class GrainAbsent(MissingData):
    @property
    def message_format(self):
        return ErrorStrings.GRAIN_ABSENT


@error_decorator(use_parent_error_code=True)
class TimeseriesGrainAbsent(MissingData):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_GRAIN_ABSENT


@error_decorator(use_parent_error_code=True)
class TimeseriesGrainAbsentValidateTrainValidData(MissingData):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_GRAIN_ABSENT_VALID_TRAIN_VALID_DAT


@error_decorator(use_parent_error_code=True)
class TimeseriesGrainAbsentNoGrainInTrain(MissingData):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_GRAIN_ABSENT_NO_GRAIN_IN_TRAIN


@error_decorator(use_parent_error_code=True)
class TimeseriesGrainAbsentNoLastDate(MissingData):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_GRAIN_ABSENT_NO_LAST_DATE


@error_decorator(use_parent_error_code=True)
class TimeseriesGrainAbsentNoDataContext(MissingData):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_GRAIN_ABSENT_NO_DATA_CONTEXT


@error_decorator(use_parent_error_code=True)
class TimeseriesNoUsableGrains(MissingData):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_NO_USABLE_GRAINS


@error_decorator(use_parent_error_code=True)
class GrainContainsEmptyValues(MissingData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_NAN_GRAIN_VALUES


@error_decorator(use_parent_error_code=True)
class TimeseriesLeadingNans(MissingData):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_LEADING_NANS


@error_decorator(use_parent_error_code=True)
class TimeseriesLaggingNans(MissingData):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_LAGGING_NANS


@error_decorator(use_parent_error_code=True)
class TimeseriesDfMissingColumn(MissingData):
    TIME_COLUMN = "Time"
    GRAIN_COLUMN = "TimeSeriesId"
    GROUP_COLUMN = "Group"
    ORIGIN_COLUMN = "Origin"
    VALUE_COLUMN = "TargetValue"
    REGULAR_COLUMN = "Regular"

    @property
    def message_format(self) -> str:
        return ErrorStrings.TIMESERIES_DF_MISSING_COLUMN


# endregion


# region EmptyData
@error_decorator(use_parent_error_code=True)
class InputDatasetEmpty(EmptyData):
    @property
    def message_format(self):
        return ErrorStrings.INPUT_DATASET_EMPTY


@error_decorator(use_parent_error_code=True)
class NoValidDates(EmptyData):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_DF_TM_COL_CONTAINS_NAT_ONLY


@error_decorator(use_parent_error_code=True)
class ForecastingEmptyDataAfterAggregation(EmptyData):
    @property
    def message_format(self):
        return ErrorStrings.FORECAST_EMPTY_AGGREGATION


# endregion


# region Authentication
class DataPathInaccessible(Authentication):
    @property
    def message_format(self):
        return ErrorStrings.DATA_PATH_INACCESSIBLE


@error_decorator(
    use_parent_error_code=True,
    details_uri="https://docs.microsoft.com/azure/machine-learning/how-to-access-data#"
    "supported-data-storage-service-types",
)
class MissingCredentialsForWorkspaceBlobStore(Authentication):
    @property
    def message_format(self):
        return ErrorStrings.MISSING_CREDENTIALS_FOR_WORKSPACE_BLOB_STORE


# endregion


# region Conflict
class CacheOperation(Conflict):
    @property
    def message_format(self):
        return ErrorStrings.CACHE_OPERATION


@error_decorator(use_parent_error_code=True, is_transient=True)
class MissingCacheContents(CacheOperation):
    @property
    def message_format(self):
        return ErrorStrings.MISSING_CACHE_CONTENTS


# endregion


# region ClientError
@error_decorator(details_uri="https://aka.ms/automltroubleshoot")
class AutoMLInternal(ClientError):
    """Base class for all AutoML system errors."""

    @property
    def message_format(self):
        return ErrorStrings.AUTOML_INTERNAL


@error_decorator(use_parent_error_code=True)
class AutoMLInternalLogSafe(AutoMLInternal):
    """Base class for all AutoML system errors."""

    @property
    def message_format(self):
        return ErrorStrings.AUTOML_INTERNAL_LOG_SAFE


@error_decorator(use_parent_error_code=True)
class TextDnnModelDownloadFailed(AutoMLInternal):
    """Base class for all AutoML system errors."""

    @property
    def message_format(self):
        return ErrorStrings.TEXTDNN_MODEL_DOWNLOAD_FAILED


class Data(AutoMLInternal):
    @property
    def message_format(self):
        return ErrorStrings.DATA


@error_decorator(use_parent_error_code=True)
class ForecastingArimaNoModel(AutoMLInternal):
    @property
    def message_format(self):
        return ErrorStrings.FORECASTING_ARIMA_NO_MODEL


@error_decorator(use_parent_error_code=True)
class ForecastingExpoSmoothingNoModel(AutoMLInternal):
    @property
    def message_format(self):
        return ErrorStrings.FORECASTING_EXPOSMOOTHING_NO_MODEL


@error_decorator(use_parent_error_code=True)
class FitNotCalled(AutoMLInternal):
    @property
    def message_format(self):
        return ErrorStrings.FIT_NOT_CALLED


class Service(AutoMLInternal):
    @property
    def message_format(self):
        return ErrorStrings.SERVICE


@error_decorator(use_parent_error_code=True)
class ArtifactUploadFailed(Service):
    @property
    def message_format(self):
        return ErrorStrings.ARTIFACT_UPLOAD_FAILURE


@error_decorator(use_parent_error_code=True)
class TimeseriesDataFormatError(AutoMLInternal):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_DATA_FORMATTING_ERROR


@error_decorator(use_parent_error_code=True)
class BothYandTargetProvidedToTsdf(AutoMLInternal):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_DS_Y_AND_TGT_COL


@error_decorator(use_parent_error_code=True)
class TimeSeriesImputerMethodTypeNotSupported(AutoMLInternal):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_IMPUTER_METHOD_TYPE_NOT_SUPPORTED


@error_decorator(use_parent_error_code=True)
class TimeSeriesImputerMethodNotSupported(AutoMLInternal):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_IMPUTER_METHOD_NOT_SUPPORTED


@error_decorator(use_parent_error_code=True)
class TimeSeriesImputerOptionNotSupported(AutoMLInternal):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_IMPUTER_OPTION_NOT_SUPPORTED


@error_decorator(use_parent_error_code=True)
class ARIMAXPDQError(AutoMLInternal):
    @property
    def message_format(self) -> str:
        return ErrorStrings.ARIMAX_PDQ_ERROR


@error_decorator(use_parent_error_code=True)
class ARIMAXSarimax(AutoMLInternal):
    @property
    def message_format(self) -> str:
        return ErrorStrings.ARIMAX_SARIMAX_ERROR


# endregion


# region ResourceExhausted
class DiskFull(ResourceExhausted):
    @property
    def message_format(self):
        return ErrorStrings.DISK_FULL


class RunInterrupted(ResourceExhausted):
    @property
    def message_format(self):
        return ErrorStrings.RUN_INTERRUPTED


# endregion


# region Memory
@error_decorator(use_parent_error_code=True)
class Memorylimit(Memory):
    @property
    def message_format(self):
        return ErrorStrings.DATA_MEMORY_ERROR


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/azurevmsizes")
class InsufficientMemory(Memory):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INSUFFICIENT_MEMORY


@error_decorator(
    use_parent_error_code=True, details_uri="https://docs.microsoft.com/en-us/azure/virtual-machines/sizes-gpu"
)
class InsufficientGPUMemory(Memory):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INSUFFICIENT_GPU_MEMORY


@error_decorator(use_parent_error_code=True)
class InsufficientSHMMemory(Memory):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INSUFFICIENT_SHM_MEMORY


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/azurevmsizes")
class InsufficientMemoryWithHeuristics(Memory):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INSUFFICIENT_MEMORY_WITH_HEURISTICS


@error_decorator(use_parent_error_code=True, details_uri="https://aka.ms/azurevmsizes")
class InsufficientMemoryLikely(Memory):
    @property
    def message_format(self) -> str:
        return ErrorStrings.INSUFFICIENT_MEMORY_LIKELY


# endregion


# region Timeout
@error_decorator(is_transient=True, details_uri="https://aka.ms/storageoptimization")
class DatasetFileRead(Timeout):
    @property
    def message_format(self) -> str:
        return ErrorStrings.DATASET_FILE_READ


class ExperimentTimedOut(Timeout):
    @property
    def message_format(self):
        return ErrorStrings.EXPERIMENT_TIMED_OUT


class IterationTimedOut(Timeout):
    @property
    def message_format(self):
        return ErrorStrings.ITERATION_TIMED_OUT


# endregion


# region ConnectionFailure
@error_decorator(use_parent_error_code=True, is_transient=True)
class HttpConnectionFailure(ConnectionFailure):
    @property
    def message_format(self):
        return ErrorStrings.HTTP_CONNECTION_FAILURE


class ManagedLocalUserError(ConnectionFailure):
    @property
    def message_format(self):
        return ErrorStrings.LOCAL_MANAGED_USER_ERROR


# endregion


# region Data
@error_decorator(use_parent_error_code=True)
class GenericFitError(Data):
    @property
    def message_format(self):
        return ErrorStrings.GENERIC_FIT_EXCEPTION


@error_decorator(use_parent_error_code=True)
class GenericTransformError(Data):
    @property
    def message_format(self):
        return ErrorStrings.GENERIC_TRANSFORM_EXCEPTION


@error_decorator(use_parent_error_code=True)
class GenericPredictError(Data):
    @property
    def message_format(self):
        return ErrorStrings.GENERIC_PREDICT_EXCEPTION


@error_decorator(use_parent_error_code=True)
class IncompatibleColumnsError(Data):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_DS_INCOMPATIBLE_COLUMNS


@error_decorator(use_parent_error_code=True)
class IncompatibleIndexError(Data):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_DS_INCOMPATIBLE_INDEX


@error_decorator(use_parent_error_code=True)
class TimeseriesHorizonAbsent(Data):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_INPUT_NO_HORIZON


@error_decorator(use_parent_error_code=True)
class TimeseriesOriginAbsent(Data):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_INPUT_NO_ORIGIN


@error_decorator(use_parent_error_code=True)
class TimeseriesUnexpectedOrigin(Data):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_UNEXPECTED_ORIGIN


@error_decorator(use_parent_error_code=True)
class DictCanNotBeConvertedToDf(Data):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_DS_DICT_CAN_NOT_BE_CONVERTED_TO_DF


@error_decorator(use_parent_error_code=True)
class TimeseriesTableGrainAbsent(Data):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_METRICS_TABLE_GRAIN


@error_decorator(use_parent_error_code=True)
class TimeseriesTableTrainAbsent(Data):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_METRICS_TABLE_TRAIN


@error_decorator(use_parent_error_code=True)
class TimeseriesTableValidAbsent(Data):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_METRICS_TABLE_VALID


# endregion


@error_decorator(use_parent_error_code=True)
class TimeseriesWrongDropnaParam(AutoMLInternal):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_WRONG_DROPNA_TYPE


@error_decorator(use_parent_error_code=True)
class NonUniqueNamesOfNewColumns(AutoMLInternal):
    @property
    def message_format(self):
        return ErrorStrings.ROLLING_WINDOW_MULTIPLE_COLUMNS


@error_decorator(use_parent_error_code=True)
class UnknownTimeseriesFeature(AutoMLInternal):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_TIME_FT_FORCE_HAS_UNKNOWN_FEATURES


@error_decorator(use_parent_error_code=True)
class NoAppropriateEsModel(AutoMLInternal):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_STL_NO_ES_MODEL


@error_decorator(use_parent_error_code=True)
class FreqByGrainWrongType(AutoMLInternal):
    @property
    def message_format(self):
        return ErrorStrings.TIMESERIES_FREQ_BY_GRAIN_WRONG_TYPE


class DataFromMultipleGroups(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.DATA_FROM_MULTIPLE_GROUPS


class HierarchyNoTrainingRun(ArgumentBlankOrEmpty):
    @property
    def message_format(self) -> str:
        return ErrorStrings.HIERARCHY_NO_TRAINING_RUN


class HierarchyAllParallelRunsFailedByUserError(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.HIERARCHY_ALL_PARALLEL_FAILURE


class HierarchyPredictionsNotFound(NotFound):
    @property
    def message_format(self) -> str:
        return ErrorStrings.HIERARCHY_PREDICTIONS_NOT_FOUND


class ExplanationsNotFound(NotFound):
    @property
    def message_format(self) -> str:
        return ErrorStrings.HIERARCHY_EXPLANATIONS_NOT_FOUND


class ModelNotFound(NotFound):
    @property
    def message_format(self) -> str:
        return ErrorStrings.MODEL_NOT_FOUND


class ModelNotPickleable(ClientError):
    @property
    def message_format(self) -> str:
        return ErrorStrings.MODEL_NOT_PICKLABLE


class TrainingDataColumnsInconsistent(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TRAINING_DATA_COLUMNS_INCONSISTENT


# region TCN Error


@error_decorator(use_parent_error_code=True)
class TCNModelNotConvergent(BadData):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TCN_MODEL_NOT_CONVERGENT


@error_decorator(use_parent_error_code=True)
class TCNForecastDeepARNaN(Data):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TCN_FORECAST_DEEPAR_NAN_IN_TRAINING_LOSS


@error_decorator(use_parent_error_code=True)
class TCNEmbeddingInvalidFactor(ArgumentInvalid):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TCN_EMBEDDING_INVALID_FACTOR


@error_decorator(use_parent_error_code=True)
class TCNEmbeddingUnsupportCalcType(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TCN_EMBEDDING_INVALID_FACTOR


@error_decorator(use_parent_error_code=True)
class TCNEmbeddingInvalidMultilevel(NotSupported):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TCN_EMBEDDING_INVALID_MULTILEVEL


@error_decorator(use_parent_error_code=True)
class TCNWrapperRuntimeError(AutoMLInternal):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TCN_RUNTIME_ERROR


@error_decorator(use_parent_error_code=True)
class TCNMetricsCalculationError(AutoMLInternal):
    @property
    def message_format(self) -> str:
        return ErrorStrings.TCN_METRICS_CALCULATION_ERROR


# endregion

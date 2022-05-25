# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Exceptions thrown by AutoML transformers."""

from azureml._common._error_response._error_response_constants import ErrorCodes

from .._diagnostics.error_definitions import ClientError

# TODO: Proper error messages for these, like in error_definitions.py


class TransformRuntimeException(ClientError):
    """
    An exception related to TransformRuntime.
    """

    _error_code = ErrorCodes.TRANSFORMRUNTIME_ERROR


class BadTransformArgumentException(TransformRuntimeException):
    """
    An exception related to BadTransformArgument.
    """

    _error_code = ErrorCodes.BADTRANSFORMARGUMENT_ERROR


class InvalidTransformArgumentException(BadTransformArgumentException):
    """
    An exception related to InvalidTransformArgument.
    """

    _error_code = ErrorCodes.INVALIDTRANSFORMARGUMENT_ERROR


class DataTransformerUnknownTaskException(InvalidTransformArgumentException):
    """
    An exception related to DataTransformerUnknownTask.
    """

    _error_code = ErrorCodes.DATATRANSFORMERUNKNOWNTASK_ERROR


class ModelingBertNoApexInvalidHiddenSizeException(InvalidTransformArgumentException):
    """
    An exception related to ModelingBertNoApexInvalidHiddenSize.
    """

    _error_code = ErrorCodes.MODELINGBERTNOAPEXINVALIDHIDDENSIZE_ERROR


class UnrecognizedTransformedFeatureNameException(InvalidTransformArgumentException):
    """
    An exception related to UnrecognizedTransformedFeatureName.
    """

    _error_code = ErrorCodes.UNRECOGNIZEDTRANSFORMEDFEATURENAME_ERROR


class UnrecognizedRawFeatureAliasNameException(InvalidTransformArgumentException):
    """
    An exception related to UnrecognizedRawFeatureAliasName.
    """

    _error_code = ErrorCodes.UNRECOGNIZEDRAWFEATUREALIASNAME_ERROR


class InvalidTransformArgumentTypeException(BadTransformArgumentException):
    """
    An exception related to InvalidTransformArgumentType.
    """

    _error_code = ErrorCodes.INVALIDTRANSFORMARGUMENTTYPE_ERROR


class ModelingBertNoApexNotIntOrStrException(InvalidTransformArgumentTypeException):
    """
    An exception related to ModelingBertNoApexNotIntOrStr.
    """

    _error_code = ErrorCodes.MODELINGBERTNOAPEXNOTINTORSTR_ERROR


class NimbusMlTextTargetEncoderFeaturizerInvalidTypeException(InvalidTransformArgumentTypeException):
    """
    An exception related to NimbusMlTextTargetEncoderFeaturizerInvalidType.
    """

    _error_code = ErrorCodes.NIMBUSMLTEXTTARGETENCODERFEATURIZERINVALIDTYPE_ERROR


class NimbusMlTextTargetEncoderLearnerInvalidTypeException(InvalidTransformArgumentTypeException):
    """
    An exception related to NimbusMlTextTargetEncoderLearnerInvalidType.
    """

    _error_code = ErrorCodes.NIMBUSMLTEXTTARGETENCODERLEARNERINVALIDTYPE_ERROR


class MalformedTransformArgumentException(BadTransformArgumentException):
    """
    An exception related to MalformedTransformArgument.
    """

    _error_code = ErrorCodes.MALFORMEDTRANSFORMARGUMENT_ERROR


class EngineeredFeatureNamesNoTransformationsInJsonException(MalformedTransformArgumentException):
    """
    An exception related to EngineeredFeatureNamesNoTransformationsInJson.
    """

    _error_code = ErrorCodes.ENGINEEREDFEATURENAMESNOTRANSFORMATIONSINJSON_ERROR


class NotSupportedTransformArgumentException(BadTransformArgumentException):
    """
    An exception related to NotSupportedTransformArgument.
    """

    _error_code = ErrorCodes.NOTSUPPORTEDTRANSFORMARGUMENT_ERROR


class EngineeredFeatureNamesUnsupportedIndexException(NotSupportedTransformArgumentException):
    """
    An exception related to EngineeredFeatureNamesUnsupportedIndex.
    """

    _error_code = ErrorCodes.ENGINEEREDFEATURENAMESUNSUPPORTEDINDEX_ERROR


class EngineeredFeatureNamesNotSupportedFeatureTypeException(NotSupportedTransformArgumentException):
    """
    An exception related to EngineeredFeatureNamesNotSupportedFeatureType.
    """

    _error_code = ErrorCodes.ENGINEEREDFEATURENAMESNOTSUPPORTEDFEATURETYPE_ERROR


class PretrainedTextDnnTransformerFitUnsupportedTaskException(NotSupportedTransformArgumentException):
    """
    An exception related to PretrainedTextDnnTransformerFitUnsupportedTask.
    """

    _error_code = ErrorCodes.PRETRAINEDTEXTDNNTRANSFORMERFITUNSUPPORTEDTASK_ERROR


class PretrainedTextDnnTransformerConvertUnsupportedTaskException(NotSupportedTransformArgumentException):
    """
    An exception related to PretrainedTextDnnTransformerConvertUnsupportedTask.
    """

    _error_code = ErrorCodes.PRETRAINEDTEXTDNNTRANSFORMERCONVERTUNSUPPORTEDTASK_ERROR


class BlankOrEmptyTransformArgumentException(BadTransformArgumentException):
    """
    An exception related to BlankOrEmptyTransformArgument.
    """

    _error_code = ErrorCodes.BLANKOREMPTYTRANSFORMARGUMENT_ERROR


class EngineeredFeatureNamesEmptyJsonException(BlankOrEmptyTransformArgumentException):
    """
    An exception related to EngineeredFeatureNamesEmptyJson.
    """

    _error_code = ErrorCodes.ENGINEEREDFEATURENAMESEMPTYJSON_ERROR


class EngineeredFeatureNamesNoRawFeatureTypeException(BlankOrEmptyTransformArgumentException):
    """
    An exception related to EngineeredFeatureNamesNoRawFeatureType.
    """

    _error_code = ErrorCodes.ENGINEEREDFEATURENAMESNORAWFEATURETYPE_ERROR


class EngineeredFeatureNamesTransformerNamesNotFoundException(BlankOrEmptyTransformArgumentException):
    """
    An exception related to EngineeredFeatureNamesTransformerNamesNotFound.
    """

    _error_code = ErrorCodes.ENGINEEREDFEATURENAMESTRANSFORMERNAMESNOTFOUND_ERROR


class InvalidTransformDataException(TransformRuntimeException):
    """
    An exception related to InvalidTransformData.
    """

    _error_code = ErrorCodes.INVALIDTRANSFORMDATA_ERROR


class TransformDataShapeErrorException(InvalidTransformDataException):
    """
    An exception related to TransformDataShapeError.
    """

    _error_code = ErrorCodes.TRANSFORMDATASHAPE_ERROR


class DataTransformerInconsistentRowCountException(TransformDataShapeErrorException):
    """
    An exception related to DataTransformerInconsistentRowCount.
    """

    _error_code = ErrorCodes.DATATRANSFORMERINCONSISTENTROWCOUNT_ERROR


class TransformerRuntimeNotCalledException(TransformRuntimeException):
    """
    An exception related to TransformerRuntimeNotCalled.
    """

    _error_code = ErrorCodes.TRANSFORMERRUNTIMENOTCALLED_ERROR


class CatImputerRuntimeNotCalledException(TransformerRuntimeNotCalledException):
    """
    An exception related to CatImputerRuntimeNotCalled.
    """

    _error_code = ErrorCodes.CATIMPUTERRUNTIMENOTCALLED_ERROR


class CrossValidationTargetImputerRuntimeNotCalledException(TransformerRuntimeNotCalledException):
    """
    An exception related to CrossValidationTargetImputerRuntimeNotCalled.
    """

    _error_code = ErrorCodes.CROSSVALIDATIONTARGETIMPUTERRUNTIMENOTCALLED_ERROR


class BinTransformerRuntimeNotCalledException(TransformerRuntimeNotCalledException):
    """
    An exception related to BinTransformerRuntimeNotCalled.
    """

    _error_code = ErrorCodes.BINTRANSFORMERRUNTIMENOTCALLED_ERROR

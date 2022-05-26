# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Error Definitions for the package."""

from azureml._common._error_definition.user_error import BadData, InvalidData
from azureml.automl.core.shared._diagnostics.automl_error_definitions import AutoMLInternal
from azureml.automl.core.shared._diagnostics.error_strings import AutoMLErrorStrings


# region ClientError
class AutoNLPInternal(AutoMLInternal):
    """Top level unknown system error."""
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.AUTOML_NLP_INTERNAL


# region BadData
class ColumnOrderingMismatch(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_COLUMN_ORDERING_MISMATCH


class ColumnTypeMismatch(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_COLUMN_TYPE_MISMATCH


class ColumnSetMismatch(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_COLUMN_SET_MISMATCH


class ConsecutiveBlankNERLines(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_CONSECUTIVE_BLANK_LINES


class DuplicateColumnNames(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_DUPLICATE_COLUMN_NAMES


class DuplicateLabelTypeMismatch(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_DUPLICATE_LABEL_TYPE_MISMATCH


class EmptyFileBeginning(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_EMPTY_NER_FILE_BEGINNING


class EmptyFileEnding(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_EMPTY_NER_FILE_ENDING


class EmptyTokenNER(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_EMPTY_NER_TOKEN


class InsufficientExamples(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_INSUFFICIENT_EXAMPLES


class InsufficientUniqueLabels(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_INSUFFICIENT_UNIQUE_LABELS


class LabelingDataConversionFailed(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_LABELING_DATA_CONVERSION_FAILED


class MalformedLabelColumn(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_MALFORMED_LABEL_COLUMN


class MalformedNERLabels(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_MALFORMED_NER_LABELS


class MalformedNERLine(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_MALFORMED_NER_LINE


class MissingDataset(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_MISSING_DATASET


class MissingLabelColumn(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_MISSING_LABEL_COLUMN


class MixedMultilabelTypes(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_MIXED_MULTILABEL_TYPES


class UnexpectedLabelFormat(BadData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_UNEXPECTED_LABEL_FORMAT
# endregion


# region InvalidData
class LabelingDataDownloadFailed(InvalidData):
    @property
    def message_format(self) -> str:
        return AutoMLErrorStrings.NLP_LABELING_DATA_DOWNLOAD_FAILED
# endregion

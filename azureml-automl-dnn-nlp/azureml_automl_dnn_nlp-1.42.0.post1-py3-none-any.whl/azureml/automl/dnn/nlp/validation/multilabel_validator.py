# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Validation logic for the AutoNLP multilabel scenario."""
from typing import Optional, Set, Tuple

import ast
import logging
import numpy as np
import pandas as pd

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.classification.multilabel.utils import change_label_col_format
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import (
    DuplicateLabelTypeMismatch,
    InsufficientUniqueLabels,
    MalformedLabelColumn,
    MixedMultilabelTypes,
    UnexpectedLabelFormat
)
from azureml.automl.dnn.nlp.common.constants import ValidationLiterals, Split
from .validators import AbstractNLPClassificationDataValidator

_logger = logging.getLogger(__name__)


class NLPMultilabelDataValidator(AbstractNLPClassificationDataValidator):
    """Validator object specific to multilabel scenario."""

    def check_custom_validation(
        self,
        label_col_name: str,
        train_data: pd.DataFrame,
        valid_data: Optional[pd.DataFrame] = None
    ) -> None:
        """
        Data validation logic specific to multilabel task, to be executed after shared validation checks.
        Side effect: may mutate the data if the old label column format is detected.

        :param label_col_name: Column name of label column.
        :param train_data: The training data to validate.
        :param valid_data: The validation data to validate.
        :return: None
        """
        if (not isinstance(train_data.loc[0, label_col_name], str)) or \
                (valid_data is not None and not isinstance(valid_data.loc[0, label_col_name], str)):
            # Early format check; this, among other things, guarantees the values can be indexed.
            raise DataException._with_error(
                AzureMLError.create(
                    MalformedLabelColumn,
                    split_type=Split.train.value,
                    info_link=ValidationLiterals.DATA_PREPARATION_DOC_LINK,
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )

        label_col_converted = False
        if not train_data.loc[0, label_col_name].startswith("["):
            try:
                change_label_col_format(input_df=train_data, label_col_name=label_col_name)
                label_col_converted = True
            except (TypeError, ValueError):
                raise DataException._with_error(
                    AzureMLError.create(
                        MalformedLabelColumn,
                        split_type=Split.train.value,
                        info_link=ValidationLiterals.DATA_PREPARATION_DOC_LINK,
                        target=ValidationLiterals.DATA_EXCEPTION_TARGET
                    )
                )

        if valid_data is not None and not valid_data.loc[0, label_col_name].startswith("["):
            try:
                change_label_col_format(input_df=valid_data, label_col_name=label_col_name)
                label_col_converted = True
            except (TypeError, ValueError):
                raise DataException._with_error(
                    AzureMLError.create(
                        MalformedLabelColumn,
                        split_type=Split.valid.value,
                        info_link=ValidationLiterals.DATA_PREPARATION_DOC_LINK,
                        target=ValidationLiterals.DATA_EXCEPTION_TARGET
                    )
                )

        if label_col_converted:
            _logger.warning("You are using the old format for the label column. It may parse labels incorrectly. "
                            "Please update your label column format to follow the new format, which you can read "
                            f"more about at {ValidationLiterals.DATA_PREPARATION_DOC_LINK}.")

        train_label_lists = self._check_eval_label_column(data=train_data,
                                                          label_col_name=label_col_name,
                                                          data_source=Split.train.value)
        label_lists = train_label_lists

        valid_label_lists = None
        if valid_data is not None:
            valid_label_lists = self._check_eval_label_column(data=valid_data,
                                                              label_col_name=label_col_name,
                                                              data_source=Split.valid.value)
            label_lists = np.concatenate([label_lists, valid_label_lists])

        if not all(isinstance(lst, list) for lst in label_lists):
            raise DataException._with_error(
                AzureMLError.create(
                    UnexpectedLabelFormat,
                    info_link=ValidationLiterals.DATA_PREPARATION_DOC_LINK,
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )

        if all(len(lst) == 1 for lst in label_lists):
            _logger.warning("IMPORTANT: All samples have exactly one label. This dataset will benefit from being run "
                            "using multi-class single-label classification instead.")

        # Get labels, partitioned by allowable types.
        int_set, str_set = self._check_label_types(train_label_lists)
        # Before merging with labels from valid set, do validation checks specific to train set.
        num_unq_labels = len(int_set | str_set)
        if num_unq_labels < ValidationLiterals.MIN_LABEL_CLASSES:
            raise DataException._with_error(
                AzureMLError.create(
                    InsufficientUniqueLabels,
                    exp_cnt=ValidationLiterals.MIN_LABEL_CLASSES,
                    act_cnt=num_unq_labels,
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )

        if valid_label_lists is not None:
            int_set_val, str_set_val = self._check_label_types(valid_label_lists)
            int_set |= int_set_val
            str_set |= str_set_val

        if int_set & str_set:
            raise DataException._with_error(
                AzureMLError.create(
                    DuplicateLabelTypeMismatch,
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )

    def _check_eval_label_column(self,
                                 data: pd.DataFrame,
                                 label_col_name: str,
                                 data_source: str) -> np.ndarray:
        """
        Convert the string-type label column into an array of label lists.
        Raise validation error if input is malformed.

        :param data: the dataframe with the labels of interest.
        :param label_col_name: name of label column.
        :param data_source: the dataset split, for logging purposes.
        :return: the array of label lists.
        """
        try:
            labels = data[label_col_name].apply(ast.literal_eval)
        except (SyntaxError, ValueError):
            raise DataException._with_error(
                AzureMLError.create(
                    MalformedLabelColumn,
                    split_type=data_source,
                    info_link=ValidationLiterals.DATA_PREPARATION_DOC_LINK,
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )
        return labels.values

    def _check_label_types(self, label_lists: np.ndarray) -> Tuple[Set[str], Set[str]]:
        """
        Iterate through the input array of label lists to create sets of all integer and string labels,
        partitioned by type. If a non-str, non-int label is found, raise a validation error.

        :param label_lists: The array of label lists.
        :return: A tuple of the integer set of labels and the string set of labels, both as strings.
        """
        int_set = set()  # type: Set[str]
        str_set = set()  # type: Set[str]
        for label_list in label_lists:
            for label in label_list:
                if isinstance(label, int):
                    int_set.add(str(label))
                elif isinstance(label, str):
                    str_set.add(label)
                else:
                    raise DataException._with_error(
                        AzureMLError.create(
                            MixedMultilabelTypes,
                            bad_type=type(label),
                            target=ValidationLiterals.DATA_EXCEPTION_TARGET
                        )
                    )
        return int_set, str_set

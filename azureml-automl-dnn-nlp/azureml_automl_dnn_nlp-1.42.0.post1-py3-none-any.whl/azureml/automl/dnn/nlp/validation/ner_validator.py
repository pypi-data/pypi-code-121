# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Validation logic specific to NER AutoNLP scenario."""
from typing import Optional

import os

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import (
    ConsecutiveBlankNERLines,
    EmptyFileBeginning,
    EmptyFileEnding,
    EmptyTokenNER,
    InsufficientExamples,
    MalformedNERLabels,
    MalformedNERLine
)
from azureml.automl.dnn.nlp.common.constants import DataLiterals, ValidationLiterals, Split
from .validators import AbstractNERDataValidator


class NLPNERDataValidator(AbstractNERDataValidator):
    """Validator object specific to NER scenario."""

    def validate(self, dir: str, train_file: str, valid_file: Optional[str] = None) -> None:
        """
        Data validation for NER scenario only.

        :param dir: directory where ner data should be downloaded
        :param train_file: name of downloaded training file.
        :param valid_file: name of downloaded validation file, if present.
        :return: None
        """
        self._check_file_format(dir, train_file, Split.train.value, True)
        if valid_file is not None:
            self._check_file_format(dir, valid_file, Split.valid.value, False)

    def _check_file_format(
        self,
        dir: str,
        file: str,
        split: str,
        check_size: Optional[bool] = False
    ) -> None:
        """
        Validate format of an input NER txt file.

        :param dir: directory containing input file.
        :param file: input file name.
        :param split: the dataset split the file corresponds to, for logging purposes.
        :param check_size: whether to check how many samples are available in the dataset.
        :return: None
        """
        file_path = os.path.join(dir, file)
        with open(file_path, encoding=DataLiterals.ENCODING, errors=DataLiterals.ERRORS) as f:
            line = f.readline()
            if line == "\n":
                raise DataException._with_error(
                    AzureMLError.create(
                        EmptyFileBeginning,
                        target=ValidationLiterals.DATA_EXCEPTION_TARGET
                    )
                )
            if line.startswith('-DOCSTART-'):  # optional beginning of a file, ignored with the following line
                line = f.readline()
                line = f.readline()

            num_examples = 0
            prev_line = None
            while line:  # not the end of file
                self._check_line_format(line, split)
                if line == '\n':  # empty line
                    if prev_line == '\n':
                        raise DataException._with_error(
                            AzureMLError.create(
                                ConsecutiveBlankNERLines,
                                split_type=split.capitalize(),
                                target=ValidationLiterals.DATA_EXCEPTION_TARGET
                            )
                        )
                    num_examples += 1
                prev_line = line
                line = f.readline()

            if prev_line != '\n':
                num_examples += 1
            if prev_line == '\n' or prev_line[-1] != '\n':
                raise DataException._with_error(
                    AzureMLError.create(
                        EmptyFileEnding,
                        split_type=split,
                        target=ValidationLiterals.DATA_EXCEPTION_TARGET
                    )
                )
            if check_size and num_examples < ValidationLiterals.MIN_TRAINING_SAMPLE:
                raise DataException._with_error(
                    AzureMLError.create(
                        InsufficientExamples,
                        exp_cnt=ValidationLiterals.MIN_TRAINING_SAMPLE,
                        act_cnt=num_examples,
                        target=ValidationLiterals.DATA_EXCEPTION_TARGET
                    )
                )

    def _check_line_format(self, line: str, split: str) -> None:
        """
        Check if one line follows the correct format. To be specific:
            1. Check if this line is empty line ('\n') or has exactly one white space
            2. If the line is not empty, check if the label starts with 'B-' or 'I-'

        :param line: string data for this line.
        :param split: the dataset split type, for logging purposes.
        :return: None
        """
        if line != '\n' and line.count(' ') > 1:
            raise DataException._with_error(
                AzureMLError.create(
                    MalformedNERLine,
                    split_type=split,
                    info_link=ValidationLiterals.NER_FORMAT_DOC_LINK,
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )

        if line != '\n':
            token, label = line.split(' ')
            if len(token) == 0:
                raise DataException._with_error(
                    AzureMLError.create(
                        EmptyTokenNER,
                        info_link=ValidationLiterals.NER_FORMAT_DOC_LINK,
                        target=ValidationLiterals.DATA_EXCEPTION_TARGET
                    )
                )
            if not (label.strip() == "O" or label.startswith("I-") or label.startswith("B-")):
                raise DataException._with_error(
                    AzureMLError.create(
                        MalformedNERLabels,
                        split_type=split,
                        info_link=ValidationLiterals.NER_FORMAT_DOC_LINK,
                        target=ValidationLiterals.DATA_EXCEPTION_TARGET
                    )
                )

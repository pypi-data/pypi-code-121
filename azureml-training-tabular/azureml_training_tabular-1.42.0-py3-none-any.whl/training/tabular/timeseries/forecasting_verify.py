# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Suite of functions for validating sanity of data."""
import datetime
from collections import Iterable
from typing import Any

import numpy as np
import pandas as pd

from .._diagnostics.azureml_error import AzureMLError
from .._diagnostics.error_definitions import (
    ArgumentInvalid,
    InvalidArgumentType,
    TimeseriesDfMissingColumn,
    TimeseriesDfWrongTypeError,
)
from .._diagnostics.reference_codes import ReferenceCodes

ALLOWED_TIME_COLUMN_TYPES = [
    pd.Timestamp,
    pd.DatetimeIndex,
    pd.Period,
    pd.PeriodIndex,
    datetime.datetime,
    datetime.date,
]


class Messages:
    """Define validation and error messages."""

    INVALID_TIMESERIESDATAFRAME = "The input X is not a TimeSeriesDataFrame."
    INPUT_IS_NOT_TIMESERIESDATAFRAME = "Input argument should be an " + "instance of TimeSeriesDataFrame class."
    XFORM_INPUT_IS_NOT_TIMESERIESDATAFRAME = "Transform input should be an " + "instance of TimeSeriesDataFrame."
    BAD_MODEL_STATE_MESSAGE = "Model not yet fit"
    SCHEMA_MISMATCH_MESSAGE = "Schema of the given dataset does not match " + "the expected schema"
    ESTIMATOR_NOT_SUPPORTED = "Estimator is not of supported type."
    PIPELINE_EXECUTION_TYPE_INVALID = "The execution type specified is " + "invalid or not supported."
    PIPELINE_FINAL_ESTIMATOR_INVALID = "The final estimator in the pipeline " + "is invalid."
    PIPELINE_FORMAT_ERROR = "Pipeline can have transformers with an ending " + "estimator"
    PIPELINE_STEP_ADD_INVALID = "Pipeline validation fails with the new step."
    PIPELINE_STEP_REMOVE_INVALID = "Pipeline step cannot be removed, " "because it doesn't exist."
    PIPELINE_EXECUTION_ERROR = "Error executing pipeline."
    PIPELINE_INVALID = "Invalid pipeline"
    COMPUTE_STRATEGY_INVALID = "Compute strategy is either invalid or not set."
    COMPUTE_STRATEGY_MUST_INHERIT_BASE = (
        "Compute strategy is invalid. The compute type must be a subclass of ComputeBase class."
    )
    COMPUTE_ERROR_STATE_INVALID = (
        "Cannot schedule jobs since compute state is invalid. View the errors on the compute object for detail."
    )
    COMPUTE_MUST_IMPLEMENT_EXECUTE_JOB = "A valid 'execute_job' implementation must be provided."
    FUNC_PARAM_NOT_SPECIFIED = "A valid processing function parameter must be specified."
    PARAM_MUST_BE_CALLABLE = "The `{}` parameter must be a callable."
    DATA_PARAM_NOT_SPECIFIED = "A valid data parameter must be specified."


def type_is_numeric(data_type: Any, message: str, should_raise: bool = True) -> bool:
    """
    Raise exception if input type is not numeric.

    :param data_type: Input type to test
    :param message: Name of variable being checked
    :param should_raise: If a failure in validating the datatype should raise an exception
    :return True, if the argument is of a numpy numeric type
    """
    if not (
        np.issubdtype(data_type, np.floating)
        or np.issubdtype(data_type, np.signedinteger)
        or np.issubdtype(data_type, np.uint8)
        or np.issubdtype(data_type, np.int16)
        or np.issubdtype(data_type, np.int32)
        or np.issubdtype(data_type, np.int64)
    ):
        if should_raise:
            raise AzureMLError.create(
                InvalidArgumentType,
                target="data_type",
                argument="data_type",
                actual_type=type(data_type),
                expected_types="int, float",
                reference_code=ReferenceCodes._TS_TYPE_NOT_NUMERIC,
            )
        return False
    return True


def type_is_one_of(data_type, given_types, message):
    """
    Raise exception if input type is among a list of given types.

    :param data_type: Input type to test
    :param given_types: List of types to check against
    :param message: Name of variable being checked
    """
    if not any([np.issubdtype(data_type, x) for x in given_types]):
        raise AzureMLError.create(
            InvalidArgumentType,
            target="data_type",
            argument="data_type",
            actual_type=type(data_type),
            expected_types=", ".join([str(x) for x in given_types]),
            reference_code=ReferenceCodes._TS_TYPE_NOT_ONE_OF,
        )


def is_list_oftype(value, valuetype):
    """
    Raise exception if input value is not a list of a given type.

    :param value: Input list to test
    :param valuetype: Value type to check against
    """
    if not isinstance(value, list):
        raise AzureMLError.create(
            ArgumentInvalid,
            target="value",
            argument_name="value",
            expected_type="list",
            reference_code=ReferenceCodes._TS_TYPE_NOT_LIST,
        )

    if any([not isinstance(x, valuetype) for x in value]):
        raise AzureMLError.create(
            InvalidArgumentType,
            target="valuetype",
            argument="valuetype",
            actual_type=", ".join(x for x in value if not isinstance(x, valuetype)),
            expected_types="valuetype",
            reference_code=ReferenceCodes._TS_TYPE_LIST_MISMATCH,
        )


def is_iterable_but_not_string(obj):
    """
    Determine if an object has iterable, list-like properties.

    Importantly, this functions *does not* consider a string
    to be list-like, even though Python strings are iterable.

    :param obj: Object to check
    :return: True if object is iterable
    """
    return isinstance(obj, Iterable) and not isinstance(obj, str)


def data_frame_properties_are_equal(property1, property2):
    """
    Determine if two TimeSeriesDataFrame properties are equal.

    Since the properties can be scalars or vectors, this check is more than
    just a single boolean statement.

    :param property1: First property to check
    :param property2: Second property to check
    :return: True if properties are equal
    """
    p1_iterable = is_iterable_but_not_string(property1)
    p2_iterable = is_iterable_but_not_string(property2)

    if p1_iterable and p2_iterable:
        return set(property1) == set(property2)
    elif (not p1_iterable) and (not p2_iterable):
        return property1 == property2
    elif p1_iterable and (not p2_iterable) and len(property1) == 1:
        return property2 in property1
    elif (not p1_iterable) and p2_iterable and len(property2) == 1:
        return property1 in property2
    else:
        return False


def data_frame_properties_intersection(property1, property2):
    """
    Determine the intersection of two TimeSeriesDataFrame properties.

    If the intersection is empty, an empty list is returned.
    Since the properties can be scalars or vectors, this check is more
    than just a single boolean statement.

    :param property1: First property to check
    :param property2: Second property to check
    :return: List of column names in the intersection
    """
    p1_iterable = is_iterable_but_not_string(property1)
    p2_iterable = is_iterable_but_not_string(property2)

    if p1_iterable and p2_iterable:
        return list(set(property1).intersection(set(property2)))
    elif (not p1_iterable) and (not p2_iterable):
        return [property1] if property1 == property2 else []
    elif p1_iterable and (not p2_iterable):
        return list(set(property1).intersection({property2}))
    elif (not p1_iterable) and p2_iterable:
        return list(set(property2).intersection({property1}))
    else:
        return []


def check_cols_exist(df, cols):
    """
    Check whether cols exist in X.

    :param df: A TimeSeriesDataFrame or pandas.DataFrame_.

    :param cols: str or array-like, a column name or a list of column names.

    :return: None.
    """
    if is_iterable_but_not_string(cols):
        for col in cols:
            if col not in df.columns:
                raise AzureMLError.create(
                    TimeseriesDfMissingColumn,
                    target=TimeseriesDfMissingColumn.REGULAR_COLUMN,
                    reference_code=ReferenceCodes._TST_NO_REGULAR_COLNAME_FC_VERI,
                    column_names=col,
                )
    elif isinstance(cols, str):
        if cols not in df.columns:
            raise AzureMLError.create(
                TimeseriesDfMissingColumn,
                target=TimeseriesDfMissingColumn.REGULAR_COLUMN,
                reference_code=ReferenceCodes._TST_NO_REGULAR_COLNAME_FC_VERI_STR,
                column_names=[cols],
            )
    else:
        raise AzureMLError.create(
            TimeseriesDfWrongTypeError, target="cols", reference_code=ReferenceCodes._TSDF_WRONG_TYPE_OF_COL
        )


###############################################################################


def is_datetime_like(x):
    """
    Check if argument is a legitimate datetime-like object.

    Only such objects can be put into time indices.

    :param x: Input Object
    :return: True if input is datetime-like
    """
    return any(isinstance(x, time_col_type) for time_col_type in ALLOWED_TIME_COLUMN_TYPES)


###############################################################################


def is_collection(x):
    """Return `True` if `x` is a list, tuple, or set, `False` otherwise."""
    return is_iterable_but_not_string(x) and not isinstance(x, dict)

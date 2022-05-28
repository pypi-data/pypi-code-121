import re
import typing

import pandas as pd

from mlfoundry.dataset.types import DatasetSchema
from mlfoundry.exceptions import MlFoundryException

DATASET_NAME_REGEX = re.compile(r"^[a-zA-Z0-9-_]*$")


def validate_dataset_name(name: str):
    if not name or not isinstance(name, str):
        raise MlFoundryException(
            f"dataset name '{name}' is not a valid non-empty string"
        )
    if not DATASET_NAME_REGEX.match(name):
        raise MlFoundryException(
            f"dataset name '{name}' should only contain alphanumeric or dash"
        )


def validate_dataset(
    features: pd.DataFrame,
    predictions: typing.Optional[pd.Series],
    actuals: typing.Optional[pd.Series],
    schema: DatasetSchema,
):
    for feature_name, inferred_field_type in schema.features.items():
        if inferred_field_type.field_type is None:
            raise MlFoundryException(
                f"Could not identify field type of feature {feature_name} "
                f"inferred pandas type is {inferred_field_type.pandas_inferred_dtype}"
            )
    num_row_features = len(features)

    if predictions is not None:
        num_row_predictions = len(predictions)
        if num_row_features != num_row_predictions:
            raise MlFoundryException(
                f"number of rows in features {num_row_features} is not equal "
                f"to number of rows in predictions {num_row_predictions}"
            )
        if schema.predictions.field_type is None:
            raise MlFoundryException(
                "Could not identify field type of predictions "
                f"inferred pandas type is {schema.predictions.pandas_inferred_dtype}"
            )

    if actuals is not None:
        num_row_actuals = len(actuals)
        if num_row_features != num_row_actuals:
            raise MlFoundryException(
                f"number of rows in features {num_row_features} is not equal "
                f"to number of rows in actuals {num_row_actuals}"
            )
        if schema.actuals.field_type is None:
            raise MlFoundryException(
                "Could not identify field type of actuals "
                f"inferred pandas type is {schema.actuals.pandas_inferred_dtype}"
            )

    if predictions is not None and actuals is not None:
        if schema.actuals.field_type != schema.predictions.field_type:
            raise MlFoundryException(
                f"predictions field type {schema.predictions.field_type} not matching with "
                f"actuals field type {schema.actuals.field_type}"
            )

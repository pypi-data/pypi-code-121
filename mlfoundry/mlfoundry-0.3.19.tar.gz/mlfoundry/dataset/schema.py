import typing

import pandas as pd

from mlfoundry.dataset.types import DatasetSchema, FieldType, InferredFieldType

CATEGORICAL_PANDAS_TYPES = {"categorical", "boolean", "integer", "string"}
NUMERICAL_PANDAS_TYPES = {"integer", "floating", "mixed-integer-float"}
EMPTY_TYPE = "empty"


def infer_field_type(data: typing.Iterable) -> InferredFieldType:
    inferred_dtype = pd.api.types.infer_dtype(data)
    # In [59]: data = pd.read_csv("tests/dataset/test_data/logged_dataset/features.csv")
    # In [60]: data["f"]
    # Out[60]:
    # 0       NaN
    # 1       NaN
    #          ..
    # 12499   NaN
    # Name: f, Length: 12500, dtype: float64
    #
    # In [61]: data["f"].isna().all()
    # Out[61]: True
    # for some reason dtype of a completly empty column is float64
    # pd.api.types.infer_dtype will look at the the column dtype first
    if pd.isna(data).all():
        return InferredFieldType(
            field_type=FieldType.EMPTY, pandas_inferred_dtype=inferred_dtype
        )

    if inferred_dtype == EMPTY_TYPE:
        return InferredFieldType(
            field_type=FieldType.EMPTY, pandas_inferred_dtype=inferred_dtype
        )

    if inferred_dtype in NUMERICAL_PANDAS_TYPES:
        return InferredFieldType(
            field_type=FieldType.NUMERICAL, pandas_inferred_dtype=inferred_dtype
        )
    if inferred_dtype in CATEGORICAL_PANDAS_TYPES:
        return InferredFieldType(
            field_type=FieldType.CATEGORICAL, pandas_inferred_dtype=inferred_dtype
        )

    # unknown type
    return InferredFieldType(field_type=None, pandas_inferred_dtype=inferred_dtype)


def build_schema(
    features: pd.DataFrame,
    predictions: typing.Optional[pd.Series],
    actuals: typing.Optional[pd.Series],
) -> DatasetSchema:
    features_schema = dict()
    for col_name in features.columns:
        features_schema[col_name] = infer_field_type(features[col_name])

    prediction_schema = None
    if predictions is not None:
        prediction_schema = infer_field_type(predictions)

    actuals_schema = None
    if actuals is not None:
        actuals_schema = infer_field_type(actuals)

    return DatasetSchema(
        features=features_schema, actuals=actuals_schema, predictions=prediction_schema
    )

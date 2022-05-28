import json
from typing import List, Any, Optional, Dict

import boto3
import numpy as np

DYNAMODB = "dynamodb"
TABLE = "Table"
ATTRIBUTE_NAME = "AttributeName"
ATTRIBUTE_TYPE = "AttributeType"
KEY_TYPE = "KeyType"
KEY_SCHEMA = "KeySchema"
ITEM = "Item"
ITEMS = "Items"
DYNAMODB_STRING_TYPE = "S"
DYNAMODB_NUMBER_TYPE = "N"
HASH = "HASH"
RANGE = "RANGE"

PRIMARY_KEY_ATTRIBUTE_NAME_VALUE = "_feature_store_internal__primary_keys"
PRIMARY_KEY_SCHEMA = {ATTRIBUTE_NAME: PRIMARY_KEY_ATTRIBUTE_NAME_VALUE, KEY_TYPE: HASH}
TTL_KEY_ATTRIBUTE_NAME_VALUE = "_feature_store_internal__ttl_column"


def to_dynamodb_primary_key(primary_key_values: List[Any]):
    return {PRIMARY_KEY_ATTRIBUTE_NAME_VALUE: json.dumps(primary_key_values)}


def to_range_schema(timestamp_key: str):
    return {ATTRIBUTE_NAME: timestamp_key, KEY_TYPE: RANGE}


def key_schema_to_tuple(key_schema_element: Dict[str, str]):
    return (key_schema_element[ATTRIBUTE_NAME], key_schema_element[KEY_TYPE])


def key_schemas_equal(key_schema1: List[Dict], key_schema2: List[Dict]):
    # Compare two KeySchemas, ignoring order of items.
    key_schema_tuples1 = set(key_schema_to_tuple(ks) for ks in key_schema1)
    key_schema_tuples2 = set(key_schema_to_tuple(ks) for ks in key_schema2)
    return key_schema_tuples1 == key_schema_tuples2


def to_safe_select_expression(feature_names: List[str]):
    """
    Helper to create the args for safe feature selection in DynamoDB. DynamoDB projection expressions (which define the
    attributes to retrieve), cannot be used with reserved keywords or special characters (including spaces).
    e.g. "feat 1", "_feat_1", "comment" are all invalid projection expressions.

    See the Amazon documentation for more details:
    https://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_Query.html#DDB-Query-request-ExpressionAttributeNames

    To be safe, we alias all features with [#f0, #f1...]. Selecting ["feat 1", "_feat_1", "comment"] yields:
        - ProjectionExpression="#f0, #f1, #f2"
        - ExpressionAttributeNames={"#f0": "feat 1", "#f1": "_feat_1", "#f2": "comment}

    :param feature_names: List of feature names to select.
    :return: Safe DynamoDB expression args for selecting the given features.
    """
    safe_aliases = [f"#f{i}" for i in range(len(feature_names))]
    return {
        "ProjectionExpression": ", ".join(safe_aliases),
        "ExpressionAttributeNames": dict(zip(safe_aliases, feature_names)),
    }


def get_dynamodb_resource(
    access_key_id: str,
    secret_access_key: str,
    region: str,
    session_token: Optional[str] = None,
):
    return boto3.resource(
        DYNAMODB,
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=region,
        aws_session_token=session_token,
    )


def return_if_none(converter):
    """
    Decorator to return None early if the value parameter passed into converter function is None.
    :param converter: Static or non-static function.
    :return: None if input is None; otherwise, converted value.
    """

    def inner(*args, **kwargs):
        # This function expects either one positional argument or one keyword argument with name
        # "value".
        # Perform has_args xor has_kwargs before applying the None logic, this way if the user
        # incorrectly passes in wrong arguments we can rely on the underlying logic of converter
        # function to catch the errors.
        non_self_args = args[
            -1:
        ]  # ignore self argument if converter is a non-static method
        if (len(non_self_args) > 0) != ("value" in kwargs.keys()):
            if (len(non_self_args) and non_self_args[0] is None) or (
                "value" in kwargs.keys() and kwargs["value"] is None
            ):
                return None
        return converter(*args, **kwargs)

    return inner


def return_if_nan(converter):
    """
    Decorator to return np.nan if the value parameter passed into the converter function is None.
    This is used for the numpy.int16/32/64 types, as np.nan is not a valid input for them.

    TODO (ML-20967): Determine what represents a empty value in online lookup and update this decorator.
    """

    def inner(value):
        """
        We currently use np.nan to represent missing values from the online store.
        np.nan is a np.float type and can't be coerced to a np.int16/32/64.
        """
        if isinstance(value, np.float) and np.isnan(value):
            return np.nan
        return converter(value)

    return inner

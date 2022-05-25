import os
import typing as t
from datetime import datetime
from decimal import Context
from functools import reduce

from lifeomic_chatbot_tools._utils import ImportExtraError


try:
    import boto3
    from boto3.dynamodb.conditions import Key
    from botocore.config import Config
except ImportError:
    raise ImportExtraError("aws", __name__)

from lifeomic_chatbot_tools.persistence.record_store.base import IRecord, IRecordStore


KeyDict = t.Dict[str, t.Any]
"""
The type of primary key/unique record identifier that DynamoDB uses, since it can sometimes use composite keys, which
are a combination of the partition key and sort key.
"""


class IDynamoDBRecord(IRecord[KeyDict], t.Protocol):
    def dict(self) -> dict:
        """Converts this object into a dictionary that DynamoDB can save."""
        ...

    @classmethod
    def parse_obj(cls, obj: t.Any) -> "IDynamoDBRecord":
        """Parses a representation of this class produced by `self.dict(...)` into a class object."""
        ...


TIDynamoDBRecord = t.TypeVar("TIDynamoDBRecord", bound=IDynamoDBRecord)


class DynamoDBRecordStore(t.Generic[TIDynamoDBRecord], IRecordStore[KeyDict, TIDynamoDBRecord]):
    """
    A DynamoDB DAO for Pydantic data models. In addition to its parent class's `WHERE equals` behavior, this class
    also supports arbitrary `WHERE` clauses (e.g. ``<=``), using Firestore's `operator string syntax <https://googleapis
    .dev/python/firestore/latest/collection.html?highlight=where#google.cloud.firestore_v1.base_collection.BaseCollectio
    nReference.where>`_.
    """

    def __init__(
        self,
        table_name: str,
        record_class: t.Type[TIDynamoDBRecord],
        *,
        primary_key_field_name="id",
        sort_key_field_name=None,
    ):
        self.record_cls = record_class
        self._table = boto3.resource(
            "dynamodb", endpoint_url=os.getenv("AWS_ENDPOINT"), config=Config(region_name=os.getenv("AWS_REGION"))
        ).Table(table_name)
        self._pk = primary_key_field_name
        self._sk = sort_key_field_name
        self._decimal_ctx = Context(prec=38)  # dynamodb has a maximum precision of 38 digits for decimal numbers

    def save(self, record: TIDynamoDBRecord):
        item_dict = {**record.dict(), **record.get_id()}
        item_dict = self.make_dynamodb_compatible(item_dict)
        self._table.put_item(Item=item_dict)

    def get(self, id_: KeyDict) -> t.Optional[TIDynamoDBRecord]:
        res = self._table.get_item(Key=self.make_dynamodb_compatible(id_))
        if "Item" not in res:
            return None
        return t.cast(TIDynamoDBRecord, self.record_cls.parse_obj(res["Item"]))

    def delete(self, id_: KeyDict) -> bool:
        res = self._table.delete_item(Key=self.make_dynamodb_compatible(id_), ReturnValues="ALL_OLD")
        # `ReturnValues="ALL_OLD"` causes DynamoDB to return the attributes of the item as it appeared
        # before the DeleteItem operation. If there are no attributes, we assume the item did not exist
        # before the delete operation, and so was not actually deleted.
        return len(res.get("Attributes", {})) > 0

    def delete_all(self, *conditions: t.Tuple[str, str, t.Any], **where_equals) -> int:
        """
        Deletes all records which satisfy the optional ``*conditions`` and ``*where_equals`` conditions. Returns the
        number of records that were deleted. **Note**: the current implementation for this method is very slow, using
        the DynamoDB scan method under the hood.
        """
        # TODO: This is an incredibly slow way of doing this. Use indexes and a batch delete instead.
        num_deleted = 0
        for record in self.get_all(*conditions, **where_equals):
            self.delete(record.get_id())
            num_deleted += 1
        return num_deleted

    def get_all(self, *conditions: t.Tuple[str, str, t.Any], **where_equals) -> t.Iterable[TIDynamoDBRecord]:
        """
        Paginates over all records in the table, yielding them in an iterator. Retrieves all records which satisfy the
        optional ``*conditions`` and ``**where_equals`` equality conditions.
        """
        done, start_key, use_query = False, None, False
        conditions_expression = self._set_conditions(*conditions, **where_equals)
        if conditions_expression is None:
            conditions_expression = {}
        if "KeyConditionExpression" in conditions_expression.keys():
            use_query = True
        while not done:
            if start_key:
                if use_query:
                    res = self._table.query(ExclusiveStartKey=start_key, **conditions_expression)
                else:
                    res = self._table.scan(ExclusiveStartKey=start_key, **conditions_expression)
            else:
                if use_query:
                    res = self._table.query(**conditions_expression)
                else:
                    res = self._table.scan(**conditions_expression)
            start_key = res.get("LastEvaluatedKey")
            done = start_key is None
            for item in res.get("Items", []):
                yield t.cast(TIDynamoDBRecord, self.record_cls.parse_obj(item))

    def _set_conditions(self, *conditions: t.Tuple[str, str, t.Any], **where_equals) -> dict:
        """
        `FilterExpression` specifies a condition that returns only items that satisfy the condition - all other items
        are discarded. However, the filter is applied only after the entire table has been scanned.
        `KeyConditionExpression` specifies a condition for partition key or sort key. It requires an equality check on a
        partition key value, and optional other operators check on sort key. Using `KeyConditionExpression`, `Query`
        performs a direct lookup to a selected partition based on primary or secondary partition/hash. `Scan` only
        accepts `FilterExpression` argument, where as query accepts both `KeyConditionExpression`, and
        `FilterExpression`. Important: To use `Query`, we must provide `KeyConditionExpression` --> so if
        `KeyConditionExpression` is not provided, we need to use `Scan`, otherwise we use `Query`.
        """
        if self._sk is None:
            filters_list, p_key_flag, p_key_condition = [], False, None
            for attr, value in where_equals.items():
                if attr == self._pk and p_key_flag is False:
                    p_key_flag = True
                    p_key_condition = Key(attr).eq(self.make_dynamodb_compatible(value))
                else:
                    filters_list.append(Key(attr).eq(self.make_dynamodb_compatible(value)))
            for attr, op, value in conditions:
                if attr == self._pk and op == "==" and p_key_flag is False:
                    p_key_flag = True
                    p_key_condition = Key(attr).eq(self.make_dynamodb_compatible(value))
                else:
                    filters_list.append(self.choose_operator(attr, op, value))

            if len(filters_list) == 0 and p_key_flag is False:
                return {}
            if len(filters_list) == 0 and p_key_flag:
                return {"KeyConditionExpression": p_key_condition}

            if len(filters_list) != 0 and p_key_flag is False:
                res = reduce(lambda x, y: x & y, filters_list)
                return {"FilterExpression": res}
            if len(filters_list) != 0 and p_key_flag:
                res = reduce(lambda x, y: x & y, filters_list)
                return {"KeyConditionExpression": p_key_condition, "FilterExpression": res}

        else:
            filters_list, p_key_flag, sort_key_list, p_key_condition = [], False, [], None
            for attr, value in where_equals.items():
                if attr == self._pk and p_key_flag is False:
                    p_key_flag = True
                    p_key_condition = Key(attr).eq(self.make_dynamodb_compatible(value))
                elif attr == self._sk:
                    sort_key_list.append(Key(attr).eq(self.make_dynamodb_compatible(value)))
                else:
                    filters_list.append(Key(attr).eq(self.make_dynamodb_compatible(value)))
            for attr, op, value in conditions:
                if attr == self._pk and op == "==" and p_key_flag is False:
                    p_key_flag = True
                    p_key_condition = Key(attr).eq(self.make_dynamodb_compatible(value))
                elif attr == self._sk:
                    sort_key_list.append(self.choose_operator(attr, op, value))
                else:
                    filters_list.append(self.choose_operator(attr, op, value))

            # important check
            if p_key_flag and len(sort_key_list) >= 3:
                raise Exception("keyconditionexpressions must only contain one condition per key")
            if p_key_flag and len(sort_key_list) == 2:
                # it converts (a <= x <= b) into Key(x).between(a, b),
                # pay attention that keyconditionexpressions must only contain one condition per key
                sort_key_list = self.combine_multiple_condition_sort_key(*conditions, **where_equals)

            if len(filters_list) == 0 and p_key_flag is False and len(sort_key_list) == 0:
                return {}
            if len(filters_list) == 0 and p_key_flag and len(sort_key_list) == 0:
                return {"KeyConditionExpression": p_key_condition}
            if len(filters_list) == 0 and p_key_flag and len(sort_key_list) != 0:
                sort_key_list.append(p_key_condition)
                key_res = reduce(lambda x, y: x & y, sort_key_list)
                return {"KeyConditionExpression": key_res}
            if len(filters_list) == 0 and p_key_flag is False and len(sort_key_list) != 0:
                res = reduce(lambda x, y: x & y, sort_key_list)
                return {"FilterExpression": res}

            if len(filters_list) != 0 and p_key_flag is False and len(sort_key_list) == 0:
                res = reduce(lambda x, y: x & y, filters_list)
                return {"FilterExpression": res}
            if len(filters_list) != 0 and p_key_flag and len(sort_key_list) == 0:
                res = reduce(lambda x, y: x & y, filters_list)
                return {"KeyConditionExpression": p_key_condition, "FilterExpression": res}
            if len(filters_list) != 0 and p_key_flag and len(sort_key_list) != 0:
                sort_key_list.append(p_key_condition)
                key_res = reduce(lambda x, y: x & y, sort_key_list)
                res = reduce(lambda x, y: x & y, filters_list)
                return {"KeyConditionExpression": key_res, "FilterExpression": res}
            if len(filters_list) != 0 and p_key_flag is False and len(sort_key_list) != 0:
                filters_list.extend(sort_key_list)
                res = reduce(lambda x, y: x & y, filters_list)
                return {"FilterExpression": res}
        return {}

    def choose_operator(self, attr, op, value):
        value = self.make_dynamodb_compatible(value)
        if op == "<=":
            return Key(attr).lte(value)
        if op == "<":
            return Key(attr).lt(value)
        if op == ">=":
            return Key(attr).gte(value)
        if op == ">":
            return Key(attr).gt(value)
        if op == "==":
            return Key(attr).eq(value)

    def combine_multiple_condition_sort_key(self, *conditions: t.Tuple[str, str, t.Any], **where_equals) -> list:
        lte_flag, gte_flag, sort_key_list, dict_value = False, False, [], {}
        for attr, value in where_equals.items():
            if attr == self._sk:
                sort_key_list.append(Key(attr).eq(self.make_dynamodb_compatible(value)))
                return sort_key_list
        for attr, op, value in conditions:
            if attr == self._sk and op == "==":
                sort_key_list.append(Key(attr).eq(self.make_dynamodb_compatible(value)))
                return sort_key_list
            if attr == self._sk and op == "<=":
                lte_flag = True
                dict_value["lte"] = self.make_dynamodb_compatible(value)
            if attr == self._sk and op == ">=":
                gte_flag = True
                dict_value["gte"] = self.make_dynamodb_compatible(value)
        if lte_flag and gte_flag:
            sort_key_list.append(Key(self._sk).between(dict_value["gte"], dict_value["lte"]))
            return sort_key_list
        return []

    def remap(self, o: object, apply: t.Callable):
        if isinstance(o, dict):
            return {k: self.remap(v, apply) for k, v in o.items()}
        elif isinstance(o, (list, tuple, set)):
            return type(o)(self.remap(elem, apply) for elem in o)
        elif isinstance(o, (str, int, float, type(None), datetime)):
            return apply(o)
        else:
            raise AssertionError(f"remap encountered unsupported type {type(o)}")

    def make_value_dynamodb_compatible(self, value):
        """Tries to convert ``value`` to a type DynamoDB can handle."""
        if isinstance(value, datetime):
            # An attribute with the type of datetime is recorded as iso format, so the value being used for conditional
            # search should be iso format as well.
            value = value.isoformat()
        elif isinstance(value, float):
            # DynamodB doesn't support float type. It must be converted to decimal. Also, a local `decimal.Context` is
            # needed because DynamoDB's default context will throw an error if any rounding occurs.
            value = self._decimal_ctx.create_decimal_from_float(value)
        return value

    def make_dynamodb_compatible(self, o: object):
        return self.remap(o, self.make_value_dynamodb_compatible)

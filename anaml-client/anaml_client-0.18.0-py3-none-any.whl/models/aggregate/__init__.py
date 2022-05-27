"""Generated implementation of aggregate."""

# WARNING DO NOT EDIT
# This code was generated from aggregate.mcn

from __future__ import annotations

import abc  # noqa: F401
import dataclasses  # noqa: F401
import datetime  # noqa: F401
import enum  # noqa: F401
import isodate  # noqa: F401
import json  # noqa: F401
import jsonschema  # noqa: F401
import logging  # noqa: F401
import typing  # noqa: F401
import uuid  # noqa: F401
try:
    from anaml_client.utils.serialisation import JsonObject  # noqa: F401
except ImportError:
    pass


class AggregateExpression(enum.Enum):
    """Aggregate expressions for Anaml Event features."""
    Sum = "sum"
    Count = "count"
    CountDistinct = "countdistinct"
    Avg = "avg"
    Std = "std"
    Max = "max"
    Min = "min"
    MaxBy = "maxby"
    MinBy = "minby"
    First = "first"
    Last = "last"
    PercentageChange = "percentagechange"
    AbsoluteChange = "absolutechange"
    StandardScore = "standardscore"
    CollectList = "collectlist"
    CollectSet = "collectset"
    BasketSum = "basketsum"
    BasketLast = "basketlast"
    
    @classmethod
    def json_schema(cls) -> dict:
        """JSON schema for 'AggregateExpression'.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [
                        "sum",
                        "count",
                        "countdistinct",
                        "avg",
                        "std",
                        "max",
                        "min",
                        "maxby",
                        "minby",
                        "first",
                        "last",
                        "percentagechange",
                        "absolutechange",
                        "standardscore",
                        "collectlist",
                        "collectset",
                        "basketsum",
                        "basketlast",
                    ]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> AggregateExpression:
        """Validate and parse JSON data into an instance of AggregateExpression.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of AggregateExpression.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return AggregateExpression(str(data['adt_type']))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing AggregateExpression", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            JSON data ready to be serialised.
        """
        return {'adt_type': self.value}
    
    @classmethod
    def from_json_key(cls, data: str) -> AggregateExpression:
        """Validate and parse a value from a JSON dictionary key.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of AggregateExpression.
        """
        return AggregateExpression(str(data))
    
    def to_json_key(self) -> str:
        """Serialised this instanse as a JSON string for use as a dictionary key.
        
        Returns:
            A JSON string ready to be used as a key.
        """
        return str(self.value)

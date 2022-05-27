"""Generated implementation of select_expression."""

# WARNING DO NOT EDIT
# This code was generated from select-expression.mcn

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


@dataclasses.dataclass(frozen=True)
class SelectExpression:
    """SQL expression for select clause.
    
    Args:
        sql (str): A data field.
    """
    
    sql: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for SelectExpression data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string"
                }
            },
            "required": [
                "sql",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> SelectExpression:
        """Validate and parse JSON data into an instance of SelectExpression.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of SelectExpression.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return SelectExpression(
                sql=str(data["sql"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing SelectExpression",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "sql": str(self.sql)
        }

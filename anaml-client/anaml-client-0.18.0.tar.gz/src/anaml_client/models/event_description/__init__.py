"""Generated implementation of event_description."""

# WARNING DO NOT EDIT
# This code was generated from event-description.mcn

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

from ..entity import EntityId


@dataclasses.dataclass(frozen=True)
class TimestampInfo:
    """Configuration to calculate the event timestamp for a table.
    
    Args:
        timestampColumn (str): A data field.
        timezone (typing.Optional[str]): A data field.
    """
    
    timestampColumn: str
    timezone: typing.Optional[str]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TimestampInfo data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "timestampColumn": {
                    "type": "string"
                },
                "timezone": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                }
            },
            "required": [
                "timestampColumn",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TimestampInfo:
        """Validate and parse JSON data into an instance of TimestampInfo.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TimestampInfo.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TimestampInfo(
                timestampColumn=str(data["timestampColumn"]),
                timezone=(lambda v: v and str(v))(data.get("timezone", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing TimestampInfo",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "timestampColumn": str(self.timestampColumn),
            "timezone": (lambda v: v and str(v))(self.timezone)
        }


@dataclasses.dataclass(frozen=True)
class EventDescription:
    """Configuration to calculate event metadata for a table.
    
    Args:
        entities (typing.Dict[EntityId, str]): A data field.
        timestampInfo (TimestampInfo): A data field.
    """
    
    entities: typing.Dict[EntityId, str]
    timestampInfo: TimestampInfo
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EventDescription data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "entities": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "string"
                    }
                },
                "timestampInfo": TimestampInfo.json_schema()
            },
            "required": [
                "entities",
                "timestampInfo",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EventDescription:
        """Validate and parse JSON data into an instance of EventDescription.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EventDescription.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EventDescription(
                entities={
                    EntityId.from_json_key(k): str(v) for k, v in data["entities"].items()
                },
                timestampInfo=TimestampInfo.from_json(data["timestampInfo"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EventDescription",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "entities": {k.to_json_key(): str(v) for k, v in self.entities.items()},
            "timestampInfo": self.timestampInfo.to_json()
        }

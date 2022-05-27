"""Generated implementation of reports."""

# WARNING DO NOT EDIT
# This code was generated from reports.mcn

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


class ActionType(enum.Enum):
    """Actions to be reported."""
    Create = "create"
    Update = "update"
    Delete = "delete"
    
    @classmethod
    def json_schema(cls) -> dict:
        """JSON schema for 'ActionType'.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [
                        "create",
                        "update",
                        "delete",
                    ]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ActionType:
        """Validate and parse JSON data into an instance of ActionType.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ActionType.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ActionType(str(data['adt_type']))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing ActionType", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            JSON data ready to be serialised.
        """
        return {'adt_type': self.value}
    
    @classmethod
    def from_json_key(cls, data: str) -> ActionType:
        """Validate and parse a value from a JSON dictionary key.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of ActionType.
        """
        return ActionType(str(data))
    
    def to_json_key(self) -> str:
        """Serialised this instanse as a JSON string for use as a dictionary key.
        
        Returns:
            A JSON string ready to be used as a key.
        """
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class ReportAction:
    """Report of an action performed by a user.
    
    Reports are computed asynchronously after the fact.
    
    Args:
        timestamp (datetime.datetime): A data field.
        branch (str): A data field.
        user (str): A data field.
        action (ActionType): A data field.
        object_type (str): A data field.
        object_id (int): A data field.
    """
    
    timestamp: datetime.datetime
    branch: str
    user: str
    action: ActionType
    object_type: str
    object_id: int
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ReportAction data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "timestamp": {
                    "type": "string",
                    "format": "date-time"
                },
                "branch": {
                    "type": "string"
                },
                "user": {
                    "type": "string"
                },
                "action": ActionType.json_schema(),
                "object_type": {
                    "type": "string"
                },
                "object_id": {
                    "type": "integer"
                }
            },
            "required": [
                "timestamp",
                "branch",
                "user",
                "action",
                "object_type",
                "object_id",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ReportAction:
        """Validate and parse JSON data into an instance of ReportAction.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ReportAction.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ReportAction(
                timestamp=isodate.parse_datetime(data["timestamp"]),
                branch=str(data["branch"]),
                user=str(data["user"]),
                action=ActionType.from_json(data["action"]),
                object_type=str(data["object_type"]),
                object_id=int(data["object_id"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing ReportAction",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "timestamp": self.timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "branch": str(self.branch),
            "user": str(self.user),
            "action": self.action.to_json(),
            "object_type": str(self.object_type),
            "object_id": int(self.object_id)
        }

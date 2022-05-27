"""Generated implementation of event_window."""

# WARNING DO NOT EDIT
# This code was generated from event-window.mcn

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
class EventWindow(abc.ABC):
    """Window specific."""
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    @classmethod
    def json_schema(cls) -> EventWindow:
        """JSON schema for variant EventWindow.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        adt_types = [klass.ADT_TYPE for klass in cls.__subclasses__()]
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": adt_types
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EventWindow:
        """Validate and parse JSON data into an instance of EventWindow.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EventWindow.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            adt_type = data.get("adt_type", None)
            for klass in cls.__subclasses__():
                if klass.ADT_TYPE == adt_type:
                    return klass.from_json(data)
            raise ValueError("Unknown adt_type: '{ty}'".format(ty=adt_type))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing EventWindow", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class OpenWindow(EventWindow):
    """An open window."""
    
    ADT_TYPE: typing.ClassVar[str] = "openwindow"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for OpenWindow data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [cls.ADT_TYPE]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> OpenWindow:
        """Validate and parse JSON data into an instance of OpenWindow.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of OpenWindow.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return OpenWindow(
                
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing OpenWindow",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "adt_type": self.ADT_TYPE
        }


@dataclasses.dataclass(frozen=True)
class DayWindow(EventWindow):
    """A window defined in days.
    
    Args:
        days (int): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "daywindow"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    days: int
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for DayWindow data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [cls.ADT_TYPE]
                },
                "days": {
                    "type": "integer"
                }
            },
            "required": [
                "adt_type",
                "days",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> DayWindow:
        """Validate and parse JSON data into an instance of DayWindow.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of DayWindow.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return DayWindow(
                days=int(data["days"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing DayWindow",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "adt_type": self.ADT_TYPE,
            "days": int(self.days)
        }


@dataclasses.dataclass(frozen=True)
class RowWindow(EventWindow):
    """A window defined in rows.
    
    Args:
        rows (int): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "rowwindow"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    rows: int
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for RowWindow data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [cls.ADT_TYPE]
                },
                "rows": {
                    "type": "integer"
                }
            },
            "required": [
                "adt_type",
                "rows",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> RowWindow:
        """Validate and parse JSON data into an instance of RowWindow.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of RowWindow.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return RowWindow(
                rows=int(data["rows"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing RowWindow",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "adt_type": self.ADT_TYPE,
            "rows": int(self.rows)
        }

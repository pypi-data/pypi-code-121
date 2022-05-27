"""Generated implementation of source_reference."""

# WARNING DO NOT EDIT
# This code was generated from source-reference.mcn

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

from ..source import SourceId


@dataclasses.dataclass(frozen=True)
class SourceReference(abc.ABC):
    """A location to read input in a source data store.
    
    Args:
        sourceId (SourceId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    sourceId: SourceId
    
    @classmethod
    def json_schema(cls) -> SourceReference:
        """JSON schema for variant SourceReference.
        
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
    def from_json(cls, data: dict) -> SourceReference:
        """Validate and parse JSON data into an instance of SourceReference.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of SourceReference.
        
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
            logging.debug("Invalid JSON data received while parsing SourceReference", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class FolderSourceReference(SourceReference):
    """Read input from a folder in the given source.
    
    Args:
        sourceId (SourceId): A data field.
        folder (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "folder"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    sourceId: SourceId
    folder: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for FolderSourceReference data.
        
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
                "sourceId": SourceId.json_schema(),
                "folder": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "sourceId",
                "folder",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FolderSourceReference:
        """Validate and parse JSON data into an instance of FolderSourceReference.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FolderSourceReference.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FolderSourceReference(
                sourceId=SourceId.from_json(data["sourceId"]),
                folder=str(data["folder"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing FolderSourceReference",
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
            "sourceId": self.sourceId.to_json(),
            "folder": str(self.folder)
        }


@dataclasses.dataclass(frozen=True)
class TableSourceReference(SourceReference):
    """Read input from a table in the given source.
    
    Args:
        sourceId (SourceId): A data field.
        tableName (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "table"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    sourceId: SourceId
    tableName: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TableSourceReference data.
        
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
                "sourceId": SourceId.json_schema(),
                "tableName": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "sourceId",
                "tableName",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TableSourceReference:
        """Validate and parse JSON data into an instance of TableSourceReference.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableSourceReference.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableSourceReference(
                sourceId=SourceId.from_json(data["sourceId"]),
                tableName=str(data["tableName"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing TableSourceReference",
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
            "sourceId": self.sourceId.to_json(),
            "tableName": str(self.tableName)
        }


@dataclasses.dataclass(frozen=True)
class TopicSourceReference(SourceReference):
    """Read input from a topic in the given source.
    
    Args:
        sourceId (SourceId): A data field.
        topic (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "topic"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    sourceId: SourceId
    topic: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TopicSourceReference data.
        
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
                "sourceId": SourceId.json_schema(),
                "topic": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "sourceId",
                "topic",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TopicSourceReference:
        """Validate and parse JSON data into an instance of TopicSourceReference.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TopicSourceReference.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TopicSourceReference(
                sourceId=SourceId.from_json(data["sourceId"]),
                topic=str(data["topic"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing TopicSourceReference",
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
            "sourceId": self.sourceId.to_json(),
            "topic": str(self.topic)
        }

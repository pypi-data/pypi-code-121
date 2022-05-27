"""Generated implementation of table_creation_request."""

# WARNING DO NOT EDIT
# This code was generated from table-creation-request.mcn

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

from ..attribute import Attribute
from ..entity_mapping import EntityMappingId
from ..event_description import EventDescription
from ..feature_id import FeatureId
from ..label import Label
from ..source_reference import SourceReference
from ..table import TableId, TableName


@dataclasses.dataclass(frozen=True)
class TableCreationRequest(abc.ABC):
    """Request to create a new table containing source data.
    
    Args:
        attributes (typing.List[Attribute]): A data field.
        description (typing.Optional[str]): A data field.
        labels (typing.List[Label]): A data field.
        name (TableName): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    attributes: typing.List[Attribute]
    description: typing.Optional[str]
    labels: typing.List[Label]
    name: TableName
    
    @classmethod
    def json_schema(cls) -> TableCreationRequest:
        """JSON schema for variant TableCreationRequest.
        
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
    def from_json(cls, data: dict) -> TableCreationRequest:
        """Validate and parse JSON data into an instance of TableCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableCreationRequest.
        
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
            logging.debug("Invalid JSON data received while parsing TableCreationRequest", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class RootTableCreationRequest(TableCreationRequest):
    """Request to create a new physical table.
    
    Args:
        name (TableName): A data field.
        description (typing.Optional[str]): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        eventDescription (typing.Optional[EventDescription]): A data field.
        source (SourceReference): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "root"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: TableName
    description: typing.Optional[str]
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    eventDescription: typing.Optional[EventDescription]
    source: SourceReference
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for RootTableCreationRequest data.
        
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
                "name": TableName.json_schema(),
                "description": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "labels": {
                    "type": "array",
                    "item": Label.json_schema()
                },
                "attributes": {
                    "type": "array",
                    "item": Attribute.json_schema()
                },
                "eventDescription": {
                    "oneOf": [
                        {"type": "null"},
                        EventDescription.json_schema(),
                    ]
                },
                "source": SourceReference.json_schema()
            },
            "required": [
                "adt_type",
                "name",
                "labels",
                "attributes",
                "source",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> RootTableCreationRequest:
        """Validate and parse JSON data into an instance of RootTableCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of RootTableCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return RootTableCreationRequest(
                name=TableName.from_json(data["name"]),
                description=(lambda v: v and str(v))(data.get("description", None)),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                eventDescription=(
                    lambda v: v and EventDescription.from_json(v)
                )(
                    data.get("eventDescription", None)
                ),
                source=SourceReference.from_json(data["source"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing RootTableCreationRequest",
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
            "name": self.name.to_json(),
            "description": (lambda v: v and str(v))(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "eventDescription": (lambda v: v and v.to_json())(self.eventDescription),
            "source": self.source.to_json()
        }


@dataclasses.dataclass(frozen=True)
class ViewTableCreationRequest(TableCreationRequest):
    """Request to create a new view table.
    
    Args:
        name (TableName): A data field.
        description (typing.Optional[str]): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        eventDescription (typing.Optional[EventDescription]): A data field.
        expression (str): A data field.
        sources (typing.List[TableId]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "view"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: TableName
    description: typing.Optional[str]
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    eventDescription: typing.Optional[EventDescription]
    expression: str
    sources: typing.List[TableId]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ViewTableCreationRequest data.
        
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
                "name": TableName.json_schema(),
                "description": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "labels": {
                    "type": "array",
                    "item": Label.json_schema()
                },
                "attributes": {
                    "type": "array",
                    "item": Attribute.json_schema()
                },
                "eventDescription": {
                    "oneOf": [
                        {"type": "null"},
                        EventDescription.json_schema(),
                    ]
                },
                "expression": {
                    "type": "string"
                },
                "sources": {
                    "type": "array",
                    "item": TableId.json_schema()
                }
            },
            "required": [
                "adt_type",
                "name",
                "labels",
                "attributes",
                "expression",
                "sources",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ViewTableCreationRequest:
        """Validate and parse JSON data into an instance of ViewTableCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ViewTableCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ViewTableCreationRequest(
                name=TableName.from_json(data["name"]),
                description=(lambda v: v and str(v))(data.get("description", None)),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                eventDescription=(
                    lambda v: v and EventDescription.from_json(v)
                )(
                    data.get("eventDescription", None)
                ),
                expression=str(data["expression"]),
                sources=[TableId.from_json(v) for v in data["sources"]],
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing ViewTableCreationRequest",
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
            "name": self.name.to_json(),
            "description": (lambda v: v and str(v))(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "eventDescription": (lambda v: v and v.to_json())(self.eventDescription),
            "expression": str(self.expression),
            "sources": [v.to_json() for v in self.sources]
        }


@dataclasses.dataclass(frozen=True)
class PivotTableCreationRequest(TableCreationRequest):
    """Request to create a new pivot table.
    
    Args:
        name (TableName): A data field.
        description (typing.Optional[str]): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        entityMapping (EntityMappingId): A data field.
        extraFeatures (typing.List[FeatureId]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "pivot"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: TableName
    description: typing.Optional[str]
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    entityMapping: EntityMappingId
    extraFeatures: typing.List[FeatureId]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for PivotTableCreationRequest data.
        
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
                "name": TableName.json_schema(),
                "description": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "labels": {
                    "type": "array",
                    "item": Label.json_schema()
                },
                "attributes": {
                    "type": "array",
                    "item": Attribute.json_schema()
                },
                "entityMapping": EntityMappingId.json_schema(),
                "extraFeatures": {
                    "type": "array",
                    "item": FeatureId.json_schema()
                }
            },
            "required": [
                "adt_type",
                "name",
                "labels",
                "attributes",
                "entityMapping",
                "extraFeatures",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> PivotTableCreationRequest:
        """Validate and parse JSON data into an instance of PivotTableCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of PivotTableCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return PivotTableCreationRequest(
                name=TableName.from_json(data["name"]),
                description=(lambda v: v and str(v))(data.get("description", None)),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                entityMapping=EntityMappingId.from_json(data["entityMapping"]),
                extraFeatures=[FeatureId.from_json(v) for v in data["extraFeatures"]],
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing PivotTableCreationRequest",
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
            "name": self.name.to_json(),
            "description": (lambda v: v and str(v))(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "entityMapping": self.entityMapping.to_json(),
            "extraFeatures": [v.to_json() for v in self.extraFeatures]
        }

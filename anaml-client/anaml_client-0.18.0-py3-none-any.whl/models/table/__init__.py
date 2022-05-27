"""Generated implementation of table."""

# WARNING DO NOT EDIT
# This code was generated from table.mcn

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
from ..entity import EntityId
from ..entity_mapping import EntityMappingId
from ..event_description import EventDescription
from ..feature_id import FeatureId
from ..label import Label
from ..source_reference import SourceReference


@dataclasses.dataclass(frozen=True)
class TableId:
    """Unique identifier for a table.
    
    Args:
        value (int): A data field.
    """
    
    value: int
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    def __int__(self) -> int:
        """Return an int of the wrapped value."""
        return int(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TableId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TableId:
        """Validate and parse JSON data into an instance of TableId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing TableId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> TableId:
        """Parse a JSON string such as a dictionary key."""
        return TableId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class TableName:
    """Unique name for a table.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TableName data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TableName:
        """Validate and parse JSON data into an instance of TableName.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableName.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableName(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing TableName", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> TableName:
        """Parse a JSON string such as a dictionary key."""
        return TableName(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class TableVersionId:
    """Unique identifier of a specific version of a table.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TableVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TableVersionId:
        """Validate and parse JSON data into an instance of TableVersionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing TableVersionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> TableVersionId:
        """Parse a JSON string such as a dictionary key."""
        return TableVersionId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class Table(abc.ABC):
    """Definition of a table containing source data.
    
    Args:
        attributes (typing.List[Attribute]): A data field.
        description (typing.Optional[str]): A data field.
        id (TableId): A data field.
        labels (typing.List[Label]): A data field.
        name (TableName): A data field.
        version (TableVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    attributes: typing.List[Attribute]
    description: typing.Optional[str]
    id: TableId
    labels: typing.List[Label]
    name: TableName
    version: TableVersionId
    
    @classmethod
    def json_schema(cls) -> Table:
        """JSON schema for variant Table.
        
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
    def from_json(cls, data: dict) -> Table:
        """Validate and parse JSON data into an instance of Table.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Table.
        
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
            logging.debug("Invalid JSON data received while parsing Table", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class RootTable(Table):
    """A physical table.
    
    Args:
        id (TableId): A data field.
        name (TableName): A data field.
        description (typing.Optional[str]): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        eventDescription (typing.Optional[EventDescription]): A data field.
        source (SourceReference): A data field.
        version (TableVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "root"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: TableId
    name: TableName
    description: typing.Optional[str]
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    eventDescription: typing.Optional[EventDescription]
    source: SourceReference
    version: TableVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for RootTable data.
        
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
                "id": TableId.json_schema(),
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
                "source": SourceReference.json_schema(),
                "version": TableVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "labels",
                "attributes",
                "source",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> RootTable:
        """Validate and parse JSON data into an instance of RootTable.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of RootTable.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return RootTable(
                id=TableId.from_json(data["id"]),
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
                version=TableVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing RootTable",
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
            "id": self.id.to_json(),
            "name": self.name.to_json(),
            "description": (lambda v: v and str(v))(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "eventDescription": (lambda v: v and v.to_json())(self.eventDescription),
            "source": self.source.to_json(),
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class ViewTable(Table):
    """A view table defined in terms of other tables.
    
    Args:
        id (TableId): A data field.
        name (TableName): A data field.
        description (typing.Optional[str]): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        eventDescription (typing.Optional[EventDescription]): A data field.
        expression (str): A data field.
        sources (typing.List[TableId]): A data field.
        version (TableVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "view"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: TableId
    name: TableName
    description: typing.Optional[str]
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    eventDescription: typing.Optional[EventDescription]
    expression: str
    sources: typing.List[TableId]
    version: TableVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ViewTable data.
        
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
                "id": TableId.json_schema(),
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
                },
                "version": TableVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "labels",
                "attributes",
                "expression",
                "sources",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ViewTable:
        """Validate and parse JSON data into an instance of ViewTable.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ViewTable.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ViewTable(
                id=TableId.from_json(data["id"]),
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
                version=TableVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing ViewTable",
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
            "id": self.id.to_json(),
            "name": self.name.to_json(),
            "description": (lambda v: v and str(v))(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "eventDescription": (lambda v: v and v.to_json())(self.eventDescription),
            "expression": str(self.expression),
            "sources": [v.to_json() for v in self.sources],
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class PivotTable(Table):
    """A pivot table.
    
    Args:
        id (TableId): A data field.
        name (TableName): A data field.
        description (typing.Optional[str]): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        entityMapping (EntityMappingId): A data field.
        extraFeatures (typing.List[FeatureId]): A data field.
        version (TableVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "pivot"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: TableId
    name: TableName
    description: typing.Optional[str]
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    entityMapping: EntityMappingId
    extraFeatures: typing.List[FeatureId]
    version: TableVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for PivotTable data.
        
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
                "id": TableId.json_schema(),
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
                },
                "version": TableVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "labels",
                "attributes",
                "entityMapping",
                "extraFeatures",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> PivotTable:
        """Validate and parse JSON data into an instance of PivotTable.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of PivotTable.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return PivotTable(
                id=TableId.from_json(data["id"]),
                name=TableName.from_json(data["name"]),
                description=(lambda v: v and str(v))(data.get("description", None)),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                entityMapping=EntityMappingId.from_json(data["entityMapping"]),
                extraFeatures=[FeatureId.from_json(v) for v in data["extraFeatures"]],
                version=TableVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing PivotTable",
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
            "id": self.id.to_json(),
            "name": self.name.to_json(),
            "description": (lambda v: v and str(v))(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "entityMapping": self.entityMapping.to_json(),
            "extraFeatures": [v.to_json() for v in self.extraFeatures],
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class EventStoreTable(Table):
    """An event store table.
    
    Args:
        id (TableId): A data field.
        name (TableName): A data field.
        description (typing.Optional[str]): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        topic (str): A data field.
        entity (EntityId): A data field.
        version (TableVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "eventstore"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: TableId
    name: TableName
    description: typing.Optional[str]
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    topic: str
    entity: EntityId
    version: TableVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EventStoreTable data.
        
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
                "id": TableId.json_schema(),
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
                "topic": {
                    "type": "string"
                },
                "entity": EntityId.json_schema(),
                "version": TableVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "labels",
                "attributes",
                "topic",
                "entity",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EventStoreTable:
        """Validate and parse JSON data into an instance of EventStoreTable.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EventStoreTable.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EventStoreTable(
                id=TableId.from_json(data["id"]),
                name=TableName.from_json(data["name"]),
                description=(lambda v: v and str(v))(data.get("description", None)),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                topic=str(data["topic"]),
                entity=EntityId.from_json(data["entity"]),
                version=TableVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EventStoreTable",
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
            "id": self.id.to_json(),
            "name": self.name.to_json(),
            "description": (lambda v: v and str(v))(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "topic": str(self.topic),
            "entity": self.entity.to_json(),
            "version": self.version.to_json()
        }

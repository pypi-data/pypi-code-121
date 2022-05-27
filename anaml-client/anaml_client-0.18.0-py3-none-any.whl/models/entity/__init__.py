"""Generated implementation of entity."""

# WARNING DO NOT EDIT
# This code was generated from entity.mcn

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
from ..label import Label


@dataclasses.dataclass(frozen=True)
class EntityId:
    """Unique identifier of a data entity.
    
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
        """Return the JSON schema for EntityId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EntityId:
        """Validate and parse JSON data into an instance of EntityId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EntityId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EntityId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing EntityId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> EntityId:
        """Parse a JSON string such as a dictionary key."""
        return EntityId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class EntityName:
    """Unique name of a data entity.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EntityName data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EntityName:
        """Validate and parse JSON data into an instance of EntityName.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EntityName.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EntityName(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing EntityName", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> EntityName:
        """Parse a JSON string such as a dictionary key."""
        return EntityName(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class EntityVersionId:
    """Unique identifier of a specific version of a data entity.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EntityVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EntityVersionId:
        """Validate and parse JSON data into an instance of EntityVersionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EntityVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EntityVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing EntityVersionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> EntityVersionId:
        """Parse a JSON string such as a dictionary key."""
        return EntityVersionId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class Entity(abc.ABC):
    """Definition of a data entity.
    
    Args:
        attributes (typing.List[Attribute]): A data field.
        description (str): A data field.
        id (EntityId): A data field.
        labels (typing.List[Label]): A data field.
        name (EntityName): A data field.
        version (EntityVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    attributes: typing.List[Attribute]
    description: str
    id: EntityId
    labels: typing.List[Label]
    name: EntityName
    version: EntityVersionId
    
    @classmethod
    def json_schema(cls) -> Entity:
        """JSON schema for variant Entity.
        
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
    def from_json(cls, data: dict) -> Entity:
        """Validate and parse JSON data into an instance of Entity.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Entity.
        
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
            logging.debug("Invalid JSON data received while parsing Entity", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class BaseEntity(Entity):
    """Base entity.

    Args:
        id (EntityId): A data field.
        name (EntityName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        defaultColumn (str): A data field.
        version (EntityVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "base"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: EntityId
    name: EntityName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    defaultColumn: str
    version: EntityVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for BaseEntity data.
        
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
                "id": EntityId.json_schema(),
                "name": EntityName.json_schema(),
                "description": {
                    "type": "string"
                },
                "labels": {
                    "type": "array",
                    "item": Label.json_schema()
                },
                "attributes": {
                    "type": "array",
                    "item": Attribute.json_schema()
                },
                "defaultColumn": {
                    "type": "string"
                },
                "version": EntityVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "defaultColumn",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> BaseEntity:
        """Validate and parse JSON data into an instance of BaseEntity.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of BaseEntity.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return BaseEntity(
                id=EntityId.from_json(data["id"]),
                name=EntityName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                defaultColumn=str(data["defaultColumn"]),
                version=EntityVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing BaseEntity",
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
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "defaultColumn": str(self.defaultColumn),
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class CompositeEntity(Entity):
    """Composite entity.

    Args:
        id (EntityId): A data field.
        name (EntityName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        entities (typing.List[EntityId]): A data field.
        version (EntityVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "composite"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: EntityId
    name: EntityName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    entities: typing.List[EntityId]
    version: EntityVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for CompositeEntity data.
        
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
                "id": EntityId.json_schema(),
                "name": EntityName.json_schema(),
                "description": {
                    "type": "string"
                },
                "labels": {
                    "type": "array",
                    "item": Label.json_schema()
                },
                "attributes": {
                    "type": "array",
                    "item": Attribute.json_schema()
                },
                "entities": {
                    "type": "array",
                    "item": EntityId.json_schema()
                },
                "version": EntityVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "entities",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> CompositeEntity:
        """Validate and parse JSON data into an instance of CompositeEntity.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of CompositeEntity.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return CompositeEntity(
                id=EntityId.from_json(data["id"]),
                name=EntityName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                entities=[EntityId.from_json(v) for v in data["entities"]],
                version=EntityVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing CompositeEntity",
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
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "entities": [v.to_json() for v in self.entities],
            "version": self.version.to_json()
        }

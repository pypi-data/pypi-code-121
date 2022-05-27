"""Generated implementation of entity_population."""

# WARNING DO NOT EDIT
# This code was generated from entity-population.mcn

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
from ..label import Label
from ..table import TableId


@dataclasses.dataclass(frozen=True)
class EntityPopulationId:
    """Unique identifier for an entity population.
    
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
        """Return the JSON schema for EntityPopulationId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EntityPopulationId:
        """Validate and parse JSON data into an instance of EntityPopulationId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EntityPopulationId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EntityPopulationId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing EntityPopulationId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> EntityPopulationId:
        """Parse a JSON string such as a dictionary key."""
        return EntityPopulationId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class EntityPopulationName:
    """Unique name of an entity population.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EntityPopulationName data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EntityPopulationName:
        """Validate and parse JSON data into an instance of EntityPopulationName.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EntityPopulationName.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EntityPopulationName(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing EntityPopulationName", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> EntityPopulationName:
        """Parse a JSON string such as a dictionary key."""
        return EntityPopulationName(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class EntityPopulationVersionId:
    """Unique identifier for versions of an entity population.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EntityPopulationVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EntityPopulationVersionId:
        """Validate and parse JSON data into an instance of EntityPopulationVersionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EntityPopulationVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EntityPopulationVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing EntityPopulationVersionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> EntityPopulationVersionId:
        """Parse a JSON string such as a dictionary key."""
        return EntityPopulationVersionId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class EntityPopulation:
    """The definition of a set of entities to generate features for and from when.
    
    Args:
        id (EntityPopulationId): A data field.
        name (EntityPopulationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        entity (EntityId): A data field.
        sources (typing.List[TableId]): A data field.
        expression (str): A data field.
        version (EntityPopulationVersionId): A data field.
    """
    
    id: EntityPopulationId
    name: EntityPopulationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    entity: EntityId
    sources: typing.List[TableId]
    expression: str
    version: EntityPopulationVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EntityPopulation data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": EntityPopulationId.json_schema(),
                "name": EntityPopulationName.json_schema(),
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
                "entity": EntityId.json_schema(),
                "sources": {
                    "type": "array",
                    "item": TableId.json_schema()
                },
                "expression": {
                    "type": "string"
                },
                "version": EntityPopulationVersionId.json_schema()
            },
            "required": [
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "entity",
                "sources",
                "expression",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EntityPopulation:
        """Validate and parse JSON data into an instance of EntityPopulation.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EntityPopulation.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EntityPopulation(
                id=EntityPopulationId.from_json(data["id"]),
                name=EntityPopulationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                entity=EntityId.from_json(data["entity"]),
                sources=[TableId.from_json(v) for v in data["sources"]],
                expression=str(data["expression"]),
                version=EntityPopulationVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EntityPopulation",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "id": self.id.to_json(),
            "name": self.name.to_json(),
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "entity": self.entity.to_json(),
            "sources": [v.to_json() for v in self.sources],
            "expression": str(self.expression),
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class EntityPopulationCreationRequest:
    """The definition of a set of entities to generate features for and from when.
    
    Args:
        name (EntityPopulationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        entity (EntityId): A data field.
        sources (typing.List[TableId]): A data field.
        expression (str): A data field.
    """
    
    name: EntityPopulationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    entity: EntityId
    sources: typing.List[TableId]
    expression: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EntityPopulationCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "name": EntityPopulationName.json_schema(),
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
                "entity": EntityId.json_schema(),
                "sources": {
                    "type": "array",
                    "item": TableId.json_schema()
                },
                "expression": {
                    "type": "string"
                }
            },
            "required": [
                "name",
                "description",
                "labels",
                "attributes",
                "entity",
                "sources",
                "expression",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EntityPopulationCreationRequest:
        """Validate and parse JSON data into an instance of EntityPopulationCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EntityPopulationCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EntityPopulationCreationRequest(
                name=EntityPopulationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                entity=EntityId.from_json(data["entity"]),
                sources=[TableId.from_json(v) for v in data["sources"]],
                expression=str(data["expression"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EntityPopulationCreationRequest",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "name": self.name.to_json(),
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "entity": self.entity.to_json(),
            "sources": [v.to_json() for v in self.sources],
            "expression": str(self.expression)
        }

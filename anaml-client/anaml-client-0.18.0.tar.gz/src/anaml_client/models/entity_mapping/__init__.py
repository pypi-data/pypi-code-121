"""Generated implementation of entity_mapping."""

# WARNING DO NOT EDIT
# This code was generated from entity-mapping.mcn

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
from ..feature_id import FeatureId


@dataclasses.dataclass(frozen=True)
class EntityMappingId:
    """Unique identifier for entity mappings.
    
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
        """Return the JSON schema for EntityMappingId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EntityMappingId:
        """Validate and parse JSON data into an instance of EntityMappingId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EntityMappingId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EntityMappingId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing EntityMappingId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> EntityMappingId:
        """Parse a JSON string such as a dictionary key."""
        return EntityMappingId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class EntityMappingVersionId:
    """Unique identifier for versions of an entity mapping.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EntityMappingVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EntityMappingVersionId:
        """Validate and parse JSON data into an instance of EntityMappingVersionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EntityMappingVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EntityMappingVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing EntityMappingVersionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> EntityMappingVersionId:
        """Parse a JSON string such as a dictionary key."""
        return EntityMappingVersionId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class EntityMapping:
    """A mapping defined between between two entities.
    
    Args:
        id (EntityMappingId): A data field.
        from_ (EntityId): A data field.
        to (EntityId): A data field.
        mapping (FeatureId): A data field.
        version (EntityMappingVersionId): A data field.
    """
    
    id: EntityMappingId
    from_: EntityId
    to: EntityId
    mapping: FeatureId
    version: EntityMappingVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EntityMapping data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": EntityMappingId.json_schema(),
                "from": EntityId.json_schema(),
                "to": EntityId.json_schema(),
                "mapping": FeatureId.json_schema(),
                "version": EntityMappingVersionId.json_schema()
            },
            "required": [
                "id",
                "from",
                "to",
                "mapping",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EntityMapping:
        """Validate and parse JSON data into an instance of EntityMapping.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EntityMapping.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EntityMapping(
                id=EntityMappingId.from_json(data["id"]),
                from_=EntityId.from_json(data["from"]),
                to=EntityId.from_json(data["to"]),
                mapping=FeatureId.from_json(data["mapping"]),
                version=EntityMappingVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EntityMapping",
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
            "from": self.from_.to_json(),
            "to": self.to.to_json(),
            "mapping": self.mapping.to_json(),
            "version": self.version.to_json()
        }

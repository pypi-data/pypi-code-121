"""Generated implementation of feature_set."""

# WARNING DO NOT EDIT
# This code was generated from feature-set.mcn

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
from ..feature_id import FeatureId
from ..label import Label


@dataclasses.dataclass(frozen=True)
class FeatureSetId:
    """Unique identifier of a feature set.
    
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
        """Return the JSON schema for FeatureSetId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FeatureSetId:
        """Validate and parse JSON data into an instance of FeatureSetId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureSetId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureSetId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing FeatureSetId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> FeatureSetId:
        """Parse a JSON string such as a dictionary key."""
        return FeatureSetId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class FeatureSetName:
    """Unique name of a feature set.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for FeatureSetName data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FeatureSetName:
        """Validate and parse JSON data into an instance of FeatureSetName.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureSetName.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureSetName(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing FeatureSetName", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> FeatureSetName:
        """Parse a JSON string such as a dictionary key."""
        return FeatureSetName(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class FeatureSetVersionId:
    """Unique identifier of a version of a feature set.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for FeatureSetVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FeatureSetVersionId:
        """Validate and parse JSON data into an instance of FeatureSetVersionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureSetVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureSetVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing FeatureSetVersionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> FeatureSetVersionId:
        """Parse a JSON string such as a dictionary key."""
        return FeatureSetVersionId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class FeatureSet:
    """A collection of related features.
    
    Args:
        id (FeatureSetId): A data field.
        name (FeatureSetName): A data field.
        entity (EntityId): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        features (typing.List[FeatureId]): A data field.
        version (FeatureSetVersionId): A data field.
    """
    
    id: FeatureSetId
    name: FeatureSetName
    entity: EntityId
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    features: typing.List[FeatureId]
    version: FeatureSetVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for FeatureSet data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": FeatureSetId.json_schema(),
                "name": FeatureSetName.json_schema(),
                "entity": EntityId.json_schema(),
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
                "features": {
                    "type": "array",
                    "item": FeatureId.json_schema()
                },
                "version": FeatureSetVersionId.json_schema()
            },
            "required": [
                "id",
                "name",
                "entity",
                "description",
                "labels",
                "attributes",
                "features",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FeatureSet:
        """Validate and parse JSON data into an instance of FeatureSet.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureSet.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureSet(
                id=FeatureSetId.from_json(data["id"]),
                name=FeatureSetName.from_json(data["name"]),
                entity=EntityId.from_json(data["entity"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                features=[FeatureId.from_json(v) for v in data["features"]],
                version=FeatureSetVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing FeatureSet",
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
            "entity": self.entity.to_json(),
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "features": [v.to_json() for v in self.features],
            "version": self.version.to_json()
        }

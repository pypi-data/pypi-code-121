"""Generated implementation of projects."""

# WARNING DO NOT EDIT
# This code was generated from projects.mcn

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
from ..feature_set import FeatureSetId
from ..feature_store import FeatureStoreId
from ..label import Label
from ..source import SourceId
from ..table import TableId


@dataclasses.dataclass(frozen=True)
class ProjectId:
    """Unique identifier for a project.
    
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
        """Return the JSON schema for ProjectId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ProjectId:
        """Validate and parse JSON data into an instance of ProjectId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ProjectId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ProjectId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing ProjectId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> ProjectId:
        """Parse a JSON string such as a dictionary key."""
        return ProjectId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class ProjectName:
    """Unique name of a project.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ProjectName data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ProjectName:
        """Validate and parse JSON data into an instance of ProjectName.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ProjectName.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ProjectName(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing ProjectName", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> ProjectName:
        """Parse a JSON string such as a dictionary key."""
        return ProjectName(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class ProjectVersionId:
    """Unique identifier for versions of a project.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ProjectVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ProjectVersionId:
        """Validate and parse JSON data into an instance of ProjectVersionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ProjectVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ProjectVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing ProjectVersionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> ProjectVersionId:
        """Parse a JSON string such as a dictionary key."""
        return ProjectVersionId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class Project:
    """The definition of a project.
    
    Args:
        id (ProjectId): A data field.
        name (ProjectName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        branches (typing.List[str]): A data field.
        entities (typing.List[EntityId]): A data field.
        features (typing.List[FeatureId]): A data field.
        featureSets (typing.List[FeatureSetId]): A data field.
        featureStores (typing.List[FeatureStoreId]): A data field.
        sources (typing.List[SourceId]): A data field.
        tables (typing.List[TableId]): A data field.
        version (ProjectVersionId): A data field.
    """
    
    id: ProjectId
    name: ProjectName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    branches: typing.List[str]
    entities: typing.List[EntityId]
    features: typing.List[FeatureId]
    featureSets: typing.List[FeatureSetId]
    featureStores: typing.List[FeatureStoreId]
    sources: typing.List[SourceId]
    tables: typing.List[TableId]
    version: ProjectVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for Project data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": ProjectId.json_schema(),
                "name": ProjectName.json_schema(),
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
                "branches": {
                    "type": "array",
                    "item": {"type": "string"}
                },
                "entities": {
                    "type": "array",
                    "item": EntityId.json_schema()
                },
                "features": {
                    "type": "array",
                    "item": FeatureId.json_schema()
                },
                "featureSets": {
                    "type": "array",
                    "item": FeatureSetId.json_schema()
                },
                "featureStores": {
                    "type": "array",
                    "item": FeatureStoreId.json_schema()
                },
                "sources": {
                    "type": "array",
                    "item": SourceId.json_schema()
                },
                "tables": {
                    "type": "array",
                    "item": TableId.json_schema()
                },
                "version": ProjectVersionId.json_schema()
            },
            "required": [
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "branches",
                "entities",
                "features",
                "featureSets",
                "featureStores",
                "sources",
                "tables",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> Project:
        """Validate and parse JSON data into an instance of Project.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Project.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return Project(
                id=ProjectId.from_json(data["id"]),
                name=ProjectName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                branches=[str(v) for v in data["branches"]],
                entities=[EntityId.from_json(v) for v in data["entities"]],
                features=[FeatureId.from_json(v) for v in data["features"]],
                featureSets=[FeatureSetId.from_json(v) for v in data["featureSets"]],
                featureStores=[FeatureStoreId.from_json(v) for v in data["featureStores"]],
                sources=[SourceId.from_json(v) for v in data["sources"]],
                tables=[TableId.from_json(v) for v in data["tables"]],
                version=ProjectVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing Project",
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
            "branches": [str(v) for v in self.branches],
            "entities": [v.to_json() for v in self.entities],
            "features": [v.to_json() for v in self.features],
            "featureSets": [v.to_json() for v in self.featureSets],
            "featureStores": [v.to_json() for v in self.featureStores],
            "sources": [v.to_json() for v in self.sources],
            "tables": [v.to_json() for v in self.tables],
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class ProjectCreationRequest:
    """The definition of a project.
    
    Args:
        name (ProjectName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        branches (typing.List[str]): A data field.
        entities (typing.List[EntityId]): A data field.
        features (typing.List[FeatureId]): A data field.
        featureSets (typing.List[FeatureSetId]): A data field.
        featureStores (typing.List[FeatureStoreId]): A data field.
        sources (typing.List[SourceId]): A data field.
        tables (typing.List[TableId]): A data field.
    """
    
    name: ProjectName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    branches: typing.List[str]
    entities: typing.List[EntityId]
    features: typing.List[FeatureId]
    featureSets: typing.List[FeatureSetId]
    featureStores: typing.List[FeatureStoreId]
    sources: typing.List[SourceId]
    tables: typing.List[TableId]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ProjectCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "name": ProjectName.json_schema(),
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
                "branches": {
                    "type": "array",
                    "item": {"type": "string"}
                },
                "entities": {
                    "type": "array",
                    "item": EntityId.json_schema()
                },
                "features": {
                    "type": "array",
                    "item": FeatureId.json_schema()
                },
                "featureSets": {
                    "type": "array",
                    "item": FeatureSetId.json_schema()
                },
                "featureStores": {
                    "type": "array",
                    "item": FeatureStoreId.json_schema()
                },
                "sources": {
                    "type": "array",
                    "item": SourceId.json_schema()
                },
                "tables": {
                    "type": "array",
                    "item": TableId.json_schema()
                }
            },
            "required": [
                "name",
                "description",
                "labels",
                "attributes",
                "branches",
                "entities",
                "features",
                "featureSets",
                "featureStores",
                "sources",
                "tables",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ProjectCreationRequest:
        """Validate and parse JSON data into an instance of ProjectCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ProjectCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ProjectCreationRequest(
                name=ProjectName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                branches=[str(v) for v in data["branches"]],
                entities=[EntityId.from_json(v) for v in data["entities"]],
                features=[FeatureId.from_json(v) for v in data["features"]],
                featureSets=[FeatureSetId.from_json(v) for v in data["featureSets"]],
                featureStores=[FeatureStoreId.from_json(v) for v in data["featureStores"]],
                sources=[SourceId.from_json(v) for v in data["sources"]],
                tables=[TableId.from_json(v) for v in data["tables"]],
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing ProjectCreationRequest",
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
            "branches": [str(v) for v in self.branches],
            "entities": [v.to_json() for v in self.entities],
            "features": [v.to_json() for v in self.features],
            "featureSets": [v.to_json() for v in self.featureSets],
            "featureStores": [v.to_json() for v in self.featureStores],
            "sources": [v.to_json() for v in self.sources],
            "tables": [v.to_json() for v in self.tables]
        }

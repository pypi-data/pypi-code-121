"""Generated implementation of commit."""

# WARNING DO NOT EDIT
# This code was generated from commit.mcn

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
from ..entity_mapping import EntityMappingId
from ..entity_population import EntityPopulationId
from ..feature_id import FeatureId
from ..feature_set import FeatureSetId
from ..feature_template import TemplateId
from ..table import TableId
from ..user import UserId


@dataclasses.dataclass(frozen=True)
class CommitId:
    """Unique identifier of a commit.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for CommitId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> CommitId:
        """Validate and parse JSON data into an instance of CommitId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of CommitId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return CommitId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing CommitId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> CommitId:
        """Parse a JSON string such as a dictionary key."""
        return CommitId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class Commit:
    """Metadata of a commit.
    
    Args:
        id (CommitId): A data field.
        parents (typing.List[CommitId]): A data field.
        createdAt (datetime.datetime): A data field.
        author (UserId): A data field.
        description (typing.Optional[str]): A data field.
    """
    
    id: CommitId
    parents: typing.List[CommitId]
    createdAt: datetime.datetime
    author: UserId
    description: typing.Optional[str]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for Commit data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": CommitId.json_schema(),
                "parents": {
                    "type": "array",
                    "item": CommitId.json_schema()
                },
                "createdAt": {
                    "type": "string",
                    "format": "date-time"
                },
                "author": UserId.json_schema(),
                "description": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                }
            },
            "required": [
                "id",
                "parents",
                "createdAt",
                "author",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> Commit:
        """Validate and parse JSON data into an instance of Commit.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Commit.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return Commit(
                id=CommitId.from_json(data["id"]),
                parents=[CommitId.from_json(v) for v in data["parents"]],
                createdAt=isodate.parse_datetime(data["createdAt"]),
                author=UserId.from_json(data["author"]),
                description=(lambda v: v and str(v))(data.get("description", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing Commit",
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
            "parents": [v.to_json() for v in self.parents],
            "createdAt": self.createdAt.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "author": self.author.to_json(),
            "description": (lambda v: v and str(v))(self.description)
        }


@dataclasses.dataclass(frozen=True)
class EntityCreatedUpdated:
    """Entity created and updated timestamps.
    
    Args:
        id (EntityId): A data field.
        created (datetime.datetime): A data field.
        updated (datetime.datetime): A data field.
    """
    
    id: EntityId
    created: datetime.datetime
    updated: datetime.datetime
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EntityCreatedUpdated data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": EntityId.json_schema(),
                "created": {
                    "type": "string",
                    "format": "date-time"
                },
                "updated": {
                    "type": "string",
                    "format": "date-time"
                }
            },
            "required": [
                "id",
                "created",
                "updated",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EntityCreatedUpdated:
        """Validate and parse JSON data into an instance of EntityCreatedUpdated.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EntityCreatedUpdated.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EntityCreatedUpdated(
                id=EntityId.from_json(data["id"]),
                created=isodate.parse_datetime(data["created"]),
                updated=isodate.parse_datetime(data["updated"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EntityCreatedUpdated",
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
            "created": self.created.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "updated": self.updated.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        }


@dataclasses.dataclass(frozen=True)
class EntityMappingCreatedUpdated:
    """EntityMapping created and updated timestamps.
    
    Args:
        id (EntityMappingId): A data field.
        created (datetime.datetime): A data field.
        updated (datetime.datetime): A data field.
    """
    
    id: EntityMappingId
    created: datetime.datetime
    updated: datetime.datetime
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EntityMappingCreatedUpdated data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": EntityMappingId.json_schema(),
                "created": {
                    "type": "string",
                    "format": "date-time"
                },
                "updated": {
                    "type": "string",
                    "format": "date-time"
                }
            },
            "required": [
                "id",
                "created",
                "updated",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EntityMappingCreatedUpdated:
        """Validate and parse JSON data into an instance of EntityMappingCreatedUpdated.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EntityMappingCreatedUpdated.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EntityMappingCreatedUpdated(
                id=EntityMappingId.from_json(data["id"]),
                created=isodate.parse_datetime(data["created"]),
                updated=isodate.parse_datetime(data["updated"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EntityMappingCreatedUpdated",
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
            "created": self.created.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "updated": self.updated.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        }


@dataclasses.dataclass(frozen=True)
class EntityPopulationCreatedUpdated:
    """EntityPopulation created and updated timestamps.
    
    Args:
        id (EntityPopulationId): A data field.
        created (datetime.datetime): A data field.
        updated (datetime.datetime): A data field.
    """
    
    id: EntityPopulationId
    created: datetime.datetime
    updated: datetime.datetime
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EntityPopulationCreatedUpdated data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": EntityPopulationId.json_schema(),
                "created": {
                    "type": "string",
                    "format": "date-time"
                },
                "updated": {
                    "type": "string",
                    "format": "date-time"
                }
            },
            "required": [
                "id",
                "created",
                "updated",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EntityPopulationCreatedUpdated:
        """Validate and parse JSON data into an instance of EntityPopulationCreatedUpdated.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EntityPopulationCreatedUpdated.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EntityPopulationCreatedUpdated(
                id=EntityPopulationId.from_json(data["id"]),
                created=isodate.parse_datetime(data["created"]),
                updated=isodate.parse_datetime(data["updated"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EntityPopulationCreatedUpdated",
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
            "created": self.created.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "updated": self.updated.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        }


@dataclasses.dataclass(frozen=True)
class FeatureCreatedUpdated:
    """Feature created and updated timestamps.
    
    Args:
        id (FeatureId): A data field.
        created (datetime.datetime): A data field.
        updated (datetime.datetime): A data field.
    """
    
    id: FeatureId
    created: datetime.datetime
    updated: datetime.datetime
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for FeatureCreatedUpdated data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": FeatureId.json_schema(),
                "created": {
                    "type": "string",
                    "format": "date-time"
                },
                "updated": {
                    "type": "string",
                    "format": "date-time"
                }
            },
            "required": [
                "id",
                "created",
                "updated",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FeatureCreatedUpdated:
        """Validate and parse JSON data into an instance of FeatureCreatedUpdated.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureCreatedUpdated.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureCreatedUpdated(
                id=FeatureId.from_json(data["id"]),
                created=isodate.parse_datetime(data["created"]),
                updated=isodate.parse_datetime(data["updated"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing FeatureCreatedUpdated",
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
            "created": self.created.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "updated": self.updated.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        }


@dataclasses.dataclass(frozen=True)
class FeatureSetCreatedUpdated:
    """FeatureSet created and updated timestamps.
    
    Args:
        id (FeatureSetId): A data field.
        created (datetime.datetime): A data field.
        updated (datetime.datetime): A data field.
    """
    
    id: FeatureSetId
    created: datetime.datetime
    updated: datetime.datetime
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for FeatureSetCreatedUpdated data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": FeatureSetId.json_schema(),
                "created": {
                    "type": "string",
                    "format": "date-time"
                },
                "updated": {
                    "type": "string",
                    "format": "date-time"
                }
            },
            "required": [
                "id",
                "created",
                "updated",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FeatureSetCreatedUpdated:
        """Validate and parse JSON data into an instance of FeatureSetCreatedUpdated.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureSetCreatedUpdated.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureSetCreatedUpdated(
                id=FeatureSetId.from_json(data["id"]),
                created=isodate.parse_datetime(data["created"]),
                updated=isodate.parse_datetime(data["updated"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing FeatureSetCreatedUpdated",
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
            "created": self.created.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "updated": self.updated.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        }


@dataclasses.dataclass(frozen=True)
class TemplateCreatedUpdated:
    """Template created and updated timestamps.
    
    Args:
        id (TemplateId): A data field.
        created (datetime.datetime): A data field.
        updated (datetime.datetime): A data field.
    """
    
    id: TemplateId
    created: datetime.datetime
    updated: datetime.datetime
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TemplateCreatedUpdated data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": TemplateId.json_schema(),
                "created": {
                    "type": "string",
                    "format": "date-time"
                },
                "updated": {
                    "type": "string",
                    "format": "date-time"
                }
            },
            "required": [
                "id",
                "created",
                "updated",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TemplateCreatedUpdated:
        """Validate and parse JSON data into an instance of TemplateCreatedUpdated.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TemplateCreatedUpdated.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TemplateCreatedUpdated(
                id=TemplateId.from_json(data["id"]),
                created=isodate.parse_datetime(data["created"]),
                updated=isodate.parse_datetime(data["updated"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing TemplateCreatedUpdated",
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
            "created": self.created.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "updated": self.updated.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        }


@dataclasses.dataclass(frozen=True)
class TableCreatedUpdated:
    """Table created and updated timestamps.
    
    Args:
        id (TableId): A data field.
        created (datetime.datetime): A data field.
        updated (datetime.datetime): A data field.
    """
    
    id: TableId
    created: datetime.datetime
    updated: datetime.datetime
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TableCreatedUpdated data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": TableId.json_schema(),
                "created": {
                    "type": "string",
                    "format": "date-time"
                },
                "updated": {
                    "type": "string",
                    "format": "date-time"
                }
            },
            "required": [
                "id",
                "created",
                "updated",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TableCreatedUpdated:
        """Validate and parse JSON data into an instance of TableCreatedUpdated.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableCreatedUpdated.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableCreatedUpdated(
                id=TableId.from_json(data["id"]),
                created=isodate.parse_datetime(data["created"]),
                updated=isodate.parse_datetime(data["updated"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing TableCreatedUpdated",
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
            "created": self.created.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "updated": self.updated.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        }

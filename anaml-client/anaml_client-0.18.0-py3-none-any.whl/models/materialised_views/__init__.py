"""Generated implementation of materialised_views."""

# WARNING DO NOT EDIT
# This code was generated from materialised-views.mcn

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

from ..cluster import ClusterId
from ..destination_reference import DestinationReference
from ..feature_store import VersionTarget
from ..schedule import Schedule
from ..table import TableId


@dataclasses.dataclass(frozen=True)
class ViewMaterialisationJobId:
    """Unique identifier of a table caching job.
    
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
        """Return the JSON schema for ViewMaterialisationJobId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ViewMaterialisationJobId:
        """Validate and parse JSON data into an instance of ViewMaterialisationJobId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ViewMaterialisationJobId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ViewMaterialisationJobId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing ViewMaterialisationJobId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> ViewMaterialisationJobId:
        """Parse a JSON string such as a dictionary key."""
        return ViewMaterialisationJobId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class ViewMaterialisationJobName:
    """Unique name for a table caching job.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ViewMaterialisationJobName data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ViewMaterialisationJobName:
        """Validate and parse JSON data into an instance of ViewMaterialisationJobName.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ViewMaterialisationJobName.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ViewMaterialisationJobName(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing ViewMaterialisationJobName", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> ViewMaterialisationJobName:
        """Parse a JSON string such as a dictionary key."""
        return ViewMaterialisationJobName(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class ViewMaterialisationJobVersionId:
    """Unique identifier for a specific version of a table caching job.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ViewMaterialisationJobVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ViewMaterialisationJobVersionId:
        """Validate and parse JSON data into an instance of ViewMaterialisationJobVersionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ViewMaterialisationJobVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ViewMaterialisationJobVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing ViewMaterialisationJobVersionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> ViewMaterialisationJobVersionId:
        """Parse a JSON string such as a dictionary key."""
        return ViewMaterialisationJobVersionId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class ViewMaterialisationRunId:
    """Unique identifier of a table caching job run.
    
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
        """Return the JSON schema for ViewMaterialisationRunId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ViewMaterialisationRunId:
        """Validate and parse JSON data into an instance of ViewMaterialisationRunId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ViewMaterialisationRunId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ViewMaterialisationRunId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing ViewMaterialisationRunId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return self.value
    
    @classmethod
    def from_json_key(cls, data: str) -> ViewMaterialisationRunId:
        """Parse a JSON string such as a dictionary key."""
        return ViewMaterialisationRunId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class ViewMaterialisation:
    """Details of the table and entity to be cached.
    
    Args:
        table (TableId): A data field.
        destination (DestinationReference): A data field.
    """
    
    table: TableId
    destination: DestinationReference
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ViewMaterialisation data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "table": TableId.json_schema(),
                "destination": DestinationReference.json_schema()
            },
            "required": [
                "table",
                "destination",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ViewMaterialisation:
        """Validate and parse JSON data into an instance of ViewMaterialisation.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ViewMaterialisation.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ViewMaterialisation(
                table=TableId.from_json(data["table"]),
                destination=DestinationReference.from_json(data["destination"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing ViewMaterialisation",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "table": self.table.to_json(),
            "destination": self.destination.to_json()
        }


@dataclasses.dataclass(frozen=True)
class ViewMaterialisationJobCreationRequest:
    """Request to create a new table caching job.
    
    Args:
        name (ViewMaterialisationJobName): A data field.
        description (str): A data field.
        views (typing.List[ViewMaterialisation]): A data field.
        schedule (Schedule): A data field.
        cluster (ClusterId): A data field.
        versionTarget (typing.Optional[VersionTarget]): A data field.
    """
    
    name: ViewMaterialisationJobName
    description: str
    views: typing.List[ViewMaterialisation]
    schedule: Schedule
    cluster: ClusterId
    versionTarget: typing.Optional[VersionTarget]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ViewMaterialisationJobCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "name": ViewMaterialisationJobName.json_schema(),
                "description": {
                    "type": "string"
                },
                "views": {
                    "type": "array",
                    "item": ViewMaterialisation.json_schema()
                },
                "schedule": Schedule.json_schema(),
                "cluster": ClusterId.json_schema(),
                "versionTarget": {
                    "oneOf": [
                        {"type": "null"},
                        VersionTarget.json_schema(),
                    ]
                }
            },
            "required": [
                "name",
                "description",
                "views",
                "schedule",
                "cluster",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ViewMaterialisationJobCreationRequest:
        """Validate and parse JSON data into an instance of ViewMaterialisationJobCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ViewMaterialisationJobCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ViewMaterialisationJobCreationRequest(
                name=ViewMaterialisationJobName.from_json(data["name"]),
                description=str(data["description"]),
                views=[ViewMaterialisation.from_json(v) for v in data["views"]],
                schedule=Schedule.from_json(data["schedule"]),
                cluster=ClusterId.from_json(data["cluster"]),
                versionTarget=(
                    lambda v: v and VersionTarget.from_json(v)
                )(
                    data.get("versionTarget", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing ViewMaterialisationJobCreationRequest",
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
            "views": [v.to_json() for v in self.views],
            "schedule": self.schedule.to_json(),
            "cluster": self.cluster.to_json(),
            "versionTarget": (lambda v: v and v.to_json())(self.versionTarget)
        }


@dataclasses.dataclass(frozen=True)
class ViewMaterialisationJob:
    """Details of a table caching job.
    
    Args:
        id (ViewMaterialisationJobId): A data field.
        name (ViewMaterialisationJobName): A data field.
        description (str): A data field.
        views (typing.List[ViewMaterialisation]): A data field.
        schedule (Schedule): A data field.
        cluster (ClusterId): A data field.
        versionTarget (typing.Optional[VersionTarget]): A data field.
        version (ViewMaterialisationJobVersionId): A data field.
    """
    
    id: ViewMaterialisationJobId
    name: ViewMaterialisationJobName
    description: str
    views: typing.List[ViewMaterialisation]
    schedule: Schedule
    cluster: ClusterId
    versionTarget: typing.Optional[VersionTarget]
    version: ViewMaterialisationJobVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ViewMaterialisationJob data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": ViewMaterialisationJobId.json_schema(),
                "name": ViewMaterialisationJobName.json_schema(),
                "description": {
                    "type": "string"
                },
                "views": {
                    "type": "array",
                    "item": ViewMaterialisation.json_schema()
                },
                "schedule": Schedule.json_schema(),
                "cluster": ClusterId.json_schema(),
                "versionTarget": {
                    "oneOf": [
                        {"type": "null"},
                        VersionTarget.json_schema(),
                    ]
                },
                "version": ViewMaterialisationJobVersionId.json_schema()
            },
            "required": [
                "id",
                "name",
                "description",
                "views",
                "schedule",
                "cluster",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ViewMaterialisationJob:
        """Validate and parse JSON data into an instance of ViewMaterialisationJob.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ViewMaterialisationJob.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ViewMaterialisationJob(
                id=ViewMaterialisationJobId.from_json(data["id"]),
                name=ViewMaterialisationJobName.from_json(data["name"]),
                description=str(data["description"]),
                views=[ViewMaterialisation.from_json(v) for v in data["views"]],
                schedule=Schedule.from_json(data["schedule"]),
                cluster=ClusterId.from_json(data["cluster"]),
                versionTarget=(
                    lambda v: v and VersionTarget.from_json(v)
                )(
                    data.get("versionTarget", None)
                ),
                version=ViewMaterialisationJobVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing ViewMaterialisationJob",
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
            "views": [v.to_json() for v in self.views],
            "schedule": self.schedule.to_json(),
            "cluster": self.cluster.to_json(),
            "versionTarget": (lambda v: v and v.to_json())(self.versionTarget),
            "version": self.version.to_json()
        }

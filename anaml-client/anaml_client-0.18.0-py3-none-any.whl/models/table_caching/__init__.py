"""Generated implementation of table_caching."""

# WARNING DO NOT EDIT
# This code was generated from table-caching.mcn

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
from ..commit import CommitId
from ..entity import EntityId
from ..feature_store_run import ExecutionStatistics
from ..jobs import RunError, RunStatus
from ..schedule import Schedule
from ..table import TableId


@dataclasses.dataclass(frozen=True)
class TableCachingJobId:
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
        """Return the JSON schema for TableCachingJobId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TableCachingJobId:
        """Validate and parse JSON data into an instance of TableCachingJobId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableCachingJobId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableCachingJobId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing TableCachingJobId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> TableCachingJobId:
        """Parse a JSON string such as a dictionary key."""
        return TableCachingJobId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class TableCachingJobName:
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
        """Return the JSON schema for TableCachingJobName data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TableCachingJobName:
        """Validate and parse JSON data into an instance of TableCachingJobName.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableCachingJobName.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableCachingJobName(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing TableCachingJobName", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> TableCachingJobName:
        """Parse a JSON string such as a dictionary key."""
        return TableCachingJobName(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class TableCachingJobVersionId:
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
        """Return the JSON schema for TableCachingJobVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TableCachingJobVersionId:
        """Validate and parse JSON data into an instance of TableCachingJobVersionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableCachingJobVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableCachingJobVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing TableCachingJobVersionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> TableCachingJobVersionId:
        """Parse a JSON string such as a dictionary key."""
        return TableCachingJobVersionId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class TableCachingRunId:
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
        """Return the JSON schema for TableCachingRunId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TableCachingRunId:
        """Validate and parse JSON data into an instance of TableCachingRunId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableCachingRunId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableCachingRunId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing TableCachingRunId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return self.value
    
    @classmethod
    def from_json_key(cls, data: str) -> TableCachingRunId:
        """Parse a JSON string such as a dictionary key."""
        return TableCachingRunId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class TableCacheId:
    """Unique identifier of a table cache.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TableCacheId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TableCacheId:
        """Validate and parse JSON data into an instance of TableCacheId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableCacheId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableCacheId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing TableCacheId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> TableCacheId:
        """Parse a JSON string such as a dictionary key."""
        return TableCacheId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class TableCache:
    """Details of a table cache.
    
    Args:
        id (TableCacheId): A data field.
        job (typing.Optional[TableCachingJobId]): A data field.
        run (typing.Optional[TableCachingRunId]): A data field.
        uri (str): A data field.
        table (TableId): A data field.
        entity (EntityId): A data field.
        commit (CommitId): A data field.
        created (datetime.datetime): A data field.
    """
    
    id: TableCacheId
    job: typing.Optional[TableCachingJobId]
    run: typing.Optional[TableCachingRunId]
    uri: str
    table: TableId
    entity: EntityId
    commit: CommitId
    created: datetime.datetime
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TableCache data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": TableCacheId.json_schema(),
                "job": {
                    "oneOf": [
                        {"type": "null"},
                        TableCachingJobId.json_schema(),
                    ]
                },
                "run": {
                    "oneOf": [
                        {"type": "null"},
                        TableCachingRunId.json_schema(),
                    ]
                },
                "uri": {
                    "type": "string"
                },
                "table": TableId.json_schema(),
                "entity": EntityId.json_schema(),
                "commit": CommitId.json_schema(),
                "created": {
                    "type": "string",
                    "format": "date-time"
                }
            },
            "required": [
                "id",
                "uri",
                "table",
                "entity",
                "commit",
                "created",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TableCache:
        """Validate and parse JSON data into an instance of TableCache.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableCache.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableCache(
                id=TableCacheId.from_json(data["id"]),
                job=(lambda v: v and TableCachingJobId.from_json(v))(data.get("job", None)),
                run=(lambda v: v and TableCachingRunId.from_json(v))(data.get("run", None)),
                uri=str(data["uri"]),
                table=TableId.from_json(data["table"]),
                entity=EntityId.from_json(data["entity"]),
                commit=CommitId.from_json(data["commit"]),
                created=isodate.parse_datetime(data["created"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing TableCache",
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
            "job": (lambda v: v and v.to_json())(self.job),
            "run": (lambda v: v and v.to_json())(self.run),
            "uri": str(self.uri),
            "table": self.table.to_json(),
            "entity": self.entity.to_json(),
            "commit": self.commit.to_json(),
            "created": self.created.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        }


@dataclasses.dataclass(frozen=True)
class TableCachingSpec:
    """Details of the table and entity to be cached.
    
    Args:
        table (TableId): A data field.
        entity (EntityId): A data field.
    """
    
    table: TableId
    entity: EntityId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TableCachingSpec data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "table": TableId.json_schema(),
                "entity": EntityId.json_schema()
            },
            "required": [
                "table",
                "entity",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TableCachingSpec:
        """Validate and parse JSON data into an instance of TableCachingSpec.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableCachingSpec.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableCachingSpec(
                table=TableId.from_json(data["table"]),
                entity=EntityId.from_json(data["entity"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing TableCachingSpec",
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
            "entity": self.entity.to_json()
        }


@dataclasses.dataclass(frozen=True)
class TableCachingJobCreationRequest:
    """Request to create a new table caching job.
    
    Args:
        name (TableCachingJobName): A data field.
        description (str): A data field.
        specs (typing.List[TableCachingSpec]): A data field.
        prefixURI (str): A data field.
        schedule (Schedule): A data field.
        cluster (ClusterId): A data field.
    """
    
    name: TableCachingJobName
    description: str
    specs: typing.List[TableCachingSpec]
    prefixURI: str
    schedule: Schedule
    cluster: ClusterId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TableCachingJobCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "name": TableCachingJobName.json_schema(),
                "description": {
                    "type": "string"
                },
                "specs": {
                    "type": "array",
                    "item": TableCachingSpec.json_schema()
                },
                "prefixURI": {
                    "type": "string"
                },
                "schedule": Schedule.json_schema(),
                "cluster": ClusterId.json_schema()
            },
            "required": [
                "name",
                "description",
                "specs",
                "prefixURI",
                "schedule",
                "cluster",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TableCachingJobCreationRequest:
        """Validate and parse JSON data into an instance of TableCachingJobCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableCachingJobCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableCachingJobCreationRequest(
                name=TableCachingJobName.from_json(data["name"]),
                description=str(data["description"]),
                specs=[TableCachingSpec.from_json(v) for v in data["specs"]],
                prefixURI=str(data["prefixURI"]),
                schedule=Schedule.from_json(data["schedule"]),
                cluster=ClusterId.from_json(data["cluster"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing TableCachingJobCreationRequest",
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
            "specs": [v.to_json() for v in self.specs],
            "prefixURI": str(self.prefixURI),
            "schedule": self.schedule.to_json(),
            "cluster": self.cluster.to_json()
        }


@dataclasses.dataclass(frozen=True)
class TableCachingJob:
    """Details of a table caching job.
    
    Args:
        id (TableCachingJobId): A data field.
        name (TableCachingJobName): A data field.
        description (str): A data field.
        specs (typing.List[TableCachingSpec]): A data field.
        prefixURI (str): A data field.
        schedule (Schedule): A data field.
        cluster (ClusterId): A data field.
        version (TableCachingJobVersionId): A data field.
    """
    
    id: TableCachingJobId
    name: TableCachingJobName
    description: str
    specs: typing.List[TableCachingSpec]
    prefixURI: str
    schedule: Schedule
    cluster: ClusterId
    version: TableCachingJobVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TableCachingJob data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": TableCachingJobId.json_schema(),
                "name": TableCachingJobName.json_schema(),
                "description": {
                    "type": "string"
                },
                "specs": {
                    "type": "array",
                    "item": TableCachingSpec.json_schema()
                },
                "prefixURI": {
                    "type": "string"
                },
                "schedule": Schedule.json_schema(),
                "cluster": ClusterId.json_schema(),
                "version": TableCachingJobVersionId.json_schema()
            },
            "required": [
                "id",
                "name",
                "description",
                "specs",
                "prefixURI",
                "schedule",
                "cluster",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TableCachingJob:
        """Validate and parse JSON data into an instance of TableCachingJob.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableCachingJob.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableCachingJob(
                id=TableCachingJobId.from_json(data["id"]),
                name=TableCachingJobName.from_json(data["name"]),
                description=str(data["description"]),
                specs=[TableCachingSpec.from_json(v) for v in data["specs"]],
                prefixURI=str(data["prefixURI"]),
                schedule=Schedule.from_json(data["schedule"]),
                cluster=ClusterId.from_json(data["cluster"]),
                version=TableCachingJobVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing TableCachingJob",
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
            "specs": [v.to_json() for v in self.specs],
            "prefixURI": str(self.prefixURI),
            "schedule": self.schedule.to_json(),
            "cluster": self.cluster.to_json(),
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class TableCachingRunCreationRequest:
    """Request to create a new table caching job run.
    
    Args:
        jobId (TableCachingJobId): A data field.
        jobVersionId (TableCachingJobVersionId): A data field.
        scheduled_start_time (typing.Optional[datetime.datetime]): A data field.
        retryCount (typing.Optional[int]): A data field.
    """
    
    jobId: TableCachingJobId
    jobVersionId: TableCachingJobVersionId
    scheduled_start_time: typing.Optional[datetime.datetime]
    retryCount: typing.Optional[int]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TableCachingRunCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "jobId": TableCachingJobId.json_schema(),
                "jobVersionId": TableCachingJobVersionId.json_schema(),
                "scheduled_start_time": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string", "format": "date-time"},
                    ]
                },
                "retryCount": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "integer"},
                    ]
                }
            },
            "required": [
                "jobId",
                "jobVersionId",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TableCachingRunCreationRequest:
        """Validate and parse JSON data into an instance of TableCachingRunCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableCachingRunCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableCachingRunCreationRequest(
                jobId=TableCachingJobId.from_json(data["jobId"]),
                jobVersionId=TableCachingJobVersionId.from_json(data["jobVersionId"]),
                scheduled_start_time=(
                    lambda v: v and isodate.parse_datetime(v)
                )(
                    data.get("scheduled_start_time", None)
                ),
                retryCount=(lambda v: v and int(v))(data.get("retryCount", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing TableCachingRunCreationRequest",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "jobId": self.jobId.to_json(),
            "jobVersionId": self.jobVersionId.to_json(),
            "scheduled_start_time": (lambda v: v and v.strftime('%Y-%m-%dT%H:%M:%S.%f%z'))(self.scheduled_start_time),
            "retryCount": (lambda v: v and int(v))(self.retryCount)
        }


@dataclasses.dataclass(frozen=True)
class TableCachingRunUpdateRequest:
    """Request to update a table caching job run.
    
    Args:
        status (RunStatus): A data field.
        error (typing.Optional[RunError]): A data field.
    """
    
    status: RunStatus
    error: typing.Optional[RunError]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TableCachingRunUpdateRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "status": RunStatus.json_schema(),
                "error": {
                    "oneOf": [
                        {"type": "null"},
                        RunError.json_schema(),
                    ]
                }
            },
            "required": [
                "status",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TableCachingRunUpdateRequest:
        """Validate and parse JSON data into an instance of TableCachingRunUpdateRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableCachingRunUpdateRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableCachingRunUpdateRequest(
                status=RunStatus.from_json(data["status"]),
                error=(lambda v: v and RunError.from_json(v))(data.get("error", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing TableCachingRunUpdateRequest",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "status": self.status.to_json(),
            "error": (lambda v: v and v.to_json())(self.error)
        }


@dataclasses.dataclass(frozen=True)
class TableCachingRun:
    """Details of a table caching job run.
    
    Args:
        id (TableCachingRunId): A data field.
        jobId (TableCachingJobId): A data field.
        jobVersionId (TableCachingJobVersionId): A data field.
        scheduled_start_time (typing.Optional[datetime.datetime]): A data field.
        retryCount (typing.Optional[int]): A data field.
        status (RunStatus): A data field.
        error (typing.Optional[RunError]): A data field.
        executionStatistics (typing.Optional[ExecutionStatistics]): A data field.
        created (datetime.datetime): A data field.
    """
    
    id: TableCachingRunId
    jobId: TableCachingJobId
    jobVersionId: TableCachingJobVersionId
    scheduled_start_time: typing.Optional[datetime.datetime]
    retryCount: typing.Optional[int]
    status: RunStatus
    error: typing.Optional[RunError]
    executionStatistics: typing.Optional[ExecutionStatistics]
    created: datetime.datetime
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TableCachingRun data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": TableCachingRunId.json_schema(),
                "jobId": TableCachingJobId.json_schema(),
                "jobVersionId": TableCachingJobVersionId.json_schema(),
                "scheduled_start_time": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string", "format": "date-time"},
                    ]
                },
                "retryCount": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "integer"},
                    ]
                },
                "status": RunStatus.json_schema(),
                "error": {
                    "oneOf": [
                        {"type": "null"},
                        RunError.json_schema(),
                    ]
                },
                "executionStatistics": {
                    "oneOf": [
                        {"type": "null"},
                        ExecutionStatistics.json_schema(),
                    ]
                },
                "created": {
                    "type": "string",
                    "format": "date-time"
                }
            },
            "required": [
                "id",
                "jobId",
                "jobVersionId",
                "status",
                "created",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TableCachingRun:
        """Validate and parse JSON data into an instance of TableCachingRun.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableCachingRun.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableCachingRun(
                id=TableCachingRunId.from_json(data["id"]),
                jobId=TableCachingJobId.from_json(data["jobId"]),
                jobVersionId=TableCachingJobVersionId.from_json(data["jobVersionId"]),
                scheduled_start_time=(
                    lambda v: v and isodate.parse_datetime(v)
                )(
                    data.get("scheduled_start_time", None)
                ),
                retryCount=(lambda v: v and int(v))(data.get("retryCount", None)),
                status=RunStatus.from_json(data["status"]),
                error=(lambda v: v and RunError.from_json(v))(data.get("error", None)),
                executionStatistics=(
                    lambda v: v and ExecutionStatistics.from_json(v)
                )(
                    data.get("executionStatistics", None)
                ),
                created=isodate.parse_datetime(data["created"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing TableCachingRun",
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
            "jobId": self.jobId.to_json(),
            "jobVersionId": self.jobVersionId.to_json(),
            "scheduled_start_time": (lambda v: v and v.strftime('%Y-%m-%dT%H:%M:%S.%f%z'))(self.scheduled_start_time),
            "retryCount": (lambda v: v and int(v))(self.retryCount),
            "status": self.status.to_json(),
            "error": (lambda v: v and v.to_json())(self.error),
            "executionStatistics": (lambda v: v and v.to_json())(self.executionStatistics),
            "created": self.created.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        }

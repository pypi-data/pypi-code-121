"""Generated implementation of event."""

# WARNING DO NOT EDIT
# This code was generated from event.mcn

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

from ..commit import CommitId
from ..feature_store import FeatureStoreId
from ..jobs import (
    FeatureStoreRunId, RunStatus, TableMonitoringJobId, TableMonitoringRunId
)
from ..materialised_views import (
    ViewMaterialisationJobId, ViewMaterialisationRunId
)
from ..merge_request import MergeRequestCommentId, MergeRequestId
from ..table_caching import TableCachingJobId, TableCachingRunId


@dataclasses.dataclass(frozen=True)
class Event(abc.ABC):
    """Event notifications sent to registered webhooks."""
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    @classmethod
    def json_schema(cls) -> Event:
        """JSON schema for variant Event.
        
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
    def from_json(cls, data: dict) -> Event:
        """Validate and parse JSON data into an instance of Event.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Event.
        
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
            logging.debug("Invalid JSON data received while parsing Event", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class NewMergeRequestEvent(Event):
    """A new merge request has been created.
    
    Args:
        id (MergeRequestId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "newmergerequest"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: MergeRequestId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for NewMergeRequestEvent data.
        
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
                "id": MergeRequestId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> NewMergeRequestEvent:
        """Validate and parse JSON data into an instance of NewMergeRequestEvent.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of NewMergeRequestEvent.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return NewMergeRequestEvent(
                id=MergeRequestId.from_json(data["id"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing NewMergeRequestEvent",
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
            "id": self.id.to_json()
        }


@dataclasses.dataclass(frozen=True)
class NewMergeRequestCommentEvent(Event):
    """A comment has been posted on a merge request.
    
    Args:
        id (MergeRequestId): A data field.
        commentId (MergeRequestCommentId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "newmergerequestcomment"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: MergeRequestId
    commentId: MergeRequestCommentId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for NewMergeRequestCommentEvent data.
        
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
                "id": MergeRequestId.json_schema(),
                "commentId": MergeRequestCommentId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "commentId",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> NewMergeRequestCommentEvent:
        """Validate and parse JSON data into an instance of NewMergeRequestCommentEvent.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of NewMergeRequestCommentEvent.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return NewMergeRequestCommentEvent(
                id=MergeRequestId.from_json(data["id"]),
                commentId=MergeRequestCommentId.from_json(data["commentId"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing NewMergeRequestCommentEvent",
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
            "commentId": self.commentId.to_json()
        }


@dataclasses.dataclass(frozen=True)
class MergeRequestAcceptedEvent(Event):
    """A merge request has been accepted.
    
    Args:
        id (MergeRequestId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "mergerequestaccepted"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: MergeRequestId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for MergeRequestAcceptedEvent data.
        
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
                "id": MergeRequestId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> MergeRequestAcceptedEvent:
        """Validate and parse JSON data into an instance of MergeRequestAcceptedEvent.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of MergeRequestAcceptedEvent.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return MergeRequestAcceptedEvent(
                id=MergeRequestId.from_json(data["id"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing MergeRequestAcceptedEvent",
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
            "id": self.id.to_json()
        }


@dataclasses.dataclass(frozen=True)
class NewCommitEvent(Event):
    """A new commit has been created.
    
    Args:
        id (CommitId): A data field.
        branch (typing.Optional[str]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "newcommit"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: CommitId
    branch: typing.Optional[str]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for NewCommitEvent data.
        
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
                "id": CommitId.json_schema(),
                "branch": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                }
            },
            "required": [
                "adt_type",
                "id",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> NewCommitEvent:
        """Validate and parse JSON data into an instance of NewCommitEvent.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of NewCommitEvent.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return NewCommitEvent(
                id=CommitId.from_json(data["id"]),
                branch=(lambda v: v and str(v))(data.get("branch", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing NewCommitEvent",
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
            "branch": (lambda v: v and str(v))(self.branch)
        }


@dataclasses.dataclass(frozen=True)
class FeatureStoreRunEvent(Event):
    """A feature store run has changed status.
    
    Args:
        featureStore (FeatureStoreId): A data field.
        run (FeatureStoreRunId): A data field.
        status (RunStatus): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "featurestorerun"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    featureStore: FeatureStoreId
    run: FeatureStoreRunId
    status: RunStatus
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for FeatureStoreRunEvent data.
        
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
                "featureStore": FeatureStoreId.json_schema(),
                "run": FeatureStoreRunId.json_schema(),
                "status": RunStatus.json_schema()
            },
            "required": [
                "adt_type",
                "featureStore",
                "run",
                "status",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FeatureStoreRunEvent:
        """Validate and parse JSON data into an instance of FeatureStoreRunEvent.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureStoreRunEvent.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureStoreRunEvent(
                featureStore=FeatureStoreId.from_json(data["featureStore"]),
                run=FeatureStoreRunId.from_json(data["run"]),
                status=RunStatus.from_json(data["status"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing FeatureStoreRunEvent",
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
            "featureStore": self.featureStore.to_json(),
            "run": self.run.to_json(),
            "status": self.status.to_json()
        }


@dataclasses.dataclass(frozen=True)
class MonitoringRunEvent(Event):
    """A monitoring run has changed status.
    
    Args:
        job (TableMonitoringJobId): A data field.
        run (TableMonitoringRunId): A data field.
        status (RunStatus): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "monitoringrun"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    job: TableMonitoringJobId
    run: TableMonitoringRunId
    status: RunStatus
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for MonitoringRunEvent data.
        
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
                "job": TableMonitoringJobId.json_schema(),
                "run": TableMonitoringRunId.json_schema(),
                "status": RunStatus.json_schema()
            },
            "required": [
                "adt_type",
                "job",
                "run",
                "status",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> MonitoringRunEvent:
        """Validate and parse JSON data into an instance of MonitoringRunEvent.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of MonitoringRunEvent.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return MonitoringRunEvent(
                job=TableMonitoringJobId.from_json(data["job"]),
                run=TableMonitoringRunId.from_json(data["run"]),
                status=RunStatus.from_json(data["status"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing MonitoringRunEvent",
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
            "job": self.job.to_json(),
            "run": self.run.to_json(),
            "status": self.status.to_json()
        }


@dataclasses.dataclass(frozen=True)
class CachingRunEvent(Event):
    """A table caching run has changed status.
    
    Args:
        job (TableCachingJobId): A data field.
        run (TableCachingRunId): A data field.
        status (RunStatus): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "cachingrun"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    job: TableCachingJobId
    run: TableCachingRunId
    status: RunStatus
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for CachingRunEvent data.
        
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
                "job": TableCachingJobId.json_schema(),
                "run": TableCachingRunId.json_schema(),
                "status": RunStatus.json_schema()
            },
            "required": [
                "adt_type",
                "job",
                "run",
                "status",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> CachingRunEvent:
        """Validate and parse JSON data into an instance of CachingRunEvent.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of CachingRunEvent.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return CachingRunEvent(
                job=TableCachingJobId.from_json(data["job"]),
                run=TableCachingRunId.from_json(data["run"]),
                status=RunStatus.from_json(data["status"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing CachingRunEvent",
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
            "job": self.job.to_json(),
            "run": self.run.to_json(),
            "status": self.status.to_json()
        }


@dataclasses.dataclass(frozen=True)
class ViewMaterialisationEvent(Event):
    """A table caching run has changed status.
    
    Args:
        job (ViewMaterialisationJobId): A data field.
        run (ViewMaterialisationRunId): A data field.
        status (RunStatus): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "viewmaterialisation"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    job: ViewMaterialisationJobId
    run: ViewMaterialisationRunId
    status: RunStatus
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ViewMaterialisationEvent data.
        
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
                "job": ViewMaterialisationJobId.json_schema(),
                "run": ViewMaterialisationRunId.json_schema(),
                "status": RunStatus.json_schema()
            },
            "required": [
                "adt_type",
                "job",
                "run",
                "status",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ViewMaterialisationEvent:
        """Validate and parse JSON data into an instance of ViewMaterialisationEvent.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ViewMaterialisationEvent.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ViewMaterialisationEvent(
                job=ViewMaterialisationJobId.from_json(data["job"]),
                run=ViewMaterialisationRunId.from_json(data["run"]),
                status=RunStatus.from_json(data["status"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing ViewMaterialisationEvent",
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
            "job": self.job.to_json(),
            "run": self.run.to_json(),
            "status": self.status.to_json()
        }

"""Generated implementation of materialised_view_runs."""

# WARNING DO NOT EDIT
# This code was generated from materialised-view-runs.mcn

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

from ..feature_store_run import ExecutionStatistics
from ..jobs import RunError, RunStatus
from ..materialised_views import (
    ViewMaterialisationJobId, ViewMaterialisationJobVersionId,
    ViewMaterialisationRunId
)
from ..schedule import ScheduleState


@dataclasses.dataclass(frozen=True)
class ViewMaterialisationRunCreationRequest:
    """Request to create a new table caching job run.
    
    Args:
        job (ViewMaterialisationJobId): A data field.
        jobVersion (ViewMaterialisationJobVersionId): A data field.
        scheduleState (typing.Optional[ScheduleState]): A data field.
        status (RunStatus): A data field.
        error (typing.Optional[RunError]): A data field.
        executionStatistics (typing.Optional[ExecutionStatistics]): A data field.
    """
    
    job: ViewMaterialisationJobId
    jobVersion: ViewMaterialisationJobVersionId
    scheduleState: typing.Optional[ScheduleState]
    status: RunStatus
    error: typing.Optional[RunError]
    executionStatistics: typing.Optional[ExecutionStatistics]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ViewMaterialisationRunCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "job": ViewMaterialisationJobId.json_schema(),
                "jobVersion": ViewMaterialisationJobVersionId.json_schema(),
                "scheduleState": {
                    "oneOf": [
                        {"type": "null"},
                        ScheduleState.json_schema(),
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
                }
            },
            "required": [
                "job",
                "jobVersion",
                "status",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ViewMaterialisationRunCreationRequest:
        """Validate and parse JSON data into an instance of ViewMaterialisationRunCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ViewMaterialisationRunCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ViewMaterialisationRunCreationRequest(
                job=ViewMaterialisationJobId.from_json(data["job"]),
                jobVersion=ViewMaterialisationJobVersionId.from_json(data["jobVersion"]),
                scheduleState=(
                    lambda v: v and ScheduleState.from_json(v)
                )(
                    data.get("scheduleState", None)
                ),
                status=RunStatus.from_json(data["status"]),
                error=(lambda v: v and RunError.from_json(v))(data.get("error", None)),
                executionStatistics=(
                    lambda v: v and ExecutionStatistics.from_json(v)
                )(
                    data.get("executionStatistics", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing ViewMaterialisationRunCreationRequest",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "job": self.job.to_json(),
            "jobVersion": self.jobVersion.to_json(),
            "scheduleState": (lambda v: v and v.to_json())(self.scheduleState),
            "status": self.status.to_json(),
            "error": (lambda v: v and v.to_json())(self.error),
            "executionStatistics": (lambda v: v and v.to_json())(self.executionStatistics)
        }


@dataclasses.dataclass(frozen=True)
class ViewMaterialisationRunUpdateRequest:
    """Request to update a table caching job run.
    
    Args:
        status (RunStatus): A data field.
        error (typing.Optional[RunError]): A data field.
        executionStatistics (typing.Optional[ExecutionStatistics]): A data field.
    """
    
    status: RunStatus
    error: typing.Optional[RunError]
    executionStatistics: typing.Optional[ExecutionStatistics]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ViewMaterialisationRunUpdateRequest data.
        
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
                },
                "executionStatistics": {
                    "oneOf": [
                        {"type": "null"},
                        ExecutionStatistics.json_schema(),
                    ]
                }
            },
            "required": [
                "status",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ViewMaterialisationRunUpdateRequest:
        """Validate and parse JSON data into an instance of ViewMaterialisationRunUpdateRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ViewMaterialisationRunUpdateRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ViewMaterialisationRunUpdateRequest(
                status=RunStatus.from_json(data["status"]),
                error=(lambda v: v and RunError.from_json(v))(data.get("error", None)),
                executionStatistics=(
                    lambda v: v and ExecutionStatistics.from_json(v)
                )(
                    data.get("executionStatistics", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing ViewMaterialisationRunUpdateRequest",
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
            "error": (lambda v: v and v.to_json())(self.error),
            "executionStatistics": (lambda v: v and v.to_json())(self.executionStatistics)
        }


@dataclasses.dataclass(frozen=True)
class ViewMaterialisationRun:
    """Details of a table caching job run.
    
    Args:
        id (ViewMaterialisationRunId): A data field.
        job (ViewMaterialisationJobId): A data field.
        jobVersion (ViewMaterialisationJobVersionId): A data field.
        scheduleState (typing.Optional[ScheduleState]): A data field.
        status (RunStatus): A data field.
        error (typing.Optional[RunError]): A data field.
        executionStatistics (typing.Optional[ExecutionStatistics]): A data field.
        created (datetime.datetime): A data field.
    """
    
    id: ViewMaterialisationRunId
    job: ViewMaterialisationJobId
    jobVersion: ViewMaterialisationJobVersionId
    scheduleState: typing.Optional[ScheduleState]
    status: RunStatus
    error: typing.Optional[RunError]
    executionStatistics: typing.Optional[ExecutionStatistics]
    created: datetime.datetime
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ViewMaterialisationRun data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": ViewMaterialisationRunId.json_schema(),
                "job": ViewMaterialisationJobId.json_schema(),
                "jobVersion": ViewMaterialisationJobVersionId.json_schema(),
                "scheduleState": {
                    "oneOf": [
                        {"type": "null"},
                        ScheduleState.json_schema(),
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
                "job",
                "jobVersion",
                "status",
                "created",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ViewMaterialisationRun:
        """Validate and parse JSON data into an instance of ViewMaterialisationRun.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ViewMaterialisationRun.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ViewMaterialisationRun(
                id=ViewMaterialisationRunId.from_json(data["id"]),
                job=ViewMaterialisationJobId.from_json(data["job"]),
                jobVersion=ViewMaterialisationJobVersionId.from_json(data["jobVersion"]),
                scheduleState=(
                    lambda v: v and ScheduleState.from_json(v)
                )(
                    data.get("scheduleState", None)
                ),
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
                "Invalid JSON data received while parsing ViewMaterialisationRun",
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
            "job": self.job.to_json(),
            "jobVersion": self.jobVersion.to_json(),
            "scheduleState": (lambda v: v and v.to_json())(self.scheduleState),
            "status": self.status.to_json(),
            "error": (lambda v: v and v.to_json())(self.error),
            "executionStatistics": (lambda v: v and v.to_json())(self.executionStatistics),
            "created": self.created.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        }

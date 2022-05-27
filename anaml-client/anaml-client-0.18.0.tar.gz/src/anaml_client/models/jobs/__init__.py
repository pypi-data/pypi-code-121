"""Generated implementation of jobs."""

# WARNING DO NOT EDIT
# This code was generated from jobs.mcn

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


@dataclasses.dataclass(frozen=True)
class FeatureStoreRunId:
    """Unique identifier of a feature store run.
    
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
        """Return the JSON schema for FeatureStoreRunId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FeatureStoreRunId:
        """Validate and parse JSON data into an instance of FeatureStoreRunId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureStoreRunId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureStoreRunId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing FeatureStoreRunId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return self.value
    
    @classmethod
    def from_json_key(cls, data: str) -> FeatureStoreRunId:
        """Parse a JSON string such as a dictionary key."""
        return FeatureStoreRunId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class TableMonitoringJobId:
    """Unique identifier of a table monitoring job.
    
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
        """Return the JSON schema for TableMonitoringJobId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TableMonitoringJobId:
        """Validate and parse JSON data into an instance of TableMonitoringJobId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableMonitoringJobId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableMonitoringJobId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing TableMonitoringJobId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> TableMonitoringJobId:
        """Parse a JSON string such as a dictionary key."""
        return TableMonitoringJobId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class TableMonitoringRunId:
    """Unique identifier of a table monitoring job run.
    
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
        """Return the JSON schema for TableMonitoringRunId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TableMonitoringRunId:
        """Validate and parse JSON data into an instance of TableMonitoringRunId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableMonitoringRunId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableMonitoringRunId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing TableMonitoringRunId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return self.value
    
    @classmethod
    def from_json_key(cls, data: str) -> TableMonitoringRunId:
        """Parse a JSON string such as a dictionary key."""
        return TableMonitoringRunId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


class RunStatus(enum.Enum):
    """Status of a job."""
    Pending = "pending"
    """The job is waiting to be started."""
    Running = "running"
    """The job is running."""
    Completed = "completed"
    """The job has completed successfully."""
    Cancel = "cancel"
    """A user has requested that the job should be cancelled."""
    Cancelled = "cancelled"
    """The job was cancelled by a user."""
    Failed = "failed"
    """The job has failed."""
    Redundant = "redundant"
    """The job was scheduled but no work is required of it."""
    
    @classmethod
    def json_schema(cls) -> dict:
        """JSON schema for 'RunStatus'.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [
                        "pending",
                        "running",
                        "completed",
                        "cancel",
                        "cancelled",
                        "failed",
                        "redundant",
                    ]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> RunStatus:
        """Validate and parse JSON data into an instance of RunStatus.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of RunStatus.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return RunStatus(str(data['adt_type']))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing RunStatus", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            JSON data ready to be serialised.
        """
        return {'adt_type': self.value}
    
    @classmethod
    def from_json_key(cls, data: str) -> RunStatus:
        """Validate and parse a value from a JSON dictionary key.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of RunStatus.
        """
        return RunStatus(str(data))
    
    def to_json_key(self) -> str:
        """Serialised this instanse as a JSON string for use as a dictionary key.
        
        Returns:
            A JSON string ready to be used as a key.
        """
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class RunError:
    """Run error.

    Args:
        message (str): A data field.
        stackTrace (typing.Optional[str]): A data field.
    """
    
    message: str
    stackTrace: typing.Optional[str]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for RunError data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string"
                },
                "stackTrace": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                }
            },
            "required": [
                "message",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> RunError:
        """Validate and parse JSON data into an instance of RunError.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of RunError.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return RunError(
                message=str(data["message"]),
                stackTrace=(lambda v: v and str(v))(data.get("stackTrace", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing RunError",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "message": str(self.message),
            "stackTrace": (lambda v: v and str(v))(self.stackTrace)
        }

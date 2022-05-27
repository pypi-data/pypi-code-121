"""Generated implementation of checks."""

# WARNING DO NOT EDIT
# This code was generated from checks.mcn

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
from ..user import UserId


class CheckStatus(enum.Enum):
    """Status of an external check run."""
    Pending = "pending"
    Running = "running"
    Completed = "completed"
    
    @classmethod
    def json_schema(cls) -> dict:
        """JSON schema for 'CheckStatus'.
        
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
                    ]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> CheckStatus:
        """Validate and parse JSON data into an instance of CheckStatus.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of CheckStatus.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return CheckStatus(str(data['adt_type']))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing CheckStatus", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            JSON data ready to be serialised.
        """
        return {'adt_type': self.value}
    
    @classmethod
    def from_json_key(cls, data: str) -> CheckStatus:
        """Validate and parse a value from a JSON dictionary key.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of CheckStatus.
        """
        return CheckStatus(str(data))
    
    def to_json_key(self) -> str:
        """Serialised this instanse as a JSON string for use as a dictionary key.
        
        Returns:
            A JSON string ready to be used as a key.
        """
        return str(self.value)


class CheckConclusion(enum.Enum):
    """Outcome of an external check run."""
    Cancelled = "cancelled"
    Failure = "failure"
    Success = "success"
    Skipped = "skipped"
    TimedOut = "timedout"
    
    @classmethod
    def json_schema(cls) -> dict:
        """JSON schema for 'CheckConclusion'.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [
                        "cancelled",
                        "failure",
                        "success",
                        "skipped",
                        "timedout",
                    ]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> CheckConclusion:
        """Validate and parse JSON data into an instance of CheckConclusion.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of CheckConclusion.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return CheckConclusion(str(data['adt_type']))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing CheckConclusion", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            JSON data ready to be serialised.
        """
        return {'adt_type': self.value}
    
    @classmethod
    def from_json_key(cls, data: str) -> CheckConclusion:
        """Validate and parse a value from a JSON dictionary key.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of CheckConclusion.
        """
        return CheckConclusion(str(data))
    
    def to_json_key(self) -> str:
        """Serialised this instanse as a JSON string for use as a dictionary key.
        
        Returns:
            A JSON string ready to be used as a key.
        """
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class CheckId:
    """Unique identifier of an external check.
    
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
        """Return the JSON schema for CheckId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> CheckId:
        """Validate and parse JSON data into an instance of CheckId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of CheckId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return CheckId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing CheckId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> CheckId:
        """Parse a JSON string such as a dictionary key."""
        return CheckId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class CheckComponent:
    """Results for a specific component in an external check.
    
    Args:
        key (str): A data field.
        value (str): A data field.
    """
    
    key: str
    value: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for CheckComponent data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string"
                },
                "value": {
                    "type": "string"
                }
            },
            "required": [
                "key",
                "value",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> CheckComponent:
        """Validate and parse JSON data into an instance of CheckComponent.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of CheckComponent.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return CheckComponent(
                key=str(data["key"]),
                value=str(data["value"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing CheckComponent",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "key": str(self.key),
            "value": str(self.value)
        }


@dataclasses.dataclass(frozen=True)
class Check:
    """Details of an external check.
    
    Args:
        id (CheckId): A data field.
        name (str): A data field.
        summary (typing.Optional[str]): A data field.
        commit (CommitId): A data field.
        created_by (UserId): A data field.
        started (typing.Optional[datetime.datetime]): A data field.
        completed (typing.Optional[datetime.datetime]): A data field.
        status (CheckStatus): A data field.
        conclusion (typing.Optional[CheckConclusion]): A data field.
        components (typing.List[CheckComponent]): A data field.
        details_url (typing.Optional[str]): A data field.
    """
    
    id: CheckId
    name: str
    summary: typing.Optional[str]
    commit: CommitId
    created_by: UserId
    started: typing.Optional[datetime.datetime]
    completed: typing.Optional[datetime.datetime]
    status: CheckStatus
    conclusion: typing.Optional[CheckConclusion]
    components: typing.List[CheckComponent]
    details_url: typing.Optional[str]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for Check data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": CheckId.json_schema(),
                "name": {
                    "type": "string"
                },
                "summary": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "commit": CommitId.json_schema(),
                "created_by": UserId.json_schema(),
                "started": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string", "format": "date-time"},
                    ]
                },
                "completed": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string", "format": "date-time"},
                    ]
                },
                "status": CheckStatus.json_schema(),
                "conclusion": {
                    "oneOf": [
                        {"type": "null"},
                        CheckConclusion.json_schema(),
                    ]
                },
                "components": {
                    "type": "array",
                    "item": CheckComponent.json_schema()
                },
                "details_url": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                }
            },
            "required": [
                "id",
                "name",
                "commit",
                "created_by",
                "status",
                "components",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> Check:
        """Validate and parse JSON data into an instance of Check.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Check.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return Check(
                id=CheckId.from_json(data["id"]),
                name=str(data["name"]),
                summary=(lambda v: v and str(v))(data.get("summary", None)),
                commit=CommitId.from_json(data["commit"]),
                created_by=UserId.from_json(data["created_by"]),
                started=(lambda v: v and isodate.parse_datetime(v))(data.get("started", None)),
                completed=(
                    lambda v: v and isodate.parse_datetime(v)
                )(
                    data.get("completed", None)
                ),
                status=CheckStatus.from_json(data["status"]),
                conclusion=(
                    lambda v: v and CheckConclusion.from_json(v)
                )(
                    data.get("conclusion", None)
                ),
                components=[CheckComponent.from_json(v) for v in data["components"]],
                details_url=(lambda v: v and str(v))(data.get("details_url", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing Check",
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
            "name": str(self.name),
            "summary": (lambda v: v and str(v))(self.summary),
            "commit": self.commit.to_json(),
            "created_by": self.created_by.to_json(),
            "started": (lambda v: v and v.strftime('%Y-%m-%dT%H:%M:%S.%f%z'))(self.started),
            "completed": (lambda v: v and v.strftime('%Y-%m-%dT%H:%M:%S.%f%z'))(self.completed),
            "status": self.status.to_json(),
            "conclusion": (lambda v: v and v.to_json())(self.conclusion),
            "components": [v.to_json() for v in self.components],
            "details_url": (lambda v: v and str(v))(self.details_url)
        }


@dataclasses.dataclass(frozen=True)
class CheckCreationRequest:
    """Request to create a new external check.
    
    Args:
        name (str): A data field.
        summary (typing.Optional[str]): A data field.
        started (typing.Optional[datetime.datetime]): A data field.
        completed (typing.Optional[datetime.datetime]): A data field.
        status (CheckStatus): A data field.
        conclusion (typing.Optional[CheckConclusion]): A data field.
        components (typing.Optional[typing.List[CheckComponent]]): A data field.
        details_url (typing.Optional[str]): A data field.
    """
    
    name: str
    summary: typing.Optional[str]
    started: typing.Optional[datetime.datetime]
    completed: typing.Optional[datetime.datetime]
    status: CheckStatus
    conclusion: typing.Optional[CheckConclusion]
    components: typing.Optional[typing.List[CheckComponent]]
    details_url: typing.Optional[str]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for CheckCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string"
                },
                "summary": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "started": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string", "format": "date-time"},
                    ]
                },
                "completed": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string", "format": "date-time"},
                    ]
                },
                "status": CheckStatus.json_schema(),
                "conclusion": {
                    "oneOf": [
                        {"type": "null"},
                        CheckConclusion.json_schema(),
                    ]
                },
                "components": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "array", "item": CheckComponent.json_schema()},
                    ]
                },
                "details_url": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                }
            },
            "required": [
                "name",
                "status",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> CheckCreationRequest:
        """Validate and parse JSON data into an instance of CheckCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of CheckCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return CheckCreationRequest(
                name=str(data["name"]),
                summary=(lambda v: v and str(v))(data.get("summary", None)),
                started=(lambda v: v and isodate.parse_datetime(v))(data.get("started", None)),
                completed=(
                    lambda v: v and isodate.parse_datetime(v)
                )(
                    data.get("completed", None)
                ),
                status=CheckStatus.from_json(data["status"]),
                conclusion=(
                    lambda v: v and CheckConclusion.from_json(v)
                )(
                    data.get("conclusion", None)
                ),
                components=(
                    lambda v: v and [CheckComponent.from_json(v) for v in v]
                )(
                    data.get("components", None)
                ),
                details_url=(lambda v: v and str(v))(data.get("details_url", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing CheckCreationRequest",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "name": str(self.name),
            "summary": (lambda v: v and str(v))(self.summary),
            "started": (lambda v: v and v.strftime('%Y-%m-%dT%H:%M:%S.%f%z'))(self.started),
            "completed": (lambda v: v and v.strftime('%Y-%m-%dT%H:%M:%S.%f%z'))(self.completed),
            "status": self.status.to_json(),
            "conclusion": (lambda v: v and v.to_json())(self.conclusion),
            "components": (lambda v: v and [v.to_json() for v in v])(self.components),
            "details_url": (lambda v: v and str(v))(self.details_url)
        }

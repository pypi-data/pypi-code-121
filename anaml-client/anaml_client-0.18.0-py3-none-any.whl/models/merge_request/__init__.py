"""Generated implementation of merge_request."""

# WARNING DO NOT EDIT
# This code was generated from merge-request.mcn

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

from ..anaml_object import AnamlObject
from ..commit import CommitId
from ..user import UserId


@dataclasses.dataclass(frozen=True)
class MergeRequestId:
    """Unique identifier of a merge request.
    
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
        """Return the JSON schema for MergeRequestId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> MergeRequestId:
        """Validate and parse JSON data into an instance of MergeRequestId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of MergeRequestId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return MergeRequestId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing MergeRequestId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> MergeRequestId:
        """Parse a JSON string such as a dictionary key."""
        return MergeRequestId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class MergeRequestCommentId:
    """Unique identifier of a merge request comment.
    
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
        """Return the JSON schema for MergeRequestCommentId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> MergeRequestCommentId:
        """Validate and parse JSON data into an instance of MergeRequestCommentId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of MergeRequestCommentId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return MergeRequestCommentId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing MergeRequestCommentId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> MergeRequestCommentId:
        """Parse a JSON string such as a dictionary key."""
        return MergeRequestCommentId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class ApprovalId:
    """Unique identifier of a merge request approval.
    
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
        """Return the JSON schema for ApprovalId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ApprovalId:
        """Validate and parse JSON data into an instance of ApprovalId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ApprovalId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ApprovalId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing ApprovalId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> ApprovalId:
        """Parse a JSON string such as a dictionary key."""
        return ApprovalId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class ApprovalVersionId:
    """Unique identifier of a specific version of a merge request approval.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ApprovalVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ApprovalVersionId:
        """Validate and parse JSON data into an instance of ApprovalVersionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ApprovalVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ApprovalVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing ApprovalVersionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> ApprovalVersionId:
        """Parse a JSON string such as a dictionary key."""
        return ApprovalVersionId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


class MergeRequestStatus(enum.Enum):
    """Status of merge requests."""
    Open = "open"
    """The merge request is open."""
    Closed = "closed"
    """The merged request has been closed."""
    Merged = "merged"
    """The merge request has been merged."""
    
    @classmethod
    def json_schema(cls) -> dict:
        """JSON schema for 'MergeRequestStatus'.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [
                        "open",
                        "closed",
                        "merged",
                    ]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> MergeRequestStatus:
        """Validate and parse JSON data into an instance of MergeRequestStatus.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of MergeRequestStatus.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return MergeRequestStatus(str(data['adt_type']))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing MergeRequestStatus", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            JSON data ready to be serialised.
        """
        return {'adt_type': self.value}
    
    @classmethod
    def from_json_key(cls, data: str) -> MergeRequestStatus:
        """Validate and parse a value from a JSON dictionary key.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of MergeRequestStatus.
        """
        return MergeRequestStatus(str(data))
    
    def to_json_key(self) -> str:
        """Serialised this instanse as a JSON string for use as a dictionary key.
        
        Returns:
            A JSON string ready to be used as a key.
        """
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class MergeRequest:
    """Details of a merge request.
    
    Args:
        id (MergeRequestId): A data field.
        name (str): A data field.
        author (UserId): A data field.
        comment (str): A data field.
        source (str): A data field.
        target (str): A data field.
        status (MergeRequestStatus): A data field.
        mergeCommit (typing.Optional[CommitId]): A data field.
        created (datetime.datetime): A data field.
        modified (datetime.datetime): A data field.
    """
    
    id: MergeRequestId
    name: str
    author: UserId
    comment: str
    source: str
    target: str
    status: MergeRequestStatus
    mergeCommit: typing.Optional[CommitId]
    created: datetime.datetime
    modified: datetime.datetime
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for MergeRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": MergeRequestId.json_schema(),
                "name": {
                    "type": "string"
                },
                "author": UserId.json_schema(),
                "comment": {
                    "type": "string"
                },
                "source": {
                    "type": "string"
                },
                "target": {
                    "type": "string"
                },
                "status": MergeRequestStatus.json_schema(),
                "mergeCommit": {
                    "oneOf": [
                        {"type": "null"},
                        CommitId.json_schema(),
                    ]
                },
                "created": {
                    "type": "string",
                    "format": "date-time"
                },
                "modified": {
                    "type": "string",
                    "format": "date-time"
                }
            },
            "required": [
                "id",
                "name",
                "author",
                "comment",
                "source",
                "target",
                "status",
                "created",
                "modified",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> MergeRequest:
        """Validate and parse JSON data into an instance of MergeRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of MergeRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return MergeRequest(
                id=MergeRequestId.from_json(data["id"]),
                name=str(data["name"]),
                author=UserId.from_json(data["author"]),
                comment=str(data["comment"]),
                source=str(data["source"]),
                target=str(data["target"]),
                status=MergeRequestStatus.from_json(data["status"]),
                mergeCommit=(
                    lambda v: v and CommitId.from_json(v)
                )(
                    data.get("mergeCommit", None)
                ),
                created=isodate.parse_datetime(data["created"]),
                modified=isodate.parse_datetime(data["modified"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing MergeRequest",
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
            "author": self.author.to_json(),
            "comment": str(self.comment),
            "source": str(self.source),
            "target": str(self.target),
            "status": self.status.to_json(),
            "mergeCommit": (lambda v: v and v.to_json())(self.mergeCommit),
            "created": self.created.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "modified": self.modified.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        }


@dataclasses.dataclass(frozen=True)
class MergeRequestCreationRequest:
    """Request to create a new merge request.
    
    Args:
        name (str): A data field.
        comment (str): A data field.
        source (str): A data field.
        target (str): A data field.
    """
    
    name: str
    comment: str
    source: str
    target: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for MergeRequestCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string"
                },
                "comment": {
                    "type": "string"
                },
                "source": {
                    "type": "string"
                },
                "target": {
                    "type": "string"
                }
            },
            "required": [
                "name",
                "comment",
                "source",
                "target",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> MergeRequestCreationRequest:
        """Validate and parse JSON data into an instance of MergeRequestCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of MergeRequestCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return MergeRequestCreationRequest(
                name=str(data["name"]),
                comment=str(data["comment"]),
                source=str(data["source"]),
                target=str(data["target"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing MergeRequestCreationRequest",
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
            "comment": str(self.comment),
            "source": str(self.source),
            "target": str(self.target)
        }


@dataclasses.dataclass(frozen=True)
class MergeRequestComment:
    """Request to create a new comment on a merge request.
    
    Args:
        id (MergeRequestCommentId): A data field.
        mergeRequest (MergeRequestId): A data field.
        author (UserId): A data field.
        comment (str): A data field.
        created (datetime.datetime): A data field.
        modified (datetime.datetime): A data field.
        anamlObject (typing.Optional[AnamlObject]): A data field.
    """
    
    id: MergeRequestCommentId
    mergeRequest: MergeRequestId
    author: UserId
    comment: str
    created: datetime.datetime
    modified: datetime.datetime
    anamlObject: typing.Optional[AnamlObject]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for MergeRequestComment data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": MergeRequestCommentId.json_schema(),
                "mergeRequest": MergeRequestId.json_schema(),
                "author": UserId.json_schema(),
                "comment": {
                    "type": "string"
                },
                "created": {
                    "type": "string",
                    "format": "date-time"
                },
                "modified": {
                    "type": "string",
                    "format": "date-time"
                },
                "anamlObject": {
                    "oneOf": [
                        {"type": "null"},
                        AnamlObject.json_schema(),
                    ]
                }
            },
            "required": [
                "id",
                "mergeRequest",
                "author",
                "comment",
                "created",
                "modified",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> MergeRequestComment:
        """Validate and parse JSON data into an instance of MergeRequestComment.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of MergeRequestComment.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return MergeRequestComment(
                id=MergeRequestCommentId.from_json(data["id"]),
                mergeRequest=MergeRequestId.from_json(data["mergeRequest"]),
                author=UserId.from_json(data["author"]),
                comment=str(data["comment"]),
                created=isodate.parse_datetime(data["created"]),
                modified=isodate.parse_datetime(data["modified"]),
                anamlObject=(
                    lambda v: v and AnamlObject.from_json(v)
                )(
                    data.get("anamlObject", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing MergeRequestComment",
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
            "mergeRequest": self.mergeRequest.to_json(),
            "author": self.author.to_json(),
            "comment": str(self.comment),
            "created": self.created.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "modified": self.modified.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "anamlObject": (lambda v: v and v.to_json())(self.anamlObject)
        }


@dataclasses.dataclass(frozen=True)
class Approval:
    """Approval of a merge request.
    
    Args:
        id (ApprovalId): A data field.
        version (ApprovalVersionId): A data field.
        predecessor (typing.Optional[ApprovalVersionId]): A data field.
        mergeRequestId (MergeRequestId): A data field.
        approvedBy (UserId): A data field.
        approvalTime (datetime.datetime): A data field.
        approvedCommit (CommitId): A data field.
        comment (typing.Optional[str]): A data field.
    """
    
    id: ApprovalId
    version: ApprovalVersionId
    predecessor: typing.Optional[ApprovalVersionId]
    mergeRequestId: MergeRequestId
    approvedBy: UserId
    approvalTime: datetime.datetime
    approvedCommit: CommitId
    comment: typing.Optional[str]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for Approval data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": ApprovalId.json_schema(),
                "version": ApprovalVersionId.json_schema(),
                "predecessor": {
                    "oneOf": [
                        {"type": "null"},
                        ApprovalVersionId.json_schema(),
                    ]
                },
                "mergeRequestId": MergeRequestId.json_schema(),
                "approvedBy": UserId.json_schema(),
                "approvalTime": {
                    "type": "string",
                    "format": "date-time"
                },
                "approvedCommit": CommitId.json_schema(),
                "comment": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                }
            },
            "required": [
                "id",
                "version",
                "mergeRequestId",
                "approvedBy",
                "approvalTime",
                "approvedCommit",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> Approval:
        """Validate and parse JSON data into an instance of Approval.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Approval.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return Approval(
                id=ApprovalId.from_json(data["id"]),
                version=ApprovalVersionId.from_json(data["version"]),
                predecessor=(
                    lambda v: v and ApprovalVersionId.from_json(v)
                )(
                    data.get("predecessor", None)
                ),
                mergeRequestId=MergeRequestId.from_json(data["mergeRequestId"]),
                approvedBy=UserId.from_json(data["approvedBy"]),
                approvalTime=isodate.parse_datetime(data["approvalTime"]),
                approvedCommit=CommitId.from_json(data["approvedCommit"]),
                comment=(lambda v: v and str(v))(data.get("comment", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing Approval",
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
            "version": self.version.to_json(),
            "predecessor": (lambda v: v and v.to_json())(self.predecessor),
            "mergeRequestId": self.mergeRequestId.to_json(),
            "approvedBy": self.approvedBy.to_json(),
            "approvalTime": self.approvalTime.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "approvedCommit": self.approvedCommit.to_json(),
            "comment": (lambda v: v and str(v))(self.comment)
        }


@dataclasses.dataclass(frozen=True)
class ApprovalCreationRequest:
    """Request to create a new approval on a merge request.
    
    Args:
        approvedCommit (CommitId): A data field.
        comment (typing.Optional[str]): A data field.
    """
    
    approvedCommit: CommitId
    comment: typing.Optional[str]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ApprovalCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "approvedCommit": CommitId.json_schema(),
                "comment": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                }
            },
            "required": [
                "approvedCommit",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ApprovalCreationRequest:
        """Validate and parse JSON data into an instance of ApprovalCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ApprovalCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ApprovalCreationRequest(
                approvedCommit=CommitId.from_json(data["approvedCommit"]),
                comment=(lambda v: v and str(v))(data.get("comment", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing ApprovalCreationRequest",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "approvedCommit": self.approvedCommit.to_json(),
            "comment": (lambda v: v and str(v))(self.comment)
        }

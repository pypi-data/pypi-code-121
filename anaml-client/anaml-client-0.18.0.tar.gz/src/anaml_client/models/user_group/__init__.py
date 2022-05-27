"""Generated implementation of user_group."""

# WARNING DO NOT EDIT
# This code was generated from user-group.mcn

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

from ..roles import Role
from ..user import UserId


@dataclasses.dataclass(frozen=True)
class UserGroupId:
    """Unique identifier for a user group.
    
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
        """Return the JSON schema for UserGroupId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> UserGroupId:
        """Validate and parse JSON data into an instance of UserGroupId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of UserGroupId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserGroupId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing UserGroupId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> UserGroupId:
        """Parse a JSON string such as a dictionary key."""
        return UserGroupId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class UserGroupVersionId:
    """Unique identifier a specific version of a user group.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for UserGroupVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> UserGroupVersionId:
        """Validate and parse JSON data into an instance of UserGroupVersionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of UserGroupVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserGroupVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing UserGroupVersionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> UserGroupVersionId:
        """Parse a JSON string such as a dictionary key."""
        return UserGroupVersionId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class UserGroupName:
    """Unique name of a user group.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for UserGroupName data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> UserGroupName:
        """Validate and parse JSON data into an instance of UserGroupName.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of UserGroupName.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserGroupName(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing UserGroupName", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> UserGroupName:
        """Parse a JSON string such as a dictionary key."""
        return UserGroupName(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class ExternalGroupId:
    """Unique identifier for external identity provider.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ExternalGroupId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ExternalGroupId:
        """Validate and parse JSON data into an instance of ExternalGroupId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ExternalGroupId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ExternalGroupId(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing ExternalGroupId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> ExternalGroupId:
        """Parse a JSON string such as a dictionary key."""
        return ExternalGroupId(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


class UserGroupMemberSource(enum.Enum):
    """User group member source type."""
    Anaml = "anaml"
    """Created internally via Anaml API."""
    External = "external"
    """Imported from external identity provider."""
    
    @classmethod
    def json_schema(cls) -> dict:
        """JSON schema for 'UserGroupMemberSource'.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [
                        "anaml",
                        "external",
                    ]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> UserGroupMemberSource:
        """Validate and parse JSON data into an instance of UserGroupMemberSource.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of UserGroupMemberSource.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserGroupMemberSource(str(data['adt_type']))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing UserGroupMemberSource", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            JSON data ready to be serialised.
        """
        return {'adt_type': self.value}
    
    @classmethod
    def from_json_key(cls, data: str) -> UserGroupMemberSource:
        """Validate and parse a value from a JSON dictionary key.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of UserGroupMemberSource.
        """
        return UserGroupMemberSource(str(data))
    
    def to_json_key(self) -> str:
        """Serialised this instanse as a JSON string for use as a dictionary key.
        
        Returns:
            A JSON string ready to be used as a key.
        """
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class UserGroupMember:
    """User group member.
    
    Args:
        userId (UserId): A data field.
        source (UserGroupMemberSource): A data field.
    """
    
    userId: UserId
    source: UserGroupMemberSource
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for UserGroupMember data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "userId": UserId.json_schema(),
                "source": UserGroupMemberSource.json_schema()
            },
            "required": [
                "userId",
                "source",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> UserGroupMember:
        """Validate and parse JSON data into an instance of UserGroupMember.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of UserGroupMember.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserGroupMember(
                userId=UserId.from_json(data["userId"]),
                source=UserGroupMemberSource.from_json(data["source"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing UserGroupMember",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "userId": self.userId.to_json(),
            "source": self.source.to_json()
        }


@dataclasses.dataclass(frozen=True)
class UserGroup:
    """Group of Anaml users.
    
    Args:
        id (UserGroupId): A data field.
        version (UserGroupVersionId): A data field.
        name (UserGroupName): A data field.
        description (str): A data field.
        members (typing.List[UserGroupMember]): A data field.
        created (datetime.datetime): A data field.
        modified (datetime.datetime): A data field.
        roles (typing.List[Role]): A data field.
        predecessor (typing.Optional[UserGroupVersionId]): A data field.
        externalGroupId (typing.Optional[ExternalGroupId]): A data field.
    """
    
    id: UserGroupId
    version: UserGroupVersionId
    name: UserGroupName
    description: str
    members: typing.List[UserGroupMember]
    created: datetime.datetime
    modified: datetime.datetime
    roles: typing.List[Role]
    predecessor: typing.Optional[UserGroupVersionId]
    externalGroupId: typing.Optional[ExternalGroupId]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for UserGroup data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": UserGroupId.json_schema(),
                "version": UserGroupVersionId.json_schema(),
                "name": UserGroupName.json_schema(),
                "description": {
                    "type": "string"
                },
                "members": {
                    "type": "array",
                    "item": UserGroupMember.json_schema()
                },
                "created": {
                    "type": "string",
                    "format": "date-time"
                },
                "modified": {
                    "type": "string",
                    "format": "date-time"
                },
                "roles": {
                    "type": "array",
                    "item": Role.json_schema()
                },
                "predecessor": {
                    "oneOf": [
                        {"type": "null"},
                        UserGroupVersionId.json_schema(),
                    ]
                },
                "externalGroupId": {
                    "oneOf": [
                        {"type": "null"},
                        ExternalGroupId.json_schema(),
                    ]
                }
            },
            "required": [
                "id",
                "version",
                "name",
                "description",
                "members",
                "created",
                "modified",
                "roles",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> UserGroup:
        """Validate and parse JSON data into an instance of UserGroup.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of UserGroup.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserGroup(
                id=UserGroupId.from_json(data["id"]),
                version=UserGroupVersionId.from_json(data["version"]),
                name=UserGroupName.from_json(data["name"]),
                description=str(data["description"]),
                members=[UserGroupMember.from_json(v) for v in data["members"]],
                created=isodate.parse_datetime(data["created"]),
                modified=isodate.parse_datetime(data["modified"]),
                roles=[Role.from_json(v) for v in data["roles"]],
                predecessor=(
                    lambda v: v and UserGroupVersionId.from_json(v)
                )(
                    data.get("predecessor", None)
                ),
                externalGroupId=(
                    lambda v: v and ExternalGroupId.from_json(v)
                )(
                    data.get("externalGroupId", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing UserGroup",
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
            "name": self.name.to_json(),
            "description": str(self.description),
            "members": [v.to_json() for v in self.members],
            "created": self.created.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "modified": self.modified.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "roles": [v.to_json() for v in self.roles],
            "predecessor": (lambda v: v and v.to_json())(self.predecessor),
            "externalGroupId": (lambda v: v and v.to_json())(self.externalGroupId)
        }


@dataclasses.dataclass(frozen=True)
class UserGroupCreationRequest:
    """Request to create a new user group.
    
    Args:
        name (UserGroupName): A data field.
        description (str): A data field.
        roles (typing.List[Role]): A data field.
        members (typing.List[UserGroupMember]): A data field.
        externalGroupId (typing.Optional[ExternalGroupId]): A data field.
    """
    
    name: UserGroupName
    description: str
    roles: typing.List[Role]
    members: typing.List[UserGroupMember]
    externalGroupId: typing.Optional[ExternalGroupId]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for UserGroupCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "name": UserGroupName.json_schema(),
                "description": {
                    "type": "string"
                },
                "roles": {
                    "type": "array",
                    "item": Role.json_schema()
                },
                "members": {
                    "type": "array",
                    "item": UserGroupMember.json_schema()
                },
                "externalGroupId": {
                    "oneOf": [
                        {"type": "null"},
                        ExternalGroupId.json_schema(),
                    ]
                }
            },
            "required": [
                "name",
                "description",
                "roles",
                "members",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> UserGroupCreationRequest:
        """Validate and parse JSON data into an instance of UserGroupCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of UserGroupCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserGroupCreationRequest(
                name=UserGroupName.from_json(data["name"]),
                description=str(data["description"]),
                roles=[Role.from_json(v) for v in data["roles"]],
                members=[UserGroupMember.from_json(v) for v in data["members"]],
                externalGroupId=(
                    lambda v: v and ExternalGroupId.from_json(v)
                )(
                    data.get("externalGroupId", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing UserGroupCreationRequest",
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
            "roles": [v.to_json() for v in self.roles],
            "members": [v.to_json() for v in self.members],
            "externalGroupId": (lambda v: v and v.to_json())(self.externalGroupId)
        }

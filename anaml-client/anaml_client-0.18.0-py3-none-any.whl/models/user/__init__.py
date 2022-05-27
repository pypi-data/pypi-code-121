"""Generated implementation of user."""

# WARNING DO NOT EDIT
# This code was generated from user.mcn

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
class UserId:
    """Unique identifier of a user, internal to Anaml.
    
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
        """Return the JSON schema for UserId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> UserId:
        """Validate and parse JSON data into an instance of UserId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of UserId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing UserId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> UserId:
        """Parse a JSON string such as a dictionary key."""
        return UserId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class UserEmail:
    """Unique email of a user.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for UserEmail data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> UserEmail:
        """Validate and parse JSON data into an instance of UserEmail.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of UserEmail.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserEmail(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing UserEmail", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> UserEmail:
        """Parse a JSON string such as a dictionary key."""
        return UserEmail(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class User:
    """Details of a user account.
    
    Args:
        id (UserId): A data field.
        email (UserEmail): A data field.
        name (str): A data field.
        givenName (typing.Optional[str]): A data field.
        surname (typing.Optional[str]): A data field.
        lastLogin (typing.Optional[datetime.datetime]): A data field.
        created (typing.Optional[datetime.datetime]): A data field.
        modified (typing.Optional[datetime.datetime]): A data field.
        roles (typing.List[Role]): A data field.
        inheritedRoles (typing.List[Role]): A data field.
        groups (typing.List[UserGroupId]): A data field.
    """
    
    id: UserId
    email: UserEmail
    name: str
    givenName: typing.Optional[str]
    surname: typing.Optional[str]
    lastLogin: typing.Optional[datetime.datetime]
    created: typing.Optional[datetime.datetime]
    modified: typing.Optional[datetime.datetime]
    roles: typing.List[Role]
    inheritedRoles: typing.List[Role]
    groups: typing.List[UserGroupId]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for User data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": UserId.json_schema(),
                "email": UserEmail.json_schema(),
                "name": {
                    "type": "string"
                },
                "givenName": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "surname": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "lastLogin": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string", "format": "date-time"},
                    ]
                },
                "created": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string", "format": "date-time"},
                    ]
                },
                "modified": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string", "format": "date-time"},
                    ]
                },
                "roles": {
                    "type": "array",
                    "item": Role.json_schema()
                },
                "inheritedRoles": {
                    "type": "array",
                    "item": Role.json_schema()
                },
                "groups": {
                    "type": "array",
                    "item": UserGroupId.json_schema()
                }
            },
            "required": [
                "id",
                "email",
                "name",
                "roles",
                "inheritedRoles",
                "groups",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> User:
        """Validate and parse JSON data into an instance of User.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of User.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return User(
                id=UserId.from_json(data["id"]),
                email=UserEmail.from_json(data["email"]),
                name=str(data["name"]),
                givenName=(lambda v: v and str(v))(data.get("givenName", None)),
                surname=(lambda v: v and str(v))(data.get("surname", None)),
                lastLogin=(
                    lambda v: v and isodate.parse_datetime(v)
                )(
                    data.get("lastLogin", None)
                ),
                created=(lambda v: v and isodate.parse_datetime(v))(data.get("created", None)),
                modified=(
                    lambda v: v and isodate.parse_datetime(v)
                )(
                    data.get("modified", None)
                ),
                roles=[Role.from_json(v) for v in data["roles"]],
                inheritedRoles=[Role.from_json(v) for v in data["inheritedRoles"]],
                groups=[UserGroupId.from_json(v) for v in data["groups"]],
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing User",
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
            "email": self.email.to_json(),
            "name": str(self.name),
            "givenName": (lambda v: v and str(v))(self.givenName),
            "surname": (lambda v: v and str(v))(self.surname),
            "lastLogin": (lambda v: v and v.strftime('%Y-%m-%dT%H:%M:%S.%f%z'))(self.lastLogin),
            "created": (lambda v: v and v.strftime('%Y-%m-%dT%H:%M:%S.%f%z'))(self.created),
            "modified": (lambda v: v and v.strftime('%Y-%m-%dT%H:%M:%S.%f%z'))(self.modified),
            "roles": [v.to_json() for v in self.roles],
            "inheritedRoles": [v.to_json() for v in self.inheritedRoles],
            "groups": [v.to_json() for v in self.groups]
        }


@dataclasses.dataclass(frozen=True)
class UserCreationRequest:
    """Request to create a new user account.
    
    Args:
        email (UserEmail): A data field.
        password (typing.Optional[str]): A data field.
        name (str): A data field.
        givenName (typing.Optional[str]): A data field.
        surname (typing.Optional[str]): A data field.
        roles (typing.List[Role]): A data field.
    """
    
    email: UserEmail
    password: typing.Optional[str]
    name: str
    givenName: typing.Optional[str]
    surname: typing.Optional[str]
    roles: typing.List[Role]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for UserCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "email": UserEmail.json_schema(),
                "password": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "name": {
                    "type": "string"
                },
                "givenName": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "surname": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "roles": {
                    "type": "array",
                    "item": Role.json_schema()
                }
            },
            "required": [
                "email",
                "name",
                "roles",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> UserCreationRequest:
        """Validate and parse JSON data into an instance of UserCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of UserCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserCreationRequest(
                email=UserEmail.from_json(data["email"]),
                password=(lambda v: v and str(v))(data.get("password", None)),
                name=str(data["name"]),
                givenName=(lambda v: v and str(v))(data.get("givenName", None)),
                surname=(lambda v: v and str(v))(data.get("surname", None)),
                roles=[Role.from_json(v) for v in data["roles"]],
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing UserCreationRequest",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "email": self.email.to_json(),
            "password": (lambda v: v and str(v))(self.password),
            "name": str(self.name),
            "givenName": (lambda v: v and str(v))(self.givenName),
            "surname": (lambda v: v and str(v))(self.surname),
            "roles": [v.to_json() for v in self.roles]
        }


@dataclasses.dataclass(frozen=True)
class UserUpdateRequest:
    """Request to update a user account.
    
    Args:
        email (UserEmail): A data field.
        name (str): A data field.
        givenName (typing.Optional[str]): A data field.
        surname (typing.Optional[str]): A data field.
    """
    
    email: UserEmail
    name: str
    givenName: typing.Optional[str]
    surname: typing.Optional[str]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for UserUpdateRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "email": UserEmail.json_schema(),
                "name": {
                    "type": "string"
                },
                "givenName": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "surname": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                }
            },
            "required": [
                "email",
                "name",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> UserUpdateRequest:
        """Validate and parse JSON data into an instance of UserUpdateRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of UserUpdateRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserUpdateRequest(
                email=UserEmail.from_json(data["email"]),
                name=str(data["name"]),
                givenName=(lambda v: v and str(v))(data.get("givenName", None)),
                surname=(lambda v: v and str(v))(data.get("surname", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing UserUpdateRequest",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "email": self.email.to_json(),
            "name": str(self.name),
            "givenName": (lambda v: v and str(v))(self.givenName),
            "surname": (lambda v: v and str(v))(self.surname)
        }


@dataclasses.dataclass(frozen=True)
class UserUpdateRequestWithRoles:
    """Request to update a user account and roles they are assigned.
    
    Args:
        email (UserEmail): A data field.
        name (str): A data field.
        givenName (typing.Optional[str]): A data field.
        surname (typing.Optional[str]): A data field.
        roles (typing.List[Role]): A data field.
    """
    
    email: UserEmail
    name: str
    givenName: typing.Optional[str]
    surname: typing.Optional[str]
    roles: typing.List[Role]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for UserUpdateRequestWithRoles data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "email": UserEmail.json_schema(),
                "name": {
                    "type": "string"
                },
                "givenName": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "surname": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "roles": {
                    "type": "array",
                    "item": Role.json_schema()
                }
            },
            "required": [
                "email",
                "name",
                "roles",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> UserUpdateRequestWithRoles:
        """Validate and parse JSON data into an instance of UserUpdateRequestWithRoles.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of UserUpdateRequestWithRoles.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserUpdateRequestWithRoles(
                email=UserEmail.from_json(data["email"]),
                name=str(data["name"]),
                givenName=(lambda v: v and str(v))(data.get("givenName", None)),
                surname=(lambda v: v and str(v))(data.get("surname", None)),
                roles=[Role.from_json(v) for v in data["roles"]],
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing UserUpdateRequestWithRoles",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "email": self.email.to_json(),
            "name": str(self.name),
            "givenName": (lambda v: v and str(v))(self.givenName),
            "surname": (lambda v: v and str(v))(self.surname),
            "roles": [v.to_json() for v in self.roles]
        }

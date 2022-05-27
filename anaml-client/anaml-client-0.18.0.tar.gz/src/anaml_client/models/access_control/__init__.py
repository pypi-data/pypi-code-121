"""Generated implementation of access_control."""

# WARNING DO NOT EDIT
# This code was generated from access-control.mcn

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

from ..user_group import UserGroupId


@dataclasses.dataclass(frozen=True)
class PrincipalId(abc.ABC):
    """Identifies the subject principal of an access rule.
    
    Args:
        id (UserGroupId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: UserGroupId
    
    @classmethod
    def json_schema(cls) -> PrincipalId:
        """JSON schema for variant PrincipalId.
        
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
    def from_json(cls, data: dict) -> PrincipalId:
        """Validate and parse JSON data into an instance of PrincipalId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of PrincipalId.
        
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
            logging.debug("Invalid JSON data received while parsing PrincipalId", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class UserGroupIdPrincipalId(PrincipalId):
    """A user group principal.
    
    Args:
        id (UserGroupId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "usergroupid"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: UserGroupId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for UserGroupIdPrincipalId data.
        
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
                "id": UserGroupId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> UserGroupIdPrincipalId:
        """Validate and parse JSON data into an instance of UserGroupIdPrincipalId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of UserGroupIdPrincipalId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserGroupIdPrincipalId(
                id=UserGroupId.from_json(data["id"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing UserGroupIdPrincipalId",
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
class ResourcePattern:
    """Pattern to match path or table within a source or destination.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ResourcePattern data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ResourcePattern:
        """Validate and parse JSON data into an instance of ResourcePattern.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ResourcePattern.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ResourcePattern(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing ResourcePattern", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> ResourcePattern:
        """Parse a JSON string such as a dictionary key."""
        return ResourcePattern(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class MaskingRule(abc.ABC):
    """Masking rule.
    
    Args:
        expression (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    expression: str
    
    @classmethod
    def json_schema(cls) -> MaskingRule:
        """JSON schema for variant MaskingRule.
        
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
    def from_json(cls, data: dict) -> MaskingRule:
        """Validate and parse JSON data into an instance of MaskingRule.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of MaskingRule.
        
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
            logging.debug("Invalid JSON data received while parsing MaskingRule", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class Filter(MaskingRule):
    """Row filter.
    
    Args:
        expression (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "filter"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    expression: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for Filter data.
        
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
                "expression": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "expression",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> Filter:
        """Validate and parse JSON data into an instance of Filter.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Filter.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return Filter(
                expression=str(data["expression"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing Filter",
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
            "expression": str(self.expression)
        }


@dataclasses.dataclass(frozen=True)
class Mask(MaskingRule):
    """Column mask.
    
    Args:
        column (str): A data field.
        expression (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "mask"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    column: str
    expression: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for Mask data.
        
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
                "column": {
                    "type": "string"
                },
                "expression": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "column",
                "expression",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> Mask:
        """Validate and parse JSON data into an instance of Mask.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Mask.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return Mask(
                column=str(data["column"]),
                expression=str(data["expression"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing Mask",
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
            "column": str(self.column),
            "expression": str(self.expression)
        }


@dataclasses.dataclass(frozen=True)
class AccessRule:
    """Access control rule.
    
    Each access control rule may contain three fields:
    
    1. patterns to match against paths or table names
    2. principals (user groups)
    3. optional masking rules (row filtering or column masking) to be applied for matching resource & principals
    (not used for destinations)
    
    Args:
        resource (ResourcePattern): A data field.
        principals (typing.List[PrincipalId]): A data field.
        maskingRules (typing.Optional[typing.List[MaskingRule]]): A data field.
    """
    
    resource: ResourcePattern
    principals: typing.List[PrincipalId]
    maskingRules: typing.Optional[typing.List[MaskingRule]]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for AccessRule data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "resource": ResourcePattern.json_schema(),
                "principals": {
                    "type": "array",
                    "item": PrincipalId.json_schema()
                },
                "maskingRules": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "array", "item": MaskingRule.json_schema()},
                    ]
                }
            },
            "required": [
                "resource",
                "principals",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> AccessRule:
        """Validate and parse JSON data into an instance of AccessRule.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of AccessRule.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return AccessRule(
                resource=ResourcePattern.from_json(data["resource"]),
                principals=[PrincipalId.from_json(v) for v in data["principals"]],
                maskingRules=(
                    lambda v: v and [MaskingRule.from_json(v) for v in v]
                )(
                    data.get("maskingRules", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing AccessRule",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "resource": self.resource.to_json(),
            "principals": [v.to_json() for v in self.principals],
            "maskingRules": (lambda v: v and [v.to_json() for v in v])(self.maskingRules)
        }

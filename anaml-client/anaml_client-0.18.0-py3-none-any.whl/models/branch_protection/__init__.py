"""Generated implementation of branch_protection."""

# WARNING DO NOT EDIT
# This code was generated from branch-protection.mcn

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

from ..user import UserId
from ..user_group import UserGroupId


@dataclasses.dataclass(frozen=True)
class BranchProtectionId:
    """Unique identifier for branch protection configurations.
    
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
        """Return the JSON schema for BranchProtectionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> BranchProtectionId:
        """Validate and parse JSON data into an instance of BranchProtectionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of BranchProtectionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return BranchProtectionId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing BranchProtectionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> BranchProtectionId:
        """Parse a JSON string such as a dictionary key."""
        return BranchProtectionId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class BranchProtectionVersionId:
    """Unique identifier for specific versions of a branch protection configuration.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for BranchProtectionVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> BranchProtectionVersionId:
        """Validate and parse JSON data into an instance of BranchProtectionVersionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of BranchProtectionVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return BranchProtectionVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing BranchProtectionVersionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> BranchProtectionVersionId:
        """Parse a JSON string such as a dictionary key."""
        return BranchProtectionVersionId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class BranchProtectionPattern:
    """Branch name pattern.
    
    Follows SQL string matching syntax.
    
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for BranchProtectionPattern data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> BranchProtectionPattern:
        """Validate and parse JSON data into an instance of BranchProtectionPattern.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of BranchProtectionPattern.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return BranchProtectionPattern(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing BranchProtectionPattern", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> BranchProtectionPattern:
        """Parse a JSON string such as a dictionary key."""
        return BranchProtectionPattern(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class PrincipalId(abc.ABC):
    """Identifies the subject principal of a branch protection rule."""
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
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
class UserIdPrincipalId(PrincipalId):
    """A specific user principal.
    
    Args:
        id (UserId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "userid"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: UserId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for UserIdPrincipalId data.
        
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
                "id": UserId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> UserIdPrincipalId:
        """Validate and parse JSON data into an instance of UserIdPrincipalId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of UserIdPrincipalId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return UserIdPrincipalId(
                id=UserId.from_json(data["id"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing UserIdPrincipalId",
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
class BranchProtection:
    """A branch protection configuration.
    
    Args:
        id (BranchProtectionId): A data field.
        version (BranchProtectionVersionId): A data field.
        predecessor (typing.Optional[BranchProtectionVersionId]): A data field.
        protectionPattern (BranchProtectionPattern): A data field.
        mergeApprovalRules (typing.List[ApprovalRule]): A data field.
        pushWhitelist (typing.List[PrincipalId]): A data field.
        applyToAdmins (bool): A data field.
        allowBranchDeletion (bool): A data field.
    """
    
    id: BranchProtectionId
    version: BranchProtectionVersionId
    predecessor: typing.Optional[BranchProtectionVersionId]
    protectionPattern: BranchProtectionPattern
    mergeApprovalRules: typing.List[ApprovalRule]
    pushWhitelist: typing.List[PrincipalId]
    applyToAdmins: bool
    allowBranchDeletion: bool
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for BranchProtection data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": BranchProtectionId.json_schema(),
                "version": BranchProtectionVersionId.json_schema(),
                "predecessor": {
                    "oneOf": [
                        {"type": "null"},
                        BranchProtectionVersionId.json_schema(),
                    ]
                },
                "protectionPattern": BranchProtectionPattern.json_schema(),
                "mergeApprovalRules": {
                    "type": "array",
                    "item": ApprovalRule.json_schema()
                },
                "pushWhitelist": {
                    "type": "array",
                    "item": PrincipalId.json_schema()
                },
                "applyToAdmins": {
                    "type": "boolean"
                },
                "allowBranchDeletion": {
                    "type": "boolean"
                }
            },
            "required": [
                "id",
                "version",
                "protectionPattern",
                "mergeApprovalRules",
                "pushWhitelist",
                "applyToAdmins",
                "allowBranchDeletion",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> BranchProtection:
        """Validate and parse JSON data into an instance of BranchProtection.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of BranchProtection.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return BranchProtection(
                id=BranchProtectionId.from_json(data["id"]),
                version=BranchProtectionVersionId.from_json(data["version"]),
                predecessor=(
                    lambda v: v and BranchProtectionVersionId.from_json(v)
                )(
                    data.get("predecessor", None)
                ),
                protectionPattern=BranchProtectionPattern.from_json(data["protectionPattern"]),
                mergeApprovalRules=[ApprovalRule.from_json(v) for v in data["mergeApprovalRules"]],
                pushWhitelist=[PrincipalId.from_json(v) for v in data["pushWhitelist"]],
                applyToAdmins=bool(data["applyToAdmins"]),
                allowBranchDeletion=bool(data["allowBranchDeletion"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing BranchProtection",
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
            "protectionPattern": self.protectionPattern.to_json(),
            "mergeApprovalRules": [v.to_json() for v in self.mergeApprovalRules],
            "pushWhitelist": [v.to_json() for v in self.pushWhitelist],
            "applyToAdmins": self.applyToAdmins,
            "allowBranchDeletion": self.allowBranchDeletion
        }


@dataclasses.dataclass(frozen=True)
class BranchProtectionCreationRequest:
    """Create a new branch protection configuration.
    
    Args:
        protectionPattern (BranchProtectionPattern): A data field.
        mergeApprovalRules (typing.List[ApprovalRule]): A data field.
        pushWhitelist (typing.List[PrincipalId]): A data field.
        applyToAdmins (bool): A data field.
        allowBranchDeletion (bool): A data field.
    """
    
    protectionPattern: BranchProtectionPattern
    mergeApprovalRules: typing.List[ApprovalRule]
    pushWhitelist: typing.List[PrincipalId]
    applyToAdmins: bool
    allowBranchDeletion: bool
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for BranchProtectionCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "protectionPattern": BranchProtectionPattern.json_schema(),
                "mergeApprovalRules": {
                    "type": "array",
                    "item": ApprovalRule.json_schema()
                },
                "pushWhitelist": {
                    "type": "array",
                    "item": PrincipalId.json_schema()
                },
                "applyToAdmins": {
                    "type": "boolean"
                },
                "allowBranchDeletion": {
                    "type": "boolean"
                }
            },
            "required": [
                "protectionPattern",
                "mergeApprovalRules",
                "pushWhitelist",
                "applyToAdmins",
                "allowBranchDeletion",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> BranchProtectionCreationRequest:
        """Validate and parse JSON data into an instance of BranchProtectionCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of BranchProtectionCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return BranchProtectionCreationRequest(
                protectionPattern=BranchProtectionPattern.from_json(data["protectionPattern"]),
                mergeApprovalRules=[ApprovalRule.from_json(v) for v in data["mergeApprovalRules"]],
                pushWhitelist=[PrincipalId.from_json(v) for v in data["pushWhitelist"]],
                applyToAdmins=bool(data["applyToAdmins"]),
                allowBranchDeletion=bool(data["allowBranchDeletion"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing BranchProtectionCreationRequest",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "protectionPattern": self.protectionPattern.to_json(),
            "mergeApprovalRules": [v.to_json() for v in self.mergeApprovalRules],
            "pushWhitelist": [v.to_json() for v in self.pushWhitelist],
            "applyToAdmins": self.applyToAdmins,
            "allowBranchDeletion": self.allowBranchDeletion
        }


@dataclasses.dataclass(frozen=True)
class ApprovalRule(abc.ABC):
    """A branch protection rule."""
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    @classmethod
    def json_schema(cls) -> ApprovalRule:
        """JSON schema for variant ApprovalRule.
        
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
    def from_json(cls, data: dict) -> ApprovalRule:
        """Validate and parse JSON data into an instance of ApprovalRule.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ApprovalRule.
        
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
            logging.debug("Invalid JSON data received while parsing ApprovalRule", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class RestrictedApprovalRule(ApprovalRule):
    """Approval required from specified principals.
    
    Args:
        approvers (typing.List[PrincipalId]): A data field.
        numRequiredApprovals (int): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "restricted"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    approvers: typing.List[PrincipalId]
    numRequiredApprovals: int
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for RestrictedApprovalRule data.
        
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
                "approvers": {
                    "type": "array",
                    "item": PrincipalId.json_schema()
                },
                "numRequiredApprovals": {
                    "type": "integer"
                }
            },
            "required": [
                "adt_type",
                "approvers",
                "numRequiredApprovals",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> RestrictedApprovalRule:
        """Validate and parse JSON data into an instance of RestrictedApprovalRule.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of RestrictedApprovalRule.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return RestrictedApprovalRule(
                approvers=[PrincipalId.from_json(v) for v in data["approvers"]],
                numRequiredApprovals=int(data["numRequiredApprovals"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing RestrictedApprovalRule",
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
            "approvers": [v.to_json() for v in self.approvers],
            "numRequiredApprovals": int(self.numRequiredApprovals)
        }


@dataclasses.dataclass(frozen=True)
class OpenApprovalRule(ApprovalRule):
    """Approval required from any principals.
    
    Args:
        numRequiredApprovals (int): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "open"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    numRequiredApprovals: int
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for OpenApprovalRule data.
        
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
                "numRequiredApprovals": {
                    "type": "integer"
                }
            },
            "required": [
                "adt_type",
                "numRequiredApprovals",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> OpenApprovalRule:
        """Validate and parse JSON data into an instance of OpenApprovalRule.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of OpenApprovalRule.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return OpenApprovalRule(
                numRequiredApprovals=int(data["numRequiredApprovals"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing OpenApprovalRule",
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
            "numRequiredApprovals": int(self.numRequiredApprovals)
        }


@dataclasses.dataclass(frozen=True)
class PassesChecksApprovalRule(ApprovalRule):
    """Merges must have passing checks."""
    
    ADT_TYPE: typing.ClassVar[str] = "passeschecks"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for PassesChecksApprovalRule data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [cls.ADT_TYPE]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> PassesChecksApprovalRule:
        """Validate and parse JSON data into an instance of PassesChecksApprovalRule.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of PassesChecksApprovalRule.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return PassesChecksApprovalRule(
                
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing PassesChecksApprovalRule",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "adt_type": self.ADT_TYPE
        }

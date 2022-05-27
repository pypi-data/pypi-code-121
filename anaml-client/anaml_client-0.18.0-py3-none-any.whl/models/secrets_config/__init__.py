"""Generated implementation of secrets_config."""

# WARNING DO NOT EDIT
# This code was generated from secrets-config.mcn

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
class SecretsConfig(abc.ABC):
    """Configuration for a secret configuration item."""
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    @classmethod
    def json_schema(cls) -> SecretsConfig:
        """JSON schema for variant SecretsConfig.
        
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
    def from_json(cls, data: dict) -> SecretsConfig:
        """Validate and parse JSON data into an instance of SecretsConfig.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of SecretsConfig.
        
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
            logging.debug("Invalid JSON data received while parsing SecretsConfig", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class BasicSecretsConfig(SecretsConfig):
    """A secret passed directly.
    
    Args:
        secret (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "basic"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    secret: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for BasicSecretsConfig data.
        
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
                "secret": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "secret",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> BasicSecretsConfig:
        """Validate and parse JSON data into an instance of BasicSecretsConfig.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of BasicSecretsConfig.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return BasicSecretsConfig(
                secret=str(data["secret"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing BasicSecretsConfig",
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
            "secret": str(self.secret)
        }


@dataclasses.dataclass(frozen=True)
class AWSSMSecretsConfig(SecretsConfig):
    """A secret stored in AWS Secret Manager.
    
    Args:
        secretId (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "awssm"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    secretId: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for AWSSMSecretsConfig data.
        
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
                "secretId": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "secretId",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> AWSSMSecretsConfig:
        """Validate and parse JSON data into an instance of AWSSMSecretsConfig.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of AWSSMSecretsConfig.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return AWSSMSecretsConfig(
                secretId=str(data["secretId"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing AWSSMSecretsConfig",
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
            "secretId": str(self.secretId)
        }


@dataclasses.dataclass(frozen=True)
class GCPSMSecretsConfig(SecretsConfig):
    """A secret stored in GCP Secret Manager.
    
    Args:
        secretProject (str): A data field.
        secretId (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "gcpsm"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    secretProject: str
    secretId: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for GCPSMSecretsConfig data.
        
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
                "secretProject": {
                    "type": "string"
                },
                "secretId": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "secretProject",
                "secretId",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> GCPSMSecretsConfig:
        """Validate and parse JSON data into an instance of GCPSMSecretsConfig.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of GCPSMSecretsConfig.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return GCPSMSecretsConfig(
                secretProject=str(data["secretProject"]),
                secretId=str(data["secretId"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing GCPSMSecretsConfig",
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
            "secretProject": str(self.secretProject),
            "secretId": str(self.secretId)
        }

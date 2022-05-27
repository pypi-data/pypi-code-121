"""Generated implementation of attribute."""

# WARNING DO NOT EDIT
# This code was generated from attribute.mcn

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

from ..secrets_config import SecretsConfig


@dataclasses.dataclass(frozen=True)
class Attribute:
    """An attribute.
    
    Args:
        key (str): A data field.
        value (str): A data field.
    """
    
    key: str
    value: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for Attribute data.
        
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
    def from_json(cls, data: dict) -> Attribute:
        """Validate and parse JSON data into an instance of Attribute.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Attribute.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return Attribute(
                key=str(data["key"]),
                value=str(data["value"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing Attribute",
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
class SensitiveAttribute:
    """A sensitive attribute, stored in a secret manager.
    
    Args:
        key (str): A data field.
        valueConfig (SecretsConfig): A data field.
    """
    
    key: str
    valueConfig: SecretsConfig
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for SensitiveAttribute data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string"
                },
                "valueConfig": SecretsConfig.json_schema()
            },
            "required": [
                "key",
                "valueConfig",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> SensitiveAttribute:
        """Validate and parse JSON data into an instance of SensitiveAttribute.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of SensitiveAttribute.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return SensitiveAttribute(
                key=str(data["key"]),
                valueConfig=SecretsConfig.from_json(data["valueConfig"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing SensitiveAttribute",
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
            "valueConfig": self.valueConfig.to_json()
        }

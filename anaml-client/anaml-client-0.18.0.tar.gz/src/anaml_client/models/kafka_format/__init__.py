"""Generated implementation of kafka_format."""

# WARNING DO NOT EDIT
# This code was generated from kafka-format.mcn

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


class KafkaFormat(enum.Enum):
    """Supported data format for Kafka."""
    Avro = "avro"
    """Avro Format."""
    Json = "json"
    """Json Format."""
    
    @classmethod
    def json_schema(cls) -> dict:
        """JSON schema for 'KafkaFormat'.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [
                        "avro",
                        "json",
                    ]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> KafkaFormat:
        """Validate and parse JSON data into an instance of KafkaFormat.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of KafkaFormat.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return KafkaFormat(str(data['adt_type']))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing KafkaFormat", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            JSON data ready to be serialised.
        """
        return {'adt_type': self.value}
    
    @classmethod
    def from_json_key(cls, data: str) -> KafkaFormat:
        """Validate and parse a value from a JSON dictionary key.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of KafkaFormat.
        """
        return KafkaFormat(str(data))
    
    def to_json_key(self) -> str:
        """Serialised this instanse as a JSON string for use as a dictionary key.
        
        Returns:
            A JSON string ready to be used as a key.
        """
        return str(self.value)

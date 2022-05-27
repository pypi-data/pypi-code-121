"""Generated implementation of health."""

# WARNING DO NOT EDIT
# This code was generated from health.mcn

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
class HealthStatus(abc.ABC):
    """Health status types.
    
    Args:
        indicator (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    indicator: str
    
    @classmethod
    def json_schema(cls) -> HealthStatus:
        """JSON schema for variant HealthStatus.
        
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
    def from_json(cls, data: dict) -> HealthStatus:
        """Validate and parse JSON data into an instance of HealthStatus.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of HealthStatus.
        
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
            logging.debug("Invalid JSON data received while parsing HealthStatus", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class Healthy(HealthStatus):
    """Healthy status.
    
    Args:
        indicator (str): A data field.
        message (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "healthy"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    indicator: str
    message: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for Healthy data.
        
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
                "indicator": {
                    "type": "string"
                },
                "message": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "indicator",
                "message",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> Healthy:
        """Validate and parse JSON data into an instance of Healthy.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Healthy.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return Healthy(
                indicator=str(data["indicator"]),
                message=str(data["message"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing Healthy",
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
            "indicator": str(self.indicator),
            "message": str(self.message)
        }


@dataclasses.dataclass(frozen=True)
class Unhealthy(HealthStatus):
    """Unhealthy status.
    
    Args:
        indicator (str): A data field.
        reason (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "unhealthy"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    indicator: str
    reason: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for Unhealthy data.
        
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
                "indicator": {
                    "type": "string"
                },
                "reason": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "indicator",
                "reason",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> Unhealthy:
        """Validate and parse JSON data into an instance of Unhealthy.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Unhealthy.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return Unhealthy(
                indicator=str(data["indicator"]),
                reason=str(data["reason"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing Unhealthy",
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
            "indicator": str(self.indicator),
            "reason": str(self.reason)
        }


@dataclasses.dataclass(frozen=True)
class HealthResponse:
    """Health status across all health indicators.
    
    Args:
        healthy (bool): A data field.
        indicators (typing.List[HealthStatus]): A data field.
    """
    
    healthy: bool
    indicators: typing.List[HealthStatus]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for HealthResponse data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "healthy": {
                    "type": "boolean"
                },
                "indicators": {
                    "type": "array",
                    "item": HealthStatus.json_schema()
                }
            },
            "required": [
                "healthy",
                "indicators",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> HealthResponse:
        """Validate and parse JSON data into an instance of HealthResponse.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of HealthResponse.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return HealthResponse(
                healthy=bool(data["healthy"]),
                indicators=[HealthStatus.from_json(v) for v in data["indicators"]],
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing HealthResponse",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "healthy": self.healthy,
            "indicators": [v.to_json() for v in self.indicators]
        }

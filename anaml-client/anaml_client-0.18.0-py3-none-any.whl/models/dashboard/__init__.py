"""Generated implementation of dashboard."""

# WARNING DO NOT EDIT
# This code was generated from dashboard.mcn

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
class FeatureStoresDashboard:
    """Statistics about Feature Stores to display on the dashboard.
    
    Args:
        totalFeatureStores (int): A data field.
        enabledFeatureStores (int): A data field.
    """
    
    totalFeatureStores: int
    enabledFeatureStores: int
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for FeatureStoresDashboard data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "totalFeatureStores": {
                    "type": "integer"
                },
                "enabledFeatureStores": {
                    "type": "integer"
                }
            },
            "required": [
                "totalFeatureStores",
                "enabledFeatureStores",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FeatureStoresDashboard:
        """Validate and parse JSON data into an instance of FeatureStoresDashboard.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureStoresDashboard.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureStoresDashboard(
                totalFeatureStores=int(data["totalFeatureStores"]),
                enabledFeatureStores=int(data["enabledFeatureStores"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing FeatureStoresDashboard",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "totalFeatureStores": int(self.totalFeatureStores),
            "enabledFeatureStores": int(self.enabledFeatureStores)
        }

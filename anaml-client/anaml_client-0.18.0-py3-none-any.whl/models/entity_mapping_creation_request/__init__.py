"""Generated implementation of entity_mapping_creation_request."""

# WARNING DO NOT EDIT
# This code was generated from entity-mapping-creation-request.mcn

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

from ..entity import EntityId
from ..feature_id import FeatureId


@dataclasses.dataclass(frozen=True)
class EntityMappingCreationRequest:
    """Request to create a new entity mapping.
    
    Args:
        from_ (EntityId): A data field.
        to (EntityId): A data field.
        mapping (FeatureId): A data field.
    """
    
    from_: EntityId
    to: EntityId
    mapping: FeatureId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EntityMappingCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "from": EntityId.json_schema(),
                "to": EntityId.json_schema(),
                "mapping": FeatureId.json_schema()
            },
            "required": [
                "from",
                "to",
                "mapping",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EntityMappingCreationRequest:
        """Validate and parse JSON data into an instance of EntityMappingCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EntityMappingCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EntityMappingCreationRequest(
                from_=EntityId.from_json(data["from"]),
                to=EntityId.from_json(data["to"]),
                mapping=FeatureId.from_json(data["mapping"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EntityMappingCreationRequest",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "from": self.from_.to_json(),
            "to": self.to.to_json(),
            "mapping": self.mapping.to_json()
        }

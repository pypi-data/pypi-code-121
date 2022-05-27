"""Generated implementation of feature_set_creation_request."""

# WARNING DO NOT EDIT
# This code was generated from feature-set-creation-request.mcn

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

from ..attribute import Attribute
from ..entity import EntityId
from ..feature_id import FeatureId
from ..feature_set import FeatureSetName
from ..label import Label


@dataclasses.dataclass(frozen=True)
class FeatureSetCreationRequest:
    """Request to create a new feature set.
    
    Args:
        name (FeatureSetName): A data field.
        entity (EntityId): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        features (typing.List[FeatureId]): A data field.
    """
    
    name: FeatureSetName
    entity: EntityId
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    features: typing.List[FeatureId]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for FeatureSetCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "name": FeatureSetName.json_schema(),
                "entity": EntityId.json_schema(),
                "description": {
                    "type": "string"
                },
                "labels": {
                    "type": "array",
                    "item": Label.json_schema()
                },
                "attributes": {
                    "type": "array",
                    "item": Attribute.json_schema()
                },
                "features": {
                    "type": "array",
                    "item": FeatureId.json_schema()
                }
            },
            "required": [
                "name",
                "entity",
                "description",
                "labels",
                "attributes",
                "features",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FeatureSetCreationRequest:
        """Validate and parse JSON data into an instance of FeatureSetCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureSetCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureSetCreationRequest(
                name=FeatureSetName.from_json(data["name"]),
                entity=EntityId.from_json(data["entity"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                features=[FeatureId.from_json(v) for v in data["features"]],
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing FeatureSetCreationRequest",
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
            "entity": self.entity.to_json(),
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "features": [v.to_json() for v in self.features]
        }

"""Generated implementation of entity_creation_request."""

# WARNING DO NOT EDIT
# This code was generated from entity-creation-request.mcn

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
from ..entity import EntityId, EntityName, EntityVersionId
from ..label import Label


@dataclasses.dataclass(frozen=True)
class EntityCreationRequest:
    """Request to create a new entity.
    
    Args:
        id (EntityId): A data field.
        name (EntityName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        defaultColumn (str): A data field.
        version (EntityVersionId): A data field.
    """
    
    id: EntityId
    name: EntityName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    defaultColumn: str
    version: EntityVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EntityCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": EntityId.json_schema(),
                "name": EntityName.json_schema(),
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
                "defaultColumn": {
                    "type": "string"
                },
                "version": EntityVersionId.json_schema()
            },
            "required": [
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "defaultColumn",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EntityCreationRequest:
        """Validate and parse JSON data into an instance of EntityCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EntityCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EntityCreationRequest(
                id=EntityId.from_json(data["id"]),
                name=EntityName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                defaultColumn=str(data["defaultColumn"]),
                version=EntityVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EntityCreationRequest",
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
            "name": self.name.to_json(),
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "defaultColumn": str(self.defaultColumn),
            "version": self.version.to_json()
        }

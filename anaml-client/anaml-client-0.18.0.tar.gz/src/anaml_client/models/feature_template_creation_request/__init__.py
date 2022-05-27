"""Generated implementation of feature_template_creation_request."""

# WARNING DO NOT EDIT
# This code was generated from feature-template-creation-request.mcn

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

from ..aggregate import AggregateExpression
from ..attribute import Attribute
from ..entity import EntityId
from ..event_window import EventWindow
from ..feature_id import FeatureId
from ..feature_template import TemplateName
from ..filter_expression import FilterExpression
from ..label import Label
from ..post_aggregate_expression import PostAggregateExpression
from ..select_expression import SelectExpression
from ..table import TableId


@dataclasses.dataclass(frozen=True)
class FeatureTemplateCreationRequest(abc.ABC):
    """Request to create a new feature template.
    
    Args:
        attributes (typing.List[Attribute]): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        name (TemplateName): A data field.
        select (SelectExpression): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    attributes: typing.List[Attribute]
    description: str
    labels: typing.List[Label]
    name: TemplateName
    select: SelectExpression
    
    @classmethod
    def json_schema(cls) -> FeatureTemplateCreationRequest:
        """JSON schema for variant FeatureTemplateCreationRequest.
        
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
    def from_json(cls, data: dict) -> FeatureTemplateCreationRequest:
        """Validate and parse JSON data into an instance of FeatureTemplateCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureTemplateCreationRequest.
        
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
            logging.debug("Invalid JSON data received while parsing FeatureTemplateCreationRequest", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class EventFeatureTemplateCreationRequest(FeatureTemplateCreationRequest):
    """Create a new event feature template.
    
    Args:
        name (TemplateName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        table (TableId): A data field.
        window (EventWindow): A data field.
        select (SelectExpression): A data field.
        filter (typing.Optional[FilterExpression]): A data field.
        aggregate (typing.Optional[AggregateExpression]): A data field.
        postAggregateExpr (typing.Optional[PostAggregateExpression]): A data field.
        entityRestrictions (typing.Optional[typing.List[EntityId]]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "event"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: TemplateName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    table: TableId
    window: EventWindow
    select: SelectExpression
    filter: typing.Optional[FilterExpression]
    aggregate: typing.Optional[AggregateExpression]
    postAggregateExpr: typing.Optional[PostAggregateExpression]
    entityRestrictions: typing.Optional[typing.List[EntityId]]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EventFeatureTemplateCreationRequest data.
        
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
                "name": TemplateName.json_schema(),
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
                "table": TableId.json_schema(),
                "window": EventWindow.json_schema(),
                "select": SelectExpression.json_schema(),
                "filter": {
                    "oneOf": [
                        {"type": "null"},
                        FilterExpression.json_schema(),
                    ]
                },
                "aggregate": {
                    "oneOf": [
                        {"type": "null"},
                        AggregateExpression.json_schema(),
                    ]
                },
                "postAggregateExpr": {
                    "oneOf": [
                        {"type": "null"},
                        PostAggregateExpression.json_schema(),
                    ]
                },
                "entityRestrictions": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "array", "item": EntityId.json_schema()},
                    ]
                }
            },
            "required": [
                "adt_type",
                "name",
                "description",
                "labels",
                "attributes",
                "table",
                "window",
                "select",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EventFeatureTemplateCreationRequest:
        """Validate and parse JSON data into an instance of EventFeatureTemplateCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EventFeatureTemplateCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EventFeatureTemplateCreationRequest(
                name=TemplateName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                table=TableId.from_json(data["table"]),
                window=EventWindow.from_json(data["window"]),
                select=SelectExpression.from_json(data["select"]),
                filter=(
                    lambda v: v and FilterExpression.from_json(v)
                )(
                    data.get("filter", None)
                ),
                aggregate=(
                    lambda v: v and AggregateExpression.from_json(v)
                )(
                    data.get("aggregate", None)
                ),
                postAggregateExpr=(
                    lambda v: v and PostAggregateExpression.from_json(v)
                )(
                    data.get("postAggregateExpr", None)
                ),
                entityRestrictions=(
                    lambda v: v and [EntityId.from_json(v) for v in v]
                )(
                    data.get("entityRestrictions", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EventFeatureTemplateCreationRequest",
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
            "name": self.name.to_json(),
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "table": self.table.to_json(),
            "window": self.window.to_json(),
            "select": self.select.to_json(),
            "filter": (lambda v: v and v.to_json())(self.filter),
            "aggregate": (lambda v: v and v.to_json())(self.aggregate),
            "postAggregateExpr": (lambda v: v and v.to_json())(self.postAggregateExpr),
            "entityRestrictions": (lambda v: v and [v.to_json() for v in v])(self.entityRestrictions)
        }


@dataclasses.dataclass(frozen=True)
class RowFeatureTemplateCreationRequest(FeatureTemplateCreationRequest):
    """Create a new row feature template.
    
    Args:
        name (TemplateName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        over (typing.List[FeatureId]): A data field.
        select (SelectExpression): A data field.
        entityId (EntityId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "row"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: TemplateName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    over: typing.List[FeatureId]
    select: SelectExpression
    entityId: EntityId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for RowFeatureTemplateCreationRequest data.
        
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
                "name": TemplateName.json_schema(),
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
                "over": {
                    "type": "array",
                    "item": FeatureId.json_schema()
                },
                "select": SelectExpression.json_schema(),
                "entityId": EntityId.json_schema()
            },
            "required": [
                "adt_type",
                "name",
                "description",
                "labels",
                "attributes",
                "over",
                "select",
                "entityId",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> RowFeatureTemplateCreationRequest:
        """Validate and parse JSON data into an instance of RowFeatureTemplateCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of RowFeatureTemplateCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return RowFeatureTemplateCreationRequest(
                name=TemplateName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                over=[FeatureId.from_json(v) for v in data["over"]],
                select=SelectExpression.from_json(data["select"]),
                entityId=EntityId.from_json(data["entityId"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing RowFeatureTemplateCreationRequest",
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
            "name": self.name.to_json(),
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "over": [v.to_json() for v in self.over],
            "select": self.select.to_json(),
            "entityId": self.entityId.to_json()
        }

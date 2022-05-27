"""Generated implementation of feature_template."""

# WARNING DO NOT EDIT
# This code was generated from feature-template.mcn

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
from ..filter_expression import FilterExpression
from ..label import Label
from ..post_aggregate_expression import PostAggregateExpression
from ..select_expression import SelectExpression
from ..table import TableId


@dataclasses.dataclass(frozen=True)
class TemplateId:
    """Unique identifier for a feature template.
    
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
        """Return the JSON schema for TemplateId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TemplateId:
        """Validate and parse JSON data into an instance of TemplateId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TemplateId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TemplateId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing TemplateId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> TemplateId:
        """Parse a JSON string such as a dictionary key."""
        return TemplateId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class TemplateName:
    """Unique name for a feature template.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TemplateName data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TemplateName:
        """Validate and parse JSON data into an instance of TemplateName.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TemplateName.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TemplateName(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing TemplateName", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> TemplateName:
        """Parse a JSON string such as a dictionary key."""
        return TemplateName(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class TemplateVersionId:
    """Unique identifier for a specific version of a feature template.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TemplateVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TemplateVersionId:
        """Validate and parse JSON data into an instance of TemplateVersionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TemplateVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TemplateVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing TemplateVersionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> TemplateVersionId:
        """Parse a JSON string such as a dictionary key."""
        return TemplateVersionId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class FeatureTemplate(abc.ABC):
    """Details of a feature template.
    
    Args:
        attributes (typing.List[Attribute]): A data field.
        description (str): A data field.
        id (TemplateId): A data field.
        labels (typing.List[Label]): A data field.
        name (TemplateName): A data field.
        select (SelectExpression): A data field.
        version (TemplateVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    attributes: typing.List[Attribute]
    description: str
    id: TemplateId
    labels: typing.List[Label]
    name: TemplateName
    select: SelectExpression
    version: TemplateVersionId
    
    @classmethod
    def json_schema(cls) -> FeatureTemplate:
        """JSON schema for variant FeatureTemplate.
        
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
    def from_json(cls, data: dict) -> FeatureTemplate:
        """Validate and parse JSON data into an instance of FeatureTemplate.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureTemplate.
        
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
            logging.debug("Invalid JSON data received while parsing FeatureTemplate", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class EventFeatureTemplate(FeatureTemplate):
    """A template definition of features on events.
    
    Args:
        id (TemplateId): A data field.
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
        version (TemplateVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "event"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: TemplateId
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
    version: TemplateVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EventFeatureTemplate data.
        
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
                "id": TemplateId.json_schema(),
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
                },
                "version": TemplateVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "table",
                "window",
                "select",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EventFeatureTemplate:
        """Validate and parse JSON data into an instance of EventFeatureTemplate.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EventFeatureTemplate.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EventFeatureTemplate(
                id=TemplateId.from_json(data["id"]),
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
                version=TemplateVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EventFeatureTemplate",
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
            "id": self.id.to_json(),
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
            "entityRestrictions": (lambda v: v and [v.to_json() for v in v])(self.entityRestrictions),
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class RowFeatureTemplate(FeatureTemplate):
    """A template definition of features on rows.
    
    Args:
        id (TemplateId): A data field.
        name (TemplateName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        over (typing.List[FeatureId]): A data field.
        select (SelectExpression): A data field.
        entityId (EntityId): A data field.
        version (TemplateVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "row"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: TemplateId
    name: TemplateName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    over: typing.List[FeatureId]
    select: SelectExpression
    entityId: EntityId
    version: TemplateVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for RowFeatureTemplate data.
        
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
                "id": TemplateId.json_schema(),
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
                "entityId": EntityId.json_schema(),
                "version": TemplateVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "over",
                "select",
                "entityId",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> RowFeatureTemplate:
        """Validate and parse JSON data into an instance of RowFeatureTemplate.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of RowFeatureTemplate.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return RowFeatureTemplate(
                id=TemplateId.from_json(data["id"]),
                name=TemplateName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                over=[FeatureId.from_json(v) for v in data["over"]],
                select=SelectExpression.from_json(data["select"]),
                entityId=EntityId.from_json(data["entityId"]),
                version=TemplateVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing RowFeatureTemplate",
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
            "id": self.id.to_json(),
            "name": self.name.to_json(),
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "over": [v.to_json() for v in self.over],
            "select": self.select.to_json(),
            "entityId": self.entityId.to_json(),
            "version": self.version.to_json()
        }

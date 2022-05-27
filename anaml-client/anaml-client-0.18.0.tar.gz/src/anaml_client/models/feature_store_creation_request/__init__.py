"""Generated implementation of feature_store_creation_request."""

# WARNING DO NOT EDIT
# This code was generated from feature-store-creation-request.mcn

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
from ..cluster import ClusterId
from ..destination_reference import DestinationReference
from ..feature_set import FeatureSetId
from ..feature_store import FeatureStoreName, VersionTarget
from ..label import Label
from ..schedule import Schedule
from ..table import TableId
from ..user import UserId


@dataclasses.dataclass(frozen=True)
class FeatureStoreCreationRequest(abc.ABC):
    """Request to create a new feature store.
    
    Args:
        attributes (typing.List[Attribute]): A data field.
        cluster (ClusterId): A data field.
        description (str): A data field.
        destinations (typing.List[DestinationReference]): A data field.
        enabled (bool): A data field.
        featureSet (FeatureSetId): A data field.
        labels (typing.List[Label]): A data field.
        name (FeatureStoreName): A data field.
        principal (UserId): A data field.
        schedule (Schedule): A data field.
        versionTarget (typing.Optional[VersionTarget]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    attributes: typing.List[Attribute]
    cluster: ClusterId
    description: str
    destinations: typing.List[DestinationReference]
    enabled: bool
    featureSet: FeatureSetId
    labels: typing.List[Label]
    name: FeatureStoreName
    principal: UserId
    schedule: Schedule
    versionTarget: typing.Optional[VersionTarget]
    
    @classmethod
    def json_schema(cls) -> FeatureStoreCreationRequest:
        """JSON schema for variant FeatureStoreCreationRequest.
        
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
    def from_json(cls, data: dict) -> FeatureStoreCreationRequest:
        """Validate and parse JSON data into an instance of FeatureStoreCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureStoreCreationRequest.
        
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
            logging.debug("Invalid JSON data received while parsing FeatureStoreCreationRequest", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class BatchFeatureStoreCreationRequest(FeatureStoreCreationRequest):
    """A batch feature store.
    
    Args:
        name (FeatureStoreName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        featureSet (FeatureSetId): A data field.
        enabled (bool): A data field.
        destinations (typing.List[DestinationReference]): A data field.
        cluster (ClusterId): A data field.
        schedule (Schedule): A data field.
        principal (UserId): A data field.
        startDate (typing.Optional[datetime.date]): A data field.
        endDate (typing.Optional[datetime.date]): A data field.
        includeMetadata (bool): A data field.
        versionTarget (typing.Optional[VersionTarget]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "batch"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: FeatureStoreName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    featureSet: FeatureSetId
    enabled: bool
    destinations: typing.List[DestinationReference]
    cluster: ClusterId
    schedule: Schedule
    principal: UserId
    startDate: typing.Optional[datetime.date]
    endDate: typing.Optional[datetime.date]
    includeMetadata: bool
    versionTarget: typing.Optional[VersionTarget]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for BatchFeatureStoreCreationRequest data.
        
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
                "name": FeatureStoreName.json_schema(),
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
                "featureSet": FeatureSetId.json_schema(),
                "enabled": {
                    "type": "boolean"
                },
                "destinations": {
                    "type": "array",
                    "item": DestinationReference.json_schema()
                },
                "cluster": ClusterId.json_schema(),
                "schedule": Schedule.json_schema(),
                "principal": UserId.json_schema(),
                "startDate": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string", "format": "date"},
                    ]
                },
                "endDate": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string", "format": "date"},
                    ]
                },
                "includeMetadata": {
                    "type": "boolean"
                },
                "versionTarget": {
                    "oneOf": [
                        {"type": "null"},
                        VersionTarget.json_schema(),
                    ]
                }
            },
            "required": [
                "adt_type",
                "name",
                "description",
                "labels",
                "attributes",
                "featureSet",
                "enabled",
                "destinations",
                "cluster",
                "schedule",
                "principal",
                "includeMetadata",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> BatchFeatureStoreCreationRequest:
        """Validate and parse JSON data into an instance of BatchFeatureStoreCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of BatchFeatureStoreCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return BatchFeatureStoreCreationRequest(
                name=FeatureStoreName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                featureSet=FeatureSetId.from_json(data["featureSet"]),
                enabled=bool(data["enabled"]),
                destinations=[DestinationReference.from_json(v) for v in data["destinations"]],
                cluster=ClusterId.from_json(data["cluster"]),
                schedule=Schedule.from_json(data["schedule"]),
                principal=UserId.from_json(data["principal"]),
                startDate=(
                    lambda v: v and datetime.date.fromisoformat(v)
                )(
                    data.get("startDate", None)
                ),
                endDate=(
                    lambda v: v and datetime.date.fromisoformat(v)
                )(
                    data.get("endDate", None)
                ),
                includeMetadata=bool(data["includeMetadata"]),
                versionTarget=(
                    lambda v: v and VersionTarget.from_json(v)
                )(
                    data.get("versionTarget", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing BatchFeatureStoreCreationRequest",
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
            "featureSet": self.featureSet.to_json(),
            "enabled": self.enabled,
            "destinations": [v.to_json() for v in self.destinations],
            "cluster": self.cluster.to_json(),
            "schedule": self.schedule.to_json(),
            "principal": self.principal.to_json(),
            "startDate": (lambda v: v and v.isoformat())(self.startDate),
            "endDate": (lambda v: v and v.isoformat())(self.endDate),
            "includeMetadata": self.includeMetadata,
            "versionTarget": (lambda v: v and v.to_json())(self.versionTarget)
        }


@dataclasses.dataclass(frozen=True)
class StreamingFeatureStoreCreationRequest(FeatureStoreCreationRequest):
    """A streaming feature store.
    
    Args:
        name (FeatureStoreName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        featureSet (FeatureSetId): A data field.
        enabled (bool): A data field.
        destinations (typing.List[DestinationReference]): A data field.
        cluster (ClusterId): A data field.
        schedule (Schedule): A data field.
        principal (UserId): A data field.
        table (TableId): A data field.
        versionTarget (typing.Optional[VersionTarget]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "streaming"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: FeatureStoreName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    featureSet: FeatureSetId
    enabled: bool
    destinations: typing.List[DestinationReference]
    cluster: ClusterId
    schedule: Schedule
    principal: UserId
    table: TableId
    versionTarget: typing.Optional[VersionTarget]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for StreamingFeatureStoreCreationRequest data.
        
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
                "name": FeatureStoreName.json_schema(),
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
                "featureSet": FeatureSetId.json_schema(),
                "enabled": {
                    "type": "boolean"
                },
                "destinations": {
                    "type": "array",
                    "item": DestinationReference.json_schema()
                },
                "cluster": ClusterId.json_schema(),
                "schedule": Schedule.json_schema(),
                "principal": UserId.json_schema(),
                "table": TableId.json_schema(),
                "versionTarget": {
                    "oneOf": [
                        {"type": "null"},
                        VersionTarget.json_schema(),
                    ]
                }
            },
            "required": [
                "adt_type",
                "name",
                "description",
                "labels",
                "attributes",
                "featureSet",
                "enabled",
                "destinations",
                "cluster",
                "schedule",
                "principal",
                "table",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> StreamingFeatureStoreCreationRequest:
        """Validate and parse JSON data into an instance of StreamingFeatureStoreCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of StreamingFeatureStoreCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return StreamingFeatureStoreCreationRequest(
                name=FeatureStoreName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                featureSet=FeatureSetId.from_json(data["featureSet"]),
                enabled=bool(data["enabled"]),
                destinations=[DestinationReference.from_json(v) for v in data["destinations"]],
                cluster=ClusterId.from_json(data["cluster"]),
                schedule=Schedule.from_json(data["schedule"]),
                principal=UserId.from_json(data["principal"]),
                table=TableId.from_json(data["table"]),
                versionTarget=(
                    lambda v: v and VersionTarget.from_json(v)
                )(
                    data.get("versionTarget", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing StreamingFeatureStoreCreationRequest",
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
            "featureSet": self.featureSet.to_json(),
            "enabled": self.enabled,
            "destinations": [v.to_json() for v in self.destinations],
            "cluster": self.cluster.to_json(),
            "schedule": self.schedule.to_json(),
            "principal": self.principal.to_json(),
            "table": self.table.to_json(),
            "versionTarget": (lambda v: v and v.to_json())(self.versionTarget)
        }

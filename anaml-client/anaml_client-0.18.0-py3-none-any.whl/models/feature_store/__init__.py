"""Generated implementation of feature_store."""

# WARNING DO NOT EDIT
# This code was generated from feature-store.mcn

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
from ..commit import CommitId
from ..destination_reference import DestinationReference
from ..feature_set import FeatureSetId
from ..label import Label
from ..schedule import Schedule
from ..table import TableId
from ..user import UserId


@dataclasses.dataclass(frozen=True)
class FeatureStoreId:
    """Unique identifier for a feature store.
    
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
        """Return the JSON schema for FeatureStoreId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FeatureStoreId:
        """Validate and parse JSON data into an instance of FeatureStoreId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureStoreId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureStoreId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing FeatureStoreId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> FeatureStoreId:
        """Parse a JSON string such as a dictionary key."""
        return FeatureStoreId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class FeatureStoreName:
    """Unique name for a feature store.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for FeatureStoreName data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FeatureStoreName:
        """Validate and parse JSON data into an instance of FeatureStoreName.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureStoreName.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureStoreName(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing FeatureStoreName", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> FeatureStoreName:
        """Parse a JSON string such as a dictionary key."""
        return FeatureStoreName(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class FeatureStoreVersionId:
    """Unique identifier of a specific version of a feature store.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for FeatureStoreVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FeatureStoreVersionId:
        """Validate and parse JSON data into an instance of FeatureStoreVersionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureStoreVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FeatureStoreVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing FeatureStoreVersionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> FeatureStoreVersionId:
        """Parse a JSON string such as a dictionary key."""
        return FeatureStoreVersionId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class FeatureStore(abc.ABC):
    """Definition of a feature store.
    
    Args:
        attributes (typing.List[Attribute]): A data field.
        cluster (ClusterId): A data field.
        description (str): A data field.
        destinations (typing.List[DestinationReference]): A data field.
        enabled (bool): A data field.
        featureSet (FeatureSetId): A data field.
        id (FeatureStoreId): A data field.
        labels (typing.List[Label]): A data field.
        name (FeatureStoreName): A data field.
        principal (typing.Optional[UserId]): A data field.
        schedule (Schedule): A data field.
        version (FeatureStoreVersionId): A data field.
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
    id: FeatureStoreId
    labels: typing.List[Label]
    name: FeatureStoreName
    principal: typing.Optional[UserId]
    schedule: Schedule
    version: FeatureStoreVersionId
    versionTarget: typing.Optional[VersionTarget]
    
    @classmethod
    def json_schema(cls) -> FeatureStore:
        """JSON schema for variant FeatureStore.
        
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
    def from_json(cls, data: dict) -> FeatureStore:
        """Validate and parse JSON data into an instance of FeatureStore.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FeatureStore.
        
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
            logging.debug("Invalid JSON data received while parsing FeatureStore", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class BatchFeatureStore(FeatureStore):
    """A batch feature store.
    
    Args:
        id (FeatureStoreId): A data field.
        name (FeatureStoreName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        featureSet (FeatureSetId): A data field.
        enabled (bool): A data field.
        destinations (typing.List[DestinationReference]): A data field.
        cluster (ClusterId): A data field.
        schedule (Schedule): A data field.
        principal (typing.Optional[UserId]): A data field.
        startDate (typing.Optional[datetime.date]): A data field.
        endDate (typing.Optional[datetime.date]): A data field.
        runDateOffset (typing.Optional[int]): A data field.
        includeMetadata (bool): A data field.
        versionTarget (typing.Optional[VersionTarget]): A data field.
        version (FeatureStoreVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "batch"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: FeatureStoreId
    name: FeatureStoreName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    featureSet: FeatureSetId
    enabled: bool
    destinations: typing.List[DestinationReference]
    cluster: ClusterId
    schedule: Schedule
    principal: typing.Optional[UserId]
    startDate: typing.Optional[datetime.date]
    endDate: typing.Optional[datetime.date]
    runDateOffset: typing.Optional[int]
    includeMetadata: bool
    versionTarget: typing.Optional[VersionTarget]
    version: FeatureStoreVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for BatchFeatureStore data.
        
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
                "id": FeatureStoreId.json_schema(),
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
                "principal": {
                    "oneOf": [
                        {"type": "null"},
                        UserId.json_schema(),
                    ]
                },
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
                "runDateOffset": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "integer"},
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
                },
                "version": FeatureStoreVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "featureSet",
                "enabled",
                "destinations",
                "cluster",
                "schedule",
                "includeMetadata",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> BatchFeatureStore:
        """Validate and parse JSON data into an instance of BatchFeatureStore.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of BatchFeatureStore.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return BatchFeatureStore(
                id=FeatureStoreId.from_json(data["id"]),
                name=FeatureStoreName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                featureSet=FeatureSetId.from_json(data["featureSet"]),
                enabled=bool(data["enabled"]),
                destinations=[DestinationReference.from_json(v) for v in data["destinations"]],
                cluster=ClusterId.from_json(data["cluster"]),
                schedule=Schedule.from_json(data["schedule"]),
                principal=(lambda v: v and UserId.from_json(v))(data.get("principal", None)),
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
                runDateOffset=(lambda v: v and int(v))(data.get("runDateOffset", None)),
                includeMetadata=bool(data["includeMetadata"]),
                versionTarget=(
                    lambda v: v and VersionTarget.from_json(v)
                )(
                    data.get("versionTarget", None)
                ),
                version=FeatureStoreVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing BatchFeatureStore",
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
            "featureSet": self.featureSet.to_json(),
            "enabled": self.enabled,
            "destinations": [v.to_json() for v in self.destinations],
            "cluster": self.cluster.to_json(),
            "schedule": self.schedule.to_json(),
            "principal": (lambda v: v and v.to_json())(self.principal),
            "startDate": (lambda v: v and v.isoformat())(self.startDate),
            "endDate": (lambda v: v and v.isoformat())(self.endDate),
            "runDateOffset": (lambda v: v and int(v))(self.runDateOffset),
            "includeMetadata": self.includeMetadata,
            "versionTarget": (lambda v: v and v.to_json())(self.versionTarget),
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class StreamingFeatureStore(FeatureStore):
    """A streaming feature store.
    
    Args:
        id (FeatureStoreId): A data field.
        name (FeatureStoreName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        featureSet (FeatureSetId): A data field.
        enabled (bool): A data field.
        destinations (typing.List[DestinationReference]): A data field.
        cluster (ClusterId): A data field.
        schedule (Schedule): A data field.
        principal (typing.Optional[UserId]): A data field.
        table (TableId): A data field.
        versionTarget (typing.Optional[VersionTarget]): A data field.
        version (FeatureStoreVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "streaming"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: FeatureStoreId
    name: FeatureStoreName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    featureSet: FeatureSetId
    enabled: bool
    destinations: typing.List[DestinationReference]
    cluster: ClusterId
    schedule: Schedule
    principal: typing.Optional[UserId]
    table: TableId
    versionTarget: typing.Optional[VersionTarget]
    version: FeatureStoreVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for StreamingFeatureStore data.
        
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
                "id": FeatureStoreId.json_schema(),
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
                "principal": {
                    "oneOf": [
                        {"type": "null"},
                        UserId.json_schema(),
                    ]
                },
                "table": TableId.json_schema(),
                "versionTarget": {
                    "oneOf": [
                        {"type": "null"},
                        VersionTarget.json_schema(),
                    ]
                },
                "version": FeatureStoreVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "featureSet",
                "enabled",
                "destinations",
                "cluster",
                "schedule",
                "table",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> StreamingFeatureStore:
        """Validate and parse JSON data into an instance of StreamingFeatureStore.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of StreamingFeatureStore.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return StreamingFeatureStore(
                id=FeatureStoreId.from_json(data["id"]),
                name=FeatureStoreName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                featureSet=FeatureSetId.from_json(data["featureSet"]),
                enabled=bool(data["enabled"]),
                destinations=[DestinationReference.from_json(v) for v in data["destinations"]],
                cluster=ClusterId.from_json(data["cluster"]),
                schedule=Schedule.from_json(data["schedule"]),
                principal=(lambda v: v and UserId.from_json(v))(data.get("principal", None)),
                table=TableId.from_json(data["table"]),
                versionTarget=(
                    lambda v: v and VersionTarget.from_json(v)
                )(
                    data.get("versionTarget", None)
                ),
                version=FeatureStoreVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing StreamingFeatureStore",
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
            "featureSet": self.featureSet.to_json(),
            "enabled": self.enabled,
            "destinations": [v.to_json() for v in self.destinations],
            "cluster": self.cluster.to_json(),
            "schedule": self.schedule.to_json(),
            "principal": (lambda v: v and v.to_json())(self.principal),
            "table": self.table.to_json(),
            "versionTarget": (lambda v: v and v.to_json())(self.versionTarget),
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class VersionTarget(abc.ABC):
    """Code version to execute when running a feature store."""
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    @classmethod
    def json_schema(cls) -> VersionTarget:
        """JSON schema for variant VersionTarget.
        
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
    def from_json(cls, data: dict) -> VersionTarget:
        """Validate and parse JSON data into an instance of VersionTarget.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of VersionTarget.
        
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
            logging.debug("Invalid JSON data received while parsing VersionTarget", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class CommitVersionTarget(VersionTarget):
    """Execute code from a specific commit.
    
    Args:
        commitId (CommitId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "commit"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    commitId: CommitId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for CommitVersionTarget data.
        
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
                "commitId": CommitId.json_schema()
            },
            "required": [
                "adt_type",
                "commitId",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> CommitVersionTarget:
        """Validate and parse JSON data into an instance of CommitVersionTarget.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of CommitVersionTarget.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return CommitVersionTarget(
                commitId=CommitId.from_json(data["commitId"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing CommitVersionTarget",
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
            "commitId": self.commitId.to_json()
        }


@dataclasses.dataclass(frozen=True)
class BranchVersionTarget(VersionTarget):
    """Execute latest code from a branch.
    
    Args:
        branchName (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "branch"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    branchName: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for BranchVersionTarget data.
        
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
                "branchName": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "branchName",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> BranchVersionTarget:
        """Validate and parse JSON data into an instance of BranchVersionTarget.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of BranchVersionTarget.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return BranchVersionTarget(
                branchName=str(data["branchName"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing BranchVersionTarget",
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
            "branchName": str(self.branchName)
        }

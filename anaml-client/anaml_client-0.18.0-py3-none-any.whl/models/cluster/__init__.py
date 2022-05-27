"""Generated implementation of cluster."""

# WARNING DO NOT EDIT
# This code was generated from cluster.mcn

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
from ..credentials_provider_config import CredentialsProviderConfig
from ..label import Label


@dataclasses.dataclass(frozen=True)
class ClusterId:
    """Unique identifier for a cluster.
    
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
        """Return the JSON schema for ClusterId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ClusterId:
        """Validate and parse JSON data into an instance of ClusterId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ClusterId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ClusterId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing ClusterId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> ClusterId:
        """Parse a JSON string such as a dictionary key."""
        return ClusterId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class ClusterVersionId:
    """Unique identifier for a version of a cluster.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ClusterVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ClusterVersionId:
        """Validate and parse JSON data into an instance of ClusterVersionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ClusterVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ClusterVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing ClusterVersionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> ClusterVersionId:
        """Parse a JSON string such as a dictionary key."""
        return ClusterVersionId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class ClusterName:
    """Unique name for a cluster.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for ClusterName data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> ClusterName:
        """Validate and parse JSON data into an instance of ClusterName.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ClusterName.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return ClusterName(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing ClusterName", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> ClusterName:
        """Parse a JSON string such as a dictionary key."""
        return ClusterName(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class SparkConfig:
    """Spark configuration.
    
    Args:
        enableHiveSupport (bool): A data field.
        hiveMetastoreUrl (typing.Optional[str]): A data field.
        additionalSparkProperties (typing.Dict[str, str]): A data field.
    """
    
    enableHiveSupport: bool
    hiveMetastoreUrl: typing.Optional[str]
    additionalSparkProperties: typing.Dict[str, str]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for SparkConfig data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "enableHiveSupport": {
                    "type": "boolean"
                },
                "hiveMetastoreUrl": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "additionalSparkProperties": {
                    "type": "object",
                    "additionalProperties": {
                        "type": "string"
                    }
                }
            },
            "required": [
                "enableHiveSupport",
                "additionalSparkProperties",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> SparkConfig:
        """Validate and parse JSON data into an instance of SparkConfig.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of SparkConfig.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return SparkConfig(
                enableHiveSupport=bool(data["enableHiveSupport"]),
                hiveMetastoreUrl=(lambda v: v and str(v))(data.get("hiveMetastoreUrl", None)),
                additionalSparkProperties={
                    str(k): str(v) for k, v in data["additionalSparkProperties"].items()
                },
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing SparkConfig",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "enableHiveSupport": self.enableHiveSupport,
            "hiveMetastoreUrl": (lambda v: v and str(v))(self.hiveMetastoreUrl),
            "additionalSparkProperties": {str(k): str(v) for k, v in self.additionalSparkProperties.items()}
        }


@dataclasses.dataclass(frozen=True)
class Cluster(abc.ABC):
    """Details for a job execution cluster.
    
    Args:
        attributes (typing.List[Attribute]): A data field.
        description (str): A data field.
        id (ClusterId): A data field.
        isPreviewCluster (bool): A data field.
        labels (typing.List[Label]): A data field.
        name (ClusterName): A data field.
        sparkConfig (SparkConfig): A data field.
        version (ClusterVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    attributes: typing.List[Attribute]
    description: str
    id: ClusterId
    isPreviewCluster: bool
    labels: typing.List[Label]
    name: ClusterName
    sparkConfig: SparkConfig
    version: ClusterVersionId
    
    @classmethod
    def json_schema(cls) -> Cluster:
        """JSON schema for variant Cluster.
        
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
    def from_json(cls, data: dict) -> Cluster:
        """Validate and parse JSON data into an instance of Cluster.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Cluster.
        
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
            logging.debug("Invalid JSON data received while parsing Cluster", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class LocalCluster(Cluster):
    """Local job execution cluster.
    
    Args:
        id (ClusterId): A data field.
        name (ClusterName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        isPreviewCluster (bool): A data field.
        anamlServerUrl (str): A data field.
        credentialsProvider (CredentialsProviderConfig): A data field.
        sparkConfig (SparkConfig): A data field.
        version (ClusterVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "local"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: ClusterId
    name: ClusterName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    isPreviewCluster: bool
    anamlServerUrl: str
    credentialsProvider: CredentialsProviderConfig
    sparkConfig: SparkConfig
    version: ClusterVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for LocalCluster data.
        
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
                "id": ClusterId.json_schema(),
                "name": ClusterName.json_schema(),
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
                "isPreviewCluster": {
                    "type": "boolean"
                },
                "anamlServerUrl": {
                    "type": "string"
                },
                "credentialsProvider": CredentialsProviderConfig.json_schema(),
                "sparkConfig": SparkConfig.json_schema(),
                "version": ClusterVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "isPreviewCluster",
                "anamlServerUrl",
                "credentialsProvider",
                "sparkConfig",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> LocalCluster:
        """Validate and parse JSON data into an instance of LocalCluster.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of LocalCluster.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return LocalCluster(
                id=ClusterId.from_json(data["id"]),
                name=ClusterName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                isPreviewCluster=bool(data["isPreviewCluster"]),
                anamlServerUrl=str(data["anamlServerUrl"]),
                credentialsProvider=CredentialsProviderConfig.from_json(data["credentialsProvider"]),
                sparkConfig=SparkConfig.from_json(data["sparkConfig"]),
                version=ClusterVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing LocalCluster",
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
            "isPreviewCluster": self.isPreviewCluster,
            "anamlServerUrl": str(self.anamlServerUrl),
            "credentialsProvider": self.credentialsProvider.to_json(),
            "sparkConfig": self.sparkConfig.to_json(),
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class SparkServerCluster(Cluster):
    """Job execution cluster managed by a Spark Server.
    
    Args:
        id (ClusterId): A data field.
        name (ClusterName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        isPreviewCluster (bool): A data field.
        sparkServerUrl (str): A data field.
        sparkConfig (SparkConfig): A data field.
        version (ClusterVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "sparkserver"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: ClusterId
    name: ClusterName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    isPreviewCluster: bool
    sparkServerUrl: str
    sparkConfig: SparkConfig
    version: ClusterVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for SparkServerCluster data.
        
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
                "id": ClusterId.json_schema(),
                "name": ClusterName.json_schema(),
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
                "isPreviewCluster": {
                    "type": "boolean"
                },
                "sparkServerUrl": {
                    "type": "string"
                },
                "sparkConfig": SparkConfig.json_schema(),
                "version": ClusterVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "isPreviewCluster",
                "sparkServerUrl",
                "sparkConfig",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> SparkServerCluster:
        """Validate and parse JSON data into an instance of SparkServerCluster.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of SparkServerCluster.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return SparkServerCluster(
                id=ClusterId.from_json(data["id"]),
                name=ClusterName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                isPreviewCluster=bool(data["isPreviewCluster"]),
                sparkServerUrl=str(data["sparkServerUrl"]),
                sparkConfig=SparkConfig.from_json(data["sparkConfig"]),
                version=ClusterVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing SparkServerCluster",
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
            "isPreviewCluster": self.isPreviewCluster,
            "sparkServerUrl": str(self.sparkServerUrl),
            "sparkConfig": self.sparkConfig.to_json(),
            "version": self.version.to_json()
        }

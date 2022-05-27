"""Generated implementation of cluster_creation_request."""

# WARNING DO NOT EDIT
# This code was generated from cluster-creation-request.mcn

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
from ..cluster import ClusterName, SparkConfig
from ..credentials_provider_config import CredentialsProviderConfig
from ..label import Label


@dataclasses.dataclass(frozen=True)
class ClusterCreationRequest(abc.ABC):
    """Request to create a new cluster configuration.
    
    Args:
        attributes (typing.List[Attribute]): A data field.
        description (str): A data field.
        isPreviewCluster (bool): A data field.
        labels (typing.List[Label]): A data field.
        name (ClusterName): A data field.
        sparkConfig (SparkConfig): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    attributes: typing.List[Attribute]
    description: str
    isPreviewCluster: bool
    labels: typing.List[Label]
    name: ClusterName
    sparkConfig: SparkConfig
    
    @classmethod
    def json_schema(cls) -> ClusterCreationRequest:
        """JSON schema for variant ClusterCreationRequest.
        
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
    def from_json(cls, data: dict) -> ClusterCreationRequest:
        """Validate and parse JSON data into an instance of ClusterCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of ClusterCreationRequest.
        
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
            logging.debug("Invalid JSON data received while parsing ClusterCreationRequest", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class LocalClusterCreationRequest(ClusterCreationRequest):
    """Request to create a new local cluster configuration.
    
    Args:
        name (ClusterName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        isPreviewCluster (bool): A data field.
        anamlServerUrl (str): A data field.
        credentialsProvider (CredentialsProviderConfig): A data field.
        sparkConfig (SparkConfig): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "local"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: ClusterName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    isPreviewCluster: bool
    anamlServerUrl: str
    credentialsProvider: CredentialsProviderConfig
    sparkConfig: SparkConfig
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for LocalClusterCreationRequest data.
        
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
                "sparkConfig": SparkConfig.json_schema()
            },
            "required": [
                "adt_type",
                "name",
                "description",
                "labels",
                "attributes",
                "isPreviewCluster",
                "anamlServerUrl",
                "credentialsProvider",
                "sparkConfig",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> LocalClusterCreationRequest:
        """Validate and parse JSON data into an instance of LocalClusterCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of LocalClusterCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return LocalClusterCreationRequest(
                name=ClusterName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                isPreviewCluster=bool(data["isPreviewCluster"]),
                anamlServerUrl=str(data["anamlServerUrl"]),
                credentialsProvider=CredentialsProviderConfig.from_json(data["credentialsProvider"]),
                sparkConfig=SparkConfig.from_json(data["sparkConfig"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing LocalClusterCreationRequest",
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
            "isPreviewCluster": self.isPreviewCluster,
            "anamlServerUrl": str(self.anamlServerUrl),
            "credentialsProvider": self.credentialsProvider.to_json(),
            "sparkConfig": self.sparkConfig.to_json()
        }


@dataclasses.dataclass(frozen=True)
class SparkServerClusterCreationRequest(ClusterCreationRequest):
    """Request to create a new Spark Server cluster configuration.
    
    Args:
        name (ClusterName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        isPreviewCluster (bool): A data field.
        sparkServerUrl (str): A data field.
        sparkConfig (SparkConfig): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "sparkserver"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: ClusterName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    isPreviewCluster: bool
    sparkServerUrl: str
    sparkConfig: SparkConfig
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for SparkServerClusterCreationRequest data.
        
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
                "sparkConfig": SparkConfig.json_schema()
            },
            "required": [
                "adt_type",
                "name",
                "description",
                "labels",
                "attributes",
                "isPreviewCluster",
                "sparkServerUrl",
                "sparkConfig",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> SparkServerClusterCreationRequest:
        """Validate and parse JSON data into an instance of SparkServerClusterCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of SparkServerClusterCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return SparkServerClusterCreationRequest(
                name=ClusterName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                isPreviewCluster=bool(data["isPreviewCluster"]),
                sparkServerUrl=str(data["sparkServerUrl"]),
                sparkConfig=SparkConfig.from_json(data["sparkConfig"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing SparkServerClusterCreationRequest",
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
            "isPreviewCluster": self.isPreviewCluster,
            "sparkServerUrl": str(self.sparkServerUrl),
            "sparkConfig": self.sparkConfig.to_json()
        }

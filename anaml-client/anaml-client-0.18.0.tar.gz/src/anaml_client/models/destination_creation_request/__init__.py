"""Generated implementation of destination_creation_request."""

# WARNING DO NOT EDIT
# This code was generated from destination-creation-request.mcn

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

from ..attribute import Attribute, SensitiveAttribute
from ..credentials_provider_config import CredentialsProviderConfig
from ..destination import DestinationName, GCSStagingArea
from ..file_format import FileFormat
from ..label import Label


@dataclasses.dataclass(frozen=True)
class DestinationCreationRequest(abc.ABC):
    """Requests to create a new output data store.
    
    Args:
        attributes (typing.List[Attribute]): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        name (DestinationName): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    attributes: typing.List[Attribute]
    description: str
    labels: typing.List[Label]
    name: DestinationName
    
    @classmethod
    def json_schema(cls) -> DestinationCreationRequest:
        """JSON schema for variant DestinationCreationRequest.
        
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
    def from_json(cls, data: dict) -> DestinationCreationRequest:
        """Validate and parse JSON data into an instance of DestinationCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of DestinationCreationRequest.
        
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
            logging.debug("Invalid JSON data received while parsing DestinationCreationRequest", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class S3DestinationCreationRequest(DestinationCreationRequest):
    """Create a new output data store on AWS S3.
    
    Args:
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        bucket (str): A data field.
        path (str): A data field.
        fileFormat (FileFormat): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "s3"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    bucket: str
    path: str
    fileFormat: FileFormat
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for S3DestinationCreationRequest data.
        
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
                "name": DestinationName.json_schema(),
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
                "bucket": {
                    "type": "string"
                },
                "path": {
                    "type": "string"
                },
                "fileFormat": FileFormat.json_schema()
            },
            "required": [
                "adt_type",
                "name",
                "description",
                "labels",
                "attributes",
                "bucket",
                "path",
                "fileFormat",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> S3DestinationCreationRequest:
        """Validate and parse JSON data into an instance of S3DestinationCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of S3DestinationCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return S3DestinationCreationRequest(
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                bucket=str(data["bucket"]),
                path=str(data["path"]),
                fileFormat=FileFormat.from_json(data["fileFormat"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing S3DestinationCreationRequest",
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
            "bucket": str(self.bucket),
            "path": str(self.path),
            "fileFormat": self.fileFormat.to_json()
        }


@dataclasses.dataclass(frozen=True)
class S3ADestinationCreationRequest(DestinationCreationRequest):
    """Create a new output data store using S3-compatible object storage.
    
    Args:
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        bucket (str): A data field.
        path (str): A data field.
        fileFormat (FileFormat): A data field.
        endpoint (str): A data field.
        accessKey (str): A data field.
        secretKey (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "s3a"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    bucket: str
    path: str
    fileFormat: FileFormat
    endpoint: str
    accessKey: str
    secretKey: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for S3ADestinationCreationRequest data.
        
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
                "name": DestinationName.json_schema(),
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
                "bucket": {
                    "type": "string"
                },
                "path": {
                    "type": "string"
                },
                "fileFormat": FileFormat.json_schema(),
                "endpoint": {
                    "type": "string"
                },
                "accessKey": {
                    "type": "string"
                },
                "secretKey": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "name",
                "description",
                "labels",
                "attributes",
                "bucket",
                "path",
                "fileFormat",
                "endpoint",
                "accessKey",
                "secretKey",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> S3ADestinationCreationRequest:
        """Validate and parse JSON data into an instance of S3ADestinationCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of S3ADestinationCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return S3ADestinationCreationRequest(
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                bucket=str(data["bucket"]),
                path=str(data["path"]),
                fileFormat=FileFormat.from_json(data["fileFormat"]),
                endpoint=str(data["endpoint"]),
                accessKey=str(data["accessKey"]),
                secretKey=str(data["secretKey"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing S3ADestinationCreationRequest",
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
            "bucket": str(self.bucket),
            "path": str(self.path),
            "fileFormat": self.fileFormat.to_json(),
            "endpoint": str(self.endpoint),
            "accessKey": str(self.accessKey),
            "secretKey": str(self.secretKey)
        }


@dataclasses.dataclass(frozen=True)
class JDBCDestinationCreationRequest(DestinationCreationRequest):
    """Create a new output data store using JDBC.
    
    Args:
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        url (str): A data field.
        schema (str): A data field.
        credentialsProvider (CredentialsProviderConfig): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "jdbc"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    url: str
    schema: str
    credentialsProvider: CredentialsProviderConfig
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for JDBCDestinationCreationRequest data.
        
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
                "name": DestinationName.json_schema(),
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
                "url": {
                    "type": "string"
                },
                "schema": {
                    "type": "string"
                },
                "credentialsProvider": CredentialsProviderConfig.json_schema()
            },
            "required": [
                "adt_type",
                "name",
                "description",
                "labels",
                "attributes",
                "url",
                "schema",
                "credentialsProvider",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> JDBCDestinationCreationRequest:
        """Validate and parse JSON data into an instance of JDBCDestinationCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of JDBCDestinationCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return JDBCDestinationCreationRequest(
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                url=str(data["url"]),
                schema=str(data["schema"]),
                credentialsProvider=CredentialsProviderConfig.from_json(data["credentialsProvider"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing JDBCDestinationCreationRequest",
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
            "url": str(self.url),
            "schema": str(self.schema),
            "credentialsProvider": self.credentialsProvider.to_json()
        }


@dataclasses.dataclass(frozen=True)
class HiveDestinationCreationRequest(DestinationCreationRequest):
    """Create a new output data store on Hive.
    
    Args:
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        database (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "hive"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    database: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for HiveDestinationCreationRequest data.
        
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
                "name": DestinationName.json_schema(),
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
                "database": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "name",
                "description",
                "labels",
                "attributes",
                "database",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> HiveDestinationCreationRequest:
        """Validate and parse JSON data into an instance of HiveDestinationCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of HiveDestinationCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return HiveDestinationCreationRequest(
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                database=str(data["database"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing HiveDestinationCreationRequest",
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
            "database": str(self.database)
        }


@dataclasses.dataclass(frozen=True)
class BigQueryDestinationCreationRequest(DestinationCreationRequest):
    """Create a new output data store on Google BigQuery.
    
    Args:
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        path (str): A data field.
        stagingArea (GCSStagingArea): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "bigquery"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    path: str
    stagingArea: GCSStagingArea
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for BigQueryDestinationCreationRequest data.
        
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
                "name": DestinationName.json_schema(),
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
                "path": {
                    "type": "string"
                },
                "stagingArea": GCSStagingArea.json_schema()
            },
            "required": [
                "adt_type",
                "name",
                "description",
                "labels",
                "attributes",
                "path",
                "stagingArea",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> BigQueryDestinationCreationRequest:
        """Validate and parse JSON data into an instance of BigQueryDestinationCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of BigQueryDestinationCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return BigQueryDestinationCreationRequest(
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                path=str(data["path"]),
                stagingArea=GCSStagingArea.from_json(data["stagingArea"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing BigQueryDestinationCreationRequest",
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
            "path": str(self.path),
            "stagingArea": self.stagingArea.to_json()
        }


@dataclasses.dataclass(frozen=True)
class GCSDestinationCreationRequest(DestinationCreationRequest):
    """Create a new output data store on Google Cloud Storage.
    
    Args:
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        bucket (str): A data field.
        path (str): A data field.
        fileFormat (FileFormat): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "gcs"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    bucket: str
    path: str
    fileFormat: FileFormat
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for GCSDestinationCreationRequest data.
        
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
                "name": DestinationName.json_schema(),
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
                "bucket": {
                    "type": "string"
                },
                "path": {
                    "type": "string"
                },
                "fileFormat": FileFormat.json_schema()
            },
            "required": [
                "adt_type",
                "name",
                "description",
                "labels",
                "attributes",
                "bucket",
                "path",
                "fileFormat",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> GCSDestinationCreationRequest:
        """Validate and parse JSON data into an instance of GCSDestinationCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of GCSDestinationCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return GCSDestinationCreationRequest(
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                bucket=str(data["bucket"]),
                path=str(data["path"]),
                fileFormat=FileFormat.from_json(data["fileFormat"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing GCSDestinationCreationRequest",
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
            "bucket": str(self.bucket),
            "path": str(self.path),
            "fileFormat": self.fileFormat.to_json()
        }


@dataclasses.dataclass(frozen=True)
class OnlineFeatureStoreDestinationCreationRequest(DestinationCreationRequest):
    """Create a new output data store using the online feature store.
    
    Args:
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        url (str): A data field.
        schema (str): A data field.
        credentialsProvider (CredentialsProviderConfig): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "onlinefeaturestore"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    url: str
    schema: str
    credentialsProvider: CredentialsProviderConfig
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for OnlineFeatureStoreDestinationCreationRequest data.
        
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
                "name": DestinationName.json_schema(),
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
                "url": {
                    "type": "string"
                },
                "schema": {
                    "type": "string"
                },
                "credentialsProvider": CredentialsProviderConfig.json_schema()
            },
            "required": [
                "adt_type",
                "name",
                "description",
                "labels",
                "attributes",
                "url",
                "schema",
                "credentialsProvider",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> OnlineFeatureStoreDestinationCreationRequest:
        """Validate and parse JSON data into an instance of OnlineFeatureStoreDestinationCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of OnlineFeatureStoreDestinationCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return OnlineFeatureStoreDestinationCreationRequest(
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                url=str(data["url"]),
                schema=str(data["schema"]),
                credentialsProvider=CredentialsProviderConfig.from_json(data["credentialsProvider"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing OnlineFeatureStoreDestinationCreationRequest",
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
            "url": str(self.url),
            "schema": str(self.schema),
            "credentialsProvider": self.credentialsProvider.to_json()
        }


@dataclasses.dataclass(frozen=True)
class LocalDestinationCreationRequest(DestinationCreationRequest):
    """Create a new output data store on the local filesystem.
    
    Args:
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        path (str): A data field.
        fileFormat (FileFormat): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "local"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    path: str
    fileFormat: FileFormat
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for LocalDestinationCreationRequest data.
        
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
                "name": DestinationName.json_schema(),
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
                "path": {
                    "type": "string"
                },
                "fileFormat": FileFormat.json_schema()
            },
            "required": [
                "adt_type",
                "name",
                "description",
                "labels",
                "attributes",
                "path",
                "fileFormat",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> LocalDestinationCreationRequest:
        """Validate and parse JSON data into an instance of LocalDestinationCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of LocalDestinationCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return LocalDestinationCreationRequest(
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                path=str(data["path"]),
                fileFormat=FileFormat.from_json(data["fileFormat"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing LocalDestinationCreationRequest",
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
            "path": str(self.path),
            "fileFormat": self.fileFormat.to_json()
        }


@dataclasses.dataclass(frozen=True)
class HDFSDestinationCreationRequest(DestinationCreationRequest):
    """Create a new output data store on HDFS.
    
    Args:
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        path (str): A data field.
        fileFormat (FileFormat): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "hdfs"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    path: str
    fileFormat: FileFormat
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for HDFSDestinationCreationRequest data.
        
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
                "name": DestinationName.json_schema(),
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
                "path": {
                    "type": "string"
                },
                "fileFormat": FileFormat.json_schema()
            },
            "required": [
                "adt_type",
                "name",
                "description",
                "labels",
                "attributes",
                "path",
                "fileFormat",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> HDFSDestinationCreationRequest:
        """Validate and parse JSON data into an instance of HDFSDestinationCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of HDFSDestinationCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return HDFSDestinationCreationRequest(
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                path=str(data["path"]),
                fileFormat=FileFormat.from_json(data["fileFormat"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing HDFSDestinationCreationRequest",
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
            "path": str(self.path),
            "fileFormat": self.fileFormat.to_json()
        }


@dataclasses.dataclass(frozen=True)
class KafkaDestinationCreationRequest(DestinationCreationRequest):
    """Create a new output data store on Kafka.
    
    Args:
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        bootstrapServers (str): A data field.
        schemaRegistryUrl (str): A data field.
        kafkaPropertiesProviders (typing.List[SensitiveAttribute]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "kafka"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    bootstrapServers: str
    schemaRegistryUrl: str
    kafkaPropertiesProviders: typing.List[SensitiveAttribute]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for KafkaDestinationCreationRequest data.
        
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
                "name": DestinationName.json_schema(),
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
                "bootstrapServers": {
                    "type": "string"
                },
                "schemaRegistryUrl": {
                    "type": "string"
                },
                "kafkaPropertiesProviders": {
                    "type": "array",
                    "item": SensitiveAttribute.json_schema()
                }
            },
            "required": [
                "adt_type",
                "name",
                "description",
                "labels",
                "attributes",
                "bootstrapServers",
                "schemaRegistryUrl",
                "kafkaPropertiesProviders",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> KafkaDestinationCreationRequest:
        """Validate and parse JSON data into an instance of KafkaDestinationCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of KafkaDestinationCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return KafkaDestinationCreationRequest(
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                bootstrapServers=str(data["bootstrapServers"]),
                schemaRegistryUrl=str(data["schemaRegistryUrl"]),
                kafkaPropertiesProviders=[SensitiveAttribute.from_json(v) for v in data["kafkaPropertiesProviders"]],
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing KafkaDestinationCreationRequest",
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
            "bootstrapServers": str(self.bootstrapServers),
            "schemaRegistryUrl": str(self.schemaRegistryUrl),
            "kafkaPropertiesProviders": [v.to_json() for v in self.kafkaPropertiesProviders]
        }


@dataclasses.dataclass(frozen=True)
class SnowflakeDestinationCreationRequest(DestinationCreationRequest):
    """Create a new output data store on Snowflake.
    
    Args:
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        url (str): A data field.
        warehouse (str): A data field.
        database (str): A data field.
        schema (str): A data field.
        credentialsProvider (CredentialsProviderConfig): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "snowflake"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    url: str
    warehouse: str
    database: str
    schema: str
    credentialsProvider: CredentialsProviderConfig
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for SnowflakeDestinationCreationRequest data.
        
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
                "name": DestinationName.json_schema(),
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
                "url": {
                    "type": "string"
                },
                "warehouse": {
                    "type": "string"
                },
                "database": {
                    "type": "string"
                },
                "schema": {
                    "type": "string"
                },
                "credentialsProvider": CredentialsProviderConfig.json_schema()
            },
            "required": [
                "adt_type",
                "name",
                "description",
                "labels",
                "attributes",
                "url",
                "warehouse",
                "database",
                "schema",
                "credentialsProvider",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> SnowflakeDestinationCreationRequest:
        """Validate and parse JSON data into an instance of SnowflakeDestinationCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of SnowflakeDestinationCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return SnowflakeDestinationCreationRequest(
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                url=str(data["url"]),
                warehouse=str(data["warehouse"]),
                database=str(data["database"]),
                schema=str(data["schema"]),
                credentialsProvider=CredentialsProviderConfig.from_json(data["credentialsProvider"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing SnowflakeDestinationCreationRequest",
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
            "url": str(self.url),
            "warehouse": str(self.warehouse),
            "database": str(self.database),
            "schema": str(self.schema),
            "credentialsProvider": self.credentialsProvider.to_json()
        }

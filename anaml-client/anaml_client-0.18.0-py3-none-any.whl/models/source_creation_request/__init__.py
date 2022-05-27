"""Generated implementation of source_creation_request."""

# WARNING DO NOT EDIT
# This code was generated from source-creation-request.mcn

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
from ..file_format import FileFormat
from ..label import Label
from ..source import SourceName


@dataclasses.dataclass(frozen=True)
class SourceCreationRequest(abc.ABC):
    """Requests to create a new input data store.
    
    Args:
        attributes (typing.List[Attribute]): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        name (SourceName): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    attributes: typing.List[Attribute]
    description: str
    labels: typing.List[Label]
    name: SourceName
    
    @classmethod
    def json_schema(cls) -> SourceCreationRequest:
        """JSON schema for variant SourceCreationRequest.
        
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
    def from_json(cls, data: dict) -> SourceCreationRequest:
        """Validate and parse JSON data into an instance of SourceCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of SourceCreationRequest.
        
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
            logging.debug("Invalid JSON data received while parsing SourceCreationRequest", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class S3SourceCreationRequest(SourceCreationRequest):
    """Create a new input data store on AWS S3.
    
    Args:
        name (SourceName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        bucket (str): A data field.
        path (str): A data field.
        fileFormat (FileFormat): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "s3"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: SourceName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    bucket: str
    path: str
    fileFormat: FileFormat
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for S3SourceCreationRequest data.
        
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
                "name": SourceName.json_schema(),
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
    def from_json(cls, data: dict) -> S3SourceCreationRequest:
        """Validate and parse JSON data into an instance of S3SourceCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of S3SourceCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return S3SourceCreationRequest(
                name=SourceName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                bucket=str(data["bucket"]),
                path=str(data["path"]),
                fileFormat=FileFormat.from_json(data["fileFormat"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing S3SourceCreationRequest",
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
class S3ASourceCreationRequest(SourceCreationRequest):
    """Create a new input data store on S3-compatible object storage.
    
    Args:
        name (SourceName): A data field.
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
    
    name: SourceName
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
        """Return the JSON schema for S3ASourceCreationRequest data.
        
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
                "name": SourceName.json_schema(),
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
    def from_json(cls, data: dict) -> S3ASourceCreationRequest:
        """Validate and parse JSON data into an instance of S3ASourceCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of S3ASourceCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return S3ASourceCreationRequest(
                name=SourceName.from_json(data["name"]),
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
                "Invalid JSON data received while parsing S3ASourceCreationRequest",
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
class JDBCSourceCreationRequest(SourceCreationRequest):
    """Create a new input data store using JDBC.
    
    Args:
        name (SourceName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        url (str): A data field.
        schema (str): A data field.
        credentialsProvider (CredentialsProviderConfig): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "jdbc"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: SourceName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    url: str
    schema: str
    credentialsProvider: CredentialsProviderConfig
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for JDBCSourceCreationRequest data.
        
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
                "name": SourceName.json_schema(),
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
    def from_json(cls, data: dict) -> JDBCSourceCreationRequest:
        """Validate and parse JSON data into an instance of JDBCSourceCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of JDBCSourceCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return JDBCSourceCreationRequest(
                name=SourceName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                url=str(data["url"]),
                schema=str(data["schema"]),
                credentialsProvider=CredentialsProviderConfig.from_json(data["credentialsProvider"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing JDBCSourceCreationRequest",
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
class HiveSourceCreationRequest(SourceCreationRequest):
    """Create a new input data store on Hive.
    
    Args:
        name (SourceName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        database (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "hive"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: SourceName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    database: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for HiveSourceCreationRequest data.
        
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
                "name": SourceName.json_schema(),
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
    def from_json(cls, data: dict) -> HiveSourceCreationRequest:
        """Validate and parse JSON data into an instance of HiveSourceCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of HiveSourceCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return HiveSourceCreationRequest(
                name=SourceName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                database=str(data["database"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing HiveSourceCreationRequest",
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
class BigQuerySourceCreationRequest(SourceCreationRequest):
    """Create a new input data store on Google BigQuery.
    
    Args:
        name (SourceName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        path (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "bigquery"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: SourceName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    path: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for BigQuerySourceCreationRequest data.
        
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
                "name": SourceName.json_schema(),
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
                }
            },
            "required": [
                "adt_type",
                "name",
                "description",
                "labels",
                "attributes",
                "path",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> BigQuerySourceCreationRequest:
        """Validate and parse JSON data into an instance of BigQuerySourceCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of BigQuerySourceCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return BigQuerySourceCreationRequest(
                name=SourceName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                path=str(data["path"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing BigQuerySourceCreationRequest",
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
            "path": str(self.path)
        }


@dataclasses.dataclass(frozen=True)
class GCSSourceCreationRequest(SourceCreationRequest):
    """Create a new input data store on Google Cloud Storage.
    
    Args:
        name (SourceName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        bucket (str): A data field.
        path (str): A data field.
        fileFormat (FileFormat): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "gcs"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: SourceName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    bucket: str
    path: str
    fileFormat: FileFormat
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for GCSSourceCreationRequest data.
        
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
                "name": SourceName.json_schema(),
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
    def from_json(cls, data: dict) -> GCSSourceCreationRequest:
        """Validate and parse JSON data into an instance of GCSSourceCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of GCSSourceCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return GCSSourceCreationRequest(
                name=SourceName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                bucket=str(data["bucket"]),
                path=str(data["path"]),
                fileFormat=FileFormat.from_json(data["fileFormat"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing GCSSourceCreationRequest",
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
class LocalSourceCreationRequest(SourceCreationRequest):
    """Create a new input data store on the local filesystem.
    
    Args:
        name (SourceName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        path (str): A data field.
        fileFormat (FileFormat): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "local"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: SourceName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    path: str
    fileFormat: FileFormat
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for LocalSourceCreationRequest data.
        
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
                "name": SourceName.json_schema(),
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
    def from_json(cls, data: dict) -> LocalSourceCreationRequest:
        """Validate and parse JSON data into an instance of LocalSourceCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of LocalSourceCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return LocalSourceCreationRequest(
                name=SourceName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                path=str(data["path"]),
                fileFormat=FileFormat.from_json(data["fileFormat"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing LocalSourceCreationRequest",
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
class HDFSSourceCreationRequest(SourceCreationRequest):
    """Create a new input data store on HDFS.
    
    Args:
        name (SourceName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        path (str): A data field.
        fileFormat (FileFormat): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "hdfs"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: SourceName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    path: str
    fileFormat: FileFormat
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for HDFSSourceCreationRequest data.
        
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
                "name": SourceName.json_schema(),
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
    def from_json(cls, data: dict) -> HDFSSourceCreationRequest:
        """Validate and parse JSON data into an instance of HDFSSourceCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of HDFSSourceCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return HDFSSourceCreationRequest(
                name=SourceName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                path=str(data["path"]),
                fileFormat=FileFormat.from_json(data["fileFormat"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing HDFSSourceCreationRequest",
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
class KafkaSourceCreationRequest(SourceCreationRequest):
    """Create a new input data store on Kafka.
    
    Args:
        name (SourceName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        bootstrapServers (str): A data field.
        schemaRegistryUrl (str): A data field.
        kafkaPropertiesProviders (typing.List[SensitiveAttribute]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "kafka"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    name: SourceName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    bootstrapServers: str
    schemaRegistryUrl: str
    kafkaPropertiesProviders: typing.List[SensitiveAttribute]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for KafkaSourceCreationRequest data.
        
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
                "name": SourceName.json_schema(),
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
    def from_json(cls, data: dict) -> KafkaSourceCreationRequest:
        """Validate and parse JSON data into an instance of KafkaSourceCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of KafkaSourceCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return KafkaSourceCreationRequest(
                name=SourceName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                bootstrapServers=str(data["bootstrapServers"]),
                schemaRegistryUrl=str(data["schemaRegistryUrl"]),
                kafkaPropertiesProviders=[SensitiveAttribute.from_json(v) for v in data["kafkaPropertiesProviders"]],
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing KafkaSourceCreationRequest",
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
class SnowflakeSourceCreationRequest(SourceCreationRequest):
    """Create a new input data store on Snowflake.
    
    Args:
        name (SourceName): A data field.
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
    
    name: SourceName
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
        """Return the JSON schema for SnowflakeSourceCreationRequest data.
        
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
                "name": SourceName.json_schema(),
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
    def from_json(cls, data: dict) -> SnowflakeSourceCreationRequest:
        """Validate and parse JSON data into an instance of SnowflakeSourceCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of SnowflakeSourceCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return SnowflakeSourceCreationRequest(
                name=SourceName.from_json(data["name"]),
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
                "Invalid JSON data received while parsing SnowflakeSourceCreationRequest",
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

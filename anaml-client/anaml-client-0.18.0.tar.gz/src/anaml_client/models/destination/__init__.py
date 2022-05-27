"""Generated implementation of destination."""

# WARNING DO NOT EDIT
# This code was generated from destination.mcn

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

from ..access_control import AccessRule
from ..attribute import Attribute, SensitiveAttribute
from ..credentials_provider_config import CredentialsProviderConfig
from ..file_format import FileFormat
from ..label import Label


@dataclasses.dataclass(frozen=True)
class DestinationId:
    """Unique identifier of a destination.
    
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
        """Return the JSON schema for DestinationId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> DestinationId:
        """Validate and parse JSON data into an instance of DestinationId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of DestinationId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return DestinationId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing DestinationId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> DestinationId:
        """Parse a JSON string such as a dictionary key."""
        return DestinationId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class DestinationName:
    """Unique name of a destination.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for DestinationName data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> DestinationName:
        """Validate and parse JSON data into an instance of DestinationName.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of DestinationName.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return DestinationName(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing DestinationName", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> DestinationName:
        """Parse a JSON string such as a dictionary key."""
        return DestinationName(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class DestinationVersionId:
    """Unique identifier for a specifiv version of a destination.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for DestinationVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> DestinationVersionId:
        """Validate and parse JSON data into an instance of DestinationVersionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of DestinationVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return DestinationVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing DestinationVersionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> DestinationVersionId:
        """Parse a JSON string such as a dictionary key."""
        return DestinationVersionId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class Destination(abc.ABC):
    """Details of a destination data store.
    
    Args:
        accessRules (typing.List[AccessRule]): A data field.
        attributes (typing.List[Attribute]): A data field.
        description (str): A data field.
        id (DestinationId): A data field.
        labels (typing.List[Label]): A data field.
        name (DestinationName): A data field.
        version (DestinationVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    accessRules: typing.List[AccessRule]
    attributes: typing.List[Attribute]
    description: str
    id: DestinationId
    labels: typing.List[Label]
    name: DestinationName
    version: DestinationVersionId
    
    @classmethod
    def json_schema(cls) -> Destination:
        """JSON schema for variant Destination.
        
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
    def from_json(cls, data: dict) -> Destination:
        """Validate and parse JSON data into an instance of Destination.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Destination.
        
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
            logging.debug("Invalid JSON data received while parsing Destination", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class S3Destination(Destination):
    """A data destination in Amazon S3.
    
    Args:
        id (DestinationId): A data field.
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        accessRules (typing.List[AccessRule]): A data field.
        bucket (str): A data field.
        path (str): A data field.
        fileFormat (FileFormat): A data field.
        version (DestinationVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "s3"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: DestinationId
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    accessRules: typing.List[AccessRule]
    bucket: str
    path: str
    fileFormat: FileFormat
    version: DestinationVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for S3Destination data.
        
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
                "id": DestinationId.json_schema(),
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
                "accessRules": {
                    "type": "array",
                    "item": AccessRule.json_schema()
                },
                "bucket": {
                    "type": "string"
                },
                "path": {
                    "type": "string"
                },
                "fileFormat": FileFormat.json_schema(),
                "version": DestinationVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "accessRules",
                "bucket",
                "path",
                "fileFormat",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> S3Destination:
        """Validate and parse JSON data into an instance of S3Destination.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of S3Destination.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return S3Destination(
                id=DestinationId.from_json(data["id"]),
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                accessRules=[AccessRule.from_json(v) for v in data["accessRules"]],
                bucket=str(data["bucket"]),
                path=str(data["path"]),
                fileFormat=FileFormat.from_json(data["fileFormat"]),
                version=DestinationVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing S3Destination",
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
            "accessRules": [v.to_json() for v in self.accessRules],
            "bucket": str(self.bucket),
            "path": str(self.path),
            "fileFormat": self.fileFormat.to_json(),
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class S3ADestination(Destination):
    """A data destination using the S3 protocol.
    
    Args:
        id (DestinationId): A data field.
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        accessRules (typing.List[AccessRule]): A data field.
        bucket (str): A data field.
        path (str): A data field.
        fileFormat (FileFormat): A data field.
        endpoint (str): A data field.
        accessKey (str): A data field.
        secretKey (str): A data field.
        version (DestinationVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "s3a"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: DestinationId
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    accessRules: typing.List[AccessRule]
    bucket: str
    path: str
    fileFormat: FileFormat
    endpoint: str
    accessKey: str
    secretKey: str
    version: DestinationVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for S3ADestination data.
        
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
                "id": DestinationId.json_schema(),
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
                "accessRules": {
                    "type": "array",
                    "item": AccessRule.json_schema()
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
                },
                "version": DestinationVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "accessRules",
                "bucket",
                "path",
                "fileFormat",
                "endpoint",
                "accessKey",
                "secretKey",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> S3ADestination:
        """Validate and parse JSON data into an instance of S3ADestination.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of S3ADestination.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return S3ADestination(
                id=DestinationId.from_json(data["id"]),
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                accessRules=[AccessRule.from_json(v) for v in data["accessRules"]],
                bucket=str(data["bucket"]),
                path=str(data["path"]),
                fileFormat=FileFormat.from_json(data["fileFormat"]),
                endpoint=str(data["endpoint"]),
                accessKey=str(data["accessKey"]),
                secretKey=str(data["secretKey"]),
                version=DestinationVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing S3ADestination",
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
            "accessRules": [v.to_json() for v in self.accessRules],
            "bucket": str(self.bucket),
            "path": str(self.path),
            "fileFormat": self.fileFormat.to_json(),
            "endpoint": str(self.endpoint),
            "accessKey": str(self.accessKey),
            "secretKey": str(self.secretKey),
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class JDBCDestination(Destination):
    """A data destination using JDBC.
    
    Args:
        id (DestinationId): A data field.
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        accessRules (typing.List[AccessRule]): A data field.
        url (str): A data field.
        schema (str): A data field.
        credentialsProvider (CredentialsProviderConfig): A data field.
        version (DestinationVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "jdbc"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: DestinationId
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    accessRules: typing.List[AccessRule]
    url: str
    schema: str
    credentialsProvider: CredentialsProviderConfig
    version: DestinationVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for JDBCDestination data.
        
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
                "id": DestinationId.json_schema(),
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
                "accessRules": {
                    "type": "array",
                    "item": AccessRule.json_schema()
                },
                "url": {
                    "type": "string"
                },
                "schema": {
                    "type": "string"
                },
                "credentialsProvider": CredentialsProviderConfig.json_schema(),
                "version": DestinationVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "accessRules",
                "url",
                "schema",
                "credentialsProvider",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> JDBCDestination:
        """Validate and parse JSON data into an instance of JDBCDestination.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of JDBCDestination.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return JDBCDestination(
                id=DestinationId.from_json(data["id"]),
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                accessRules=[AccessRule.from_json(v) for v in data["accessRules"]],
                url=str(data["url"]),
                schema=str(data["schema"]),
                credentialsProvider=CredentialsProviderConfig.from_json(data["credentialsProvider"]),
                version=DestinationVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing JDBCDestination",
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
            "accessRules": [v.to_json() for v in self.accessRules],
            "url": str(self.url),
            "schema": str(self.schema),
            "credentialsProvider": self.credentialsProvider.to_json(),
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class HiveDestination(Destination):
    """A data destination in Hive.
    
    Args:
        id (DestinationId): A data field.
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        accessRules (typing.List[AccessRule]): A data field.
        database (str): A data field.
        version (DestinationVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "hive"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: DestinationId
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    accessRules: typing.List[AccessRule]
    database: str
    version: DestinationVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for HiveDestination data.
        
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
                "id": DestinationId.json_schema(),
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
                "accessRules": {
                    "type": "array",
                    "item": AccessRule.json_schema()
                },
                "database": {
                    "type": "string"
                },
                "version": DestinationVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "accessRules",
                "database",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> HiveDestination:
        """Validate and parse JSON data into an instance of HiveDestination.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of HiveDestination.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return HiveDestination(
                id=DestinationId.from_json(data["id"]),
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                accessRules=[AccessRule.from_json(v) for v in data["accessRules"]],
                database=str(data["database"]),
                version=DestinationVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing HiveDestination",
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
            "accessRules": [v.to_json() for v in self.accessRules],
            "database": str(self.database),
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class BigQueryDestination(Destination):
    """A data destination in Google BigQuery.
    
    Args:
        id (DestinationId): A data field.
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        accessRules (typing.List[AccessRule]): A data field.
        path (str): A data field.
        stagingArea (GCSStagingArea): A data field.
        version (DestinationVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "bigquery"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: DestinationId
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    accessRules: typing.List[AccessRule]
    path: str
    stagingArea: GCSStagingArea
    version: DestinationVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for BigQueryDestination data.
        
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
                "id": DestinationId.json_schema(),
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
                "accessRules": {
                    "type": "array",
                    "item": AccessRule.json_schema()
                },
                "path": {
                    "type": "string"
                },
                "stagingArea": GCSStagingArea.json_schema(),
                "version": DestinationVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "accessRules",
                "path",
                "stagingArea",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> BigQueryDestination:
        """Validate and parse JSON data into an instance of BigQueryDestination.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of BigQueryDestination.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return BigQueryDestination(
                id=DestinationId.from_json(data["id"]),
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                accessRules=[AccessRule.from_json(v) for v in data["accessRules"]],
                path=str(data["path"]),
                stagingArea=GCSStagingArea.from_json(data["stagingArea"]),
                version=DestinationVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing BigQueryDestination",
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
            "accessRules": [v.to_json() for v in self.accessRules],
            "path": str(self.path),
            "stagingArea": self.stagingArea.to_json(),
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class GCSDestination(Destination):
    """A data destination in Google Cloud Storage.
    
    Args:
        id (DestinationId): A data field.
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        accessRules (typing.List[AccessRule]): A data field.
        bucket (str): A data field.
        path (str): A data field.
        fileFormat (FileFormat): A data field.
        version (DestinationVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "gcs"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: DestinationId
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    accessRules: typing.List[AccessRule]
    bucket: str
    path: str
    fileFormat: FileFormat
    version: DestinationVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for GCSDestination data.
        
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
                "id": DestinationId.json_schema(),
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
                "accessRules": {
                    "type": "array",
                    "item": AccessRule.json_schema()
                },
                "bucket": {
                    "type": "string"
                },
                "path": {
                    "type": "string"
                },
                "fileFormat": FileFormat.json_schema(),
                "version": DestinationVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "accessRules",
                "bucket",
                "path",
                "fileFormat",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> GCSDestination:
        """Validate and parse JSON data into an instance of GCSDestination.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of GCSDestination.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return GCSDestination(
                id=DestinationId.from_json(data["id"]),
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                accessRules=[AccessRule.from_json(v) for v in data["accessRules"]],
                bucket=str(data["bucket"]),
                path=str(data["path"]),
                fileFormat=FileFormat.from_json(data["fileFormat"]),
                version=DestinationVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing GCSDestination",
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
            "accessRules": [v.to_json() for v in self.accessRules],
            "bucket": str(self.bucket),
            "path": str(self.path),
            "fileFormat": self.fileFormat.to_json(),
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class OnlineFeatureStoreDestination(Destination):
    """A data destination on an online feature store.
    
    Args:
        id (DestinationId): A data field.
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        accessRules (typing.List[AccessRule]): A data field.
        url (str): A data field.
        schema (str): A data field.
        credentialsProvider (CredentialsProviderConfig): A data field.
        version (DestinationVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "onlinefeaturestore"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: DestinationId
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    accessRules: typing.List[AccessRule]
    url: str
    schema: str
    credentialsProvider: CredentialsProviderConfig
    version: DestinationVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for OnlineFeatureStoreDestination data.
        
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
                "id": DestinationId.json_schema(),
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
                "accessRules": {
                    "type": "array",
                    "item": AccessRule.json_schema()
                },
                "url": {
                    "type": "string"
                },
                "schema": {
                    "type": "string"
                },
                "credentialsProvider": CredentialsProviderConfig.json_schema(),
                "version": DestinationVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "accessRules",
                "url",
                "schema",
                "credentialsProvider",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> OnlineFeatureStoreDestination:
        """Validate and parse JSON data into an instance of OnlineFeatureStoreDestination.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of OnlineFeatureStoreDestination.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return OnlineFeatureStoreDestination(
                id=DestinationId.from_json(data["id"]),
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                accessRules=[AccessRule.from_json(v) for v in data["accessRules"]],
                url=str(data["url"]),
                schema=str(data["schema"]),
                credentialsProvider=CredentialsProviderConfig.from_json(data["credentialsProvider"]),
                version=DestinationVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing OnlineFeatureStoreDestination",
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
            "accessRules": [v.to_json() for v in self.accessRules],
            "url": str(self.url),
            "schema": str(self.schema),
            "credentialsProvider": self.credentialsProvider.to_json(),
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class LocalDestination(Destination):
    """A data destination on the local filesystem.
    
    Args:
        id (DestinationId): A data field.
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        accessRules (typing.List[AccessRule]): A data field.
        path (str): A data field.
        fileFormat (FileFormat): A data field.
        version (DestinationVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "local"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: DestinationId
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    accessRules: typing.List[AccessRule]
    path: str
    fileFormat: FileFormat
    version: DestinationVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for LocalDestination data.
        
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
                "id": DestinationId.json_schema(),
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
                "accessRules": {
                    "type": "array",
                    "item": AccessRule.json_schema()
                },
                "path": {
                    "type": "string"
                },
                "fileFormat": FileFormat.json_schema(),
                "version": DestinationVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "accessRules",
                "path",
                "fileFormat",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> LocalDestination:
        """Validate and parse JSON data into an instance of LocalDestination.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of LocalDestination.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return LocalDestination(
                id=DestinationId.from_json(data["id"]),
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                accessRules=[AccessRule.from_json(v) for v in data["accessRules"]],
                path=str(data["path"]),
                fileFormat=FileFormat.from_json(data["fileFormat"]),
                version=DestinationVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing LocalDestination",
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
            "accessRules": [v.to_json() for v in self.accessRules],
            "path": str(self.path),
            "fileFormat": self.fileFormat.to_json(),
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class HDFSDestination(Destination):
    """A data destination in HDFS.
    
    Args:
        id (DestinationId): A data field.
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        accessRules (typing.List[AccessRule]): A data field.
        path (str): A data field.
        fileFormat (FileFormat): A data field.
        version (DestinationVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "hdfs"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: DestinationId
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    accessRules: typing.List[AccessRule]
    path: str
    fileFormat: FileFormat
    version: DestinationVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for HDFSDestination data.
        
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
                "id": DestinationId.json_schema(),
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
                "accessRules": {
                    "type": "array",
                    "item": AccessRule.json_schema()
                },
                "path": {
                    "type": "string"
                },
                "fileFormat": FileFormat.json_schema(),
                "version": DestinationVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "accessRules",
                "path",
                "fileFormat",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> HDFSDestination:
        """Validate and parse JSON data into an instance of HDFSDestination.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of HDFSDestination.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return HDFSDestination(
                id=DestinationId.from_json(data["id"]),
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                accessRules=[AccessRule.from_json(v) for v in data["accessRules"]],
                path=str(data["path"]),
                fileFormat=FileFormat.from_json(data["fileFormat"]),
                version=DestinationVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing HDFSDestination",
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
            "accessRules": [v.to_json() for v in self.accessRules],
            "path": str(self.path),
            "fileFormat": self.fileFormat.to_json(),
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class KafkaDestination(Destination):
    """A data destination in a Kafka cluster.
    
    Args:
        id (DestinationId): A data field.
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        accessRules (typing.List[AccessRule]): A data field.
        bootstrapServers (str): A data field.
        schemaRegistryUrl (str): A data field.
        kafkaPropertiesProviders (typing.List[SensitiveAttribute]): A data field.
        version (DestinationVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "kafka"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: DestinationId
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    accessRules: typing.List[AccessRule]
    bootstrapServers: str
    schemaRegistryUrl: str
    kafkaPropertiesProviders: typing.List[SensitiveAttribute]
    version: DestinationVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for KafkaDestination data.
        
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
                "id": DestinationId.json_schema(),
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
                "accessRules": {
                    "type": "array",
                    "item": AccessRule.json_schema()
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
                },
                "version": DestinationVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "accessRules",
                "bootstrapServers",
                "schemaRegistryUrl",
                "kafkaPropertiesProviders",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> KafkaDestination:
        """Validate and parse JSON data into an instance of KafkaDestination.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of KafkaDestination.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return KafkaDestination(
                id=DestinationId.from_json(data["id"]),
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                accessRules=[AccessRule.from_json(v) for v in data["accessRules"]],
                bootstrapServers=str(data["bootstrapServers"]),
                schemaRegistryUrl=str(data["schemaRegistryUrl"]),
                kafkaPropertiesProviders=[SensitiveAttribute.from_json(v) for v in data["kafkaPropertiesProviders"]],
                version=DestinationVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing KafkaDestination",
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
            "accessRules": [v.to_json() for v in self.accessRules],
            "bootstrapServers": str(self.bootstrapServers),
            "schemaRegistryUrl": str(self.schemaRegistryUrl),
            "kafkaPropertiesProviders": [v.to_json() for v in self.kafkaPropertiesProviders],
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class SnowflakeDestination(Destination):
    """A data destination in Snowflake.
    
    Args:
        id (DestinationId): A data field.
        name (DestinationName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        accessRules (typing.List[AccessRule]): A data field.
        url (str): A data field.
        warehouse (str): A data field.
        database (str): A data field.
        schema (str): A data field.
        credentialsProvider (CredentialsProviderConfig): A data field.
        version (DestinationVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "snowflake"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: DestinationId
    name: DestinationName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    accessRules: typing.List[AccessRule]
    url: str
    warehouse: str
    database: str
    schema: str
    credentialsProvider: CredentialsProviderConfig
    version: DestinationVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for SnowflakeDestination data.
        
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
                "id": DestinationId.json_schema(),
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
                "accessRules": {
                    "type": "array",
                    "item": AccessRule.json_schema()
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
                "credentialsProvider": CredentialsProviderConfig.json_schema(),
                "version": DestinationVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "accessRules",
                "url",
                "warehouse",
                "database",
                "schema",
                "credentialsProvider",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> SnowflakeDestination:
        """Validate and parse JSON data into an instance of SnowflakeDestination.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of SnowflakeDestination.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return SnowflakeDestination(
                id=DestinationId.from_json(data["id"]),
                name=DestinationName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                accessRules=[AccessRule.from_json(v) for v in data["accessRules"]],
                url=str(data["url"]),
                warehouse=str(data["warehouse"]),
                database=str(data["database"]),
                schema=str(data["schema"]),
                credentialsProvider=CredentialsProviderConfig.from_json(data["credentialsProvider"]),
                version=DestinationVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing SnowflakeDestination",
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
            "accessRules": [v.to_json() for v in self.accessRules],
            "url": str(self.url),
            "warehouse": str(self.warehouse),
            "database": str(self.database),
            "schema": str(self.schema),
            "credentialsProvider": self.credentialsProvider.to_json(),
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class GCSStagingArea(abc.ABC):
    """Staging area configuration for a Google BigQuery destination.
    
    Args:
        bucket (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    bucket: str
    
    @classmethod
    def json_schema(cls) -> GCSStagingArea:
        """JSON schema for variant GCSStagingArea.
        
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
    def from_json(cls, data: dict) -> GCSStagingArea:
        """Validate and parse JSON data into an instance of GCSStagingArea.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of GCSStagingArea.
        
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
            logging.debug("Invalid JSON data received while parsing GCSStagingArea", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class TemporaryGCSStagingArea(GCSStagingArea):
    """Google BigQuery temporary staging.
    
    Args:
        bucket (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "temporary"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    bucket: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TemporaryGCSStagingArea data.
        
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
                "bucket": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "bucket",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TemporaryGCSStagingArea:
        """Validate and parse JSON data into an instance of TemporaryGCSStagingArea.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TemporaryGCSStagingArea.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TemporaryGCSStagingArea(
                bucket=str(data["bucket"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing TemporaryGCSStagingArea",
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
            "bucket": str(self.bucket)
        }


@dataclasses.dataclass(frozen=True)
class PersistentGCSStagingArea(GCSStagingArea):
    """Google BigQuery permanent staging.
    
    Args:
        bucket (str): A data field.
        path (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "persistent"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    bucket: str
    path: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for PersistentGCSStagingArea data.
        
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
                "bucket": {
                    "type": "string"
                },
                "path": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "bucket",
                "path",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> PersistentGCSStagingArea:
        """Validate and parse JSON data into an instance of PersistentGCSStagingArea.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of PersistentGCSStagingArea.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return PersistentGCSStagingArea(
                bucket=str(data["bucket"]),
                path=str(data["path"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing PersistentGCSStagingArea",
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
            "bucket": str(self.bucket),
            "path": str(self.path)
        }

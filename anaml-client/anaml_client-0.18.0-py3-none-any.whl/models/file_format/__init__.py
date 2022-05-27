"""Generated implementation of file_format."""

# WARNING DO NOT EDIT
# This code was generated from file-format.mcn

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


@dataclasses.dataclass(frozen=True)
class FileFormat(abc.ABC):
    """Supported data store file formats."""
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    @classmethod
    def json_schema(cls) -> FileFormat:
        """JSON schema for variant FileFormat.
        
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
    def from_json(cls, data: dict) -> FileFormat:
        """Validate and parse JSON data into an instance of FileFormat.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FileFormat.
        
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
            logging.debug("Invalid JSON data received while parsing FileFormat", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class Parquet(FileFormat):
    """Apache Parquet format."""
    
    ADT_TYPE: typing.ClassVar[str] = "parquet"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for Parquet data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [cls.ADT_TYPE]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> Parquet:
        """Validate and parse JSON data into an instance of Parquet.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Parquet.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return Parquet(
                
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing Parquet",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "adt_type": self.ADT_TYPE
        }


@dataclasses.dataclass(frozen=True)
class Orc(FileFormat):
    """Apache Orc format."""
    
    ADT_TYPE: typing.ClassVar[str] = "orc"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for Orc data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [cls.ADT_TYPE]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> Orc:
        """Validate and parse JSON data into an instance of Orc.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Orc.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return Orc(
                
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing Orc",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "adt_type": self.ADT_TYPE
        }


@dataclasses.dataclass(frozen=True)
class CSV(FileFormat):
    """Comma separated value format.
    
    These configuration parameters will be passed directly to Spark.
    
    Date and time formatting uses the format strings described in the Spark documentation:
    https://spark.apache.org/docs/latest/sql-ref-datetime-pattern.html
    
    
    Args:
        sep (typing.Optional[str]): A data field.
        quoteAll (typing.Optional[bool]): A data field.
        includeHeader (typing.Optional[bool]): A data field.
        emptyValue (typing.Optional[str]): A data field.
        compression (typing.Optional[str]): A data field.
        dateFormat (typing.Optional[str]): A data field.
        timestampFormat (typing.Optional[str]): A data field.
        ignoreLeadingWhiteSpace (typing.Optional[bool]): A data field.
        ignoreTrailingWhiteSpace (typing.Optional[bool]): A data field.
        lineSep (typing.Optional[str]): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "csv"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    sep: typing.Optional[str]
    quoteAll: typing.Optional[bool]
    includeHeader: typing.Optional[bool]
    emptyValue: typing.Optional[str]
    compression: typing.Optional[str]
    dateFormat: typing.Optional[str]
    timestampFormat: typing.Optional[str]
    ignoreLeadingWhiteSpace: typing.Optional[bool]
    ignoreTrailingWhiteSpace: typing.Optional[bool]
    lineSep: typing.Optional[str]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for CSV data.
        
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
                "sep": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "quoteAll": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "boolean"},
                    ]
                },
                "includeHeader": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "boolean"},
                    ]
                },
                "emptyValue": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "compression": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "dateFormat": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "timestampFormat": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "ignoreLeadingWhiteSpace": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "boolean"},
                    ]
                },
                "ignoreTrailingWhiteSpace": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "boolean"},
                    ]
                },
                "lineSep": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> CSV:
        """Validate and parse JSON data into an instance of CSV.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of CSV.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return CSV(
                sep=(lambda v: v and str(v))(data.get("sep", None)),
                quoteAll=(lambda v: v and bool(v))(data.get("quoteAll", None)),
                includeHeader=(lambda v: v and bool(v))(data.get("includeHeader", None)),
                emptyValue=(lambda v: v and str(v))(data.get("emptyValue", None)),
                compression=(lambda v: v and str(v))(data.get("compression", None)),
                dateFormat=(lambda v: v and str(v))(data.get("dateFormat", None)),
                timestampFormat=(lambda v: v and str(v))(data.get("timestampFormat", None)),
                ignoreLeadingWhiteSpace=(
                    lambda v: v and bool(v)
                )(
                    data.get("ignoreLeadingWhiteSpace", None)
                ),
                ignoreTrailingWhiteSpace=(
                    lambda v: v and bool(v)
                )(
                    data.get("ignoreTrailingWhiteSpace", None)
                ),
                lineSep=(lambda v: v and str(v))(data.get("lineSep", None)),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing CSV",
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
            "sep": (lambda v: v and str(v))(self.sep),
            "quoteAll": (lambda v: v and v)(self.quoteAll),
            "includeHeader": (lambda v: v and v)(self.includeHeader),
            "emptyValue": (lambda v: v and str(v))(self.emptyValue),
            "compression": (lambda v: v and str(v))(self.compression),
            "dateFormat": (lambda v: v and str(v))(self.dateFormat),
            "timestampFormat": (lambda v: v and str(v))(self.timestampFormat),
            "ignoreLeadingWhiteSpace": (lambda v: v and v)(self.ignoreLeadingWhiteSpace),
            "ignoreTrailingWhiteSpace": (lambda v: v and v)(self.ignoreTrailingWhiteSpace),
            "lineSep": (lambda v: v and str(v))(self.lineSep)
        }

"""Generated implementation of table_preview."""

# WARNING DO NOT EDIT
# This code was generated from table-preview.mcn

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
class TablePreview:
    """Preview data for a table.
    
    Args:
        headers (typing.List[Header]): A data field.
        rows (typing.List[TableRow]): A data field.
    """
    
    headers: typing.List[Header]
    rows: typing.List[TableRow]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TablePreview data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "headers": {
                    "type": "array",
                    "item": Header.json_schema()
                },
                "rows": {
                    "type": "array",
                    "item": TableRow.json_schema()
                }
            },
            "required": [
                "headers",
                "rows",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TablePreview:
        """Validate and parse JSON data into an instance of TablePreview.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TablePreview.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TablePreview(
                headers=[Header.from_json(v) for v in data["headers"]],
                rows=[TableRow.from_json(v) for v in data["rows"]],
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing TablePreview",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "headers": [v.to_json() for v in self.headers],
            "rows": [v.to_json() for v in self.rows]
        }


@dataclasses.dataclass(frozen=True)
class TableRow:
    """Individual record from a table preview.
    
    Args:
        cells (typing.List[Cell]): A data field.
    """
    
    cells: typing.List[Cell]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for TableRow data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "cells": {
                    "type": "array",
                    "item": Cell.json_schema()
                }
            },
            "required": [
                "cells",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> TableRow:
        """Validate and parse JSON data into an instance of TableRow.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of TableRow.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return TableRow(
                cells=[Cell.from_json(v) for v in data["cells"]],
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing TableRow",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "cells": [v.to_json() for v in self.cells]
        }


@dataclasses.dataclass(frozen=True)
class Cell(abc.ABC):
    """Individual datum from a table preview."""
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    @classmethod
    def json_schema(cls) -> Cell:
        """JSON schema for variant Cell.
        
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
    def from_json(cls, data: dict) -> Cell:
        """Validate and parse JSON data into an instance of Cell.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Cell.
        
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
            logging.debug("Invalid JSON data received while parsing Cell", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class IntCell(Cell):
    """An integer value in a table preview.
    
    Args:
        data (int): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "int"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    data: int
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for IntCell data.
        
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
                "data": {
                    "type": "integer"
                }
            },
            "required": [
                "adt_type",
                "data",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> IntCell:
        """Validate and parse JSON data into an instance of IntCell.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of IntCell.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return IntCell(
                data=int(data["data"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing IntCell",
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
            "data": int(self.data)
        }


@dataclasses.dataclass(frozen=True)
class LongCell(Cell):
    """A long value in a table preview.
    
    Args:
        data (int): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "long"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    data: int
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for LongCell data.
        
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
                "data": {
                    "type": "integer"
                }
            },
            "required": [
                "adt_type",
                "data",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> LongCell:
        """Validate and parse JSON data into an instance of LongCell.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of LongCell.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return LongCell(
                data=int(data["data"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing LongCell",
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
            "data": self.data
        }


@dataclasses.dataclass(frozen=True)
class DoubleCell(Cell):
    """A double value in a table preview.
    
    Args:
        data (float): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "double"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    data: float
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for DoubleCell data.
        
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
                "data": {
                    "type": "number"
                }
            },
            "required": [
                "adt_type",
                "data",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> DoubleCell:
        """Validate and parse JSON data into an instance of DoubleCell.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of DoubleCell.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return DoubleCell(
                data=float(data["data"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing DoubleCell",
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
            "data": self.data
        }


@dataclasses.dataclass(frozen=True)
class StringCell(Cell):
    """A string value in a table preview.
    
    Args:
        data (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "string"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    data: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for StringCell data.
        
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
                "data": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "data",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> StringCell:
        """Validate and parse JSON data into an instance of StringCell.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of StringCell.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return StringCell(
                data=str(data["data"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing StringCell",
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
            "data": str(self.data)
        }


@dataclasses.dataclass(frozen=True)
class NullCell(Cell):
    """A null value in a table preview."""
    
    ADT_TYPE: typing.ClassVar[str] = "null"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for NullCell data.
        
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
    def from_json(cls, data: dict) -> NullCell:
        """Validate and parse JSON data into an instance of NullCell.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of NullCell.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return NullCell(
                
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing NullCell",
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
class Header:
    """Name of an individual column in a data preview.
    
    Args:
        name (str): A data field.
    """
    
    name: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for Header data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string"
                }
            },
            "required": [
                "name",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> Header:
        """Validate and parse JSON data into an instance of Header.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Header.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return Header(
                name=str(data["name"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing Header",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "name": str(self.name)
        }

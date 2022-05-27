"""Generated implementation of ref."""

# WARNING DO NOT EDIT
# This code was generated from ref.mcn

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
class Ref(abc.ABC):
    """A reference to a branch or commit.
    
    Args:
        ref (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    ref: str
    
    @classmethod
    def json_schema(cls) -> Ref:
        """JSON schema for variant Ref.
        
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
    def from_json(cls, data: dict) -> Ref:
        """Validate and parse JSON data into an instance of Ref.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Ref.
        
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
            logging.debug("Invalid JSON data received while parsing Ref", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class CommitRef(Ref):
    """A reference to a specific commit.
    
    Args:
        ref (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "commit"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    ref: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for CommitRef data.
        
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
                "ref": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "ref",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> CommitRef:
        """Validate and parse JSON data into an instance of CommitRef.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of CommitRef.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return CommitRef(
                ref=str(data["ref"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing CommitRef",
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
            "ref": str(self.ref)
        }


@dataclasses.dataclass(frozen=True)
class BranchRef(Ref):
    """A reference to a branch.
    
    Args:
        ref (str): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "branch"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    ref: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for BranchRef data.
        
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
                "ref": {
                    "type": "string"
                }
            },
            "required": [
                "adt_type",
                "ref",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> BranchRef:
        """Validate and parse JSON data into an instance of BranchRef.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of BranchRef.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return BranchRef(
                ref=str(data["ref"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing BranchRef",
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
            "ref": str(self.ref)
        }

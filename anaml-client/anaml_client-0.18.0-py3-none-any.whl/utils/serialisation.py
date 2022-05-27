#
# Copyright 2021 Simple Machines Pty Ltd - All Rights Reserved.
#
# This file is part of Anaml.
#
# Unauthorized copying and/or distribution of this file, via any medium is
# strictly prohibited.
#
"""Interfaces and implementation of Anaml server serialisation."""
import dataclasses
import datetime
import enum
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Type, Any

import isodate
from jsonschema import validate
from jsonschema.exceptions import ValidationError


# Type variables used in the serialisation interface.
S = TypeVar('S', bound='Serialisation')
E = TypeVar('E', bound='AnamlBaseEnum')
D = TypeVar('D', bound='AnamlBaseClass')


TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
INSTANT_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


logger = logging.getLogger(__name__)


def json_safe(data: Any, datetime_format: Optional[str] = None) -> Any:
    """Convert values to JSON-safe values."""
    if datetime_format is None:
        datetime_format = INSTANT_FORMAT
    if isinstance(data, str) or isinstance(data, bool) or isinstance(data, float) or isinstance(data, int):
        return data
    elif data is None:
        return None
    elif isinstance(data, AnamlBaseClass):
        return data.to_json()
    elif isinstance(data, enum.Enum):
        if callable(getattr(data, 'to_json', None)):
            return data.to_json()
        else:
            return data.value
    elif isinstance(data, uuid.UUID):
        return str(data)
    elif isinstance(data, datetime.timedelta):
        return isodate.duration_isoformat(data)
    elif isinstance(data, datetime.time):
        return data.strftime("%H:%M:%S")
    elif isinstance(data, datetime.datetime):
        # NB: datetime <: date, so make sure you don't switch the order here!
        if datetime_format == INSTANT_FORMAT:
            return data.astimezone(datetime.timezone.utc).strftime(datetime_format)
        else:
            return data.strftime(datetime_format)
    elif isinstance(data, datetime.date):
        return data.isoformat()
    elif isinstance(data, dict):
        return {k: json_safe(v, datetime_format) for k, v in data.items()}
    elif isinstance(data, list):
        return [json_safe(v, datetime_format) for v in data]
    else:
        # TODO: This is probably an error.
        return data


class Serialisation:
    """Serialisation interface for Anaml data-types.

    We use this on dataclasses and enums to
    """

    @classmethod
    def json_schema(cls) -> Optional[dict]:
        """JSON Schema for this resource type."""
        return None

    @classmethod
    @abstractmethod
    def from_dict(cls: Type[S], data: dict) -> S:
        """Construct an instance from a validated dictionary of JSON data."""
        raise NotImplementedError

    @abstractmethod
    def to_dict(self) -> dict:
        """Return a dictionary of fields and values from this object.

        Unlike :ref:`dataclasses.asdict`, this method does not decompose the field values.
        It should be the case that `obj == type(obj)(**self.to_dict())`.
        """
        raise NotImplementedError

    def to_json(self) -> dict:
        """Return a JSON dictionary encoding the object."""
        return json_safe(self.to_dict())

    @classmethod
    def from_json(cls: Type[S], d: dict) -> S:
        """Validate a dictionary of JSON data and parse it into a new instance of this type."""
        try:
            schema = cls.json_schema()
            if schema:
                validate(d, schema)
            return cls.from_dict(d)
        except ValidationError:
            logger.error("Unable to validate {klass} schema {schema} from dict {data}".format(
                klass=cls.__name__, schema=cls.json_schema(), data=d
            ))
            raise


@dataclasses.dataclass(frozen=True)
class AnamlBaseClass(Serialisation, ABC):
    """Base class for data types used in the Anaml API."""

    def to_dict(self) -> dict:
        """Return the object as a dictionary.

        Unlike :ref:`dataclasses.asdict`, this method is not recursive: it returns a dictionary
        of this object only. The values of this object's fields are included unchanged.
        """
        return {
            f.name: getattr(self, f.name) for f in dataclasses.fields(self)
        }


class AnamlBaseEnum(Serialisation, enum.Enum):
    """Base class for enumerations used in the Anaml API."""

    @classmethod
    def json_schema(cls) -> Optional[dict]:
        """Build JSON schema for enumerations encoded as an ADT."""
        return {
            "type": "object",
            "properties": {
                "adt_type": {"type": "string", "enum": [item.value for item in cls]}
            },
            "required": ["adt_type"]
        }

    @classmethod
    def from_dict(cls: Type[E], data: dict) -> E:
        """Parse an enumeration member from valid JSON data."""
        return cls(data['adt_type'])

    def to_dict(self) -> dict:
        """Return the object as a dictionary.

        Unlike :ref:`dataclasses.asdict`, this method is not recursive: it returns a dictionary
        of this object only. The values of this object's fields are included unchanged.
        """
        return {"adt_type": self.value}


class AnamlDirectEnum(AnamlBaseEnum):
    """Base class for enumerations that are directly encoded."""

    @classmethod
    def json_schema(cls) -> Optional[dict]:
        """JSON schema for directly-represented enumerations."""
        return {"type": "string", "enum": [item.value for item in cls]}

    @classmethod
    def from_dict(cls, data: str) -> E:
        """Parse an enumeration value from valid JSON data."""
        return cls(data)

    def to_dict(self) -> dict:
        """Return the ready-for-JSON-ification representation."""
        return self.value


class JsonObject(dict):
    """Passing through the json object."""

    @classmethod
    def json_schema(cls) -> dict:
        """JSON schema for 'JsonObject'.

        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object"
        }

    @classmethod
    def from_json(cls, data: dict) -> dict:
        """Validate and parse JSON data into an instance of JsonObject.

        Args:
            data (dict): JSON data to validate and parse.

        Returns:
            Passes the data through.
        """
        return data

    def to_json(self) -> dict:
        """Serialise this instance as JSON.

        Returns:
            JSON data ready to be serialised.
        """
        return self.value

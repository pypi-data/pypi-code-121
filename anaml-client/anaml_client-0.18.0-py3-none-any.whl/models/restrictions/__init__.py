"""Generated implementation of restrictions."""

# WARNING DO NOT EDIT
# This code was generated from restrictions.mcn

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
class AttributeRestrictionId:
    """Unique identifier for an attribute.
    
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
        """Return the JSON schema for AttributeRestrictionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> AttributeRestrictionId:
        """Validate and parse JSON data into an instance of AttributeRestrictionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of AttributeRestrictionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return AttributeRestrictionId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing AttributeRestrictionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> AttributeRestrictionId:
        """Parse a JSON string such as a dictionary key."""
        return AttributeRestrictionId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class AttributeRestrictionVersionId:
    """Unique identifier of a particular version of an attribute.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for AttributeRestrictionVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> AttributeRestrictionVersionId:
        """Validate and parse JSON data into an instance of AttributeRestrictionVersionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of AttributeRestrictionVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return AttributeRestrictionVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing AttributeRestrictionVersionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> AttributeRestrictionVersionId:
        """Parse a JSON string such as a dictionary key."""
        return AttributeRestrictionVersionId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class AttributeKey:
    """Attribute name.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for AttributeKey data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> AttributeKey:
        """Validate and parse JSON data into an instance of AttributeKey.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of AttributeKey.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return AttributeKey(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing AttributeKey", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> AttributeKey:
        """Parse a JSON string such as a dictionary key."""
        return AttributeKey(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class AttributeDisplay:
    """Display details for an attribute value.
    
    Args:
        emoji (str): A data field.
        colour (str): A data field.
    """
    
    emoji: str
    colour: str
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for AttributeDisplay data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "emoji": {
                    "type": "string"
                },
                "colour": {
                    "type": "string"
                }
            },
            "required": [
                "emoji",
                "colour",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> AttributeDisplay:
        """Validate and parse JSON data into an instance of AttributeDisplay.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of AttributeDisplay.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return AttributeDisplay(
                emoji=str(data["emoji"]),
                colour=str(data["colour"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing AttributeDisplay",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "emoji": str(self.emoji),
            "colour": str(self.colour)
        }


@dataclasses.dataclass(frozen=True)
class AttributeChoice:
    """An attribute value.
    
    Args:
        value (str): A data field.
        display (typing.Optional[AttributeDisplay]): A data field.
    """
    
    value: str
    display: typing.Optional[AttributeDisplay]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for AttributeChoice data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "value": {
                    "type": "string"
                },
                "display": {
                    "oneOf": [
                        {"type": "null"},
                        AttributeDisplay.json_schema(),
                    ]
                }
            },
            "required": [
                "value",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> AttributeChoice:
        """Validate and parse JSON data into an instance of AttributeChoice.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of AttributeChoice.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return AttributeChoice(
                value=str(data["value"]),
                display=(
                    lambda v: v and AttributeDisplay.from_json(v)
                )(
                    data.get("display", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing AttributeChoice",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "value": str(self.value),
            "display": (lambda v: v and v.to_json())(self.display)
        }


class AttributeTarget(enum.Enum):
    """Object types an attribute may be applied to."""
    Cluster = "cluster"
    """Cluster attribute."""
    Destination = "destination"
    """Destination attribute."""
    Entity = "entity"
    """Entity attribute."""
    Feature = "feature"
    """Feature attribute."""
    FeatureSet = "featureset"
    """FeatureSet attribute."""
    FeatureStore = "featurestore"
    """FeatureStore attribute."""
    FeatureTemplate = "featuretemplate"
    """FeatureTemplate attribute."""
    Source = "source"
    """Source attribute."""
    Table = "table"
    """Table attribute."""
    
    @classmethod
    def json_schema(cls) -> dict:
        """JSON schema for 'AttributeTarget'.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "adt_type": {
                    "type": "string",
                    "enum": [
                        "cluster",
                        "destination",
                        "entity",
                        "feature",
                        "featureset",
                        "featurestore",
                        "featuretemplate",
                        "source",
                        "table",
                    ]
                }
            },
            "required": [
                "adt_type",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> AttributeTarget:
        """Validate and parse JSON data into an instance of AttributeTarget.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of AttributeTarget.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return AttributeTarget(str(data['adt_type']))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing AttributeTarget", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            JSON data ready to be serialised.
        """
        return {'adt_type': self.value}
    
    @classmethod
    def from_json_key(cls, data: str) -> AttributeTarget:
        """Validate and parse a value from a JSON dictionary key.
        
        Args:
            data (str): JSON data to validate and parse.
        
        Returns:
            An instance of AttributeTarget.
        """
        return AttributeTarget(str(data))
    
    def to_json_key(self) -> str:
        """Serialised this instanse as a JSON string for use as a dictionary key.
        
        Returns:
            A JSON string ready to be used as a key.
        """
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class AttributeRestriction(abc.ABC):
    """Defines attributes, values, and the objects they can be applied to.
    
    Args:
        appliesTo (typing.List[AttributeTarget]): A data field.
        description (str): A data field.
        id (AttributeRestrictionId): A data field.
        key (AttributeKey): A data field.
        version (AttributeRestrictionVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = ""
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    appliesTo: typing.List[AttributeTarget]
    description: str
    id: AttributeRestrictionId
    key: AttributeKey
    version: AttributeRestrictionVersionId
    
    @classmethod
    def json_schema(cls) -> AttributeRestriction:
        """JSON schema for variant AttributeRestriction.
        
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
    def from_json(cls, data: dict) -> AttributeRestriction:
        """Validate and parse JSON data into an instance of AttributeRestriction.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of AttributeRestriction.
        
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
            logging.debug("Invalid JSON data received while parsing AttributeRestriction", exc_info=ex)
            raise
    
    @abc.abstractmethod
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class EnumAttribute(AttributeRestriction):
    """Enumeration attribute with fixed choices.
    
    Args:
        id (AttributeRestrictionId): A data field.
        key (AttributeKey): A data field.
        description (str): A data field.
        choices (typing.List[AttributeChoice]): A data field.
        appliesTo (typing.List[AttributeTarget]): A data field.
        version (AttributeRestrictionVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "enumattribute"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: AttributeRestrictionId
    key: AttributeKey
    description: str
    choices: typing.List[AttributeChoice]
    appliesTo: typing.List[AttributeTarget]
    version: AttributeRestrictionVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EnumAttribute data.
        
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
                "id": AttributeRestrictionId.json_schema(),
                "key": AttributeKey.json_schema(),
                "description": {
                    "type": "string"
                },
                "choices": {
                    "type": "array",
                    "item": AttributeChoice.json_schema()
                },
                "appliesTo": {
                    "type": "array",
                    "item": AttributeTarget.json_schema()
                },
                "version": AttributeRestrictionVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "key",
                "description",
                "choices",
                "appliesTo",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EnumAttribute:
        """Validate and parse JSON data into an instance of EnumAttribute.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EnumAttribute.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EnumAttribute(
                id=AttributeRestrictionId.from_json(data["id"]),
                key=AttributeKey.from_json(data["key"]),
                description=str(data["description"]),
                choices=[AttributeChoice.from_json(v) for v in data["choices"]],
                appliesTo=[AttributeTarget.from_json(v) for v in data["appliesTo"]],
                version=AttributeRestrictionVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EnumAttribute",
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
            "key": self.key.to_json(),
            "description": str(self.description),
            "choices": [v.to_json() for v in self.choices],
            "appliesTo": [v.to_json() for v in self.appliesTo],
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class FreeTextAttribute(AttributeRestriction):
    """Free text (String) response attribute.
    
    Args:
        id (AttributeRestrictionId): A data field.
        key (AttributeKey): A data field.
        description (str): A data field.
        appliesTo (typing.List[AttributeTarget]): A data field.
        version (AttributeRestrictionVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "freetextattribute"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: AttributeRestrictionId
    key: AttributeKey
    description: str
    appliesTo: typing.List[AttributeTarget]
    version: AttributeRestrictionVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for FreeTextAttribute data.
        
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
                "id": AttributeRestrictionId.json_schema(),
                "key": AttributeKey.json_schema(),
                "description": {
                    "type": "string"
                },
                "appliesTo": {
                    "type": "array",
                    "item": AttributeTarget.json_schema()
                },
                "version": AttributeRestrictionVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "key",
                "description",
                "appliesTo",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> FreeTextAttribute:
        """Validate and parse JSON data into an instance of FreeTextAttribute.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of FreeTextAttribute.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return FreeTextAttribute(
                id=AttributeRestrictionId.from_json(data["id"]),
                key=AttributeKey.from_json(data["key"]),
                description=str(data["description"]),
                appliesTo=[AttributeTarget.from_json(v) for v in data["appliesTo"]],
                version=AttributeRestrictionVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing FreeTextAttribute",
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
            "key": self.key.to_json(),
            "description": str(self.description),
            "appliesTo": [v.to_json() for v in self.appliesTo],
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class IntegerAttribute(AttributeRestriction):
    """Integer response attribute.
    
    Args:
        id (AttributeRestrictionId): A data field.
        key (AttributeKey): A data field.
        description (str): A data field.
        appliesTo (typing.List[AttributeTarget]): A data field.
        version (AttributeRestrictionVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "integerattribute"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: AttributeRestrictionId
    key: AttributeKey
    description: str
    appliesTo: typing.List[AttributeTarget]
    version: AttributeRestrictionVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for IntegerAttribute data.
        
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
                "id": AttributeRestrictionId.json_schema(),
                "key": AttributeKey.json_schema(),
                "description": {
                    "type": "string"
                },
                "appliesTo": {
                    "type": "array",
                    "item": AttributeTarget.json_schema()
                },
                "version": AttributeRestrictionVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "key",
                "description",
                "appliesTo",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> IntegerAttribute:
        """Validate and parse JSON data into an instance of IntegerAttribute.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of IntegerAttribute.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return IntegerAttribute(
                id=AttributeRestrictionId.from_json(data["id"]),
                key=AttributeKey.from_json(data["key"]),
                description=str(data["description"]),
                appliesTo=[AttributeTarget.from_json(v) for v in data["appliesTo"]],
                version=AttributeRestrictionVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing IntegerAttribute",
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
            "key": self.key.to_json(),
            "description": str(self.description),
            "appliesTo": [v.to_json() for v in self.appliesTo],
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class BooleanAttribute(AttributeRestriction):
    """Boolean response attribute.
    
    Args:
        id (AttributeRestrictionId): A data field.
        key (AttributeKey): A data field.
        description (str): A data field.
        appliesTo (typing.List[AttributeTarget]): A data field.
        version (AttributeRestrictionVersionId): A data field.
    """
    
    ADT_TYPE: typing.ClassVar[str] = "booleanattribute"
    adt_type: str = dataclasses.field(init=False, repr=False, default=ADT_TYPE)
    
    id: AttributeRestrictionId
    key: AttributeKey
    description: str
    appliesTo: typing.List[AttributeTarget]
    version: AttributeRestrictionVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for BooleanAttribute data.
        
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
                "id": AttributeRestrictionId.json_schema(),
                "key": AttributeKey.json_schema(),
                "description": {
                    "type": "string"
                },
                "appliesTo": {
                    "type": "array",
                    "item": AttributeTarget.json_schema()
                },
                "version": AttributeRestrictionVersionId.json_schema()
            },
            "required": [
                "adt_type",
                "id",
                "key",
                "description",
                "appliesTo",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> BooleanAttribute:
        """Validate and parse JSON data into an instance of BooleanAttribute.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of BooleanAttribute.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return BooleanAttribute(
                id=AttributeRestrictionId.from_json(data["id"]),
                key=AttributeKey.from_json(data["key"]),
                description=str(data["description"]),
                appliesTo=[AttributeTarget.from_json(v) for v in data["appliesTo"]],
                version=AttributeRestrictionVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing BooleanAttribute",
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
            "key": self.key.to_json(),
            "description": str(self.description),
            "appliesTo": [v.to_json() for v in self.appliesTo],
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class LabelRestrictionId:
    """Unique identifier for an attribute.
    
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
        """Return the JSON schema for LabelRestrictionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> LabelRestrictionId:
        """Validate and parse JSON data into an instance of LabelRestrictionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of LabelRestrictionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return LabelRestrictionId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing LabelRestrictionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> LabelRestrictionId:
        """Parse a JSON string such as a dictionary key."""
        return LabelRestrictionId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class LabelRestrictionVersionId:
    """Unique identifier of a particular version of an attribute.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for LabelRestrictionVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> LabelRestrictionVersionId:
        """Validate and parse JSON data into an instance of LabelRestrictionVersionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of LabelRestrictionVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return LabelRestrictionVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing LabelRestrictionVersionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> LabelRestrictionVersionId:
        """Parse a JSON string such as a dictionary key."""
        return LabelRestrictionVersionId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class LabelRestriction:
    """Label restriction rule.
    
    Args:
        id (LabelRestrictionId): A data field.
        text (str): A data field.
        emoji (typing.Optional[str]): A data field.
        colour (typing.Optional[str]): A data field.
        version (LabelRestrictionVersionId): A data field.
    """
    
    id: LabelRestrictionId
    text: str
    emoji: typing.Optional[str]
    colour: typing.Optional[str]
    version: LabelRestrictionVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for LabelRestriction data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": LabelRestrictionId.json_schema(),
                "text": {
                    "type": "string"
                },
                "emoji": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "colour": {
                    "oneOf": [
                        {"type": "null"},
                        {"type": "string"},
                    ]
                },
                "version": LabelRestrictionVersionId.json_schema()
            },
            "required": [
                "id",
                "text",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> LabelRestriction:
        """Validate and parse JSON data into an instance of LabelRestriction.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of LabelRestriction.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return LabelRestriction(
                id=LabelRestrictionId.from_json(data["id"]),
                text=str(data["text"]),
                emoji=(lambda v: v and str(v))(data.get("emoji", None)),
                colour=(lambda v: v and str(v))(data.get("colour", None)),
                version=LabelRestrictionVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing LabelRestriction",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "id": self.id.to_json(),
            "text": str(self.text),
            "emoji": (lambda v: v and str(v))(self.emoji),
            "colour": (lambda v: v and str(v))(self.colour),
            "version": self.version.to_json()
        }

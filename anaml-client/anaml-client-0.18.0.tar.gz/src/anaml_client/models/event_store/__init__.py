"""Generated implementation of event_store."""

# WARNING DO NOT EDIT
# This code was generated from event-store.mcn

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
from ..cluster import ClusterId
from ..entity import EntityId
from ..event_description import TimestampInfo
from ..jobs import RunStatus
from ..label import Label
from ..schedule import Schedule


@dataclasses.dataclass(frozen=True)
class EventStoreId:
    """Unique identifier for an event store.
    
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
        """Return the JSON schema for EventStoreId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EventStoreId:
        """Validate and parse JSON data into an instance of EventStoreId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EventStoreId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EventStoreId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing EventStoreId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> EventStoreId:
        """Parse a JSON string such as a dictionary key."""
        return EventStoreId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class EventStoreVersionId:
    """Unique identifier of a particular version of an event store.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EventStoreVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EventStoreVersionId:
        """Validate and parse JSON data into an instance of EventStoreVersionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EventStoreVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EventStoreVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing EventStoreVersionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> EventStoreVersionId:
        """Parse a JSON string such as a dictionary key."""
        return EventStoreVersionId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class EventStoreRunId:
    """Unique identifier of an event store run.
    
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
        """Return the JSON schema for EventStoreRunId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EventStoreRunId:
        """Validate and parse JSON data into an instance of EventStoreRunId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EventStoreRunId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EventStoreRunId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing EventStoreRunId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return self.value
    
    @classmethod
    def from_json_key(cls, data: str) -> EventStoreRunId:
        """Parse a JSON string such as a dictionary key."""
        return EventStoreRunId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class EventStoreName:
    """Unique name of an event store.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EventStoreName data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EventStoreName:
        """Validate and parse JSON data into an instance of EventStoreName.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EventStoreName.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EventStoreName(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing EventStoreName", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> EventStoreName:
        """Parse a JSON string such as a dictionary key."""
        return EventStoreName(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class Topic:
    """Unique name of topic in an event store.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for Topic data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> Topic:
        """Validate and parse JSON data into an instance of Topic.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Topic.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return Topic(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing Topic", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> Topic:
        """Parse a JSON string such as a dictionary key."""
        return Topic(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class EventStoreTopicColumns:
    """Columns in topic of an event store.
    
    Args:
        entity (str): A data field.
        timestampInfo (TimestampInfo): A data field.
    """
    
    entity: str
    timestampInfo: TimestampInfo
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EventStoreTopicColumns data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "entity": {
                    "type": "string"
                },
                "timestampInfo": TimestampInfo.json_schema()
            },
            "required": [
                "entity",
                "timestampInfo",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EventStoreTopicColumns:
        """Validate and parse JSON data into an instance of EventStoreTopicColumns.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EventStoreTopicColumns.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EventStoreTopicColumns(
                entity=str(data["entity"]),
                timestampInfo=TimestampInfo.from_json(data["timestampInfo"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EventStoreTopicColumns",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "entity": str(self.entity),
            "timestampInfo": self.timestampInfo.to_json()
        }


@dataclasses.dataclass(frozen=True)
class EventStore:
    """Details for an event store.
    
    Args:
        id (EventStoreId): A data field.
        name (EventStoreName): A data field.
        description (str): A data field.
        labels (typing.List[Label]): A data field.
        attributes (typing.List[Attribute]): A data field.
        accessRules (typing.List[AccessRule]): A data field.
        bootstrapServers (str): A data field.
        schemaRegistryUrl (str): A data field.
        kafkaPropertiesProviders (typing.List[SensitiveAttribute]): A data field.
        ingestions (typing.Dict[Topic, EventStoreTopicColumns]): A data field.
        connectBaseURI (str): A data field.
        scatterBaseURI (str): A data field.
        glacierBaseURI (str): A data field.
        schedule (Schedule): A data field.
        cluster (ClusterId): A data field.
        version (EventStoreVersionId): A data field.
    """
    
    id: EventStoreId
    name: EventStoreName
    description: str
    labels: typing.List[Label]
    attributes: typing.List[Attribute]
    accessRules: typing.List[AccessRule]
    bootstrapServers: str
    schemaRegistryUrl: str
    kafkaPropertiesProviders: typing.List[SensitiveAttribute]
    ingestions: typing.Dict[Topic, EventStoreTopicColumns]
    connectBaseURI: str
    scatterBaseURI: str
    glacierBaseURI: str
    schedule: Schedule
    cluster: ClusterId
    version: EventStoreVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EventStore data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": EventStoreId.json_schema(),
                "name": EventStoreName.json_schema(),
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
                "ingestions": {
                    "type": "object",
                    "additionalProperties": EventStoreTopicColumns.json_schema()
                },
                "connectBaseURI": {
                    "type": "string"
                },
                "scatterBaseURI": {
                    "type": "string"
                },
                "glacierBaseURI": {
                    "type": "string"
                },
                "schedule": Schedule.json_schema(),
                "cluster": ClusterId.json_schema(),
                "version": EventStoreVersionId.json_schema()
            },
            "required": [
                "id",
                "name",
                "description",
                "labels",
                "attributes",
                "accessRules",
                "bootstrapServers",
                "schemaRegistryUrl",
                "kafkaPropertiesProviders",
                "ingestions",
                "connectBaseURI",
                "scatterBaseURI",
                "glacierBaseURI",
                "schedule",
                "cluster",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EventStore:
        """Validate and parse JSON data into an instance of EventStore.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EventStore.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EventStore(
                id=EventStoreId.from_json(data["id"]),
                name=EventStoreName.from_json(data["name"]),
                description=str(data["description"]),
                labels=[Label.from_json(v) for v in data["labels"]],
                attributes=[Attribute.from_json(v) for v in data["attributes"]],
                accessRules=[AccessRule.from_json(v) for v in data["accessRules"]],
                bootstrapServers=str(data["bootstrapServers"]),
                schemaRegistryUrl=str(data["schemaRegistryUrl"]),
                kafkaPropertiesProviders=[SensitiveAttribute.from_json(v) for v in data["kafkaPropertiesProviders"]],
                ingestions={
                    Topic.from_json_key(k): EventStoreTopicColumns.from_json(v) for k, v in data["ingestions"].items()
                },
                connectBaseURI=str(data["connectBaseURI"]),
                scatterBaseURI=str(data["scatterBaseURI"]),
                glacierBaseURI=str(data["glacierBaseURI"]),
                schedule=Schedule.from_json(data["schedule"]),
                cluster=ClusterId.from_json(data["cluster"]),
                version=EventStoreVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EventStore",
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
            "name": self.name.to_json(),
            "description": str(self.description),
            "labels": [v.to_json() for v in self.labels],
            "attributes": [v.to_json() for v in self.attributes],
            "accessRules": [v.to_json() for v in self.accessRules],
            "bootstrapServers": str(self.bootstrapServers),
            "schemaRegistryUrl": str(self.schemaRegistryUrl),
            "kafkaPropertiesProviders": [v.to_json() for v in self.kafkaPropertiesProviders],
            "ingestions": {k.to_json_key(): v.to_json() for k, v in self.ingestions.items()},
            "connectBaseURI": str(self.connectBaseURI),
            "scatterBaseURI": str(self.scatterBaseURI),
            "glacierBaseURI": str(self.glacierBaseURI),
            "schedule": self.schedule.to_json(),
            "cluster": self.cluster.to_json(),
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class EventStoreReference:
    """A location to read input in a source data store.
    
    Args:
        eventStoreId (EventStoreId): A data field.
        topic (str): A data field.
        entity (EntityId): A data field.
    """
    
    eventStoreId: EventStoreId
    topic: str
    entity: EntityId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EventStoreReference data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "eventStoreId": EventStoreId.json_schema(),
                "topic": {
                    "type": "string"
                },
                "entity": EntityId.json_schema()
            },
            "required": [
                "eventStoreId",
                "topic",
                "entity",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EventStoreReference:
        """Validate and parse JSON data into an instance of EventStoreReference.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EventStoreReference.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EventStoreReference(
                eventStoreId=EventStoreId.from_json(data["eventStoreId"]),
                topic=str(data["topic"]),
                entity=EntityId.from_json(data["entity"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EventStoreReference",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "eventStoreId": self.eventStoreId.to_json(),
            "topic": str(self.topic),
            "entity": self.entity.to_json()
        }


@dataclasses.dataclass(frozen=True)
class EventStoreGlacierId:
    """Unique id of an allocated glacier.
    
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
        """Return the JSON schema for EventStoreGlacierId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EventStoreGlacierId:
        """Validate and parse JSON data into an instance of EventStoreGlacierId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EventStoreGlacierId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EventStoreGlacierId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing EventStoreGlacierId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> EventStoreGlacierId:
        """Parse a JSON string such as a dictionary key."""
        return EventStoreGlacierId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class EventStoreGlacierCommitId:
    """Glacier commit for keeping track of files externally?
    
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
        """Return the JSON schema for EventStoreGlacierCommitId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EventStoreGlacierCommitId:
        """Validate and parse JSON data into an instance of EventStoreGlacierCommitId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EventStoreGlacierCommitId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EventStoreGlacierCommitId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing EventStoreGlacierCommitId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> EventStoreGlacierCommitId:
        """Parse a JSON string such as a dictionary key."""
        return EventStoreGlacierCommitId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class EventStoreGlacier:
    """An allocated glacier.
    
    Args:
        id (EventStoreGlacierId): A data field.
        glacierCommit (typing.Optional[EventStoreGlacierCommitId]): A data field.
        eventStoreId (EventStoreId): A data field.
        eventStoreVersionId (EventStoreVersionId): A data field.
        status (RunStatus): A data field.
        created (datetime.datetime): A data field.
        valid (bool): A data field.
    """
    
    id: EventStoreGlacierId
    glacierCommit: typing.Optional[EventStoreGlacierCommitId]
    eventStoreId: EventStoreId
    eventStoreVersionId: EventStoreVersionId
    status: RunStatus
    created: datetime.datetime
    valid: bool
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EventStoreGlacier data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": EventStoreGlacierId.json_schema(),
                "glacierCommit": {
                    "oneOf": [
                        {"type": "null"},
                        EventStoreGlacierCommitId.json_schema(),
                    ]
                },
                "eventStoreId": EventStoreId.json_schema(),
                "eventStoreVersionId": EventStoreVersionId.json_schema(),
                "status": RunStatus.json_schema(),
                "created": {
                    "type": "string",
                    "format": "date-time"
                },
                "valid": {
                    "type": "boolean"
                }
            },
            "required": [
                "id",
                "eventStoreId",
                "eventStoreVersionId",
                "status",
                "created",
                "valid",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EventStoreGlacier:
        """Validate and parse JSON data into an instance of EventStoreGlacier.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EventStoreGlacier.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EventStoreGlacier(
                id=EventStoreGlacierId.from_json(data["id"]),
                glacierCommit=(
                    lambda v: v and EventStoreGlacierCommitId.from_json(v)
                )(
                    data.get("glacierCommit", None)
                ),
                eventStoreId=EventStoreId.from_json(data["eventStoreId"]),
                eventStoreVersionId=EventStoreVersionId.from_json(data["eventStoreVersionId"]),
                status=RunStatus.from_json(data["status"]),
                created=isodate.parse_datetime(data["created"]),
                valid=bool(data["valid"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EventStoreGlacier",
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
            "glacierCommit": (lambda v: v and v.to_json())(self.glacierCommit),
            "eventStoreId": self.eventStoreId.to_json(),
            "eventStoreVersionId": self.eventStoreVersionId.to_json(),
            "status": self.status.to_json(),
            "created": self.created.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "valid": self.valid
        }


@dataclasses.dataclass(frozen=True)
class EventStoreGlacierCreationRequest:
    """Update a Glacier.
    
    Args:
        glacierCommit (typing.Optional[EventStoreGlacierCommitId]): A data field.
        eventStoreId (EventStoreId): A data field.
        eventStoreVersionId (EventStoreVersionId): A data field.
        status (RunStatus): A data field.
        valid (bool): A data field.
    """
    
    glacierCommit: typing.Optional[EventStoreGlacierCommitId]
    eventStoreId: EventStoreId
    eventStoreVersionId: EventStoreVersionId
    status: RunStatus
    valid: bool
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EventStoreGlacierCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "glacierCommit": {
                    "oneOf": [
                        {"type": "null"},
                        EventStoreGlacierCommitId.json_schema(),
                    ]
                },
                "eventStoreId": EventStoreId.json_schema(),
                "eventStoreVersionId": EventStoreVersionId.json_schema(),
                "status": RunStatus.json_schema(),
                "valid": {
                    "type": "boolean"
                }
            },
            "required": [
                "eventStoreId",
                "eventStoreVersionId",
                "status",
                "valid",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EventStoreGlacierCreationRequest:
        """Validate and parse JSON data into an instance of EventStoreGlacierCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EventStoreGlacierCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EventStoreGlacierCreationRequest(
                glacierCommit=(
                    lambda v: v and EventStoreGlacierCommitId.from_json(v)
                )(
                    data.get("glacierCommit", None)
                ),
                eventStoreId=EventStoreId.from_json(data["eventStoreId"]),
                eventStoreVersionId=EventStoreVersionId.from_json(data["eventStoreVersionId"]),
                status=RunStatus.from_json(data["status"]),
                valid=bool(data["valid"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EventStoreGlacierCreationRequest",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "glacierCommit": (lambda v: v and v.to_json())(self.glacierCommit),
            "eventStoreId": self.eventStoreId.to_json(),
            "eventStoreVersionId": self.eventStoreVersionId.to_json(),
            "status": self.status.to_json(),
            "valid": self.valid
        }

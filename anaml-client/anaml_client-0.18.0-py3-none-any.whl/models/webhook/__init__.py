"""Generated implementation of webhook."""

# WARNING DO NOT EDIT
# This code was generated from webhook.mcn

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
class WebhookId:
    """Unique identifier of a webhook.
    
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
        """Return the JSON schema for WebhookId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "integer"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> WebhookId:
        """Validate and parse JSON data into an instance of WebhookId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of WebhookId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return WebhookId(int(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing WebhookId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return int(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> WebhookId:
        """Parse a JSON string such as a dictionary key."""
        return WebhookId(int(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class WebhookName:
    """Unique name of a webhook.
    
    Args:
        value (str): A data field.
    """
    
    value: str
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for WebhookName data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> WebhookName:
        """Validate and parse JSON data into an instance of WebhookName.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of WebhookName.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return WebhookName(str(data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing WebhookName", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> WebhookName:
        """Parse a JSON string such as a dictionary key."""
        return WebhookName(str(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class WebhookVersionId:
    """Unique identifier of a specific version of a webhook.
    
    Args:
        value (uuid.UUID): A data field.
    """
    
    value: uuid.UUID
    
    def __str__(self) -> str:
        """Return a str of the wrapped value."""
        return str(self.value)
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for WebhookVersionId data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "string",
            "format": "uuid"
        }
    
    @classmethod
    def from_json(cls, data: dict) -> WebhookVersionId:
        """Validate and parse JSON data into an instance of WebhookVersionId.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of WebhookVersionId.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return WebhookVersionId(uuid.UUID(hex=data))
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug("Invalid JSON data received while parsing WebhookVersionId", exc_info=ex)
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return str(self.value)
    
    @classmethod
    def from_json_key(cls, data: str) -> WebhookVersionId:
        """Parse a JSON string such as a dictionary key."""
        return WebhookVersionId((lambda s: uuid.UUID(hex=s))(data))
    
    def to_json_key(self) -> str:
        """Serialise as a JSON string suitable for use as a dictionary key."""
        return str(self.value)


@dataclasses.dataclass(frozen=True)
class EventConfiguration:
    """Webhook configuration for a specific event type."""
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for EventConfiguration data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
            
            },
            "required": []
        }
    
    @classmethod
    def from_json(cls, data: dict) -> EventConfiguration:
        """Validate and parse JSON data into an instance of EventConfiguration.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of EventConfiguration.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return EventConfiguration(
                
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing EventConfiguration",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
        
        }


@dataclasses.dataclass(frozen=True)
class Webhook:
    """Configuration for a webhook.
    
    Args:
        id (WebhookId): A data field.
        name (WebhookName): A data field.
        description (str): A data field.
        url (str): A data field.
        mergeRequests (typing.Optional[EventConfiguration]): A data field.
        mergeRequestComments (typing.Optional[EventConfiguration]): A data field.
        commits (typing.Optional[EventConfiguration]): A data field.
        featureStoreRuns (typing.Optional[EventConfiguration]): A data field.
        monitoringRuns (typing.Optional[EventConfiguration]): A data field.
        cachingRuns (typing.Optional[EventConfiguration]): A data field.
        materialisationRuns (typing.Optional[EventConfiguration]): A data field.
        version (WebhookVersionId): A data field.
    """
    
    id: WebhookId
    name: WebhookName
    description: str
    url: str
    mergeRequests: typing.Optional[EventConfiguration]
    mergeRequestComments: typing.Optional[EventConfiguration]
    commits: typing.Optional[EventConfiguration]
    featureStoreRuns: typing.Optional[EventConfiguration]
    monitoringRuns: typing.Optional[EventConfiguration]
    cachingRuns: typing.Optional[EventConfiguration]
    materialisationRuns: typing.Optional[EventConfiguration]
    version: WebhookVersionId
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for Webhook data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": WebhookId.json_schema(),
                "name": WebhookName.json_schema(),
                "description": {
                    "type": "string"
                },
                "url": {
                    "type": "string"
                },
                "mergeRequests": {
                    "oneOf": [
                        {"type": "null"},
                        EventConfiguration.json_schema(),
                    ]
                },
                "mergeRequestComments": {
                    "oneOf": [
                        {"type": "null"},
                        EventConfiguration.json_schema(),
                    ]
                },
                "commits": {
                    "oneOf": [
                        {"type": "null"},
                        EventConfiguration.json_schema(),
                    ]
                },
                "featureStoreRuns": {
                    "oneOf": [
                        {"type": "null"},
                        EventConfiguration.json_schema(),
                    ]
                },
                "monitoringRuns": {
                    "oneOf": [
                        {"type": "null"},
                        EventConfiguration.json_schema(),
                    ]
                },
                "cachingRuns": {
                    "oneOf": [
                        {"type": "null"},
                        EventConfiguration.json_schema(),
                    ]
                },
                "materialisationRuns": {
                    "oneOf": [
                        {"type": "null"},
                        EventConfiguration.json_schema(),
                    ]
                },
                "version": WebhookVersionId.json_schema()
            },
            "required": [
                "id",
                "name",
                "description",
                "url",
                "version",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> Webhook:
        """Validate and parse JSON data into an instance of Webhook.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of Webhook.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return Webhook(
                id=WebhookId.from_json(data["id"]),
                name=WebhookName.from_json(data["name"]),
                description=str(data["description"]),
                url=str(data["url"]),
                mergeRequests=(
                    lambda v: v and EventConfiguration.from_json(v)
                )(
                    data.get("mergeRequests", None)
                ),
                mergeRequestComments=(
                    lambda v: v and EventConfiguration.from_json(v)
                )(
                    data.get("mergeRequestComments", None)
                ),
                commits=(
                    lambda v: v and EventConfiguration.from_json(v)
                )(
                    data.get("commits", None)
                ),
                featureStoreRuns=(
                    lambda v: v and EventConfiguration.from_json(v)
                )(
                    data.get("featureStoreRuns", None)
                ),
                monitoringRuns=(
                    lambda v: v and EventConfiguration.from_json(v)
                )(
                    data.get("monitoringRuns", None)
                ),
                cachingRuns=(
                    lambda v: v and EventConfiguration.from_json(v)
                )(
                    data.get("cachingRuns", None)
                ),
                materialisationRuns=(
                    lambda v: v and EventConfiguration.from_json(v)
                )(
                    data.get("materialisationRuns", None)
                ),
                version=WebhookVersionId.from_json(data["version"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing Webhook",
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
            "url": str(self.url),
            "mergeRequests": (lambda v: v and v.to_json())(self.mergeRequests),
            "mergeRequestComments": (lambda v: v and v.to_json())(self.mergeRequestComments),
            "commits": (lambda v: v and v.to_json())(self.commits),
            "featureStoreRuns": (lambda v: v and v.to_json())(self.featureStoreRuns),
            "monitoringRuns": (lambda v: v and v.to_json())(self.monitoringRuns),
            "cachingRuns": (lambda v: v and v.to_json())(self.cachingRuns),
            "materialisationRuns": (lambda v: v and v.to_json())(self.materialisationRuns),
            "version": self.version.to_json()
        }


@dataclasses.dataclass(frozen=True)
class WebhookCreationRequest:
    """Request to create or update a webhook.
    
    Args:
        name (WebhookName): A data field.
        description (str): A data field.
        url (str): A data field.
        mergeRequests (typing.Optional[EventConfiguration]): A data field.
        mergeRequestComments (typing.Optional[EventConfiguration]): A data field.
        commits (typing.Optional[EventConfiguration]): A data field.
        featureStoreRuns (typing.Optional[EventConfiguration]): A data field.
        monitoringRuns (typing.Optional[EventConfiguration]): A data field.
        cachingRuns (typing.Optional[EventConfiguration]): A data field.
        materialisationRuns (typing.Optional[EventConfiguration]): A data field.
    """
    
    name: WebhookName
    description: str
    url: str
    mergeRequests: typing.Optional[EventConfiguration]
    mergeRequestComments: typing.Optional[EventConfiguration]
    commits: typing.Optional[EventConfiguration]
    featureStoreRuns: typing.Optional[EventConfiguration]
    monitoringRuns: typing.Optional[EventConfiguration]
    cachingRuns: typing.Optional[EventConfiguration]
    materialisationRuns: typing.Optional[EventConfiguration]
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for WebhookCreationRequest data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "name": WebhookName.json_schema(),
                "description": {
                    "type": "string"
                },
                "url": {
                    "type": "string"
                },
                "mergeRequests": {
                    "oneOf": [
                        {"type": "null"},
                        EventConfiguration.json_schema(),
                    ]
                },
                "mergeRequestComments": {
                    "oneOf": [
                        {"type": "null"},
                        EventConfiguration.json_schema(),
                    ]
                },
                "commits": {
                    "oneOf": [
                        {"type": "null"},
                        EventConfiguration.json_schema(),
                    ]
                },
                "featureStoreRuns": {
                    "oneOf": [
                        {"type": "null"},
                        EventConfiguration.json_schema(),
                    ]
                },
                "monitoringRuns": {
                    "oneOf": [
                        {"type": "null"},
                        EventConfiguration.json_schema(),
                    ]
                },
                "cachingRuns": {
                    "oneOf": [
                        {"type": "null"},
                        EventConfiguration.json_schema(),
                    ]
                },
                "materialisationRuns": {
                    "oneOf": [
                        {"type": "null"},
                        EventConfiguration.json_schema(),
                    ]
                }
            },
            "required": [
                "name",
                "description",
                "url",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> WebhookCreationRequest:
        """Validate and parse JSON data into an instance of WebhookCreationRequest.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of WebhookCreationRequest.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return WebhookCreationRequest(
                name=WebhookName.from_json(data["name"]),
                description=str(data["description"]),
                url=str(data["url"]),
                mergeRequests=(
                    lambda v: v and EventConfiguration.from_json(v)
                )(
                    data.get("mergeRequests", None)
                ),
                mergeRequestComments=(
                    lambda v: v and EventConfiguration.from_json(v)
                )(
                    data.get("mergeRequestComments", None)
                ),
                commits=(
                    lambda v: v and EventConfiguration.from_json(v)
                )(
                    data.get("commits", None)
                ),
                featureStoreRuns=(
                    lambda v: v and EventConfiguration.from_json(v)
                )(
                    data.get("featureStoreRuns", None)
                ),
                monitoringRuns=(
                    lambda v: v and EventConfiguration.from_json(v)
                )(
                    data.get("monitoringRuns", None)
                ),
                cachingRuns=(
                    lambda v: v and EventConfiguration.from_json(v)
                )(
                    data.get("cachingRuns", None)
                ),
                materialisationRuns=(
                    lambda v: v and EventConfiguration.from_json(v)
                )(
                    data.get("materialisationRuns", None)
                ),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing WebhookCreationRequest",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "name": self.name.to_json(),
            "description": str(self.description),
            "url": str(self.url),
            "mergeRequests": (lambda v: v and v.to_json())(self.mergeRequests),
            "mergeRequestComments": (lambda v: v and v.to_json())(self.mergeRequestComments),
            "commits": (lambda v: v and v.to_json())(self.commits),
            "featureStoreRuns": (lambda v: v and v.to_json())(self.featureStoreRuns),
            "monitoringRuns": (lambda v: v and v.to_json())(self.monitoringRuns),
            "cachingRuns": (lambda v: v and v.to_json())(self.cachingRuns),
            "materialisationRuns": (lambda v: v and v.to_json())(self.materialisationRuns)
        }


@dataclasses.dataclass(frozen=True)
class WebhookLog:
    """Webhook delivery attempt log record.
    
    Args:
        id (int): A data field.
        hook (WebhookId): A data field.
        payload (str): A data field.
        url (str): A data field.
        responseCode (int): A data field.
        responseBody (str): A data field.
        delivered (datetime.datetime): A data field.
    """
    
    id: int
    hook: WebhookId
    payload: str
    url: str
    responseCode: int
    responseBody: str
    delivered: datetime.datetime
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for WebhookLog data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer"
                },
                "hook": WebhookId.json_schema(),
                "payload": {
                    "type": "string"
                },
                "url": {
                    "type": "string"
                },
                "responseCode": {
                    "type": "integer"
                },
                "responseBody": {
                    "type": "string"
                },
                "delivered": {
                    "type": "string",
                    "format": "date-time"
                }
            },
            "required": [
                "id",
                "hook",
                "payload",
                "url",
                "responseCode",
                "responseBody",
                "delivered",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> WebhookLog:
        """Validate and parse JSON data into an instance of WebhookLog.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of WebhookLog.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return WebhookLog(
                id=int(data["id"]),
                hook=WebhookId.from_json(data["hook"]),
                payload=str(data["payload"]),
                url=str(data["url"]),
                responseCode=int(data["responseCode"]),
                responseBody=str(data["responseBody"]),
                delivered=isodate.parse_datetime(data["delivered"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing WebhookLog",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "id": self.id,
            "hook": self.hook.to_json(),
            "payload": str(self.payload),
            "url": str(self.url),
            "responseCode": int(self.responseCode),
            "responseBody": str(self.responseBody),
            "delivered": self.delivered.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        }


@dataclasses.dataclass(frozen=True)
class WebhookMessage:
    """A message to be send to a webhook.
    
    Args:
        id (int): A data field.
        hook (WebhookId): A data field.
        payload (str): A data field.
        created (datetime.datetime): A data field.
        backoff (int): A data field.
    """
    
    id: int
    hook: WebhookId
    payload: str
    created: datetime.datetime
    backoff: int
    
    @classmethod
    def json_schema(cls) -> dict:
        """Return the JSON schema for WebhookMessage data.
        
        Returns:
            A Python dictionary describing the JSON schema.
        """
        return {
            "type": "object",
            "properties": {
                "id": {
                    "type": "integer"
                },
                "hook": WebhookId.json_schema(),
                "payload": {
                    "type": "string"
                },
                "created": {
                    "type": "string",
                    "format": "date-time"
                },
                "backoff": {
                    "type": "integer"
                }
            },
            "required": [
                "id",
                "hook",
                "payload",
                "created",
                "backoff",
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> WebhookMessage:
        """Validate and parse JSON data into an instance of WebhookMessage.
        
        Args:
            data (dict): JSON data to validate and parse.
        
        Returns:
            An instance of WebhookMessage.
        
        Raises:
            ValidationError: When schema validation fails.
            KeyError: When a required field is missing from the JSON.
        """
        try:
            jsonschema.validate(data, cls.json_schema())
            return WebhookMessage(
                id=int(data["id"]),
                hook=WebhookId.from_json(data["hook"]),
                payload=str(data["payload"]),
                created=isodate.parse_datetime(data["created"]),
                backoff=int(data["backoff"]),
            )
        except jsonschema.exceptions.ValidationError as ex:
            logging.debug(
                "Invalid JSON data received while parsing WebhookMessage",
                exc_info=ex
            )
            raise
    
    def to_json(self) -> dict:
        """Serialise this instance as JSON.
        
        Returns:
            Data ready to serialise as JSON.
        """
        return {
            "id": self.id,
            "hook": self.hook.to_json(),
            "payload": str(self.payload),
            "created": self.created.strftime('%Y-%m-%dT%H:%M:%S.%f%z'),
            "backoff": int(self.backoff)
        }

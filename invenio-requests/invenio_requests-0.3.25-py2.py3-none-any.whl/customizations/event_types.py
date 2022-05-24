# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Requests is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base class for creating custom event types of requests."""

import inspect

import marshmallow as ma
from marshmallow import RAISE, fields, validate
from marshmallow_utils import fields as utils_fields

from ..proxies import current_requests


class EventType:
    """Base class for event types."""

    type_id = None
    """The unique and constant identifier for this type of event."""

    payload_schema = None
    """Schema for supported payload fields.

    Define it as a dictionary of fields mapping or callable that returns a dictionary:

    .. code-block:: python

        payload_schema = {
            "content": fields.String(),
            # ...
        }

        # or a callable
        def payload_schema():
            return {
                "content": fields.String(),
                # ...
            }
    """

    payload_required = False
    """Require the event payload."""

    def __init__(self, payload=None):
        """Constructor."""
        self.payload = payload or {}

    def __eq__(self, other):
        """Implement comparison test."""
        if inspect.isclass(other):
            # if a class was passed rather than an instance, try to instantiate it
            other = other()
        if isinstance(other, EventType):
            return self.type_id == other.type_id
        elif isinstance(other, str):
            return self.type_id == other
        raise Exception("unknown value")

    def __str__(self):
        """Return str(self)."""
        # Value used by marshmallow schemas to represent the type.
        return self.type_id

    def __repr__(self):
        """Return repr(self)."""
        return f"<RequestEventType '{self.type_id}'>"

    @classmethod
    def _create_marshmallow_schema(cls):
        """Create a marshmallow schema for this request type."""
        # Avoid circular imports
        from invenio_requests.services.schemas import RequestEventSchema

        additional_fields = {}

        # Raise on invalid payload keys
        class PayloadBaseSchema(ma.Schema):
            class Meta:
                unknown = RAISE

        # If a payload schema is defined, add it to the request schema
        if cls.payload_schema is not None:
            payload_schema = cls.payload_schema
            if callable(cls.payload_schema):
                payload_schema = payload_schema()

            payload_required = False
            if cls.payload_required is not None:
                payload_required = cls.payload_required
            additional_fields["payload"] = ma.fields.Nested(
                PayloadBaseSchema.from_dict(payload_schema),
                required=payload_required
            )

        # Dynamically create a schema from the fields defined
        # by the payload schema dict.
        return RequestEventSchema.from_dict(additional_fields)

    @classmethod
    def marshmallow_schema(cls):
        """Create a schema for the entire request including payload."""
        type_id = cls.type_id
        if type_id not in current_requests._events_schema_cache:
            current_requests._events_schema_cache[type_id] = \
                cls._create_marshmallow_schema()
        return current_requests._events_schema_cache[type_id]


class LogEventType(EventType):
    """Log event type."""

    type_id = "L"

    def payload_schema():
        """Return payload schema as a dictionary."""
        # we need to import here because of circular imports
        from invenio_requests.records.api import RequestEventFormat
        return dict(
            event=fields.String(validate=validate.Length(min=1)),
            content=utils_fields.SanitizedHTML(
                validate=validate.Length(min=1)
            ),
            format=fields.Str(
                validate=validate.OneOf(choices=[e.value for e in RequestEventFormat]),
                load_default=RequestEventFormat.HTML.value,
            )
        )


class CommentEventType(EventType):
    """Comment event type."""

    type_id = "C"

    def payload_schema():
        """Return payload schema as a dictionary."""
        # we need to import here because of circular imports
        from invenio_requests.records.api import RequestEventFormat
        return dict(
            content=utils_fields.SanitizedHTML(
                required=True, validate=validate.Length(min=1)
            ),
            format=fields.Str(
                validate=validate.OneOf(choices=[e.value for e in RequestEventFormat]),
                load_default=RequestEventFormat.HTML.value,
            )
        )

    payload_required = True

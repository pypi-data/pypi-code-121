# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2021 - 2022 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Request Event Schemas."""

from datetime import timezone

from invenio_records_resources.services.records.schema import BaseRecordSchema
from marshmallow import (
    INCLUDE,
    RAISE,
    Schema,
    ValidationError,
    fields,
    post_dump,
    post_load,
    validate,
)
from marshmallow_utils import fields as utils_fields

from invenio_requests.proxies import current_requests

from ..customizations.event_types import CommentEventType, EventType
from ..proxies import current_event_type_registry


class RequestSchema(BaseRecordSchema):
    """Schema for requests.

    Note that the payload schema and the entity reference schemas (i.e. creator,
    receiver, and topic) are dynamically constructed and injected into this schema.
    """

    # load and dump
    type = fields.String()
    title = utils_fields.SanitizedUnicode(default="")
    description = utils_fields.SanitizedUnicode()

    # Dump-only
    number = fields.String(dump_only=True)
    status = fields.String(dump_only=True)
    is_closed = fields.Boolean(dump_only=True)
    is_open = fields.Boolean(dump_only=True)
    expires_at = utils_fields.TZDateTime(
        timezone=timezone.utc, format="iso", dump_only=True
    )
    is_expired = fields.Boolean(dump_only=True)

    class Meta:
        """Schema meta."""

        unknown = RAISE


class GenericRequestSchema(RequestSchema):
    """Generic request schema.

    CAUTION: This schema should not be used for the final validation of input
    data. Use the request type's own defined schema instead.

    This schema can be used in situations where you need to do basic validation
    or dumping of a request without the payload.

    This is used e.g. in Invenio-RDM-Records for dumping a request without
    having to know the specific request type.
    """

    created_by = fields.Dict()
    receiver = fields.Dict()
    topic = fields.Dict()


class EventTypeMarshmallowField(fields.Str):
    """Serializes event type from `EventType` to string."""

    def _serialize(self, value, attr, data, **kwargs):
        if isinstance(value, EventType):
            value = value.type_id
        return value


class RequestEventSchema(BaseRecordSchema):
    """Base Event schema that other schemas should inherit from."""

    type = EventTypeMarshmallowField(dump_only=True)
    created_by = fields.Dict(dump_only=True)
    permissions = fields.Method("get_permissions", dump_only=True)

    def get_permissions(self, obj):
        """Return permissions to act on comments or empty dict."""
        is_comment = obj.type == CommentEventType
        if is_comment:
            service = current_requests.request_events_service
            return {
                "can_update_comment": service.check_permission(
                    self.context['identity'], "update_comment", event=obj
                ),
                "can_delete_comment": service.check_permission(
                    self.context['identity'], "delete_comment", event=obj
                ),
            }
        else:
            return {}

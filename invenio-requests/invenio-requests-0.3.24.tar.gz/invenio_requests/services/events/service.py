# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
# Copyright (C) 2021-2022 Northwestern University.
# Copyright (C) 2021-2022 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""RequestEvents Service."""

from elasticsearch_dsl import Q
from flask_babelex import _
from invenio_access.permissions import system_process
from invenio_records_resources.services import RecordService, ServiceSchemaWrapper
from invenio_records_resources.services.base.links import LinksTemplate
from invenio_records_resources.services.uow import (
    RecordCommitOp,
    RecordDeleteOp,
    unit_of_work,
)

from invenio_requests.customizations import CommentEventType
from invenio_requests.customizations.event_types import LogEventType
from invenio_requests.records.api import RequestEventFormat
from invenio_requests.services.results import EntityResolverExpandableField


class RequestEventsService(RecordService):
    """Request Events service."""

    def _wrap_schema(self, schema):
        """Wrap schema."""
        return ServiceSchemaWrapper(self, schema)

    @property
    def expandable_fields(self):
        """Get expandable fields."""
        return [
            EntityResolverExpandableField("created_by")
        ]

    @unit_of_work()
    def create(self, identity, request_id, data, event_type, uow=None,
               expand=False):
        """Create a request event.

        :param request_id: Identifier of the request (data-layer id).
        :param identity: Identity of user creating the event.
        :param dict data: Input data according to the data schema.
        """
        request = self._get_request(request_id)
        # If you can read the request you can create events for the request.
        self.require_permission(identity, "read", request=request)

        # Validate data (if there are errors, .load() raises)
        schema = self._wrap_schema(event_type.marshmallow_schema())

        data, errors = schema.load(
            data,
            context={"identity": identity},
        )

        event = self.record_cls.create(
            {},
            request=request.model,
            request_id=str(request_id),
            type=event_type,
        )
        event.update(data)
        event.created_by = self._get_creator(identity)
        # Persist record (DB and index)
        uow.register(RecordCommitOp(event, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            event,
            schema=schema,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    def read(self, identity, id_, expand=False):
        """Retrieve a record."""
        event = self._get_event(id_)
        request = self._get_request(event.request_id)

        self.require_permission(identity, "read", request=request)

        return self.result_item(
            self,
            identity,
            event,
            schema=self._wrap_schema(event.type.marshmallow_schema()),
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def update(self, identity, id_, data, revision_id=None, uow=None,
               expand=False):
        """Update a comment (only comments can be updated)."""
        event = self._get_event(id_)
        request = self._get_request(event.request.id)
        self.require_permission(
            identity, "update_comment", request=request, event=event)
        self.check_revision_id(event, revision_id)

        if event.type != CommentEventType:
            raise PermissionError("You cannot update this event.")

        schema = self._wrap_schema(event.type.marshmallow_schema())
        data, _ = schema.load(
            data,
            context=dict(
                identity=identity,
                record=event,
                event_type=event.type
            ),
        )
        event['payload']['content'] = data['payload']['content']
        event['payload']['format'] = data['payload']['format']
        uow.register(RecordCommitOp(event, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            event,
            schema=schema,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def delete(self, identity, id_, revision_id=None, uow=None):
        """Delete a comment (only comments can be deleted)."""
        event = self._get_event(id_)
        request_id = event.request_id
        request = self._get_request(request_id)

        # Permissions
        self.require_permission(
            identity, "delete_comment", request=request, event=event)
        self.check_revision_id(event, revision_id)

        if event.type != CommentEventType:
            raise PermissionError("You cannot delete this event.")

        # soft delete the comment
        uow.register(RecordDeleteOp(event, self.indexer))

        # create a new event for the deleted comment
        data = dict(
            payload=dict(
                event="comment_deleted",
                content=_("deleted a comment"),
                format=RequestEventFormat.HTML.value,
            )
        )

        self.create(identity, request_id, data, LogEventType, uow=uow)
        return True

    def search(self, identity, request_id, params=None, es_preference=None,
               **kwargs):
        """Search for events for a given request matching the querystring."""
        params = params or {}
        params.setdefault("sort", "oldest")

        expand = kwargs.pop("expand", False)

        # Permissions - guarded by the request's can_read.
        request = self._get_request(request_id)
        self.require_permission(identity, "read", request=request)

        # Prepare and execute the search
        search = self._search(
            "search",
            identity,
            params,
            es_preference,
            permission_action="unused",
            extra_filter=Q("term", request_id=str(request_id)),
            **kwargs,
        )
        search_result = search.execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(
                self.config.links_search,
                context={"request_id": request_id, "args": params},
            ),
            links_item_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    # Utilities
    @property
    def request_cls(self):
        """Get associated request class."""
        return self.config.request_cls

    def _get_request(self, request_id):
        """Get associated request."""
        return self.request_cls.get_record(request_id)

    def _get_event(self, event_id, with_deleted=True):
        """Get associated event_id."""
        return self.record_cls.get_record(event_id, with_deleted=with_deleted)

    def _get_creator(self, identity):
        """Get the creator dict from the identity."""
        if system_process in identity.provides:
            return None  # TODO: Change this for some agreed value
        else:
            return {"user": str(identity.id)}

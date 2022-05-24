# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2021 - 2022 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Requests service."""

from elasticsearch_dsl.query import Bool, Q
from invenio_records_resources.services import RecordService, ServiceSchemaWrapper
from invenio_records_resources.services.base import LinksTemplate
from invenio_records_resources.services.uow import (
    IndexRefreshOp,
    RecordCommitOp,
    RecordDeleteOp,
    unit_of_work,
)

from ...customizations import RequestActions
from ...customizations.event_types import CommentEventType
from ...errors import CannotExecuteActionError
from ...proxies import current_events_service, current_request_type_registry
from ...resolvers.registry import ResolverRegistry
from ..results import EntityResolverExpandableField
from .links import RequestLinksTemplate


class RequestsService(RecordService):
    """Requests service."""

    @property
    def links_item_tpl(self):
        """Item links template."""
        return RequestLinksTemplate(
            self.config.links_item,
            self.config.action_link,
            context={
                'permission_policy_cls': self.config.permission_policy_cls,
            }
        )

    @property
    def request_type_registry(self):
        """Request_type_registry."""
        return current_request_type_registry

    def _wrap_schema(self, schema):
        """Wrap schema."""
        return ServiceSchemaWrapper(self, schema)

    @property
    def expandable_fields(self):
        """Get expandable fields."""
        return [
            EntityResolverExpandableField("created_by"),
            EntityResolverExpandableField("receiver"),
        ]

    @unit_of_work()
    def create(
        self, identity, data, request_type, receiver, creator=None, topic=None,
        expires_at=None, uow=None, expand=False
    ):
        """Create a record."""
        self.require_permission(identity, "create")

        # we're not using "self.schema" b/c the schema may differ per
        # request type!
        schema = self._wrap_schema(request_type.marshmallow_schema())
        data, errors = schema.load(
            data,
            context={"identity": identity},
            raise_errors=False,
        )

        # most of the data is initialized via the components
        request = self.record_cls.create(
            {},
            type=request_type,
            expires_at=expires_at,
        )

        creator = (
            ResolverRegistry.reference_entity(creator, raise_=True)
            if creator is not None
            else ResolverRegistry.reference_identity(identity)
        )
        if topic is not None:
            topic = ResolverRegistry.reference_entity(topic, raise_=True)
        if receiver is not None:
            receiver = ResolverRegistry.reference_entity(receiver, raise_=True)

        # Run components
        self.run_components(
            "create",
            identity,
            data=data,
            record=request,
            errors=errors,
            created_by=creator,
            topic=topic,
            receiver=receiver,
            uow=uow,
        )

        # Get and run the request type's create action.
        self._execute(identity, request, request_type.create_action, uow)

        # persist record (DB and index)
        uow.register(RecordCommitOp(request, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            request,
            schema=schema,
            links_tpl=self.links_item_tpl,
            errors=errors,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    def read(self, identity, id_, expand=False):
        """Retrieve a request."""
        # resolve and require permission
        request = self.record_cls.get_record(id_)
        self.require_permission(identity, f"read", request=request)

        # run components
        for component in self.components:
            if hasattr(component, "read"):
                component.read(identity, record=request)

        return self.result_item(
            self,
            identity,
            request,
            schema=self._wrap_schema(request.type.marshmallow_schema()),
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def update(self, identity, id_, data, revision_id=None, uow=None,
               expand=False):
        """Update a request."""
        request = self.record_cls.get_record(id_)

        self.check_revision_id(request, revision_id)

        self.require_permission(identity, f"update", request=request)

        # we're not using "self.schema" b/c the schema may differ per
        # request type!
        schema = self._wrap_schema(request.type.marshmallow_schema())
        data, _ = schema.load(
            data,
            context={
                "identity": identity,
                "record": request,
            },
        )

        # run components
        self.run_components("update", identity, data=data, record=request,
                            uow=uow)

        uow.register(RecordCommitOp(request, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            request,
            schema=schema,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    @unit_of_work()
    def delete(self, identity, id_, uow=None):
        """Delete a request from database and search indexes."""
        request = self.record_cls.get_record(id_)

        # TODO do we need revisions for requests?
        # self.check_revision_id(request, revision_id)

        # check permissions
        self.require_permission(identity, f"delete", request=request)

        # run components
        self.run_components("delete", identity, record=request, uow=uow)

        # Get and run the request type's create action.
        self._execute(identity, request, request.type.delete_action, uow)

        uow.register(RecordDeleteOp(request, indexer=self.indexer))

        return True

    def _execute(self, identity, request, action, uow):
        """Internal method to execute a given named action."""
        action_obj = RequestActions.get_action(request, action)

        if not action_obj.can_execute():
            raise CannotExecuteActionError(action)

        action_obj.execute(identity, uow)

    @unit_of_work()
    def execute_action(self, identity, id_, action, data=None, uow=None,
                       expand=False):
        """Execute the given action for the request, if possible.

        For instance, it would be not possible to execute the specified
        action on the request, if the latter has the wrong status.
        """
        # Retrieve request and action
        request = self.record_cls.get_record(id_)
        action_obj = RequestActions.get_action(request, action)

        # Check permissions - example of permission: can_cancel_submitted
        permission_name = f"action_{action}"
        self.require_permission(identity, permission_name, request=request)

        # Check if the action *can* be executed (i.e. a given state transition
        # is allowed).
        if not action_obj.can_execute():
            raise CannotExecuteActionError(action)

        # Execute action and register request for persistence.
        action_obj.execute(identity, uow)
        uow.register(RecordCommitOp(request, indexer=self.indexer))

        # Assuming that data is just for comment payload
        if data:
            _data = dict(
                payload=data.get("payload", {}),
            )
            current_events_service.create(identity, request.id, _data, CommentEventType,
                                          uow=uow)

        # make events immediately available in search
        uow.register(IndexRefreshOp(indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            request,
            schema=self._wrap_schema(request.type.marshmallow_schema()),
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    def search_user_requests(
            self, identity, params=None, es_preference=None, expand=False, **kwargs):
        """Search for requests matching the querystring and belong to user.

        The user is able to search the requests that were created by them
        or they are the receiver.
        """
        self.require_permission(identity, 'search_user_requests')

        # Prepare and execute the search
        params = params or {}
        search_result = self._search(
            'search',
            identity,
            params,
            es_preference,
            permission_action=None,
            extra_filter=Bool("should", should=[
                Q("term", **{"created_by.user": identity.id}),
                Q("term", **{"receiver.user": identity.id}),
            ]),
            **kwargs
        ).execute()

        return self.result_list(
            self,
            identity,
            search_result,
            params,
            links_tpl=LinksTemplate(
                self.config.links_user_requests_search, context={"args": params}),
            links_item_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Requests service configuration."""

from invenio_records_resources.services import RecordServiceConfig, SearchOptions
from invenio_records_resources.services.records.links import pagination_links

from invenio_requests.services.requests import facets

from ...customizations import RequestActions
from ...records.api import Request
from ..configurator import ConfiguratorMixin, FromConfig
from ..permissions import PermissionPolicy
from .components import (
    EntityReferencesComponent,
    RequestDataComponent,
    RequestNumberComponent,
)
from .links import RequestLink
from .params import IsOpenParam, ReferenceFilterParam
from .results import RequestItem, RequestList


def _is_action_available(request, context):
    """Check if the given action is available on the request."""
    action = context.get("action")
    identity = context.get("identity")
    permission_policy_cls = context.get('permission_policy_cls')
    permission = permission_policy_cls(f"action_{action}", request=request)
    return RequestActions.can_execute(request, action) and \
        permission.allows(identity)


class RequestSearchOptions(SearchOptions):
    """Search options."""

    params_interpreters_cls = SearchOptions.params_interpreters_cls + [
        ReferenceFilterParam.factory(param="created_by", field="created_by"),
        ReferenceFilterParam.factory(param="receiver", field="receiver"),
        ReferenceFilterParam.factory(param="topic", field="topic"),
        IsOpenParam.factory("is_open"),
    ]

    facets = {
        'type': facets.type,
        'status': facets.status,
    }


class RequestsServiceConfig(RecordServiceConfig, ConfiguratorMixin):
    """Requests service configuration."""

    # common configuration
    permission_policy_cls = FromConfig(
        "REQUESTS_PERMISSION_POLICY", default=PermissionPolicy
    )
    result_item_cls = RequestItem
    result_list_cls = RequestList
    search = RequestSearchOptions

    # request-specific configuration
    record_cls = Request  # needed for model queries
    schema = None  # stored in the API classes, for customization
    index_dumper = None

    # links configuration
    links_item = {
        "self": RequestLink("{+api}/requests/{id}"),
        "comments": RequestLink("{+api}/requests/{id}/comments"),
        "timeline": RequestLink("{+api}/requests/{id}/timeline"),
    }
    links_search = pagination_links("{+api}/requests{?args*}")
    links_user_requests_search = pagination_links("{+api}/user/requests{?args*}")
    action_link = RequestLink(
        "{+api}/requests/{id}/actions/{action}", when=_is_action_available
    )

    components = [
        # Order of components are important!
        RequestDataComponent,
        EntityReferencesComponent,
        RequestNumberComponent,
    ]

# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 - 2022 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for generic and customizable requests."""

from invenio_users_resources.resolvers import UserResolver

from invenio_requests.services.requests import facets

from .customizations import CommentEventType, LogEventType
from .services.permissions import PermissionPolicy

REQUESTS_PERMISSION_POLICY = PermissionPolicy
"""Override the default requests/comments permission policy."""

REQUESTS_REGISTERED_TYPES = []
"""Configuration for registered Request Types."""

REQUESTS_REGISTERED_EVENT_TYPES = [
    LogEventType(),
    CommentEventType(),
]
"""Configuration for registered Request Event Types."""

REQUESTS_ENTITY_RESOLVERS = [
    UserResolver(),
]
"""Registered resolvers for resolving/creating references in request metadata."""

REQUESTS_ROUTES = {
    'details': '/requests/<pid_value>',
}
"""Invenio requests ui endpoints."""

REQUESTS_FACETS = {
    'type': {
        'facet': facets.type,
        'ui': {
            'field': 'type',
        }
    },
    'status': {
        'facet': facets.status,
        'ui': {
            'field': 'status',
        }
    },
}
"""Invenio requests facets."""

REQUESTS_TIMELINE_PAGE_SIZE = 15
"""Amount of items per page on the request details timeline"""

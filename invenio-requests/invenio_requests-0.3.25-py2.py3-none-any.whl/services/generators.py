# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Request permissions."""

import operator
from functools import reduce
from itertools import chain

from elasticsearch_dsl import Q
from invenio_records_permissions.generators import Generator
from invenio_records_resources.references import EntityGrant


class Status(Generator):
    """Generator to validate needs only for a given request status."""

    def __init__(self, statuses, generators):
        """Initialize need entity generator."""
        self._statuses = statuses
        self._generators = generators or []

    def needs(self, request=None, **kwargs):
        """Needs if status is in one of the provided ones."""
        if request.status in self._statuses:
            needs = [
                g.needs(request=request, **kwargs) for g in self._generators
            ]
            return set(chain.from_iterable(needs))
        return []

    def query_filter(self, **kwargs):
        """Query filters for the current identity."""
        queries = [g.query_filter(**kwargs) for g in self._generators]
        queries = [q for q in queries if q]
        queries = reduce(operator.or_, queries) if queries else None

        if queries:
            return Q("terms", **{"status": self._statuses}) & queries
        return None


class EntityNeedsGenerator(Generator):
    """Allows the creator of the request."""

    entity_field = None
    grants_field = 'grants'

    def __init__(self):
        """Initialize need entity generator."""
        assert self.entity_field is not None, "Subclass must define entity_field."

    def needs(self, request=None, **kwargs):
        """Needs for the given entity reference."""
        entity = getattr(request, self.entity_field)
        return request.type.entity_needs(entity)

    def query_filter(self, identity=None, **kwargs):
        """Query filters for the current identity."""
        grants = []
        for need in identity.provides:
            grants.append(EntityGrant(self.entity_field, need).token)
        if grants:
            return Q("terms", **{self.grants_field: grants})
        return None


class Creator(EntityNeedsGenerator):
    """Allows the creator of the request."""

    entity_field = 'created_by'


class Receiver(EntityNeedsGenerator):
    """Allows the receiver of the request."""

    entity_field = 'receiver'


class Commenter(Generator):
    """The user who created a specific comment."""

    def needs(self, event=None, request=None, **kwargs):
        """Enabling Needs."""
        if event.created_by is not None:
            return event.created_by.get_needs()
        return []

    def query_filter(self, identity=None, **kwargs):
        """Filters for current identity as creator."""
        raise RuntimeError('The generator cannot be used for searching.')

# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dumps entity grant tokens into the indexed request record."""


from invenio_records.dumpers import ElasticsearchDumperExt
from invenio_records_resources.references import EntityGrant


class GrantTokensDumperExt(ElasticsearchDumperExt):
    """Grant tokens dumper.

    Responsible for serializing the required needs for accessing a request
    into the indexed request record.
    """

    grants_field = 'grants'

    def __init__(self, *fields):
        """Constructor."""
        super().__init__()
        self.fields = fields

    def dump(self, request, data):
        """Dump grant tokens for entity fields into indexed request."""
        grants = []
        for field_name in self.fields:
            entity = getattr(request, field_name)
            for need in request.type.entity_needs(entity):
                grants.append(EntityGrant(field_name, need).token)
        data[self.grants_field] = grants

    def load(self, data, request_cls):
        """Load the data."""
        data.pop(self.grants_field)

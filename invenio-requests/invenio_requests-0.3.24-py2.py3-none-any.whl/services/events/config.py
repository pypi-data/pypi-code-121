# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
# Copyright (C) 2021 TU Wien.
#
# Invenio-Requests is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Request Events Service Config."""

from invenio_records_resources.services import (
    Link,
    RecordServiceConfig,
    ServiceSchemaWrapper,
)
from invenio_records_resources.services.records.components import DataComponent
from invenio_records_resources.services.records.links import pagination_links
from invenio_records_resources.services.records.results import RecordItem, RecordList

from ...records.api import Request, RequestEvent
from ..configurator import ConfiguratorMixin, FromConfig
from ..permissions import PermissionPolicy
from ..requests.components import EntityReferencesComponent
from ..schemas import RequestEventSchema


class RequestEventItem(RecordItem):
    """RequestEvent result item."""

    @property
    def id(self):
        """Id property."""
        return self._record.id


class RequestEventList(RecordList):
    """RequestEvent result item."""

    @property
    def hits(self):
        """Iterator over the hits."""
        for hit in self._results:
            # Load dump
            record = self._service.record_cls.loads(hit.to_dict())

            # Project the record
            schema = ServiceSchemaWrapper(
                self._service, record.type.marshmallow_schema())
            projection = schema.dump(
                record,
                context=dict(
                    identity=self._identity,
                    record=record,
                )
            )

            if self._links_item_tpl:
                projection['links'] = self._links_item_tpl.expand(record)

            yield projection


class RequestEventLink(Link):
    """Link variables setter for RequestEvent links."""

    @staticmethod
    def vars(record, vars):
        """Variables for the URI template."""
        vars.update({"id": record.id, "request_id": record.request_id})


class RequestEventsServiceConfig(RecordServiceConfig, ConfiguratorMixin):
    """Config."""

    request_cls = Request
    permission_policy_cls = FromConfig(
        "REQUESTS_PERMISSION_POLICY", default=PermissionPolicy
    )
    schema = RequestEventSchema
    record_cls = RequestEvent
    result_item_cls = RequestEventItem
    result_list_cls = RequestEventList

    # ResultItem configurations
    links_item = {
        "self": RequestEventLink("{+api}/requests/{request_id}/comments/{id}"),
    }
    links_search = pagination_links("{+api}/requests/{request_id}/timeline{?args*}")

# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks for requests."""

from datetime import datetime

from celery import shared_task
from elasticsearch_dsl import Q
from elasticsearch_dsl.query import Bool
from flask import current_app
from invenio_access.permissions import system_identity

from .proxies import current_requests_service


@shared_task
def check_expired_requests():
    """Retrieve expired requests and perform expired action."""
    service = current_requests_service
    now = datetime.utcnow().isoformat()

    # using scan to get all requests
    requests_list = service.scan(
        identity=system_identity,
        extra_filter=Bool(
            "must",
            must=[
                # somehow querying for '"term", **{"is_expired: True"}' will not return any requests # noqa
                Q("range", **{"expires_at": {"lte": now}}),
                Q("term", **{"is_open": True}),
            ],
        ),
    )
    for r in requests_list:
        try:
            service.execute_action(
                identity=system_identity, id_=r["id"], action="expire"
            )
        except Exception as e:
            current_app.logger.warning(e)
            pass

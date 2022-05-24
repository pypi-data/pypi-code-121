# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Request views decorators module."""

from functools import wraps

from flask import g

from invenio_requests.proxies import current_requests


def pass_request(expand=False):
    """Fetch the request record and pass it as kwarg."""
    def decorator(f):
        @wraps(f)
        def view(**kwargs):
            """Decorated view."""
            pid_value = kwargs["request_pid_value"]
            request = current_requests.requests_service.read(
                id_=pid_value, identity=g.identity, expand=expand
            )
            kwargs["request"] = request
            return f(**kwargs)
        return view
    return decorator

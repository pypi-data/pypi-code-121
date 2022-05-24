# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-Requests is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Request views module."""

from .api import create_request_events_bp, create_requests_bp
from .ui import create_ui_blueprint

__all__ = (
    'create_ui_blueprint',
    'create_requests_bp',
    'create_request_events_bp',
)

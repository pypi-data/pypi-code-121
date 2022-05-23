# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Helper proxies."""

from __future__ import absolute_import, print_function

from flask import current_app
from werkzeug.local import LocalProxy

current_cache_ext = LocalProxy(lambda: current_app.extensions["invenio-cache"])
"""Helper proxy to access cache extension object."""


current_cache = LocalProxy(lambda: current_app.extensions["invenio-cache"].cache)
"""Helper proxy to access cache object."""

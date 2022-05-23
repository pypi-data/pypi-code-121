# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Configuration for Invenio-Cache module.

By default the module is configured to use a Redis database 0 on localhost.
The underlying Flask-Caching module however supports many other cahe backends.

For how to configure other cache backends please refer to the `Flask-Caching
<http://pythonhosted.org/Flask-Caching/#configuring-flask-caching>`_
documentation.
"""

CACHE_KEY_PREFIX = "cache::"
"""Cache key prefix."""

#: Sets the cache type.
CACHE_TYPE = "redis"
"""Cache type.

Please refer to Flask-Caching documentation for other cache types.
"""

CACHE_REDIS_URL = "redis://localhost:6379/0"
"""Redis location and database."""


CACHE_IS_AUTHENTICATED_CALLBACK = None
"""Import path to callback.

Callback is executed to determine if request is authenticated.
"""

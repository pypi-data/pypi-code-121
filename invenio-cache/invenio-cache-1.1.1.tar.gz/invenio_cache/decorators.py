# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Decorators to help with caching."""

from __future__ import absolute_import, print_function

from functools import wraps

from .proxies import current_cache, current_cache_ext


def cached_unless_authenticated(timeout=50, key_prefix="default"):
    """Cache anonymous traffic."""

    def caching(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            cache_fun = current_cache.cached(
                timeout=timeout,
                key_prefix=key_prefix,
                unless=lambda: current_cache_ext.is_authenticated_callback(),
            )
            return cache_fun(f)(*args, **kwargs)

        return wrapper

    return caching

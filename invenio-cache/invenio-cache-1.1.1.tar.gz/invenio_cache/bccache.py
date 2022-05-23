# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Jinja bytecode cache for Redis."""

from __future__ import absolute_import, print_function

from jinja2.bccache import MemcachedBytecodeCache

from .proxies import current_cache


class BytecodeCache(MemcachedBytecodeCache):
    """A bytecode cache."""

    def __init__(self, app):
        """Initialize `BytecodeCache`."""
        prefix = "{0}jinja::".format(app.config.get("CACHE_KEY_PREFIX"))
        super(self.__class__, self).__init__(
            current_cache, prefix=prefix, timeout=None, ignore_memcache_errors=True
        )

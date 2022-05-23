# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from __future__ import absolute_import, print_function

from flask import Flask

from invenio_cache import (
    InvenioCache,
    cached_unless_authenticated,
    current_cache,
    current_cache_ext,
)


def test_decorator(base_app, ext):
    """Test cached_unless_authenticated."""
    base_app.config["MYVAR"] = "1"
    ext.is_authenticated_callback = lambda: False

    @base_app.route("/")
    @cached_unless_authenticated()
    def my_cached_view():
        return base_app.config["MYVAR"]

    # Test when unauthenticated
    with base_app.test_client() as c:
        # Generate cache
        assert c.get("/").get_data(as_text=True) == "1"
        base_app.config["MYVAR"] = "2"
        # We are getting a cached version
        assert c.get("/").get_data(as_text=True) == "1"

    # Test for when authenticated
    base_app.config["MYVAR"] = "1"
    ext.is_authenticated_callback = lambda: True

    with base_app.test_client() as c:
        # Generate cache
        assert c.get("/").get_data(as_text=True) == "1"
        base_app.config["MYVAR"] = "2"
        # We are NOT getting a cached version
        assert c.get("/").get_data(as_text=True) == "2"

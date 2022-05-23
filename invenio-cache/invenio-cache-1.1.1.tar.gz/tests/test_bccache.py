# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Bytecode cache tests."""

from __future__ import absolute_import, print_function

from flask import render_template

from invenio_cache import BytecodeCache


def test_bccache(base_app, ext):
    """Test bytecode cache."""
    app = base_app
    app.jinja_options = dict(
        app.jinja_options, cache_size=1000, bytecode_cache=BytecodeCache(app)
    )

    @app.route("/")
    def view():
        return render_template("template.html", msg="test")

    with app.test_client() as c:
        assert c.get("/").get_data(as_text=True) == "test"

# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 Graz University of Technology.
#
# invenio-alma is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from flask import Flask

from invenio_alma import InvenioAlma, __version__


def test_version():
    """Test version import."""
    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask("testapp")
    ext = InvenioAlma(app)
    assert "invenio-alma" in app.extensions

    app = Flask("testapp")
    ext = InvenioAlma()
    assert "invenio-alma" not in app.extensions

    ext.init_app(app)
    assert "invenio-alma" in app.extensions

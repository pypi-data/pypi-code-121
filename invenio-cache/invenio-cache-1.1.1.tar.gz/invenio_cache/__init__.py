# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Cache module for Invenio.

Initialization
--------------

Create a Flask application:

>>> from flask import Flask
>>> app = Flask('myapp')
>>> app.config['CACHE_TYPE'] = 'simple'

Initialize Invenio-Cache:

>>> from invenio_cache import InvenioCache
>>> ext = InvenioCache(app)

Jinja bytecode caching
----------------------
By default Jinja only supports filesystem and memcached backends for bytecode
caching. Invenio-Cache provides another backend, which will use the default
configured cache backend instead (and thus e.g. supports Redis). Bytecode
caching helps reduce template load time especially in a multi-process
environment where workers are recycled from time to time.

For more information about Jinja bytecode caching please see
http://jinja.pocoo.org/docs/2.9/api/#bytecode-cache

Enabling the bytecode cache is as simple as:

>>> from invenio_cache import BytecodeCache
>>> app.jinja_options = dict(
...     app.jinja_options,
...     cache_size=1000,
...     bytecode_cache=BytecodeCache(app)
... )

Programmatic API
----------------
The programmatic cache API is very simple. First get your cache instance:

>>> cache = ext.cache

If you are in an Flask application context you can also use a handy proxy:

>>> app.app_context().push()
>>> from invenio_cache import current_cache

Now, simply set, get and delete cache values:

>>> current_cache.set('mykey', 'myvalue')
True
>>> current_cache.get('mykey')
'myvalue'
>>> current_cache.delete('mykey')
True

Further documentation
---------------------
`Flask-Caching
<http://pythonhosted.org/Flask-Caching/#configuring-flask-caching>`_ has a good
and extensive API documentation so please refer to that for other APIs such
as cache decorators for view, memoization of functions, Jinja snippet caching.
"""

from __future__ import absolute_import, print_function

from .bccache import BytecodeCache
from .decorators import cached_unless_authenticated
from .ext import InvenioCache
from .proxies import current_cache, current_cache_ext

__version__ = "1.1.1"

__all__ = (
    "__version__",
    "cached_unless_authenticated",
    "current_cache_ext",
    "current_cache",
    "BytecodeCache",
    "InvenioCache",
)

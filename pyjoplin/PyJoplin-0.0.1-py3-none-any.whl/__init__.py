# -*- coding: utf-8 -*-

"""
PyJoplin
~~~~~~~~~~~~

Basic usage:

import PyJoplin

token='xxxxxxxxxxxx'
jop=JoplinHttpProxy(token)

notes=jop.get_pages_with('notes')
"""

from PyJoplin.helpers.http_helper import JoplinHttpProxy


__all__ = (
    'JoplinHttpProxy'
)

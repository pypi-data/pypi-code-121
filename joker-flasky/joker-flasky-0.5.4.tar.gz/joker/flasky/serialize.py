#!/usr/bin/env python3
# coding: utf-8

"""
Deprecated. This module will be removed on ver 0.6.0.
"""

import warnings

from volkanic.utils import indented_json_dumps, indented_json_print

from joker.flasky.viewutils import JSONEncoderPlus, jsonp

_warning = """\
joker.flasky.serialize is deprecated, please consider use
- joker.flasky.viewutils.JSONEncoderPlus
- joker.flasky.viewutils.jsonp
- volkanic.utils.indented_json_dumps
- volkanic.utils.indented_json_print
"""

warnings.warn(
    _warning,
    DeprecationWarning
)

__all__ = []
__deprecated__ = [
    JSONEncoderPlus,
    jsonp,
    indented_json_dumps,
    indented_json_print,
]

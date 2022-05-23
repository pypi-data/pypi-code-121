"""
A subclass of MutableAttr that has defaultdict support.
"""
from collections.abc import Mapping

import six

from attrdict.default import AttrDefault


__all__ = ['AttrStrictKey']


class AttrStrictKey(AttrDefault):
    """
    Restricting add new key.
    """
    def __init__(self, default_factory=None, items=None, sequence_type=tuple, pass_key=False):
        super(AttrDefault, self).__init__(default_factory, items, sequence_type, pass_key)
        
    def __setitem__(self, key, value):
        if key not in self:
            raise KeyError("{} is not a legal key of this StricDict".format(repr(key)))
        super(AttrStrictKey, self).__setitem__(key, value)

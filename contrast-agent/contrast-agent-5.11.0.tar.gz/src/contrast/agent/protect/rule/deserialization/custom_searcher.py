# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
class CustomSearcher(object):
    """
    Base object for Custom Searchers that rules can implement
    """

    IMPACT_NONE = 0
    IMPACT_LOW = 1
    IMPACT_MEDIUM = 2
    IMPACT_HIGH = 3
    IMPACT_CRITICAL = 4

    def __init__(self, searcher_id):
        self._searcher_id = searcher_id

    @property
    def searcher_id(self):
        return self._searcher_id

    def impact_of(self, value):
        return NotImplementedError

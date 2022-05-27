# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
class AdjustedSpan(object):
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop

    def length(self):
        return self.stop - self.start

    def __eq__(self, other):
        if not isinstance(other, AdjustedSpan):
            return False
        return self.start == other.start and self.stop == other.stop

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.start}, {self.stop})>"

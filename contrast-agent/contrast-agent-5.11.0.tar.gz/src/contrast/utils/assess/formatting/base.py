# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from abc import ABCMeta, abstractmethod

from contrast.agent.assess.adjusted_span import AdjustedSpan


class StringToken(object):
    def __init__(self, value, offset):
        self.value = value
        self.offset = offset
        self.len = len(value)

    @property
    def span(self):
        return AdjustedSpan(self.offset, self.offset + self.len)

    def __len__(self):
        return self.len

    def __repr__(self):
        reprstr = "<{}({}, {})>"
        clsname = self.__class__.__name__
        return reprstr.format(clsname, repr(self.value), self.offset)


class FormatToken(object):
    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def span(self):
        pass

    @abstractmethod
    def format(self, args, kwargs):
        pass

    @abstractmethod
    def get_arg(self, args, kwargs):
        pass

    @abstractmethod
    def __len__(self):
        pass

# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import re

from contrast.agent import scope
from contrast.agent.assess.adjusted_span import AdjustedSpan
from .base import StringToken, FormatToken as BaseFormatToken


# This regex was built from the following description:
# https://docs.python.org/3/library/stdtypes.html#printf-style-string-formatting
from contrast.utils.string_utils import ensure_string, ensure_binary

FORMAT_REGEX_STRING = r"""
    %                           # required for all format strings
    (?:\(([^\d\W]\w*)\))?       # optional mapping key (identifer name)
    ([#0\- +])?                 # optional conversion flags
    ([1-9]+[0-9]?|\*)?          # optional minimum field width
    (?:\.([0-9]+|\*))?          # optional precision
    ([hlL])?                    # optional length modifier (ignored)
    ([diouxXeEfFgGcrsa%])       # conversion type (required)
    """

UNICODE_REGEX_FLAGS = re.X | re.UNICODE
FORMAT_REGEX = re.compile(FORMAT_REGEX_STRING, UNICODE_REGEX_FLAGS)
# For matching bytes and bytearray objects
FORMAT_REGEX_BYTES = re.compile(FORMAT_REGEX_STRING.encode(), re.X)


class BaseCFormatToken(BaseFormatToken):
    def __init__(self, match, index):
        self.start, self.end = match.span()
        (
            self.mapping,
            self.conversion,
            self.width,
            self.precision,
            _,
            self.type,
        ) = match.groups()
        self.match = match

        # From the Python documentation: if either the width or the precision
        # is specified as an '*' (asterisk), the actual width or precision is
        # read from the next element of the argument tuple, and the value to
        # convert comes after the width and/or precision.
        if self.width == self.wildcard:
            index += 1
        if self.precision == self.wildcard:
            index += 1

        self.index = index

    def _convert_int(self, val):
        return self.encode(str(int(val))) if val else self.empty

    def _build_width_and_precision(self, args):

        if self.width == self.wildcard and self.precision == self.wildcard:
            width, precision = args[self.index - 2 : self.index]
        elif self.width == self.wildcard:
            width, precision = args[self.index - 1], self.precision
        elif self.precision == self.wildcard:
            width, precision = self.width, args[self.index - 1]
        else:
            width, precision = self.width, self.precision

        width = self._convert_int(width)
        precision = self.dot + self._convert_int(precision) if precision else self.empty

        return self.formatter % (width, precision)

    def format(self, args, kwargs):
        string = self.get_arg(args, kwargs)

        fmt = self.percent
        if self.conversion:
            fmt += self.conversion
        fmt += self._build_width_and_precision(args)
        fmt += self.type

        return string, fmt % (string,)

    def get_arg(self, args, kwargs):
        if self.type == self.percent:
            return self.percent
        if self.mapping:
            return args[0][self.mapping]
        return args[self.index]

    @property
    def next_index(self):
        # This ensures that we handle indexing properly in cases where there
        # are escape sequences in the string that is being tokenized.
        # We don't increment the index in these cases since the token doesn't
        # correspond to any of the input arguments to be formatted.
        return self.index if self.type == self.percent else self.index + 1

    @property
    def span(self):
        return AdjustedSpan(self.start, self.end)

    def __len__(self):
        return self.end - self.start

    def __repr__(self):
        reprstr = "<{}({})>"
        clsname = self.__class__.__name__
        return reprstr.format(clsname, self.match)


def _build_token_class(name, encoder):
    cls = type(name, (BaseCFormatToken,), {})

    consts = dict(wildcard="*", empty="", dot=".", percent="%", formatter="%s%s")
    for name, val in consts.items():
        setattr(cls, name, encoder(val))

    def encode(self, val):
        return encoder(val)

    setattr(cls, "encode", encode)

    return cls


StrFormatToken = _build_token_class("StrFormatToken", ensure_string)
BytesFormatToken = _build_token_class("BytesFormatToken", ensure_binary)


def tokenize_format(format_string):

    tokens = []
    token_index = 0

    is_string = isinstance(format_string, str)
    token_cls = StrFormatToken if is_string else BytesFormatToken

    regex = FORMAT_REGEX if is_string else FORMAT_REGEX_BYTES

    start_index = 0
    with scope.contrast_scope():
        # contrast scope required here to prevent analysis in finditer patch.
        for match in regex.finditer(format_string):
            start, end = match.span()
            if start_index != start:
                string = format_string[start_index:start]
                tokens.append(StringToken(string, start_index))

            fmt_token = token_cls(match, token_index)
            tokens.append(fmt_token)

            start_index = end
            token_index = fmt_token.next_index

    if start_index < len(format_string):
        string = format_string[start_index:]
        tokens.append(StringToken(string, start_index))

    return tokens

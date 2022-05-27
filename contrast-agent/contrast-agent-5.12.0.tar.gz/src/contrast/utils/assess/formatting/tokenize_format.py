# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from string import Formatter

from contrast.agent import scope
from contrast.agent.assess.adjusted_span import AdjustedSpan
from .base import StringToken, FormatToken as BaseFormatToken


class FormatToken(BaseFormatToken):
    def __init__(self, name, spec, conversion, offset, size, formatter):
        self.name = name
        self.spec = spec
        self.conversion = conversion
        self.offset = offset
        self.len = size
        self.formatter = formatter

    def format(self, args, kwargs):
        value = self.get_arg(args, kwargs)

        fmt = "{"
        if self.conversion:
            fmt += "!" + self.conversion
        if self.spec:
            fmt += ":" + self.spec
        fmt += "}"

        return value, fmt.format(value)

    def get_arg(self, args, kwargs):
        """
        Returns the value associated with this format token

        We need to convert the object if it is not actually a string type in order to
        determine whether/how to propagate. Unfortunately we only see the original
        object at the time the propagator is called, and so we're required to do the
        conversion manually. There is a small risk here if the __str__ or __repr__
        methods of the object are not idempotent for some reason, but that seems like
        a fairly extreme edge case.
        """
        field, _ = self.formatter.get_field(self.name, args, kwargs)
        if not isinstance(field, str) and not self.spec:
            # The default conversion behavior is to do nothing if no conversion is
            # given, but we need the default to be to call field.__str__, since that's
            # what format does by default. We pop out of scope in order to enable any
            # string conversion operations to propagate tags back to the field.
            with scope.pop_contrast_scope():
                return self.formatter.convert_field(field, self.conversion or "s")
        return field

    @property
    def span(self):
        return AdjustedSpan(self.offset, self.offset + self.len)

    def __len__(self):
        return self.len

    def __repr__(self):
        reprstr = "<{}({}, {}, {}, {}, len={})>"
        clsname = self.__class__.__name__
        return reprstr.format(
            clsname,
            repr(self.name),
            repr(self.spec),
            repr(self.conversion),
            self.offset,
            self.len,
        )


def tokenize_format(format_string):
    formatter = Formatter()

    tokens = []

    index = 0
    format_index = 0
    string = format_string

    nodes = list(formatter.parse(format_string))
    for (literal, name, spec, conversion) in nodes:

        # Handle case of '{{' or '}}'
        if literal and literal[-1] in ["{", "}"]:
            literal += literal[-1]

        offset = string.find(literal)
        string = string[offset:]

        if tokens and isinstance(tokens[-1], FormatToken):
            # Handle case of '{}}}'
            if literal and literal[-1] == "}":
                offset += 1
                string = string[1:]
            tokens[-1].len = offset

        index += offset

        if literal != "":
            tokens.append(StringToken(literal, index))
            index += len(literal)
            string = string[len(literal) :]

        if (name, spec, conversion) != (None, None, None):
            # Handle the case of adjacent format strings
            if tokens and isinstance(tokens[-1], FormatToken):
                # Find the offset immediately after the end of the last format
                offset = string.find("}") + 1
                tokens[-1].len = offset
                string = string[offset:]
                index += offset

            if not name:
                name = str(format_index)
                format_index += 1

            current_token = FormatToken(
                name, spec, conversion, index, offset, formatter
            )

            tokens.append(current_token)

    if isinstance(tokens[-1], FormatToken):
        current_token.len = len(format_string) - index

    return tokens

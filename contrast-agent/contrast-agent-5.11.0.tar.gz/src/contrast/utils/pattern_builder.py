# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import re


class PatternBuilder(object):
    QUOTE_PATTERN = "('|\")"
    MATCHED_PARENS = r"\(.*\)"
    STRING_CONCATENATE = (
        r'(\'|")(?:\s*)(?:\/\*.*\*\/)?(?:\s*)\+(?:\s*)(?:\/\*.*\*\/)?(?:\s*)(\'|")'
    )
    BLOCK_COMMENTS_AND_SPACES = r"(?:\s*)(?:\/\*.*\*\/)?(?:\s*)"
    JAVASCRIPT_IDENTIFIER = r"(?:[^\d({-][\w]*)"
    ESCAPE_REGEX = re.compile(r"([\[\]^()+*{}|?.-])")

    def __init__(self):
        self.pattern = []

    def build(self):
        # multiline = make anchors look for newline
        # dotall = make dot ('.') match newline
        return re.compile(
            "".join(self.pattern),
            flags=re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL,
        )

    def quote(self):
        self.pattern.append(PatternBuilder.QUOTE_PATTERN)

        return self

    def some_or_no_block_comments_and_spaces(self):
        self.pattern.append(PatternBuilder.BLOCK_COMMENTS_AND_SPACES)

        return self

    def javascript_variable_identifiers(self):
        self.pattern.append(PatternBuilder.JAVASCRIPT_IDENTIFIER)

        return self

    def literally(self, string):
        self.pattern.append(self.escape(string))

        return self

    def anything(self):
        self.pattern.append(r".*")

        return self

    def any_of_these(self, string_list, escape=True, minimum=1, maximum=1):
        if not string_list or len(string_list) == 0:
            return self

        self.pattern.append("(")

        self.add_string_literals_to(
            string_list, "|", lambda x: self.escape(x) if escape else x
        )

        if minimum == maximum and minimum == 1:
            self.pattern.append(")")
        else:
            self.pattern.append("){" + str(minimum) + "," + str(maximum) + "}")

        return self

    def letters_at_least(self, length):
        self.pattern.append("[A-Za-z]{" + str(length) + ",}")

        return self

    def escape(self, string):
        # This also works; have not determined which is better
        # re.escape(string)

        return re.sub(PatternBuilder.ESCAPE_REGEX, lambda x: "\\" + x.group(0), string)

    def add_string_literals_to(self, source, separator, block):
        if not source:
            return

        self.pattern.append(block(source[0]))

        for string in source[1:]:
            if separator:
                self.pattern.append(separator)

            self.pattern.append(block(string))

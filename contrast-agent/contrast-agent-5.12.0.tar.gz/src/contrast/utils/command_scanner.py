# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import os
import re

from contrast.utils.string_utils import index_of_any


class ParseResults(object):
    def __init__(self, args, command_chains):
        self.args = args
        self.command_chains = command_chains


class CommandScanner(object):
    """
    Taken from Java Agent and Apache Commons
    """

    SINGLE_QUOTE = "'"
    DOUBLE_QUOTE = '"'

    CHAIN = ["&", ";", "|", ">", "<", "\n"]

    def __init__(self, executable):
        self.arguments = []
        self.command_chains = []
        self.executable = executable.replace("/", os.sep).replace("\\", os.sep)

    @staticmethod
    def parse(command):
        if not command:
            return None

        results = CommandScanner.translate_command_line(command)

        if results is None:
            return None

        try:
            command_scanner = CommandScanner(results.args[0])
        except Exception:
            return results

        for item in results.args[1:]:
            command_scanner.add_argument(item)

        command_scanner.command_chains = results.command_chains

        return results

    def add_argument(self, argument):
        if not argument:
            return

        self.arguments.append(self.quote_argument(argument))

    def quote_argument(self, argument):

        cleaned_argument = argument.strip()

        while cleaned_argument.startswith(
            self.SINGLE_QUOTE
        ) or cleaned_argument.startswith(self.DOUBLE_QUOTE):
            cleaned_argument = cleaned_argument[1:]

        while cleaned_argument.endswith(self.SINGLE_QUOTE) or cleaned_argument.endswith(
            self.DOUBLE_QUOTE
        ):
            cleaned_argument = cleaned_argument[:-1]

        if self.DOUBLE_QUOTE in cleaned_argument:
            if self.SINGLE_QUOTE in cleaned_argument:
                raise TypeError(
                    "Cannot handle single and double quotes in same argument"
                )

            result = ""
            result += self.SINGLE_QUOTE
            result += cleaned_argument
            result += self.SINGLE_QUOTE
            return result

        if " " in cleaned_argument:
            result = ""
            result += self.DOUBLE_QUOTE
            result += cleaned_argument
            result += self.DOUBLE_QUOTE
            return result

        return cleaned_argument

    @staticmethod
    def translate_command_line(command):
        normal = 0
        in_quote = 1
        in_double_quote = 2

        state = normal

        tokenized = re.split("([\"' ])", command)

        vectors = []
        chained_indices = []

        current = ""

        last_token_has_been_quoted = False

        index = 0

        for token in tokenized:
            index += len(token)

            if state == in_quote:
                if CommandScanner.SINGLE_QUOTE == token:
                    last_token_has_been_quoted = True
                    state = normal
                else:
                    current += token
            elif state == in_double_quote:
                if CommandScanner.DOUBLE_QUOTE == token:
                    last_token_has_been_quoted = True
                    state = normal
                else:
                    current += token
            else:
                if CommandScanner.SINGLE_QUOTE == token:
                    state = in_quote
                elif CommandScanner.DOUBLE_QUOTE == token:
                    state = in_double_quote
                elif token == " ":

                    if last_token_has_been_quoted or len(current) > -1:
                        vectors.append(current)
                        current = ""
                elif "#" in token:
                    break
                else:
                    current += token
                    chain_index = index_of_any(token, CommandScanner.CHAIN)

                    if chain_index != -1:
                        chained_indices.append(index - len(token) + chain_index)

                last_token_has_been_quoted = False

        if last_token_has_been_quoted or len(current) > -1:
            vectors.append(current)

        if state in (in_quote, in_double_quote):
            raise TypeError("Unbalanced quotes")

        return ParseResults(list(vectors), chained_indices)

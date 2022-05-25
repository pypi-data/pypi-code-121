#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Text Matcher Class """


class TextMatcher(object):
    """ Text Matcher Class """

    @staticmethod
    def exists(value: str,
               input_text: str,
               case_sensitive: bool = False) -> bool:
        """ Check for the existence of a value in input text

        Args:
            value (str): any value string
            input_text (str): any text string to search in
            case_sensitive (bool): True if case sensitivity matters

        Returns:
            bool: True if the value exists in the input text
        """

        if not case_sensitive:
            value = value.lower()
            input_text = input_text.lower()

        if value == input_text:
            return True

        match_lr = f" {value} "
        if match_lr in input_text:
            return True

        match_l = f" {value}"
        if input_text.endswith(match_l):
            return True

        match_r = f"{value} "
        if input_text.startswith(match_r):
            return True

        return False

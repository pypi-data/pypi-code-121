#!/usr/bin/env python3


class EmptyStackError(Exception):
    """Exception raised when trying to get a value from an empty stack"""
    pass


class LangError(Exception):
    """Exception raised when a problem is found while parsing a lang file"""
    def __init__(self, l_no, msg, file):
        super().__init__(f"File \"{file}\", line {l_no + 1} - {msg}")


class LangEncodingError(Exception):
    """Exception raised when parsing a lang file in the wrong encoding"""
    pass


class NoLabelError(Exception):
    """Exception raised when an InputLabel is initalized without a label"""
    pass

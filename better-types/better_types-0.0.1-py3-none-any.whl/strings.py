"""
Some reusable strings helpers
"""
import json
import random
import re

# Compile regexps once to avoid performance hit on each call
RE_SPLIT_CAMEL = re.compile(r"[A-Z][^A-Z]*")


def shuffle(string: str) -> str:
    """
    Shuffle all the characters of a given string
    """
    chars = list(string)
    random.shuffle(chars)
    return "".join(chars)


def is_json(string: str) -> bool:
    """
    Check wether the string is a valid JSON or not.
    """
    try:
        json.loads(string)
    except ValueError:
        return False
    return True


def camel_to_caps(string: str) -> str:
    """
    Transform a CamelCase string into an ALL_CAPS one

    >>> camel_to_caps("SomeCamelCase")
    'SOME_CAMEL_CASE'
    """
    return "_".join(RE_SPLIT_CAMEL.findall(string)).upper()


def camel_to_snake(string: str) -> str:
    """
    Transform a CamelCase string into a snake_case one

    >>> camel_to_snake("SomeCamelCase")
    'some_camel_case'
    """
    return "_".join(RE_SPLIT_CAMEL.findall(string)).lower()


def caps_to_camel(string: str) -> str:
    """
    Transform an ALL_CAPS string into a CamelCase one

    >>> caps_to_camel("SOME_CAPS")
    'SomeCaps'
    """
    return "".join(string.replace("_", " ").title().split())

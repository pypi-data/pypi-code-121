#!/usr/bin/env python3

""" Add ACT types """

import functools
import json
import os
import re
from typing import Any, Dict, List, Text

from pkg_resources import resource_filename

DEFAULT_VALIDATOR = r"(.|\n)*"


class TypeLoadError(Exception):
    pass


def etc_file(filename: Text) -> Text:
    "Get content of file from resource/etc"
    return resource_filename(
        "act.types", "etc/{}".format(filename)
    )  # ).decode('utf-8')


@functools.lru_cache(32)
def default_object_types():
    return load_types(etc_file("object-types.json"))


def default_fact_types():
    return load_types(etc_file("fact-types.json"))


def default_meta_fact_types():
    return load_types(etc_file("meta-fact-types.json"))


@functools.lru_cache(32)
def get_object_validator(object_type: Text) -> Text:
    """Get object validator, default to DEFAULT_VALIDATOR)"""

    typedef = [t for t in default_object_types() if t["name"] == object_type]

    if not typedef:
        raise TypeLoadError(f"Type not found: {object_type}")
    if len(typedef) > 1:
        print(typedef)
        raise TypeLoadError(f"Multiple types found for {object_type}")

    return typedef[0].get("validator", DEFAULT_VALIDATOR)


def object_validates(object_type: Text, object_value: Text) -> bool:
    """Validate object using current valdiator"""

    if not isinstance(object_value, Text):
        raise TypeError(
            "Illegal type for argument object_value: "
            f"(object_value={object_value}, object_value (type) = {type(object_value)}, object_type={object_type})"
        )

    if object_value == "*":
        # Fact Chain value -> do not validate
        return True

    validator = get_object_validator(object_type)

    if re.fullmatch(validator, object_value):
        return True

    return False


def load_types(filename: Text) -> List[Dict[Text, Any]]:
    """
    Parse as json, and exit on parse error
    """
    if not os.path.isfile(filename):
        raise TypeLoadError(f"File not found: {filename}")

    try:
        with open(filename, encoding="UTF8") as f:
            types = json.load(f)
    except json.decoder.JSONDecodeError:
        raise TypeLoadError(f"Unable to parse file as json: {filename}")

    if not isinstance(types, list):
        raise TypeLoadError("Types must be a list of dicts")

    return types

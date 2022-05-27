"""Utility classes and functions related to Transformations.

This module contains useful utility classes and functions for working
with Transformations.
"""
from typing import Any, cast

import yaml


class _MarshmallowYamlShim:
    """Shim to allow Marshmallow to load/save to YAML.

    A class to be used as a Marshmallow render_module that allows reading/writing
    schemas directly from/to YAML.
    """

    @staticmethod
    def loads(s: str) -> Any:
        """Loads the supplied YAML string as an object."""
        return yaml.safe_load(s)

    @staticmethod
    def dumps(obj: Any) -> str:
        """Dumps the supplied object to a yaml string."""
        return cast(str, yaml.dump(obj))

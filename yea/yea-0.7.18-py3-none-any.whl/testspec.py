"""
Utilities for parsing a test specification.
"""

import ast
import pathlib
from typing import Any, Dict, Optional, Union

import yaml


def load_docstring(filepath: Union[str, pathlib.Path]) -> str:
    with open(filepath, encoding="utf8") as fd:
        file_contents = fd.read()
    module = ast.parse(file_contents)
    docstring = ast.get_docstring(module)
    return docstring or ""


def find_yaml_str(s: str) -> Optional[str]:
    """Loads YAML from docstring."""
    split_lines = s.split("\n")

    # Cut YAML from rest of docstring
    for index, line in enumerate(split_lines):
        line = line.strip()
        if line == "---" or line.startswith("--- "):
            # TODO: validate, capture type
            # !<tag:wandb.ai,2021:yea>
            cut_from = index + 1
            yaml_string = "\n".join(split_lines[cut_from:])
            return yaml_string
    return None


def load_yaml_from_docstring(docstring: str) -> Dict[str, Any]:
    found = find_yaml_str(docstring)
    if not found:
        return dict()
    return load_yaml_from_str(found)


def load_yaml_from_str(yaml_string: str) -> Dict[str, Any]:
    try:
        data = dict(yaml.load(yaml_string, Loader=yaml.SafeLoader))
    except yaml.scanner.ScannerError:
        print("WARNING: Unable to parse yaml")
        data = {}
    return data


def load_yaml_from_file(filepath: Union[str, pathlib.Path]) -> Dict[str, Any]:
    file_contents = ""
    with open(filepath, encoding="utf8") as fd:
        file_contents = fd.read()
    found = find_yaml_str(file_contents)
    found = found or file_contents
    return load_yaml_from_str(found)

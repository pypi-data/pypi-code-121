"""
:mod:`xpipe.config` is a package implementing main classes needed to load the yaml tree file and load objects from it.
"""

from .config import load_config, load_config_from_str, to_yaml, to_dict, merge

__all__ = [
    "load_config", 
    "load_config_from_str", 
    "to_dict", 
    "to_yaml",
    "merge", 

    "objects",
    "variables",
    "tags"
]

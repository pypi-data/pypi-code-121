"""mfire.settings module

This module manages the processing of constants and templates

"""
from mfire.settings.algorithms import TEXT_ALGO, PREFIX_TO_VAR
from mfire.settings.constants import (
    RULES_DIR,
    RULES_NAMES,
    TEMPLATES_FILENAMES,
    LOCAL,
    UNITS_TABLES,
    SETTINGS_DIR,
)
from mfire.settings.logger import get_logger
from mfire.settings.settings import Settings

__all__ = [
    "Settings",
    "get_logger",
    "TEXT_ALGO",
    "RULES_DIR",
    "RULES_NAMES",
    "TEMPLATES_FILENAMES",
    "PREFIX_TO_VAR",
    "LOCAL",
    "UNITS_TABLES",
    "SETTINGS_DIR",
]

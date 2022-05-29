# -*- coding: utf-8 -*-
"""Control parameters for using forcefields
"""

import importlib
import logging
import os
import pkg_resources
import seamm

logger = logging.getLogger(__name__)


# Get the list of available forcefields
path = pkg_resources.resource_filename(__name__, "data/")

# Check if we can use OpenKIM
if importlib.util.find_spec("kim_query") is None:
    forcefields = []
else:
    forcefields = ["OpenKIM"]

logger.debug("Looking for forcefields at " + path)
with os.scandir(path) as it:
    for entry in it:
        if not entry.name.startswith(".") and entry.is_file():
            logger.debug("   " + entry.name)
            ffname, ext = os.path.splitext(entry.name)
            if ext == ".frc":
                forcefields.append(entry.name)

forcefields = sorted(forcefields)


class ForcefieldParameters(seamm.Parameters):
    """The control parameters for forcefields"""

    parameters = {
        "task": {
            "default": "setup forcefield",
            "kind": "enumeration",
            "default_units": "",
            "enumeration": (
                "setup forcefield",
                "assign forcefield to structure",
            ),
            "format_string": "s",
            "description": "What to do:",
            "help_text": "What to do with the forcefield.",
        },
        "forcefield_file": {
            "default": forcefields[0],
            "kind": "enumeration",
            "default_units": "",
            "enumeration": tuple(forcefields),
            "format_string": "s",
            "description": "Forcefield Repository:",
            "help_text": "The forcefield repository or file to use.",
        },
        "forcefield": {
            "default": "default",
            "kind": "enumeration",
            "default_units": "",
            "enumeration": ("default",),
            "format_string": "s",
            "description": "Forcefield:",
            "help_text": "The forcefield with the file.",
        },
        "elements": {
            "default": "",
            "kind": "periodic table",
            "default_units": None,
            "enumeration": None,
            "format_string": "",
            "description": "Elements:",
            "help_text": "The elements to include.",
        },
        "potentials": {
            "default": "",
            "kind": "enumeration",
            "default_units": "",
            "enumeration": ("will be replaced",),
            "format_string": "s",
            "description": "Interatomic Potentials:",
            "help_text": "The interatomic potentials to use.",
        },
    }

    def __init__(self, defaults={}, data=None):
        """Initialize the instance, by default from the default
        parameters given in the class"""

        super().__init__(
            defaults={**ForcefieldParameters.parameters, **defaults}, data=data
        )

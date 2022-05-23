# -*- coding: utf-8 -*-
"""
Control parameters for the Write Structure step in a SEAMM flowchart
"""

import logging

from . import formats
import seamm

logger = logging.getLogger(__name__)


_filetypes = sorted(formats.registries.REGISTERED_WRITERS.keys())


class WriteStructureParameters(seamm.Parameters):
    """The control parameters for Write Structure

    This is a dictionary of Parameters objects, which themselves are
    dictionaries.  You need to replace the 'time' example below with one or
    more definitions of the control parameters for your plugin and application.

    The fields of each Parameter are:

        default: the default value of the parameter, used to reset it
        kind: one of 'integer', 'float', 'string', 'boolean' or 'enum'
        default_units: the default units, used for reseting the value
        enumeration: a tuple of enumerated values. See below for more.
        format_string: a format string for 'pretty' output
        description: a short string used as a prompt in the GUI
        help_text: a longer string to display as help for the user

    While the 'kind' of a variable might be a numeric value, it may still have
    enumerated values, such as 'normal', 'precise', etc. In addition, any
    parameter can be set to a variable of expression, indicated by having '$'
    as the first character in the field.
    """

    parameters = {
        "file": {
            "default": "",
            "kind": "string",
            "default_units": "",
            "enumeration": tuple(),
            "format_string": "s",
            "description": "File:",
            "help_text": ("The file to write."),
        },
        "file type": {
            "default": "from extension",
            "kind": "enum",
            "default_units": "",
            "enumeration": ("from extension", *_filetypes),
            "format_string": "s",
            "description": "Type of file:",
            "help_text": ("The type of file, overrides the extension"),
        },
        "remove hydrogens": {
            "default": "no",
            "kind": "enum",
            "default_units": "",
            "enumeration": ("no", "nonpolar", "all"),
            "format_string": "s",
            "description": "Remove hydrogens:",
            "help_text": (
                "Whether to remove hydrogen atoms before writing, and if so, just the "
                "nonpolar ones or all."
            ),
        },
        "structures": {
            "default": "current configuration",
            "kind": "string",
            "default_units": "",
            "enumeration": (
                "current configuration",
                "all configurations of current system",
                "all systems",
            ),
            "format_string": "s",
            "description": "Structures to write:",
            "help_text": ("The set of structures to write"),
        },
    }

    def __init__(self, defaults={}, data=None):
        """
        Initialize the parameters, by default with the parameters defined above

        Args:
            defaults: A dictionary of parameters to initialize. The parameters
                above are used first and any given will override/add to them.
            data: A dictionary of keys and a subdictionary with value and units
                for updating the current, default values.
        """

        logger.debug("WriteStructureParameters.__init__")

        super().__init__(
            defaults={
                **WriteStructureParameters.parameters,
                **defaults,
            },
            data=data,
        )

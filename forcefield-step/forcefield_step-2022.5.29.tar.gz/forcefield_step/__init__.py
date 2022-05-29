# -*- coding: utf-8 -*-

"""
forcefield_step
A step for choosing the default forcefield.
"""

# Bring up the classes so that they appear to be directly in
# the package.

from forcefield_step.forcefield import Forcefield  # noqa: F401
from forcefield_step.forcefield_parameters import (  # noqa: F401
    ForcefieldParameters,
)
from forcefield_step.forcefield_step import ForcefieldStep  # noqa: F401
from forcefield_step.tk_forcefield import TkForcefield  # noqa: F401

# Handle versioneer
from ._version import get_versions

__author__ = """Paul Saxe"""
__email__ = "psaxe@molssi.org"
versions = get_versions()
__version__ = versions["version"]
__git_revision__ = versions["full-revisionid"]
del get_versions, versions

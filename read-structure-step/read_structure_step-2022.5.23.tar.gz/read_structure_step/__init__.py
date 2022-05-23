# -*- coding: utf-8 -*-

"""
read_structure_step
A SEAMM plugin to read common formats in computational chemistry
"""

# Bring up the classes so that they appear to be directly in
# the read_structure_step package.

from read_structure_step.read_structure import ReadStructure  # noqa: F401
from read_structure_step.read_structure_parameters import (  # noqa: F401
    ReadStructureParameters,
)
from read_structure_step.read_structure_step import ReadStructureStep  # noqa: F401
from read_structure_step.tk_read_structure import TkReadStructure  # noqa: F401
from .read import read  # noqa: F401

from read_structure_step.write_structure import WriteStructure  # noqa: F401
from read_structure_step.write_structure_parameters import (  # noqa: F401
    WriteStructureParameters,
)
from read_structure_step.write_structure_step import WriteStructureStep  # noqa: F401
from read_structure_step.tk_write_structure import TkWriteStructure  # noqa: F401
from .write import write  # noqa: F401

# Handle versioneer
from ._version import get_versions

__author__ = """Eliseo Marin-R-Rimoldi"""
__email__ = "meliseo@vt.edu"
versions = get_versions()
__version__ = versions["version"]
__git_revision__ = versions["full-revisionid"]
del get_versions, versions

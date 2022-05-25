# Author: Snow Yang
# Date  : 2022/03/28

"""Public exceptions exposed by the package."""

from mdev.lib.exceptions import ToolsError


class MxosProjectError(ToolsError):
    """Base exception for mxos-project."""


class VersionControlError(MxosProjectError):
    """Raised when a source control management operation failed."""


class ExistingProgram(MxosProjectError):
    """Raised when a program already exists at a given path."""


class ProgramNotFound(MxosProjectError):
    """Raised when an expected program is not found."""


class MxosOSNotFound(MxosProjectError):
    """A valid copy of MxosOS was not found."""

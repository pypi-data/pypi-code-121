"""Proxy to get data from resmoke."""
from __future__ import annotations

import os
import sys

import structlog

LOGGER = structlog.get_logger(__name__)


class ResmokeProxy:
    """A proxy for interacting with resmoke."""

    def __init__(self) -> None:
        """Initialize the service."""
        self.multiversion_constants = None

    def _lazy_load(self) -> None:
        """Import multiversionconstants from resmoke."""
        if self.multiversion_constants is None:
            if not os.path.isfile(
                os.path.join(os.getcwd(), "buildscripts", "resmokelib", "multiversionconstants.py")
            ):
                LOGGER.error("This command should be run from the root of the mongo repo.")
                LOGGER.error(
                    "If you're running it from the root of the mongo repo and still seeing"
                    " this error, please reach out in #server-testing slack channel."
                )
                raise ImportError()
            sys.path.append(os.path.join(os.getcwd(), "buildscripts", "resmokelib"))
            try:
                import multiversionconstants as _multiversionconstants
            except ImportError:
                LOGGER.error("Could not import `multiversionconstants`.")
                LOGGER.error(
                    "If you're running this command from the root of the mongo repo,"
                    " please reach out in #server-testing slack channel."
                )
                raise
            self.multiversion_constants = _multiversionconstants

    def get_multiversion_constants(self):
        """Get the multiversion constants from resmoke."""
        self._lazy_load()
        return self.multiversion_constants

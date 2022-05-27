"""Proxy to get data from resmoke."""
from __future__ import annotations

import subprocess
from typing import List, Optional

import structlog
import yaml
from pydantic import BaseModel

LOGGER = structlog.get_logger(__name__)


class MultiversionConfig(BaseModel):
    """
    Multiversion Configuration obtained from resmoke.

    * last_lts_fcv: Version of the last LTS release.
    * last_continuous_fcv: Version of the last continuous release.
    """

    last_lts_fcv: str
    last_continuous_fcv: str


class ResmokeProxy:
    """A proxy for interacting with resmoke."""

    def __init__(self, resmoke_cmd: List[str]) -> None:
        """
        Initialize the service.

        :param resmoke_cmd: Command to invoke resmoke.py.
        """
        self.resmoke_cmd = resmoke_cmd
        self.multiversion_constants: Optional[MultiversionConfig] = None

    @classmethod
    def with_cmd(cls, resmoke_cmd: str) -> ResmokeProxy:
        """
        Create an instance of ResmokeProxy that invokes the given command.

        :param resmoke_cmd: Command to invoke resmoke.
        :return: Instance of ResmokeProxy using the given command.
        """
        return cls([part.strip() for part in resmoke_cmd.split(" ")])

    def _lazy_load(self) -> None:
        """Import multiversionconstants from resmoke."""
        if self.multiversion_constants is None:
            cmd = self.resmoke_cmd
            cmd.append("multiversion-config")
            try:
                result = subprocess.run(cmd, capture_output=True, check=True)
            except subprocess.CalledProcessError:
                LOGGER.error("Error invoking resmoke", exc_info=True)
                LOGGER.error(
                    "This command should be run from the root of the mongo repo and the resmoke "
                    "virtualenv should be activated."
                )
                LOGGER.error(
                    "If you're running it from the root of the mongo repo and still seeing"
                    " this error, please reach out in #server-testing slack channel."
                )
                raise
            self.multiversion_constants = MultiversionConfig(**yaml.safe_load(result.stdout))

    def get_multiversion_constants(self) -> MultiversionConfig:
        """Get the multiversion constants from resmoke."""
        self._lazy_load()
        assert self.multiversion_constants
        return self.multiversion_constants

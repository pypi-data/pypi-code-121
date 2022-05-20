"""A service for working with platforms."""
from typing import Optional

import inject

from db_contrib_tool.clients.platform_details import PlatformDetailsClient
from db_contrib_tool.config import SETUP_REPRO_ENV_CONFIG_FILE


class PlatformService:
    """A service for working with platforms."""

    @inject.autoparams()
    def __init__(self, platform_details_client: PlatformDetailsClient) -> None:
        """
        Initialize the service.

        :param platform_details_client: Client for getting platform details.
        """
        self.platform_details_client = platform_details_client

    def infer_platform(self, edition: Optional[str] = None, version: Optional[str] = None) -> str:
        """
        Determine which platform should be downloaded based on the system being run on.

        :param edition: Mongo edition that should be targeted.
        :param version: Mongo version that should be targeted.
        :return: Platform to target.
        """
        system_name = self.platform_details_client.get_platform_system()
        platform_name = None

        if system_name == "Darwin":
            platform_name = "osx"

        elif system_name == "Windows":
            platform_name = "windows"
            if edition == "base" and version == "4.2":
                platform_name += "_x86_64-2012plus"

        elif system_name == "Linux":
            id_name = self.platform_details_client.get_distro_id()
            if id_name in ("ubuntu", "rhel"):
                platform_name = (
                    id_name
                    + self.platform_details_client.get_distro_major_version()
                    + self.platform_details_client.get_distro_minor_version()
                )

        if platform_name is None:
            raise ValueError(
                "Platform cannot be inferred. Please specify platform explicitly with -p. "
                f"Available platforms can be found in {SETUP_REPRO_ENV_CONFIG_FILE}."
            )
        else:
            return platform_name

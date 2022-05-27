"""A client to proxy platform details."""

import platform

import distro


class PlatformDetailsClient:
    """A client to get details about the platform being run on."""

    def get_platform_system(self) -> str:
        """Get the system that is being run on."""
        return platform.system()

    def get_distro_id(self) -> str:
        """Get the id of the distro being run on."""
        return distro.id()

    def get_distro_major_version(self) -> str:
        """Get the major version of the distro being run on."""
        return distro.major_version()

    def get_distro_minor_version(self) -> str:
        """Get the minor version of the distro being run on."""
        return distro.minor_version()

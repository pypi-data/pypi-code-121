"""InstalledPackage is an installation of a software package in a particular location on a particular host."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class InstalledPackage:
    """InstalledPackage is an installation of a software package in a particular location on a particular host.
    """

    location: Optional[str] = None
    version: Optional[str] = None

    def __str__(self):
        """Debug string representation.

        Use the `omniversion.pretty_print` module for prettier output more suitable for human consumption."""
        version = '?' if self.version is None else self.version
        location = '?' if self.location is None else self.location
        return f"version `{version}` in location `{location}`"

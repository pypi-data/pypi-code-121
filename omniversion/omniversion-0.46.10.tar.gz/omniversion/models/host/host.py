"""A remote server, container or local host from which package data can be fetched."""
from dataclasses import dataclass
from typing import List, Union

from omniversion.models.package_metadata.package_metadata import PackageMetadata
from omniversion.models.package_metadata.list.packages_metadata_list import PackagesMetadataList


@dataclass
class Host:
    """A remote server, container or local host from which package data can be fetched."""
    name: str
    """The name of the host, e.g. an ssh host or `localhost`. This should be unique."""
    packages: PackagesMetadataList
    """The package data fetched from this host."""

    @classmethod
    def list_from_packages(cls, packages: Union[PackagesMetadataList, List[PackageMetadata]]) -> List['Host']:
        """Create a list of hosts from a list of packages.

        Parameters
        ----------
        packages
            A `PackagesMetadataList` or a list of `PackageMetadata` items that should be grouped by their `host` \
            property.

        Returns
        -------
        List[Host]
            A list of `Host` objects, each containing only the packages belonging to this host.
        """
        hostnames = sorted(list({package.host for package in packages}))
        return [Host(hostname, PackagesMetadataList([package for package in packages if package.host == hostname]))
                for hostname in hostnames]

    def __str__(self):
        return f"host: {self.name}"

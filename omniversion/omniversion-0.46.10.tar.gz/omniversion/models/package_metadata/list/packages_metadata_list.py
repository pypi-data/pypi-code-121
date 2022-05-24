"""A list of package metadata items, each describing all that is known about a particular software package."""
from collections import UserList
from typing import Optional, Union, List

from ..package_metadata import PackageMetadata

from .available_updates import AvailableUpdates
from .versions_match import VersionsMatch
from .vulnerabilities import Vulnerabilities


class PackagesMetadataList(UserList):
    """A list of package metadata items, each describing all that is known about a particular software package.

    This object is offers convenient methods for filtering packages."""

    def filter(
            self,
            verb: Optional[Union[str, List[str]]] = None,
            host: Optional[str] = None,
            package_manager: Optional[str] = None,
            package_name: Optional[Union[str, List[str]]] = None,
    ) -> 'PackagesMetadataList':
        """List all dependencies matching the given criteria.

        Parameters
        ----------
        verb
            If provided, will ensure only packages obtained via this verb/these verbs will be returned. A verb is a \
            package manager command type like `list`, `audit`, `outdated` etc.

        host
            If provided, will ensure only packages extracted from to the specified host(s) will be returned.

        package_manager
            If provided, the identifier of a package manager whose packages should be returned.

        package_name
            If provided, only packages matching this name or list of names will be returned.

        Returns
        -------
        PackagesMetadataList
            A list of matching packages.
        """

        def filter_condition(package: PackageMetadata) -> bool:
            if host is not None and package.host != host:
                return False
            if package_manager is not None and package.package_manager != package_manager:
                return False
            if (isinstance(verb, list) and package.verb not in verb) or (
                    isinstance(verb, str) and verb != package.verb):
                return False
            if package_name is None:
                return True
            return (isinstance(package_name, list) and package.name in package_name) or (
                    package.name == package_name)

        return PackagesMetadataList([item for item in self if filter_condition(item)])

    def audit(
            self,
            host: Optional[str] = None,
            package_manager: Optional[str] = None,
            package_name: Optional[Union[str, List[str]]] = None,
    ) -> Vulnerabilities:
        """Extract security vulnerabilities from the data.

        Parameters
        ----------
        host
            If provided, will ensure only packages extracted from to the specified host(s) will be returned.

        package_manager
            If provided, the identifier of a package manager whose packages should be returned.

        package_name
            If provided, only packages matching this name or list of names will be returned.

        Returns
        -------
        omniversion.models.package_metadata.list.vulnerabilities.Vulnerabilities
            All security issues contained in the input.
        """
        return Vulnerabilities(self.filter("audit", host, package_manager, package_name))

    def list(
            self,
            host: Optional[str] = None,
            package_manager: Optional[str] = None,
            package_name: Optional[Union[str, List[str]]] = None,
    ):
        """Extract installed package metadata items.

        Parameters
        ----------
        host
            If provided, will ensure only packages extracted from to the specified host(s) will be returned.

        package_manager
            If provided, the identifier of a package manager whose packages should be returned.

        package_name
            If provided, only packages matching this name or list of names will be returned.

        Returns
        -------
        PackagesMetadataList
            All package metadata items relating to installed packages contained in the input.
        """
        return PackagesMetadataList(self.filter(["list", "version"], host, package_manager, package_name))

    def outdated(
            self,
            host: Optional[str] = None,
            package_manager: Optional[str] = None,
            package_name: Optional[Union[str, List[str]]] = None,
    ):
        """Extract available updates from the data.

        Parameters
        ----------
        host
            If provided, will ensure only packages extracted from to the specified host(s) will be returned.

        package_manager
            If provided, the identifier of a package manager whose packages should be returned.

        package_name
            If provided, only packages matching this name or list of names will be returned.

        Returns
        -------
        omniversion.models.package_metadata.list.available_updates.AvailableUpdates
            All available updates for the packages contained in the input.
        """
        return AvailableUpdates(self.filter("outdated", host, package_manager, package_name))

    def show(
            self, package_name: Union[str, List[str]], display_name: Optional[str] = None
    ):
        """Extract metadata for a particular package or list of related packages.

        This is especially useful for ensuring consistency of versions installed on different hosts, \
        as well as versions of related packages delivered through different package managers.

        Parameters
        ----------
        package_name
            The name(s) of the package(s) that should be extracted.

        display_name
            An optional value used in human-readable output.

        Returns
        -------
        omniversion.models.package_metadata.list.versions_match.VersionsMatch
            All available metadata for the specified package(s).
        """
        return VersionsMatch(
            self.filter(["list", "version"], package_name=package_name).data,
            package_name,
            display_name,
        )

    def __repr__(self) -> str:
        num_dependencies = len(self)
        return f"{num_dependencies} package{'' if num_dependencies == 1 else 's'}"

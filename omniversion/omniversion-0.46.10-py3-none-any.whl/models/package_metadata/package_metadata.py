"""Contains all available information about a particular software package,
including existing installations, security advisories and all sorts of other metadata.

If multiple versions of the same package need to be tracked
for a single combination of package manager and host,
this should be done using a single PackageMetadata structure.
By contrast, otherwise identical packages made available by different package managers
are considered different, as their metadata and/or content *may* indeed differ.
We also distinguish between package metadata on different hosts,
as installations are different and available versions
will depend on the configured repositories, firewall settings etc.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from .advisory import Advisory
from .dependency_type import DependencyType
from .installed_package import InstalledPackage
from .package_source import PackageSource


@dataclass
class PackageMetadata:  # pylint: disable=too-many-instance-attributes
    """PackageMetadata contains all available information about a particular software package,
including existing installations, security advisories and all sorts of other metadata.

If multiple versions of the same package need to be tracked
for a single combination of package manager and host,
this should be done using a single PackageMetadata structure.

By contrast, otherwise identical packages made available by different package managers
are considered different.
We also distinguish between package metadata on different hosts,
as installations are different and available versions
will depend on the configured repositories, firewall settings etc.
"""

    name: Optional[str] = None
    """The identifier used to install the package."""
    aliases: Optional[List[str]] = field(default_factory=lambda: [])
    """Alternative names by which the package may be known or have been known"""

    package_manager: Optional[str] = None
    """The package manager through which the package can be installed.

    If a package is available through multiple package managers, we should use separate
    PackageMetadata objects to track them.
    """
    host: Optional[str] = None
    verb: Optional[str] = None
    """The name of the machine on which this package has been installed, requested
    or otherwise tracked by a package manager.

    This may be `localhost`, a hostname (with or without schema) or the name of a docker container.
    While the naming is flexible, care should be taken to keep these identifiers unique.
    If a package is installed on multiple hosts, we should use separate
    PackageMetadata objects to track them.
    """
    installations: List[InstalledPackage] = field(default_factory=lambda: [])
    """Metadata on versions of the package installed on the current machine."""

    type: Optional[DependencyType] = None
    """The kind of dependency (`prod`, `dev`, `peer`)"""
    optional: Optional[bool] = None
    """True if the dependency need not be installed, None if unknown"""
    direct: Optional[bool] = None
    """Specifies whether the dependency has been required directly or transitively"""

    current: Optional[str] = None
    """The currently installed version of the package as reported by the package manager.

    E.g. what is reported by `npm ls <package>`, `rvm info` `pip show <package>`.
    """
    default: Optional[str] = None
    """The version the package manager would select by default.

    E.g. the version designated as `default` by `rvm ls`.
    """
    latest: Optional[str] = None
    """The most recent version of the package known to be available."""
    wanted: Optional[str] = None
    """The version of the package that would be installed
    based on the relevant constraints defined for this package manager.

    E.g. this is the highest version matching the range defined in `package.json` for `npm`.
    """
    locked: Optional[str] = None
    """The version specified in the relevant lock file for this package manager.

    E.g. the version defined in `package-lock.json` or `npm-shrinkwrap.json`.
    """
    extraneous: Optional[bool] = None
    """True if the package is not required, but installed.

    Installed optional packages do not count as extraneous."""
    missing: Optional[bool] = None
    """Missing is true if the package is required, but not installed."""

    dependencies: Optional[List[str]] = None
    """Packages directly required by this package at runtime."""
    dev_dependencies: Optional[List[str]] = None
    """Packages directly required by this package during development."""
    peer_dependencies: Optional[List[str]] = None
    """Packages directly required, but not managed by this package.

    E.g. a plugin might add functionality to another package
    which is assumed to be installed independently of the plugin.
    """

    architecture: Optional[str] = None
    """The architecture for which the package was compiled.

    E.g. the architecture field reported by `rvm ls` or `apt list`.
    """
    author: Optional[str] = None
    """The author or list of authors reported by the package manager."""
    description: Optional[str] = None
    """The package description reported by the package manager."""
    homepage: Optional[str] = None
    """The package's homepage reported by the package manager."""
    license: Optional[str] = None
    """A license identifier as reported by the package manager.

    This is not currently standardized across package managers.
    """
    sources: List[PackageSource] = field(default_factory=lambda: [])
    """Sources through which the package is available, as reported by the package manager.

    E.g. the `sources` field in `apt list`.
    """
    advisories: List[Advisory] = field(default_factory=lambda: [])
    """Security notices on known vulnerabilities.

    E.g. the information contained in the output of `npm audit`.
    """

    def __str__(self):
        if self.name is None:
            return "unknown package name"
        version = ""
        if self.current is not None:
            version = f"@{self.current} installed"
        elif self.wanted is not None:
            version = f"@{self.wanted} wanted"
        via = f" via `{self.package_manager}`" if self.package_manager else ""
        return f"package `{self.name}`{version}{via}"

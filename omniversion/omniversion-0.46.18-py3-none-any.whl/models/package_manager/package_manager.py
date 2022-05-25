"""Representation of a package manager. Use this class to obtain all packages managed by a particular package \
manager across all servers and directories."""
from dataclasses import dataclass
from enum import Enum
from typing import List, Union

from omniversion.models.package_metadata.list.packages_metadata_list import PackagesMetadataList
from omniversion.models.package_metadata.package_metadata import PackageMetadata


class PackageManagerIdentifier(Enum):
    """All package managers currently known to omniversion."""

    APT = "apt"
    """[Aptitude](https://salsa.debian.org/apt-team/apt)"""
    FILE = "file"
    """Not an actual package manager. We use this value for package infos extracted from local configuration files."""
    GALAXY = "galaxy"
    """[Ansible Galaxy](https://galaxy.ansible.com)"""
    GO = "go"
    """[go modules](https://go.dev/ref/mod)"""
    BREW = "homebrew"
    """[homebrew](https://brew.sh)"""
    NPM = "npm"
    """[npm](https://www.npmjs.com)"""
    NVM = "nvm"
    """[nvm](https://github.com/nvm-sh/nvm)"""
    PIP = "pip"
    """[pip](https://pypi.org/project/pip/)"""
    RUBYGEMS = "rubygems"
    """[rubygems](https://rubygems.org)"""
    RVM = "rvm"
    """[rvm](https://rvm.io)"""


@dataclass
class PackageManager:
    """Representation of a package manager. Use this class to obtain all packages managed by a particular package \
    manager across all servers and directories."""

    identifier: str
    """The package manager's unique identifier. Refer to `PackageManagerIdentifier` for valid values."""
    packages: PackagesMetadataList

    @classmethod
    def list_from_packages(cls, packages: Union[PackagesMetadataList, List[PackageMetadata]]) -> List['PackageManager']:
        """Create a list of `PackageManager` objects from a list of package metadata items.
        
        Parameters
        ----------
        packages
            A `PackagesMetadataList` or a list of `PackageMetadata` items that should be grouped by their
            `package_manager` property.
            
        Returns
        -------
        List[PackageManager]
            A list of `PackageManager` objects, each containing only the package infos obtained via this package
            manager.        
        """
        package_manager_identifiers = sorted(list({package.package_manager for package in packages
                                                   if package.package_manager is not None}))
        return [PackageManager(identifier, PackagesMetadataList([
            package for package in packages if package.package_manager == identifier]))
                for identifier in package_manager_identifiers]

    def __str__(self):
        return f"package manager: {self.identifier}"

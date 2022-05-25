"""
Store implementation.
"""
import json
import pathlib
import shutil
import sys
from datetime import datetime
from typing import Dict
from typing import List
from typing import Tuple

try:
    from typing_extensions import TypedDict
except ImportError:
    from typing import TypedDict  # type: ignore[attr-defined,no-redef]

import pkg_resources
from pip._vendor.packaging.utils import canonicalize_name
from pip._internal.req.constructors import parse_req_from_line

from tiamatpip import configure


class PackageDict(TypedDict):
    """
    Type declaration for an installed package.
    """

    name: str
    version: str
    install_date: str


class StoreDict(TypedDict):
    """
    Type declaration for the store data format to write to disk.
    """

    fmt_version: int
    packages: List[PackageDict]
    python_version: Tuple[int, int, int]


def parse_package_name(pkg: str) -> str:
    """
    Parse the package name.

    Given a package name(``pop_config``), or requirement(``pop_config<9.0.0``),
    return the canonical name of the package.
    """
    req = parse_req_from_line(pkg, None)
    if req.requirement:
        return canonicalize_name(req.requirement.name)
    return canonicalize_name(pkg)


def get_distribution(pkg: str, pypath: pathlib.Path) -> pkg_resources.Distribution:
    """
    Custom ``pkg_resources.get_distribution`` implementation.

    The difference is that we provide the path on where to look for
    the distributions.
    """
    pkg = parse_package_name(pkg)
    working_set = pkg_resources.WorkingSet(entries=[str(pypath)])
    for dist in working_set:
        if dist.key == pkg:
            return dist
    raise DistributionNotFound(f"Distribution {pkg} was not found installed")


class DistributionNotFound(Exception):
    """
    Exception raised when the distribution is not found.
    """


class InstalledPackage:
    """
    Thin wrapper around an installed package.
    """

    __slots__ = ("name", "version", "install_date")

    def __init__(self, name, version, install_date=None):
        self.name = name
        self.version = version
        if isinstance(install_date, str):
            install_date = datetime.strptime(install_date, "%Y-%m-%dT%H:%M:%S.%f")
        self.install_date = install_date

    def __repr__(self):
        """
        String representation of the class.
        """
        return (
            f"<{self.__class__.__name__} name={self.name}, "
            f"version={self.version}, "
            f"install_date={self.install_date.isoformat()}>"
        )

    @classmethod
    def from_distribution(cls, distribution):
        """
        Instantiate class from a distribution.
        """
        return cls(
            distribution.key,
            version=str(distribution.version),
            install_date=datetime.utcnow(),
        )

    def to_dict(self) -> PackageDict:
        """
        Convert thin wrapper to a dictionary.
        """
        return {
            "name": self.name,
            "version": self.version,
            "install_date": self.install_date.isoformat(),
        }


class Store:
    """
    Store implementation to track installed packages.
    """

    fmt_version = 1

    slots = ("_pypath", "_path", "_path_save", "_store", "_py_version", "fmt_version")

    def __init__(self, pypath=None):
        self._store: Dict[str, InstalledPackage] = {}
        self._pypath = pypath = pypath or configure.get_user_base_path()
        self._path = pypath / ".installs.json"
        self._path_save = pypath / ".installs.json.new"
        self._py_version = sys.version_info[:3]
        if self._path.exists():
            try:
                contents = self._path.read_text()
                store = json.loads(contents)
                self._py_version = store["python_version"]
                for entry in store["packages"]:
                    ipkg = InstalledPackage(**entry)
                    self._store[ipkg.name] = ipkg
            except ValueError:
                pass

    def __repr__(self):
        """
        String representation of the class.
        """
        return f"<{self.__class__.__name__} path={self._path}, stored={self._store}>"

    def add(self, pkg: str) -> None:
        """
        Add package to the store.
        """
        user_site_path = configure.get_user_site_path()
        assert user_site_path
        distribution = get_distribution(pkg, user_site_path)
        ipkg = InstalledPackage.from_distribution(distribution)
        self._store[ipkg.name] = ipkg

    def remove(self, pkg: str) -> None:
        """
        Remove package from the store.
        """
        pkg = parse_package_name(pkg)
        if pkg in self._store:
            self._store.pop(pkg)
            return
        raise DistributionNotFound(f"The '{pkg}' package was not found installed")

    def write(self) -> None:
        """
        Write the store state to disk.
        """
        data: StoreDict = {
            "fmt_version": self.fmt_version,
            "packages": [],
            "python_version": self._py_version,
        }
        for pkg in self._store.values():
            data["packages"].append(pkg.to_dict())
        contents = json.dumps(data, sort_keys=True, indent=4)
        self._path_save.write_text(contents)
        shutil.move(self._path_save, self._path)

    def __contains__(self, pkg: str) -> bool:
        """
        Method to check if the package exists on the store.
        """
        pkg = parse_package_name(pkg)
        if pkg in self._store:
            return True
        return False

    def __getitem__(self, pkg: str) -> InstalledPackage:
        """
        Method to get the package details from the store.
        """
        pkg = parse_package_name(pkg)
        try:
            return self._store[pkg]
        except KeyError:
            raise DistributionNotFound(f"The '{pkg}' package was not found in store")

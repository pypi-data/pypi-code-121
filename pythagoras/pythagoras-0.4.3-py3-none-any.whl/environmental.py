"""Members of this module are used to ensure that user environment satisfies given constraints"""
import subprocess
import sys
from dataclasses import dataclass
from typing import Any, List, Optional

import pkg_resources


# Valid for pip 21.1.3
PACKAGE_UPGRADE_MARKER = b"Successfully uninstalled"


class PipInstallError(Exception):
    """Raised when pip is unable to install package"""

    def __init__(self, message: Any):
        self.message = message

    def __str__(self):
        return f"Failed to install package: {self.message}"


class EnvironmentModifiedException(Exception):
    """
    Raised when python environment was modified, so it is advised to restart
    current process.
    """


class UnsupportedPythonVersion(Exception):
    """
    Raised when python version of environment does not satisfies version constraints.
    """


@dataclass
class PythonEnvironment:
    """
    Class that stores information about python environment and makes an attempt to
    bring it to desired state.

    Attributes
    ----------
    required_packages: list of required packages in format understandable by pip
    min_python_version: minimal python version supported
    max_python_version: maximal python version supported
    """

    required_packages: List[str]
    min_python_version: Optional[str] = None
    max_python_version: Optional[str] = None

    def __post_init__(self):
        """
        Make an attempt to bring python environment to state defined by given constraints.

        Raises
        ------
        UnsupportedPythonVersion
            If current python version does not satisfies constrains defined in
            min_python_version and max_python_version
        """
        sys_python_version = pkg_resources.parse_version(
            f"{sys.version_info.major}.{sys.version_info.minor}"
        )
        if self.min_python_version is not None:
            min_version_parsed = pkg_resources.parse_version(self.min_python_version)
            if sys_python_version < min_version_parsed:
                raise UnsupportedPythonVersion(
                    f"{sys_python_version} is lower than {self.min_python_version}"
                )
        if self.max_python_version is not None:
            max_version_parsed = pkg_resources.parse_version(self.max_python_version)
            if sys_python_version > max_version_parsed:
                raise UnsupportedPythonVersion(
                    f"{sys_python_version} is higher than {self.max_python_version}"
                )

        self.required_packages = sorted(self.required_packages)
        if len(self.required_packages) > 0:
            if not self.check_packages_installed():
                self.install_packages()

    def check_packages_installed(self):
        """Check that all packages specified in self.required_packages are installed"""
        for package in self.required_packages:
            try:
                pkg_resources.get_distribution(package)
            except pkg_resources.DistributionNotFound:
                return False
            else:
                return True

    def install_packages(self):
        """
        Install all packages specified in self.required_packages.

        Raises
        ------
        PipInstallError
            If pip process returned nonzero error code
        """
        try:
            output = subprocess.check_output(
                [sys.executable, "-m", "pip", "install"] + self.required_packages
            )
        except (subprocess.SubprocessError, FileNotFoundError) as error:
            raise PipInstallError(error)
        else:
            if PACKAGE_UPGRADE_MARKER in output:
                raise EnvironmentModifiedException()

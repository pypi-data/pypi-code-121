import sys
from abc import ABC, abstractmethod
from typing import Optional


class PythonVersionChecker(ABC):
    """
    Interface for classes which check if the Python version matches a certain criteria.
    """
    @abstractmethod
    def check(self, major: int, minor: int, micro: int, releaselevel: str, serial: int) -> Optional[str]:
        """
        Checks if the given Python version is supported. Returns None if it is supported,
        or an error message if not.

        :param major:           The major version number.
        :param minor:           The minor version number.
        :param micro:           The micro version number.
        :param releaselevel:    The release-level string.
        :param serial:          The serial number.
        :return:                None for pass and error-string for fail.
        """
        pass

    def check_current(self) -> Optional[str]:
        """
        Checks the current Python version.

        :return:    None for pass and error-string for fail.
        """
        # Get the current Python version
        version = sys.version_info

        # Run the check
        return self.check(version.major,
                          version.minor,
                          version.micro,
                          version.releaselevel,
                          version.serial)

    def ensure_current(self):
        """
        Ensures the current Python version passes this check, raising an error if not.
        """
        # Check the current Python version
        error: Optional[str] = self.check_current()

        # If the check failed, raise
        if error is not None:
            raise PythonVersionError(f"Python version check failed: {error}")

    def current_passes(self) -> bool:
        """
        Checks if the current Python version passes this check.
        """
        return self.check_current() is None


class PythonVersionError(Exception):
    """
    Error class for incorrect Python versions.
    """
    pass

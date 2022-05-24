from typing import Optional, List, Dict

from ._PythonVersionChecker import PythonVersionChecker
from ._Python36Checker import Python36Checker
from ._Python37Checker import Python37Checker


class SupportedVersionChecker(PythonVersionChecker):
    """
    Checks if the version of Python is supported by this library.
    """
    supported_versions: Dict[str, PythonVersionChecker] = {
        "Python 3.6": Python36Checker(),
        "Python 3.7": Python37Checker()
    }

    def check(self, major: int, minor: int, micro: int, releaselevel: str, serial: int) -> Optional[str]:
        if any(checker.check(major, minor, micro, releaselevel, serial) is None
               for checker in self.supported_versions.values()):
            return None
        return f"Version {major}.{minor}.{micro} {releaselevel} #{serial} is not supported. " \
            f"Supported versions: {', '.join(self.supported_versions.keys())}"

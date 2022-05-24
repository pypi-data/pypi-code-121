from typing import Optional

from ._PythonVersionChecker import PythonVersionChecker


class Python36Checker(PythonVersionChecker):
    """
    Checks if the version of Python is somewhere in 3.6.
    """
    def check(self, major: int, minor: int, micro: int, releaselevel: str, serial: int) -> Optional[str]:
        if major == 3 and minor == 6:
            return None
        return "Not Python 3.6"

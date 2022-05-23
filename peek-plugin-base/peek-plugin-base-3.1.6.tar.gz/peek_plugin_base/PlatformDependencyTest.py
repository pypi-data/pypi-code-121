import subprocess
import unittest
from os import path
from typing import List
import logging

logger = logging.getLogger(__name__)


class PlatformDependencyTestCaseBase(unittest.TestCase):
    _excludeLinesContaining = (
        # Exclude examples from docstrings
        "from peek_plugin_example",
        # Exclude this file
        "PlatformDependencyTest.py",
    )

    _checkForUnderscoresCmd = (
        'cd "%s" && grep -R peek_plugin .'
        " | grep -v -e peek_plugin_base -e  __pycache__"
    )

    _checkForHyphensCmd = (
        'cd "%s" && grep -R peek-plugin .'
        " | grep -v -e peek-plugin-base -e  __pycache__"
    )

    def _runCmd(self, cmd: str):
        cmdOut = subprocess.check_output(["bash", "-c", cmd + " || true "])

        logger.info("Running command: %s", cmdOut)

        errors = self.__convertErrors(cmdOut)

        for error in errors:
            logger.error(error)

        self.assertFalse(errors)

    def __convertErrors(self, cmdOut: bytes) -> List[str]:
        errors = cmdOut.decode().strip()

        if not errors:
            return []

        errors = errors.split("\n")
        errors = filter(
            lambda e: not [e for t in self._excludeLinesContaining if t in e], errors
        )

        return list(errors)


class PlatformDependencyTestCase(PlatformDependencyTestCaseBase):
    def setUp(self):
        self._excludeLinesContaining += (
            "Example from peek_plugin_noop.storage.DeclarativeBase.py",
        )
        self._pkgPath = path.dirname(__file__)

    def test_for_plugin_references_1(self):
        self._runCmd(self._checkForHyphensCmd % self._pkgPath)

    def test_for_plugin_references_2(self):
        self._runCmd(self._checkForUnderscoresCmd % self._pkgPath)

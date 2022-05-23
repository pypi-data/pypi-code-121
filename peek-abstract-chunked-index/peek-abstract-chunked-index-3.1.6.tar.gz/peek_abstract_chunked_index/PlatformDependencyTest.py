from os import path

from peek_plugin_base.PlatformDependencyTest import PlatformDependencyTestCaseBase


class PlatformDependencyTestCase(PlatformDependencyTestCaseBase):
    def setUp(self):
        self._pkgPath = path.dirname(__file__)
        self._checkForHyphensCmd += " | grep -v peek-plugin-chunked-index"
        self._checkForUnderscoresCmd += " | grep -v peek_plugin_chunked_index"

    def test_for_plugin_references_1(self):
        self._runCmd(self._checkForHyphensCmd % self._pkgPath)

    def test_for_plugin_references_2(self):
        self._runCmd(self._checkForUnderscoresCmd % self._pkgPath)

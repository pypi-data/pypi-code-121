"""
TODO
"""
import pytest
from pdm import Core
from pytest_cppython.plugin import InterfaceIntegrationTests
from pytest_mock import MockerFixture

from cppython_pdm.plugin import CPPythonPlugin


class TestCPPythonInterface(InterfaceIntegrationTests):
    """
    The tests for the PDM interface
    """

    @pytest.fixture(name="interface")
    def fixture_interface(self) -> CPPythonPlugin:
        """
        Override of the plugin provided interface fixture.

        Returns:
            ConsoleInterface -- The Interface object to use for the CPPython defined tests
        """
        return CPPythonPlugin(Core())

    def test_entrypoint(self, mocker: MockerFixture):
        """
        Verify that this project's plugin hook is setup correctly
        """

        patch = mocker.patch("cppython_pdm.plugin.CPPythonPlugin")

        core = Core()
        core.load_plugins()

        assert patch.called

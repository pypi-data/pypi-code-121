"""
TODO
"""
import pytest
from cppython_core.schema import (
    PEP621,
    CPPythonData,
    GeneratorConfiguration,
    PyProject,
    TargetEnum,
    ToolData,
)
from pytest_cppython.plugin import GeneratorIntegrationTests

from cppython_vcpkg.plugin import VcpkgGenerator

default_pep621 = PEP621(name="test_name", version="1.0")
default_cppython_data = CPPythonData(**{"target": TargetEnum.EXE})
default_tool_data = ToolData(**{"cppython": default_cppython_data})
default_pyproject = PyProject(**{"project": default_pep621, "tool": default_tool_data})


class TestCPPythonGenerator(GeneratorIntegrationTests):
    """
    The tests for the PDM generator
    """

    @pytest.fixture(name="generator")
    def fixture_generator(self) -> VcpkgGenerator:
        """
        Override of the plugin provided generator fixture.
        """
        configuration = GeneratorConfiguration()
        return VcpkgGenerator(configuration, default_pep621, default_cppython_data)

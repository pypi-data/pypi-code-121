import sys
import pytest
from tests.support.helpers import TiamatPipProject

@pytest.fixture
def project(tmp_path):
    name = "tiamat-pip-upgrade"
    project = TiamatPipProject(
        name=name,
        path=tmp_path,
        requirements=["Jinja2==3.0.0"],
    )
    with project:
        yield project


def test_pip_upgrade(project):
    """
    Test that we can upgrade a package which was shipped with the tiamat package.
    """
    code = """
    import sys
    import jinja2
    sys.stdout.write(jinja2.__version__)
    sys.stdout.flush()
    """
    installed_packages = project.get_installed_packages(include_frozen=True)
    assert "jinja2" in installed_packages
    assert installed_packages["jinja2"] == "3.0.0"

    ret = project.run_code(code)
    assert ret.exitcode == 0
    assert ret.stdout.strip() == "3.0.0"

    ret = project.run("pip", "install", "jinja2==3.1.0")
    assert ret.exitcode == 0
    installed_packages = project.get_installed_packages()
    assert "jinja2" in installed_packages
    assert installed_packages["jinja2"] == "3.1.0"

    installed_packages = project.get_installed_packages(include_frozen=True)
    assert "jinja2" in installed_packages
    assert installed_packages["jinja2"] == "3.1.0"

    ret = project.run_code(code)
    assert ret.exitcode == 0
    assert ret.stdout.strip() == "3.1.0"

import sys
import pytest
from tests.support.helpers import TiamatPipProject

@pytest.fixture(scope="module")
def build_project(tmpdir_factory):

    name = "tiamat-pip-upgrade"
    project = TiamatPipProject(
        name=name,,
        path=pathlib.Path(tmpdir_factory.mktemp(name, numbered=True)),
        requirements=["Jinja2==3.0.0", "importlib_metadata"]
    )
    with project:
        yield project


def project(build_project):
    try:
        log.info("Built Project: %s", build_project)
        yield build_project
    finally:
        build_project.delete_pypath()


def test_dunder_version(project):
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


def test_pkg_resources(project):
    code = """
    import sys
    import pkg_resources
    sys.stdout.write("{}".format(pkg_resources.get_distribution("jinja2").version))
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


def test_importlib_metadata_backport(project):
    code = """
    import sys
    import importlib_metadata
    sys.stdout.write(importlib_metadata.version("jinja2"))
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


def test_importlib_metadata_stdlib(project):
    code = """
    import sys
    import importlib.metadata
    sys.stdout.write(importlib.metadata.version("jinja2"))
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

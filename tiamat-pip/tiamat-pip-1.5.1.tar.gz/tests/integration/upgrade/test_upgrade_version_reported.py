import sys

import pytest


def test_dunder_version(project, initial_jinja_version, upgraded_jinja_version):
    code = """
    import sys
    import jinja2
    sys.stdout.write(jinja2.__version__)
    sys.stdout.flush()
    """
    installed_packages = project.get_installed_packages(include_frozen=True)
    assert "jinja2" in installed_packages
    assert installed_packages["jinja2"] == initial_jinja_version

    ret = project.run_code(code)
    assert ret.exitcode == 0
    assert ret.stdout.strip() == initial_jinja_version

    ret = project.run("pip", "install", f"jinja2=={upgraded_jinja_version}")
    assert ret.exitcode == 0
    installed_packages = project.get_installed_packages()
    assert "jinja2" in installed_packages
    assert installed_packages["jinja2"] == upgraded_jinja_version

    installed_packages = project.get_installed_packages(include_frozen=True)
    assert "jinja2" in installed_packages
    assert installed_packages["jinja2"] == upgraded_jinja_version

    ret = project.run_code(code)
    assert ret.exitcode == 0
    assert ret.stdout.strip() == upgraded_jinja_version


@pytest.mark.xfail
def test_pkg_resources(project, initial_jinja_version, upgraded_jinja_version):
    code = """
    import sys
    import pkg_resources
    sys.stdout.write("{}".format(pkg_resources.get_distribution("jinja2").version))
    sys.stdout.flush()
    """
    installed_packages = project.get_installed_packages(include_frozen=True)
    assert "jinja2" in installed_packages
    assert installed_packages["jinja2"] == initial_jinja_version

    ret = project.run_code(code)
    assert ret.exitcode == 0
    assert ret.stdout.strip() == initial_jinja_version

    ret = project.run("pip", "install", f"jinja2=={upgraded_jinja_version}")
    assert ret.exitcode == 0
    installed_packages = project.get_installed_packages()
    assert "jinja2" in installed_packages
    assert installed_packages["jinja2"] == upgraded_jinja_version

    installed_packages = project.get_installed_packages(include_frozen=True)
    assert "jinja2" in installed_packages
    assert installed_packages["jinja2"] == upgraded_jinja_version

    ret = project.run_code(code)
    assert ret.exitcode == 0
    assert ret.stdout.strip() == upgraded_jinja_version


def test_importlib_metadata_backport(
    project, initial_jinja_version, upgraded_jinja_version
):
    code = """
    import sys
    import importlib_metadata
    sys.stdout.write(importlib_metadata.version("jinja2"))
    sys.stdout.flush()
    """
    installed_packages = project.get_installed_packages(include_frozen=True)
    assert "jinja2" in installed_packages
    assert installed_packages["jinja2"] == initial_jinja_version

    ret = project.run_code(code)
    assert ret.exitcode == 0
    assert ret.stdout.strip() == initial_jinja_version

    ret = project.run("pip", "install", f"jinja2=={upgraded_jinja_version}")
    assert ret.exitcode == 0
    installed_packages = project.get_installed_packages()
    assert "jinja2" in installed_packages
    assert installed_packages["jinja2"] == upgraded_jinja_version

    installed_packages = project.get_installed_packages(include_frozen=True)
    assert "jinja2" in installed_packages
    assert installed_packages["jinja2"] == upgraded_jinja_version

    ret = project.run_code(code)
    assert ret.exitcode == 0
    assert ret.stdout.strip() == upgraded_jinja_version


def test_importlib_metadata_stdlib(
    project, initial_jinja_version, upgraded_jinja_version
):
    if sys.version_info < (3, 8):
        pytest.skip("'importlib.metadata' only exists on Py3.8+")

    code = """
    import sys
    import importlib.metadata
    sys.stdout.write(importlib.metadata.version("jinja2"))
    sys.stdout.flush()
    """
    installed_packages = project.get_installed_packages(include_frozen=True)
    assert "jinja2" in installed_packages
    assert installed_packages["jinja2"] == initial_jinja_version

    ret = project.run_code(code)
    assert ret.exitcode == 0
    assert ret.stdout.strip() == initial_jinja_version

    ret = project.run("pip", "install", f"jinja2=={upgraded_jinja_version}")
    assert ret.exitcode == 0
    installed_packages = project.get_installed_packages()
    assert "jinja2" in installed_packages
    assert installed_packages["jinja2"] == upgraded_jinja_version

    installed_packages = project.get_installed_packages(include_frozen=True)
    assert "jinja2" in installed_packages
    assert installed_packages["jinja2"] == upgraded_jinja_version

    ret = project.run_code(code)
    assert ret.exitcode == 0
    assert ret.stdout.strip() == upgraded_jinja_version

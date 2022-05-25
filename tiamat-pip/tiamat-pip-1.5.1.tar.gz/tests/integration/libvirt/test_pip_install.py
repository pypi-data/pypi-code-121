"""
Test the pip install of libvirt-python which needs to link to a system installed library.
"""
import logging
import shutil
import subprocess

import pytest

log = logging.getLogger(__name__)


@pytest.fixture(scope="module", autouse=True)
def check_system_requirements():
    if shutil.which("gcc") is None:
        pytest.skip("Could not find the `gcc` binary")
    pkg_config_path = shutil.which("pkg-config")
    if pkg_config_path is None:
        pytest.skip("Could not find the `pkg-config` binary")
    assert pkg_config_path
    ret = subprocess.run([pkg_config_path, "libvirt"], shell=False, check=False)
    if ret.returncode != 0:
        pytest.skip("The `libvirt` system package is not installed")


def test_libvirt(project):

    # pip list when not installed")
    ret = project.run("pip", "list")
    assert ret.exitcode == 0
    assert "libvirt-python" not in ret.stdout

    # pip install libvirt-python
    ret = project.run("pip", "install", "libvirt-python")
    assert ret.exitcode == 0
    ret = project.run("pip", "list")
    log.debug("Installed packages:\n%s", ret.stdout)
    assert "libvirt-python" in ret.stdout

    # pip uninstall -y libvirt-python
    ret = project.run("pip", "uninstall", "-y", "libvirt-python")
    assert ret.exitcode == 0
    assert "as it is not installed" not in ret.stderr

    # pip list after uninstall
    ret = project.run("pip", "list")
    assert ret.exitcode == 0
    assert "libvirt-python" not in ret.stdout

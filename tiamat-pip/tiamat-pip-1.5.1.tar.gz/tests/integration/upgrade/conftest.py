import logging
import pathlib
import sys

import pytest

from tests.support.helpers import TiamatPipProject

log = logging.getLogger(__name__)


@pytest.fixture(scope="package")
def initial_jinja_version():
    if sys.version_info < (3, 7):
        return "2.11.3"
    return "3.0.0"


@pytest.fixture(scope="package")
def upgraded_jinja_version():
    if sys.version_info < (3, 7):
        return "3.0.0"
    return "3.1.0"


@pytest.fixture(scope="package")
def build_project(tmpdir_factory, initial_jinja_version):
    name = "tiamat-pip-upgrade"
    project = TiamatPipProject(
        name=name,
        path=pathlib.Path(tmpdir_factory.mktemp(name, numbered=True)),
        requirements=[f"Jinja2=={initial_jinja_version}", "importlib_metadata"],
    )
    with project:
        yield project


@pytest.fixture
def project(build_project):
    try:
        log.info("Built Project: %s", build_project)
        yield build_project
    finally:
        build_project.delete_pypath()

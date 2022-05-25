import pytest
from mock import Mock, patch

import vessl
from test.conftest import USE_MOCK
from vessl.util.exception import InvalidProjectError
from vessl.util.random import random_string


@pytest.mark.skipif(USE_MOCK, reason="Does not run if mocking is used.")
class TestProject:
    project_name = random_string()

    @pytest.mark.order(index=1)
    def test_create_project(self):
        vessl.create_project(self.project_name)

    def test_read_project(self):
        vessl.read_project(self.project_name)

    def test_list_projects(self):
        vessl.list_projects()


def test_get_project_name():
    with patch.object(vessl.vessl_api, "project", None):
        with pytest.raises(InvalidProjectError):
            vessl.project._get_project_name()

    project_name = "proj"
    assert vessl.project._get_project_name(project_name=project_name) == project_name

    project = Mock()
    project.name = project_name
    with patch.object(vessl.vessl_api, "project", project):
        assert vessl.project._get_project_name() == project_name


def test_get_project():
    with patch.object(vessl.vessl_api, "project", None):
        with pytest.raises(InvalidProjectError):
            vessl.project._get_project()

    project_name = "proj"

    project = Mock()
    project.name = project_name
    with patch.object(vessl.project, "read_project", return_value=project):
        assert (
            vessl.project._get_project(project_name=project_name).name == project_name
        )

    with patch.object(vessl.vessl_api, "project", project):
        assert vessl.project._get_project().name == project_name

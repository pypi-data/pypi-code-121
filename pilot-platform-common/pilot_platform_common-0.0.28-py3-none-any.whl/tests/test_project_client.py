import pytest

from common import ProjectClientSync as ProjectClient
from common import ProjectException, ProjectNotFoundException
from tests.conftest import PROJECT_DATA, PROJECT_ID, PROJECT_URL


def test_get_by_code_200(redis, mock_get_by_code):
    project_client = ProjectClient(PROJECT_URL, redis.url)
    project = project_client.get(code=PROJECT_DATA["code"])
    assert project.name == PROJECT_DATA["name"]
    assert project.json()["name"] == PROJECT_DATA["name"]


def test_get_by_id_200(redis, mock_get_by_id):
    project_client = ProjectClient(PROJECT_URL, redis.url)
    project = project_client.get(id=PROJECT_ID)
    assert project.name == PROJECT_DATA["name"]
    assert project.json()["name"] == PROJECT_DATA["name"]


def test_get_by_id_404(redis, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url=PROJECT_URL + "/v1/projects/notfound",
        json={},
        status_code=404,
    )
    project_client = ProjectClient(PROJECT_URL, redis.url)
    with pytest.raises(ProjectNotFoundException):
        project_client.get(code="notfound")


def test_get_by_id_500(redis, httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url=PROJECT_URL + "/v1/projects/error",
        json={},
        status_code=500,
    )
    project_client = ProjectClient(PROJECT_URL, redis.url)
    with pytest.raises(ProjectException):
        project_client.get(code="error")


def test_project_update_200(redis, mock_get_by_code, httpx_mock):
    update_data = PROJECT_DATA.copy()
    update_data["name"] = "updated"
    project_id = update_data["id"]
    httpx_mock.add_response(
        method="PATCH",
        url=PROJECT_URL + f"/v1/projects/{project_id}",
        json=update_data,
        status_code=200,
    )

    project_client = ProjectClient(PROJECT_URL, redis.url, enable_cache=False)
    project = project_client.get(code=PROJECT_DATA["code"])
    assert project.name == PROJECT_DATA["name"]
    project.update(name="updated")
    assert project.name == "updated"


def test_project_update_500(redis, mock_get_by_code, httpx_mock):
    update_data = PROJECT_DATA.copy()
    update_data["name"] = "updated"
    project_id = update_data["id"]
    httpx_mock.add_response(
        method="PATCH",
        url=PROJECT_URL + f"/v1/projects/{project_id}",
        json={},
        status_code=500,
    )

    project_client = ProjectClient(PROJECT_URL, redis.url, enable_cache=False)
    project = project_client.get(code=PROJECT_DATA["code"])
    assert project.name == PROJECT_DATA["name"]
    with pytest.raises(ProjectException):
        project.update(name="updated")


def test_create_project_200(redis, httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url=PROJECT_URL + "/v1/projects/",
        json=PROJECT_DATA,
        status_code=200,
    )

    project_client = ProjectClient(PROJECT_URL, redis.url, enable_cache=False)
    project = project_client.create(
        name=PROJECT_DATA["name"],
        code=PROJECT_DATA["code"],
        description=PROJECT_DATA["description"],
        tags=PROJECT_DATA["tags"],
        system_tags=PROJECT_DATA["system_tags"],
    )
    assert project.name == PROJECT_DATA["name"]


def test_create_project_500(redis, httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url=PROJECT_URL + "/v1/projects/",
        json={},
        status_code=500,
    )

    project_client = ProjectClient(PROJECT_URL, redis.url, enable_cache=False)
    with pytest.raises(ProjectException):
        project_client.create(
            name=PROJECT_DATA["name"],
            code=PROJECT_DATA["code"],
            description=PROJECT_DATA["description"],
            tags=PROJECT_DATA["tags"],
            system_tags=PROJECT_DATA["system_tags"],
        )


def test_project_search_200(redis, httpx_mock):
    result = {
        "result": [PROJECT_DATA],
        "total": 1,
    }
    url = PROJECT_URL + ("/v1/projects/?name=Unit+Test+Project&code=unittestproject&description=Test"
                         "&tags_all=tag1&tags_all=tag2")
    httpx_mock.add_response(
        method="GET",
        url=url,
        json=result,
        status_code=200,
    )

    project_client = ProjectClient(PROJECT_URL, redis.url, enable_cache=False)
    result = project_client.search(
        name=PROJECT_DATA["name"],
        code=PROJECT_DATA["code"],
        description=PROJECT_DATA["description"],
        tags_all=PROJECT_DATA["tags"],
    )
    assert result["result"][0].name == PROJECT_DATA["name"]
    assert result["total"] == 1

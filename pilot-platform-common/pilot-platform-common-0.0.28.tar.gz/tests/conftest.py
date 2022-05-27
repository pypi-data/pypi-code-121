from uuid import uuid4

import pytest
from testcontainers.redis import RedisContainer

PROJECT_URL  = "http://project"

PROJECT_ID = str(uuid4())

PROJECT_DATA = {
    "id": PROJECT_ID,
    "code": "unittestproject",
    "description": "Test",
    "name": "Unit Test Project",
    "tags": ["tag1", "tag2"],
    "system_tags": ["system"],
}


@pytest.fixture
def mock_get_by_code(httpx_mock):
    code = PROJECT_DATA["code"]
    httpx_mock.add_response(
        method="GET",
        url=PROJECT_URL + f"/v1/projects/{code}",
        json=PROJECT_DATA,
        status_code=200,
    )

@pytest.fixture
def mock_get_by_id(httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url=PROJECT_URL + f"/v1/projects/{PROJECT_ID}",
        json=PROJECT_DATA,
        status_code=200,
    )


@pytest.fixture(scope='session', autouse=True)
def redis():
    with RedisContainer("redis:latest") as redis:
        host = redis.get_container_host_ip()
        port = redis.get_exposed_port(redis.port_to_expose)
        redis.url = f"redis://{host}:{port}"
        yield redis

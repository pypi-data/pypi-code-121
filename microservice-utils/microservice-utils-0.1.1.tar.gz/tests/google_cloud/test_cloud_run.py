import pytest

from microservice_utils.google_cloud.adapters.cloud_run import get_service_url


class FakeGcpProjectConfig:
    ...


async def test_url_provider(*args, **kwargs) -> list[str]:
    return [
        "https://staging-accounts-service-oir932o-uc.a.run.app",
        "https://production-accounts-service-0smn3lu-uc.a.run.app",
        "https://staging-photos-service-9fsnd3w-uc.a.run.app",
    ]


@pytest.mark.parametrize(
    "matches,expected",
    [
        (["staging", "photos"], "https://staging-photos-service-9fsnd3w-uc.a.run.app"),
        (
            ["production", "accounts"],
            "https://production-accounts-service-0smn3lu-uc.a.run.app",
        ),
    ],
)
async def test_get_service_url(matches, expected):
    url = await get_service_url(
        FakeGcpProjectConfig(), matches, url_provider=test_url_provider
    )

    assert url == expected

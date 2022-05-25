import typing

from google.cloud import run_v2

from microservice_utils.google_cloud.models import GcpProjectConfig


async def get_cloud_run_urls(project: GcpProjectConfig) -> list[str]:
    client = run_v2.ServicesAsyncClient()
    request = run_v2.ListServicesRequest(parent=project.location_path)
    page_result = await client.list_services(request=request)

    return [response.uri async for response in page_result]


async def get_service_url(
    project: GcpProjectConfig,
    matches: list[str],
    url_provider: typing.Callable[
        [GcpProjectConfig], typing.Awaitable[list[str]]
    ] = get_cloud_run_urls,
) -> str:
    urls = await url_provider(project)
    matches = [url for url in urls if all(match in url for match in matches)]

    if len(matches) != 1:
        raise RuntimeError(f"Expected 1 service match, got {len(matches)}")

    return matches[0]

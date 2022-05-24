from typing import Any, Dict, Optional

import httpx

from ...client import Client
from ...models.benchling_app_configuration import BenchlingAppConfiguration
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    app_id: str,
) -> Dict[str, Any]:
    url = "{}/apps/{app_id}/configuration".format(client.base_url, app_id=app_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[BenchlingAppConfiguration]:
    if response.status_code == 200:
        response_200 = BenchlingAppConfiguration.from_dict(response.json())

        return response_200
    return None


def _build_response(*, response: httpx.Response) -> Response[BenchlingAppConfiguration]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    app_id: str,
) -> Response[BenchlingAppConfiguration]:
    kwargs = _get_kwargs(
        client=client,
        app_id=app_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    app_id: str,
) -> Optional[BenchlingAppConfiguration]:
    """ Get an app's configuration by app id """

    return sync_detailed(
        client=client,
        app_id=app_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    app_id: str,
) -> Response[BenchlingAppConfiguration]:
    kwargs = _get_kwargs(
        client=client,
        app_id=app_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    app_id: str,
) -> Optional[BenchlingAppConfiguration]:
    """ Get an app's configuration by app id """

    return (
        await asyncio_detailed(
            client=client,
            app_id=app_id,
        )
    ).parsed

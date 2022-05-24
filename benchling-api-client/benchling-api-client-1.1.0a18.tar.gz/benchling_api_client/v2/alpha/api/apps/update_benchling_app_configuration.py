from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.benchling_app_configuration import BenchlingAppConfiguration
from ...models.benchling_app_configuration_update import BenchlingAppConfigurationUpdate
from ...models.forbidden_error import ForbiddenError
from ...models.not_found_error import NotFoundError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    configuration_id: str,
    json_body: BenchlingAppConfigurationUpdate,
) -> Dict[str, Any]:
    url = "{}/app-configurations/{configuration_id}".format(
        client.base_url, configuration_id=configuration_id
    )

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[BenchlingAppConfiguration, ForbiddenError, NotFoundError]]:
    if response.status_code == 200:
        response_200 = BenchlingAppConfiguration.from_dict(response.json())

        return response_200
    if response.status_code == 403:
        response_403 = ForbiddenError.from_dict(response.json())

        return response_403
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[BenchlingAppConfiguration, ForbiddenError, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    configuration_id: str,
    json_body: BenchlingAppConfigurationUpdate,
) -> Response[Union[BenchlingAppConfiguration, ForbiddenError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        configuration_id=configuration_id,
        json_body=json_body,
    )

    response = httpx.patch(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    configuration_id: str,
    json_body: BenchlingAppConfigurationUpdate,
) -> Optional[Union[BenchlingAppConfiguration, ForbiddenError, NotFoundError]]:
    """ Update app configuration """

    return sync_detailed(
        client=client,
        configuration_id=configuration_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    configuration_id: str,
    json_body: BenchlingAppConfigurationUpdate,
) -> Response[Union[BenchlingAppConfiguration, ForbiddenError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        configuration_id=configuration_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.patch(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    configuration_id: str,
    json_body: BenchlingAppConfigurationUpdate,
) -> Optional[Union[BenchlingAppConfiguration, ForbiddenError, NotFoundError]]:
    """ Update app configuration """

    return (
        await asyncio_detailed(
            client=client,
            configuration_id=configuration_id,
            json_body=json_body,
        )
    ).parsed

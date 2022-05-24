from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.feature import Feature
from ...models.not_found_error import NotFoundError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    feature_id: str,
) -> Dict[str, Any]:
    url = "{}/features/{feature_id}".format(client.base_url, feature_id=feature_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Feature, NotFoundError]]:
    if response.status_code == 200:
        response_200 = Feature.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Feature, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    feature_id: str,
) -> Response[Union[Feature, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        feature_id=feature_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    feature_id: str,
) -> Optional[Union[Feature, NotFoundError]]:
    """ Get a feature by ID """

    return sync_detailed(
        client=client,
        feature_id=feature_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    feature_id: str,
) -> Response[Union[Feature, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        feature_id=feature_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    feature_id: str,
) -> Optional[Union[Feature, NotFoundError]]:
    """ Get a feature by ID """

    return (
        await asyncio_detailed(
            client=client,
            feature_id=feature_id,
        )
    ).parsed

from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.feature_library import FeatureLibrary
from ...models.feature_library_update import FeatureLibraryUpdate
from ...models.not_found_error import NotFoundError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    feature_library_id: str,
    json_body: FeatureLibraryUpdate,
) -> Dict[str, Any]:
    url = "{}/feature-libraries/{feature_library_id}".format(
        client.base_url, feature_library_id=feature_library_id
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
) -> Optional[Union[FeatureLibrary, BadRequestError, NotFoundError]]:
    if response.status_code == 200:
        response_200 = FeatureLibrary.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[FeatureLibrary, BadRequestError, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    feature_library_id: str,
    json_body: FeatureLibraryUpdate,
) -> Response[Union[FeatureLibrary, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        feature_library_id=feature_library_id,
        json_body=json_body,
    )

    response = httpx.patch(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    feature_library_id: str,
    json_body: FeatureLibraryUpdate,
) -> Optional[Union[FeatureLibrary, BadRequestError, NotFoundError]]:
    """Update a feature library. Note: Features cannot be updated from this endpoint.
    Use the /features* endpoints to add or modify features.
    """

    return sync_detailed(
        client=client,
        feature_library_id=feature_library_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    feature_library_id: str,
    json_body: FeatureLibraryUpdate,
) -> Response[Union[FeatureLibrary, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        feature_library_id=feature_library_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.patch(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    feature_library_id: str,
    json_body: FeatureLibraryUpdate,
) -> Optional[Union[FeatureLibrary, BadRequestError, NotFoundError]]:
    """Update a feature library. Note: Features cannot be updated from this endpoint.
    Use the /features* endpoints to add or modify features.
    """

    return (
        await asyncio_detailed(
            client=client,
            feature_library_id=feature_library_id,
            json_body=json_body,
        )
    ).parsed

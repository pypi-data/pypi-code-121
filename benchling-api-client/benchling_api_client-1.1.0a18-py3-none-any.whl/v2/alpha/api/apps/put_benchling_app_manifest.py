from typing import Any, Dict, Optional, Union

import httpx
import yaml

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.benchling_app_manifest import BenchlingAppManifest
from ...models.conflict_error import ConflictError
from ...models.forbidden_error import ForbiddenError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    app_id: str,
    yaml_body: BenchlingAppManifest,
) -> Dict[str, Any]:
    url = "{}/apps/{app_id}/manifest.yaml".format(client.base_url, app_id=app_id)

    headers: Dict[str, Any] = client.get_headers()

    yaml_yaml_body = yaml_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": yaml_yaml_body,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[
    Union[BenchlingAppManifest, BenchlingAppManifest, BadRequestError, ForbiddenError, ConflictError]
]:
    if response.status_code == 200:
        yaml_dict = yaml.safe_load(response.text.encode("utf-8"))
        response_200 = BenchlingAppManifest.from_dict(yaml_dict)

        return response_200
    if response.status_code == 201:
        yaml_dict = yaml.safe_load(response.text.encode("utf-8"))
        response_201 = BenchlingAppManifest.from_dict(yaml_dict)

        return response_201
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    if response.status_code == 403:
        response_403 = ForbiddenError.from_dict(response.json())

        return response_403
    if response.status_code == 409:
        response_409 = ConflictError.from_dict(response.json())

        return response_409
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[
    Union[BenchlingAppManifest, BenchlingAppManifest, BadRequestError, ForbiddenError, ConflictError]
]:
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
    yaml_body: BenchlingAppManifest,
) -> Response[
    Union[BenchlingAppManifest, BenchlingAppManifest, BadRequestError, ForbiddenError, ConflictError]
]:
    kwargs = _get_kwargs(
        client=client,
        app_id=app_id,
        yaml_body=yaml_body,
    )

    response = httpx.put(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    app_id: str,
    yaml_body: BenchlingAppManifest,
) -> Optional[
    Union[BenchlingAppManifest, BenchlingAppManifest, BadRequestError, ForbiddenError, ConflictError]
]:
    """ Create or update from an app manifest """

    return sync_detailed(
        client=client,
        app_id=app_id,
        yaml_body=yaml_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    app_id: str,
    yaml_body: BenchlingAppManifest,
) -> Response[
    Union[BenchlingAppManifest, BenchlingAppManifest, BadRequestError, ForbiddenError, ConflictError]
]:
    kwargs = _get_kwargs(
        client=client,
        app_id=app_id,
        yaml_body=yaml_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.put(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    app_id: str,
    yaml_body: BenchlingAppManifest,
) -> Optional[
    Union[BenchlingAppManifest, BenchlingAppManifest, BadRequestError, ForbiddenError, ConflictError]
]:
    """ Create or update from an app manifest """

    return (
        await asyncio_detailed(
            client=client,
            app_id=app_id,
            yaml_body=yaml_body,
        )
    ).parsed

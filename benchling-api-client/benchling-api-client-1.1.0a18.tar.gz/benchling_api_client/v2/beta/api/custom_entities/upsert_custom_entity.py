from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.custom_entity import CustomEntity
from ...models.custom_entity_upsert_request import CustomEntityUpsertRequest
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    entity_registry_id: str,
    json_body: CustomEntityUpsertRequest,
) -> Dict[str, Any]:
    url = "{}/custom-entities/{entity_registry_id}:upsert".format(
        client.base_url, entity_registry_id=entity_registry_id
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
) -> Optional[Union[CustomEntity, CustomEntity, BadRequestError]]:
    if response.status_code == 200:
        response_200 = CustomEntity.from_dict(response.json())

        return response_200
    if response.status_code == 201:
        response_201 = CustomEntity.from_dict(response.json())

        return response_201
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[CustomEntity, CustomEntity, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    entity_registry_id: str,
    json_body: CustomEntityUpsertRequest,
) -> Response[Union[CustomEntity, CustomEntity, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        entity_registry_id=entity_registry_id,
        json_body=json_body,
    )

    response = httpx.patch(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    entity_registry_id: str,
    json_body: CustomEntityUpsertRequest,
) -> Optional[Union[CustomEntity, CustomEntity, BadRequestError]]:
    """Create or update a registered custom entity.

    Schema field links can be populated using entity registry IDs or API IDs. In the `value` field of the [Field](#/components/schemas/FieldWithResolution) resource, the object `{\"entityRegistryId\": ENTITY_REGISTRY_ID}` may be provided instead of the API ID if desired (see example value).
    """

    return sync_detailed(
        client=client,
        entity_registry_id=entity_registry_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    entity_registry_id: str,
    json_body: CustomEntityUpsertRequest,
) -> Response[Union[CustomEntity, CustomEntity, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        entity_registry_id=entity_registry_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.patch(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    entity_registry_id: str,
    json_body: CustomEntityUpsertRequest,
) -> Optional[Union[CustomEntity, CustomEntity, BadRequestError]]:
    """Create or update a registered custom entity.

    Schema field links can be populated using entity registry IDs or API IDs. In the `value` field of the [Field](#/components/schemas/FieldWithResolution) resource, the object `{\"entityRegistryId\": ENTITY_REGISTRY_ID}` may be provided instead of the API ID if desired (see example value).
    """

    return (
        await asyncio_detailed(
            client=client,
            entity_registry_id=entity_registry_id,
            json_body=json_body,
        )
    ).parsed

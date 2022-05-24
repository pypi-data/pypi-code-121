from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.async_task_link import AsyncTaskLink
from ...models.bad_request_error import BadRequestError
from ...models.rna_oligos_bulk_upsert_request import RnaOligosBulkUpsertRequest
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    json_body: RnaOligosBulkUpsertRequest,
    returning: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/rna-oligos:bulk-upsert".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {}
    if not isinstance(returning, Unset) and returning is not None:
        params["returning"] = returning

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[AsyncTaskLink, BadRequestError]]:
    if response.status_code == 202:
        response_202 = AsyncTaskLink.from_dict(response.json())

        return response_202
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[AsyncTaskLink, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    json_body: RnaOligosBulkUpsertRequest,
    returning: Union[Unset, str] = UNSET,
) -> Response[Union[AsyncTaskLink, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
        returning=returning,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    json_body: RnaOligosBulkUpsertRequest,
    returning: Union[Unset, str] = UNSET,
) -> Optional[Union[AsyncTaskLink, BadRequestError]]:
    """All entities and their schemas must be within the same registry.

    This operation performs the following actions:
    1. Any existing objects are looked up in Benchling by the provided entity registry ID.
    2. Then, all objects are either created or updated accordingly, temporarily skipping any schema field links between objects.
    3. Schema field links can be populated using entity registry IDs or API IDs. In the `value` field of the [Field](#/components/schemas/FieldWithResolution) resource, the object `{\"entityRegistryId\": ENTITY_REGISTRY_ID}` may be provided instead of the API ID if desired (see example value). You may link to objects being created in the same operation.
    4. Entities are registered, using the provided name and entity registry ID.

    If any action fails, the whole operation is canceled and no objects are created or updated.

    Limit of 1000 entities per request.
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
        returning=returning,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    json_body: RnaOligosBulkUpsertRequest,
    returning: Union[Unset, str] = UNSET,
) -> Response[Union[AsyncTaskLink, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
        returning=returning,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    json_body: RnaOligosBulkUpsertRequest,
    returning: Union[Unset, str] = UNSET,
) -> Optional[Union[AsyncTaskLink, BadRequestError]]:
    """All entities and their schemas must be within the same registry.

    This operation performs the following actions:
    1. Any existing objects are looked up in Benchling by the provided entity registry ID.
    2. Then, all objects are either created or updated accordingly, temporarily skipping any schema field links between objects.
    3. Schema field links can be populated using entity registry IDs or API IDs. In the `value` field of the [Field](#/components/schemas/FieldWithResolution) resource, the object `{\"entityRegistryId\": ENTITY_REGISTRY_ID}` may be provided instead of the API ID if desired (see example value). You may link to objects being created in the same operation.
    4. Entities are registered, using the provided name and entity registry ID.

    If any action fails, the whole operation is canceled and no objects are created or updated.

    Limit of 1000 entities per request.
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
            returning=returning,
        )
    ).parsed

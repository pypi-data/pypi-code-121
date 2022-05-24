from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.entry_templates_paginated_list import EntryTemplatesPaginatedList
from ...types import Response, UNSET, Unset


def _get_kwargs(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    template_collection_id: Union[Unset, str] = UNSET,
    mentions: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    schema_id: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/entry-templates".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {}
    if not isinstance(page_size, Unset) and page_size is not None:
        params["pageSize"] = page_size
    if not isinstance(next_token, Unset) and next_token is not None:
        params["nextToken"] = next_token
    if not isinstance(modified_at, Unset) and modified_at is not None:
        params["modifiedAt"] = modified_at
    if not isinstance(name, Unset) and name is not None:
        params["name"] = name
    if not isinstance(template_collection_id, Unset) and template_collection_id is not None:
        params["templateCollectionId"] = template_collection_id
    if not isinstance(mentions, Unset) and mentions is not None:
        params["mentions"] = mentions
    if not isinstance(ids, Unset) and ids is not None:
        params["ids"] = ids
    if not isinstance(schema_id, Unset) and schema_id is not None:
        params["schemaId"] = schema_id
    if not isinstance(namesany_of, Unset) and namesany_of is not None:
        params["names.anyOf"] = namesany_of
    if not isinstance(namesany_ofcase_sensitive, Unset) and namesany_ofcase_sensitive is not None:
        params["names.anyOf.caseSensitive"] = namesany_ofcase_sensitive
    if not isinstance(creator_ids, Unset) and creator_ids is not None:
        params["creatorIds"] = creator_ids

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[EntryTemplatesPaginatedList, BadRequestError]]:
    if response.status_code == 200:
        response_200 = EntryTemplatesPaginatedList.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[EntryTemplatesPaginatedList, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    template_collection_id: Union[Unset, str] = UNSET,
    mentions: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    schema_id: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
) -> Response[Union[EntryTemplatesPaginatedList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        page_size=page_size,
        next_token=next_token,
        modified_at=modified_at,
        name=name,
        template_collection_id=template_collection_id,
        mentions=mentions,
        ids=ids,
        schema_id=schema_id,
        namesany_of=namesany_of,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        creator_ids=creator_ids,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    template_collection_id: Union[Unset, str] = UNSET,
    mentions: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    schema_id: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
) -> Optional[Union[EntryTemplatesPaginatedList, BadRequestError]]:
    """ List entry templates """

    return sync_detailed(
        client=client,
        page_size=page_size,
        next_token=next_token,
        modified_at=modified_at,
        name=name,
        template_collection_id=template_collection_id,
        mentions=mentions,
        ids=ids,
        schema_id=schema_id,
        namesany_of=namesany_of,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        creator_ids=creator_ids,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    template_collection_id: Union[Unset, str] = UNSET,
    mentions: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    schema_id: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
) -> Response[Union[EntryTemplatesPaginatedList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        page_size=page_size,
        next_token=next_token,
        modified_at=modified_at,
        name=name,
        template_collection_id=template_collection_id,
        mentions=mentions,
        ids=ids,
        schema_id=schema_id,
        namesany_of=namesany_of,
        namesany_ofcase_sensitive=namesany_ofcase_sensitive,
        creator_ids=creator_ids,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    page_size: Union[Unset, int] = 50,
    next_token: Union[Unset, str] = UNSET,
    modified_at: Union[Unset, str] = UNSET,
    name: Union[Unset, str] = UNSET,
    template_collection_id: Union[Unset, str] = UNSET,
    mentions: Union[Unset, str] = UNSET,
    ids: Union[Unset, str] = UNSET,
    schema_id: Union[Unset, str] = UNSET,
    namesany_of: Union[Unset, str] = UNSET,
    namesany_ofcase_sensitive: Union[Unset, str] = UNSET,
    creator_ids: Union[Unset, str] = UNSET,
) -> Optional[Union[EntryTemplatesPaginatedList, BadRequestError]]:
    """ List entry templates """

    return (
        await asyncio_detailed(
            client=client,
            page_size=page_size,
            next_token=next_token,
            modified_at=modified_at,
            name=name,
            template_collection_id=template_collection_id,
            mentions=mentions,
            ids=ids,
            schema_id=schema_id,
            namesany_of=namesany_of,
            namesany_ofcase_sensitive=namesany_ofcase_sensitive,
            creator_ids=creator_ids,
        )
    ).parsed

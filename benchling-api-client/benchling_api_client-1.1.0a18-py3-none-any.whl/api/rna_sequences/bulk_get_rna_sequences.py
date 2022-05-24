from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.rna_sequences_bulk_get import RnaSequencesBulkGet
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    rna_sequence_ids: str,
) -> Dict[str, Any]:
    url = "{}/rna-sequences:bulk-get".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    params: Dict[str, Any] = {
        "rnaSequenceIds": rna_sequence_ids,
    }

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[RnaSequencesBulkGet, BadRequestError]]:
    if response.status_code == 200:
        response_200 = RnaSequencesBulkGet.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = BadRequestError.from_dict(response.json())

        return response_400
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[RnaSequencesBulkGet, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    rna_sequence_ids: str,
) -> Response[Union[RnaSequencesBulkGet, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        rna_sequence_ids=rna_sequence_ids,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    rna_sequence_ids: str,
) -> Optional[Union[RnaSequencesBulkGet, BadRequestError]]:
    """ Bulk get RNA sequences by ID """

    return sync_detailed(
        client=client,
        rna_sequence_ids=rna_sequence_ids,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    rna_sequence_ids: str,
) -> Response[Union[RnaSequencesBulkGet, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        rna_sequence_ids=rna_sequence_ids,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    rna_sequence_ids: str,
) -> Optional[Union[RnaSequencesBulkGet, BadRequestError]]:
    """ Bulk get RNA sequences by ID """

    return (
        await asyncio_detailed(
            client=client,
            rna_sequence_ids=rna_sequence_ids,
        )
    ).parsed

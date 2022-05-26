import random
from time import sleep
from typing import Any, Dict, Union

import httpx

from ...client import AuthenticatedClient
from ...models.http_error import HttpError
from ...models.http_validation_error import HTTPValidationError
from ...models.list_response_application_out import ListResponseApplicationOut
from ...types import UNSET, Unset


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    iterator: Union[Unset, None, str] = UNSET,
    limit: Union[Unset, None, int] = 50,
    idempotency_key: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/api/v1/app/".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    if not isinstance(idempotency_key, Unset):
        headers["idempotency-key"] = idempotency_key

    params: Dict[str, Any] = {}
    params["iterator"] = iterator

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> ListResponseApplicationOut:
    if response.status_code == 401:
        raise HttpError(response.json(), response.status_code)
    if response.status_code == 403:
        raise HttpError(response.json(), response.status_code)
    if response.status_code == 404:
        raise HttpError(response.json(), response.status_code)
    if response.status_code == 409:
        raise HttpError(response.json(), response.status_code)
    if response.status_code == 422:
        raise HTTPValidationError(response.json(), response.status_code)
    if response.status_code == 429:
        raise HttpError(response.json(), response.status_code)
    response_200 = ListResponseApplicationOut.from_dict(response.json())

    return response_200


sleep_time = 0.05
num_retries = 3


def sync_detailed(
    *,
    client: AuthenticatedClient,
    iterator: Union[Unset, None, str] = UNSET,
    limit: Union[Unset, None, int] = 50,
    idempotency_key: Union[Unset, str] = UNSET,
) -> ListResponseApplicationOut:
    """List Applications

     List of all the organization's applications.

    Args:
        iterator (Union[Unset, None, str]):  Example: app_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        limit (Union[Unset, None, int]):  Default: 50.
        idempotency_key (Union[Unset, str]): The request's idempotency key

    Returns:
        ListResponseApplicationOut
    """

    kwargs = _get_kwargs(
        client=client,
        iterator=iterator,
        limit=limit,
        idempotency_key=idempotency_key,
    )

    kwargs["headers"] = {"svix-req-id": f"{random.getrandbits(32)}", **kwargs["headers"]}

    retry_count = 0
    for retry in range(num_retries):
        response = httpx.request(
            verify=client.verify_ssl,
            **kwargs,
        )
        if response.status_code >= 500 and retry < num_retries:
            retry_count += 1
            kwargs["headers"]["svix-retry-count"] = str(retry_count)
            sleep(sleep_time)
            sleep_time * 2
        else:
            break

    return _parse_response(response=response)


def sync(
    *,
    client: AuthenticatedClient,
    iterator: Union[Unset, None, str] = UNSET,
    limit: Union[Unset, None, int] = 50,
    idempotency_key: Union[Unset, str] = UNSET,
) -> ListResponseApplicationOut:
    """List Applications

     List of all the organization's applications.

    Args:
        iterator (Union[Unset, None, str]):  Example: app_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        limit (Union[Unset, None, int]):  Default: 50.
        idempotency_key (Union[Unset, str]): The request's idempotency key

    Returns:
        ListResponseApplicationOut
    """

    return sync_detailed(
        client=client,
        iterator=iterator,
        limit=limit,
        idempotency_key=idempotency_key,
    )


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    iterator: Union[Unset, None, str] = UNSET,
    limit: Union[Unset, None, int] = 50,
    idempotency_key: Union[Unset, str] = UNSET,
) -> ListResponseApplicationOut:
    """List Applications

     List of all the organization's applications.

    Args:
        iterator (Union[Unset, None, str]):  Example: app_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        limit (Union[Unset, None, int]):  Default: 50.
        idempotency_key (Union[Unset, str]): The request's idempotency key

    Returns:
        ListResponseApplicationOut
    """

    kwargs = _get_kwargs(
        client=client,
        iterator=iterator,
        limit=limit,
        idempotency_key=idempotency_key,
    )

    kwargs["headers"] = {"svix-req-id": f"{random.getrandbits(32)}", **kwargs["headers"]}

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        retry_count = 0
        for retry in range(num_retries):
            response = await _client.request(**kwargs)
            if response.status_code >= 500 and retry < num_retries:
                retry_count += 1
                kwargs["headers"]["svix-retry-count"] = str(retry_count)
                sleep(sleep_time)
                sleep_time * 2
            else:
                break

    return _parse_response(response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    iterator: Union[Unset, None, str] = UNSET,
    limit: Union[Unset, None, int] = 50,
    idempotency_key: Union[Unset, str] = UNSET,
) -> ListResponseApplicationOut:
    """List Applications

     List of all the organization's applications.

    Args:
        iterator (Union[Unset, None, str]):  Example: app_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        limit (Union[Unset, None, int]):  Default: 50.
        idempotency_key (Union[Unset, str]): The request's idempotency key

    Returns:
        ListResponseApplicationOut
    """

    return await asyncio_detailed(
        client=client,
        iterator=iterator,
        limit=limit,
        idempotency_key=idempotency_key,
    )

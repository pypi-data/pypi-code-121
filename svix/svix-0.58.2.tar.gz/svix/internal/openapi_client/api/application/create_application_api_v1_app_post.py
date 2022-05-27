import random
from time import sleep
from typing import Any, Dict, Union

import httpx

from ...client import AuthenticatedClient
from ...models.application_in import ApplicationIn
from ...models.application_out import ApplicationOut
from ...models.http_error import HttpError
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Unset


def _get_kwargs(
    *,
    client: AuthenticatedClient,
    json_body: ApplicationIn,
    get_if_exists: Union[Unset, None, bool] = False,
    idempotency_key: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/api/v1/app/".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    if not isinstance(idempotency_key, Unset):
        headers["idempotency-key"] = idempotency_key

    params: Dict[str, Any] = {}
    params["get_if_exists"] = get_if_exists

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    json_json_body = json_body.to_dict()

    return {
        "method": "post",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "json": json_json_body,
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> ApplicationOut:
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
    response_200 = ApplicationOut.from_dict(response.json())

    return response_200


sleep_time = 0.05
num_retries = 3


def sync_detailed(
    *,
    client: AuthenticatedClient,
    json_body: ApplicationIn,
    get_if_exists: Union[Unset, None, bool] = False,
    idempotency_key: Union[Unset, str] = UNSET,
) -> ApplicationOut:
    """Create Application

     Create a new application.

    Args:
        get_if_exists (Union[Unset, None, bool]): Get an existing application, or create a new one
            if doesn't exist. It's two separate functions in the libs.
        idempotency_key (Union[Unset, str]): The request's idempotency key
        json_body (ApplicationIn):

    Returns:
        ApplicationOut
    """

    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
        get_if_exists=get_if_exists,
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
    json_body: ApplicationIn,
    get_if_exists: Union[Unset, None, bool] = False,
    idempotency_key: Union[Unset, str] = UNSET,
) -> ApplicationOut:
    """Create Application

     Create a new application.

    Args:
        get_if_exists (Union[Unset, None, bool]): Get an existing application, or create a new one
            if doesn't exist. It's two separate functions in the libs.
        idempotency_key (Union[Unset, str]): The request's idempotency key
        json_body (ApplicationIn):

    Returns:
        ApplicationOut
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
        get_if_exists=get_if_exists,
        idempotency_key=idempotency_key,
    )


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    json_body: ApplicationIn,
    get_if_exists: Union[Unset, None, bool] = False,
    idempotency_key: Union[Unset, str] = UNSET,
) -> ApplicationOut:
    """Create Application

     Create a new application.

    Args:
        get_if_exists (Union[Unset, None, bool]): Get an existing application, or create a new one
            if doesn't exist. It's two separate functions in the libs.
        idempotency_key (Union[Unset, str]): The request's idempotency key
        json_body (ApplicationIn):

    Returns:
        ApplicationOut
    """

    kwargs = _get_kwargs(
        client=client,
        json_body=json_body,
        get_if_exists=get_if_exists,
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
    json_body: ApplicationIn,
    get_if_exists: Union[Unset, None, bool] = False,
    idempotency_key: Union[Unset, str] = UNSET,
) -> ApplicationOut:
    """Create Application

     Create a new application.

    Args:
        get_if_exists (Union[Unset, None, bool]): Get an existing application, or create a new one
            if doesn't exist. It's two separate functions in the libs.
        idempotency_key (Union[Unset, str]): The request's idempotency key
        json_body (ApplicationIn):

    Returns:
        ApplicationOut
    """

    return await asyncio_detailed(
        client=client,
        json_body=json_body,
        get_if_exists=get_if_exists,
        idempotency_key=idempotency_key,
    )

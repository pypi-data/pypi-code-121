import datetime
import random
from time import sleep
from typing import Any, Dict, List, Union

import httpx

from ...client import AuthenticatedClient
from ...models.http_error import HttpError
from ...models.http_validation_error import HTTPValidationError
from ...models.list_response_message_attempt_endpoint_out import ListResponseMessageAttemptEndpointOut
from ...models.message_status import MessageStatus
from ...types import UNSET, Unset


def _get_kwargs(
    app_id: str,
    msg_id: str,
    endpoint_id: str,
    *,
    client: AuthenticatedClient,
    iterator: Union[Unset, None, str] = UNSET,
    limit: Union[Unset, None, int] = 50,
    event_types: Union[Unset, None, List[str]] = UNSET,
    channel: Union[Unset, None, str] = UNSET,
    status: Union[Unset, None, MessageStatus] = UNSET,
    before: Union[Unset, None, datetime.datetime] = UNSET,
    after: Union[Unset, None, datetime.datetime] = UNSET,
    idempotency_key: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/api/v1/app/{app_id}/msg/{msg_id}/endpoint/{endpoint_id}/attempt/".format(
        client.base_url, app_id=app_id, msg_id=msg_id, endpoint_id=endpoint_id
    )

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    if not isinstance(idempotency_key, Unset):
        headers["idempotency-key"] = idempotency_key

    params: Dict[str, Any] = {}
    params["iterator"] = iterator

    params["limit"] = limit

    json_event_types: Union[Unset, None, List[str]] = UNSET
    if not isinstance(event_types, Unset):
        if event_types is None:
            json_event_types = None
        else:
            json_event_types = event_types

    params["event_types"] = json_event_types

    params["channel"] = channel

    json_status: Union[Unset, None, int] = UNSET
    if not isinstance(status, Unset):
        json_status = status.value if status else None

    params["status"] = json_status

    json_before: Union[Unset, None, str] = UNSET
    if not isinstance(before, Unset):
        json_before = before.isoformat() if before else None

    params["before"] = json_before

    json_after: Union[Unset, None, str] = UNSET
    if not isinstance(after, Unset):
        json_after = after.isoformat() if after else None

    params["after"] = json_after

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> ListResponseMessageAttemptEndpointOut:
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
    response_200 = ListResponseMessageAttemptEndpointOut.from_dict(response.json())

    return response_200


sleep_time = 0.05
num_retries = 3


def sync_detailed(
    app_id: str,
    msg_id: str,
    endpoint_id: str,
    *,
    client: AuthenticatedClient,
    iterator: Union[Unset, None, str] = UNSET,
    limit: Union[Unset, None, int] = 50,
    event_types: Union[Unset, None, List[str]] = UNSET,
    channel: Union[Unset, None, str] = UNSET,
    status: Union[Unset, None, MessageStatus] = UNSET,
    before: Union[Unset, None, datetime.datetime] = UNSET,
    after: Union[Unset, None, datetime.datetime] = UNSET,
    idempotency_key: Union[Unset, str] = UNSET,
) -> ListResponseMessageAttemptEndpointOut:
    """List Attempts For Endpoint

     DEPRECATED: please use list_attempts with endpoint_id as a query parameter instead.

    List the message attempts for a particular endpoint.

    Returning the endpoint.

    The `before` parameter lets you filter all items created before a certain date and is ignored if an
    iterator is passed.

    Args:
        app_id (str): The application's ID or UID Example: app_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        msg_id (str): The message's ID or eventID Example: msg_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        endpoint_id (str): The endpoint's ID or UID Example: ep_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        iterator (Union[Unset, None, str]):  Example: atmpt_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        limit (Union[Unset, None, int]):  Default: 50.
        event_types (Union[Unset, None, List[str]]):
        channel (Union[Unset, None, str]):  Example: project_1337.
        status (Union[Unset, None, MessageStatus]): The sending status of the message:
            - Success = 0
            - Pending = 1
            - Fail = 2
            - Sending = 3
        before (Union[Unset, None, datetime.datetime]):
        after (Union[Unset, None, datetime.datetime]):
        idempotency_key (Union[Unset, str]): The request's idempotency key

    Returns:
        ListResponseMessageAttemptEndpointOut
    """

    kwargs = _get_kwargs(
        app_id=app_id,
        msg_id=msg_id,
        endpoint_id=endpoint_id,
        client=client,
        iterator=iterator,
        limit=limit,
        event_types=event_types,
        channel=channel,
        status=status,
        before=before,
        after=after,
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
    app_id: str,
    msg_id: str,
    endpoint_id: str,
    *,
    client: AuthenticatedClient,
    iterator: Union[Unset, None, str] = UNSET,
    limit: Union[Unset, None, int] = 50,
    event_types: Union[Unset, None, List[str]] = UNSET,
    channel: Union[Unset, None, str] = UNSET,
    status: Union[Unset, None, MessageStatus] = UNSET,
    before: Union[Unset, None, datetime.datetime] = UNSET,
    after: Union[Unset, None, datetime.datetime] = UNSET,
    idempotency_key: Union[Unset, str] = UNSET,
) -> ListResponseMessageAttemptEndpointOut:
    """List Attempts For Endpoint

     DEPRECATED: please use list_attempts with endpoint_id as a query parameter instead.

    List the message attempts for a particular endpoint.

    Returning the endpoint.

    The `before` parameter lets you filter all items created before a certain date and is ignored if an
    iterator is passed.

    Args:
        app_id (str): The application's ID or UID Example: app_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        msg_id (str): The message's ID or eventID Example: msg_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        endpoint_id (str): The endpoint's ID or UID Example: ep_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        iterator (Union[Unset, None, str]):  Example: atmpt_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        limit (Union[Unset, None, int]):  Default: 50.
        event_types (Union[Unset, None, List[str]]):
        channel (Union[Unset, None, str]):  Example: project_1337.
        status (Union[Unset, None, MessageStatus]): The sending status of the message:
            - Success = 0
            - Pending = 1
            - Fail = 2
            - Sending = 3
        before (Union[Unset, None, datetime.datetime]):
        after (Union[Unset, None, datetime.datetime]):
        idempotency_key (Union[Unset, str]): The request's idempotency key

    Returns:
        ListResponseMessageAttemptEndpointOut
    """

    return sync_detailed(
        app_id=app_id,
        msg_id=msg_id,
        endpoint_id=endpoint_id,
        client=client,
        iterator=iterator,
        limit=limit,
        event_types=event_types,
        channel=channel,
        status=status,
        before=before,
        after=after,
        idempotency_key=idempotency_key,
    )


async def asyncio_detailed(
    app_id: str,
    msg_id: str,
    endpoint_id: str,
    *,
    client: AuthenticatedClient,
    iterator: Union[Unset, None, str] = UNSET,
    limit: Union[Unset, None, int] = 50,
    event_types: Union[Unset, None, List[str]] = UNSET,
    channel: Union[Unset, None, str] = UNSET,
    status: Union[Unset, None, MessageStatus] = UNSET,
    before: Union[Unset, None, datetime.datetime] = UNSET,
    after: Union[Unset, None, datetime.datetime] = UNSET,
    idempotency_key: Union[Unset, str] = UNSET,
) -> ListResponseMessageAttemptEndpointOut:
    """List Attempts For Endpoint

     DEPRECATED: please use list_attempts with endpoint_id as a query parameter instead.

    List the message attempts for a particular endpoint.

    Returning the endpoint.

    The `before` parameter lets you filter all items created before a certain date and is ignored if an
    iterator is passed.

    Args:
        app_id (str): The application's ID or UID Example: app_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        msg_id (str): The message's ID or eventID Example: msg_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        endpoint_id (str): The endpoint's ID or UID Example: ep_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        iterator (Union[Unset, None, str]):  Example: atmpt_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        limit (Union[Unset, None, int]):  Default: 50.
        event_types (Union[Unset, None, List[str]]):
        channel (Union[Unset, None, str]):  Example: project_1337.
        status (Union[Unset, None, MessageStatus]): The sending status of the message:
            - Success = 0
            - Pending = 1
            - Fail = 2
            - Sending = 3
        before (Union[Unset, None, datetime.datetime]):
        after (Union[Unset, None, datetime.datetime]):
        idempotency_key (Union[Unset, str]): The request's idempotency key

    Returns:
        ListResponseMessageAttemptEndpointOut
    """

    kwargs = _get_kwargs(
        app_id=app_id,
        msg_id=msg_id,
        endpoint_id=endpoint_id,
        client=client,
        iterator=iterator,
        limit=limit,
        event_types=event_types,
        channel=channel,
        status=status,
        before=before,
        after=after,
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
    app_id: str,
    msg_id: str,
    endpoint_id: str,
    *,
    client: AuthenticatedClient,
    iterator: Union[Unset, None, str] = UNSET,
    limit: Union[Unset, None, int] = 50,
    event_types: Union[Unset, None, List[str]] = UNSET,
    channel: Union[Unset, None, str] = UNSET,
    status: Union[Unset, None, MessageStatus] = UNSET,
    before: Union[Unset, None, datetime.datetime] = UNSET,
    after: Union[Unset, None, datetime.datetime] = UNSET,
    idempotency_key: Union[Unset, str] = UNSET,
) -> ListResponseMessageAttemptEndpointOut:
    """List Attempts For Endpoint

     DEPRECATED: please use list_attempts with endpoint_id as a query parameter instead.

    List the message attempts for a particular endpoint.

    Returning the endpoint.

    The `before` parameter lets you filter all items created before a certain date and is ignored if an
    iterator is passed.

    Args:
        app_id (str): The application's ID or UID Example: app_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        msg_id (str): The message's ID or eventID Example: msg_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        endpoint_id (str): The endpoint's ID or UID Example: ep_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        iterator (Union[Unset, None, str]):  Example: atmpt_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        limit (Union[Unset, None, int]):  Default: 50.
        event_types (Union[Unset, None, List[str]]):
        channel (Union[Unset, None, str]):  Example: project_1337.
        status (Union[Unset, None, MessageStatus]): The sending status of the message:
            - Success = 0
            - Pending = 1
            - Fail = 2
            - Sending = 3
        before (Union[Unset, None, datetime.datetime]):
        after (Union[Unset, None, datetime.datetime]):
        idempotency_key (Union[Unset, str]): The request's idempotency key

    Returns:
        ListResponseMessageAttemptEndpointOut
    """

    return await asyncio_detailed(
        app_id=app_id,
        msg_id=msg_id,
        endpoint_id=endpoint_id,
        client=client,
        iterator=iterator,
        limit=limit,
        event_types=event_types,
        channel=channel,
        status=status,
        before=before,
        after=after,
        idempotency_key=idempotency_key,
    )

import random
from time import sleep
from typing import Any, Dict, Union

import httpx

from ...client import AuthenticatedClient
from ...models.http_error import HttpError
from ...models.http_validation_error import HTTPValidationError
from ...models.message_in import MessageIn
from ...models.message_out import MessageOut
from ...types import UNSET, Unset


def _get_kwargs(
    app_id: str,
    *,
    client: AuthenticatedClient,
    json_body: MessageIn,
    with_content: Union[Unset, None, bool] = True,
    idempotency_key: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/api/v1/app/{app_id}/msg/".format(client.base_url, app_id=app_id)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    if not isinstance(idempotency_key, Unset):
        headers["idempotency-key"] = idempotency_key

    params: Dict[str, Any] = {}
    params["with_content"] = with_content

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


def _parse_response(*, response: httpx.Response) -> MessageOut:
    if response.status_code == 401:
        raise HttpError(response.json(), response.status_code)
    if response.status_code == 403:
        raise HttpError(response.json(), response.status_code)
    if response.status_code == 404:
        raise HttpError(response.json(), response.status_code)
    if response.status_code == 409:
        raise HttpError(response.json(), response.status_code)
    if response.status_code == 413:
        raise HttpError(response.json(), response.status_code)
    if response.status_code == 422:
        raise HTTPValidationError(response.json(), response.status_code)
    if response.status_code == 429:
        raise HttpError(response.json(), response.status_code)
    response_202 = MessageOut.from_dict(response.json())

    return response_202


sleep_time = 0.05
num_retries = 3


def sync_detailed(
    app_id: str,
    *,
    client: AuthenticatedClient,
    json_body: MessageIn,
    with_content: Union[Unset, None, bool] = True,
    idempotency_key: Union[Unset, str] = UNSET,
) -> MessageOut:
    """Create Message

     Creates a new message and dispatches it to all of the application's endpoints.

    The `eventId` is an optional custom unique ID. It's verified to be unique only up to a day, after
    that no verification will be made.
    If a message with the same `eventId` already exists for any application in your environment, a 409
    conflict error will be returned.

    The `eventType` indicates the type and schema of the event. All messages of a certain `eventType`
    are expected to have the same schema. Endpoints can choose to only listen to specific event types.
    Messages can also have `channels`, which similar to event types let endpoints filter by them. Unlike
    event types, messages can have multiple channels, and channels don't imply a specific message
    content or schema.

    The `payload' property is the webhook's body (the actual webhook message).

    Args:
        app_id (str): The application's ID or UID Example: app_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        with_content (Union[Unset, None, bool]):  Default: True.
        idempotency_key (Union[Unset, str]): The request's idempotency key
        json_body (MessageIn):

    Returns:
        MessageOut
    """

    kwargs = _get_kwargs(
        app_id=app_id,
        client=client,
        json_body=json_body,
        with_content=with_content,
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
    *,
    client: AuthenticatedClient,
    json_body: MessageIn,
    with_content: Union[Unset, None, bool] = True,
    idempotency_key: Union[Unset, str] = UNSET,
) -> MessageOut:
    """Create Message

     Creates a new message and dispatches it to all of the application's endpoints.

    The `eventId` is an optional custom unique ID. It's verified to be unique only up to a day, after
    that no verification will be made.
    If a message with the same `eventId` already exists for any application in your environment, a 409
    conflict error will be returned.

    The `eventType` indicates the type and schema of the event. All messages of a certain `eventType`
    are expected to have the same schema. Endpoints can choose to only listen to specific event types.
    Messages can also have `channels`, which similar to event types let endpoints filter by them. Unlike
    event types, messages can have multiple channels, and channels don't imply a specific message
    content or schema.

    The `payload' property is the webhook's body (the actual webhook message).

    Args:
        app_id (str): The application's ID or UID Example: app_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        with_content (Union[Unset, None, bool]):  Default: True.
        idempotency_key (Union[Unset, str]): The request's idempotency key
        json_body (MessageIn):

    Returns:
        MessageOut
    """

    return sync_detailed(
        app_id=app_id,
        client=client,
        json_body=json_body,
        with_content=with_content,
        idempotency_key=idempotency_key,
    )


async def asyncio_detailed(
    app_id: str,
    *,
    client: AuthenticatedClient,
    json_body: MessageIn,
    with_content: Union[Unset, None, bool] = True,
    idempotency_key: Union[Unset, str] = UNSET,
) -> MessageOut:
    """Create Message

     Creates a new message and dispatches it to all of the application's endpoints.

    The `eventId` is an optional custom unique ID. It's verified to be unique only up to a day, after
    that no verification will be made.
    If a message with the same `eventId` already exists for any application in your environment, a 409
    conflict error will be returned.

    The `eventType` indicates the type and schema of the event. All messages of a certain `eventType`
    are expected to have the same schema. Endpoints can choose to only listen to specific event types.
    Messages can also have `channels`, which similar to event types let endpoints filter by them. Unlike
    event types, messages can have multiple channels, and channels don't imply a specific message
    content or schema.

    The `payload' property is the webhook's body (the actual webhook message).

    Args:
        app_id (str): The application's ID or UID Example: app_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        with_content (Union[Unset, None, bool]):  Default: True.
        idempotency_key (Union[Unset, str]): The request's idempotency key
        json_body (MessageIn):

    Returns:
        MessageOut
    """

    kwargs = _get_kwargs(
        app_id=app_id,
        client=client,
        json_body=json_body,
        with_content=with_content,
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
    *,
    client: AuthenticatedClient,
    json_body: MessageIn,
    with_content: Union[Unset, None, bool] = True,
    idempotency_key: Union[Unset, str] = UNSET,
) -> MessageOut:
    """Create Message

     Creates a new message and dispatches it to all of the application's endpoints.

    The `eventId` is an optional custom unique ID. It's verified to be unique only up to a day, after
    that no verification will be made.
    If a message with the same `eventId` already exists for any application in your environment, a 409
    conflict error will be returned.

    The `eventType` indicates the type and schema of the event. All messages of a certain `eventType`
    are expected to have the same schema. Endpoints can choose to only listen to specific event types.
    Messages can also have `channels`, which similar to event types let endpoints filter by them. Unlike
    event types, messages can have multiple channels, and channels don't imply a specific message
    content or schema.

    The `payload' property is the webhook's body (the actual webhook message).

    Args:
        app_id (str): The application's ID or UID Example: app_1srOrx2ZWZBpBUvZwXKQmoEYga2.
        with_content (Union[Unset, None, bool]):  Default: True.
        idempotency_key (Union[Unset, str]): The request's idempotency key
        json_body (MessageIn):

    Returns:
        MessageOut
    """

    return await asyncio_detailed(
        app_id=app_id,
        client=client,
        json_body=json_body,
        with_content=with_content,
        idempotency_key=idempotency_key,
    )

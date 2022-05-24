from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.canvas import Canvas
from ...models.not_found_error import NotFoundError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    canvas_id: str,
) -> Dict[str, Any]:
    url = "{}/canvases/{canvas_id}".format(client.base_url, canvas_id=canvas_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Canvas, NotFoundError]]:
    if response.status_code == 200:
        response_200 = Canvas.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Canvas, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    canvas_id: str,
) -> Response[Union[Canvas, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        canvas_id=canvas_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    canvas_id: str,
) -> Optional[Union[Canvas, NotFoundError]]:
    """ Get the current state of the App Canvas, including user input elements. """

    return sync_detailed(
        client=client,
        canvas_id=canvas_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    canvas_id: str,
) -> Response[Union[Canvas, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        canvas_id=canvas_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    canvas_id: str,
) -> Optional[Union[Canvas, NotFoundError]]:
    """ Get the current state of the App Canvas, including user input elements. """

    return (
        await asyncio_detailed(
            client=client,
            canvas_id=canvas_id,
        )
    ).parsed

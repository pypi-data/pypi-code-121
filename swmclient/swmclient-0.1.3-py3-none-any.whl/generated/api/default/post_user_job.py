from io import BytesIO
from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.post_user_job_multipart_data import PostUserJobMultipartData
from ...types import File, Response


def _get_kwargs(
    *,
    client: Client,
    multipart_data: PostUserJobMultipartData,
) -> Dict[str, Any]:
    url = "{}/user/job".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    multipart_multipart_data = multipart_data.to_multipart()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "files": multipart_multipart_data,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Any, File]]:
    if response.status_code == 200:
        response_200 = File(payload=BytesIO(response.content))

        return response_200
    if response.status_code == 405:
        response_405 = None

        return response_405
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Any, File]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    multipart_data: PostUserJobMultipartData,
) -> Response[Union[Any, File]]:
    kwargs = _get_kwargs(
        client=client,
        multipart_data=multipart_data,
    )

    response = httpx.post(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    multipart_data: PostUserJobMultipartData,
) -> Optional[Union[Any, File]]:
    """A new job is submitted with a specific job script"""

    return sync_detailed(
        client=client,
        multipart_data=multipart_data,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    multipart_data: PostUserJobMultipartData,
) -> Response[Union[Any, File]]:
    kwargs = _get_kwargs(
        client=client,
        multipart_data=multipart_data,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    multipart_data: PostUserJobMultipartData,
) -> Optional[Union[Any, File]]:
    """A new job is submitted with a specific job script"""

    return (
        await asyncio_detailed(
            client=client,
            multipart_data=multipart_data,
        )
    ).parsed

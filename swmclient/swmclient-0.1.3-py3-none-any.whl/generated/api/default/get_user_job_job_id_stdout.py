from io import BytesIO
from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...types import File, Response


def _get_kwargs(
    job_id: str,
    *,
    client: Client,
) -> Dict[str, Any]:
    url = "{}/user/job/{jobId}/stdout".format(client.base_url, jobId=job_id)

    headers: Dict[str, Any] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    return {
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Any, File]]:
    if response.status_code == 200:
        response_200 = File(payload=BytesIO(response.content))

        return response_200
    if response.status_code == 400:
        response_400 = None

        return response_400
    if response.status_code == 404:
        response_404 = None

        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Any, File]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    job_id: str,
    *,
    client: Client,
) -> Response[Union[Any, File]]:
    kwargs = _get_kwargs(
        job_id=job_id,
        client=client,
    )

    response = httpx.get(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    job_id: str,
    *,
    client: Client,
) -> Optional[Union[Any, File]]:
    """Get job standard output content"""

    return sync_detailed(
        job_id=job_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    job_id: str,
    *,
    client: Client,
) -> Response[Union[Any, File]]:
    kwargs = _get_kwargs(
        job_id=job_id,
        client=client,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    job_id: str,
    *,
    client: Client,
) -> Optional[Union[Any, File]]:
    """Get job standard output content"""

    return (
        await asyncio_detailed(
            job_id=job_id,
            client=client,
        )
    ).parsed

from typing import Any, Dict, Optional, Union

import httpx

from ...client import Client
from ...models.analysis_step import AnalysisStep
from ...models.not_found_error import NotFoundError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    analysis_step_id: str,
) -> Dict[str, Any]:
    url = "{}/analysis_steps/{analysis_step_id}".format(client.base_url, analysis_step_id=analysis_step_id)

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[AnalysisStep, NotFoundError]]:
    if response.status_code == 200:
        response_200 = AnalysisStep.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = NotFoundError.from_dict(response.json())

        return response_404
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[AnalysisStep, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    analysis_step_id: str,
) -> Response[Union[AnalysisStep, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        analysis_step_id=analysis_step_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    analysis_step_id: str,
) -> Optional[Union[AnalysisStep, NotFoundError]]:
    """ Get an analysis step """

    return sync_detailed(
        client=client,
        analysis_step_id=analysis_step_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    analysis_step_id: str,
) -> Response[Union[AnalysisStep, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        analysis_step_id=analysis_step_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    analysis_step_id: str,
) -> Optional[Union[AnalysisStep, NotFoundError]]:
    """ Get an analysis step """

    return (
        await asyncio_detailed(
            client=client,
            analysis_step_id=analysis_step_id,
        )
    ).parsed

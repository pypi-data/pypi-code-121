from typing import Any, Dict, Union

import httpx

from ...client import Client
from ...models.url_conversion_request_body import URLConversionRequestBody
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: Client,
    multipart_data: URLConversionRequestBody,
    gotenberg_output_filename: Union[Unset, str] = UNSET,
    gotenberg_trace: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/forms/chromium/convert/url".format(client.base_url)

    headers: Dict[str, str] = client.get_headers()
    cookies: Dict[str, Any] = client.get_cookies()

    if not isinstance(gotenberg_output_filename, Unset):
        headers["Gotenberg-Output-Filename"] = gotenberg_output_filename

    if not isinstance(gotenberg_trace, Unset):
        headers["Gotenberg-Trace"] = gotenberg_trace

    multipart_multipart_data = multipart_data.to_multipart()

    return {
        "method": "post",
        "url": url,
        "headers": headers,
        "cookies": cookies,
        "timeout": client.get_timeout(),
        "files": multipart_multipart_data,
    }


def _build_response(*, response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=None,
    )


def sync_detailed(
    *,
    client: Client,
    multipart_data: URLConversionRequestBody,
    gotenberg_output_filename: Union[Unset, str] = UNSET,
    gotenberg_trace: Union[Unset, str] = UNSET,
) -> Response[Any]:
    """Convert the contents of a given URL to PDF

     Send a URL in your API request via the `url` form field Send a remote URL in your API request via
    the `remoteURL` parameter, and get the resulting PDF file. The API will fetch the given URL and
    render the page to PDF using the underlying headless Chrome instance. You can optionally include
    `header.html` and `footer.html` files as part of the request as well. See externalDocs for more
    details.

    Args:
        gotenberg_output_filename (Union[Unset, str]):
        gotenberg_trace (Union[Unset, str]):
        multipart_data (URLConversionRequestBody):

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        client=client,
        multipart_data=multipart_data,
        gotenberg_output_filename=gotenberg_output_filename,
        gotenberg_trace=gotenberg_trace,
    )

    response = httpx.request(
        verify=client.verify_ssl,
        **kwargs,
    )

    return _build_response(response=response)


async def asyncio_detailed(
    *,
    client: Client,
    multipart_data: URLConversionRequestBody,
    gotenberg_output_filename: Union[Unset, str] = UNSET,
    gotenberg_trace: Union[Unset, str] = UNSET,
) -> Response[Any]:
    """Convert the contents of a given URL to PDF

     Send a URL in your API request via the `url` form field Send a remote URL in your API request via
    the `remoteURL` parameter, and get the resulting PDF file. The API will fetch the given URL and
    render the page to PDF using the underlying headless Chrome instance. You can optionally include
    `header.html` and `footer.html` files as part of the request as well. See externalDocs for more
    details.

    Args:
        gotenberg_output_filename (Union[Unset, str]):
        gotenberg_trace (Union[Unset, str]):
        multipart_data (URLConversionRequestBody):

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        client=client,
        multipart_data=multipart_data,
        gotenberg_output_filename=gotenberg_output_filename,
        gotenberg_trace=gotenberg_trace,
    )

    async with httpx.AsyncClient(verify=client.verify_ssl) as _client:
        response = await _client.request(**kwargs)

    return _build_response(response=response)

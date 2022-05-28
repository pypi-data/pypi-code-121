from typing import Any, Dict, Union

import httpx

from ...client import Client
from ...models.office_conversion_request_body import OfficeConversionRequestBody
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    client: Client,
    multipart_data: OfficeConversionRequestBody,
    gotenberg_output_filename: Union[Unset, str] = UNSET,
    gotenberg_trace: Union[Unset, str] = UNSET,
) -> Dict[str, Any]:
    url = "{}/forms/libreoffice/convert".format(client.base_url)

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
    multipart_data: OfficeConversionRequestBody,
    gotenberg_output_filename: Union[Unset, str] = UNSET,
    gotenberg_trace: Union[Unset, str] = UNSET,
) -> Response[Any]:
    """Convert an Office document to PDF

     This route accepts multipart/form-data requests and files with the following extensions:
    .bib  .doc  .xml  .docx  .fodt  .html  .ltx  .txt  .odt  .ott  .pdb  .pdf  .psw  .rtf .sdw  .stw
    .sxw  .uot  .vor  .wps  .epub  .png  .bmp  .emf  .eps  .fodg  .gif  .jpg .met  .odd  .otg  .pbm
    .pct  .pgm  .ppm  .ras  .std  .svg  .svm  .swf  .sxd  .sxw .tiff  .xhtml  .xpm  .fodp  .potm  .pot
    .pptx  .pps  .ppt  .pwp  .sda  .sdd  .sti .sxi  .uop  .wmf  .csv  .dbf  .dif  .fods  .ods  .ots
    .pxl  .sdc  .slk  .stc  .sxc .uos  .xls  .xlt  .xlsx  .tif  .jpeg  .odp
    By default, if you send more than one file to convert, the route returns a ZIP archive of the
    resulting PDF files. However, you may prefer to merge all the PDF files into an individual PDF file.
    > **Attention:** The files will be merged alphabetically for the resulting PDF.
    You may also specify the page ranges to convert from the incoming Office documents. The expected
    format is the same as the one from the print options of LibreOffice, e.g. `1-1` or `1-4`.
    > **Attention:** if more than one document, the page ranges will be applied for each document.
    See externalDocs for more details.

    Args:
        gotenberg_output_filename (Union[Unset, str]):
        gotenberg_trace (Union[Unset, str]):
        multipart_data (OfficeConversionRequestBody):

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
    multipart_data: OfficeConversionRequestBody,
    gotenberg_output_filename: Union[Unset, str] = UNSET,
    gotenberg_trace: Union[Unset, str] = UNSET,
) -> Response[Any]:
    """Convert an Office document to PDF

     This route accepts multipart/form-data requests and files with the following extensions:
    .bib  .doc  .xml  .docx  .fodt  .html  .ltx  .txt  .odt  .ott  .pdb  .pdf  .psw  .rtf .sdw  .stw
    .sxw  .uot  .vor  .wps  .epub  .png  .bmp  .emf  .eps  .fodg  .gif  .jpg .met  .odd  .otg  .pbm
    .pct  .pgm  .ppm  .ras  .std  .svg  .svm  .swf  .sxd  .sxw .tiff  .xhtml  .xpm  .fodp  .potm  .pot
    .pptx  .pps  .ppt  .pwp  .sda  .sdd  .sti .sxi  .uop  .wmf  .csv  .dbf  .dif  .fods  .ods  .ots
    .pxl  .sdc  .slk  .stc  .sxc .uos  .xls  .xlt  .xlsx  .tif  .jpeg  .odp
    By default, if you send more than one file to convert, the route returns a ZIP archive of the
    resulting PDF files. However, you may prefer to merge all the PDF files into an individual PDF file.
    > **Attention:** The files will be merged alphabetically for the resulting PDF.
    You may also specify the page ranges to convert from the incoming Office documents. The expected
    format is the same as the one from the print options of LibreOffice, e.g. `1-1` or `1-4`.
    > **Attention:** if more than one document, the page ranges will be applied for each document.
    See externalDocs for more details.

    Args:
        gotenberg_output_filename (Union[Unset, str]):
        gotenberg_trace (Union[Unset, str]):
        multipart_data (OfficeConversionRequestBody):

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

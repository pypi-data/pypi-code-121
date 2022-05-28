import json
from io import BytesIO
from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, File, Unset

T = TypeVar("T", bound="MarkdownConversionRequestBody")


@attr.s(auto_attribs=True)
class MarkdownConversionRequestBody:
    """
    Attributes:
        files (List[File]):
        margin_top (Union[Unset, float]): Top margin for the page in inches. Default: 1.0.
        margin_bottom (Union[Unset, float]): Bottom margin for the page in inches. Default: 1.0.
        margin_left (Union[Unset, float]): Left margin for the page in inches. Default: 1.0.
        margin_right (Union[Unset, float]): Right margin for the page in inches. Default: 1.0.
        paper_width (Union[Unset, float]): Paper width to be used while rendering the PDF. The default page size is A4.
            Example: 8.27.
        paper_height (Union[Unset, float]): Paper height to be used while rendering the PDF. The default page size is
            A4. Example: 11.69.
        prefer_css_page_size (Union[Unset, bool]): Define whether to prefer page size as defined by CSS (default false)
        print_background (Union[Unset, bool]): Print the background graphics (default false)
        landscape (Union[Unset, bool]): The default orientation for rendering the page is "portrait" mode. By sending
            "landscape" parameter, you can ask the output to be landscape. Example: True.
        scale (Union[Unset, float]): The scale of the page rendering Default: 1.0. Example: 1.5.
        wait_delay (Union[Unset, str]): When the page relies on JavaScript for rendering, and you don't have access to
            the page's code, you may want to wait a certain amount of time to make sure Chromium has fully rendered the page
            you're trying to generate. Example: 5s.
        wait_window_status (Union[Unset, str]): If you have access to the page's code, you may set the window status and
            tell Gotenberg to wait for a specific value. For instance
               await promises()
               window.status = 'ready'
            Prefer this option over waitDelay. Example: done.
        extra_http_headers (Union[Unset, str]): HTTP headers to send by Chromium while loading the HTML document (JSON
            format)
        native_page_ranges (Union[Unset, str]): The page ranges to be converted to PDF for the incoming Office
            documents. Example: 1-4.
        pdf_format (Union[Unset, str]): The PDF format of the resulting PDF. Caution! You cannot use both
            nativePdfA1aFormat and pdfFormat form fields. Example: PDF/A-1a.
    """

    files: List[File]
    margin_top: Union[Unset, float] = 1.0
    margin_bottom: Union[Unset, float] = 1.0
    margin_left: Union[Unset, float] = 1.0
    margin_right: Union[Unset, float] = 1.0
    paper_width: Union[Unset, float] = UNSET
    paper_height: Union[Unset, float] = UNSET
    prefer_css_page_size: Union[Unset, bool] = False
    print_background: Union[Unset, bool] = False
    landscape: Union[Unset, bool] = False
    scale: Union[Unset, float] = 1.0
    wait_delay: Union[Unset, str] = UNSET
    wait_window_status: Union[Unset, str] = UNSET
    extra_http_headers: Union[Unset, str] = UNSET
    native_page_ranges: Union[Unset, str] = UNSET
    pdf_format: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_tuple()

            files.append(files_item)

        margin_top = self.margin_top
        margin_bottom = self.margin_bottom
        margin_left = self.margin_left
        margin_right = self.margin_right
        paper_width = self.paper_width
        paper_height = self.paper_height
        prefer_css_page_size = self.prefer_css_page_size
        print_background = self.print_background
        landscape = self.landscape
        scale = self.scale
        wait_delay = self.wait_delay
        wait_window_status = self.wait_window_status
        extra_http_headers = self.extra_http_headers
        native_page_ranges = self.native_page_ranges
        pdf_format = self.pdf_format

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "files": files,
            }
        )
        if margin_top is not UNSET:
            field_dict["marginTop"] = margin_top
        if margin_bottom is not UNSET:
            field_dict["marginBottom"] = margin_bottom
        if margin_left is not UNSET:
            field_dict["marginLeft"] = margin_left
        if margin_right is not UNSET:
            field_dict["marginRight"] = margin_right
        if paper_width is not UNSET:
            field_dict["paperWidth"] = paper_width
        if paper_height is not UNSET:
            field_dict["paperHeight"] = paper_height
        if prefer_css_page_size is not UNSET:
            field_dict["preferCssPageSize"] = prefer_css_page_size
        if print_background is not UNSET:
            field_dict["printBackground"] = print_background
        if landscape is not UNSET:
            field_dict["landscape"] = landscape
        if scale is not UNSET:
            field_dict["scale"] = scale
        if wait_delay is not UNSET:
            field_dict["waitDelay"] = wait_delay
        if wait_window_status is not UNSET:
            field_dict["waitWindowStatus"] = wait_window_status
        if extra_http_headers is not UNSET:
            field_dict["extraHttpHeaders"] = extra_http_headers
        if native_page_ranges is not UNSET:
            field_dict["nativePageRanges"] = native_page_ranges
        if pdf_format is not UNSET:
            field_dict["pdfFormat"] = pdf_format

        return field_dict

    def to_multipart(self) -> Dict[str, Any]:
        _temp_files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_tuple()

            _temp_files.append(files_item)
        files = (None, json.dumps(_temp_files).encode(), "application/json")

        margin_top = (
            self.margin_top
            if isinstance(self.margin_top, Unset)
            else (None, str(self.margin_top).encode(), "text/plain")
        )
        margin_bottom = (
            self.margin_bottom
            if isinstance(self.margin_bottom, Unset)
            else (None, str(self.margin_bottom).encode(), "text/plain")
        )
        margin_left = (
            self.margin_left
            if isinstance(self.margin_left, Unset)
            else (None, str(self.margin_left).encode(), "text/plain")
        )
        margin_right = (
            self.margin_right
            if isinstance(self.margin_right, Unset)
            else (None, str(self.margin_right).encode(), "text/plain")
        )
        paper_width = (
            self.paper_width
            if isinstance(self.paper_width, Unset)
            else (None, str(self.paper_width).encode(), "text/plain")
        )
        paper_height = (
            self.paper_height
            if isinstance(self.paper_height, Unset)
            else (None, str(self.paper_height).encode(), "text/plain")
        )
        prefer_css_page_size = (
            self.prefer_css_page_size
            if isinstance(self.prefer_css_page_size, Unset)
            else (None, str(self.prefer_css_page_size).encode(), "text/plain")
        )
        print_background = (
            self.print_background
            if isinstance(self.print_background, Unset)
            else (None, str(self.print_background).encode(), "text/plain")
        )
        landscape = (
            self.landscape if isinstance(self.landscape, Unset) else (None, str(self.landscape).encode(), "text/plain")
        )
        scale = self.scale if isinstance(self.scale, Unset) else (None, str(self.scale).encode(), "text/plain")
        wait_delay = (
            self.wait_delay
            if isinstance(self.wait_delay, Unset)
            else (None, str(self.wait_delay).encode(), "text/plain")
        )
        wait_window_status = (
            self.wait_window_status
            if isinstance(self.wait_window_status, Unset)
            else (None, str(self.wait_window_status).encode(), "text/plain")
        )
        extra_http_headers = (
            self.extra_http_headers
            if isinstance(self.extra_http_headers, Unset)
            else (None, str(self.extra_http_headers).encode(), "text/plain")
        )
        native_page_ranges = (
            self.native_page_ranges
            if isinstance(self.native_page_ranges, Unset)
            else (None, str(self.native_page_ranges).encode(), "text/plain")
        )
        pdf_format = (
            self.pdf_format
            if isinstance(self.pdf_format, Unset)
            else (None, str(self.pdf_format).encode(), "text/plain")
        )

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {key: (None, str(value).encode(), "text/plain") for key, value in self.additional_properties.items()}
        )
        field_dict.update(
            {
                "files": files,
            }
        )
        if margin_top is not UNSET:
            field_dict["marginTop"] = margin_top
        if margin_bottom is not UNSET:
            field_dict["marginBottom"] = margin_bottom
        if margin_left is not UNSET:
            field_dict["marginLeft"] = margin_left
        if margin_right is not UNSET:
            field_dict["marginRight"] = margin_right
        if paper_width is not UNSET:
            field_dict["paperWidth"] = paper_width
        if paper_height is not UNSET:
            field_dict["paperHeight"] = paper_height
        if prefer_css_page_size is not UNSET:
            field_dict["preferCssPageSize"] = prefer_css_page_size
        if print_background is not UNSET:
            field_dict["printBackground"] = print_background
        if landscape is not UNSET:
            field_dict["landscape"] = landscape
        if scale is not UNSET:
            field_dict["scale"] = scale
        if wait_delay is not UNSET:
            field_dict["waitDelay"] = wait_delay
        if wait_window_status is not UNSET:
            field_dict["waitWindowStatus"] = wait_window_status
        if extra_http_headers is not UNSET:
            field_dict["extraHttpHeaders"] = extra_http_headers
        if native_page_ranges is not UNSET:
            field_dict["nativePageRanges"] = native_page_ranges
        if pdf_format is not UNSET:
            field_dict["pdfFormat"] = pdf_format

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        files = []
        _files = d.pop("files")
        for files_item_data in _files:
            files_item = File(payload=BytesIO(files_item_data))

            files.append(files_item)

        margin_top = d.pop("marginTop", UNSET)

        margin_bottom = d.pop("marginBottom", UNSET)

        margin_left = d.pop("marginLeft", UNSET)

        margin_right = d.pop("marginRight", UNSET)

        paper_width = d.pop("paperWidth", UNSET)

        paper_height = d.pop("paperHeight", UNSET)

        prefer_css_page_size = d.pop("preferCssPageSize", UNSET)

        print_background = d.pop("printBackground", UNSET)

        landscape = d.pop("landscape", UNSET)

        scale = d.pop("scale", UNSET)

        wait_delay = d.pop("waitDelay", UNSET)

        wait_window_status = d.pop("waitWindowStatus", UNSET)

        extra_http_headers = d.pop("extraHttpHeaders", UNSET)

        native_page_ranges = d.pop("nativePageRanges", UNSET)

        pdf_format = d.pop("pdfFormat", UNSET)

        markdown_conversion_request_body = cls(
            files=files,
            margin_top=margin_top,
            margin_bottom=margin_bottom,
            margin_left=margin_left,
            margin_right=margin_right,
            paper_width=paper_width,
            paper_height=paper_height,
            prefer_css_page_size=prefer_css_page_size,
            print_background=print_background,
            landscape=landscape,
            scale=scale,
            wait_delay=wait_delay,
            wait_window_status=wait_window_status,
            extra_http_headers=extra_http_headers,
            native_page_ranges=native_page_ranges,
            pdf_format=pdf_format,
        )

        markdown_conversion_request_body.additional_properties = d
        return markdown_conversion_request_body

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

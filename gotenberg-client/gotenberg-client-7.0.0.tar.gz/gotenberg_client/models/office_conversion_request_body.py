import json
from io import BytesIO
from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, File, Unset

T = TypeVar("T", bound="OfficeConversionRequestBody")


@attr.s(auto_attribs=True)
class OfficeConversionRequestBody:
    """
    Attributes:
        files (List[File]):
        native_page_ranges (Union[Unset, str]): The page ranges to be converted to PDF for the incoming Office
            documents. **If there are multiple files sent to the API, this page range will apply to all of the documents**.
            Empty means all pages. Example: 1-4.
        native_pdf_a1_a_format (Union[Unset, bool]): Use unoconv to convert the resulting PDF to the 'PDF/A-1a' format.
            Caution! You cannot use both nativePdfA1aFormat and pdfFormat form fields.
        pdf_format (Union[Unset, str]): The PDF format of the resulting PDF. Caution! You cannot use both
            nativePdfA1aFormat and pdfFormat form fields. Example: PDF/A-1a.
        landscape (Union[Unset, bool]): The default orientation for rendering the page is "portrait" mode. By sending
            "landscape" parameter, you can ask the output to be landscape. Example: True.
        merge (Union[Unset, bool]): Merge all PDF files into an individual PDF file.
    """

    files: List[File]
    native_page_ranges: Union[Unset, str] = UNSET
    native_pdf_a1_a_format: Union[Unset, bool] = UNSET
    pdf_format: Union[Unset, str] = UNSET
    landscape: Union[Unset, bool] = False
    merge: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_tuple()

            files.append(files_item)

        native_page_ranges = self.native_page_ranges
        native_pdf_a1_a_format = self.native_pdf_a1_a_format
        pdf_format = self.pdf_format
        landscape = self.landscape
        merge = self.merge

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "files": files,
            }
        )
        if native_page_ranges is not UNSET:
            field_dict["nativePageRanges"] = native_page_ranges
        if native_pdf_a1_a_format is not UNSET:
            field_dict["nativePdfA1aFormat"] = native_pdf_a1_a_format
        if pdf_format is not UNSET:
            field_dict["pdfFormat"] = pdf_format
        if landscape is not UNSET:
            field_dict["landscape"] = landscape
        if merge is not UNSET:
            field_dict["merge"] = merge

        return field_dict

    def to_multipart(self) -> Dict[str, Any]:
        _temp_files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_tuple()

            _temp_files.append(files_item)
        files = (None, json.dumps(_temp_files).encode(), "application/json")

        native_page_ranges = (
            self.native_page_ranges
            if isinstance(self.native_page_ranges, Unset)
            else (None, str(self.native_page_ranges).encode(), "text/plain")
        )
        native_pdf_a1_a_format = (
            self.native_pdf_a1_a_format
            if isinstance(self.native_pdf_a1_a_format, Unset)
            else (None, str(self.native_pdf_a1_a_format).encode(), "text/plain")
        )
        pdf_format = (
            self.pdf_format
            if isinstance(self.pdf_format, Unset)
            else (None, str(self.pdf_format).encode(), "text/plain")
        )
        landscape = (
            self.landscape if isinstance(self.landscape, Unset) else (None, str(self.landscape).encode(), "text/plain")
        )
        merge = self.merge if isinstance(self.merge, Unset) else (None, str(self.merge).encode(), "text/plain")

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {key: (None, str(value).encode(), "text/plain") for key, value in self.additional_properties.items()}
        )
        field_dict.update(
            {
                "files": files,
            }
        )
        if native_page_ranges is not UNSET:
            field_dict["nativePageRanges"] = native_page_ranges
        if native_pdf_a1_a_format is not UNSET:
            field_dict["nativePdfA1aFormat"] = native_pdf_a1_a_format
        if pdf_format is not UNSET:
            field_dict["pdfFormat"] = pdf_format
        if landscape is not UNSET:
            field_dict["landscape"] = landscape
        if merge is not UNSET:
            field_dict["merge"] = merge

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        files = []
        _files = d.pop("files")
        for files_item_data in _files:
            files_item = File(payload=BytesIO(files_item_data))

            files.append(files_item)

        native_page_ranges = d.pop("nativePageRanges", UNSET)

        native_pdf_a1_a_format = d.pop("nativePdfA1aFormat", UNSET)

        pdf_format = d.pop("pdfFormat", UNSET)

        landscape = d.pop("landscape", UNSET)

        merge = d.pop("merge", UNSET)

        office_conversion_request_body = cls(
            files=files,
            native_page_ranges=native_page_ranges,
            native_pdf_a1_a_format=native_pdf_a1_a_format,
            pdf_format=pdf_format,
            landscape=landscape,
            merge=merge,
        )

        office_conversion_request_body.additional_properties = d
        return office_conversion_request_body

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

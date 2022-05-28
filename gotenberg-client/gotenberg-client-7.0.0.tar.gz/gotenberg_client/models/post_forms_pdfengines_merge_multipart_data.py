import json
from io import BytesIO
from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, File, Unset

T = TypeVar("T", bound="PostFormsPdfenginesMergeMultipartData")


@attr.s(auto_attribs=True)
class PostFormsPdfenginesMergeMultipartData:
    """
    Attributes:
        files (List[File]):
        pdf_format (Union[Unset, str]): The PDF format of the resulting PDF Example: PDF/A-1a.
    """

    files: List[File]
    pdf_format: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_tuple()

            files.append(files_item)

        pdf_format = self.pdf_format

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "files": files,
            }
        )
        if pdf_format is not UNSET:
            field_dict["pdfFormat"] = pdf_format

        return field_dict

    def to_multipart(self) -> Dict[str, Any]:
        _temp_files = []
        for files_item_data in self.files:
            files_item = files_item_data.to_tuple()

            _temp_files.append(files_item)
        files = (None, json.dumps(_temp_files).encode(), "application/json")

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

        pdf_format = d.pop("pdfFormat", UNSET)

        post_forms_pdfengines_merge_multipart_data = cls(
            files=files,
            pdf_format=pdf_format,
        )

        post_forms_pdfengines_merge_multipart_data.additional_properties = d
        return post_forms_pdfengines_merge_multipart_data

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

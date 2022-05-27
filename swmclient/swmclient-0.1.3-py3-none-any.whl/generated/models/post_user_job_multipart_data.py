from io import BytesIO
from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, File, FileJsonType, Unset

T = TypeVar("T", bound="PostUserJobMultipartData")


@attr.s(auto_attribs=True)
class PostUserJobMultipartData:
    """ """

    script_content: Union[Unset, File] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        script_content: Union[Unset, FileJsonType] = UNSET
        if not isinstance(self.script_content, Unset):
            script_content = self.script_content.to_tuple()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if script_content is not UNSET:
            field_dict["script_content"] = script_content

        return field_dict

    def to_multipart(self) -> Dict[str, Any]:
        script_content: Union[Unset, FileJsonType] = UNSET
        if not isinstance(self.script_content, Unset):
            script_content = self.script_content.to_tuple()

        field_dict: Dict[str, Any] = {}
        field_dict.update({key: (None, str(value), "text/plain") for key, value in self.additional_properties.items()})
        field_dict.update({})
        if script_content is not UNSET:
            field_dict["script_content"] = script_content

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        _script_content = d.pop("script_content", UNSET)
        script_content: Union[Unset, File]
        if isinstance(_script_content, Unset):
            script_content = UNSET
        else:
            script_content = File(payload=BytesIO(_script_content))

        post_user_job_multipart_data = cls(
            script_content=script_content,
        )

        post_user_job_multipart_data.additional_properties = d
        return post_user_job_multipart_data

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

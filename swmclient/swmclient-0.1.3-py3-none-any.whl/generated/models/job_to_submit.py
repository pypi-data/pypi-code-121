from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="JobToSubmit")


@attr.s(auto_attribs=True)
class JobToSubmit:
    """A new job specification to submit"""

    name: Union[Unset, str] = UNSET
    script: Union[Unset, str] = UNSET
    nodes_number: Union[Unset, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        script = self.script
        nodes_number = self.nodes_number

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if script is not UNSET:
            field_dict["script"] = script
        if nodes_number is not UNSET:
            field_dict["nodes_number"] = nodes_number

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name", UNSET)

        script = d.pop("script", UNSET)

        nodes_number = d.pop("nodes_number", UNSET)

        job_to_submit = cls(
            name=name,
            script=script,
            nodes_number=nodes_number,
        )

        job_to_submit.additional_properties = d
        return job_to_submit

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

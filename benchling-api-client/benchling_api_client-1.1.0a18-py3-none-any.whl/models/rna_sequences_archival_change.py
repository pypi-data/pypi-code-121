from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="RnaSequencesArchivalChange")


@attr.s(auto_attribs=True, repr=False)
class RnaSequencesArchivalChange:
    """IDs of all RNA Sequences that were archived or unarchived, grouped by resource type."""

    _rna_sequence_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("rna_sequence_ids={}".format(repr(self._rna_sequence_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RnaSequencesArchivalChange({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        rna_sequence_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._rna_sequence_ids, Unset):
            rna_sequence_ids = self._rna_sequence_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if rna_sequence_ids is not UNSET:
            field_dict["rnaSequenceIds"] = rna_sequence_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_rna_sequence_ids() -> Union[Unset, List[str]]:
            rna_sequence_ids = cast(List[str], d.pop("rnaSequenceIds"))

            return rna_sequence_ids

        rna_sequence_ids = (
            get_rna_sequence_ids() if "rnaSequenceIds" in d else cast(Union[Unset, List[str]], UNSET)
        )

        rna_sequences_archival_change = cls(
            rna_sequence_ids=rna_sequence_ids,
        )

        rna_sequences_archival_change.additional_properties = d
        return rna_sequences_archival_change

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

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def rna_sequence_ids(self) -> List[str]:
        if isinstance(self._rna_sequence_ids, Unset):
            raise NotPresentError(self, "rna_sequence_ids")
        return self._rna_sequence_ids

    @rna_sequence_ids.setter
    def rna_sequence_ids(self, value: List[str]) -> None:
        self._rna_sequence_ids = value

    @rna_sequence_ids.deleter
    def rna_sequence_ids(self) -> None:
        self._rna_sequence_ids = UNSET

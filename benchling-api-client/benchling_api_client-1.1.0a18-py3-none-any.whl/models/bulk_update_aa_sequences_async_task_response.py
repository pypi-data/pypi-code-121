from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.aa_sequence import AaSequence
from ..types import UNSET, Unset

T = TypeVar("T", bound="BulkUpdateAaSequencesAsyncTaskResponse")


@attr.s(auto_attribs=True, repr=False)
class BulkUpdateAaSequencesAsyncTaskResponse:
    """  """

    _as_sequences: Union[Unset, List[AaSequence]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("as_sequences={}".format(repr(self._as_sequences)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BulkUpdateAaSequencesAsyncTaskResponse({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        as_sequences: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._as_sequences, Unset):
            as_sequences = []
            for as_sequences_item_data in self._as_sequences:
                as_sequences_item = as_sequences_item_data.to_dict()

                as_sequences.append(as_sequences_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if as_sequences is not UNSET:
            field_dict["AsSequences"] = as_sequences

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_as_sequences() -> Union[Unset, List[AaSequence]]:
            as_sequences = []
            _as_sequences = d.pop("AsSequences")
            for as_sequences_item_data in _as_sequences or []:
                as_sequences_item = AaSequence.from_dict(as_sequences_item_data)

                as_sequences.append(as_sequences_item)

            return as_sequences

        as_sequences = (
            get_as_sequences() if "AsSequences" in d else cast(Union[Unset, List[AaSequence]], UNSET)
        )

        bulk_update_aa_sequences_async_task_response = cls(
            as_sequences=as_sequences,
        )

        bulk_update_aa_sequences_async_task_response.additional_properties = d
        return bulk_update_aa_sequences_async_task_response

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
    def as_sequences(self) -> List[AaSequence]:
        if isinstance(self._as_sequences, Unset):
            raise NotPresentError(self, "as_sequences")
        return self._as_sequences

    @as_sequences.setter
    def as_sequences(self, value: List[AaSequence]) -> None:
        self._as_sequences = value

    @as_sequences.deleter
    def as_sequences(self) -> None:
        self._as_sequences = UNSET

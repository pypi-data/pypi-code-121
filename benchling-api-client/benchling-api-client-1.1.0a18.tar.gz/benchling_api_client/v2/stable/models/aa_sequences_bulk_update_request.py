from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.aa_sequence_bulk_update import AaSequenceBulkUpdate
from ..types import UNSET, Unset

T = TypeVar("T", bound="AaSequencesBulkUpdateRequest")


@attr.s(auto_attribs=True, repr=False)
class AaSequencesBulkUpdateRequest:
    """  """

    _aa_sequences: Union[Unset, List[AaSequenceBulkUpdate]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("aa_sequences={}".format(repr(self._aa_sequences)))
        return "AaSequencesBulkUpdateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        aa_sequences: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._aa_sequences, Unset):
            aa_sequences = []
            for aa_sequences_item_data in self._aa_sequences:
                aa_sequences_item = aa_sequences_item_data.to_dict()

                aa_sequences.append(aa_sequences_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if aa_sequences is not UNSET:
            field_dict["aaSequences"] = aa_sequences

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_aa_sequences() -> Union[Unset, List[AaSequenceBulkUpdate]]:
            aa_sequences = []
            _aa_sequences = d.pop("aaSequences")
            for aa_sequences_item_data in _aa_sequences or []:
                aa_sequences_item = AaSequenceBulkUpdate.from_dict(aa_sequences_item_data)

                aa_sequences.append(aa_sequences_item)

            return aa_sequences

        aa_sequences = (
            get_aa_sequences()
            if "aaSequences" in d
            else cast(Union[Unset, List[AaSequenceBulkUpdate]], UNSET)
        )

        aa_sequences_bulk_update_request = cls(
            aa_sequences=aa_sequences,
        )

        return aa_sequences_bulk_update_request

    @property
    def aa_sequences(self) -> List[AaSequenceBulkUpdate]:
        if isinstance(self._aa_sequences, Unset):
            raise NotPresentError(self, "aa_sequences")
        return self._aa_sequences

    @aa_sequences.setter
    def aa_sequences(self, value: List[AaSequenceBulkUpdate]) -> None:
        self._aa_sequences = value

    @aa_sequences.deleter
    def aa_sequences(self) -> None:
        self._aa_sequences = UNSET

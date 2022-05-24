from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.dna_sequence_bulk_upsert_request import DnaSequenceBulkUpsertRequest
from ..types import UNSET, Unset

T = TypeVar("T", bound="DnaSequencesBulkUpsertRequest")


@attr.s(auto_attribs=True, repr=False)
class DnaSequencesBulkUpsertRequest:
    """  """

    _dna_sequences: List[DnaSequenceBulkUpsertRequest]

    def __repr__(self):
        fields = []
        fields.append("dna_sequences={}".format(repr(self._dna_sequences)))
        return "DnaSequencesBulkUpsertRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dna_sequences = []
        for dna_sequences_item_data in self._dna_sequences:
            dna_sequences_item = dna_sequences_item_data.to_dict()

            dna_sequences.append(dna_sequences_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "dnaSequences": dna_sequences,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_dna_sequences() -> List[DnaSequenceBulkUpsertRequest]:
            dna_sequences = []
            _dna_sequences = d.pop("dnaSequences")
            for dna_sequences_item_data in _dna_sequences:
                dna_sequences_item = DnaSequenceBulkUpsertRequest.from_dict(dna_sequences_item_data)

                dna_sequences.append(dna_sequences_item)

            return dna_sequences

        dna_sequences = (
            get_dna_sequences() if "dnaSequences" in d else cast(List[DnaSequenceBulkUpsertRequest], UNSET)
        )

        dna_sequences_bulk_upsert_request = cls(
            dna_sequences=dna_sequences,
        )

        return dna_sequences_bulk_upsert_request

    @property
    def dna_sequences(self) -> List[DnaSequenceBulkUpsertRequest]:
        if isinstance(self._dna_sequences, Unset):
            raise NotPresentError(self, "dna_sequences")
        return self._dna_sequences

    @dna_sequences.setter
    def dna_sequences(self, value: List[DnaSequenceBulkUpsertRequest]) -> None:
        self._dna_sequences = value

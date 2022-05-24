from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="RnaSequencesUnarchive")


@attr.s(auto_attribs=True, repr=False)
class RnaSequencesUnarchive:
    """The request body for unarchiving RNA sequences."""

    _rna_sequence_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("rna_sequence_ids={}".format(repr(self._rna_sequence_ids)))
        return "RnaSequencesUnarchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        rna_sequence_ids = self._rna_sequence_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "rnaSequenceIds": rna_sequence_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_rna_sequence_ids() -> List[str]:
            rna_sequence_ids = cast(List[str], d.pop("rnaSequenceIds"))

            return rna_sequence_ids

        rna_sequence_ids = get_rna_sequence_ids() if "rnaSequenceIds" in d else cast(List[str], UNSET)

        rna_sequences_unarchive = cls(
            rna_sequence_ids=rna_sequence_ids,
        )

        return rna_sequences_unarchive

    @property
    def rna_sequence_ids(self) -> List[str]:
        if isinstance(self._rna_sequence_ids, Unset):
            raise NotPresentError(self, "rna_sequence_ids")
        return self._rna_sequence_ids

    @rna_sequence_ids.setter
    def rna_sequence_ids(self, value: List[str]) -> None:
        self._rna_sequence_ids = value

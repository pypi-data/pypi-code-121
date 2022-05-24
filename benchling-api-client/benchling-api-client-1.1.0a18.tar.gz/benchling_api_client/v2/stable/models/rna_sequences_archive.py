from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.entity_archive_reason import EntityArchiveReason
from ..types import UNSET, Unset

T = TypeVar("T", bound="RnaSequencesArchive")


@attr.s(auto_attribs=True, repr=False)
class RnaSequencesArchive:
    """The request body for archiving RNA sequences."""

    _reason: EntityArchiveReason
    _rna_sequence_ids: List[str]

    def __repr__(self):
        fields = []
        fields.append("reason={}".format(repr(self._reason)))
        fields.append("rna_sequence_ids={}".format(repr(self._rna_sequence_ids)))
        return "RnaSequencesArchive({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        reason = self._reason.value

        rna_sequence_ids = self._rna_sequence_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "reason": reason,
                "rnaSequenceIds": rna_sequence_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_reason() -> EntityArchiveReason:
            _reason = d.pop("reason")
            try:
                reason = EntityArchiveReason(_reason)
            except ValueError:
                reason = EntityArchiveReason.of_unknown(_reason)

            return reason

        reason = get_reason() if "reason" in d else cast(EntityArchiveReason, UNSET)

        def get_rna_sequence_ids() -> List[str]:
            rna_sequence_ids = cast(List[str], d.pop("rnaSequenceIds"))

            return rna_sequence_ids

        rna_sequence_ids = get_rna_sequence_ids() if "rnaSequenceIds" in d else cast(List[str], UNSET)

        rna_sequences_archive = cls(
            reason=reason,
            rna_sequence_ids=rna_sequence_ids,
        )

        return rna_sequences_archive

    @property
    def reason(self) -> EntityArchiveReason:
        """The reason for archiving the provided entities. Accepted reasons may differ based on tenant configuration."""
        if isinstance(self._reason, Unset):
            raise NotPresentError(self, "reason")
        return self._reason

    @reason.setter
    def reason(self, value: EntityArchiveReason) -> None:
        self._reason = value

    @property
    def rna_sequence_ids(self) -> List[str]:
        if isinstance(self._rna_sequence_ids, Unset):
            raise NotPresentError(self, "rna_sequence_ids")
        return self._rna_sequence_ids

    @rna_sequence_ids.setter
    def rna_sequence_ids(self, value: List[str]) -> None:
        self._rna_sequence_ids = value

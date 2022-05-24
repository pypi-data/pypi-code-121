from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.oligo_bulk_upsert_request import OligoBulkUpsertRequest
from ..types import UNSET, Unset

T = TypeVar("T", bound="DnaOligosBulkUpsertRequest")


@attr.s(auto_attribs=True, repr=False)
class DnaOligosBulkUpsertRequest:
    """  """

    _dna_oligos: List[OligoBulkUpsertRequest]

    def __repr__(self):
        fields = []
        fields.append("dna_oligos={}".format(repr(self._dna_oligos)))
        return "DnaOligosBulkUpsertRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dna_oligos = []
        for dna_oligos_item_data in self._dna_oligos:
            dna_oligos_item = dna_oligos_item_data.to_dict()

            dna_oligos.append(dna_oligos_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "dnaOligos": dna_oligos,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_dna_oligos() -> List[OligoBulkUpsertRequest]:
            dna_oligos = []
            _dna_oligos = d.pop("dnaOligos")
            for dna_oligos_item_data in _dna_oligos:
                dna_oligos_item = OligoBulkUpsertRequest.from_dict(dna_oligos_item_data)

                dna_oligos.append(dna_oligos_item)

            return dna_oligos

        dna_oligos = get_dna_oligos() if "dnaOligos" in d else cast(List[OligoBulkUpsertRequest], UNSET)

        dna_oligos_bulk_upsert_request = cls(
            dna_oligos=dna_oligos,
        )

        return dna_oligos_bulk_upsert_request

    @property
    def dna_oligos(self) -> List[OligoBulkUpsertRequest]:
        if isinstance(self._dna_oligos, Unset):
            raise NotPresentError(self, "dna_oligos")
        return self._dna_oligos

    @dna_oligos.setter
    def dna_oligos(self, value: List[OligoBulkUpsertRequest]) -> None:
        self._dna_oligos = value

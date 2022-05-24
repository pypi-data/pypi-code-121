from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..models.oligo_bulk_upsert_request import OligoBulkUpsertRequest
from ..types import UNSET, Unset

T = TypeVar("T", bound="RnaOligosBulkUpsertRequest")


@attr.s(auto_attribs=True, repr=False)
class RnaOligosBulkUpsertRequest:
    """  """

    _rna_oligos: List[OligoBulkUpsertRequest]

    def __repr__(self):
        fields = []
        fields.append("rna_oligos={}".format(repr(self._rna_oligos)))
        return "RnaOligosBulkUpsertRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        rna_oligos = []
        for rna_oligos_item_data in self._rna_oligos:
            rna_oligos_item = rna_oligos_item_data.to_dict()

            rna_oligos.append(rna_oligos_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "rnaOligos": rna_oligos,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_rna_oligos() -> List[OligoBulkUpsertRequest]:
            rna_oligos = []
            _rna_oligos = d.pop("rnaOligos")
            for rna_oligos_item_data in _rna_oligos:
                rna_oligos_item = OligoBulkUpsertRequest.from_dict(rna_oligos_item_data)

                rna_oligos.append(rna_oligos_item)

            return rna_oligos

        rna_oligos = get_rna_oligos() if "rnaOligos" in d else cast(List[OligoBulkUpsertRequest], UNSET)

        rna_oligos_bulk_upsert_request = cls(
            rna_oligos=rna_oligos,
        )

        return rna_oligos_bulk_upsert_request

    @property
    def rna_oligos(self) -> List[OligoBulkUpsertRequest]:
        if isinstance(self._rna_oligos, Unset):
            raise NotPresentError(self, "rna_oligos")
        return self._rna_oligos

    @rna_oligos.setter
    def rna_oligos(self, value: List[OligoBulkUpsertRequest]) -> None:
        self._rna_oligos = value

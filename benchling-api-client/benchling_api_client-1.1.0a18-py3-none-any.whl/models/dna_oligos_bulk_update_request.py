from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.dna_oligo_bulk_update import DnaOligoBulkUpdate
from ..types import UNSET, Unset

T = TypeVar("T", bound="DnaOligosBulkUpdateRequest")


@attr.s(auto_attribs=True, repr=False)
class DnaOligosBulkUpdateRequest:
    """  """

    _dna_oligos: Union[Unset, List[DnaOligoBulkUpdate]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("dna_oligos={}".format(repr(self._dna_oligos)))
        return "DnaOligosBulkUpdateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        dna_oligos: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._dna_oligos, Unset):
            dna_oligos = []
            for dna_oligos_item_data in self._dna_oligos:
                dna_oligos_item = dna_oligos_item_data.to_dict()

                dna_oligos.append(dna_oligos_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if dna_oligos is not UNSET:
            field_dict["dnaOligos"] = dna_oligos

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_dna_oligos() -> Union[Unset, List[DnaOligoBulkUpdate]]:
            dna_oligos = []
            _dna_oligos = d.pop("dnaOligos")
            for dna_oligos_item_data in _dna_oligos or []:
                dna_oligos_item = DnaOligoBulkUpdate.from_dict(dna_oligos_item_data)

                dna_oligos.append(dna_oligos_item)

            return dna_oligos

        dna_oligos = (
            get_dna_oligos() if "dnaOligos" in d else cast(Union[Unset, List[DnaOligoBulkUpdate]], UNSET)
        )

        dna_oligos_bulk_update_request = cls(
            dna_oligos=dna_oligos,
        )

        return dna_oligos_bulk_update_request

    @property
    def dna_oligos(self) -> List[DnaOligoBulkUpdate]:
        if isinstance(self._dna_oligos, Unset):
            raise NotPresentError(self, "dna_oligos")
        return self._dna_oligos

    @dna_oligos.setter
    def dna_oligos(self, value: List[DnaOligoBulkUpdate]) -> None:
        self._dna_oligos = value

    @dna_oligos.deleter
    def dna_oligos(self) -> None:
        self._dna_oligos = UNSET

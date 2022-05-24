from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.rna_oligo_bulk_update import RnaOligoBulkUpdate
from ..types import UNSET, Unset

T = TypeVar("T", bound="RnaOligosBulkUpdateRequest")


@attr.s(auto_attribs=True, repr=False)
class RnaOligosBulkUpdateRequest:
    """  """

    _rna_oligos: Union[Unset, List[RnaOligoBulkUpdate]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("rna_oligos={}".format(repr(self._rna_oligos)))
        return "RnaOligosBulkUpdateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        rna_oligos: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._rna_oligos, Unset):
            rna_oligos = []
            for rna_oligos_item_data in self._rna_oligos:
                rna_oligos_item = rna_oligos_item_data.to_dict()

                rna_oligos.append(rna_oligos_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if rna_oligos is not UNSET:
            field_dict["rnaOligos"] = rna_oligos

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_rna_oligos() -> Union[Unset, List[RnaOligoBulkUpdate]]:
            rna_oligos = []
            _rna_oligos = d.pop("rnaOligos")
            for rna_oligos_item_data in _rna_oligos or []:
                rna_oligos_item = RnaOligoBulkUpdate.from_dict(rna_oligos_item_data)

                rna_oligos.append(rna_oligos_item)

            return rna_oligos

        rna_oligos = (
            get_rna_oligos() if "rnaOligos" in d else cast(Union[Unset, List[RnaOligoBulkUpdate]], UNSET)
        )

        rna_oligos_bulk_update_request = cls(
            rna_oligos=rna_oligos,
        )

        return rna_oligos_bulk_update_request

    @property
    def rna_oligos(self) -> List[RnaOligoBulkUpdate]:
        if isinstance(self._rna_oligos, Unset):
            raise NotPresentError(self, "rna_oligos")
        return self._rna_oligos

    @rna_oligos.setter
    def rna_oligos(self, value: List[RnaOligoBulkUpdate]) -> None:
        self._rna_oligos = value

    @rna_oligos.deleter
    def rna_oligos(self) -> None:
        self._rna_oligos = UNSET

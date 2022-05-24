from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.initial_table import InitialTable
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntryCreateInitialTablesArray")


@attr.s(auto_attribs=True, repr=False)
class EntryCreateInitialTablesArray:
    """  """

    _initial_tables: Union[Unset, List[InitialTable]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("initial_tables={}".format(repr(self._initial_tables)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EntryCreateInitialTablesArray({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        initial_tables: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._initial_tables, Unset):
            initial_tables = []
            for initial_tables_item_data in self._initial_tables:
                initial_tables_item = initial_tables_item_data.to_dict()

                initial_tables.append(initial_tables_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if initial_tables is not UNSET:
            field_dict["initialTables"] = initial_tables

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_initial_tables() -> Union[Unset, List[InitialTable]]:
            initial_tables = []
            _initial_tables = d.pop("initialTables")
            for initial_tables_item_data in _initial_tables or []:
                initial_tables_item = InitialTable.from_dict(initial_tables_item_data)

                initial_tables.append(initial_tables_item)

            return initial_tables

        initial_tables = (
            get_initial_tables() if "initialTables" in d else cast(Union[Unset, List[InitialTable]], UNSET)
        )

        entry_create_initial_tables_array = cls(
            initial_tables=initial_tables,
        )

        entry_create_initial_tables_array.additional_properties = d
        return entry_create_initial_tables_array

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
    def initial_tables(self) -> List[InitialTable]:
        if isinstance(self._initial_tables, Unset):
            raise NotPresentError(self, "initial_tables")
        return self._initial_tables

    @initial_tables.setter
    def initial_tables(self, value: List[InitialTable]) -> None:
        self._initial_tables = value

    @initial_tables.deleter
    def initial_tables(self) -> None:
        self._initial_tables = UNSET

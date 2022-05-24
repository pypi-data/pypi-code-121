from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.structured_table_column_info import StructuredTableColumnInfo
from ..types import UNSET, Unset

T = TypeVar("T", bound="StructuredTableApiIdentifiers")


@attr.s(auto_attribs=True, repr=False)
class StructuredTableApiIdentifiers:
    """  """

    _api_id: Union[Unset, str] = UNSET
    _columns: Union[Unset, List[StructuredTableColumnInfo]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("api_id={}".format(repr(self._api_id)))
        fields.append("columns={}".format(repr(self._columns)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "StructuredTableApiIdentifiers({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        api_id = self._api_id
        columns: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._columns, Unset):
            columns = []
            for columns_item_data in self._columns:
                columns_item = columns_item_data.to_dict()

                columns.append(columns_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if api_id is not UNSET:
            field_dict["apiId"] = api_id
        if columns is not UNSET:
            field_dict["columns"] = columns

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_api_id() -> Union[Unset, str]:
            api_id = d.pop("apiId")
            return api_id

        api_id = get_api_id() if "apiId" in d else cast(Union[Unset, str], UNSET)

        def get_columns() -> Union[Unset, List[StructuredTableColumnInfo]]:
            columns = []
            _columns = d.pop("columns")
            for columns_item_data in _columns or []:
                columns_item = StructuredTableColumnInfo.from_dict(columns_item_data)

                columns.append(columns_item)

            return columns

        columns = (
            get_columns() if "columns" in d else cast(Union[Unset, List[StructuredTableColumnInfo]], UNSET)
        )

        structured_table_api_identifiers = cls(
            api_id=api_id,
            columns=columns,
        )

        structured_table_api_identifiers.additional_properties = d
        return structured_table_api_identifiers

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
    def api_id(self) -> str:
        if isinstance(self._api_id, Unset):
            raise NotPresentError(self, "api_id")
        return self._api_id

    @api_id.setter
    def api_id(self, value: str) -> None:
        self._api_id = value

    @api_id.deleter
    def api_id(self) -> None:
        self._api_id = UNSET

    @property
    def columns(self) -> List[StructuredTableColumnInfo]:
        if isinstance(self._columns, Unset):
            raise NotPresentError(self, "columns")
        return self._columns

    @columns.setter
    def columns(self, value: List[StructuredTableColumnInfo]) -> None:
        self._columns = value

    @columns.deleter
    def columns(self) -> None:
        self._columns = UNSET

from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.analysis_step_data_base_media_type import AnalysisStepDataBaseMediaType
from ..models.analysis_step_file_data_kind import AnalysisStepFileDataKind
from ..types import UNSET, Unset

T = TypeVar("T", bound="AnalysisStepFileData")


@attr.s(auto_attribs=True, repr=False)
class AnalysisStepFileData:
    """  """

    _file_ids: Union[Unset, List[str]] = UNSET
    _kind: Union[Unset, AnalysisStepFileDataKind] = UNSET
    _id: Union[Unset, str] = UNSET
    _is_multi: Union[Unset, bool] = UNSET
    _media_type: Union[Unset, AnalysisStepDataBaseMediaType] = UNSET
    _name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("file_ids={}".format(repr(self._file_ids)))
        fields.append("kind={}".format(repr(self._kind)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("is_multi={}".format(repr(self._is_multi)))
        fields.append("media_type={}".format(repr(self._media_type)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AnalysisStepFileData({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        file_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._file_ids, Unset):
            file_ids = self._file_ids

        kind: Union[Unset, int] = UNSET
        if not isinstance(self._kind, Unset):
            kind = self._kind.value

        id = self._id
        is_multi = self._is_multi
        media_type: Union[Unset, int] = UNSET
        if not isinstance(self._media_type, Unset):
            media_type = self._media_type.value

        name = self._name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if file_ids is not UNSET:
            field_dict["file_ids"] = file_ids
        if kind is not UNSET:
            field_dict["kind"] = kind
        if id is not UNSET:
            field_dict["id"] = id
        if is_multi is not UNSET:
            field_dict["isMulti"] = is_multi
        if media_type is not UNSET:
            field_dict["mediaType"] = media_type
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_file_ids() -> Union[Unset, List[str]]:
            file_ids = cast(List[str], d.pop("file_ids"))

            return file_ids

        file_ids = get_file_ids() if "file_ids" in d else cast(Union[Unset, List[str]], UNSET)

        def get_kind() -> Union[Unset, AnalysisStepFileDataKind]:
            kind = None
            _kind = d.pop("kind")
            if _kind is not None and _kind is not UNSET:
                try:
                    kind = AnalysisStepFileDataKind(_kind)
                except ValueError:
                    kind = AnalysisStepFileDataKind.of_unknown(_kind)

            return kind

        kind = get_kind() if "kind" in d else cast(Union[Unset, AnalysisStepFileDataKind], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_is_multi() -> Union[Unset, bool]:
            is_multi = d.pop("isMulti")
            return is_multi

        is_multi = get_is_multi() if "isMulti" in d else cast(Union[Unset, bool], UNSET)

        def get_media_type() -> Union[Unset, AnalysisStepDataBaseMediaType]:
            media_type = None
            _media_type = d.pop("mediaType")
            if _media_type is not None and _media_type is not UNSET:
                try:
                    media_type = AnalysisStepDataBaseMediaType(_media_type)
                except ValueError:
                    media_type = AnalysisStepDataBaseMediaType.of_unknown(_media_type)

            return media_type

        media_type = (
            get_media_type() if "mediaType" in d else cast(Union[Unset, AnalysisStepDataBaseMediaType], UNSET)
        )

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        analysis_step_file_data = cls(
            file_ids=file_ids,
            kind=kind,
            id=id,
            is_multi=is_multi,
            media_type=media_type,
            name=name,
        )

        analysis_step_file_data.additional_properties = d
        return analysis_step_file_data

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
    def file_ids(self) -> List[str]:
        if isinstance(self._file_ids, Unset):
            raise NotPresentError(self, "file_ids")
        return self._file_ids

    @file_ids.setter
    def file_ids(self, value: List[str]) -> None:
        self._file_ids = value

    @file_ids.deleter
    def file_ids(self) -> None:
        self._file_ids = UNSET

    @property
    def kind(self) -> AnalysisStepFileDataKind:
        if isinstance(self._kind, Unset):
            raise NotPresentError(self, "kind")
        return self._kind

    @kind.setter
    def kind(self, value: AnalysisStepFileDataKind) -> None:
        self._kind = value

    @kind.deleter
    def kind(self) -> None:
        self._kind = UNSET

    @property
    def id(self) -> str:
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @id.deleter
    def id(self) -> None:
        self._id = UNSET

    @property
    def is_multi(self) -> bool:
        if isinstance(self._is_multi, Unset):
            raise NotPresentError(self, "is_multi")
        return self._is_multi

    @is_multi.setter
    def is_multi(self, value: bool) -> None:
        self._is_multi = value

    @is_multi.deleter
    def is_multi(self) -> None:
        self._is_multi = UNSET

    @property
    def media_type(self) -> AnalysisStepDataBaseMediaType:
        if isinstance(self._media_type, Unset):
            raise NotPresentError(self, "media_type")
        return self._media_type

    @media_type.setter
    def media_type(self, value: AnalysisStepDataBaseMediaType) -> None:
        self._media_type = value

    @media_type.deleter
    def media_type(self) -> None:
        self._media_type = UNSET

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET

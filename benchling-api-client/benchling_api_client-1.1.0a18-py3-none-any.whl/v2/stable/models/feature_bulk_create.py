from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.feature_create_match_type import FeatureCreateMatchType
from ..types import UNSET, Unset

T = TypeVar("T", bound="FeatureBulkCreate")


@attr.s(auto_attribs=True, repr=False)
class FeatureBulkCreate:
    """  """

    _match_type: Union[Unset, FeatureCreateMatchType] = UNSET
    _color: Union[Unset, str] = UNSET
    _feature_library_id: Union[Unset, str] = UNSET
    _feature_type: Union[Unset, None, str] = UNSET
    _name: Union[Unset, str] = UNSET
    _pattern: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("match_type={}".format(repr(self._match_type)))
        fields.append("color={}".format(repr(self._color)))
        fields.append("feature_library_id={}".format(repr(self._feature_library_id)))
        fields.append("feature_type={}".format(repr(self._feature_type)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("pattern={}".format(repr(self._pattern)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "FeatureBulkCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        match_type: Union[Unset, int] = UNSET
        if not isinstance(self._match_type, Unset):
            match_type = self._match_type.value

        color = self._color
        feature_library_id = self._feature_library_id
        feature_type = self._feature_type
        name = self._name
        pattern = self._pattern

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if match_type is not UNSET:
            field_dict["matchType"] = match_type
        if color is not UNSET:
            field_dict["color"] = color
        if feature_library_id is not UNSET:
            field_dict["featureLibraryId"] = feature_library_id
        if feature_type is not UNSET:
            field_dict["featureType"] = feature_type
        if name is not UNSET:
            field_dict["name"] = name
        if pattern is not UNSET:
            field_dict["pattern"] = pattern

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_match_type() -> Union[Unset, FeatureCreateMatchType]:
            match_type = None
            _match_type = d.pop("matchType")
            if _match_type is not None and _match_type is not UNSET:
                try:
                    match_type = FeatureCreateMatchType(_match_type)
                except ValueError:
                    match_type = FeatureCreateMatchType.of_unknown(_match_type)

            return match_type

        match_type = (
            get_match_type() if "matchType" in d else cast(Union[Unset, FeatureCreateMatchType], UNSET)
        )

        def get_color() -> Union[Unset, str]:
            color = d.pop("color")
            return color

        color = get_color() if "color" in d else cast(Union[Unset, str], UNSET)

        def get_feature_library_id() -> Union[Unset, str]:
            feature_library_id = d.pop("featureLibraryId")
            return feature_library_id

        feature_library_id = (
            get_feature_library_id() if "featureLibraryId" in d else cast(Union[Unset, str], UNSET)
        )

        def get_feature_type() -> Union[Unset, None, str]:
            feature_type = d.pop("featureType")
            return feature_type

        feature_type = get_feature_type() if "featureType" in d else cast(Union[Unset, None, str], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_pattern() -> Union[Unset, str]:
            pattern = d.pop("pattern")
            return pattern

        pattern = get_pattern() if "pattern" in d else cast(Union[Unset, str], UNSET)

        feature_bulk_create = cls(
            match_type=match_type,
            color=color,
            feature_library_id=feature_library_id,
            feature_type=feature_type,
            name=name,
            pattern=pattern,
        )

        feature_bulk_create.additional_properties = d
        return feature_bulk_create

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
    def match_type(self) -> FeatureCreateMatchType:
        """ The match type of the feature. Used to determine how auto-annotate matches are made. """
        if isinstance(self._match_type, Unset):
            raise NotPresentError(self, "match_type")
        return self._match_type

    @match_type.setter
    def match_type(self, value: FeatureCreateMatchType) -> None:
        self._match_type = value

    @match_type.deleter
    def match_type(self) -> None:
        self._match_type = UNSET

    @property
    def color(self) -> str:
        """ The color of the annotations generated by the feature. Must be a valid hex string """
        if isinstance(self._color, Unset):
            raise NotPresentError(self, "color")
        return self._color

    @color.setter
    def color(self, value: str) -> None:
        self._color = value

    @color.deleter
    def color(self) -> None:
        self._color = UNSET

    @property
    def feature_library_id(self) -> str:
        """ The id of the feature library the feature belongs to """
        if isinstance(self._feature_library_id, Unset):
            raise NotPresentError(self, "feature_library_id")
        return self._feature_library_id

    @feature_library_id.setter
    def feature_library_id(self, value: str) -> None:
        self._feature_library_id = value

    @feature_library_id.deleter
    def feature_library_id(self) -> None:
        self._feature_library_id = UNSET

    @property
    def feature_type(self) -> Optional[str]:
        """The type of feature, like gene, promoter, etc. Note: This is an arbitrary string, not an enum"""
        if isinstance(self._feature_type, Unset):
            raise NotPresentError(self, "feature_type")
        return self._feature_type

    @feature_type.setter
    def feature_type(self, value: Optional[str]) -> None:
        self._feature_type = value

    @feature_type.deleter
    def feature_type(self) -> None:
        self._feature_type = UNSET

    @property
    def name(self) -> str:
        """ The name of the feature """
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET

    @property
    def pattern(self) -> str:
        """ The pattern used for matching during auto-annotation. """
        if isinstance(self._pattern, Unset):
            raise NotPresentError(self, "pattern")
        return self._pattern

    @pattern.setter
    def pattern(self, value: str) -> None:
        self._pattern = value

    @pattern.deleter
    def pattern(self) -> None:
        self._pattern = UNSET

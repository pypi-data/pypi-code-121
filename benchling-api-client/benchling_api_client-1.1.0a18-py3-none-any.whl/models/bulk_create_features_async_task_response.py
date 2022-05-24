from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.feature import Feature
from ..types import UNSET, Unset

T = TypeVar("T", bound="BulkCreateFeaturesAsyncTaskResponse")


@attr.s(auto_attribs=True, repr=False)
class BulkCreateFeaturesAsyncTaskResponse:
    """  """

    _features: Union[Unset, List[Feature]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("features={}".format(repr(self._features)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BulkCreateFeaturesAsyncTaskResponse({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        features: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._features, Unset):
            features = []
            for features_item_data in self._features:
                features_item = features_item_data.to_dict()

                features.append(features_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if features is not UNSET:
            field_dict["features"] = features

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_features() -> Union[Unset, List[Feature]]:
            features = []
            _features = d.pop("features")
            for features_item_data in _features or []:
                features_item = Feature.from_dict(features_item_data)

                features.append(features_item)

            return features

        features = get_features() if "features" in d else cast(Union[Unset, List[Feature]], UNSET)

        bulk_create_features_async_task_response = cls(
            features=features,
        )

        bulk_create_features_async_task_response.additional_properties = d
        return bulk_create_features_async_task_response

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
    def features(self) -> List[Feature]:
        if isinstance(self._features, Unset):
            raise NotPresentError(self, "features")
        return self._features

    @features.setter
    def features(self, value: List[Feature]) -> None:
        self._features = value

    @features.deleter
    def features(self) -> None:
        self._features = UNSET

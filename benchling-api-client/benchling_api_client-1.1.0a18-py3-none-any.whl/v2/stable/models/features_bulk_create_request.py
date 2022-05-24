from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.feature_bulk_create import FeatureBulkCreate
from ..types import UNSET, Unset

T = TypeVar("T", bound="FeaturesBulkCreateRequest")


@attr.s(auto_attribs=True, repr=False)
class FeaturesBulkCreateRequest:
    """ Inputs for bulk creating a new feature """

    _features: Union[Unset, List[FeatureBulkCreate]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("features={}".format(repr(self._features)))
        return "FeaturesBulkCreateRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        features: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._features, Unset):
            features = []
            for features_item_data in self._features:
                features_item = features_item_data.to_dict()

                features.append(features_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if features is not UNSET:
            field_dict["features"] = features

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_features() -> Union[Unset, List[FeatureBulkCreate]]:
            features = []
            _features = d.pop("features")
            for features_item_data in _features or []:
                features_item = FeatureBulkCreate.from_dict(features_item_data)

                features.append(features_item)

            return features

        features = get_features() if "features" in d else cast(Union[Unset, List[FeatureBulkCreate]], UNSET)

        features_bulk_create_request = cls(
            features=features,
        )

        return features_bulk_create_request

    @property
    def features(self) -> List[FeatureBulkCreate]:
        if isinstance(self._features, Unset):
            raise NotPresentError(self, "features")
        return self._features

    @features.setter
    def features(self, value: List[FeatureBulkCreate]) -> None:
        self._features = value

    @features.deleter
    def features(self) -> None:
        self._features = UNSET

from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.canvas_ui_block import CanvasUiBlock
from ..types import UNSET, Unset

T = TypeVar("T", bound="Canvas")


@attr.s(auto_attribs=True, repr=False)
class Canvas:
    """  """

    _blocks: List[CanvasUiBlock]
    _feature_id: str
    _id: Union[Unset, str] = UNSET
    _enabled: Union[Unset, bool] = UNSET
    _resource_id: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("blocks={}".format(repr(self._blocks)))
        fields.append("feature_id={}".format(repr(self._feature_id)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("enabled={}".format(repr(self._enabled)))
        fields.append("resource_id={}".format(repr(self._resource_id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "Canvas({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        blocks = []
        for blocks_item_data in self._blocks:
            blocks_item = blocks_item_data.to_dict()

            blocks.append(blocks_item)

        feature_id = self._feature_id
        id = self._id
        enabled = self._enabled
        resource_id = self._resource_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "blocks": blocks,
                "featureId": feature_id,
            }
        )
        if id is not UNSET:
            field_dict["id"] = id
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if resource_id is not UNSET:
            field_dict["resourceId"] = resource_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_blocks() -> List[CanvasUiBlock]:
            blocks = []
            _blocks = d.pop("blocks")
            for blocks_item_data in _blocks:
                blocks_item = CanvasUiBlock.from_dict(blocks_item_data)

                blocks.append(blocks_item)

            return blocks

        blocks = get_blocks() if "blocks" in d else cast(List[CanvasUiBlock], UNSET)

        def get_feature_id() -> str:
            feature_id = d.pop("featureId")
            return feature_id

        feature_id = get_feature_id() if "featureId" in d else cast(str, UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_enabled() -> Union[Unset, bool]:
            enabled = d.pop("enabled")
            return enabled

        enabled = get_enabled() if "enabled" in d else cast(Union[Unset, bool], UNSET)

        def get_resource_id() -> Union[Unset, None, str]:
            resource_id = d.pop("resourceId")
            return resource_id

        resource_id = get_resource_id() if "resourceId" in d else cast(Union[Unset, None, str], UNSET)

        canvas = cls(
            blocks=blocks,
            feature_id=feature_id,
            id=id,
            enabled=enabled,
            resource_id=resource_id,
        )

        canvas.additional_properties = d
        return canvas

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
    def blocks(self) -> List[CanvasUiBlock]:
        if isinstance(self._blocks, Unset):
            raise NotPresentError(self, "blocks")
        return self._blocks

    @blocks.setter
    def blocks(self, value: List[CanvasUiBlock]) -> None:
        self._blocks = value

    @property
    def feature_id(self) -> str:
        """ Identifier of the feature defined in Benchling App Manifest this canvas corresponds to. """
        if isinstance(self._feature_id, Unset):
            raise NotPresentError(self, "feature_id")
        return self._feature_id

    @feature_id.setter
    def feature_id(self, value: str) -> None:
        self._feature_id = value

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
    def enabled(self) -> bool:
        """Overall control for whether the canvas is interactable or not. If `false`, every block is disabled and will override the individual block's `enabled` property. If `true` or absent, the interactivity status will defer to the block's `enabled` property."""
        if isinstance(self._enabled, Unset):
            raise NotPresentError(self, "enabled")
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    @enabled.deleter
    def enabled(self) -> None:
        self._enabled = UNSET

    @property
    def resource_id(self) -> Optional[str]:
        """ Identifier of the resource object to attach canvas to. """
        if isinstance(self._resource_id, Unset):
            raise NotPresentError(self, "resource_id")
        return self._resource_id

    @resource_id.setter
    def resource_id(self, value: Optional[str]) -> None:
        self._resource_id = value

    @resource_id.deleter
    def resource_id(self) -> None:
        self._resource_id = UNSET

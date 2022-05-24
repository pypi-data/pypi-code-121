from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.canvas_leaf_node_ui_block import CanvasLeafNodeUiBlock
from ..models.section_ui_block_type import SectionUiBlockType
from ..types import UNSET, Unset

T = TypeVar("T", bound="SectionUiBlock")


@attr.s(auto_attribs=True, repr=False)
class SectionUiBlock:
    """  """

    _children: Union[Unset, List[CanvasLeafNodeUiBlock]] = UNSET
    _type: Union[Unset, SectionUiBlockType] = UNSET

    def __repr__(self):
        fields = []
        fields.append("children={}".format(repr(self._children)))
        fields.append("type={}".format(repr(self._type)))
        return "SectionUiBlock({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        children: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._children, Unset):
            children = []
            for children_item_data in self._children:
                children_item = children_item_data.to_dict()

                children.append(children_item)

        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if children is not UNSET:
            field_dict["children"] = children
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_children() -> Union[Unset, List[CanvasLeafNodeUiBlock]]:
            children = []
            _children = d.pop("children")
            for children_item_data in _children or []:
                children_item = CanvasLeafNodeUiBlock.from_dict(children_item_data)

                children.append(children_item)

            return children

        children = (
            get_children() if "children" in d else cast(Union[Unset, List[CanvasLeafNodeUiBlock]], UNSET)
        )

        def get_type() -> Union[Unset, SectionUiBlockType]:
            type = None
            _type = d.pop("type")
            if _type is not None and _type is not UNSET:
                try:
                    type = SectionUiBlockType(_type)
                except ValueError:
                    type = SectionUiBlockType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(Union[Unset, SectionUiBlockType], UNSET)

        section_ui_block = cls(
            children=children,
            type=type,
        )

        return section_ui_block

    @property
    def children(self) -> List[CanvasLeafNodeUiBlock]:
        if isinstance(self._children, Unset):
            raise NotPresentError(self, "children")
        return self._children

    @children.setter
    def children(self, value: List[CanvasLeafNodeUiBlock]) -> None:
        self._children = value

    @children.deleter
    def children(self) -> None:
        self._children = UNSET

    @property
    def type(self) -> SectionUiBlockType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: SectionUiBlockType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET

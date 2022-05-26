from __future__ import annotations

from typing import TYPE_CHECKING, Iterable, NamedTuple, Optional, Tuple, TypeVar, Union

from sila2.framework.abc.constraint import Constraint
from sila2.framework.utils import xpath_sila

if TYPE_CHECKING:
    from sila2.framework.abc.data_type import DataType
    from sila2.framework.feature import Feature


T = TypeVar("T", bound=Union[str, bytes])


class ContentType(Constraint[T]):
    type: str
    subtype: str
    parameters: Tuple[ContentTypeParameter, ...]

    # noinspection PyShadowingBuiltins
    def __init__(
        self,
        type: str,
        subtype: str,
        parameters: Optional[Iterable[ContentTypeParameter]] = None,
    ):
        self.type = type
        self.subtype = subtype
        self.parameters = () if parameters is None else tuple(parameters)

    def validate(self, value: T) -> bool:
        return True

    @property
    def media_type(self) -> str:
        media_type = f"{self.type}/{self.subtype}"
        for par in self.parameters:
            media_type += f"; {par.attribute}={par.value}"
        return media_type

    @classmethod
    def from_fdl_node(cls, fdl_node, parent_feature: Feature, base_type: DataType) -> ContentType:
        _type = xpath_sila(fdl_node, "sila:Type/text()")[0]
        subtype = xpath_sila(fdl_node, "sila:Subtype/text()")[0]

        parameters = []
        for par_node in xpath_sila(fdl_node, "sila:Parameters/sila:Parameter"):
            attribute = xpath_sila(par_node, "sila:Attribute/text()")[0]
            value = xpath_sila(par_node, "sila:Value/text()")[0]
            parameters.append(ContentTypeParameter(attribute, value))

        return cls(_type, subtype, parameters)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.media_type!r})"


class ContentTypeParameter(NamedTuple):
    attribute: str
    value: str

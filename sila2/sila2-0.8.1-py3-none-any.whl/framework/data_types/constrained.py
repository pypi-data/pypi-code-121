from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, List, Optional

from google.protobuf.message import Message

from sila2.framework.abc.constraint import Constraint
from sila2.framework.abc.data_type import DataType
from sila2.framework.abc.named_data_node import NamedDataNode
from sila2.framework.errors.validation_error import ValidationError
from sila2.framework.utils import xpath_sila

if TYPE_CHECKING:
    from sila2.framework.feature import Feature


class Constrained(DataType):
    base_type: DataType
    constraints: List[Constraint]

    def __init__(self, base_type: DataType, constraints: Iterable[Constraint]):
        self.base_type = base_type
        self.constraints = list(constraints)

    def to_native_type(self, message: Message, toplevel_named_data_node: Optional[NamedDataNode] = None) -> Any:
        native_object = self.base_type.to_native_type(message, toplevel_named_data_node=toplevel_named_data_node)
        self.__validate(native_object)
        return native_object

    def to_message(self, *args: Any, **kwargs: Any) -> Message:
        msg = self.base_type.to_message(*args, **kwargs)

        toplevel_named_data_node = kwargs.get("toplevel_named_data_node")
        native_object = self.base_type.to_native_type(msg, toplevel_named_data_node=toplevel_named_data_node)
        self.__validate(native_object)

        return msg

    def __validate(self, value: Any) -> None:
        for constraint in self.constraints:
            if not constraint.validate(value):
                raise ValidationError(f"Constraint violated: {constraint!r} ({value!r})")

    @staticmethod
    def from_fdl_node(fdl_node, parent_feature: Feature, parent_namespace) -> Constrained:
        dtype = DataType.from_fdl_node(xpath_sila(fdl_node, "sila:DataType")[0], parent_feature, parent_namespace)
        constraints = [
            Constraint.from_fdl_node(constraint_node, parent_feature, dtype)
            for constraint_node in xpath_sila(fdl_node, "sila:Constraints/*")
        ]
        return Constrained(dtype, constraints)

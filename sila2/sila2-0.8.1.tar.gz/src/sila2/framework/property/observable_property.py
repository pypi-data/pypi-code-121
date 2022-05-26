from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from sila2.framework.property.property import Property

if TYPE_CHECKING:
    from sila2.framework.feature import Feature


PythonType = TypeVar("PythonType")


class ObservableProperty(Property, Generic[PythonType]):
    """Represents an observable property"""

    def __init__(self, fdl_node, parent_feature: Feature):
        super().__init__(fdl_node, parent_feature)
        self.parameter_message_type = getattr(parent_feature._pb2_module, f"Subscribe_{self._identifier}_Parameters")
        self.response_message_type = getattr(parent_feature._pb2_module, f"Subscribe_{self._identifier}_Responses")

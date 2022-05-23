from __future__ import annotations

from typing import Dict, Type

from sarus_data_spec.base import Referring
import sarus_data_spec.protobuf as sp
import sarus_data_spec.typing as st


class Attribute(Referring[sp.Attribute]):
    """A python class to describe attributes"""

    def __init__(self, protobuf: sp.Attribute) -> None:
        self._referred = {protobuf.object}
        # This has to be defined before it is initialized
        super().__init__(protobuf=protobuf)

    def prototype(self) -> Type[sp.Attribute]:
        """Return the type of the underlying protobuf."""
        return sp.Attribute


def attach_properties(
    node: st.DataSpec, properties: Dict[str, str]
) -> Attribute:
    return Attribute(
        sp.Attribute(
            object=node.uuid(),
            properties=properties,
        )
    )

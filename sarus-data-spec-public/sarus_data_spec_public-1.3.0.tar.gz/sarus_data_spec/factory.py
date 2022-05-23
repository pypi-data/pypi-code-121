from typing import Callable, MutableMapping, TypeVar

from sarus_data_spec.protobuf import type_name
from sarus_data_spec.protobuf.typing import Protobuf
import sarus_data_spec.typing as st


class Factory(st.Factory):
    """Can produce objects from protobuf messages"""

    type_name_create: MutableMapping[
        str, Callable[[Protobuf], st.HasProtobuf]
    ] = {}

    def register(
        self, name: str, create: Callable[[Protobuf], st.HasProtobuf]
    ) -> None:
        self.type_name_create[name] = create

    M = TypeVar('M', bound=Protobuf)

    def create(self, message: M) -> st.HasProtobuf[M]:
        return self.type_name_create[type_name(message)](message)

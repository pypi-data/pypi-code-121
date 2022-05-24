from types import TracebackType
import typing as t

from sarus_data_spec.context.state import (
    pop_global_context,
    push_global_context,
)
from sarus_data_spec.context.typing import Context
from sarus_data_spec.manager.typing import Manager
from sarus_data_spec.storage.typing import Storage
import sarus_data_spec.typing as st


class Public(Context):
    """A public context base"""

    def __init__(self) -> None:
        pass

    def factory(self) -> st.Factory:
        raise NotImplementedError

    def storage(self) -> Storage:
        raise NotImplementedError()

    def manager(self) -> Manager:
        raise NotImplementedError()

    def __enter__(self) -> Context:
        push_global_context(self)
        return self

    def __exit__(
        self,
        type: t.Optional[t.Type[BaseException]],
        value: t.Optional[BaseException],
        traceback: t.Optional[TracebackType],
    ) -> None:
        pop_global_context()
        return None

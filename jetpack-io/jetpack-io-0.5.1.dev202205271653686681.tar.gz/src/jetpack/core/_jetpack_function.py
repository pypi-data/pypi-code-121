from typing import Awaitable, Callable, TypeVar, Union

from jetpack.core._jetpack_function_with_client import JetpackFunctionWithClient
from jetpack.runtime._client import client

T = TypeVar("T")


class JetpackFunction(JetpackFunctionWithClient[T]):
    def __init__(
        self,
        func: Callable[..., Union[T, Awaitable[T]]],
        with_checkpointing: bool = False,
    ) -> None:
        super().__init__(client, func, with_checkpointing)

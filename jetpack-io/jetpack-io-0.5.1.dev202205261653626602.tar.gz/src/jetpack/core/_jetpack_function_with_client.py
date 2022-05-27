from __future__ import annotations

import base64
import contextvars
import inspect
import time
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    Final,
    Generic,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)

from jetpack import _utils
from jetpack.config import _instrumentation
from jetpack.core._task import Task
from jetpack.util.network import _codec

if TYPE_CHECKING:
    from jetpack.runtime._client import Client

T = TypeVar("T")
DEFAULT_TASK_ID: Final[str] = "app"

target_time_var = contextvars.ContextVar[int]("target_time")
task_var = contextvars.ContextVar[Task]("task")
task_id_var = contextvars.ContextVar[str]("task_id", default=DEFAULT_TASK_ID)


class JetpackFunctionWithClient(Generic[T]):
    def __init__(
        self,
        client: Client,
        func: Callable[..., Union[T, Awaitable[T]]],
        with_checkpointing: bool = False,
    ) -> None:
        self.func = func
        self.client = client
        self.with_checkpointing = with_checkpointing

    async def __call__(self, *args: Any, **kwargs: Any) -> T:
        t = await self.create_task(args, kwargs)
        if not t.is_scheduled and t.target_time <= time.time():
            # Only wait for result if schedule() was not used and target_time is
            # in the past.
            assert t.id is not None
            result = await self.client.wait_for_result(t.id, t.symbol_name())
        else:
            # This is a little hacky. We want __call__ to have return type T
            # so that when a user defines a function with return type and adds
            # @function decorator, calling the function will have the same return
            # type. But when we use schedule(), we don't care about the return.
            # Returning None technically violates the type T, but this is an
            # internal detail. Note that schedule() does not use the return.
            result = None
        return cast(T, result)

    async def create_task(self, args: Any, kwargs: Any) -> Task:
        try:
            target_time = target_time_var.get()
            is_scheduled = True
        except LookupError:
            target_time = int(time.time())
            is_scheduled = False

        parent_task_id = task_id_var.get()
        with_checkpointing = self.with_checkpointing

        task = Task(self, parent_task_id, with_checkpointing, target_time, is_scheduled)
        task_var.set(task)
        await self.client.create_task(task, args, kwargs)
        return task

    def name(self) -> str:
        return _utils.qualified_func_name(self.func)

    async def exec(
        self,
        exec_id: str = "",
        encoded_args: bytes = b"",
        post_result: bool = True,
    ) -> Tuple[Optional[T], Optional[Exception]]:
        task_id_var.set(exec_id)
        args: Tuple[Any, ...] = ()
        kwargs: Dict[str, Any] = {}
        if encoded_args:
            decoded_args, decoded_kwargs = _codec.decode_args(
                encoded_args.decode("utf-8")
            )
            if decoded_args:
                args = decoded_args
            if decoded_kwargs:
                kwargs = decoded_kwargs

        retval, err = None, None
        try:
            _instrumentation.get_tracer().jetpack_function_called(self)
            if inspect.iscoroutinefunction(self.func):
                retval = await cast(Awaitable[T], self.func(*args, **kwargs))
            else:
                retval = cast(T, self.func(*args, **kwargs))
        except Exception as e:
            err = e

        # for now, we post the result back to the runtime. A slightly better approach is to
        # have the caller of this function post it (the CLI). Doing it here for now because
        # the runtime is already initialized and set up here.
        if post_result:
            await self.client.post_result(exec_id, value=retval, error=err)
        # If there is an exception, we're rethrowing it to let the pod know the process exits
        # with non-zero code. This will allow job retries if backoffLimit is not set to zero.
        if err is not None:
            raise err
        return retval, err


async def schedule(
    coro: Awaitable[T],
    target_time: Optional[int] = None,
    delta: Optional[int] = None,
) -> Task:
    if target_time is not None and delta is not None:
        raise ValueError("target_time and delta cannot both be specified")
    if target_time:
        target_time_var.set(target_time)
    elif delta:
        target_time_var.set(int(time.time()) + delta)
    else:
        raise ValueError("target_time or delta must be specified")

    await coro
    return task_var.get()  # Propagate LookupError if it happens

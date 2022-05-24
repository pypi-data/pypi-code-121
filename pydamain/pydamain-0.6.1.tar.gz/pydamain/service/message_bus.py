import asyncio
from typing import (
    Any,
    Awaitable,
    Callable,
    Literal,
    Optional,
    TypeVar,
    overload,
)

from pydamain.domain.messages import Message

from .handler import Handler
from .message_catcher import MessageCatcher

T = TypeVar("T")
R = TypeVar("R")
Handlers = tuple[Handler[T, R], ...]
Hook = Callable[[T, Handler[T, R]], Awaitable[None]]


async def handle(
    message: T,
    handler: Handler[T, Any],
    deps: dict[str, Any],
    pre_hook: Optional[Hook[T, Any]] = None,
    post_hook: Optional[Hook[T, Any]] = None,
):
    if pre_hook:
        await pre_hook(message, handler)
    result = await handler(message, **deps)
    if post_hook:
        await post_hook(message, handler)
    return result


async def handle_parallel(
    message: T,
    handlers: tuple[Handler[T, Any], ...],
    deps: dict[str, Any],
    pre_hook: Optional[Hook[T, Any]] = None,
    post_hook: Optional[Hook[T, Any]] = None,
):
    coros = (
        handle(message, handler, deps, pre_hook, post_hook) for handler in handlers
    )
    return await asyncio.gather(*coros, return_exceptions=True)


M = TypeVar("M", bound=Message)


class MessageBus:
    def __init__(
        self,
        *,
        deps: dict[str, Any],
        pre_hook: Optional[Hook[Message, Any]] = None,
        post_hook: Optional[Hook[Message, Any]] = None,
    ) -> None:
        self._deps: dict[str, Any] = deps
        self._handler_map: dict[
            type[Message], Handler[Any, Any] | Handlers[Any, Any]
        ] = {}
        self._pre_hook = pre_hook
        self._post_hook = post_hook

    def register(
        self,
        message_type: type[M],
        handler: Handler[M, Any] | Handlers[M, Any],
    ):
        self._handler_map[message_type] = handler

    @overload
    async def dispatch(self, message: Message) -> Any:
        ...

    @overload
    async def dispatch(
        self, message: Message, return_hooked_task: Literal[True] = True
    ) -> tuple[Any, asyncio.Future[list[Any]]]:
        ...

    async def dispatch(self, message: Message, return_hooked_task: bool = False):
        result, hooked = await asyncio.create_task(self._dispatch(message))
        coros = (self._dispatch(msg) for msg in hooked)
        hooked_task = asyncio.gather(*coros, return_exceptions=True)
        if return_hooked_task:
            return result, hooked_task
        await hooked_task
        return result

    async def _dispatch(self, message: Message):
        handler = self._handler_map[type(message)]
        with MessageCatcher() as message_catcher:
            if isinstance(handler, tuple):
                result = await handle_parallel(
                    message, handler, self._deps, self._pre_hook, self._post_hook
                )
            else:
                result = await handle(
                    message, handler, self._deps, self._pre_hook, self._post_hook
                )
        return result, message_catcher.issued_messages

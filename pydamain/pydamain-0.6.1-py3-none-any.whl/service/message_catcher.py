from contextvars import ContextVar, Token
from dataclasses import field
from types import TracebackType
from typing import Any, Optional, ContextManager
from typing_extensions import Self


_messages_context_var: ContextVar[set[Any]] = ContextVar("messages")


class MessageCatcher(ContextManager["MessageCatcher"]):

    _token: Token[set[Any]] = field(init=False)
    issued_messages: set[Any] = field(init=False)

    def __enter__(self) -> Self:
        self._token = _messages_context_var.set(set())
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.issued_messages = _messages_context_var.get()
        _messages_context_var.reset(self._token)


def issue(message: Any):
    _messages_context_var.get().add(message)


def get_issued_messages():
    return _messages_context_var.get()

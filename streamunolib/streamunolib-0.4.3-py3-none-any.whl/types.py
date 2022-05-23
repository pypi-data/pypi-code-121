"""This package defines types hints used by the streamunolib library."""

from typing import Any, Callable, Protocol, TypeVar, runtime_checkable

F = TypeVar('F', bound=Callable[..., Any])


@runtime_checkable
class ExposableCallable(Protocol[F]):
    """Interface of all components that can be exposed or hidden."""

    __call__: F
    __exposed__: bool

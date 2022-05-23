"""This package provides the decorators to annotate a transform component."""
from __future__ import annotations

from typing import Any, Callable, TypeVar, cast

from .types import ExposableCallable

F = TypeVar('F', bound=Callable[..., Any])


def exposed(f: F) -> ExposableCallable[F]:
    """Marks a function as a UI-visible transform component."""
    g = cast(ExposableCallable[F], f)
    g.__exposed__ = True
    return g


def hidden(f: F) -> ExposableCallable[F]:
    """Marks a function as a non UI-visible transform component."""
    g = cast(ExposableCallable[F], f)
    g.__exposed__ = False
    return g

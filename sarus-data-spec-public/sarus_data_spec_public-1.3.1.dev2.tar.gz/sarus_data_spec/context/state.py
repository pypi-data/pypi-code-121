import typing as t

from sarus_data_spec.context.typing import Context

_global_context_stack: t.List[Context] = []


def push_global_context(context: Context) -> None:
    _global_context_stack.append(context)


def pop_global_context() -> Context:
    return _global_context_stack.pop()


def global_context() -> Context:
    return _global_context_stack[-1]

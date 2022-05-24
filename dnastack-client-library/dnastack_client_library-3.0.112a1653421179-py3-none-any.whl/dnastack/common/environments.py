import os

from typing import Any, Callable, Optional

__boolean_flag = lambda v: str(v or '').lower() in ['1', 'true']


class EnvironmentVariableRequired(RuntimeError):
    def __init__(self, environment_variable_name: str, hint: Optional[str]):
        feedback = f'Environment variable required: {environment_variable_name}'

        if hint:
            feedback += f' ({hint})'

        super(EnvironmentVariableRequired, self).__init__(feedback)


def env(key: str,
        default: Any = None,
        required: bool = False,
        transform: Optional[Callable] = None,
        hint: Optional[str] = None) -> Any:
    if key not in os.environ and required:
        raise EnvironmentVariableRequired(key, hint)

    value = os.getenv(key)

    if value is None:
        return default or value
    else:
        return transform(value) if transform else value


def flag(key: str) -> bool:
    return bool(env(key, default=False, transform=__boolean_flag))

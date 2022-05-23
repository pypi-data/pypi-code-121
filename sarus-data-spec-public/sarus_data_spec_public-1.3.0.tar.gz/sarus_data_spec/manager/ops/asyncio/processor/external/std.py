from typing import Any

from .utils import two_arguments_ops


@two_arguments_ops
async def add(val_1: Any, val_2: Any) -> Any:
    return val_1 + val_2


@two_arguments_ops
async def sub(val_1: Any, val_2: Any) -> Any:
    return val_1 - val_2


@two_arguments_ops
async def mul(val_1: Any, val_2: Any) -> Any:
    return val_1 * val_2


@two_arguments_ops
async def div(val_1: Any, val_2: Any) -> Any:
    return val_1 / val_2

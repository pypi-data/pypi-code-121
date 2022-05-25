from typing import Any

from .utils import one_parent_ops, two_arguments_ops


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


@one_parent_ops
async def invert(val: Any) -> Any:
    return ~val


@one_parent_ops
async def length(val: Any) -> Any:
    return len(val)


@two_arguments_ops
async def getitem(val: Any, key: Any) -> Any:
    return val[key]


@two_arguments_ops
async def greater_than(val_1: Any, val_2: Any) -> Any:
    return val_1 > val_2


@two_arguments_ops
async def greater_equal(val_1: Any, val_2: Any) -> Any:
    return val_1 >= val_2


@two_arguments_ops
async def lower_than(val_1: Any, val_2: Any) -> Any:
    return val_1 < val_2


@two_arguments_ops
async def lower_equal(val_1: Any, val_2: Any) -> Any:
    return val_1 <= val_2


@two_arguments_ops
async def not_equal(val_1: Any, val_2: Any) -> Any:
    return val_1 != val_2


@one_parent_ops
async def neg(val_1: Any) -> Any:
    return -val_1


@one_parent_ops
async def pos(val_1: Any) -> Any:
    return +val_1


@one_parent_ops
async def _abs(val_1: Any) -> Any:
    return abs(val_1)


@one_parent_ops
async def _round(val_1: Any) -> Any:
    return round(val_1)


@two_arguments_ops
async def modulo(val_1: Any, val_2: Any) -> Any:
    return val_1 % val_2


@two_arguments_ops
async def _or(val_1: Any, val_2: Any) -> Any:
    return val_1 | val_2


@two_arguments_ops
async def _and(val_1: Any, val_2: Any) -> Any:
    return val_1 & val_2

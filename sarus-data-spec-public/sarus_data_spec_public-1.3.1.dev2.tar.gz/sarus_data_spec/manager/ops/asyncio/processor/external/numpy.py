from typing import Any

from .utils import one_parent_ops


@one_parent_ops
async def np_mean(val: Any, *args: Any, **kwargs: Any) -> Any:
    return val.mean(*args, **kwargs)


@one_parent_ops
async def np_std(val: Any, *args: Any, **kwargs: Any) -> Any:
    return val.std(*args, **kwargs)

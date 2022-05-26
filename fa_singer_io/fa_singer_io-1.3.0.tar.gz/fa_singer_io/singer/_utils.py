from fa_purity import (
    Result,
)
from typing import (
    FrozenSet,
    Optional,
    TypeVar,
)

_T = TypeVar("_T")


def all_keys_in(
    items: FrozenSet[_T], requires: Optional[FrozenSet[_T]]
) -> Result[None, FrozenSet[_T]]:
    _requires: FrozenSet[_T] = (
        requires if requires is not None else frozenset([])
    )
    if all([r in items for r in _requires]):
        return Result.success(None)
    return Result.failure(_requires - items)

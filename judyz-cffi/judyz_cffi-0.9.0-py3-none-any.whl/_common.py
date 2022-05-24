from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Iterable, Mapping, Optional, Tuple, Union, ClassVar

    TKey = ClassVar["TKey"]


class _JudyCommon:
    def update(self, other: Mapping[TKey, int] | Iterable[tuple[TKey, int]] | None) -> None:
        if other is None:
            return
        has_keys = True
        try:
            other.keys  # noqa
        except AttributeError:
            has_keys = False
        if has_keys:
            for key in other:
                self[key] = other[key]
        else:
            for (k, v) in other:
                self[k] = v

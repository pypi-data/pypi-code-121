from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class BenchlingAppManifestManifestVersion(Enums.KnownInt):
    VALUE_1 = 1

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: int) -> "BenchlingAppManifestManifestVersion":
        if not isinstance(val, int):
            raise ValueError(
                f"Value of BenchlingAppManifestManifestVersion must be an int (encountered: {val})"
            )
        newcls = Enum("BenchlingAppManifestManifestVersion", {"_UNKNOWN": val}, type=Enums.UnknownInt)  # type: ignore
        return cast(BenchlingAppManifestManifestVersion, getattr(newcls, "_UNKNOWN"))

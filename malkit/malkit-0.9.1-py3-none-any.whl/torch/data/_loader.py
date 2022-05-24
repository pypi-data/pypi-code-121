from typing import Tuple

from torch import Tensor

from ..._typing import FilePath


class Loader:
    def __call__(self, path: FilePath) -> Tensor:
        raise NotImplementedError

    def __repr__(self) -> str:
        # Format arguments.
        args = self._get_args()
        args_str = ", ".join(f"{a}={getattr(self, a)!r}" for a in args)
        return f"{type(self).__name__}({args_str})"

    def _get_args(self) -> Tuple[str, ...]:
        raise NotImplementedError

from typing import Any, Protocol, TypeVar


T_contra = TypeVar("T_contra", contravariant=True)
R_co = TypeVar("R_co", covariant=True)


class _Handler(Protocol[T_contra, R_co]):

    __name__: str

    async def __call__(self, _msg: T_contra, **_: Any) -> R_co:
        ...


Handler = _Handler
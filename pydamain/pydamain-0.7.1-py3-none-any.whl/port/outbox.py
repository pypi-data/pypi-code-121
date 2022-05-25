from typing import Protocol, TypeVar


E = TypeVar("E", contravariant=True)


class Outbox(Protocol[E]):
    async def put(self, _envelope: E) -> None:
        ...

    async def delete(self, _envelope: E) -> None:
        ...

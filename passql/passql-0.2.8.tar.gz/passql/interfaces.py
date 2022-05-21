from typing import Protocol, Any, List, Iterator

__all__ = (
    'IDbRecord',
    'IOriginTransaction',
    'IOriginConnection',
)


class IDbRecord(Protocol):
    def __contains__(self, field_name) -> bool:
        ...

    def __getitem__(self, field_name) -> Any:
        ...

    def __len__(self) -> int:
        ...

    def keys(self) -> Iterator[str]:
        ...

    def values(self) -> Iterator[Any]:
        ...


class IOriginTransaction(Protocol):
    async def start(self):
        ...

    async def commit(self):
        ...

    async def rollback(self):
        ...

    async def __aenter__(self):
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...


class IOriginConnection(Protocol):
    async def fetch(self, sql: str, timeout=None) -> List[IDbRecord]:
        ...

    async def fetchrow(self, sql: str, timeout=None) -> IDbRecord:
        ...

    async def execute(self, sql: str, timeout=None):
        ...

    async def fetchval(self, sql: str, timeout=None) -> Any:
        ...

    async def close(self):
        ...

    def is_closed(self) -> bool:
        ...

    def transaction(self) -> IOriginTransaction:
        ...

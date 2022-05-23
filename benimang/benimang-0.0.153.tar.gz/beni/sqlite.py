from __future__ import annotations

import asyncio
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Iterable, Sequence, cast

import aiosqlite

sqlite3.register_converter(
    "bool",
    lambda x: x not in (
        b'',
        b'0',
        # None, # 如果是None根本就不会进来，这里判断也没有意义
    )
)


class SqliteDbPool():

    def __init__(self, db_file: str | Path, count: int = 9):
        self._avaliable_list: asyncio.Queue[_SqliteDbRead] = asyncio.Queue()
        self._using_list: list[_SqliteDbRead] = []
        self._readlock_list: list[asyncio.Lock] = []
        self._dbwrite: _SqliteDbWrite | None = None
        self._writelock = asyncio.Lock()
        self._db_file = db_file
        self._count = count

    async def close(self):
        while self._using_list or not self._avaliable_list.empty():
            xx = await self._avaliable_list.get()
            await xx.close()
        await self._writelock.acquire()
        if self._dbwrite:
            await self._dbwrite.close()
        self._writelock.release()

    async def _getDbRead(self):
        if len(self._using_list) < self._count:
            if self._avaliable_list.empty():
                db = _SqliteDbRead()
                await db.connect(self._db_file)
            else:
                db = self._avaliable_list.get_nowait()
        else:
            db = await self._avaliable_list.get()
        self._using_list.append(db)
        return db

    def _releaseDbRead(self, db: _SqliteDbRead):
        self._using_list.remove(db)
        self._avaliable_list.put_nowait(db)

    @asynccontextmanager
    async def read(self):
        lock = asyncio.Lock()
        await lock.acquire()
        db = await self._getDbRead()
        if self._writelock.locked():
            await self._writelock.acquire()
            self._readlock_list.append(lock)
            self._writelock.release()
        else:
            self._readlock_list.append(lock)
        try:
            yield db
        finally:
            self._releaseDbRead(db)
            self._readlock_list.remove(lock)
            lock.release()

    @asynccontextmanager
    async def write(self):
        await self._writelock.acquire()
        while self._readlock_list:
            lock = self._readlock_list[0]
            await lock.acquire()
            lock.release()
        if not self._dbwrite:
            self._dbwrite = _SqliteDbWrite()
            await self._dbwrite.connect(self._db_file)
        db = self._dbwrite
        try:
            yield db
            await db.commit()
        except:
            await db.rollback()
            raise
        finally:
            self._writelock.release()


class _SqliteDbRead():

    _db: aiosqlite.Connection

    async def connect(self, db_file: Path | str):
        self._db = await aiosqlite.connect(db_file, detect_types=sqlite3.PARSE_DECLTYPES)
        self._db.row_factory = sqlite3.Row

    async def fetchAll(self, sql: str, parameters: Iterable[Any] | None = None):
        async with self._db.execute(sql, parameters) as cursor:
            return cast(list[sqlite3.Row], await cursor.fetchall())

    async def fetchOne(self, sql: str, parameters: Iterable[Any] | None = None):
        async with self._db.execute(sql, parameters) as cursor:
            return await cursor.fetchone()

    async def close(self):
        await self._db.close()


class _SqliteDbWrite(_SqliteDbRead):

    async def insert(self, table: str, data: dict[str, Any]):
        keylist = sorted(data.keys())
        fieldname_list = ','.join([f'"{x}"' for x in keylist])
        placement_list = ','.join(['?' for _ in range(len(keylist))])
        fieldvalue_list = [data[x] for x in keylist]
        async with self._db.execute(
            f'''
            INSERT INTO "{table}" ({fieldname_list}) 
            VALUES 
                ({placement_list});
            ''',
            fieldvalue_list,
        ) as cursor:
            return cursor.lastrowid

    async def insertMany(self, table: str, dataList: Sequence[dict[str, Any]]):
        keyset: set[str] = set()
        for data in dataList:
            keyset.update(data.keys())
        keylist = sorted(keyset)
        fieldname_list = ','.join([f'`{x}`' for x in keylist])
        placement_list = ','.join(['?' for _ in range(len(keylist))])
        fieldvalue_list = [[data.get(key) for key in keylist] for data in dataList]
        async with self._db.executemany(
            f'''
            INSERT INTO "{table}" ({fieldname_list}) 
            VALUES 
                ({placement_list});
            ''',
            fieldvalue_list
        ) as _cursor:
            pass

    async def insertOrReplace(self, table: str, data: dict[str, Any]):
        keylist = sorted(data.keys())
        fieldname_list = ','.join([f'"{x}"' for x in keylist])
        placement_list = ','.join(['?' for _ in range(len(keylist))])
        fieldvalue_list = [data[x] for x in keylist]
        async with self._db.execute(
            f'''
            INSERT OR REPLACE INTO "{table}" ({fieldname_list}) 
            VALUES 
                ({placement_list});
            ''',
            fieldvalue_list,
        ) as _cursor:
            pass

    async def execute(self, sql: str, parameters: Iterable[Any] | None = None):
        async with self._db.execute(sql, parameters) as cursor:
            return cursor.rowcount

    async def commit(self):
        await self._db.commit()

    async def rollback(self):
        await self._db.rollback()

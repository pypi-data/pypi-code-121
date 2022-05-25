from typing import List

from fastapi import FastAPI, Request, Response

from dropland.storages.containers import with_async_engines


def add_middleware(
        app: FastAPI, sql_backends: List[str] = None, redis_names: List[str] = None,
        begin_sql_tx: bool = True, autocommit: bool = True):
    @app.middleware('http')
    async def __set_data_source_middleware(request: Request, call_next) -> Response:
        async with with_async_engines(sql_backends, redis_names, begin_sql_tx, autocommit):
            return await call_next(request)

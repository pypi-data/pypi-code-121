#!/usr/bin/env python
# encoding: utf-8
from concurrent.futures import ThreadPoolExecutor
import asyncio

class AsyncWrapper:
    def __init__(self, subject,methods=[], loop=None, max_workers=None):
        self.subject = subject
        self.methods = methods
        self.loop = loop or asyncio.get_event_loop()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def __getattr__(self, name):
        origin = getattr(self.subject, name)
        if callable(origin) and name in self.methods:
            def foo(*args, **kwargs):
                return self.run(origin, *args, **kwargs)

            # cache the function we built right now, to avoid later lookup
            self.__dict__[name] = foo
            return foo
        else:
            return origin

    async def run(self, origin_func, *args, **kwargs):
        def wrapper():
            return origin_func(*args, **kwargs)

        return await self.loop.run_in_executor(self.executor, wrapper)
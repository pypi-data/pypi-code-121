from aiohttp import web


@web.middleware
class Middleware:
    async def handler(self, request, handler):
        raise NotImplementedError()

    async def __call__(self, request, handler):
        return await self.handler(request, handler)

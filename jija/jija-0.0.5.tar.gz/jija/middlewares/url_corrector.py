from aiohttp import web


@web.middleware
async def slash_redirect(request, handler):
    if request.path[-1] != '/':
        raise web.HTTPFound(request.path + '/')

    response = await handler(request)
    return response

#!/usr/bin/env python
import asyncio
import json
import aiohttp
from typing import List, Dict
import aiofiles


async def func(url, target):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(target, mode='wb')
                await f.write(await resp.read())
                await f.close()


class AsyncClient(object):
    def __init__(self, url, loop=None):
        self.url = url
        self.loop = loop or asyncio.get_event_loop()

    async def get(self, url):
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                return await response.json()

    async def post(self, url, data):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                return await response.json()

    async def post_with_session(self, session, url, data):
        """ Different from the above method, this method will reuse aiohttp.ClientSession """
        async with session.post(url, data=data) as response:
            return await response.json()

    async def get_with_session(self, session, url):
        async with session.get(url) as response:
            return await response.json()

    async def concurrent_get(self, urls: List[str]):
        """ This method will use aiohttp.ClientSession to make multiple requests """
        async with aiohttp.ClientSession() as session:
            tasks = [asyncio.ensure_future(
                self.get_with_session(session, url)) for url in urls]
            return await asyncio.gather(*tasks)

    async def concurrent_post(self, urls: List[str], data):
        async with aiohttp.ClientSession() as session:
            tasks = [asyncio.ensure_future(
                self.post_with_session(session, url, data)) for url in urls
            ]
            return await asyncio.gather(*tasks)

    async def main(self):
        urls = [self.url] * 10
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self.concurrent_get(urls))
        print(resp)


if __name__ == '__main__':
    import base64
    b64url = 'aHR0cHM6Ly9pcGluZm8uaW8vanNvbj90b2tlbj03NzJjNGFmMDdhZTUxZgo='
    url = base64.b64decode(b64url).decode('utf-8').rstrip('\n')
    client = AsyncClient(url)
    asyncio.run(client.main())

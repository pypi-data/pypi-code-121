import aiohttp


class OpenLibraryApi(object):
    def __init__(self):
        self.session = None

    async def __aenter__(self, *args, **kwargs):
        self.session = aiohttp.ClientSession()
        await self.session.__aenter__(*args, **kwargs)
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.session.__aexit__(*args, **kwargs)

    async def search_book(self, q):
        async with self.session.get(f'http://openlibrary.org/search.json?q={q}') as response:
            return await response.json()


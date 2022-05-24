import aiohttp
import asyncio


class SunriseApi(object):
    def __init__(self, rate_limit=2):
        self.session = None
        self.semaphore = asyncio.Semaphore(rate_limit)

    async def __aenter__(self, *args, **kwargs):
        self.session = aiohttp.ClientSession()
        await self.session.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self.session.__aexit__(*args, **kwargs)

    async def get_sunrise_data(self, lat, lon):
        async with self.semaphore:
            async with self.session.get(f'https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}') as response:
                return await response.json()

    async def get_sunrise_data_dummy(self, lat, lon):
        async with self.semaphore:
            await asyncio.sleep(1)
            return (lat, lon)

import itertools
import aiohttp
import asyncio
import logging

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


def get_sunrise_data(api, gps_positions):
    tasks = []
    for lat, lon in gps_positions:
        async def run(lat, lon):
            logging.debug(f'Starting {lat} {lon}')
            result = await api.get_sunrise_data_dummy(lat, lon)
            logging.debug(f'Ending {lat} {lon}')
            return result

        tasks.append(run(lat, lon))
    return tasks


async def async_main():
    logging.basicConfig(level=logging.DEBUG)
    async with SunriseApi(rate_limit=100) as api:
        gps_positions = itertools.product(
            range(-90, 90, 10),
            range(0, 360, 10)
        )

        await asyncio.gather(
            *get_sunrise_data(api, gps_positions)
        )


def main():
    asyncio.run(async_main())


if __name__ == '__main__':
    main()

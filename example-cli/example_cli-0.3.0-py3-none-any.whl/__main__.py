import aiohttp
import asyncio
import json
import itertools
import logging
from .sunrise import SunriseApi


def log(doc):
    print(json.dumps(doc, indent=4))


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

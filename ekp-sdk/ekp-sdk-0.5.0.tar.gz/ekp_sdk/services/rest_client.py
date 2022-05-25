import json
import time

import aiohttp
from aioretry import retry
from ekp_sdk.services.limiter import Limiter
from ekp_sdk.util.retry import default_retry_policy


class RestClient:

    @retry(default_retry_policy)
    async def get(
        self,
        url,
        fn=lambda data, text: data,
        limiter: Limiter = None
    ):
        if limiter is not None:
            await limiter.acquire()
        
        try:
            async with aiohttp.ClientSession() as session:
                print(f"🐛 GET {url}")
                start = time.perf_counter()
                response = await session.get(url=url)

                if (response.status != 200):
                    raise Exception(f"Response code: {response.status}")

                text = await response.read()
                data = json.loads(text.decode())

                print(f"⏱  GET [{url}] {time.perf_counter() - start:0.3f}s")

                return fn(data, text)
        finally:
            if limiter is not None:
                limiter.release()

    async def post(
        self,
        url,
        data,
        fn=lambda data, text: data,
        limiter: Limiter = None
    ):
        if limiter is not None:
            await limiter.acquire()

        try:
            async with aiohttp.ClientSession() as session:
                print(f"🐛 POST {url}")
                start = time.perf_counter()
                response = await session.post(url=url, data=json.dumps(data), headers={"content-type": "application/json"})

                if (response.status not in [200, 201]):
                    raise Exception(f"Response code: {response.status}")

                text = await response.read()
                data = None
                if text:
                    data = json.loads(text.decode())

                print(f"⏱  POST [{url}] {time.perf_counter() - start:0.3f}s")

                return fn(data, text)
        finally:
            if limiter is not None:
                limiter.release()
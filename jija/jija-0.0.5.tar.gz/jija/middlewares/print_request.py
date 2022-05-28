import datetime
import time

from aiohttp.web_exceptions import HTTPNotFound
from jija.middleware import Middleware


class PrintRequest(Middleware):
    async def handler(self, request, handler):
        timer = time.time()
        try:
            response = await handler(request)
        except HTTPNotFound as exception:
            PrintRequest.print(timer, 404, request.url)
            raise exception

        except Exception as exception:
            PrintRequest.print(timer, 500, request.url)
            raise exception

        PrintRequest.print(timer, response.status, request.url)
        return response

    @classmethod
    def print(cls, timer, status, url):
        timer = time.time() - timer
        time_label = f'{datetime.datetime.today().replace(microsecond=0)}'
        print(f'[{time_label}] [{round(timer, 4)} s] [{status}] {str(url).split("?")[0]}')

from aiohttp import ClientSession
from typing import no_type_check
# from loguru import logger


class BaseModel:
    def __init__(self):
        self.domain = "https://api.elschool.ru/api/"

    @no_type_check
    def get_set_params(cls, params: dict) -> dict:
        exclude_params = params.copy()
        exclude_params.update(params["kwargs"])
        exclude_params.pop("kwargs")
        return {
            k if not k.startswith("_") else k[1:]: v
            for k, v in exclude_params.items()
            if k != "self" and k != "url" and v is not None
        }

    async def _request(self, request: str, url: str, query: dict):
        """
        :param request: type of request get/post
        :param url: api url
        :param query: api query
        :return: response api server
        """

        url = self.domain + url  # https://api.elschool.ru/api/ + method

        async with ClientSession() as session, \
                session.request(request, url, params=query) as response:
            # logger.debug(f"Request sent to '{url}', status: {response.status}")
            return response.status, await response.json(content_type="text/plain; charset=utf-8")

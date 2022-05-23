import asyncio
import aiohttp
import json
import logging

logger = logging.getLogger(__name__)

class BaseClient:

    def __init__(self, url, session=None, identity=None):
        self._url = url
        self._session = session

        if identity is None:
            self._identity = {"token": "ZHVtbXlfdG9rZW4="}
        else:
            self._identity = identity

    async def __aenter__(self):
        return self

    async def __aexit__(self, exception_type, exception_value, traceback):
        await self.close() 

    async def close(self):
        if self._session:
            await self._session.close()

    async def do_get(self, path, options={}):
        headers = self.__get_default_headers()
        headers.update(options.get('headers', {}))
        headers.update(self.__get_auth_headers())

        request_url = f"{self._url}{path}"

        async with aiohttp.ClientSession() as session:

            current_session = self._session if self._session else session

            async with current_session.get(request_url, headers=headers) as response:
                response.raise_for_status()
                if response.status == 200:
                    return await response.json()

    async def do_delete(self, path, options={}):
        headers = self.__get_default_headers()
        headers.update(options.get('headers', {}))
        headers.update(self.__get_auth_headers())

        request_url = f"{self._url}{path}"

        async with aiohttp.ClientSession() as session:

            current_session = self._session if self._session else session

            async with current_session.delete(request_url, headers=headers) as response:
                response.raise_for_status()
                if response.status == 200:
                    return await response.json()

    async def do_post(self, path, payload, options={}):
        headers = self.__get_default_headers()
        headers.update(options.get('headers', {}))
        headers.update(self.__get_auth_headers())

        request_url = f"{self._url}{path}"

        logger.debug(f"post request to {request_url} with json payload {payload}")

        async with aiohttp.ClientSession() as session:

            current_session = self._session if self._session else session

            async with current_session.post(request_url, json=payload, headers=headers) as response:
                logger.debug(f"handle response {response.status}")
                response.raise_for_status()
                if response.status in [200, 201, 202]:
                    return await response.json()
                elif response.status == 204:
                    return ""
                else:
                    raise Exception(f"TODO: need a better error {response.status}")
    
    async def do_put(self, path, payload, options={}):
        headers = self.__get_default_headers()
        headers.update(options.get('headers', {}))
        headers.update(self.__get_auth_headers())

        request_url = f"{self._url}{path}"

        logger.debug(f"put request to {request_url} with json payload {payload}")

        async with aiohttp.ClientSession() as session:

            current_session = self._session if self._session else session

            async with current_session.put(request_url, json=payload, headers=headers) as response:
                logger.debug(f"handle response {response.status}")
                response.raise_for_status()
                if response.status in [200, 201, 202]:
                    return await response.json()
                elif response.status == 204:
                    return ""
                else:
                    raise Exception(f"TODO: need a better error {response.status}")
    
    async def get_serverinfo(self):
        return await self.do_get('/atlas_engine/api/v1/info')

    def __get_auth_headers(self):
        identity = self.__get_identity()
        token = identity['token']
        return {'Authorization': 'Bearer {}'.format(token)}

    def __get_default_headers(self):
        return {'Content-Type': 'application/json'}

    def __get_identity(self):
        identity = self._identity

        if callable(self._identity):
            identity = self._identity()

        return identity
            

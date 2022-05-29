from . import _AbstractAsyncClient
from . import _AbstractClient
from ..schemas import Team


class _TeamsClient(_AbstractClient):
    def list(self):
        """Gets teams and yields them as a generator"""
        response = self._http_get()
        response_json = response.json()
        if isinstance(response_json, list):
            if len(response_json) == 0:
                return
            else:
                for team in response_json:
                    yield Team(**team)
        else:
            yield Team(**response_json)


class _TeamsAsyncClient(_AbstractAsyncClient):
    async def list(self):
        """Gets teams and yields them as a generator"""
        response = await self._http_get()
        response_json = response.json()
        if isinstance(response_json, list):
            if len(response_json) == 0:
                return
            else:
                for team in response_json:
                    yield Team(**team)
        else:
            yield Team(**response_json)

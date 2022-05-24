from .generic_config import GenericConfig
import aiohttp

class ConfigAsync(GenericConfig):        
    def __init__(self, API, API_SECRET, staging):
        super().__init__(API, API_SECRET, staging)

    def __client_creator(self):
        return aiohttp.ClientSession(
            headers=self._headers()
        )
        
    def __build_session_method(self, method, session):
        if method == "GET":
            return session.get(self.url)
        elif method == "POST":
            return session.post(self.url)
        
    async def requests_and_parse(self, method):
        async with self.__client_creator() as session:
            async with self.__build_session_method(method, session) as response:
                return await response.json()
       
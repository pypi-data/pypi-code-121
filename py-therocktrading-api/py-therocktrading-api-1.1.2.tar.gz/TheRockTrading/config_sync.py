from .generic_config import GenericConfig
import httpx



class ConfigSync(GenericConfig):  
    def __init__(self, API, API_SECRET, staging):
        super().__init__(API, API_SECRET, staging)

    def __exit__(self):
        self.__client.close()
         
    def __client_creator(self):
        self.__client = httpx.Client(
            http2 = True,
            headers = self._headers(),
            limits = httpx.Limits(max_connections=10),
            timeout = None
        )

    def requests_and_parse(self, method):
        self.__client_creator()
        response = self.__client.send(
            self.__client.build_request(method, self.url)
        ).json()
        return response
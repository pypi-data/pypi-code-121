import requests

from utils.config import serverUrl, headers
from utils.helpers import ApiResourceIterator


class Currencies:
    path = "/v1/locale/currencies"

    def __init__(self, apiToken):
        self.token = apiToken

    def get_all(self, limit=5):
        params = {
            "limit": str(limit)
        }
        response = requests.request("GET",
                                    serverUrl() + self.path,
                                    headers=headers(self.token),
                                    params=params)
        return response.json()['data']

    def find(self, countryId=None):
        return ApiResourceIterator(self.token, self.path, params={"countryId": countryId})

    def get_by_country_id(self, countryId, limit=5):
        params = {
            "limit": str(limit),
            "countryId": countryId
        }
        response = requests.request("GET",
                                    serverUrl() + self.path,
                                    headers=headers(self.token),
                                    params=params)
        return response.json()['data']


if __name__ == "__main__":
    print(Currencies("402acade62msh388e91d32480224p1e4fd2jsn998d47344407").get_by_country_id('PT'))

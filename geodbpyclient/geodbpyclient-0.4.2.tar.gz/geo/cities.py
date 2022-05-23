import time

import requests

from utils.config import serverUrl, headers
from utils.helpers import ApiResourceIterator, ResourceGetter


class Cities(ResourceGetter):
    path = "/v1/geo/cities"

    def __init__(self, apiToken):
        super().__init__(apiToken)

    def get_all(self, limit=5, offset=0):
        params = {
            "limit": str(limit),
            "offset": str(offset)
        }
        response = requests.request("GET",
                                    serverUrl() + self.path,
                                    headers=headers(self.token),
                                    params=params)
        return response.json()['data']

    def get_by_country_id(self, countryId, limit=5, offset=0):
        params = {
            "limit": str(limit),
            "offset": str(offset),
            "countryIds": countryId
        }
        response = requests.request("GET",
                                    serverUrl() + self.path,
                                    headers=headers(self.token),
                                    params=params)
        return response.json()['data']

    def find(self, countryId=None):
        return ApiResourceIterator(self.token, self.path, params={"countryIds": countryId})

    def get_by_id(self, cityId):
        return self.get(cityId)


if __name__ == "__main__":
    print(Cities("402acade62msh388e91d32480224p1e4fd2jsn998d47344407").get("3270202"))

    # for city in Cities("402acade62msh388e91d32480224p1e4fd2jsn998d47344407").find("us"):
    # print(city)
    # time.sleep(0.11)

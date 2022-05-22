import requests

from utils.config import serverUrl, headers
from utils.helpers import ApiResourceIterator


class TimeZones:
    def __init__(self, apiToken):
        self.token = apiToken

    path = "/v1/locale/timezones"

    def get_all(self, limit=5, offset=0):
        params = {
            "limit": str(limit),
            "offset": str(offset)
        }
        response = requests.request("GET",
                                    serverUrl() + self.path,
                                    headers=headers(self.token),
                                    params=params)
        return response.json()

    def find(self):
        return ApiResourceIterator(self.token, self.path)

    def get_by_id(self, zoneId):
        return self.get(zoneId)

    def get(self, zoneId):
        response = requests.request("GET",
                                    serverUrl() + self.path + "/" + zoneId,
                                    headers=headers(self.token), )
        return response.json()['data']

    def time_in_zone(self, zoneId):
        response = requests.request("GET",
                                    serverUrl() + self.path + "/" + zoneId + "/" + "time",
                                    headers=headers(self.token), )
        return response.json()['data']


if __name__ == "__main__":
    print(TimeZones("402acade62msh388e91d32480224p1e4fd2jsn998d47344407").time_in_zone('America__Cuiaba'))

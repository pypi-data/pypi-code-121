import requests

from utils.config import serverUrl, headers
from utils.helpers import ApiResourceIterator, ResourceGetter


class TimeZones(ResourceGetter):
    def __init__(self, apiToken):
        super().__init__(apiToken)

    path = "/v1/locale/timezones"

    def find(self, **kwargs):
        return ApiResourceIterator(self.token, self.path)

    def time_in_zone(self, zoneId):
        response = requests.request("GET",
                                    serverUrl() + self.path + "/" + zoneId + "/" + "time",
                                    headers=headers(self.token), )
        return response.json()['data']

    def find_criteria(self):
        return []

if __name__ == "__main__":
    print(TimeZones("402acade62msh388e91d32480224p1e4fd2jsn998d47344407").get('America__Cuiaba'))

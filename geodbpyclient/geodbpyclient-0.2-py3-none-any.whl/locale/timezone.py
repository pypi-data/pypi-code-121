import requests

from utils.config import serverUrl, headers


class TimeZones:
    def __init__(self, apiToken):
        self.token = apiToken

    path = "/v1/locales/timezones"

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

    def get_by_id(self, zoneId):
        response = requests.request("GET",
                                    serverUrl() + self.path + "/" + zoneId,
                                    headers=headers(self.token),)
        return response.json()

    def time_in_zone(self, zoneId):
        response = requests.request("GET",
                                    serverUrl() + self.path + "/" + zoneId + "/" + "time",
                                    headers=headers(self.token), )
        return response.json()


if __name__ == "__main__":
    print(TimeZones("402acade62msh388e91d32480224p1e4fd2jsn998d47344407").time_in_zone('America__Cuiaba'))

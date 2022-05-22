import requests

from utils.config import serverUrl, headers


class Countries:
    path = "/v1/geo/countries"

    def __init__(self, apiToken):
        self.token = apiToken

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

    def get_by_id(self, countryId):
        response = requests.request("GET",
                                    serverUrl() + self.path + "/" + countryId,
                                    headers=headers(self.token))
        return response.json()

    def find_by_name(self, countryName, limit=5, offset=0):
        params = {
            "limit": str(limit),
            "offset": str(offset),
            "namePrefix": countryName
        }
        response = requests.request("GET",
                                    serverUrl() + self.path,
                                    headers=headers(self.token),
                                    params=params)
        return response.json()


if __name__ == "__main__":
    print(Countries("402acade62msh388e91d32480224p1e4fd2jsn998d47344407").get_by_id("US"))

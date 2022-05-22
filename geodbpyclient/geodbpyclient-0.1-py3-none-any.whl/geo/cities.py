import requests

from utils.config import serverUrl, headers


class Cities:
    path = "/v1/geo/cities"

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
        return response.json()

    def get_by_id(self, cityId):
        response = requests.request("GET",
                                    serverUrl() + self.path + "/" + cityId,
                                    headers=headers(self.token))
        return response.json()


if __name__ == "__main__":
    print(Cities("402acade62msh388e91d32480224p1e4fd2jsn998d47344407").get_by_id('Q24668'))

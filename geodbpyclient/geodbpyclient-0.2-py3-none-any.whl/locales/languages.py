import requests as requests

from utils.config import serverUrl, headers


class Languages:
    path = "/v1/locales/languages"

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
        return response.json()


if __name__ == "__main__":
    print(Languages("402acade62msh388e91d32480224p1e4fd2jsn998d47344407").get_all(8))
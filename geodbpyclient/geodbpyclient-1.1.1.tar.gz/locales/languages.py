import requests as requests

from utils.config import serverUrl, headers
from utils.helpers import ApiResourceIterator


class Languages:
    path = "/v1/locale/languages"

    def __init__(self, apiToken):
        self.token = apiToken

    def find(self, **kwargs):
        try:
            countryId = kwargs['countryId']
        except KeyError:
            countryId = None
        return ApiResourceIterator(self.token, self.path, params={"countryId": countryId})

    def find_criteria(self):
        return ["countryId"]


if __name__ == "__main__":
    print(Languages("402acade62msh388e91d32480224p1e4fd2jsn998d47344407").find())

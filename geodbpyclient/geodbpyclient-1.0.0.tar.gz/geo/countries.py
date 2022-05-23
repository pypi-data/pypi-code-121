import time

import requests

from utils.config import serverUrl, headers
from utils.helpers import ApiResourceIterator, ResourceGetter


class Countries(ResourceGetter):
    path = "/v1/geo/countries"

    def __init__(self, apiToken):
        super().__init__(apiToken)

    def find(self, countryName=None):
        return ApiResourceIterator(self.token, self.path, params={"namePrefix": countryName})


if __name__ == "__main__":
    for item in Countries("402acade62msh388e91d32480224p1e4fd2jsn998d47344407").find():
        print(item)
        time.sleep(0.11)

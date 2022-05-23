import time

import requests

from utils.config import serverUrl, headers
from utils.helpers import ApiResourceIterator, ResourceGetter


class Countries(ResourceGetter):
    path = "/v1/geo/countries"

    def __init__(self, apiToken):
        super().__init__(apiToken)

    def find(self, **kwargs):
        try:
            countryName = kwargs['countryName']
        except KeyError:
            countryName = None
        # print(countryName)
        return ApiResourceIterator(self.token, self.path, params={"namePrefix": countryName})

    def find_criteria(self):
        return ["countryName"]


if __name__ == "__main__":
    for item in Countries("402acade62msh388e91d32480224p1e4fd2jsn998d47344407").find(countryName="a"):
        print(item)
        time.sleep(0.11)

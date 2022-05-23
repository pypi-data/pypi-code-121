import time

import requests

from utils.config import serverUrl, headers
from utils.helpers import ApiResourceIterator, ResourceGetter


class Divisions(ResourceGetter):
    path = "/v1/geo/adminDivisions"

    def __init__(self,  apiToken):
        super().__init__(apiToken)

    def find(self, **kwargs):
        try:
            countryId = kwargs['countryId']
        except KeyError:
            countryId = None
        return ApiResourceIterator(self.token, self.path, params={"countryIds": countryId})

    def find_criteria(self):
        return ["countryId"]


if __name__ == "__main__":
    argname = 'countryId'
    # for item in Divisions("402acade62msh388e91d32480224p1e4fd2jsn998d47344407").find(**{argname: "US"}):
    for item in Divisions("402acade62msh388e91d32480224p1e4fd2jsn998d47344407").find():
        print(item)
        time.sleep(0.12)

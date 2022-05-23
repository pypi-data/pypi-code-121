import requests

from utils.config import serverUrl, headers
from utils.helpers import ApiResourceIterator, ResourceGetter


class Divisions(ResourceGetter):
    path = "/v1/geo/adminDivisions"

    def __init__(self,  apiToken):
        super().__init__(apiToken)

    def find(self, countryId=None):
        return ApiResourceIterator(self.token, self.path, params={"countryIds": countryId})


if __name__ == "__main__":
    print(Divisions("402acade62msh388e91d32480224p1e4fd2jsn998d47344407").get("Q2670909"))

"""Mock ApiClient for requests to get packages and projects.
"""
import json
import os

import package_fixtures

PROJECTS_RESPONSE = {"data": [
    {"id": "123|deadpool", "name": "Deadpool",
     "status": "active"},
    {"id": "456|harrypotter", "name": "Harry Potter & the chamber of secrets",
     "status": "active"},
    {"id": "789|corelli", "name": "Captain Corelli's Mandolin",
     "status": "active"},
    {"id": "000|gwtw", "name": "Gone with the Wind",
     "status": "inactive"}
]}

PACKAGES_RESPONSE = {"data": package_fixtures.SOFTWARE_DATA}

class ApiClient(object):
    def make_request(self, **kw):
        path = kw.get("uri_path", "")

        print("Using mock %s call to %s" % (self.__class__.__name__, path))

        if path.startswith("api/v1/projects"):
            return [json.dumps(PROJECTS_RESPONSE), 200]

        if path.startswith("api/v1/ee/packages"):
            return [json.dumps(PACKAGES_RESPONSE), 200]

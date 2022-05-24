"""Data class for Northstar API."""

# Standard library
from typing import Any
import copy
import json
import urllib3

# Third Party
import requests

# Local
from pydantic import BaseModel

# Disable HTTPS local certificate warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NorthstarHelper(BaseModel):
    """Helper for interacting with the Northstar API."""

    server: dict
    project: dict
    api_token: str = ""
    auth: str = ""
    baseurl: str = ""
    headers: dict = {}
    index: int = 0

    def __init__(self, **data: Any):
        """
        Here we manipulate pydandic's BaseModel auto-generated __init__ method.
          - create json payload based on data stored in YAML config file
          - create a new baseurl with data stored in YAML config file
          - create authenticated call headers, `create_token()` is an exception
          - create API token by calling our create_token() method
        """

        super().__init__(**data)

        self.auth = json.dumps(self.server["auth"])
        self.baseurl = f'https://{self.server["baseurl"]}'

        # create a new API token for our session
        self.api_token = self.create_token()

        self.headers = {
            "Accept": "*/*",
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

        # check if api_token is valid by testing the get_projects() method.
        self.get_license()

    def _path_strip(self, path):
        """Strip off leading / within the url path and return full url."""

        if path[0] == "/":
            path = path[1:]

        return f"{self.baseurl}/{path}"

    def get(self, path, headers):
        """HTTP GET method."""
        return self.send("GET", path, headers)

    def put(self, path, headers, data=None):
        """HTTP PUT method."""
        return self.send("PUT", path, headers, data)

    def post(self, path, headers, data=None):
        """HTTP POST method."""
        return self.send("POST", path, headers, data)

    def delete(self, path, headers, data=None):
        """HTTP DELETE method."""
        return self.send("DELETE", path, headers, data)

    def send(self, method, path, headers, data=None):
        """Build the URL, handle the response of API calls."""

        url = self._path_strip(path)

        print(f"url: {url}")
        print(f"method: {method}")
        print(f"path: {path}")
        print(f"headers: {headers}")
        print(f"data: {data}")

        response = requests.request(
            method,
            url,
            headers=headers,
            data=json.dumps(data),
            verify=False,
        )
        response.raise_for_status()

        return response

    def create_project(self):
        """Create our project for this session."""

        try:
            response = self.post("epe-plan", self.headers, self.project["meta"])
            response.raise_for_status()

            if response.status_code == 401:
                return "API Token has expired."

            if response.status_code == 202:
                index = response.json()
                self.index = index["projectIndex"]

                return response

        except requests.exceptions.RequestException as response_error:
            # Gracefully exit upon reaching an error
            raise SystemExit from response_error

    def create_token(self):
        """Create API token for our session."""

        try:
            response = self.post(
                "oauth2/token", self.server["headers"], self.server["auth"]
            )
            response.raise_for_status()

            if response.status_code == 401:
                return "API Token has expired."

            if response.status_code == 200:
                token_info = response.json()
                token = token_info["access_token"]
                return token

        except requests.exceptions.RequestException as response_error:
            # Gracefully exit upon reaching an error
            raise SystemExit from response_error

    def delete_project(self, project_id):
        """Delete a project."""

        try:
            response = self.delete(f"/epe-plan/{project_id}", self.headers)
            response.raise_for_status()

            if response.status_code == 401:
                return "Failed to login using API token, verify YAML config."

            if response.status_code == 204:
                return "Project deleted"

        except requests.exceptions.RequestException as response_error:
            # Gracefully exit upon reaching an error
            raise SystemExit from response_error

    def get_license(self):
        """Testing API reachability with a license pull."""

        try:
            """
            We need to specify headers, Northstar is very specific.
            We pop off two headers and insert our own to send:
            {
                'Authorization': 'Bearer apitokenhere',
                'Accept': 'application/json'
            }
            """
            headers_copy = copy.deepcopy(self.headers)
            headers_copy.pop("Content-Type")
            headers_copy.pop("Accept")
            headers_copy["Accept"] = "application/json"

            response = self.get("licenseCheck", headers=headers_copy)
            response.raise_for_status()

            if response.status_code == 400:
                return "Northstar doesn't like this request, please check your headers."

            if response.status_code == 200:
                license_info = response.json()
                customer_name = license_info["customerName"]
                return f"Successfully authenticated, license details: {customer_name}"

        except requests.exceptions.RequestException as response_error:
            # Gracefully exit upon reaching an error
            raise SystemExit from response_error

    def get_projects(self):
        """Request a list of all projects."""

        try:
            headers_copy = copy.deepcopy(self.headers)
            headers_copy.pop("Content-Type")

            response = self.get("epe-plan", headers=headers_copy)
            response.raise_for_status()

            if response.status_code == 200:
                return response.json()

        except requests.exceptions.RequestException as response_error:
            # Gracefully exit upon reaching an error
            raise SystemExit from response_error

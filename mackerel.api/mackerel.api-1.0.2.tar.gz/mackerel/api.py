import json

import requests


class Client:
    def __init__(self, api_key: str = "", version: str = "v0") -> None:
        self.base_url = "https://api.mackerelio.com/api/{}".format(version)
        self.headers = {
            "Content-type": "application/json",
            "X-Api-Key": api_key,
        }

    def get(self, path: str = "", params: dict = {}) -> requests.Response:
        return requests.get(self.base_url + path, headers=self.headers, params=params)

    def post(self, path: str = "", data: dict = {}) -> requests.Response:
        return requests.post(
            self.base_url + path, headers=self.headers, data=json.dumps(data)
        )

    def put(self, path: str = "", data: dict = {}) -> requests.Response:
        return requests.put(
            self.base_url + path,
            headers=self.headers,
            data=json.dumps(data),
        )

    def delete(self, path: str = "") -> requests.Response:
        return requests.delete(
            self.base_url + path,
            headers=self.headers,
        )

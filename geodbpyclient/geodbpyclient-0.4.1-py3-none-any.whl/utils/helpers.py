import requests

from utils.config import serverUrl, headers


class ApiResourceIterator:
    count = 0
    response = []
    limit = 10

    def __init__(self, apiToken, path, params=None):
        self.token = apiToken
        self.path = path
        self.nextPath = path
        if params is None:
            params = {}
        self.params = params
        self.params['limit'] = self.limit

    def get_next(self):
        response = requests.request("GET",
                                    serverUrl() + self.nextPath,
                                    headers=headers(self.token),
                                    params=self.params)
        try:
            self.nextPath = response.json()['links'][1]['href']
        except KeyError:
            self.nextPath = None
        return response.json()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            self.count += 1
            return self.response[self.count - 1]
        except IndexError:
            self.count = 0
            self.response = self.get_next()['data']
            if len(self.response) == 0 or self.nextPath is None:
                raise StopIteration
            else:
                self.count += 1
                return self.response[self.count - 1]

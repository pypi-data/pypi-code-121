import requests

from utils.config import serverUrl, headers


class ResourceGetter:
    def __init__(self, apiToken):
        self.token = apiToken

    def get(self, resourceId):
        response = requests.request("GET",
                                    serverUrl() + self.path + "/" + resourceId,
                                    headers=headers(self.token))
        try:
            return response.json()['data']
        except KeyError:
            return None


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
        response = None
        try:
            response = requests.request("GET",
                                        serverUrl() + self.nextPath,
                                        headers=headers(self.token),
                                        params=self.params)
            self.params = None
            # print(response.json())
            self.nextPath = response.json()['links'][1]['href']
        except TypeError:
            raise StopIteration
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
            try:
                tmp = self.get_next()
                self.response = tmp['data']
            except KeyError:
                raise ApiException(tmp['message'])
            if len(self.response) == 0:
                raise StopIteration
            else:
                self.count += 1
                return self.response[self.count - 1]


class ApiException(Exception):
    pass

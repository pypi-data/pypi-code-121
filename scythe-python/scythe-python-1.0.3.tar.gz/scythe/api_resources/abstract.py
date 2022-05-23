from itertools import count
from scythe.request_resource import RequestClient, Response

from typing import Dict, List


class AbstractObject(object):
    def __init__(self, response: Response, list_object: bool = False):
        self._response = response
        self._success = response.success
        for key, value in response.data.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return str(self._response.data)

    def __repr__(self) -> str:
        return str(self._response.data)


class AbstractListObject(object):
    def __init__(self, data: Dict):
        self._data = data
        for key, value in self._data.items():
            setattr(self, key, value)

    def __str__(self) -> str:
        return str(self._data)

    def __repr__(self) -> str:
        return str(self._data)


class AbstractList(object):
    def __init__(self, response: Response):
        self._response = response
        self._success = response.success

        self.count = response.data['count']
        self.next = response.data['next']
        self.previous = response.data['previous']
        self.objects = []
        for result in response.data['results']:
            self.objects.append(AbstractListObject(data=result))

    def __getitem__(self, indx):
        return self.objects[indx]

    def __str__(self) -> str:
        return str(self.objects)

    def __repr__(self) -> str:
        return str(self.objects)


class AbstractResource(object):
    def __init__(self, client: RequestClient):
        self.client = client

    def fetch(self, params: Dict, api_key: str = None) -> AbstractObject:
        response = self.client.get(url=self.OBJECT_NAME, params=params)
        return AbstractObject(response=response)

    def list(self, params: Dict, api_key: str = None) -> AbstractList:
        response = self.client.get(url=self.OBJECT_NAME, params=params)
        return AbstractList(response=response)

    def create(self, data: Dict, api_key: str = None) -> AbstractObject:
        response = self.client.post(url=self.OBJECT_NAME, data=data)
        return AbstractObject(response=response)

    def update(self, data: Dict, api_key: str = None) -> AbstractObject:
        response = self.client.put(url=self.OBJECT_NAME, data=data)
        return AbstractObject(response=response)

    def delete(self, data: Dict, api_key: str = None) -> AbstractObject:
        response = self.client.delete(url=self.OBJECT_NAME, data=data)
        return AbstractObject(response=response)

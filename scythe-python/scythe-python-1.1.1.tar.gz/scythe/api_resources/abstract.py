from scythe.exceptions import NotFoundError, MultipleResultsError
from scythe.request_resource import RequestClient, Response

from typing import Dict, List


class SingleAbstractObject(object):
    def __init__(self, data, attrs=None):
        for key, value in data.items():
            if attrs is not None:
                if key not in attrs:
                    continue
            if isinstance(value, (list, tuple)):
                setattr(self, key, [SingleAbstractObject(val) if isinstance(
                    val, dict) else val for val in value])
            else:
                setattr(self, key, SingleAbstractObject(value)
                        if isinstance(value, dict) else value)

    def __str__(self) -> str:
        return str(self.__dict__)

    def __repr__(self) -> str:
        return str(self.__dict__)


class AbstractObject(object):
    base_attrs = ['id', 'updated_on']

    def __init__(self, response: Response, attrs: List[str]):
        self.response = response
        self.success = response.success
        if not self.success:
            self.object = SingleAbstractObject({})
            return

        self.object = SingleAbstractObject(
            data=response.data, attrs=attrs + self.base_attrs
        )

    def __str__(self) -> str:
        return str(self.object)

    def __repr__(self) -> str:
        return str(self.object)


class AbstractListObject(object):
    base_attrs = ['id', 'updated_on']

    def __init__(self, data: Dict, attrs: List[str]):
        self.object = SingleAbstractObject(
            data=data, attrs=attrs + self.base_attrs
        )

    def __str__(self) -> str:
        return str(self.object)

    def __repr__(self) -> str:
        return str(self.object)


class AbstractList(object):

    def __init__(self, response: Response, attrs: List[str]):
        self.response = response
        self.success = response.success
        if not self.success:
            self.objects = []
            return

        self.count = response.data['count']
        self.next = response.data['next']
        self.previous = response.data['previous']

        # Objects
        self.objects = []
        for result in response.data['results']:
            self.objects.append(AbstractListObject(data=result, attrs=attrs))

    def __getitem__(self, indx):
        return self.objects[indx]

    def __str__(self) -> str:
        return str(self.objects)

    def __repr__(self) -> str:
        return str(self.objects)


class AbstractResource(object):
    attrs = []

    def __init__(self, client: RequestClient):
        self.client = client

    def fetch(self, raise_exception=False, **kwargs) -> AbstractObject:
        response = self.client.get(
            url=self.OBJECT_NAME, params=kwargs, raise_exception=raise_exception,
            single_object=True
        )
        return AbstractObject(response=response, attrs=self.attrs)

    def fetch_or_create(self, raise_exception=False, **kwargs) -> AbstractObject:
        try:
            response = self.client.get(
                url=self.OBJECT_NAME, params=kwargs, raise_exception=raise_exception,
                single_object=True
            )
        except NotFoundError:
            return self.create(data=kwargs, raise_exception=raise_exception)
        return AbstractObject(response=response, attrs=self.attrs)

    def list(self, raise_exception=False, **kwargs) -> AbstractList:
        response = self.client.get(
            url=self.OBJECT_NAME, params=kwargs, raise_exception=raise_exception
        )
        return AbstractList(response=response, attrs=self.attrs)

    def create(self, data: Dict, raise_exception=False) -> AbstractObject:
        response = self.client.post(
            url=self.OBJECT_NAME, data=data, raise_exception=raise_exception
        )
        return AbstractObject(response=response, attrs=self.attrs)

    def update(self, data: Dict, raise_exception=False) -> AbstractObject:
        response = self.client.put(
            url=self.OBJECT_NAME, data=data, raise_exception=raise_exception
        )
        return AbstractObject(response=response, attrs=self.attrs)

    def deactivate(self, data: Dict, raise_exception=False) -> AbstractObject:
        response = self.client.delete(
            url=f"{self.OBJECT_NAME}/deactivate/", data=data, raise_exception=raise_exception
        )
        return AbstractObject(response=response)

    def activate(self, data: Dict, raise_exception=False) -> AbstractObject:
        response = self.client.delete(
            url=f"{self.OBJECT_NAME}/activate/", data=data, raise_exception=raise_exception
        )
        return AbstractObject(response=response)

    def delete(self, data: Dict, raise_exception=False) -> AbstractObject:
        response = self.client.delete(
            url=self.OBJECT_NAME, data=data, raise_exception=raise_exception
        )
        return AbstractObject(response=response)

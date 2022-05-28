from typing import Dict, Type, List

from .abstract import AbstractContainer, AbstractResource, R
from .errors import ResourceNotFound


class Container(AbstractContainer):

    def __init__(self, resources: Dict[str, AbstractResource]):
        self.resources = resources

    def get(self, name: str, context: AbstractContainer = None, _type: Type[R] = object) -> R:
        if name == 'context':
            return context or self
        resource = self.resources.get(name)
        if not resource:
            raise ResourceNotFound(context or self, name)
        return resource.resolve(context or self, name)

    def has(self, name: str, context: AbstractContainer = None) -> bool:
        return name == 'context' or name in self.resources.keys()

    def resource_names(self) -> list:
        return ['context', *self.resources.keys()]


class ContainerGroup(AbstractContainer):

    def __init__(self, containers: List[AbstractContainer]):
        self.containers = containers
        self._cache = {}
        self._resource_names_cache = {}

    def get(self, name: str, context: AbstractContainer = None, _type: Type[R] = object) -> R:
        if name not in self._cache.keys():
            for container in self.containers:
                if container.has(name, context or self):
                    self._cache[name] = lambda: container.get(name, context or self, _type)
                    break
            else:
                raise ResourceNotFound(context or self, name)
        return self._cache[name]()

    def has(self, name: str, context: AbstractContainer = None) -> bool:
        return name in self._cache.keys() or any(container.has(name, context or self) for container in self.containers)

    def resource_names(self) -> list:
        if not self._resource_names_cache:
            self._resource_names_cache = list(dict.fromkeys([item for container in self.containers for item in container.resource_names()]))
        return self._resource_names_cache


class CacheContainer(AbstractContainer):

    def __init__(self, context_name: str, container: AbstractContainer):
        self.container = container
        self.cache = {}
        self.context_name = context_name

    def get(self, name: str, context: AbstractContainer = None, _type: Type[R] = object) -> R:
        if name == 'scope':
            return self.context_name
        if name not in self.cache.keys():
            resource = self.container.get(name, context or self, _type)
            if self.context_name in getattr(resource, '__singleton__', ['runtime']):
                self.cache[name] = resource
            else:
                return resource
        return self.cache[name]

    def has(self, name: str, context: AbstractContainer = None) -> bool:
        return name == 'scope' or self.container.has(name, context or self)

    def resource_names(self) -> list:
        return ['scope', *self.container.resource_names()]

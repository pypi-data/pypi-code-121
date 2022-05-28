from importlib import import_module
from re import compile

from logos_cdi.abstract import AbstractResource, AbstractContainer
from os import environ

from logos_cdi.builder import ResourceBuilder


class Parameter(AbstractResource):

    def __init__(self, value):
        self.value = value

    @classmethod
    def recursive_resolve(cls, value, container: AbstractContainer, **kwargs):
        if isinstance(value, dict):
            return {k: cls.recursive_resolve(v, container, **kwargs) for k, v in value.items()}
        if isinstance(value, list):
            return [cls.recursive_resolve(v, container, **kwargs) for v in value]
        if isinstance(value, str):
            if value.startswith('%') and value.endswith('%'):
                return cls.recursive_resolve(container.get(value[1:-1], container), container, **kwargs)
            if value.startswith('@') and value.endswith('@'):
                return cls.recursive_resolve(environ.get(value[1:-1]), container, **kwargs)
            if value.startswith('__') and value.endswith('__'):
                return cls.recursive_resolve(kwargs.get(value[2: -2]), container, **kwargs)
        return value

    def resolve(self, container: AbstractContainer, _name: str = None):
        return self.recursive_resolve(self.value, container, name=_name)


class Class(AbstractResource):

    def __init__(self, class_path: str):
        self.module_path, self.class_name = class_path.split(':', 1)

    def resolve(self, container: AbstractContainer, _name: str = None):
        return getattr(import_module(self.module_path), self.class_name)


class Service(AbstractResource):

    def __init__(self, factory: str, parameters: dict = None):
        self.factory = factory
        self.parameters = parameters or {}

    def resolve(self, container: AbstractContainer, _name: str = None):
        factory = None
        if self.factory.startswith('class'):
            factory = lambda parameters: ResourceBuilder()\
                    .from_type('class')\
                    .with_arguments(self.factory.replace('class::', '', 1))\
                    .build(container)\
                    .resolve(container, _name).__call__(**parameters)
        else:
            factory = lambda parameters: container.get(self.factory).new(**parameters)

        return factory(ResourceBuilder()
                       .from_type('parameter')
                       .with_arguments(self.parameters)
                       .build(container).resolve(container, _name)
       )


class Group(AbstractResource):

    def __init__(self, regex: str, resolve_resources=False):
        self.regex = compile(regex)
        self.resolve_resources = resolve_resources

    def resolve(self, container: AbstractContainer, _name: str = None):
        print(container.resource_names())
        groups = {}
        for resource_name in container.resource_names():
            match = self.regex.match(resource_name)
            if match:
                if self.resolve_resources:
                    groups[match.group('name')] = ResourceBuilder()\
                            .from_type('parameter')\
                            .with_arguments(f'%{resource_name}%')\
                            .build(container)\
                            .resolve(container, resource_name)
                else:
                    groups[match.group('name')] = resource_name
        return groups








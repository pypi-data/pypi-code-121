from logos_cdi.abstract import AbstractContainer, AbstractResource
from logos_cdi.container import Container, ContainerGroup


class ResourceBuilder:

    def __init__(self):
        self.type = None
        self.parameters = {}
        self.arguments = []

    def from_type(self, type):
        self.type = type
        return self

    def with_parameters(self, **kwargs):
        self.parameters = kwargs
        return self

    def with_arguments(self, *args):
        self.arguments = args
        return self

    def build(self, container: AbstractContainer) -> AbstractResource:
        klzz = container.get(f'resource:{self.type}')
        return klzz(*self.arguments, **self.parameters)


class ContainerBuilder:

    def __init__(self):
        self.containers = []
        self.resources = {}

    def add_container(self, container: AbstractContainer):
        self.containers.append(container)
        return self

    def add_resource(self, name: str, type: str, *args, **kwargs):
        self.resources[name] = {
            "type": type,
            "arguments": args,
            "parameters": kwargs
        }
        return self

    def build(self, container: AbstractContainer) -> AbstractContainer:
        container = Container({
            key: ResourceBuilder()
            .from_type(value['type'])
            .with_arguments(*value['arguments'])
            .with_parameters(**value['parameters'])
            .build(container)
            for key, value in self.resources.items()
        })
        if not self.containers:
            container = ContainerGroup([container, *self.containers])
        return container

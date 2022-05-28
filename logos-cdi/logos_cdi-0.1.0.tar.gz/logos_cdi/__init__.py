from logos_cdi.application import Module
from logos_cdi.container import Container
from logos_cdi.resource import Class, Group, Parameter

__container__ = Container({
    'resources': Group(r'^resource:(?P<name>\w+)'),
    'resource:class': Class('logos_cdi.resource:Class'),
    'resource:service': Class('logos_cdi.resource:Service'),
    'resource:parameter': Class('logos_cdi.resource:Parameter'),
    'resource:group': Class('logos_cdi.resource:Group')
})

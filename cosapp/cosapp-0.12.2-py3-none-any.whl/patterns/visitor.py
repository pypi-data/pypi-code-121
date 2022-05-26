import abc
from typing import List


class Component(metaclass=abc.ABCMeta):
    """Abstract Base Class for visited components"""
    __slots__ = ()

    @abc.abstractmethod
    def accept(self, visitor) -> None:
        """Determines class-dependent course of action when visited by `visitor`"""
        pass


class Visitor:
    """Base class for visitors"""
    def visit_system(self, system) -> None:
        pass

    def visit_port(self, port) -> None:
        pass

    def visit_driver(self, driver) -> None:
        pass


def send(visitor: Visitor, components: List[Component]):
    """Send a visitor to a list of generic components"""
    for component in components:
        component.accept(visitor)

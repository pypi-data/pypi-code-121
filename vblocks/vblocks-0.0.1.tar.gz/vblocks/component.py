from abc import ABC, abstractmethod


class Component(ABC):
    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def json(self):
        pass

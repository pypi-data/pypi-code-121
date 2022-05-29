from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar

TSettings = TypeVar('TSettings')
TInstance = TypeVar('TInstance')

class InstanceFactory(Generic[TSettings, TInstance], ABC):

    @abstractmethod
    def create(self, settings: TSettings) -> TInstance:
        pass

    def __call__(self, settings: TSettings) -> TInstance:
        return self.create(settings)
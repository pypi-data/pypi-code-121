from typing import Any, Callable, Dict, Generic, List, Type, Union

from .abstractions.instance_factory import InstanceFactory, TInstance
from .abstractions.machine_learning_experimentation_service import InstanceSettings
from .default_instance_factory import DefaultInstanceFactory

class DefaultDictInstanceFactory(Generic[TInstance], InstanceFactory[Dict[str, InstanceSettings], Dict[str, TInstance]]):
    def __init__(self, available_types: Dict[str, Union[Type[TInstance], Callable[[Dict[str, Any]], TInstance]]]):
        if available_types is None:
            raise ValueError("available_types")

        self.__single_instance_factory: InstanceFactory[InstanceSettings, TInstance] = DefaultInstanceFactory[TInstance](available_types)

    def create(self, settings: Dict[str, InstanceSettings]) -> Dict[str, TInstance]:
        if settings is None:
            raise ValueError("settings")

        instances: Dict[str, TInstance] = {}

        for alias, instance_item in settings.items():
            instances[alias] = self.__single_instance_factory.create(instance_item)

        return instances

        
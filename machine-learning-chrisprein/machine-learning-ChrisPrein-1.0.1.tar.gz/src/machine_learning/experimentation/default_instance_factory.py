from typing import Any, Callable, Dict, Generic, Type, Union

from .abstractions.instance_factory import InstanceFactory, TInstance
from .abstractions.machine_learning_experimentation_service import InstanceSettings

class DefaultInstanceFactory(Generic[TInstance], InstanceFactory[InstanceSettings, TInstance]):
    def __init__(self, available_types: Dict[str, Union[Type[TInstance], Callable[[Dict[str, Any]], TInstance]]]):
        if available_types is None:
            raise ValueError("available_types")

        self.__available_types: Dict[str, Union[Type[TInstance], Callable[[Dict[str, Any]], TInstance]]] = available_types

    def create(self, settings: InstanceSettings) -> TInstance:
        if settings is None:
            raise ValueError("settings")

        if settings.name is None:
            raise ValueError("settings.name")

        if settings.params is None:
            raise ValueError("settings.params")

        if not settings.name in self.__available_types:
            raise KeyError(f'No matching type with name {settings.name} found.')

        type: Union[Type[TInstance], Callable[[Dict[str, Any]], TInstance]] = self.__available_types[settings.name]

        return type(**settings.params)
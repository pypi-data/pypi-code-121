
import abc

from typing import Any, cast, Dict, List, Optional

from qtoggleserver.core.typing import NullablePortValue, PortValue
from qtoggleserver.lib.polled import PolledPort

from .inverter import MPPSolarInverter


class MPPSolarPort(PolledPort, metaclass=abc.ABCMeta):
    def __init__(self, *, property_name: str, display_name: str, writable: bool, **kwargs) -> None:
        self._property_name: str = property_name

        super().__init__(**kwargs)

        self._display_name: str = display_name
        self._writable: bool = writable

    def get_peripheral(self) -> MPPSolarInverter:
        return cast(MPPSolarInverter, super().get_peripheral())

    def make_id(self) -> str:
        return self._property_name

    async def read_value(self) -> NullablePortValue:
        return self.get_peripheral().get_property(self._property_name)

    async def write_value(self, value: PortValue) -> None:
        await self.get_peripheral().set_property(self._property_name, value)


class BooleanPort(MPPSolarPort):
    TYPE = 'boolean'


class NumberPort(MPPSolarPort):
    TYPE = 'number'

    def __init__(self, *, unit: Optional[str] = None, choices: Optional[List[Dict[str, Any]]] = None, **kwargs) -> None:
        super().__init__(**kwargs)

        self._unit: Optional[str] = unit
        self._choices: Optional[List[Dict[str, Any]]] = choices


class StringPort(MPPSolarPort):
    TYPE = 'number'

    def __init__(self, *, unit: Optional[str] = None, choices: List[Dict[str, Any]], **kwargs) -> None:
        super().__init__(**kwargs)

        # Associate a number to each choice value, since we can't deal with string values
        self._value_mapping: Dict[str, int] = {}
        adapted_choices = []
        for i, choice in enumerate(choices):
            adapted_choice = dict(choice, value=i)
            adapted_choices.append(adapted_choice)
            self._value_mapping[choice['value']] = i

        self._unit: Optional[str] = unit
        self._choices: List[Dict[str, Any]] = adapted_choices

    async def read_value(self) -> NullablePortValue:
        value = self.get_peripheral().get_property(self._property_name)
        if value is not None:
            return self._value_mapping[value]

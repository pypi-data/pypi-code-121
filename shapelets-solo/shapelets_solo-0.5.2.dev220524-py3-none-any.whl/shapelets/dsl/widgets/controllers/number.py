# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from typing import Union

from shapelets.dsl import TypeNotSupported
from shapelets.dsl.argument_types import ArgumentType, ArgumentTypeEnum, ArgumentValue
from shapelets.dsl.widgets import WidgetNode, AttributeNames


class Number(WidgetNode):
    def __init__(self,
                 name: str = None,
                 default_value: Union[int, float] = None,
                 value_type: type = float,
                 **additional):
        super().__init__(self.__class__.__name__,
                         name,
                         Number._argument_type(default_value, value_type),
                         default_value,
                         **additional)

    def to_dict_widget(self):
        number_dict = super().to_dict_widget()
        number_dict[AttributeNames.PROPERTIES.value].update(self._argument_value_to_dict())
        return number_dict

    @staticmethod
    def _argument_type(default_value: Union[int, float] = None,
                       default_type: type = None) -> ArgumentType:
        if not default_type:
            if not default_value:
                argument_type = ArgumentTypeEnum.DOUBLE
            else:
                if isinstance(default_value, float):
                    argument_type = ArgumentTypeEnum.DOUBLE
                elif isinstance(default_value, int):
                    argument_type = ArgumentTypeEnum.INT
                else:
                    raise TypeNotSupported(AttributeNames.TYPE_NOT_SUPPORTED.value)
        else:
            if default_type is float:
                argument_type = ArgumentTypeEnum.DOUBLE
            elif default_type is int:
                argument_type = ArgumentTypeEnum.INT
            else:
                raise TypeNotSupported(AttributeNames.TYPE_NOT_SUPPORTED.value)
        return ArgumentType(argument_type)

    def _argument_value_to_dict(self) -> dict:
        value_dict = self.value.to_dict()
        keys = list(value_dict.keys())
        del keys[keys.index(ArgumentValue.TYPE_KEY)]
        key = keys[0]
        value = value_dict[key]
        del value_dict[key]
        value_dict[ArgumentValue.VALUE_KEY] = value
        return value_dict

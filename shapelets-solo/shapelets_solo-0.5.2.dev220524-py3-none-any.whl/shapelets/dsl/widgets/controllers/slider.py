# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from typing import Union

from shapelets.dsl import Node, ArgumentType, ArgumentTypeEnum, TypeNotSupported, ArgumentValue
from shapelets.dsl.widgets import WidgetNode, AttributeNames
from shapelets.dsl.widgets.controllers.number import Number


class Slider(WidgetNode):
    def __init__(self,
                 min_value,
                 max_value,
                 step,
                 default_value: Union[int, float] = None,
                 value_type: type = float,
                 in_range: bool = False,
                 name: str = None,
                 title: Union[str, Node] = None,
                 formatter: str = "number",
                 **additional):
        super().__init__(self.__class__.__name__,
                         name,
                         Number._argument_type(default_value, value_type),
                         default_value,
                         **additional)
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.title = title
        self.in_range = in_range
        self.formatter = formatter

    def to_dict_widget(self):
        slider_dict = super().to_dict_widget()
        slider_dict[AttributeNames.PROPERTIES.value].update(self._argument_value_to_dict())
        slider_dict[AttributeNames.PROPERTIES.value].update({
            AttributeNames.MIN.value: self.min_value,
            AttributeNames.MAX.value: self.max_value,
            AttributeNames.STEP.value: self.step,
            AttributeNames.RANGE.value: self.in_range,
            AttributeNames.FORMAT.value: self.formatter
        })

        if self.title is not None:
            if isinstance(self.title, str):
                slider_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TITLE.value: self.title
                })
            if isinstance(self.title, Node):
                slider_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TITLE.value: {
                        AttributeNames.REF.value: f"{self.title.node_id}:{self.title.active_output}"
                    }
                })
        return slider_dict

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
                    raise TypeNotSupported("only supports int/float types")
        else:
            if default_type is float:
                argument_type = ArgumentTypeEnum.DOUBLE
            elif default_type is int:
                argument_type = ArgumentTypeEnum.INT
            else:
                raise TypeNotSupported("only supports int/float types")
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
                    raise TypeNotSupported("only supports int/float types")
        else:
            if default_type is float:
                argument_type = ArgumentTypeEnum.DOUBLE
            elif default_type is int:
                argument_type = ArgumentTypeEnum.INT
            else:
                raise TypeNotSupported("only supports int/float types")
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

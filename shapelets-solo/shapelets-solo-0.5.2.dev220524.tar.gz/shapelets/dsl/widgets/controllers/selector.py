# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from typing import List, Union

from shapelets.dsl import ArgumentType, ArgumentTypeEnum, Node
from shapelets.dsl.widgets import WidgetNode, AttributeNames


class Selector(WidgetNode):

    def __init__(self,
                 options: Union[List, Node],
                 title: Union[str, Node] = None,
                 label_by: str = None,
                 value_by: str = None,
                 value: Union[int, float, str, Node, any] = None,
                 **additional):
        argument_type, default_value = Selector._argument_type(options, value_by)
        super().__init__(self.__class__.__name__, "Selector", argument_type, default_value, **additional)
        self.title = title
        self.options = options
        self.label_by = label_by
        self.value_by = value_by
        self.value = value
        self.argument_type = argument_type

        if isinstance(self.options, list) and all((isinstance(x, dict)) for x in self.options):
            if self.label_by is None:
                raise Exception("You must indicate the label_by property")
            if self.value_by is None:
                raise Exception("You must indicate the value_by property")

    def to_dict_widget(self):
        selector_dict = super().to_dict_widget()

        selector_dict[AttributeNames.PROPERTIES.value].update({
            AttributeNames.TYPE.value: self.argument_type.types[0].__dict__["_value_"],
            AttributeNames.OPTIONS.value: self.options,
        })

        if self.options is not None and isinstance(self.options, Node):
            selector_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.OPTIONS.value: {
                    AttributeNames.REF.value: f"{self.options.node_id}:{self.options.active_output}"
                },
            })

        if self.title is not None:
            if isinstance(self.title, Node):
                selector_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TITLE.value: {
                        AttributeNames.REF.value: f"{self.title.node_id}:{self.title.active_output}"
                    },
                })
            else:
                selector_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TITLE.value: self.title,
                })

        if self.label_by is not None:
            selector_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.LABEL_BY.value: self.label_by,
            })

        if self.value_by is not None:
            selector_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.VALUE_BY.value: self.value_by,
            })

        if self.value is not None:
            if isinstance(self.value, Node):
                selector_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.VALUE.value: {
                        AttributeNames.REF.value: f"{self.value.node_id}:{self.value.active_output}"
                    },
                })
            else:
                selector_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.VALUE.value: self.value,
                })

        return selector_dict

    @staticmethod
    def _argument_type(options: List, value_by: str) -> ArgumentType:

        if isinstance(options, Node):
            argument_type = ArgumentTypeEnum.STRING
            default_value = ""
            return ArgumentType(argument_type), default_value

        if all(isinstance(x, str) for x in options):
            argument_type = ArgumentTypeEnum.STRING
            default_value = ""
        if all(isinstance(x, int) for x in options):
            argument_type = ArgumentTypeEnum.INT
            default_value = 0
        if all(isinstance(x, float) for x in options):
            argument_type = ArgumentTypeEnum.FLOAT
            default_value = 0
        if all(isinstance(x, dict) for x in options):
            return Selector._argument_type(options[0][value_by], value_by)

        return ArgumentType(argument_type), default_value

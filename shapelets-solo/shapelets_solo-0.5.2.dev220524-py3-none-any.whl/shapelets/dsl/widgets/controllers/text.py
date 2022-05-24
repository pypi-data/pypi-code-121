# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from typing import Union

from shapelets.dsl import Node, ArgumentType, ArgumentTypeEnum
from shapelets.dsl.widgets import WidgetNode, AttributeNames


class Text(WidgetNode):

    def __init__(self, title: Union[str, Node] = None, text: Union[str, Node] = None, **additional):

        super().__init__(self.__class__.__name__, "Text", ArgumentType(ArgumentTypeEnum.STRING), "", **additional)
        self.title = title
        self.text = text

    def to_dict_widget(self):
        text_dict = super().to_dict_widget()

        if self.title is not None:
            if isinstance(self.title, str):
                text_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TITLE.value: self.title
                })
            if isinstance(self.title, Node):
                text_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TITLE.value: {
                        AttributeNames.REF.value: f"{self.title.node_id}:{self.title.active_output}"
                    }
                })

        if self.text is not None:
            if isinstance(self.text, str):
                text_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TEXT.value: self.text
                })
            if isinstance(self.text, Node):
                text_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TEXT.value: {
                        AttributeNames.REF.value: f"{self.text.node_id}:{self.text.active_output}"
                    }
                })

        return text_dict

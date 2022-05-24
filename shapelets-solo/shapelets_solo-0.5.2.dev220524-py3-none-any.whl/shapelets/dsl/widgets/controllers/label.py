# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from typing import Union

from shapelets.dsl import Node
from shapelets.dsl.widgets import AttributeNames, Widget


class Label(Widget):

    def __init__(self, text: Union[str, int, float, Node], **additional):
        super().__init__(self.__class__.__name__, "Label", **additional)
        self.text = text

    def to_dict_widget(self):
        label_dict = super().to_dict_widget()
        text_value = None

        if isinstance(self.text, Node):
            text_value = {
                AttributeNames.REF.value: f"{self.text.node_id}:{self.text.active_output}"
            }
        if isinstance(self.text, str):
            text_value = self.text

        label_dict[AttributeNames.PROPERTIES.value].update({
            AttributeNames.TEXT.value: text_value,
        })
        return label_dict

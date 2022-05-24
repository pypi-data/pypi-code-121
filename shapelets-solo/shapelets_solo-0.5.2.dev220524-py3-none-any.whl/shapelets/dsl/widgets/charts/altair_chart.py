# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from typing import Union, Any

from shapelets.dsl import Node
from shapelets.dsl.widgets import Widget, AttributeNames


class AltairChart(Widget):
    def __init__(self, alt: Union[Any, Node], **additional):
        Widget.__init__(self, self.__class__.__name__, "Altair", **additional)
        self.alt = alt

    def to_dict_widget(self):
        alt_dict = super().to_dict_widget()

        if isinstance(self.alt, Node):
            alt_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.VALUE.value: {
                    AttributeNames.REF.value: f"{self.alt.node_id}:{self.alt.active_output}"
                },
            })
        else:
            if not hasattr(self.alt, "to_json"):
                raise Exception("You must inject an altair chart")

            alt_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.VALUE.value: self.alt.to_json(indent=2),
            })
        return alt_dict

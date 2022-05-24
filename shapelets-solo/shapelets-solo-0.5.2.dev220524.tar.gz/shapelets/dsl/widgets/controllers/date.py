# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from typing import Union

from shapelets.dsl import Node, ArgumentType, ArgumentTypeEnum
from shapelets.dsl.widgets import WidgetNode, AttributeNames


class Date(WidgetNode):

    def __init__(self, title: Union[str, Node] = None, date: Union[float, Node] = None,
                 min_date: Union[float, Node] = None, max_date: Union[float, Node] = None, **additional):

        super().__init__(self.__class__.__name__, "Date", ArgumentType(ArgumentTypeEnum.DOUBLE), 0, **additional)
        self.title = title
        self.date = date
        self.min_date = min_date
        self.max_date = max_date

    def to_dict_widget(self):
        date_dict = super().to_dict_widget()

        if self.title is not None:
            if isinstance(self.title, str):
                date_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TITLE.value: self.title
                })
            if isinstance(self.title, Node):
                date_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TITLE.value: {
                        AttributeNames.REF.value: f"{self.title.node_id}:{self.title.active_output}"
                    }
                })

        if self.date is not None:
            if isinstance(self.date, float) or isinstance(self.date, int):
                date_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.DATE.value: self.date
                })
            if isinstance(self.date, Node):
                date_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.DATE.value: {
                        AttributeNames.REF.value: f"{self.date.node_id}:{self.date.active_output}"
                    }
                })

        if self.min_date is not None:
            if isinstance(self.min_date, float) or isinstance(self.min_date, int):
                date_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.MIN_DATE.value: self.min_date
                })
            if isinstance(self.min_date, Node):
                date_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.MIN_DATE.value: {
                        AttributeNames.REF.value: f"{self.min_date.node_id}:{self.min_date.active_output}"
                    }
                })

        if self.max_date is not None:
            if isinstance(self.max_date, float) or isinstance(self.max_date, int):
                date_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.MAX_DATE.value: self.max_date
                })
            if isinstance(self.max_date, Node):
                date_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.MAX_DATE.value: {
                        AttributeNames.REF.value: f"{self.max_date.node_id}:{self.max_date.active_output}"
                    }
                })

        return date_dict

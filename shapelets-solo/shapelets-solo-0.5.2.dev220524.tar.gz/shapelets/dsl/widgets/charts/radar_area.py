# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from typing import Union, List

from shapelets.dsl import Node
from shapelets.dsl.widgets import Widget, AttributeNames
from shapelets.model import NDArray


class RadarArea(Widget):
    def __init__(self,
                 categories: Union[List[int], List[float], List[str], NDArray, Node],
                 data: Union[List[int], List[float], NDArray, Node],
                 groups: Union[List[int], List[float], List[str], NDArray, Node],
                 name: str = None,
                 title: Union[str, Node] = None,
                 **additional):
        super().__init__(self.__class__.__name__,
                         name,
                         **additional)
        self.categories = categories
        self.data = data
        self.groups = groups
        self.title = title

    def to_dict_widget(self):
        radar_chart_dict = super().to_dict_widget()
        if self.categories is not None:
            categories_value = None
            if isinstance(self.categories, List) and all(
                    [isinstance(item, int) or isinstance(item, float) or isinstance(item, str) for item in
                     self.categories]):
                categories_value = self.categories
            if isinstance(self.categories, Node):
                categories_value = {
                    AttributeNames.REF.value: f"{self.categories.node_id}:{self.categories.active_output}"
                }
            if isinstance(self.categories, NDArray):
                categories_value = self.categories.nd_array_id

            radar_chart_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.CATEGORIES.value: categories_value
            })
        if self.data:
            data_value = None
            if isinstance(self.data, List) and all(
                    [isinstance(item, int) or isinstance(item, float) for item in self.data]):
                data_value = self.data
            if isinstance(self.data, Node):
                data_value = {
                    AttributeNames.REF.value: f"{self.data.node_id}:{self.data.active_output}"
                }
            if isinstance(self.data, NDArray):
                data_value = self.data.nd_array_id

            radar_chart_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.DATA.value: data_value
            })
        if self.groups:
            groups_value = None
            if isinstance(self.groups, List) and all(
                    [isinstance(item, int) or isinstance(item, float) or isinstance(item, str) for item in
                     self.groups]):
                groups_value = self.groups
            if isinstance(self.groups, Node):
                groups_value = {
                    AttributeNames.REF.value: f"{self.groups.node_id}:{self.groups.active_output}"
                }
            if isinstance(self.groups, NDArray):
                groups_value = self.groups.nd_array_id

            radar_chart_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.GROUPS.value: groups_value
            })
        if self.title is not None:
            if isinstance(self.title, str):
                radar_chart_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TITLE.value: self.title
                })
            if isinstance(self.title, Node):
                radar_chart_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TITLE.value: {
                        AttributeNames.REF.value: f"{self.title.node_id}:{self.title.active_output}"
                    }
                })
        return radar_chart_dict

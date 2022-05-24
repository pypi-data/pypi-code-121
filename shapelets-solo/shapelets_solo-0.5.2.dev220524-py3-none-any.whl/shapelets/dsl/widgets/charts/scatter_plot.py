# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from typing import Union, List

from shapelets.dsl import Node
from shapelets.dsl.widgets import Widget, AttributeNames
from shapelets.model import NDArray


class ScatterPlot(Widget):
    def __init__(self,
                 x_axis: Union[List[int], List[float], NDArray, Node],
                 y_axis: Union[List[int], List[float], NDArray, Node],
                 size: Union[List[int], List[float], NDArray, Node] = None,
                 color: Union[List[int], List[float], NDArray, Node] = None,
                 categories: Union[List[int], List[float], List[str], NDArray, Node] = None,
                 name: str = None,
                 title: Union[str, Node] = None,
                 trend_line: bool = False,
                 **additional):
        super().__init__(self.__class__.__name__, name, **additional)
        if size:
            self.size = size
        if color:
            self.color = color
        if categories:
            self.categories = categories
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.title = title
        self.trend_line = trend_line

    def to_dict_widget(self):
        scatter_plot_dict = super().to_dict_widget()
        if hasattr(self, "size"):
            size_value = None

            if isinstance(self.size, List) and all(
                    [isinstance(item, int) or isinstance(item, float) for item in self.size]):
                size_value = self.size

            if isinstance(self.size, Node):
                size_value = {
                    AttributeNames.REF.value: f"{self.size.node_id}:{self.size.active_output}"
                }
            if isinstance(self.size, NDArray):
                size_value = self.size.nd_array_id

            scatter_plot_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.SIZE.value: size_value
            })
        if hasattr(self, "color"):
            color_value = None

            if isinstance(self.color, List) and all(
                    [isinstance(item, int) or isinstance(item, float) for item in self.color]):
                color_value = self.color

            if isinstance(self.color, Node):
                color_value = {
                    AttributeNames.REF.value: f"{self.color.node_id}:{self.color.active_output}"
                }
            if isinstance(self.color, NDArray):
                color_value = self.color.nd_array_id

            scatter_plot_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.COLOR.value: color_value
            })

        if hasattr(self, "categories"):
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

            scatter_plot_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.CATEGORIES.value: categories_value
            })

        if self.title is not None:
            if isinstance(self.title, str):
                scatter_plot_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TITLE.value: self.title
                })
            if isinstance(self.title, Node):
                scatter_plot_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TITLE.value: {
                        AttributeNames.REF.value: f"{self.title.node_id}:{self.title.active_output}"
                    }
                })

        if hasattr(self, "x_axis"):
            x_axis_value = None

            if isinstance(self.x_axis, List) and all(
                    [isinstance(item, int) or isinstance(item, float) for item in self.x_axis]):
                x_axis_value = self.x_axis

            if isinstance(self.x_axis, Node):
                x_axis_value = {
                    AttributeNames.REF.value: f"{self.x_axis.node_id}:{self.x_axis.active_output}"
                }
            if isinstance(self.x_axis, NDArray):
                x_axis_value = self.x_axis.nd_array_id

            scatter_plot_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.X_AXIS.value: x_axis_value
            })

        if hasattr(self, "y_axis"):
            y_axis_value = None

            if isinstance(self.y_axis, List) and all(
                    [isinstance(item, int) or isinstance(item, float) for item in self.y_axis]):
                y_axis_value = self.y_axis

            if isinstance(self.y_axis, Node):
                y_axis_value = {
                    AttributeNames.REF.value: f"{self.y_axis.node_id}:{self.y_axis.active_output}"
                }
            if isinstance(self.y_axis, NDArray):
                y_axis_value = self.y_axis.nd_array_id

            scatter_plot_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.Y_AXIS.value: y_axis_value
            })

        if hasattr(self, "trend_line"):
            scatter_plot_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.TREND_LINE.value: self.trend_line
            })
        return scatter_plot_dict

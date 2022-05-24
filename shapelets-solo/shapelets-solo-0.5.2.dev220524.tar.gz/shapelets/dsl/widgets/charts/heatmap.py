# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from typing import Union, List

from shapelets.dsl import Node
from shapelets.dsl.widgets import Widget, AttributeNames
from shapelets.model import NDArray


class HeatMap(Widget):
    def __init__(self,
                 x_axis: Union[List[int], List[float], List[str], NDArray, Node],
                 y_axis: Union[List[int], List[float], List[str], NDArray, Node],
                 z_axis: Union[List[int], List[float], NDArray, Node],
                 name: str = None,
                 title: Union[str, Node] = None,
                 **additional):
        super().__init__(self.__class__.__name__, name, **additional)
        self.title = title
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.z_axis = z_axis

    def to_dict_widget(self):
        heatmap_dict = super().to_dict_widget()

        # title
        if isinstance(self.title, str):
            heatmap_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.TITLE.value: self.title
            })
        if isinstance(self.title, Node):
            heatmap_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.TITLE.value: {
                    AttributeNames.REF.value: f"{self.title.node_id}:{self.title.active_output}"
                }
            })

        def _check_types(axis):
            print(axis)
            if all(isinstance(element, type(axis[0])) for element in axis):
                return axis
            else:
                raise Exception("Mixed types not supported")

        # x_axis
        if isinstance(self.x_axis, List):
            heatmap_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.X_AXIS.value: _check_types(self.x_axis)
            })

        if isinstance(self.x_axis, NDArray):
            heatmap_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.X_AXIS.value: self.x_axis.nd_array_id
            })

        if isinstance(self.x_axis, Node):
            heatmap_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.X_AXIS.value: {
                    AttributeNames.REF.value: f"{self.x_axis.node_id}:{self.x_axis.active_output}"
                }
            })

        # y_axis
        if isinstance(self.y_axis, List):
            heatmap_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.Y_AXIS.value: _check_types(self.y_axis)
            })

        if isinstance(self.y_axis, NDArray):
            heatmap_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.Y_AXIS.value: self.y_axis.nd_array_id
            })

        if isinstance(self.y_axis, Node):
            heatmap_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.Y_AXIS.value: {
                    AttributeNames.REF.value: f"{self.y_axis.node_id}:{self.y_axis.active_output}"
                }
            })

        # z_axis
        if isinstance(self.z_axis, List):
            heatmap_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.Z_AXIS.value: _check_types(self.z_axis)
            })

        if isinstance(self.z_axis, NDArray):
            heatmap_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.Z_AXIS.value: self.z_axis.nd_array_id
            })

        if isinstance(self.z_axis, Node):
            heatmap_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.Z_AXIS.value: {
                    AttributeNames.REF.value: f"{self.z_axis.node_id}:{self.z_axis.active_output}"
                }
            })

        return heatmap_dict

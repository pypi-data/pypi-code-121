# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from typing import Union, List

from shapelets.dsl import Node
from shapelets.dsl.widgets import Widget, AttributeNames
from shapelets.model import NDArray


class Histogram(Widget):
    def __init__(self, x: Union[List[int], List[float], NDArray, Node],
                 bins: Union[int, float, Node] = None,
                 cumulative: Union[bool, Node] = False, **additional):
        super().__init__(self.__class__.__name__, "Histogram", **additional)
        self._x = x
        self._bins = bins
        self._cumulative = cumulative

    def to_dict_widget(self):
        histogram_dict = super().to_dict_widget()

        if isinstance(self._x, List) and all([isinstance(item, int) or isinstance(item, float) for item in self._x]):
            histogram_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.X.value: self._x
            })
        if isinstance(self._x, NDArray):
            histogram_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.X.value: self._x.nd_array_id
            })
        if isinstance(self._x, Node):
            histogram_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.X.value: {
                    AttributeNames.REF.value: f"{self._x.node_id}:{self._x.active_output}"
                }
            })
        if self._bins is not None:
            if isinstance(self._bins, int) or isinstance(self._bins, float):
                histogram_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.BINS.value: self._bins
                })
            if isinstance(self._bins, float) or isinstance(self._bins, float):
                histogram_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.BINS.value: self._bins
                })
            if isinstance(self._bins, Node):
                histogram_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.BINS.value: {
                        AttributeNames.REF.value: f"{self._bins.node_id}:{self._bins.active_output}"
                    }
                })
        if isinstance(self._cumulative, bool):
            histogram_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.CUMULATIVE.value: self._cumulative
            })
        if isinstance(self._cumulative, Node):
            histogram_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.CUMULATIVE.value: {
                    AttributeNames.REF.value: f"{self._cumulative.node_id}:{self._cumulative.active_output}"
                }
            })

        return histogram_dict

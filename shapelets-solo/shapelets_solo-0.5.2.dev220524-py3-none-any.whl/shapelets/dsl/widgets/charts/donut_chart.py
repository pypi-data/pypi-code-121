# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from typing import Union, List

from shapelets.dsl import Node
from shapelets.dsl.widgets.charts.pie_chart import PieChart
from shapelets.model import NDArray


class DonutChart(PieChart):
    def __init__(self,
                 data: Union[List[int], List[float], NDArray, Node],
                 categories: Union[List[int], List[float], List[str], NDArray, Node] = None,
                 name: str = None,
                 title: Union[str, Node] = None,
                 **additional):
        super().__init__(data,
                         categories,
                         name,
                         title,
                         **additional)

        self.widget_type = self.__class__.__name__

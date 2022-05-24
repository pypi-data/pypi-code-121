# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from typing import Union, List

from shapelets.dsl import Node
from shapelets.dsl.widgets.controllers.selector import Selector


class RadioGroup(Selector):
    def __init__(self,
                 options: Union[List, Node],
                 title: Union[str, Node] = None,
                 label_by: str = None,
                 value_by: str = None,
                 value: Union[int, float, str, Node, any] = None,
                 **additional):
        super().__init__(options,
                         title,
                         label_by,
                         value_by,
                         value,
                         **additional)

        self.widget_type = self.__class__.__name__

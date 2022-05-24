# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from typing import Union

from shapelets.dsl import Node
from shapelets.dsl.widgets import Widget, AttributeNames
from shapelets.model import Dataframe, NDArray


class Table(Widget):

    def __init__(self, data: Union[Dataframe, Node] = None, cols: Union[NDArray, Node] = None,
                 rows: Union[NDArray, Node] = None, **additional):
        super().__init__(self.__class__.__name__, "Table", **additional)
        self.data = data
        self.cols = cols
        self.rows = rows

        if self.data is not None and self.rows is not None:
            raise Exception("Cannot create a table with data and rows")

        if self.cols is not None and self.rows is None:
            raise Exception("if cols is set, rows is also needed")

        if self.data is None and self.rows is None:
            raise Exception("You must set at least data or rows parameter")

    def to_dict_widget(self):
        table_dict = super().to_dict_widget()

        if isinstance(self.data, Node):
            table_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.DATA.value: {
                    AttributeNames.REF.value: f"{self.data.node_id}:{self.data.active_output}"
                },
            })

        elif isinstance(self.data, Dataframe):
            table_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.DATA.value: self.data.dataframe_id,
            })

        if isinstance(self.cols, NDArray):
            table_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.COL.value: self.cols.nd_array_id
            })
        elif isinstance(self.cols, Node):
            table_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.COL.value: {
                    AttributeNames.REF.value: f"{self.cols.node_id}:{self.cols.active_output}"
                },
            })

        if isinstance(self.rows, NDArray):
            table_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.ROW.value: self.rows.nd_array_id
            })

        elif isinstance(self.rows, Node):
            table_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.ROW.value: {
                    AttributeNames.REF.value: f"{self.rows.node_id}:{self.rows.active_output}"
                },
            })

        return table_dict

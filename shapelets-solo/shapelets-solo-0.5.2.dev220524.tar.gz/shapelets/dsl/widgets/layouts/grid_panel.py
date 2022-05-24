# Copyright (c) 2021 Grumpy Cat Software S.L.
#
# This Source Code is licensed under the MIT 2.0 license.
# the terms can be found in LICENSE.md at the root of
# this project, or at http://mozilla.org/MPL/2.0/.
from shapelets.dsl.widgets import Widget, AttributeNames
from shapelets.dsl.widgets.layouts.panel import Panel


class GridPanel(Panel):
    """
    TO BE FILLED
    """

    def __init__(self,
                 num_rows: int,
                 num_cols: int,
                 panel_title: str = None,
                 panel_id: str = None,
                 **additional
                 ):
        super().__init__(panel_title=panel_title, panel_id=panel_id, **additional)
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.placements = dict()

    def place(self, widget: Widget, row: int, col: int, row_span: int = 1, col_span: int = 1):
        GridPanel.__check_bounds("row", row + row_span - 1, self.num_rows)
        GridPanel.__check_bounds("col", col + col_span - 1, self.num_cols)
        super()._place(widget)
        self.placements[widget.widget_id] = (row, col, row_span, col_span)

    @staticmethod
    def __check_bounds(name, index, max_index):
        if not (0 <= index < max_index):
            raise IndexError(f"{name} index out of bounds {index} not in [0, {max_index})")

    def to_dict_widget(self):
        panel_dict = super().to_dict_widget()
        panel_dict[AttributeNames.PROPERTIES.value].update({
            AttributeNames.NUM_ROWS.value: self.num_rows,
            AttributeNames.NUM_COLS.value: self.num_cols,
            AttributeNames.PLACEMENTS.value: [{
                AttributeNames.WIDGET_REF.value: key,
                AttributeNames.ROW.value: row,
                AttributeNames.COL.value: col,
                AttributeNames.ROW_SPAN.value: row_span,
                AttributeNames.COL_SPAN.value: col_span
            } for key, (row, col, row_span, col_span) in self.placements.items()]
        })
        return panel_dict

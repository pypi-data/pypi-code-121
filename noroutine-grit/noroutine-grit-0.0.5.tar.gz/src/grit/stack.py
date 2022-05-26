from attr import define, field

from .row import Row

@define
class Stack:
    """
    Panel Stack (of Rows)

    :param rows: list of rows

    """
    rows: list[Row] = field(default=[])

    def __init__(self, *args: Row):
        self.rows = args

    def to_panels(self):
        y_int = 0
        panels = []
        for row in self.rows:
            panels += row.to_panels(y_int)
            y_int += row.height

        return panels

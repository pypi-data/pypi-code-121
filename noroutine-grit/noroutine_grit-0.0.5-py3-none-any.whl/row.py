from attr import define

import copy

from grafanalib.core import (Panel, GridPos)


GRAFANA_DASHBOARD_SCREEN_WIDTH = 24

@define
class Row:
    """
    Panel Row

    :param height: row height
    :param panel_list: list of panels
    """

    height: int
    panel_list: list[Panel]

    def __init__(self, height: int, *args: Panel):
        self.height = height
        self.panel_list = args

    def to_panels(self, y: int):
        panel_width_int = int(
            GRAFANA_DASHBOARD_SCREEN_WIDTH / len(self.panel_list))
        auto_panel_list = []
        x_int = 0

        for panel in self.panel_list:
            panel_copy = copy.deepcopy(panel)
            auto_panel_list.append(panel_copy)
            panel_copy.gridPos = GridPos(
                h=self.height,
                w=panel_width_int,
                x=x_int,
                y=y)
            x_int += panel_width_int

        return auto_panel_list

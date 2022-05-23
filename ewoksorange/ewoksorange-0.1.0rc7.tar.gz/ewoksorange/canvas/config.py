"""Copy parts of Orange.canvas.config to be used when Orange3 is not installed.
"""

import pkg_resources
from orangewidget.workflow import config as orangeconfig
from orangewidget.workflow.config import WIDGETS_ENTRY


class Config(orangeconfig.Config):
    @staticmethod
    def widgets_entry_points():
        """
        Return an `EntryPoint` iterator for all 'orange.widget' entry
        points.
        """
        # Ensure the 'this' distribution's ep is the first. iter_entry_points
        # yields them in unspecified order.
        all_eps = pkg_resources.iter_entry_points(WIDGETS_ENTRY)
        return iter(all_eps)

    @staticmethod
    def addon_entry_points():
        return Config.widgets_entry_points()


def widgets_entry_points():
    return Config.widgets_entry_points()

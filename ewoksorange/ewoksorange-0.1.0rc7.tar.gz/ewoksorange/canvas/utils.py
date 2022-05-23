from typing import Optional

from ..orange_version import ORANGE_VERSION

if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
    from oasys.canvas.mainwindow import OASYSMainWindow as MainWindow
elif ORANGE_VERSION == ORANGE_VERSION.latest_orange:
    from Orange.canvas.mainwindow import MainWindow
else:
    from orangewidget.workflow.mainwindow import OWCanvasMainWindow as MainWindow

from ..bindings.qtapp import get_qtapp


def get_orange_canvas() -> Optional[MainWindow]:
    app = get_qtapp()
    if app is None:
        return None
    for widget in app.topLevelWidgets():
        if isinstance(widget, MainWindow):
            return widget
    return None

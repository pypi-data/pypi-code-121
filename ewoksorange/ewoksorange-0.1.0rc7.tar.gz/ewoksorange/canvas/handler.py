import time
from AnyQt.QtCore import Qt

from ..orange_version import ORANGE_VERSION

if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
    from oasys.canvas.mainwindow import OASYSMainWindow as _MainWindow, QDialog
    from orangecanvas.registry import set_global_registry
    from orangecanvas.registry.qt import QtWidgetRegistry
    from oasys.canvas import conf as orangeconfig
    from orangecanvas import config as canvasconfig

    class MainWindow(_MainWindow):
        def show_scheme_properties_for(self, scheme, window_title=None):
            return QDialog.Accepted

else:
    from orangecanvas.registry import set_global_registry
    from orangecanvas.registry.qt import QtWidgetRegistry
    from orangecanvas import config as canvasconfig

    if ORANGE_VERSION == ORANGE_VERSION.latest_orange:
        # load MainWindow and config from Orange if installed
        from Orange.canvas.mainwindow import MainWindow
        from Orange.canvas import config as orangeconfig
    else:
        # else use the base one from orangewidget
        from orangewidget.workflow.mainwindow import OWCanvasMainWindow as MainWindow
        from ewoksorange.canvas import config as orangeconfig

from .utils import get_orange_canvas
from ..bindings import qtapp
from ..bindings.owsignal_manager import SignalManagerWithOutputTracking


class OrangeCanvasHandler:
    def __init__(self):
        self.canvas = get_orange_canvas()
        self.__is_owner = self.canvas is None

    def __del__(self):
        self.close()

    def __enter__(self):
        if self.canvas is None:
            self._init_canvas()
            self.__is_owner = True
        return self

    def __exit__(self, *args):
        self.close()

    def _init_canvas(self):
        qtapp.ensure_qtapp()

        widget_registry = QtWidgetRegistry()
        set_global_registry(widget_registry)

        if ORANGE_VERSION == ORANGE_VERSION.oasys_fork:
            config = orangeconfig.oasysconf()
            config.init()
            canvasconfig.set_default(config)
            widget_discovery = config.widget_discovery(widget_registry)
            widget_discovery.run(config.widgets_entry_points())
        else:
            config = orangeconfig.Config()
            config.init()
            canvasconfig.set_default(config)
            widget_discovery = config.widget_discovery(widget_registry)
            widget_discovery.run(orangeconfig.widgets_entry_points())

        canvas = MainWindow()
        canvas.setAttribute(Qt.WA_DeleteOnClose)
        canvas.set_widget_registry(widget_registry)  # makes a copy of the registry
        self.canvas = canvas
        self.process_events()

    def close(self, force=False):
        if self.canvas is None or (not self.__is_owner and not force):
            return
        canvas, self.canvas = self.canvas, None
        self.process_events()
        # do not prompt for saving modification:
        canvas.current_document().setModified(False)
        canvas.close()
        self.process_events()

    def load_ows(self, filename: str):
        self.canvas.load_scheme(filename)

    @property
    def scheme(self):
        return self.canvas.current_document().scheme()

    @property
    def signal_manager(self) -> SignalManagerWithOutputTracking:
        signal_manager = self.scheme.signal_manager
        assert isinstance(
            signal_manager, SignalManagerWithOutputTracking
        ), "Orange signal manager was not patched before instantiated"
        return signal_manager

    def iter_nodes(self):
        scheme = self.scheme
        for node in scheme.nodes:
            yield node

    def process_events(self):
        qtapp.process_qtapp_events()

    def show(self):
        qtapp.process_qtapp_events()
        self.canvas.show()
        qtapp.get_qtapp().exec()

    def widgets_from_name(self, name: str):
        for node in self.iter_nodes():
            if node.title == name:
                yield self.scheme.widget_for_node(node)

    def iter_widgets(self):
        for node in self.iter_nodes():
            yield self.scheme.widget_for_node(node)

    def iter_widgets_with_name(self):
        for node in self.iter_nodes():
            yield node.title, self.scheme.widget_for_node(node)

    def iter_output_values(self):
        for name, widget in self.iter_widgets_with_name():
            yield name, widget.task_output_values

    def wait_widgets(self, timeout=None):
        signal_manager = self.signal_manager
        widgets = list(self.iter_widgets())
        t0 = time.time()
        while True:
            self.process_events()
            executed = (signal_manager.widget_is_executed(widget) for widget in widgets)
            executed = list(executed)
            if all(executed):
                break
            if timeout is not None:
                t1 = time.time()
                timeout -= t1 - t0
                if timeout < 0:
                    raise TimeoutError
                t0 = t1
            time.sleep(0.1)

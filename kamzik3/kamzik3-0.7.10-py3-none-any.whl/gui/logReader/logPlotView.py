import pyqtgraph as pg
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMdiSubWindow

from kamzik3.snippets.snippetsUnits import get_scaled_time_duration

pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")


class TimeAxisItem(pg.AxisItem):
    """This class converts unix timestamps into HH:mm format for X axis."""

    x_values = None

    def __init__(self, *args, **kwargs):
        pg.AxisItem.__init__(self, *args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        """
        Convert all timestamps into HH:mm Strings.

        :param values: List of timestamps
        :param scale: float
        :param spacing: float
        :return:
        """
        if self.x_values is None or len(self.x_values) == 0:
            return []
        values = values - self.x_values[0]
        return [get_scaled_time_duration(value, short=True) for value in values]


class LogPlotView(pg.PlotWidget):
    sig_repaint = pyqtSignal()

    def __init__(self, parent=None, background="default", **kwargs):
        self.time_Axis = TimeAxisItem(orientation="bottom")
        super().__init__(
            parent, background, axisItems={"bottom": self.time_Axis}, **kwargs
        )
        try:
            self.base_unit = kwargs.get("unit", "")
        except TypeError:
            self.base_unit = ""

        pen1 = pg.mkPen(color=kwargs.get("color", (0, 0, 255)))
        self.value_curve = pg.PlotDataItem([], [], pen=pen1)
        self.setLabel("left", kwargs.get("left_label", ""), units=self.base_unit)
        self.setLabel("bottom", kwargs.get("bottom_label", None))
        self.setTitle(kwargs.get("top_label", None))
        self.showGrid(x=True, y=True, alpha=0.1)
        self.getAxis("left").enableAutoSIPrefix(False)
        self.addItem(self.value_curve)
        self.sig_repaint.connect(self.slot_set_data)

    @pyqtSlot()
    def slot_set_data(self, x, y):
        self.time_Axis.x_values = x
        self.value_curve.setData(x, y)

    def close(self):
        self.reset()
        super().close()

    def reset(self):
        self.x_buffer.clear()
        self.y_buffer.clear()
        self.value_curve.setData([], [])


class LogPlotViewMaster(LogPlotView):
    def __init__(self, parent=None, background="default", **kwargs):
        super().__init__(parent, background, **kwargs)

        self.lookingGlass = pg.LinearRegionItem([0, 0])
        self.lookingGlass.setZValue(-10)
        self.addItem(self.lookingGlass)

    @pyqtSlot()
    def slot_set_data(self, x, y):
        self.time_Axis.x_values = x
        self.value_curve.setData(x, y)
        if len(x) > 0:
            zoom_from, zoom_to = int(len(x) * 0.4), int(len(x) * 0.6)
            self.lookingGlass.setRegion([x[zoom_from], x[zoom_to]])

    def reset_zoom(self):
        zoom_from, zoom_to = 0, len(self.value_curve.xData) - 1
        self.lookingGlass.setRegion(
            [self.value_curve.xData[zoom_from], self.value_curve.xData[zoom_to]]
        )


class QMdiSubWindowPlot(QMdiSubWindow):
    def __init__(self, id, parent=None):
        self.id = id
        QMdiSubWindow.__init__(self, parent)

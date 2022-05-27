import collections

import pint
import pyqtgraph as pg
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QGridLayout

from kamzik3 import units
from kamzik3.constants import *
from kamzik3.gui.deviceWidget import DeviceWidget
from kamzik3.snippets.snippetsYaml import YamlSerializable

pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")


class AttributePlot(pg.PlotWidget, YamlSerializable):
    sig_repaint = pyqtSignal()

    def __init__(
        self,
        attribute,
        buffer_size,
        plot=None,
        parent=None,
        background="#fff",
        **kwargs
    ):
        super().__init__(parent, background, **kwargs)
        self.current_point = 0
        self.attribute = attribute
        self.x_buffer = collections.deque([], maxlen=buffer_size)
        self.y_buffer = collections.deque([], maxlen=buffer_size)
        try:
            self.base_unit = kwargs.get("unit", attribute[UNIT])
        except (TypeError, KeyError):
            self.base_unit = ""

        pen1 = pg.mkPen(color=(0, 0, 255))
        pen2 = pg.mkPen(color=(0, 0, 0))
        self.value_curve = pg.PlotDataItem(
            self.x_buffer,
            self.y_buffer,
            pen=pen1,
            antialias=False,
            symbol="s",
            symbolSize=2,
            symbolPen=pen2,
        )
        if plot is None:
            self.setLabel("left", kwargs.get("left_label", ""), units=self.base_unit)
            if kwargs.get("bottom_label") is not None:
                self.setLabel("bottom", kwargs.get("bottom_label"))
            if kwargs.get("top_label"):
                self.setLabel("top", kwargs.get("top_label"))
            self.showGrid(x=True, y=True, alpha=0.1)
            self.addItem(self.value_curve)
            self.getAxis("left").enableAutoSIPrefix(False)
            self.main_plot = self
        else:
            plot.setLabel("left", kwargs.get("left_label", ""), units=self.base_unit)
            if kwargs.get("bottom_label") is not None:
                self.setLabel("bottom", kwargs.get("bottom_label"))
            if kwargs.get("top_label"):
                self.setLabel("top", kwargs.get("top_label"))
            plot.showGrid(x=True, y=True, alpha=0.1)
            plot.addItem(self.value_curve)
            plot.getAxis("left").enableAutoSIPrefix(False)
            self.main_plot = plot
        self.sig_repaint.connect(self.slot_set_data)

    def yaml_mapping(self):
        mapping = super().yaml_mapping()
        del mapping["parent"]
        return mapping

    @pyqtSlot()
    def slot_set_data(self):
        if self.main_plot.isVisible():
            if self.main_plot.parent() is None or self.main_plot.parent().isVisible():
                self.value_curve.setData(self.x_buffer, self.y_buffer)

    def update(self, current_point=None, current_value=None):
        if current_point is None:
            self.current_point += 1
        else:
            self.current_point = current_point
        if current_value is None:
            try:
                current_value = self.attribute.value().to(self.base_unit).m
            except (AttributeError, pint.errors.DimensionalityError):
                # Value is None, ignore this point
                return
        else:
            assert isinstance(current_value, units.Quantity)
            current_value = current_value.to(self.base_unit).m
        try:
            self.y_buffer.append(current_value)
            self.x_buffer.append(self.current_point)
        except Exception as e:
            print(e, current_point, current_value)
            return
        self.sig_repaint.emit()

    def close(self):
        self.attribute = None
        self.current_point = 0
        self.reset()
        super().close()

    def reset(self):
        self.x_buffer.clear()
        self.y_buffer.clear()
        self.value_curve.setData([], [])


class DeviceAttributePlot(DeviceWidget):
    def __init__(
        self,
        device,
        attribute,
        buffer_size,
        max_update_rate=300,
        plot=None,
        parent=None,
        background="#fff",
        **kwargs
    ):
        self.attribute = attribute
        self.kwargs = kwargs
        self.buffer_size = buffer_size
        self.max_update_rate = max_update_rate
        self.plot = plot
        self.background = background
        DeviceWidget.__init__(self, device, parent=parent)

    # pylint: disable=unused-argument
    def setupUi(self, form):
        layout = QGridLayout()
        self.setLayout(layout)

    @pyqtSlot()
    def slot_handle_configuration(self):
        """
        Handle widget configuration.

        If overloading make sure to set configured flag.
        """
        self.configured = True
        attribute = self.device.get_attribute(self.attribute)
        if self.kwargs.get("top_label") == "auto":
            self.kwargs["top_label"] = self.device.device_id
        if self.kwargs.get("left_label") == "auto":
            self.kwargs["left_label"] = self.attribute
        attribute_plot = AttributePlot(
            attribute,
            self.buffer_size,
            plot=self.plot,
            background=self.background,
            **self.kwargs
        )
        self.layout().addWidget(attribute_plot)
        attribute.attach_callback(
            lambda _: attribute_plot.update(),
            max_update_rate=self.max_update_rate,
            key_filter=VALUE,
        )

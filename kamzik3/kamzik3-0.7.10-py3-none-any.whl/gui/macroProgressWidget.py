import logging

from PyQt5.QtCore import pyqtSlot, pyqtSignal
from pyqtgraph import GraphicsLayoutWidget

import kamzik3
from kamzik3 import units
from kamzik3.constants import *
from kamzik3.gui.attributePlot import AttributePlot
from kamzik3.gui.deviceWidget import DeviceWidget
from kamzik3.gui.templates.macroProgressTemplate import Ui_Form


class MacroProgressWidget(Ui_Form, DeviceWidget):
    sig_update_progress = pyqtSignal("float")
    sig_update_plot = pyqtSignal(object)
    sig_update_macro_status = pyqtSignal("QString")

    def __init__(self, device, template, model_image=None, config=None, parent=None):
        self.template = template
        self.plot_widgets = []
        self.plot_area = GraphicsLayoutWidget()
        self.logger = logging.getLogger("Gui.MacroProgressWidget")
        super().__init__(device, model_image, config, parent)
        self.plot_widget.layout().addWidget(self.plot_area)

    def _init_macro_plots(self):
        for index, value in enumerate(self.device.get_chain_link_output()):
            if value is not None:
                (device_id, attribute_name, points) = value
                device = kamzik3.session.get_device(device_id)
                attribute = device.get_attribute(attribute_name)
                left_label = "{} - {}".format(device_id, attribute_name)
                plot = self.plot_area.addPlot(index, 0)
                plot.setParent(self.plot_area)
                attribute_plot = AttributePlot(
                    attribute, buffer_size=points, left_label=left_label, plot=plot
                )
                self.plot_widgets.append(attribute_plot)
            else:
                self.plot_widgets.append(None)

    @pyqtSlot()
    def slot_handle_configuration(self):
        """
        Handle widget configuration.

        If overloading make sure to set configured flag.
        """
        self._init_macro_plots()
        self.device.attach_attribute_callback(ATTR_PROGRESS, self.progress_update)
        self.device.attach_attribute_callback(ATTR_CHAIN_LINK_OUTPUT, self.plot_update)
        self.sig_update_progress.connect(self.set_macro_progress)
        self.sig_update_plot.connect(self.set_plot_update)
        self.button_start.hide()
        DeviceWidget.slot_handle_configuration(self)

    @pyqtSlot("float")
    def set_macro_progress(self, progress):
        self.progress_bar.setFormat("{0:.2f}%".format(progress))
        self.progress_bar.setValue(progress)
        self.label_macro_step_progress.setText(
            "  {} / {}  ".format(
                int(self.device[ATTR_POINT_INDEX][VALUE]),
                int(self.device[ATTR_POINTS_COUNT][VALUE]),
            )
        )
        self.label_running_time.setText(
            "  {}  ".format(self.device[ATTR_RUNNING_TIME][VALUE])
        )
        self.label_remaining_time.setText(
            "  {}  ".format(self.device[ATTR_REMAINING_TIME][VALUE])
        )
        self.label_estimated_finish.setText(
            "  {}  ".format(self.device[ATTR_ESTIMATED_END][VALUE])
        )

    def set_plot_update(self, link_data):
        macro_point, chain_link, current_value = link_data
        if self.device[ATTR_POINT_INDEX][VALUE] > 0:
            plot_widget = self.plot_widgets[chain_link]
            if plot_widget is not None:
                current_value = units.Quantity(current_value)
                plot_widget.update(macro_point, current_value)

    @pyqtSlot("PyQt_PyObject")
    def slot_set_status(self, value):
        """
        This slot is always called when device status has changed.

        Recall thic method when overloading.

        :param value:
        """
        if not self.configured and value in READY_DEVICE_STATUSES:
            self.slot_handle_configuration()
        if value == STATUS_BUSY:
            self.button_stop.setDisabled(False)
            self.button_start.setDisabled(True)
            for plot in self.plot_widgets:
                if plot is not None:
                    plot.reset()
        elif value in (STATUS_IDLE, STATUS_ERROR):
            self.button_stop.setDisabled(True)
            self.button_start.setDisabled(False)
        elif value not in READY_DEVICE_STATUSES:
            self.button_stop.setDisabled(True)
            self.button_start.setDisabled(True)

        self.label_status.setText(value)
        self.label_status.setStyleSheet(
            "QLabel {{background:{}}}".format(
                DeviceWidget.status_colors.get(value, "blue")
            )
        )

    def progress_update(self, key, value):
        if key == VALUE:
            self.sig_update_progress.emit(value)

    def status_update(self, key, value):
        if key == VALUE:
            self.sig_update_macro_status.emit(value)

    def plot_update(self, key, value):
        if key == VALUE:
            self.sig_update_plot.emit(value)

    @pyqtSlot()
    def start(self):
        self.device.start()

    @pyqtSlot()
    def stop(self):
        self.device.stop()

    def close(self):
        self.device.detach_attribute_callback(ATTR_PROGRESS, self.progress_update)
        for plot in self.plot_widgets:
            if plot is None:
                continue
            plot.close()
            del plot
        del self.template
        del self.plot_widgets
        del self.plot_area
        macro = self.device
        DeviceWidget.close(self)
        macro.remove()

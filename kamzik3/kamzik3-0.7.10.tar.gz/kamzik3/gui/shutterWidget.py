from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QLabel
from kamzik3.gui.attributeDeviceDisplayWidget import AttributeDeviceDisplayWidget

from kamzik3.constants import *
from kamzik3.gui.attributeWidgets.attributeBoolWidget import AttributeBoolWidget
from kamzik3.gui.deviceWidget import DeviceWidget
from kamzik3.gui.general.stackableWidget import StackableWidget
from kamzik3.gui.templates.shutterTemplate import Ui_Form
from kamzik3.snippets.snippetsYaml import YamlSerializable


class ShutterWidget(Ui_Form, DeviceWidget, StackableWidget, YamlSerializable):
    sig_opened_status_changed = pyqtSignal("PyQt_PyObject", "PyQt_PyObject")
    sig_auto_mode_changed = pyqtSignal("PyQt_PyObject", "PyQt_PyObject")
    configured = False

    def __init__(self, device, config=None, parent=None):
        self.value_controls = {}
        DeviceWidget.__init__(self, device, config, parent)

    def setupUi(self, Form):
        super().setupUi(Form)
        self.button_close.setVisible(False)
        self.button_open.setVisible(False)
        self.set_status_label(self.device.get_value(ATTR_STATUS))
        self.label_device_name.setText(self.device_id)
        self.setEnabled(False)

    def init_signals(self):
        super().init_signals()
        self.sig_opened_status_changed.connect(self.change_opened_status)

    def set_device(self, device):
        DeviceWidget.__init__(self, device)
        self.label_axis_name.setText(device.device_id)
        self.set_status_label(device.get_value(ATTR_STATUS))
        self.value_controls = (
            self.label_auto_mode,
            self.checkbox_auto_mode,
            self.button_open,
            self.button_close,
        )

    def open_shutter(self):
        self.device.open_shutter()

    def close_shutter(self):
        self.device.close_shutter()

    def stop(self):
        self.device.stop()

    @pyqtSlot()
    def set_status_label(self, status):
        self.label_status.setText(status)
        self.label_status.setStyleSheet(
            "QLabel {{background:{}}}".format(self.get_status_color(status))
        )

    @pyqtSlot()
    def slot_handle_configuration(self):
        DeviceWidget.slot_handle_configuration(self)
        self.device.attach_attribute_callback(
            ATTR_OPENED, self.sig_opened_status_changed.emit
        )
        self.set_opened(self.device.get_value(ATTR_OPENED))
        auto_mode_widget = AttributeDeviceDisplayWidget(self.device, ATTR_AUTO_MODE)
        self.widget_holder.layout().insertWidget(3, auto_mode_widget)

    @pyqtSlot("bool")
    def slot_set_enabled(self, value):
        self.setEnabled(value)

    @pyqtSlot("PyQt_PyObject")
    def slot_set_status(self, value):
        DeviceWidget.slot_set_status(self, value)

        if value in READY_DEVICE_STATUSES:
            self.setEnabled(True)
        else:
            self.setEnabled(False)
            return

        if value == STATUS_BUSY:
            self.button_stop.setEnabled(True)
            self.button_close.setEnabled(False)
            self.button_open.setEnabled(False)
        else:
            self.button_stop.setEnabled(False)
            self.set_opened(self.device.get_value(ATTR_OPENED))

        self.set_status_label(value)

    @pyqtSlot("PyQt_PyObject", "PyQt_PyObject")
    def change_opened_status(self, key, value):
        if key == VALUE:
            self.set_opened(value)

    def set_opened(self, flag):
        self.label_open_status.setText("Opened" if flag else "Closed")
        self.label_open_status.setStyleSheet(
            "QLabel {{background:{}}}".format("red" if flag else "#68d532")
        )
        if flag:
            self.button_close.setVisible(True)
            self.button_open.setVisible(False)
            self.button_close.setEnabled(True)
        else:
            self.button_close.setVisible(False)
            self.button_open.setVisible(True)
            self.button_open.setEnabled(True)


class ManualShutterWidget(ShutterWidget):
    """Implementation of the ShutterWidget without auto_mode Widget."""

    def set_device(self, device):
        DeviceWidget.__init__(self, device)
        self.label_axis_name.setText(device.device_id)
        self.set_status_label(device.get_value(ATTR_STATUS))
        self.value_controls = (self.button_open, self.button_close)

    @pyqtSlot()
    def slot_handle_configuration(self):
        DeviceWidget.slot_handle_configuration(self)
        self.device.attach_attribute_callback(
            ATTR_OPENED, self.sig_opened_status_changed.emit
        )
        self.set_opened(self.device.get_value(ATTR_OPENED))

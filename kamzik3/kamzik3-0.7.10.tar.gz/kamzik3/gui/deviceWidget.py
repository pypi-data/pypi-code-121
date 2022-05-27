import logging
from typing import Union

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget

import kamzik3
from kamzik3 import DeviceError
from kamzik3.constants import *
from kamzik3.devices.device import Device
from kamzik3.devices.observer import Observer
from kamzik3.snippets.snippetsWidgets import show_error_message
from kamzik3.snippets.snippetsYaml import YamlSerializable


class DeviceWidget(Observer, QWidget, YamlSerializable):
    sigHandleConfiguration = pyqtSignal()
    sigEnable = pyqtSignal("bool")
    sigStatus = pyqtSignal("PyQt_PyObject")
    sigErrorCheck = pyqtSignal("PyQt_PyObject", "PyQt_PyObject")
    sigShowModel = pyqtSignal("QIcon")
    sigHideModel = pyqtSignal("QIcon")
    device = None
    status_colors = {
        STATUS_DISCONNECTED: "silver",
        STATUS_CONNECTING: "#d532cc",
        STATUS_CONFIGURING: "#d532cc",
        STATUS_CONFIGURED: "#68d532",
        STATUS_IDLE: "#68d532",
        STATUS_ERROR: "#d53232",
        STATUS_BUSY: "#3290d5",
        STATUS_DISCONNECTING: "silver",
    }
    model_image = None
    config = None
    configured = False

    def __init__(
        self, device: Union[Device, str], model_image=None, config=None, parent=None
    ):
        QWidget.__init__(self)
        Observer.__init__(parent)
        if isinstance(device, Device):
            self.device_id = device.device_id
            self.device = device
        else:
            self.device_id = device
            if kamzik3.session is not None:
                self.device = kamzik3.session.get_device(device)
            else:
                raise DeviceError("kamzik3 session is None")
        if model_image is not None:
            self.model_image = QIcon(model_image)
        self.config = config
        if self.config is None:
            self.config = {}
        self.logger = logging.getLogger("Gui.Device.{}".format(self.device_id))
        self.setupUi(self)  # type: ignore
        self.init_signals()
        self.attach_to_subject(self.device)

    def init_signals(self):
        self.sigHandleConfiguration.connect(self.slot_handle_configuration)
        self.sigEnable.connect(self.slot_set_enabled)
        self.sigStatus.connect(self.slot_set_status)
        self.sigErrorCheck.connect(self.slot_check_error)

    def yaml_mapping(self):
        mapping = super().yaml_mapping()
        del mapping["parent"]
        return mapping

    @pyqtSlot("PyQt_PyObject", "PyQt_PyObject")
    def slot_check_error(self, attribute, output):
        if attribute == RESPONSE_ERROR:
            self.logger.error(output)
            show_error_message(output, parent=self)

    @pyqtSlot()
    def slot_handle_configuration(self):
        """
        Handle widget configuration.

        If overloading make sure to set configured flag.
        """
        self.configured = True

    @pyqtSlot("bool")
    def slot_set_enabled(self, value):
        raise NotImplementedError("Not implemented")

    @pyqtSlot("PyQt_PyObject")
    def slot_set_status(self, value):
        """
        This slot is always called when device status has changed.

        Recall this method when overloading.

        :param value:
        """
        if not self.configured and value in READY_DEVICE_STATUSES:
            self.slot_handle_configuration()

    def on_status_changed(self, key, value):
        if key == VALUE:
            self.sigStatus.emit(value)

    def on_enabled_changed(self, key, value):
        if key == VALUE:
            self.sigEnable.emit(value)

    def subject_update(self, key, value, subject):
        """
        This method is called by observing device.

        Useual key is ATTR_STATUS.

        :param key: mixed
        :param value: mixed
        :param subject: Subject
        """
        if key == ATTR_STATUS:
            self.on_status_changed(VALUE, value)

    def get_status_color(self, status=None):
        """
        Get color for each STATUS.

        Overload status_colors if You want to use different status colors.

        :param status: string
        :return: status color
        """
        if status is None:
            status = self.device.get_value(ATTR_STATUS)

        return self.status_colors.get(status, "blue")

    def show_setpoints_history(self):
        print("test", self.input_value.setpoints_history)

    def close(self):
        self.detach_subject(self.device)
        self.device.detach_observer(self)
        self.device = None
        self.model_image = None
        self.sigHandleConfiguration.disconnect()
        self.sigEnable.disconnect()
        self.sigStatus.disconnect()
        self.sigErrorCheck.disconnect()
        self.setParent(None)
        QWidget.close(self)

from PyQt5.QtCore import pyqtSlot

from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.gui.attributeDeviceDisplayWidget import AttributeDeviceDisplayWidget
from kamzik3.gui.deviceWidget import DeviceWidget
from kamzik3.gui.general.stackableWidget import StackableWidget
from kamzik3.gui.templates.deviceDisplayAttributeTemplate import Ui_Form


class DeviceDisplayAttributeWidget(Ui_Form, DeviceWidget, StackableWidget):
    attribute = None
    debug_widget = None
    input_value = None

    # Probably super should be called
    # pylint: disable=super-init-not-called
    def __init__(self, device, attribute, config=None, parent=None):
        self.attribute = Attribute.list_attribute(attribute)
        DeviceWidget.__init__(self, device, config=config, parent=parent)
        self.set_status_label(self.device.get_value(ATTR_STATUS))
        self.label_device_name.setText(self.device.device_id)

    @pyqtSlot()
    def set_status_label(self, status):
        self.label_status.setText(status)
        self.label_status.setStyleSheet(
            "QLabel {{background:{}}}".format(self.get_status_color(status))
        )

    @pyqtSlot()
    def slot_handle_configuration(self):
        DeviceWidget.slot_handle_configuration(self)

        self.input_not_ready_placeholder.setParent(None)
        layout = self.widget_holder.layout()
        self.input_value = AttributeDeviceDisplayWidget(
            self.device_id, self.attribute, config=self.config
        )
        layout.insertWidget(2, self.input_value)

    @pyqtSlot("bool")
    def slot_set_enabled(self, value):
        self.self.input_value.setEnabled(value)

    @pyqtSlot("PyQt_PyObject")
    def slot_set_status(self, value):
        DeviceWidget.slot_set_status(self, value)

        if value in READY_DEVICE_STATUSES:
            if self.input_value is not None:
                self.input_value.setEnabled(True)
        else:
            if self.input_value is not None:
                self.input_value.setEnabled(False)

        self.set_status_label(value)

    def close(self):
        self.input_value.close()
        self.input_value = None
        self.attribute = None
        self.input_value = None
        super().close()


class DeviceDisplayAttributesListWidget(DeviceDisplayAttributeWidget):
    # pylint: disable=super-init-not-called
    def __init__(self, device, attributes_list, config=None, parent=None):
        self.attributes = []
        self.display_widgets = []
        for attribute in attributes_list:
            self.attributes.append(Attribute.list_attribute(attribute))
        # Bad style, fix later if possible
        # pylint: disable=non-parent-init-called
        DeviceWidget.__init__(self, device, config=config, parent=parent)
        self.set_status_label(self.device.get_value(ATTR_STATUS))
        self.label_device_name.setText(self.device.device_id)

    @pyqtSlot()
    def slot_handle_configuration(self):
        DeviceWidget.slot_handle_configuration(self)

        self.input_not_ready_placeholder.setParent(None)
        layout = self.widget_holder.layout()
        for attribute in reversed(self.attributes):
            display_widget = AttributeDeviceDisplayWidget(
                self.device_id, attribute, config=self.config
            )
            self.display_widgets.append(display_widget)
            layout.insertWidget(2, display_widget)

    @pyqtSlot("bool")
    def slot_set_enabled(self, value):
        for display_widget in self.display_widgets:
            display_widget.setEnabled(value)

    @pyqtSlot("PyQt_PyObject")
    def slot_set_status(self, value):
        DeviceWidget.slot_set_status(self, value)

        if value in READY_DEVICE_STATUSES:
            if self.input_value is not None:
                self.slot_set_enabled(True)
        else:
            if self.input_value is not None:
                self.slot_set_enabled(False)

        self.set_status_label(value)

    def close(self):
        self.input_value.close()
        self.input_value = None
        self.attributes = None
        self.display_widgets = None
        super().close()

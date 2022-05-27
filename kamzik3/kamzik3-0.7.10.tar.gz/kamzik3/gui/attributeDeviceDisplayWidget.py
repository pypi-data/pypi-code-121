import time
from collections import deque

import pint
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from pint import DimensionalityError
from typing import Dict, Tuple

from kamzik3 import units, DeviceError
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.devices.device import Device
from kamzik3.gui.attributeDisplayWidget import AttributeDisplayWidget
from kamzik3.gui.deviceWidget import DeviceWidget
from kamzik3.snippets.snippetsWidgets import show_error_message


class AttributeDeviceDisplayWidget(DeviceWidget, AttributeDisplayWidget):
    sigAttributeChanged = pyqtSignal("PyQt_PyObject", "PyQt_PyObject")
    attribute = None
    # Global history for every device display attribute
    setpoints_history: deque = deque(maxlen=100)
    # Global dictionary for last device, attribute unit
    user_attribute_units: Dict[Tuple, str] = {}

    # Should super() be called? Not sure, disable for now
    # pylint: disable=super-init-not-called
    def __init__(self, device, attribute, config=None, parent=None):
        self.initial_attribute = Attribute.list_attribute(attribute)
        self.config = config
        if self.config is None:
            self.config = {}
        self.title = self.initial_attribute[-1]

        if isinstance(device, Device):
            self.attribute_device_key = (
                device.device_id,
                tuple(self.initial_attribute),
            )
        else:
            self.attribute_device_key = (device, tuple(self.initial_attribute))

        DeviceWidget.__init__(self, device, config=config, parent=parent)

    def init_signals(self):
        super().init_signals()
        self.sigAttributeChanged.connect(self.slot_attribute_changed)

    def setupUi(self, parent=None):
        return

    def on_attribute_changed(self, key, value):
        self.sigAttributeChanged.emit(key, value)

    def get_current_user_unit(self):
        return AttributeDeviceDisplayWidget.user_attribute_units.get(
            self.attribute_device_key, None
        )

    @pyqtSlot("QString")
    def set_unit(self, unit=None, reset=False):
        self.attribute_widget.set_unit(unit, reset)

    @pyqtSlot()
    def slot_handle_configuration(self):
        DeviceWidget.slot_handle_configuration(self)

        self.attribute = self.device.get_attribute(self.initial_attribute)
        AttributeDisplayWidget.setupUi(self)

        current_user_unit = self.get_current_user_unit()
        if current_user_unit is not None:
            self.unit_widget.set_unit(current_user_unit)

        self.unit_widget.sig_unit_changed.connect(self.set_unit)
        self.unit_widget.sig_unit_changed.connect(self.on_user_unit_changed)
        self.input_widget.reset_on_blur = True
        self.slot_observing_start()

    @pyqtSlot("QString")
    def on_user_unit_changed(self, unit):
        AttributeDeviceDisplayWidget.user_attribute_units[
            self.attribute_device_key
        ] = unit

    @pyqtSlot("bool")
    def slot_set_enabled(self, value):
        self.input_widget.setEnabled(value)
        self.setEnabled(value)

    @pyqtSlot()
    def slot_observing_start(self):
        if self.device is not None:
            self.device.attach_attribute_callback(
                self.initial_attribute,
                self.on_attribute_changed,
                self.config.get("max_update_rate"),
            )
            self.device.attach_attribute_callback(ATTR_ENABLED, self.on_enabled_changed)
            self.setEnabled(self.device.get_value(ATTR_ENABLED))
            self.update_value()

    @pyqtSlot()
    def slot_observing_stop(self):
        if self.device is not None:
            self.device.detach_attribute_callback(
                self.initial_attribute, self.on_attribute_changed
            )
            self.device.detach_attribute_callback(ATTR_ENABLED, self.on_enabled_changed)

    def update_value(self):
        if self.attribute is not None:
            self.set_value(self.attribute.value())

    # def hideEvent(self, hide_event):
    #     self.slot_observing_stop()
    #     DeviceWidget.hideEvent(self, hide_event)
    #
    # pylint: disable=unused-argument
    def showEvent(self, show_event):
        self.update_value()
        # self.slot_observing_start()
        # DeviceWidget.showEvent(self, show_event)

    def _add_in_setpoint_history(self, value):
        """
        Add setpoint into setpoint setpoints_history list.

        Each input is in format (epoch time, device ID, attribute name, previous value,
        current setpoint)

        :param value:
        """
        previous_value = self.attribute.value()
        if previous_value is not None:
            previous_value = previous_value.to(self.get_unit())
        self.setpoints_history.append(
            (time.time(), self.device_id, self.initial_attribute, previous_value, value)
        )

    def on_value_set(self, value):
        if isinstance(value, units.Quantity) or (
            self.attribute.numerical and self.get_unit() is not None
        ):
            if not isinstance(value, units.Quantity):
                try:
                    value = units.Quantity(value, self.get_unit())
                    value = value.to(self.attribute[UNIT])
                except (
                    AttributeError,
                    pint.UndefinedUnitError,
                    pint.DefinitionSyntaxError,
                ):
                    value = units.Quantity(value)
            else:
                value = value.to(self.attribute[UNIT])

            if self.attribute.within_limits(value):
                value = value.m
                self._add_in_setpoint_history(value)
                self.logger.info(
                    "Set {} to {} {}".format(
                        self.initial_attribute, value, self.attribute[UNIT]
                    )
                )
            else:
                self.logger.info(f"Can't set value {value}, out of limits")
                value = self.attribute.value().m  # set value back to what it was before

        elif self.attribute[TYPE] == TYPE_LIST:
            value = self.get_widget_value()

        try:
            self.device.set_attribute(
                self.initial_attribute + [VALUE],  # e.g. ['Position', 'Value']
                self.attribute_widget.attribute_type_cast(value),
                callback=self.sigErrorCheck.emit,
            )
        except DeviceError as e:
            # Set value back to what it was before
            self.set_value(self.attribute.value())
            show_error_message(e, parent=self)

        self.input_widget.setFocus()
        self.input_widget.clearFocus()
        if self.parent() is not None:
            self.parent().clearFocus()

    @pyqtSlot("PyQt_PyObject")
    def slot_set_status(self, value):
        DeviceWidget.slot_set_status(self, value)
        if not self.isVisible():
            return
        elif value in READY_DEVICE_STATUSES:
            self.setEnabled(self.device.get_value(ATTR_ENABLED))
        elif value in (STATUS_DISCONNECTED, STATUS_DISCONNECTING):
            self.setDisabled(True)

    @pyqtSlot("PyQt_PyObject", "PyQt_PyObject")
    def slot_attribute_changed(self, key, value):
        if self.attribute is None:
            return
        if self.isVisible() and key == VALUE:
            if (
                self.input_widget is not None
                and self.input_widget.hasFocus()
                or value is None
            ):
                return
            if self.attribute.numerical:
                try:
                    self.set_value(units.Quantity(value, self.attribute[UNIT]))
                except AttributeError:
                    self.set_value(units.Quantity(value))
                except DimensionalityError:
                    self.set_value(
                        units.Quantity(units.Quantity(value).m, self.get_unit())
                    )
            else:
                self.set_value(value)
        elif key == UNIT:
            self.attribute_widget.unit = value
            self.unit_widget.set_unit(value)
            self.set_unit(value, True)
            self.set_minimum(units.Quantity(self.attribute[MIN], value))
            self.set_maximum(units.Quantity(self.attribute[MAX], value))
            self.slot_attribute_changed(VALUE, self.attribute[VALUE])
        elif key == MIN:
            self.set_minimum(units.Quantity(value, self.attribute[UNIT]))
        elif key == MAX:
            self.set_maximum(units.Quantity(value, self.attribute[UNIT]))
        elif key == FACTOR:
            self.slot_attribute_changed(VALUE, self.attribute[VALUE])

    def close(self):
        self.sigAttributeChanged.disconnect()
        try:
            self.device.detach_attribute_callback(
                self.initial_attribute, self.on_attribute_changed
            )
            self.device.detach_attribute_callback(ATTR_ENABLED, self.on_enabled_changed)
        except:
            pass
        self.initial_attribute = None
        self.config = None
        DeviceWidget.close(self)
        AttributeDisplayWidget.close(self)

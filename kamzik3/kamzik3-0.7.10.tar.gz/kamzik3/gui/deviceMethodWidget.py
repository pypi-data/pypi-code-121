from typing import Callable, List, Optional, Tuple, Union

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QSizePolicy,
    QLineEdit,
)
from kamzik3.gui.attributeDeviceDisplayWidget import AttributeDeviceDisplayWidget

from kamzik3 import DeviceError, units
from kamzik3.constants import *
from kamzik3.devices.device import Device
from kamzik3.gui.attributeDisplayWidget import AttributeDisplayWidget
from kamzik3.gui.deviceWidget import DeviceWidget
from kamzik3.gui.general.stackableWidget import StackableWidget
from kamzik3.gui.templates.deviceMethodTemplate import Ui_Form
from kamzik3.snippets.snippetsWidgets import (
    QSpinBox,
    QDoubleSpinBox,
    show_error_message,
)


class DeviceMethodWidget(Ui_Form, DeviceWidget, StackableWidget):
    attribute = None
    input_value: Optional[QWidget] = None

    # Probably super should be called
    # pylint: disable=super-init-not-called
    def __init__(
        self,
        device: Union[Device, str],
        method: Callable,
        model_image=None,
        config=None,
        parent=None,
    ):
        self.method = method
        self.value_controls: Tuple[QWidget, ...] = ()
        DeviceWidget.__init__(
            self, device, model_image=model_image, config=config, parent=parent
        )
        if self.device is not None:
            self.set_status_label(self.device.get_value(ATTR_STATUS))
        self.label_device_name.setText(self.device_id)

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
        self.input_value = self.method_widget()
        layout.insertWidget(2, self.input_value)
        self.set_status_label(self.device.get_value(ATTR_STATUS))
        self.value_controls = (self.input_value,)

    def method_widget(self) -> QWidget:
        if self.device is None:
            raise DeviceError("Cannot generate a method widget, the device is None")
        device_methods = self.device.exposed_methods
        method_widget = QWidget()

        def exec_method(method_name, argument_inputs=None):
            kwargs = {}
            for argument_input in argument_inputs:
                if isinstance(argument_input, AttributeDisplayWidget):
                    value = argument_input.get_attribute_value()
                    if isinstance(value, units.Quantity):
                        # ~ is a pint format specification
                        kwargs[argument_input.name] = "{:~}".format(value)  # type: ignore
                    else:
                        kwargs[argument_input.name] = value
                else:
                    kwargs[argument_input.name] = argument_input.text()
            try:
                getattr(self.device, method_name)(**kwargs)
            except DeviceError as e:
                show_error_message(e, parent=self)

        layout = QHBoxLayout(method_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        for (method_name, method_attributes) in device_methods:
            if method_name == self.method:
                method_label = QLabel(method_name + " (")
                method_label.setAlignment(
                    Qt.AlignCenter | Qt.AlignRight  # type: ignore
                )
                method_label.setStyleSheet("QLabel {font-weight:bold}")
                layout.addWidget(method_label)
                method_execute_button = QPushButton("< Call >")
                method_execute_button.setSizePolicy(
                    QSizePolicy.Fixed, QSizePolicy.Fixed
                )
                argument_inputs: List[Union[AttributeDisplayWidget, QLineEdit]] = []
                if method_attributes:
                    inputs_widget = QWidget()
                    inputs_layout = QHBoxLayout()
                    inputs_widget.setLayout(inputs_layout)
                    for attribute_title, attribute_type in method_attributes.items():
                        device_attribute = self.device.get_attribute(attribute_type)
                        if device_attribute is None:
                            inputs_layout.addWidget(
                                QLabel("{}".format(attribute_title))
                            )
                            input_value = QLineEdit()
                            input_value.setPlaceholderText(attribute_type)
                            input_value.name = attribute_title  # type: ignore
                            inputs_layout.addWidget(input_value)
                            argument_inputs.append(input_value)
                        else:
                            attribute_widget = AttributeDisplayWidget(
                                attribute_title, device_attribute
                            )
                            attribute_widget.name = attribute_title
                            if attribute_widget.label_widget is not None:
                                inputs_layout.addWidget(attribute_widget.label_widget)
                            if attribute_widget.input_widget is not None:
                                inputs_layout.addWidget(attribute_widget.input_widget)
                            if attribute_widget.unit_widget is not None:
                                inputs_layout.addWidget(attribute_widget.unit_widget)
                            argument_inputs.append(attribute_widget)
                    layout.addWidget(inputs_widget)
                else:
                    label = QLabel("None")
                    label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
                    label.setStyleSheet("QLabel {font-weight:bold}")
                    layout.addWidget(label)

                method_execute_button.released.connect(
                    lambda method_name=method_name, argument_inputs=argument_inputs: exec_method(
                        method_name, argument_inputs
                    )
                )
                method_label = QLabel(")")
                method_label.setStyleSheet("QLabel {font-weight:bold}")
                layout.addWidget(method_label)
                layout.addWidget(method_execute_button)
                break

        return method_widget

    @pyqtSlot("bool")
    def slot_set_enabled(self, value):
        self.setEnabled(value)

    @pyqtSlot("PyQt_PyObject")
    def slot_set_status(self, value):
        DeviceWidget.slot_set_status(self, value)

        if value in READY_DEVICE_STATUSES:
            self.setEnabled(True)
            if value == STATUS_BUSY:
                for widget in self.value_controls:
                    widget.setEnabled(False)
                self.button_stop.setEnabled(True)
            else:
                for widget in self.value_controls:
                    widget.setEnabled(True)
                self.button_stop.setEnabled(False)
        else:
            self.setEnabled(False)

        self.set_status_label(value)

    @pyqtSlot()
    def stop(self):
        self.device.stop()

    def close(self):
        if self.input_value is not None:
            self.input_value.close()
        self.input_value = None
        super().close()


class DeviceMethodEnabledWidget(DeviceMethodWidget):
    """
    Same class as DeviceMethodWidget except that the widget is enabled independently
    of the status of the device.
    """

    @pyqtSlot("PyQt_PyObject")
    def slot_set_status(self, value):
        DeviceWidget.slot_set_status(self, value)

        if value in READY_DEVICE_STATUSES:
            self.setEnabled(True)
            for widget in self.value_controls:
                widget.setEnabled(True)

            if value == STATUS_BUSY:
                self.button_stop.setEnabled(True)
            else:
                self.button_stop.setEnabled(False)
        else:
            self.setEnabled(False)

        self.set_status_label(value)


class MethodEnabledByAttributeWidget(DeviceMethodEnabledWidget):
    """
    The input fields of this method widget will be disabled when the attribute is True,
    enabled when it is False.

    This widget is used for the `start_run` method of the TapeDrive Runner, and the
    attribute used for enabling/disabling is the external trigger (chopper).
    """

    sig_control_changed = pyqtSignal("PyQt_PyObject")  # Python object type unknown

    def __init__(
        self,
        device: Union[Device, str],
        method: Callable,
        external_device_attribute: Tuple[Device, str],
        model_image=None,
        config=None,
        parent=None,
    ) -> None:
        self.external_device_attribute = external_device_attribute
        super().__init__(
            device=device,
            method=method,
            model_image=model_image,
            config=config,
            parent=parent,
        )

    def control_changed(self, value: bool) -> None:
        """
        Slot executed when a signal is emitted from `sig_control_changed`.
        """
        editable_widgets = self._find_editable_widgets()
        if self.input_value is not None:
            for index in editable_widgets:
                if value:
                    self.input_value.children()[index].setEnabled(False)  # type: ignore
                else:
                    self.input_value.children()[index].setEnabled(True)  # type: ignore

    def _find_editable_widgets(self) -> List[int]:
        """Find the indices of the input fields that should be enabled/disabled"""
        editable_widgets: List[int] = []
        if self.input_value is not None:
            for idx, child in enumerate(self.input_value.children()):
                if type(child) == QWidget:  # pylint: disable=unidiomatic-typecheck
                    # Here the exact type is needed, or it will pick up all widgets
                    # inherited from it
                    for grandchild in child.children():
                        if isinstance(grandchild, (QSpinBox, QDoubleSpinBox)):
                            editable_widgets.append(idx)
                            break
        return editable_widgets

    def init_signals(self) -> None:
        """
        Connect the signals to the slots.

        This method is called in DeviceWidget.__init__
        """
        super().init_signals()
        self.sig_control_changed.connect(self.control_changed)

    @pyqtSlot()
    def slot_handle_configuration(self) -> None:
        DeviceWidget.slot_handle_configuration(self)
        self.input_not_ready_placeholder.setParent(None)
        layout = self.widget_holder.layout()
        self.input_value = self.method_widget()
        layout.insertWidget(2, self.input_value)

        # find the index of the widgets to be enabled/disabled
        self._find_editable_widgets()

        # emit a signal each time the external trigger value is changed
        # callback(attribute_object[key_filter]) is called
        if self.device is not None:
            self.device.attach_attribute_callback(
                attribute=ATTR_EXTERNAL_TRIGGER,
                callback=self.sig_control_changed.emit,
                key_filter=VALUE,
            )

            # define the status of the input field
            # using the current value of the attribute
            self.control_changed(self.device.get_value(ATTR_EXTERNAL_TRIGGER))

            # create the checkbox for the attribute
            control_widget = AttributeDeviceDisplayWidget(
                device=self.external_device_attribute[0],
                attribute=self.external_device_attribute[1],
            )
            self.widget_holder.layout().insertWidget(3, control_widget)

            self.set_status_label(self.device.get_value(ATTR_STATUS))
            self.value_controls = (self.input_value,)


class DeviceSimpleMethodsListWidget(DeviceMethodWidget):
    # Probably should be called
    # pylint: disable=super-init-not-called
    def __init__(
        self, device, methods_list, model_image=None, config=None, parent=None
    ):
        self.methods_list = methods_list
        self.value_controls = []
        self.input_values = []
        # Bad style
        # pylint: disable=non-parent-init-called
        DeviceWidget.__init__(
            self, device, model_image=model_image, config=config, parent=parent
        )
        self.set_status_label(self.device.get_value(ATTR_STATUS))
        self.label_device_name.setText(self.device_id)

    @pyqtSlot()
    def slot_handle_configuration(self):
        DeviceWidget.slot_handle_configuration(self)

        self.input_not_ready_placeholder.setParent(None)
        layout = self.widget_holder.layout()
        layout.insertStretch(2)
        for required_method in reversed(self.methods_list):
            input_value = self.required_method_widget(required_method)
            layout.insertWidget(2, input_value)
            self.set_status_label(self.device.get_value(ATTR_STATUS))
            self.value_controls.append(input_value)
            self.input_values.append(input_value)

    def required_method_widget(self, required_method_name):
        device_methods = self.device.exposed_methods
        method_widget = QWidget()

        def exec_method(method_name, argument_inputs=None):
            kwargs = {}
            for argument_input in argument_inputs:
                if isinstance(argument_input, AttributeDisplayWidget):
                    value = argument_input.get_attribute_value()
                    if isinstance(value, units.Quantity):
                        # ~ is a pint format specification
                        kwargs[argument_input.name] = "{:~}".format(value)  # type: ignore
                    else:
                        kwargs[argument_input.name] = value
            try:
                getattr(self.device, method_name)(**kwargs)
            except DeviceError as e:
                show_error_message(e, parent=self)

        layout = QHBoxLayout(method_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        for (method_name, _method_attributes) in device_methods:
            if method_name == required_method_name:
                method_execute_button = QPushButton(method_name)
                method_execute_button.setSizePolicy(
                    QSizePolicy.Fixed, QSizePolicy.Fixed
                )
                argument_inputs = []

                method_execute_button.released.connect(
                    lambda method_name=method_name, argument_inputs=argument_inputs: exec_method(
                        method_name, argument_inputs
                    )
                )
                layout.addWidget(method_execute_button)
                break

        return method_widget

    def close(self):
        for input in self.input_values:
            input.close()
        self.input_values = None
        super().close()


class DeviceSimpleAttributeMethodsListWidget(DeviceSimpleMethodsListWidget):
    def __init__(
        self,
        device,
        attributes_list,
        methods_list,
        model_image=None,
        config=None,
        parent=None,
    ):
        self.attributes_list = attributes_list
        DeviceSimpleMethodsListWidget.__init__(
            self, device, methods_list, model_image, config, parent
        )

    @pyqtSlot()
    def slot_handle_configuration(self):
        DeviceWidget.slot_handle_configuration(self)

        self.input_not_ready_placeholder.setParent(None)
        layout = self.widget_holder.layout()
        layout.insertStretch(2)
        for required_method in reversed(self.methods_list):
            input_value = self.required_method_widget(required_method)
            layout.insertWidget(2, input_value)
            self.set_status_label(self.device.get_value(ATTR_STATUS))
            self.value_controls.append(input_value)
            self.input_values.append(input_value)

        for attribute in reversed(self.attributes_list):
            input_value = AttributeDeviceDisplayWidget(self.device_id, attribute)
            layout.insertWidget(2, input_value)
            self.value_controls.append(input_value)
            self.input_values.append(input_value)

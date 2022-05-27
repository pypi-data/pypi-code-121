from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QPushButton,
    QLabel,
    QSizePolicy,
    QWidget,
    QHBoxLayout,
    QLineEdit,
    QSpacerItem,
    QGridLayout,
    QFrame,
)
from kamzik3.devices.deviceClient import DeviceClient

from kamzik3 import DeviceClientError, CommandFormatException, DeviceError, units
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.gui.attributeDeviceDisplayWidget import AttributeDeviceDisplayWidget
from kamzik3.gui.attributeDisplayWidget import AttributeDisplayWidget
from kamzik3.gui.deviceWidget import DeviceWidget
from kamzik3.gui.templates.deviceDebugTemplate import Ui_Form
from kamzik3.snippets.snippetsWidgets import clear_layout, show_error_message


class DeviceDebugWidget(Ui_Form, DeviceWidget):
    sigNewCommand = pyqtSignal("QString")
    command_terminator = None

    def __init__(self, device=None, config=None, parent=None):
        self.groups = []
        DeviceWidget.__init__(self, device, config=config, parent=parent)
        if not isinstance(self.device, DeviceClient):
            self.button_reconnect.hide()

    def setupUi(self, Form):
        super().setupUi(Form)
        self.button_connect.hide()
        self.button_enable.hide()
        self.label_device_id.setText(self.device_id)
        self.button_enable.setEnabled(False)
        self.button_disable.setEnabled(False)
        self.button_terminal.setEnabled(False)
        self.page_3.setEnabled(False)
        self.setWindowTitle("{} debug".format(self.device_id))
        self.setWindowIcon(QIcon(":/icons/icons/settings.png"))

    def init_signals(self):
        super().init_signals()
        self.sigNewCommand.connect(self.output_commands.setPlainText)

    def keyPressEvent(self, key_event):
        if key_event.key() == Qt.Key_Escape and hasattr(self.device, "stop"):
            self.device.stop()

        DeviceWidget.keyPressEvent(self, key_event)

    @pyqtSlot()
    def slot_handle_configuration(self):
        DeviceWidget.slot_handle_configuration(self)
        if len(self.groups) == 0:
            self.generate_attribute_layout()
            self.generate_methods_layout()

        self.device.attach_attribute_callback(ATTR_ENABLED, self.on_enabled_changed)

    @pyqtSlot("PyQt_PyObject")
    def slot_set_status(self, value):
        DeviceWidget.slot_set_status(self, value)
        if value in READY_DEVICE_STATUSES:
            self.button_disconnect.show()
            self.button_disconnect.setEnabled(True)
            self.button_connect.hide()

            self.button_enable.setEnabled(True)
            self.button_disable.setEnabled(True)
            self.button_terminal.setEnabled(True)
            self.page.setEnabled(True)
            self.page_2.setEnabled(True)
            self.page_3.setEnabled(True)
            self.page_4.setEnabled(True)
            self.slot_set_enabled(self.device.get_value(ATTR_ENABLED))
            self.button_reconnect.hide()
        else:
            self.button_enable.setEnabled(False)
            self.button_disable.setEnabled(False)
            self.button_terminal.setEnabled(False)
            self.page.setEnabled(False)
            self.page_2.setEnabled(False)
            self.page_3.setEnabled(False)
            self.page_4.setEnabled(False)
            self.button_disconnect.hide()
            self.button_connect.show()
            if isinstance(self.device, DeviceClient):
                self.button_reconnect.show()
        if value == STATUS_DISCONNECTED:
            self.button_connect.setEnabled(True)

        self.label_device_id.setStyleSheet(
            "QLabel {{background:{}}}".format(self.get_status_color(value))
        )

    @pyqtSlot("bool")
    def slot_set_enabled(self, value):
        self.button_enable.setVisible(not value)
        self.button_disable.setVisible(value)
        self.page.setEnabled(value)
        self.page_2.setEnabled(value)
        self.page_3.setEnabled(value)
        self.page_4.setEnabled(value)

    @pyqtSlot(int)
    # pylint: disable=unused-argument
    def slot_attribute_group_changed(self, page):
        self.tab_attribute_groups.currentWidget().setFocus()

    def show_attributes_widget(self):
        self.logger.debug("Showing page with device attributes")
        self.widgets_stack.setCurrentIndex(0)

    def show_configuration_widget(self):
        self.logger.debug("Showing page with device configuration")
        self.widgets_stack.setCurrentIndex(1)

    def show_terminal_widget(self):
        self.logger.debug("Showing page with device terminal")
        self.widgets_stack.setCurrentIndex(2)
        self.input_command.setFocus()

    def show_methods_widget(self):
        self.logger.debug("Showing page with methods")
        self.widgets_stack.setCurrentIndex(3)

    def send_command(self):
        self.input_command.selectAll()
        command = self.input_command.text().strip()
        if self.command_terminator:
            command += self.command_terminator
        self.logger.debug("Sending command: {0!r}".format(command))
        try:
            self.device.command(
                command,
                callback=self.receive_command,
                returning=self.returning.isChecked(),
            )
        except (DeviceClientError, CommandFormatException, DeviceError) as e:
            self.logger.exception("Sending command error")
            self.sigNewCommand.emit(str(e))

    def receive_command(self, *args):
        if isinstance(args[-1], list):
            self.sigNewCommand.emit("".join(args[-1]))
        else:
            self.sigNewCommand.emit(args[-1])

    def disconnect_device(self):
        self.logger.debug("Disconnecting from device")
        self.device.disconnect()
        self.button_disconnect.setDisabled(True)

    def connect_device(self):
        self.logger.debug("Connecting to device")
        self.device.reconnect()
        self.button_connect.setDisabled(True)

    def enable_device(self):
        self.logger.debug("Enabling device")
        self.device.set_attribute((ATTR_ENABLED, VALUE), 1)

    def disable_device(self):
        self.logger.debug("Disabling device")
        self.device.set_attribute((ATTR_ENABLED, VALUE), 0)

    def generate_methods_layout(self):
        device_methods = self.device.exposed_methods
        layout = self.widget_grid_for_methods.layout()

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
                output = getattr(self.device, method_name)(**kwargs)
            except DeviceError as e:
                show_error_message(e, parent=self)
                output = e
            self.output_methods.setPlainText(
                "{} output:\n'{}'".format(method_name, output)
            )

        if device_methods:
            for row, (method_name, method_attributes) in enumerate(device_methods):

                method_label = QLabel(method_name + " (")
                method_label.setAlignment(Qt.AlignCenter | Qt.AlignRight)
                method_label.setStyleSheet("QLabel {font-weight:bold}")
                layout.addWidget(method_label, row, 1)
                method_execute_button = QPushButton("< Call >")
                method_execute_button.setSizePolicy(
                    QSizePolicy.Fixed, QSizePolicy.Fixed
                )
                argument_inputs = []
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
                            input_value.name = attribute_title
                            inputs_layout.addWidget(input_value)
                            argument_inputs.append(input_value)
                        else:
                            attribute_widget = AttributeDisplayWidget(
                                attribute_title, device_attribute.attribute_copy()
                            )
                            attribute_widget.name = attribute_title
                            inputs_layout.addWidget(attribute_widget.label_widget)
                            inputs_layout.addWidget(attribute_widget.input_widget)
                            inputs_layout.addWidget(attribute_widget.unit_widget)
                            argument_inputs.append(attribute_widget)
                    layout.addWidget(inputs_widget, row, 2)
                else:
                    label = QLabel("None")
                    label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
                    label.setStyleSheet("QLabel {font-weight:bold}")
                    layout.addWidget(label, row, 2)

                method_execute_button.released.connect(
                    lambda method_name=method_name, argument_inputs=argument_inputs: exec_method(
                        method_name, argument_inputs
                    )
                )
                method_label = QLabel(")")
                method_label.setStyleSheet("QLabel {font-weight:bold}")
                layout.addWidget(method_label, row, 3)
                layout.addWidget(method_execute_button, row, 0)

            spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
            # We're using row although the loop is over. Not good design, but it works as long as we have rows
            # (as far as I can tell)
            # pylint: disable=undefined-loop-variable
            layout.addItem(spacer, row + 1, 2)
        else:
            label = QLabel("No methods available")
            label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
            label.setStyleSheet("QLabel {font-size:15px; font-weight:bold}")
            layout.addWidget(label, 0, 0)

    def generate_attribute_layout(self):
        group = self._generate_attribute_group("General")
        self._generate_attribute_groups(
            self.device.attributes, group, attribute_path=[]
        )

    def _reset_attribute_layout(self):
        while self.groups:
            self.tab_attribute_groups.removeTab(0)
            clear_layout(self.groups[0], self.groups[0].layout())
            self.groups[0].deleteLater()
            del self.groups[0]
        self.groups = []

    def _generate_attribute_groups(self, attributes, group, attribute_path):
        column, row = 0, 0
        columns = 4 if self.config is None else self.config.get("columns", 4)
        is_picture_in = False
        for key, value in attributes.items():
            if Attribute.is_attribute(value):
                if value.get(DISPLAY) is False:
                    continue
                if column % columns == 0:
                    row += 1
                    column = 0
                attribute_widget = self._generate_attribute_element(
                    attribute_path + [key]
                )
                attribute_widget.setParent(group)
                group.layout().addWidget(attribute_widget, row, column)
                column += 1
                if value.get(DISPLAY) == IMAGE:
                    is_picture_in = True
            else:
                new_group = self._generate_attribute_group(key)
                self._generate_attribute_groups(
                    value, new_group, attribute_path + [key]
                )
        if not is_picture_in:
            spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
            group.layout().addItem(spacer, row + 1, 0)

        row_count = group.layout().rowCount()
        column_count = group.layout().columnCount()
        for col in range(column_count - 1):
            line = QFrame()
            line.setFrameShape(QFrame.VLine)
            line.setFrameShadow(QFrame.Plain)
            line.setStyleSheet(
                "QFrame {color: #f0f0f0; padding-left: 5px; padding-right: 5px}"
            )
            group.layout().addWidget(line, 1, col + 1, row_count, 1)

    def _generate_attribute_group(self, group_title):
        group_widget = QWidget()
        layout = QGridLayout(group_widget)
        layout.setParent(group_widget)
        layout.setContentsMargins(9, 9, 9, 9)
        layout.setSpacing(9)
        self.groups.append(group_widget)
        self.tab_attribute_groups.insertTab(
            len(self.groups) - 1, group_widget, group_title
        )
        return group_widget

    def _generate_attribute_element(self, attribute_path):
        config = {
            "label_width": 110,
        }
        attribute_widget = AttributeDeviceDisplayWidget(
            self.device_id, attribute=attribute_path, config=config
        )
        return attribute_widget

    def set_command_terminator(self, terminator):
        if terminator == "None":
            self.command_terminator = None
        elif terminator == "\\r\\n":
            self.command_terminator = "\r\n"
        elif terminator == "\\r":
            self.command_terminator = "\r"
        elif terminator == "\\n":
            self.command_terminator = "\n"
        elif terminator == "\\t":
            self.command_terminator = "\t"

    def filter_attributes(self):
        filter_string = self.input_attribute_filter.text()
        attributes_layout = self.tab_attribute_groups.currentWidget().layout()
        for widget_index in range(attributes_layout.count()):
            widget = attributes_layout.itemAt(widget_index).widget()
            if isinstance(widget, AttributeDeviceDisplayWidget):
                if widget.title.find(filter_string) != -1:
                    widget.show()
                else:
                    widget.hide()

    def close(self):
        self.device.detach_attribute_callback(ATTR_ENABLED, self.on_enabled_changed)
        self.tab_attribute_groups.blockSignals(True)
        self._reset_attribute_layout()
        return DeviceWidget.close(self)

    def reconnect_device(self):
        try:
            self.device.server_reconnect()
        except Exception as e:
            show_error_message(e, parent=self)

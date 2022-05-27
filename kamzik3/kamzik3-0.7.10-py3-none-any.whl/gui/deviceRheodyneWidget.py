from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QLabel, QPushButton

from kamzik3.constants import *
from kamzik3.gui.attributeDeviceDisplayWidget import AttributeDeviceDisplayWidget
from kamzik3.gui.deviceWidget import DeviceWidget
from kamzik3.gui.general.stackableWidget import StackableWidget
from kamzik3.gui.templates.deviceRheodyneTemplate import Ui_Form


class DeviceRheodyneWidget(Ui_Form, DeviceWidget, StackableWidget):
    configured = False

    # Probably should be called.
    # pylint: disable=super-init-not-called
    def __init__(self, device, config=None, parent=None):
        self.value_controls = {}
        DeviceWidget.__init__(self, device, config, parent)
        self.set_status_label(self.device.get_value(ATTR_STATUS))
        self.label_device_name.setText(self.device_id)
        self.setEnabled(False)

    @pyqtSlot()
    def slot_handle_configuration(self):
        DeviceWidget.slot_handle_configuration(self)

        active_switches = self.device.get_value(ATTR_ACTIVE_SWITCHES)
        for switch in range(active_switches):
            self.add_switch(switch + 1)

        self.add_macros()

    @pyqtSlot("PyQt_PyObject")
    def slot_set_status(self, value):
        DeviceWidget.slot_set_status(self, value)
        if value in READY_DEVICE_STATUSES:
            self.setEnabled(True)
        else:
            self.setEnabled(False)

        self.set_status_label(value)

    @pyqtSlot()
    def set_status_label(self, status):
        self.label_status.setText(status)
        self.label_status.setStyleSheet(
            "QLabel {{background:{}}}".format(self.get_status_color(status))
        )

    def add_macros(self):
        row = 0
        for macro_name, _ in self.device.exposed_methods:
            if macro_name == "stop_all_tasks":
                continue

            macro_button = QPushButton(macro_name)
            macro_button.clicked.connect(
                lambda *args, macro_name=macro_name: getattr(self.device, macro_name)()
            )
            self.layout_macro_grid.addWidget(macro_button, int(row / 3), row % 3)
            row += 1

    def add_switch(self, switch_number):
        switch_name = "Switch{}".format(switch_number)
        current_sample_widget = AttributeDeviceDisplayWidget(
            self.device, [switch_name, ATTR_CURRENT_SAMPLE]
        )
        switch_label = QLabel(switch_name)
        switch_label.setStyleSheet(
            "QLabel {font-weight:bold;background:#f6b442;padding:5}"
        )
        self.layout_switch_list.addWidget(switch_label, 0, switch_number)
        self.layout_switch_list.addWidget(current_sample_widget, 1, switch_number)

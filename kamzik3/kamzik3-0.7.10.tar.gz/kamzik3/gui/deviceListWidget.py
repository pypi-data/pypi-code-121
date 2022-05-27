from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget
import re

import kamzik3
from kamzik3.constants import *
from kamzik3.gui.deviceDisplayAttributeWidget import DeviceDisplayAttributeWidget
from kamzik3.gui.templates.deviceListTemplate import Ui_Form
from kamzik3.snippets.snippetsWidgets import clear_layout
from kamzik3.snippets.snippetsYaml import YamlSerializable


class DeviceListWidget(Ui_Form, QWidget, YamlSerializable):
    def __init__(
        self, columns, title=None, default_widgets=None, config=None, parent=None
    ):
        super().__init__(parent)
        self.config = config
        self.title = title
        self.widgets = []
        self.columns = columns
        self.setupUi(self)
        if default_widgets is not None:
            for widget in default_widgets:
                self.add_widget(widget)

    def yaml_mapping(self):
        mapping = super().yaml_mapping()
        del mapping["parent"]
        return mapping

    def setupUi(self, Form):
        super().setupUi(Form)

        if self.title is not None:
            self.label_device_id.setText(self.title)

        layout = self.widget_content.layout()
        clear_layout(self, layout)

    def add_widget(self, widget):
        layout = self.widget_content.layout()
        row = layout.rowCount() - 1
        new_row = True
        for column in range(self.columns):
            if not layout.itemAtPosition(row, column):
                new_row = False
                break
        if new_row:
            row += 1
            column = 0
        self.widgets.append(widget)
        layout.addWidget(widget, row, column)

    def filter_devices(self):
        filter_string = str(self.input_command.text())
        for widget in self.widgets:
            if re.search(filter_string, widget.device.device_id, re.IGNORECASE):
                widget.show()
            else:
                widget.hide()

    def remove_widget(self, widget):
        widget.close()
        self.widgets.remove(widget)


class DeviceListWidgetSession(DeviceListWidget):
    sigDeviceCountChanged = pyqtSignal("PyQt_PyObject", "PyQt_PyObject")

    def __init__(self, columns, title=None, default_widgets=None, parent=None):
        super().__init__(columns, title, parent)
        self.sigDeviceCountChanged.connect(self.device_count_changed)
        kamzik3.session.attach_attribute_callback(
            ATTR_DEVICES_COUNT, self.sigDeviceCountChanged.emit
        )

    @pyqtSlot("PyQt_PyObject", "PyQt_PyObject")
    # pylint: disable=unused-argument
    def device_count_changed(self, key, value):
        """
        This slot is called when device counter in current session has been changed.

        Get thru all widgets and remove or add new / old devices from list.

        :param key:
        :param value:
        """
        current_devices = list(kamzik3.session.devices.keys())
        for widget in self.widgets[:]:
            if widget.device.device_id not in current_devices:
                self.remove_widget(widget)
            else:
                current_devices.remove(widget.device.device_id)
        for device_id in current_devices:
            self.add_widget(
                DeviceDisplayAttributeWidget(
                    device=device_id,
                    attribute=ATTR_LATENCY,
                    config={"max_update_rate": 400},
                )
            )

    def close(self):
        kamzik3.session.detach_attribute_callback(
            ATTR_DEVICES_COUNT, self.sigDeviceCountChanged.emit
        )
        return super().close()

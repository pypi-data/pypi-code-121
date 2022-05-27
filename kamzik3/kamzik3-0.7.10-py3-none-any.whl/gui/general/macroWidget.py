import numpy as np
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget

import kamzik3
from kamzik3 import units
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.gui.attributeDisplayWidget import AttributeDisplayWidget
from kamzik3.snippets.snippetsYaml import YamlSerializable


class MacroWidget(QWidget, YamlSerializable):

    user_mode = MODE_SIMPLE

    def __init__(self, title=None, config=None, user_mode=MODE_SIMPLE, parent=None):
        self.title = title
        self.user_mode = user_mode
        self.macro_inputs = {}
        self.macro_widgets = {}
        self.config = config
        QWidget.__init__(self, parent)

    def yaml_mapping(self):
        mapping = super().yaml_mapping()
        del mapping["parent"]
        return mapping

    def set_title(self, title=None):
        if title is None:
            title = ""
        self.title = "{} scan".format(title)
        self.label_axis_settings.setText(self.title)

    def _show_method_attribute_widget(self, attribute_title, attribute, row):
        if attribute is None:
            attribute = Attribute("")
        if (
            self.config.get(attribute_title, False)
            and self.config.get(attribute_title, None) is not None
        ):
            attribute[VALUE] = self.config[attribute_title]
        attribute_widget = AttributeDisplayWidget(
            attribute_title, attribute, config={"label_width": 110}
        )
        self.layout().addWidget(attribute_widget.label_widget, row, 0)
        self.layout().addWidget(attribute_widget.input_widget, row, 1)
        self.layout().addWidget(attribute_widget.unit_widget, row, 2)
        self.macro_inputs[attribute_title] = attribute_widget
        return attribute_widget

    def _show_attribute_widget(self, row):
        attribute = self.attribute.attribute_copy()
        attribute_widget = AttributeDisplayWidget(
            "Value", attribute, config={"label_width": 110}
        )
        self.layout().addWidget(attribute_widget.label_widget, row, 0)
        self.layout().addWidget(attribute_widget.input_widget, row, 1)
        self.layout().addWidget(attribute_widget.unit_widget, row, 2)
        self.macro_inputs["value"] = attribute_widget
        return attribute_widget

    def _show_start_point_widget(self, row, default_unit=None):
        attribute = self.attribute.attribute_copy()
        if default_unit is not None and attribute.value() is not None:
            default_value = units.Quantity(
                self.config.get("end_point", attribute.value())
            ).to(default_unit)
        else:
            default_value = self.config.get("end_point", attribute.value())
        attribute[VALUE] = default_value
        start_point_widget = AttributeDisplayWidget(
            "Start point", attribute, config={"label_width": 110}
        )
        if default_unit is not None:
            start_point_widget.set_unit(default_unit)
        self.layout().addWidget(start_point_widget.label_widget, row, 0)
        self.layout().addWidget(start_point_widget.input_widget, row, 1)
        self.layout().addWidget(start_point_widget.unit_widget, row, 2)
        self.macro_inputs["start_point"] = start_point_widget
        start_point_widget.input_widget.valueChanged.connect(
            self.signal_start_end_changed
        )
        return start_point_widget

    def _show_end_point_widget(self, row, default_unit=None):
        attribute = self.attribute.attribute_copy()
        if default_unit is not None and attribute.value() is not None:
            default_value = units.Quantity(
                self.config.get("end_point", attribute.value())
            ).to(default_unit)
        else:
            default_value = self.config.get("end_point", attribute.value())
        attribute[VALUE] = default_value
        end_point_widget = AttributeDisplayWidget(
            "End point", attribute, config={"label_width": 110}
        )
        if default_unit is not None:
            end_point_widget.set_unit(default_unit)
        self.end_point_lock_button.toggled.connect(
            end_point_widget.input_widget.setDisabled
        )
        self.end_point_set_widget.layout().addWidget(end_point_widget.input_widget)
        self.layout().addWidget(end_point_widget.label_widget, row, 0)
        self.layout().addWidget(self.end_point_set_widget, row, 1)
        self.layout().addWidget(end_point_widget.unit_widget, row, 2)
        self.macro_inputs["end_point"] = end_point_widget
        end_point_widget.input_widget.valueChanged.connect(
            self.signal_start_end_changed
        )
        end_point_widget.input_widget.editingFinished.connect(
            self.signal_start_end_check_limits
        )
        return end_point_widget

    def _show_field_size_widget(self, row, default_unit=None):
        field_size_attribute = self.attribute.attribute_copy()
        default_value = 0
        if default_unit is not None:
            default_value = units.Quantity(default_value, default_unit)
        field_size_attribute[VALUE] = default_value
        field_size_attribute[MAX] = abs(
            field_size_attribute[MAX] - field_size_attribute[MIN]
        )
        field_size_attribute[MIN] = 0
        field_size_widget = AttributeDisplayWidget(
            "Field size", field_size_attribute, config={"label_width": 110}
        )
        if default_unit is not None:
            field_size_widget.set_unit(default_unit)
        self.field_size_lock_button.toggled.connect(
            field_size_widget.input_widget.setDisabled
        )
        self.field_size_set_widget.layout().addWidget(field_size_widget.input_widget)
        self.macro_inputs["field_size"] = field_size_widget
        field_size_widget.input_widget.setDisabled(
            self.field_size_lock_button.isChecked()
        )
        self.layout().addWidget(field_size_widget.label_widget, row, 0)
        self.layout().addWidget(self.field_size_set_widget, row, 1)
        self.layout().addWidget(field_size_widget.unit_widget, row, 2)
        field_size_widget.input_widget.valueChanged.connect(
            self.signal_field_size_changed
        )
        field_size_widget.input_widget.editingFinished.connect(
            self.signal_field_size_check_limits
        )
        return field_size_widget

    def _show_step_size_widget(self, row, default_unit=None):
        step_size_attribute = self.attribute.attribute_copy()
        default_value = 0
        if default_unit is not None:
            default_value = units.Quantity(default_value, default_unit)
        step_size_attribute[VALUE] = default_value
        if self.radio_absolute_scan.isChecked():
            distance = abs(step_size_attribute[MAX] - step_size_attribute[MIN])
            step_size_attribute[MIN] = -distance
            step_size_attribute[MAX] = distance
        step_size_widget = AttributeDisplayWidget(
            "Step size", step_size_attribute, config={"label_width": 110}
        )
        if default_unit is not None:
            step_size_widget.set_unit(default_unit)
        self.step_size_set_widget.layout().addWidget(step_size_widget.input_widget)
        self.step_size_lock_button.toggled.connect(
            step_size_widget.input_widget.setDisabled
        )
        step_size_widget.input_widget.setDisabled(
            self.step_size_lock_button.isChecked()
        )
        self.layout().addWidget(self.step_size_set_widget, row, 1)

        if self.radio_relative_scan.isChecked():
            step_size_widget.input_widget.valueChanged.connect(
                self.signal_step_size_changed
            )
            step_size_widget.input_widget.editingFinished.connect(
                self.signal_step_size_check_limits
            )
        else:
            step_size_widget.input_widget.valueChanged.connect(
                self.signal_absolute_step_size_changed
            )
            step_size_widget.input_widget.editingFinished.connect(
                self.signal_absolute_step_size_check_limits
            )
        self.layout().addWidget(step_size_widget.label_widget, row, 0)
        self.layout().addWidget(step_size_widget.unit_widget, row, 2)
        self.macro_inputs["step_size"] = step_size_widget
        return step_size_widget

    def _show_total_steps_widget(self, row):
        default_value = self.config.get("total_steps", 10)
        total_steps_widget = AttributeDisplayWidget(
            "Total steps",
            Attribute(default_value=default_value, min_value=0, default_type=np.uint64),
            config={"label_width": 110},
        )
        self.total_steps_set_widget.layout().addWidget(total_steps_widget.input_widget)
        self.total_steps_lock_button.toggled.connect(
            total_steps_widget.input_widget.setDisabled
        )
        total_steps_widget.input_widget.setDisabled(
            self.total_steps_lock_button.isChecked()
        )
        self.layout().addWidget(self.total_steps_set_widget, row, 1)

        if self.radio_relative_scan.isChecked():
            total_steps_widget.input_widget.valueChanged.connect(
                self.signal_total_steps_changed
            )
            total_steps_widget.input_widget.editingFinished.connect(
                self.signal_total_steps_check_limits
            )
        else:
            total_steps_widget.input_widget.valueChanged.connect(
                self.signal_absolute_total_steps_changed
            )
            total_steps_widget.input_widget.editingFinished.connect(
                self.signal_absolute_total_steps_check_limits
            )
        self.step_size_lock_button.setChecked(False)
        self.layout().addWidget(total_steps_widget.label_widget, row, 0)
        self.macro_inputs["total_steps"] = total_steps_widget
        self.layout().addWidget(total_steps_widget.unit_widget, row, 2)
        return total_steps_widget

    def _show_negative_tolerance_widget(self, row, default_unit=None):
        negative_tolerance_attribute = self.attribute.attribute_copy()
        negative_tolerance_attribute[VALUE] = self.attribute[TOLERANCE][0]
        negative_tolerance_widget = AttributeDisplayWidget(
            "Negative tolerance",
            negative_tolerance_attribute,
            config={"label_width": 110},
        )
        negative_tolerance_widget.input_widget.setPrefix("- ")
        if default_unit is not None:
            negative_tolerance_widget.set_unit(default_unit)
        self.layout().addWidget(negative_tolerance_widget.label_widget, row, 0)
        self.layout().addWidget(negative_tolerance_widget.input_widget, row, 1)
        self.layout().addWidget(negative_tolerance_widget.unit_widget, row, 2)
        self.macro_inputs["negative_tolerance"] = negative_tolerance_widget
        return negative_tolerance_widget

    def _show_positive_tolerance_widget(self, row, default_unit=None):
        positive_tolerance_attribute = self.attribute.attribute_copy()
        positive_tolerance_attribute[VALUE] = self.attribute[TOLERANCE][1]
        positive_tolerance_widget = AttributeDisplayWidget(
            "Positive tolerance",
            positive_tolerance_attribute,
            config={"label_width": 110},
        )
        positive_tolerance_widget.input_widget.setPrefix("+ ")
        if default_unit is not None:
            positive_tolerance_widget.set_unit(default_unit)
        self.layout().addWidget(positive_tolerance_widget.label_widget, row, 0)
        self.layout().addWidget(positive_tolerance_widget.input_widget, row, 1)
        self.layout().addWidget(positive_tolerance_widget.unit_widget, row, 2)
        self.macro_inputs["positive_tolerance"] = positive_tolerance_widget
        return positive_tolerance_widget

    def _show_random_deviation_widget(self, row):
        default_value = units.Quantity(
            self.config.get("Random deviation", "0 percent")
        ).to("percent")
        random_deviation_widget = AttributeDisplayWidget(
            "Random deviation",
            Attribute(
                default_value=default_value,
                decimals=2,
                default_type=np.float16,
                min_value=0,
                max_value=100,
                unit="%",
            ),
            config={"static_unit": True, "label_width": 110},
        )
        self.layout().addWidget(random_deviation_widget.label_widget, row, 0)
        self.layout().addWidget(random_deviation_widget.input_widget, row, 1)
        self.layout().addWidget(random_deviation_widget.unit_widget, row, 2)
        self.macro_inputs["random_deviation"] = random_deviation_widget
        return random_deviation_widget

    def _show_wait_after_widget(self, row):
        default_value = units.Quantity(self.config.get("wait_after", "0s")).to("s")
        wait_after_widget = AttributeDisplayWidget(
            "Wait after",
            Attribute(
                default_value=default_value,
                decimals=0,
                default_type=np.float64,
                min_value=0,
                unit="ms",
                description="Set waiting time after each step.",
            ),
            config={"static_unit": False, "label_width": 110},
        )
        self.layout().addWidget(wait_after_widget.label_widget, row, 0)
        self.layout().addWidget(wait_after_widget.input_widget, row, 1)
        self.layout().addWidget(wait_after_widget.unit_widget, row, 2)
        self.macro_inputs["wait_after"] = wait_after_widget
        return wait_after_widget

    def _show_repeat_widget(self, row):
        repeat_widget = AttributeDisplayWidget(
            "Repeat",
            Attribute(
                default_value=0,
                default_type=np.uint64,
                description="Repeat step after first execution. Set number of repeats.\r\nEach step is executed at least ones",
            ),
            config={"label_width": 110},
        )
        self.layout().addWidget(repeat_widget.label_widget, row, 0)
        self.layout().addWidget(repeat_widget.input_widget, row, 1)
        self.layout().addWidget(repeat_widget.unit_widget, row, 2)
        self.macro_inputs["repeat"] = repeat_widget
        return repeat_widget

    def _show_retry_widget(self, row):
        default_value = self.config.get("retry_count", 0)
        retry_widget = AttributeDisplayWidget(
            "Retry step",
            Attribute(
                default_value=int(default_value),
                default_type=np.uint32,
                min_value=0,
                description="In case of error, retry_count step again.\r\nSet maximum number of retries before throwing an error.",
            ),
            config={"static_unit": True, "label_width": 110},
        )
        self.layout().addWidget(retry_widget.label_widget, row, 0)
        self.layout().addWidget(retry_widget.input_widget, row, 1)
        self.layout().addWidget(retry_widget.unit_widget, row, 2)
        self.macro_inputs["retry_count"] = retry_widget
        return retry_widget

    def _show_busy_timeout(self, row):
        default_value = units.Quantity(self.config.get("busy_timeout", "1000ms")).to(
            "ms"
        )
        busy_timeout_widget = AttributeDisplayWidget(
            "Busy timeout",
            Attribute(
                default_value=default_value,
                decimals=0,
                default_type=np.float64,
                min_value=0,
                unit="ms",
                description="Maximum waiting time for device to change from IDLE to BUSY status. Otherwise consider step as DONE.",
            ),
            config={"static_unit": False, "label_width": 110},
        )
        self.layout().addWidget(busy_timeout_widget.label_widget, row, 0)
        self.layout().addWidget(busy_timeout_widget.input_widget, row, 1)
        self.layout().addWidget(busy_timeout_widget.unit_widget, row, 2)
        self.macro_inputs["busy_timeout"] = busy_timeout_widget
        return busy_timeout_widget

    def _show_timeout(self, row):
        default_value = units.Quantity(self.config.get("timeout", "0s")).to("s")
        timeout_widget = AttributeDisplayWidget(
            "Step timeout",
            Attribute(
                default_value=default_value,
                decimals=0,
                default_type=np.float64,
                min_value=0,
                unit="s",
                description="Maximum waiting time for step to finish.",
            ),
            config={"static_unit": False, "label_width": 110},
        )
        self.layout().addWidget(timeout_widget.label_widget, row, 0)
        self.layout().addWidget(timeout_widget.input_widget, row, 1)
        self.layout().addWidget(timeout_widget.unit_widget, row, 2)
        self.macro_inputs["timeout"] = timeout_widget
        return timeout_widget

    def _show_on_warning_widget(self, row):
        default_value = self.config.get("on_warning", "Abort macro")
        on_warning_widget = AttributeDisplayWidget(
            "On warning",
            Attribute(
                default_value=default_value,
                default_type=["Abort macro", "Skip"],
                description="In case of warning, do specific action.",
            ),
            config={"static_unit": True, "label_width": 110},
        )
        self.layout().addWidget(on_warning_widget.label_widget, row, 0)
        self.layout().addWidget(on_warning_widget.input_widget, row, 1)
        self.layout().addWidget(on_warning_widget.unit_widget, row, 2)
        self.macro_inputs["on_warning"] = on_warning_widget
        return on_warning_widget

    def _get_scanner(self):
        scanner = self.config.get("scanner", "None")
        if scanner == "None":
            scanner = None
        scanner_attributes = {}
        if scanner is not None:
            scanner_device = kamzik3.session.get_device(scanner)
            for attribute in scanner_device.get_scanner_attributes():
                scanner_attributes[attribute] = self.macro_inputs[
                    attribute
                ].get_attribute_value()
        return scanner, scanner_attributes

    def get_input_values(self):
        output = {}
        for key, input in self.macro_inputs.items():
            output[key] = input.get_attribute_value()
        return output

    def get_link(self):
        raise NotImplementedError()

    @pyqtSlot()
    def set_simple_mode(self):
        self.user_mode = MODE_SIMPLE

    @pyqtSlot()
    def set_extended_mode(self):
        self.user_mode = MODE_EXTENDED

    @pyqtSlot()
    def set_all_mode(self):
        self.user_mode = MODE_ALL

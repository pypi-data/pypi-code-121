import kamzik3
from kamzik3 import units
from kamzik3.constants import *
from kamzik3.devices.attribute import Attribute
from kamzik3.gui.deviceDebugWidget import DeviceDebugWidget
from kamzik3.gui.general.macroWidget import MacroWidget
from kamzik3.gui.templates.macroStepTemplate import Ui_Form
from kamzik3.macro.step import (
    StepDeviceMethod,
    StepDeviceAttributeNumerical,
    StepDeviceAttribute,
)
from kamzik3.snippets.snippetsWidgets import show_centralized_top, show_error_message


class MacroStepWidget(Ui_Form, MacroWidget):
    device = None
    attribute = None
    debug_widget = None

    def __init__(
        self, title="Step settings", config=None, user_mode=MODE_SIMPLE, parent=None
    ):
        MacroWidget.__init__(self, user_mode=user_mode, parent=parent)
        self.config = config
        if self.config is None:
            self.config = {}
        self.setupUi(self)
        if self.config.get("step") is not None:
            self.combobox_step.hide()
            self.label_step.hide()

        self.button_settings.setEnabled(False)
        self.method_attributes = []
        self.set_title(title)
        self.spacer = self.gridLayout.itemAtPosition(8, 0)
        self.label_attribute.hide()
        self.combobox_attribute.hide()
        self.label_method.hide()
        self.combobox_method.hide()
        self._init_device_list()
        self._init_scanner_list()
        self._init_template_settings()

    def _init_device_list(self):
        self.combobox_device.blockSignals(True)
        if self.config.get("attribute") is not None:
            attribute = self.config.get("attribute").split(" # ")
            devices_list = list(
                kamzik3.session.get_devices(attribute_filter=attribute).keys()
            )
        elif self.config.get("method") is not None:
            devices_list = list(
                kamzik3.session.get_devices(
                    method_filter=self.config.get("method")
                ).keys()
            )
        else:
            devices_list = list(kamzik3.session.get_devices().keys())

        self.combobox_device.addItems(["None"] + devices_list)
        self.combobox_device.blockSignals(False)

        if self.config.get("device_id") is not None:
            self.combobox_device.setCurrentText(self.config.get("device_id"))

    def _init_step_list(self, device):
        current_text = self.combobox_step.currentText()
        self.combobox_step.clear()
        self.combobox_step.blockSignals(True)
        if device is None:
            self.combobox_step.addItem("None")
        else:
            attribute_list = []
            self.get_devices_macro_steps(device.macro_steps, attribute_list)
            self.combobox_step.addItems(attribute_list)
        index = self.combobox_step.findText(current_text)
        if index == -1:
            self.combobox_step.setCurrentIndex(0)
        else:
            self.combobox_step.setCurrentIndex(index)
        self.combobox_step.blockSignals(False)
        self.step_selected(self.combobox_step.currentText())

    def _init_attribute_list(self, device):
        current_text = self.combobox_attribute.currentText()
        self.combobox_attribute.clear()
        self.combobox_attribute.blockSignals(True)
        if device is None:
            self.combobox_attribute.addItem("None")
        else:
            attribute_list = []
            self.get_settable_attribute_list(device.attributes, attribute_list)
            if len(attribute_list) == 0:
                attribute_list.append("None")
            self.combobox_attribute.addItems(attribute_list)
        index = self.combobox_attribute.findText(current_text)
        if index == -1:
            self.combobox_attribute.setCurrentIndex(0)
        else:
            self.combobox_attribute.setCurrentIndex(index)
        self.combobox_attribute.blockSignals(False)
        self.attribute_selected(self.combobox_attribute.currentText())

    def _init_method_list(self, device):
        current_text = self.combobox_method.currentText()
        self.combobox_method.clear()
        self.combobox_method.blockSignals(True)
        if device is None:
            self.combobox_method.addItem("None")
        else:
            methods_list = []
            self.get_device_methods_list(device.exposed_methods, methods_list)
            if len(methods_list) == 0:
                methods_list.append("None")
            self.combobox_method.addItems(methods_list)
        index = self.combobox_method.findText(current_text)
        if index == -1:
            self.combobox_method.setCurrentIndex(0)
        else:
            self.combobox_method.setCurrentIndex(index)
        self.combobox_method.blockSignals(False)
        self.method_selected(self.combobox_method.currentText())

    def _init_template_settings(self):
        if not self.config.get(CFG_TEMPLATE, False):
            if self.user_mode != MODE_ALL:
                self.label_settings.hide()
                self.widget_settings.hide()
            self.label_scanner.hide()
            self.combobox_scanner.hide()
            self.label_warning.hide()
            self.combobox_warning.hide()

    def _init_scanner_list(self):
        self.combobox_scanner.blockSignals(True)
        devices_list = list(
            kamzik3.session.get_devices(method_filter="get_scanner_attributes").keys()
        )

        self.combobox_scanner.addItems(["None"] + devices_list)
        self.combobox_scanner.blockSignals(False)

        if self.config.get("device_id") is not None:
            self.combobox_scanner.setCurrentText(self.config.get("device_id"))

    def set_title(self, title=None):
        self.title = title
        self.label_axis_settings.setText(title)

    def device_selected(self, device_id):
        if device_id == "None":
            self.device = None
            self._init_step_list(None)
            self.button_settings.setEnabled(False)
        else:
            self.button_settings.setEnabled(True)
            self.device = kamzik3.session.get_device(device_id)
            if self.config.get("attribute") is not None:
                self.attribute_selected(self.config.get("attribute"))
            elif self.config.get("method") is not None:
                self.method_selected(self.config.get("method"))
            else:
                self._init_step_list(self.device)

    def step_selected(self, step_id):
        if step_id == MACRO_SET_ATTRIBUTE_STEP:
            self._init_attribute_list(self.device)
            self.combobox_method.hide()
            self.label_method.hide()
            self.combobox_attribute.show()
            self.label_attribute.show()
        elif step_id == MACRO_EXECUTE_METHOD_STEP:
            self._init_method_list(self.device)
            self.combobox_attribute.hide()
            self.label_attribute.hide()
            self.combobox_method.show()
            self.label_method.show()
        else:
            self.combobox_attribute.hide()
            self.label_attribute.hide()
            self.combobox_method.hide()
            self.label_method.hide()

    def attribute_selected(self, attribute):
        if self.config.get(CFG_TEMPLATE, False):
            return

        for widget in self.macro_widgets:
            widget.close()
            widget.setParent(None)
        self.macro_widgets = []
        self.macro_inputs = {}
        if attribute == "":
            return

        if self.user_mode == MODE_ALL:
            self.label_settings.show()
            self.widget_settings.show()
            self.checkbox_log.setChecked(self.config.get("trigger_log", True))
        else:
            self.label_settings.hide()
            self.widget_settings.hide()

        attribute = attribute.split(" # ")
        self.attribute = self.device.get_attribute(attribute)
        row = 5
        self.macro_widgets.append(self._show_attribute_widget(row))
        row += 1
        if self.config.get("scanner", "None") != "None":
            scanner = kamzik3.session.get_device(self.config["scanner"])
            scanner_attributes = scanner.get_scanner_attributes()
            for attribute_ in scanner_attributes:
                self.macro_widgets.append(
                    self._show_method_attribute_widget(
                        attribute_,
                        scanner.get_attribute(attribute_).attribute_copy(),
                        row,
                    )
                )
                row += 1
        if self.user_mode in (MODE_ALL, MODE_EXTENDED):
            if self.attribute.numerical:
                self.macro_widgets.append(self._show_negative_tolerance_widget(row))
                row += 1
                self.macro_widgets.append(self._show_positive_tolerance_widget(row))
                row += 1
                # self.macro_widgets.append(self._show_random_deviation_widget(row))
                # row += 1
            self.macro_widgets.append(self._show_wait_after_widget(row))
            row += 1
            self.macro_widgets.append(self._show_repeat_widget(row))
            row += 1
            self.macro_widgets.append(self._show_retry_widget(row))
            row += 1
            self.macro_widgets.append(self._show_timeout(row))
            row += 1
            self.macro_widgets.append(self._show_on_warning_widget(row))
            row += 1
        self.layout().removeItem(self.spacer)
        self.layout().addItem(self.spacer, row, 0)

    def method_selected(self, method):
        if self.config.get(CFG_TEMPLATE, False):
            return

        for widget in self.macro_widgets:
            widget.close()
            widget.setParent(None)
        self.macro_widgets = []
        self.macro_inputs = {}
        self.method_attributes = []
        if method == "":
            return

        if self.user_mode == MODE_ALL:
            self.label_settings.show()
            self.widget_settings.show()
            self.checkbox_log.setChecked(self.config.get("trigger_log", True))
        else:
            self.label_settings.hide()
            self.widget_settings.hide()

        row = 5
        for exposed_method in self.device.exposed_methods:
            if exposed_method[0] == method:
                if exposed_method[1] is not None:
                    for attribute_title, attribute_type in exposed_method[1].items():
                        device = kamzik3.session.get_device(
                            self.combobox_device.currentText()
                        )
                        device_attribute = device.get_attribute(attribute_type)
                        self.method_attributes.append(attribute_title)
                        self.macro_widgets.append(
                            self._show_method_attribute_widget(
                                attribute_title, device_attribute, row
                            )
                        )
                        row += 1
                break
        if self.config.get("scanner", "None") != "None":
            scanner = kamzik3.session.get_device(self.config["scanner"])
            scanner_attributes = scanner.get_scanner_attributes()
            for attribute in scanner_attributes:
                self.macro_widgets.append(
                    self._show_method_attribute_widget(
                        attribute,
                        scanner.get_attribute(attribute).attribute_copy(),
                        row,
                    )
                )
                row += 1
        if self.user_mode in (MODE_ALL, MODE_EXTENDED):
            self.macro_widgets.append(self._show_wait_after_widget(row))
            row += 1
            self.macro_widgets.append(self._show_repeat_widget(row))
            row += 1
            self.macro_widgets.append(self._show_retry_widget(row))
            row += 1
            self.macro_widgets.append(self._show_busy_timeout(row))
            row += 1
            self.macro_widgets.append(self._show_timeout(row))
            row += 1
            self.macro_widgets.append(self._show_on_warning_widget(row))
            row += 1

        self.layout().removeItem(self.spacer)
        self.layout().addItem(self.spacer, row, 0)

    def get_settable_attribute_list(self, attributes, output):
        for k, v in attributes.items():
            if Attribute.is_attribute(v):
                if not v[READONLY]:
                    output.append(k)
            else:
                leaf = []
                self.get_settable_attribute_list(v, leaf)
                # pylint: disable=cell-var-from-loop
                output += map(lambda nk: "{} # {}".format(k, nk), leaf)

    @staticmethod
    def get_devices_macro_steps(macro_steps, output):
        for step_title in macro_steps.keys():
            output.append(step_title)

    @staticmethod
    def get_device_methods_list(device_methods, output):
        for method in device_methods:
            output.append(method[0])

    def get_template(self):
        template = {
            "type": "action",
            "device_id": self.combobox_device.currentText(),
            "step": self.combobox_step.currentText(),
            "trigger_log": self.checkbox_log.isChecked(),
            "scanner": self.combobox_scanner.currentText(),
            "on_warning": self.combobox_warning.currentText(),
        }
        if template["step"] == "Set attribute":
            template["attribute"] = self.combobox_attribute.currentText()
        elif template["step"] == "Execute method":
            template["method"] = self.combobox_method.currentText()
        return template

    def save(self):
        if self.combobox_device.currentText() == "None":
            raise KeyError("Device was not set for {}".format(self.title))
        try:
            values = self.get_input_values()
            step = None
            scanner, scanner_attributes = self._get_scanner()
            if self.config.get("attribute") is not None:
                if self.attribute.numerical:
                    step = StepDeviceAttributeNumerical(
                        common_id="Step",
                        device_id=self.combobox_device.currentText(),
                        attribute=self.config.get("attribute").split(" # "),
                        setpoint=values["value"],
                        negative_tolerance=self.attribute.negative_tolerance()
                        if self.user_mode == MODE_SIMPLE
                        else (
                            values["negative_tolerance"]
                            if self.attribute.numerical
                            else None
                        ),
                        positive_tolerance=self.attribute.positive_tolerance()
                        if self.user_mode == MODE_SIMPLE
                        else (
                            values["positive_tolerance"]
                            if self.attribute.numerical
                            else None
                        ),
                        repeat_count=self.config.get("repeat", 0)
                        if self.user_mode == MODE_SIMPLE
                        else values["repeat"],
                        wait_after=units.Quantity(
                            self.config.get("wait_after", "0s")
                            if self.user_mode == MODE_SIMPLE
                            else values["wait_after"]
                        ).to("s"),
                        retry_count=self.config.get("retry_count", 0)
                        if self.user_mode == MODE_SIMPLE
                        else int(values["retry_count"].m),
                        trigger_log=self.checkbox_log.isChecked()
                        if self.user_mode == MODE_ALL
                        else self.config.get("trigger_log", True),
                        on_warning=self.config.get("on_warning", "Abort macro")
                        if self.user_mode == MODE_SIMPLE
                        else values["on_warning"],
                        timeout=units.Quantity(
                            self.config.get("timeout", "0s")
                            if self.user_mode == MODE_SIMPLE
                            else values["timeout"]
                        ).to("s"),
                        scanner=scanner,
                        scanner_attributes=scanner_attributes,
                    )
                else:
                    step = StepDeviceAttribute(
                        common_id="Step",
                        device_id=self.combobox_device.currentText(),
                        attribute=self.config.get("attribute").split(" # "),
                        setpoint=values["value"],
                        repeat_count=self.config.get("repeat", 0)
                        if self.user_mode == MODE_SIMPLE
                        else values["repeat"],
                        wait_after=units.Quantity(
                            self.config.get("wait_after", "0s")
                            if self.user_mode == MODE_SIMPLE
                            else values["wait_after"]
                        ).to("s"),
                        retry_count=self.config.get("retry_count", 0)
                        if self.user_mode == MODE_SIMPLE
                        else int(values["retry_count"].m),
                        trigger_log=self.checkbox_log.isChecked()
                        if self.user_mode == MODE_ALL
                        else self.config.get("trigger_log", True),
                        on_warning=self.config.get("on_warning", "Abort macro")
                        if self.user_mode == MODE_SIMPLE
                        else values["on_warning"],
                        timeout=units.Quantity(
                            self.config.get("timeout", "0s")
                            if self.user_mode == MODE_SIMPLE
                            else values["timeout"]
                        ).to("s"),
                        scanner=scanner,
                        scanner_attributes=scanner_attributes,
                    )
            elif self.config.get("method") is not None:
                method_parameters = {}
                for method_attribute in self.method_attributes:

                    if isinstance(values[method_attribute], units.Quantity):
                        # ~ is a pint format specification
                        method_parameters[method_attribute] = "{:~}".format(  # type: ignore
                            values[method_attribute]
                        )
                    else:
                        method_parameters[method_attribute] = values[method_attribute]
                step = StepDeviceMethod(
                    common_id="Step",
                    device_id=self.combobox_device.currentText(),
                    method=self.config.get("method"),
                    method_parameters=method_parameters,
                    repeat_count=self.config.get("repeat", 0)
                    if self.user_mode == MODE_SIMPLE
                    else values["repeat"],
                    wait_after=units.Quantity(
                        self.config.get("wait_after", "0s")
                        if self.user_mode == MODE_SIMPLE
                        else values["wait_after"]
                    ).to("s"),
                    retry_count=self.config.get("retry_count", 0)
                    if self.user_mode == MODE_SIMPLE
                    else int(values["retry_count"].m),
                    busy_timeout=units.Quantity(
                        self.config.get("busy_timeout", "1000ms")
                        if self.user_mode == MODE_SIMPLE
                        else values["busy_timeout"]
                    ).to("ms"),
                    trigger_log=self.checkbox_log.isChecked()
                    if self.user_mode == MODE_ALL
                    else self.config.get("trigger_log", True),
                    on_warning=self.config.get("on_warning", "Abort macro")
                    if self.user_mode == MODE_SIMPLE
                    else values["on_warning"],
                    timeout=units.Quantity(
                        self.config.get("timeout", "0s")
                        if self.user_mode == MODE_SIMPLE
                        else values["timeout"]
                    ).to("s"),
                    scanner=scanner,
                    scanner_attributes=scanner_attributes,
                )
            return step
        except KeyError:
            raise KeyError("One of attributes for {} were not set".format(self.title))

    def show_debug_widget(self):
        if self.device is None:
            show_error_message("No device selected", parent=self)
            return
        if self.debug_widget is None:
            self.debug_widget = DeviceDebugWidget(self.device)
        elif self.debug_widget.device != self.device:
            self.debug_widget.close()
            self.debug_widget.setParent(None)
            self.debug_widget.deleteLater()
            self.debug_widget = None
            self.debug_widget = DeviceDebugWidget(self.device)

        show_centralized_top(self.debug_widget)

    def set_simple_mode(self):
        MacroWidget.set_simple_mode(self)
        self.device_selected(self.config.get("device_id"))

    def set_extended_mode(self):
        MacroWidget.set_extended_mode(self)
        self.device_selected(self.config.get("device_id"))

    def set_all_mode(self):
        MacroWidget.set_all_mode(self)
        self.device_selected(self.config.get("device_id"))

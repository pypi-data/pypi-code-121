import logging

import oyaml
import yaml
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy, QListWidgetItem

import kamzik3
from kamzik3 import DeviceError
from kamzik3.constants import *
from kamzik3.gui.deviceWidget import DeviceWidget
from kamzik3.gui.macroProgressWidget import MacroProgressWidget
from kamzik3.gui.macroStepWidget import MacroStepWidget
from kamzik3.gui.scanAttributeWidget import ScanAttributeWidget
from kamzik3.gui.templates.macroToolTemplate import Ui_Form
from kamzik3.macro.macro import Macro
from kamzik3.snippets.snippetsGenerators import axis_name_generator
from kamzik3.snippets.snippetsWidgets import (
    clear_layout,
    show_error_message,
    show_prompt_dialog,
    show_info_message,
    show_question_dialog,
)
from kamzik3.snippets.snippetsYaml import YamlDumper

CUSTOM_TEMPLATE = "Custom"


class MacroToolWidget(Ui_Form, DeviceWidget):
    sig_reload_templates = pyqtSignal()
    sig_set_macro_prefix = pyqtSignal()
    sig_running_macro_update = pyqtSignal()
    sig_finished_macro_update = pyqtSignal()
    sig_last_error_update = pyqtSignal(str)

    def __init__(self, device, model_image=None, config=None, parent=None):
        self.available_templates = None
        self.config = config
        self.user_mode = MODE_SIMPLE
        if self.config is None:
            self.config = {}
        self.iterative_widgets = []
        self.action_widgets = []
        self.displayed_macros = {}
        self.loaded_templates = {}
        self.logger = logging.getLogger("Gui.MacroToolWidget")
        self.vertical_spacer = None
        DeviceWidget.__init__(self, device, model_image, config, parent)

    def init_signals(self):
        super().init_signals()
        self.sig_reload_templates.connect(self.slot_reload_templates)
        self.sig_set_macro_prefix.connect(self.slot_set_macro_prefix)
        self.sig_running_macro_update.connect(self.slot_set_running_macros)
        self.sig_finished_macro_update.connect(self.slot_set_finished_macros)
        self.sig_last_error_update.connect(self.slot_handle_last_error)

    @pyqtSlot()
    def slot_handle_configuration(self):
        """
        Handle widget configuration.

        If overloading make sure to set configured flag.
        """
        self.device.attach_attribute_callback(
            ATTR_TEMPLATES_COUNT, lambda _, __: self.sig_reload_templates.emit()
        )
        self.device.attach_attribute_callback(
            ATTR_MACRO_PREFIX, lambda _, __: self.sig_set_macro_prefix.emit()
        )
        self.device.attach_attribute_callback(
            ATTR_RUNNING_COUNT, lambda _, __: self.sig_running_macro_update.emit()
        )
        self.device.attach_attribute_callback(
            ATTR_FINISHED_COUNT, lambda _, __: self.sig_finished_macro_update.emit()
        )
        self.device.attach_attribute_callback(
            ATTR_LAST_ERROR, lambda key, value: self.sig_last_error_update.emit(value)
        )
        self.slot_reload_templates()
        self.slot_set_macro_prefix()
        self.slot_set_running_macros()
        DeviceWidget.slot_handle_configuration(self)

    @pyqtSlot(str)
    def slot_handle_last_error(self, value):
        if len(value) > 0:
            show_error_message(value, self)

    def slot_set_status(self, value):
        if value == STATUS_DISCONNECTED:
            while self.tab_widget_macro_list.count() != 0:
                self.close_macro_tab(0)
        return super().slot_set_status(value)

    @pyqtSlot()
    def slot_reload_templates(self):
        self.loaded_templates = self.device.get_templates()
        self.combobox_template.clear()
        self.combobox_template.blockSignals(True)

        self.combobox_template.addItems(self.loaded_templates.keys())
        self.combobox_template.addItem(CUSTOM_TEMPLATE)
        self.combobox_template.setCurrentText(CUSTOM_TEMPLATE)
        self.combobox_template.blockSignals(False)
        self.template_selected(CUSTOM_TEMPLATE)

    @pyqtSlot()
    def slot_set_macro_prefix(self):
        macro_prefix = self.device.get_value(ATTR_MACRO_PREFIX)
        self.label_new_macro.setText("Create new {}".format(macro_prefix))

    @pyqtSlot()
    def slot_set_running_macros(self):
        for running_macro in self.device.get_running_macros():
            if running_macro not in self.displayed_macros:
                macro = kamzik3.session.get_device(running_macro)
                template, _ = self.device.get_macro_template(macro_id=running_macro)
                running_macro_widget = MacroProgressWidget(macro, template)
                running_macro_widget.setContentsMargins(6, 6, 6, 6)
                self.displayed_macros[running_macro] = running_macro_widget
                self.tab_widget_macro_list.addTab(running_macro_widget, running_macro)
                self.tab_widget_macro_list.setCurrentIndex(
                    self.tab_widget_macro_list.count() - 1
                )

    @pyqtSlot()
    def slot_set_finished_macros(self):
        macros_on_server = (
            self.device.get_finished_macros() + self.device.get_running_macros()
        )
        remove_ids = []
        for widget_index in reversed(range(self.tab_widget_macro_list.count())):
            widget = self.tab_widget_macro_list.widget(widget_index)
            if widget.device.device_id not in macros_on_server:
                remove_ids.append(widget_index)
                self.close_macro_tab(widget_index, False)

    @pyqtSlot()
    def set_simple_mode(self):
        self.user_mode = MODE_SIMPLE
        current_template, _template_filepath = self.loaded_templates.get(
            self.combobox_template.currentText()
        )
        scan_layout = self.widget_macro_list.layout()
        for index, _item in enumerate(current_template["items"]):
            scan_item_widget = scan_layout.itemAt(index).widget()
            scan_item_widget.set_simple_mode()

    @pyqtSlot()
    def set_extended_mode(self):
        self.user_mode = MODE_EXTENDED
        current_template, _template_filepath = self.loaded_templates.get(
            self.combobox_template.currentText()
        )
        scan_layout = self.widget_macro_list.layout()
        for index, _item in enumerate(current_template["items"]):
            scan_item_widget = scan_layout.itemAt(index).widget()
            scan_item_widget.set_extended_mode()

    @pyqtSlot()
    def set_all_mode(self):
        self.user_mode = MODE_ALL
        current_template, _template_filepath = self.loaded_templates.get(
            self.combobox_template.currentText()
        )
        scan_layout = self.widget_macro_list.layout()
        for index, _item in enumerate(current_template["items"]):
            scan_item_widget = scan_layout.itemAt(index).widget()
            scan_item_widget.set_all_mode()

    def get_template_meta(self):
        """
        Go through all widgets in template and export it's meta.

        :return: list of meta data describing template
        """
        meta = []
        layout = self.widget_custom_template.layout()
        for item in range(len(layout)):
            widget = layout.itemAt(item).widget()
            if widget is not None:
                meta.append(widget.get_template())
        return meta

    def export_template(self):
        """Export and save new created template."""
        try:
            items = self.get_template_meta()
        except ValueError as e:
            self.logger.info(e)
            show_error_message(e, self)
            return

        template_title = show_prompt_dialog("Template title")
        if not template_title or template_title == "":
            return

        selected_measurement_groups = [
            item.text() for item in self.list_measurement_groups.selectedItems()
        ]
        data = {
            "title": template_title,
            "iterations": len(self.iterative_widgets),
            "actions": len(self.action_widgets),
            "items": items,
            "measurement_groups": selected_measurement_groups,
        }
        yaml_serialized_data = oyaml.dump(data)
        try:
            template_file = self.device.create_template(
                template_metadata=yaml_serialized_data
            )
            show_info_message(
                "New template {} saved.".format(template_file), parent=self
            )
        except DeviceError as e:
            show_error_message(e, parent=self)

    def remove_template(self):
        """Remove currently selected template."""
        current_template = self.combobox_template.currentText()
        if show_question_dialog(
            "Do You want to remove template {} ?".format(current_template),
            "Remove template",
            self,
        ):
            try:
                self.device.remove_template(template_id=current_template)
            except DeviceError as error_message:
                error_message = "Template could not be removed: {}".format(
                    error_message
                )
                self.logger.error(error_message)
                show_error_message(error_message, self)

    def template_selected(self, template_id):
        if template_id == CUSTOM_TEMPLATE:
            self.reset_template_input()
            self.init_measurement_groups_list()
            self.widget_macro_components.setCurrentWidget(self.page_template_designer)
        else:
            self.reset_macro_input()
            self.widget_macro_components.setCurrentWidget(self.page_macro_components)
            self.generate_macro_layout(self.loaded_templates.get(template_id))

    def reset_template_input(self):
        clear_layout(
            self.scroll_area_custom_template, self.widget_custom_template.layout()
        )
        self.iterative_widgets = []
        self.action_widgets = []
        self.vertical_spacer = QSpacerItem(
            40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

    def reset_macro_input(self):
        clear_layout(self.scroll_area_macro, self.widget_macro_list.layout())
        self.iterative_widgets = []
        self.action_widgets = []
        self.vertical_spacer = QSpacerItem(
            40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding
        )

    def init_measurement_groups_list(self):
        measurement_groups = self.device.get_measurement_groups()
        self.list_measurement_groups.clear()
        for title in measurement_groups.keys():
            self.list_measurement_groups.addItem(QListWidgetItem(title))
        self.list_measurement_groups.setCurrentRow(0)

    def add_action_step(self):
        """
        Add action step widget.

        Which is either set attribute or method.
        """
        self.widget_custom_template.layout().removeItem(self.vertical_spacer)
        step_widget = MacroStepWidget(config={CFG_TEMPLATE: True})
        self.action_widgets.append(step_widget)
        self.widget_custom_template.layout().addWidget(step_widget)
        self.widget_custom_template.layout().addItem(self.vertical_spacer)
        self.update_template_view_step_titles()

    def add_iterative_step(self):
        """
        Add iterative step widget.

        This widget represents any scan over numerical value.
        """
        self.widget_custom_template.layout().removeItem(self.vertical_spacer)
        iterative_widget = ScanAttributeWidget(config={CFG_TEMPLATE: True})
        self.iterative_widgets.append(iterative_widget)
        self.widget_custom_template.layout().addWidget(iterative_widget)
        self.widget_custom_template.layout().addItem(self.vertical_spacer)
        self.update_template_view_step_titles()

    def update_template_view_step_titles(self):
        """
        Since we are using different names for scan widgets like slow, fast scan...

        After adding.
        """
        axis_names = axis_name_generator(len(self.iterative_widgets))
        for widget in self.iterative_widgets:
            widget.set_title(next(axis_names))

    def generate_macro_layout(self, template):
        if template is None:
            return
        meta, _file_path = template
        axis_names = axis_name_generator(meta["iterations"])

        for item in meta.get("items", []):
            if item["type"] == "iterative":
                iterative_widget = ScanAttributeWidget(
                    "{} {}".format(next(axis_names), item["attribute"]),
                    config=item,
                    user_mode=self.user_mode,
                )
                self.iterative_widgets.append(iterative_widget)
                self.widget_macro_list.layout().addWidget(iterative_widget)
            elif item["type"] == "action":
                step_title = None
                if item["step"] == "Set attribute":
                    step_title = "{} {}".format(item["step"], item["attribute"])
                elif item["step"] == "Execute method":
                    step_title = "{} {}".format(item["step"], item["method"])
                action_widget = MacroStepWidget(
                    step_title, config=item, user_mode=self.user_mode
                )
                self.action_widgets.append(action_widget)
                self.widget_macro_list.layout().addWidget(action_widget)

        self.widget_macro_list.layout().addItem(self.vertical_spacer)

    def save(self):
        current_template, _template_filepath = self.loaded_templates.get(
            self.combobox_template.currentText()
        )
        scan_layout = self.widget_macro_list.layout()
        # Create macro for current scan
        macro = Macro(
            "Macro",
            repeat_count=self.input_repeat_macro.value(),
            comment=self.input_comment.text(),
        )
        try:
            # Go through current template and create all steps
            for index, _item in enumerate(current_template["items"]):
                scan_item_widget = scan_layout.itemAt(index).widget()
                step = scan_item_widget.save()
                macro.add(step)
        except (ValueError, KeyError) as e:
            show_error_message(e, self)
            macro.remove()
            return None

        return macro

    def start_macro(self):
        template_id = self.combobox_template.currentText()
        macro = self.save()
        if macro is None:
            return
        yaml_serialized_macro = yaml.dump(macro, Dumper=YamlDumper)
        try:
            macro_id = self.device.upload_macro(
                template_id=template_id, macro_data=yaml_serialized_macro
            )
            self.device.start_macro(macro_id=macro_id)
        except DeviceError as e:
            show_error_message(e, self)

    @pyqtSlot(int)
    def close_macro_tab(self, tab_index, remove_tab=True):
        macro_widget = self.tab_widget_macro_list.widget(tab_index)
        macro_name = macro_widget.device.device_id
        del self.displayed_macros[macro_name]
        if remove_tab:
            self.tab_widget_macro_list.removeTab(tab_index)
        macro_widget.close()

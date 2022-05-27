import os
import re
import time
from collections import OrderedDict
from datetime import datetime
from threading import RLock

import numpy as np
import oyaml
import yaml

import kamzik3
from kamzik3 import DeviceError
from kamzik3.constants import *
from kamzik3.devices.device import Device
from kamzik3.macro.common import StepGenerator
from kamzik3.macro.scan import Scan
from kamzik3.macro.step import StepDeviceAttributeNumerical
from kamzik3.snippets.snippetDataAccess import get_next_file_index
from kamzik3.snippets.snippetsDecorators import expose_method


class MacroServer(Device):
    factory_class_names = {"StepDeviceAttributeNumerical": StepDeviceAttributeNumerical}

    def __init__(self, device_id=None, config=None):
        self.loaded_templates = {}
        self.uploaded_macros = OrderedDict()
        self.running_macros = OrderedDict()
        self.finished_macros = OrderedDict()
        self.update_lock = RLock()
        super().__init__(device_id, config)
        self.connect()

    def handle_configuration(self):
        start_at = time.time()
        self._config_commands()
        self._config_attributes()
        self.set_macro_log_directory()
        self.set_macro_templates_directory()
        self.get_macro_count()
        self.read_scan_templates_directory()
        self.set_status(STATUS_CONFIGURED)
        self.logger.info(
            "Device configuration took {} sec.".format(time.time() - start_at)
        )

    def _init_attributes(self):
        Device._init_attributes(self)
        self.create_attribute(ATTR_TEMPLATES_COUNT, default_value=0, readonly=True)
        self.create_attribute(
            ATTR_MACRO_COUNT, default_value=0, default_type=np.uint64, readonly=True
        )
        self.create_attribute(
            ATTR_MACRO_PREFIX,
            default_value="Scan",
            set_function=self.set_macro_prefix,
            set_value_when_set_function=False,
        )
        self.create_attribute(
            ATTR_UPLOADED_COUNT, default_value=0, default_type=np.uint64, readonly=True
        )
        self.create_attribute(
            ATTR_RUNNING_COUNT, default_value=0, default_type=np.uint64, readonly=True
        )
        self.create_attribute(
            ATTR_FINISHED_COUNT, default_value=0, default_type=np.uint64, readonly=True
        )
        self.create_attribute(
            ATTR_OUTPUT_DIRECTORY,
            default_value=os.path.join(
                kamzik3.session.get_value(ATTR_LOG_DIRECTORY), "Scan_logs"
            ),
            readonly=True,
        )
        self.create_attribute(
            ATTR_TEMPLATE_DIRECTORY,
            default_value=os.path.join(
                kamzik3.session.get_value(ATTR_RESOURCE_DIRECTORY), "Scan_templates"
            ),
            readonly=True,
        )
        self.create_attribute(
            ATTR_MAX_RUNNING_MACROS, default_value=1, default_type=np.uint16
        )
        self.create_attribute(
            ATTR_MAX_MACRO_HISTORY, default_value=1, default_type=np.uint16, min_value=1
        )
        self.create_attribute(
            ATTR_AUTO_CONTROL_SHUTTER, default_value=True, default_type=bool
        )

    def _init_templates(self):
        pass

    def command(self, command, callback=None, with_token=False, returning=True):
        raise DeviceError("Device does not accept any commands.")

    def set_macro_templates_directory(self, value=None):
        if value is not None:
            template_directory_path = os.path.join(
                kamzik3.session.get_value(ATTR_RESOURCE_DIRECTORY), value
            )
        else:
            template_directory_path = self.get_value(ATTR_TEMPLATE_DIRECTORY)

        if not os.path.exists(template_directory_path):
            self.logger.info(
                "Template directory {} does not exists, trying to create it.".format(
                    template_directory_path
                )
            )
            os.makedirs(template_directory_path)

        self.set_value(ATTR_TEMPLATE_DIRECTORY, template_directory_path)
        self.read_scan_templates_directory()

    def read_scan_templates_directory(self):
        self.loaded_templates = {}
        dir_path = self.get_value(ATTR_TEMPLATE_DIRECTORY)
        files = [
            os.path.join(dir_path, f)
            for f in os.listdir(dir_path)
            if os.path.isfile(os.path.join(dir_path, f))
        ]
        files.sort()
        loaded_templates_count = 0
        for file_item in files:
            with open(file_item, "r") as fp:
                template = yaml.load(fp, Loader=yaml.Loader)
                self.loaded_templates[template.get("title")] = (template, file_item)
                loaded_templates_count += 1
        self.set_attribute([ATTR_TEMPLATES_COUNT, VALUE], loaded_templates_count)

    @expose_method()
    def get_measurement_groups(self):
        return kamzik3.session.measurement_groups

    @expose_method()
    def get_templates(self):
        return self.loaded_templates

    @expose_method()
    def get_running_macros(self):
        return list(self.running_macros.keys())

    @expose_method()
    def get_finished_macros(self):
        return list(self.finished_macros.keys())

    @expose_method()
    def get_uploaded_macros(self):
        return list(self.uploaded_macros.keys())

    @expose_method()
    def get_running_macros_meta(self):
        macros_meta_list = []
        for running_macro in self.running_macros.values():
            macros_meta_list.append(
                {
                    "id": running_macro.device_id,
                    "header": running_macro.macro_logger.get_value(ATTR_HEADER),
                }
            )
        return macros_meta_list

    @expose_method()
    def broadcast_macro_header(self):
        """
        This is just a patch function to support Onda.

        TODO: remove this function after Onda is properly communicating with Kamzik3
        """
        for running_macro in self.running_macros.values():
            attribute_object = running_macro.macro_logger[ATTR_HEADER]
            header = "{}.{}".format(attribute_object.attribute_id, VALUE)
            kamzik3.session.publisher.push_message(
                header, running_macro.macro_logger.get_value(ATTR_HEADER)
            )

    @expose_method({"macro_id": "ID of uploaded macro"})
    def get_macro_template(self, macro_id):
        try:
            return self.loaded_templates[self.running_macros.get(macro_id).template_id]
        except (AttributeError, TypeError) as e:
            pass
        try:
            return self.loaded_templates[self.uploaded_macros.get(macro_id).template_id]
        except (AttributeError, TypeError) as e:
            pass
        try:
            return self.loaded_templates[self.finished_macros.get(macro_id).template_id]
        except (AttributeError, TypeError) as e:
            error_message = "Could not get Template: {}".format(e)
            self.logger.error(error_message)
            raise DeviceError(error_message)

    @expose_method({"template_metadata": "YAML serialized template metadata"})
    def create_template(self, template_metadata):
        try:
            template_data = oyaml.load(template_metadata, Loader=yaml.Loader)
            file_path = os.path.join(
                self.get_value(ATTR_TEMPLATE_DIRECTORY),
                template_data["title"].replace(" ", "_") + ".stpl",
            )
        except (AttributeError, TypeError) as e:
            raise DeviceError("Template could not be created. {}".format(e))
        if file_path != "":
            with open(file_path, "w") as fp:
                fp.write(template_metadata)
                self.logger.info("New template {} saved.".format(file_path))
            self.read_scan_templates_directory()
            return file_path
        else:
            raise DeviceError("Cannot save template {}.".format(template_data["title"]))

    @expose_method({"template_id": "ID of template to be removed"})
    def remove_template(self, template_id):
        try:
            template, file_item = self.loaded_templates.get(template_id, None)
            os.remove(file_item)
        except (FileNotFoundError, OSError, TypeError) as e:
            error_message = "Template could not be removed: {}".format(e)
            self.logger.error(error_message)
            raise DeviceError(error_message)

        self.logger.info("Removing template {} at {}.".format(template_id, file_item))
        self.read_scan_templates_directory()

    @expose_method(
        {
            "template_id": "Name of macro template",
            "macro_data": "YAML serialized macro data",
        }
    )
    def upload_macro(self, template_id, macro_data):
        macro_id = "{}_{}".format(
            self.get_value(ATTR_MACRO_PREFIX), self.get_macro_count()
        )
        macro_data = re.sub(
            "^device_id:.*",
            "device_id: {}".format(macro_id),
            macro_data,
            flags=re.MULTILINE,
        )
        macro = yaml.load(macro_data, Loader=oyaml.Loader)
        if macro is None:
            raise DeviceError("Macro could not be uploaded")
        try:
            macro.template_id = template_id
        except (AttributeError, TypeError) as e:
            raise DeviceError("Macro could not be uploaded. {}".format(e))

        return self.add_macro(macro)

    def add_macro(self, macro):
        self.uploaded_macros[macro.device_id] = macro
        self.set_value(ATTR_UPLOADED_COUNT, self.get_value(ATTR_UPLOADED_COUNT) + 1)
        self.set_macro_log(macro.device_id)

        if len(self.finished_macros) > self.get_value(ATTR_MAX_MACRO_HISTORY):
            self.finished_macros.popitem(last=False)[1].remove()
            self.set_value(ATTR_FINISHED_COUNT, len(self.finished_macros))
        cb = lambda value, macro=macro: self.macro_status_update(value, macro)
        macro.attach_attribute_callback(ATTR_STATUS, cb, key_filter=VALUE)
        return macro.common_id

    @expose_method({"macro_id": "ID of uploaded macro"})
    def start_macro(self, macro_id):
        if self.get_value(ATTR_RUNNING_COUNT) >= self.get_value(
            ATTR_MAX_RUNNING_MACROS
        ):
            raise DeviceError("Maximum running macros count reached.")
        if macro_id not in self.uploaded_macros:
            raise DeviceError("Macro {} was not found on MacroServer".format(macro_id))
        macro = self.uploaded_macros.pop(macro_id)
        self.set_value(ATTR_UPLOADED_COUNT, len(self.uploaded_macros))

        if self.get_value(ATTR_AUTO_CONTROL_SHUTTER):
            for shutter in self.session.get_devices(class_filter="DeviceShutter"):
                shutter_device = self.session.get_device(shutter)
                if shutter_device.get_value(ATTR_AUTO_MODE):
                    shutter_device.open_shutter(clear_auto_mode=False)

        macro.start()

    @expose_method()
    def clear_uploaded_macros(self):
        for macro in list(self.uploaded_macros.values()):
            del self.uploaded_macros[macro.common_id]
            macro.remove()
        self.set_value(ATTR_UPLOADED_COUNT, len(self.uploaded_macros))

    @expose_method()
    def clear_finished_macros(self):
        for macro in list(self.finished_macros.values()):
            del self.finished_macros[macro.common_id]
            macro.remove()
        self.set_value(ATTR_FINISHED_COUNT, len(self.finished_macros))

    def macro_status_update(self, value, macro):
        with self.update_lock:
            if value in (STATUS_IDLE, STATUS_ERROR):
                if macro.common_id in self.running_macros:
                    del self.running_macros[macro.common_id]
                self.finished_macros[macro.common_id] = macro
                self.set_value(ATTR_RUNNING_COUNT, len(self.running_macros))
                self.set_value(ATTR_FINISHED_COUNT, len(self.finished_macros))

                if self.get_value(ATTR_AUTO_CONTROL_SHUTTER):
                    for shutter in self.session.get_devices(
                        class_filter="DeviceShutter"
                    ):
                        shutter_device = self.session.get_device(shutter)
                        if shutter_device.get_value(ATTR_AUTO_MODE):
                            shutter_device.close_shutter(clear_auto_mode=False)

                if value == STATUS_ERROR:
                    self.handle_command_error(
                        macro.common_id,
                        "{}: {}".format(
                            macro.common_id, macro.get_value(ATTR_LAST_ERROR)
                        ),
                    )
            elif value == STATUS_BUSY:
                self.running_macros[macro.common_id] = macro
                self.set_value(ATTR_UPLOADED_COUNT, len(self.uploaded_macros))
                self.set_value(ATTR_RUNNING_COUNT, len(self.running_macros))

    def set_macro_log(self, macro_id):
        macro = self.uploaded_macros.get(macro_id)
        output_file, macro_index = macro.setup_output_file(
            self.get_value(ATTR_OUTPUT_DIRECTORY), self.get_value(ATTR_MACRO_PREFIX)
        )
        current_template, _ = self.loaded_templates.get(macro.template_id, ({}, None))
        header_lines = [
            "Log version: {}".format("0.5"),
            "Session ID: {}".format(kamzik3.session.device_id),
            "Template: {}{}".format(
                self.get_value(ATTR_MACRO_PREFIX), macro.template_id
            ),
            "Prefix: {}".format(self.get_value(ATTR_MACRO_PREFIX)),
            "Index: {}".format(macro_index),
            "Comment: {}".format(macro.comment),
            "Output file: {}".format(output_file),
            "Points count: {}".format(macro.get_total_points_count()),
            "Repeat count: {}".format(macro.repeat_count),
            "Measurement groups: {}".format(
                current_template.get("measurement_groups", None)
            ),
            "-" * 32,
        ]
        header_lines += macro.get_output_header()
        # Check if attribute log is enabled for session
        if self.session.get_value(ATTR_ALLOW_ATTRIBUTE_LOG):
            attribute_logger = self.session.get_device("AttributeLogger")
            header = attribute_logger.get_value(ATTR_HEADER)[2:]
            sep = attribute_logger.separator
            log_line = attribute_logger.get_value(ATTR_LAST_LOG_LINE)
            now = datetime.now()
            # Add last logged attributes to the Scan header
            header_lines += [
                "Session logged attributes",
                header,
                sep.join(
                    [now.strftime("%Y-%m-%d %H:%M:%S"), str(time.time()), log_line]
                ),
                "-" * 32,
            ]
        # Set macro logger header
        macro.macro_logger.preset_header = (
            "\n".join("# {0}".format(s) for s in header_lines) + "\n"
        )

        # Get through all items in macro and set attributes to log for each macro step
        for index, chain_item in enumerate(macro.chain):
            if isinstance(chain_item, Scan):
                # It's Scan step
                log_attribute_name = chain_item.step_attributes.get(
                    "output", chain_item.step_attributes["attribute"]
                )
                for measurement_group in current_template.get("measurement_groups", []):
                    for device, attribute in kamzik3.session.measurement_groups[
                        measurement_group
                    ]:
                        macro.add_output_attribute(device, attribute)

                macro.add_output_attribute(
                    chain_item.step_attributes["device_id"], log_attribute_name
                )
            elif isinstance(chain_item, StepGenerator):
                # It's Step generator
                for measurement_group in current_template.get("measurement_groups", []):
                    for device, attribute in kamzik3.session.measurement_groups[
                        measurement_group
                    ]:
                        macro.add_output_attribute(device, attribute)

    def set_macro_prefix(self, value):
        """
        Set prefix for each new macro, which will be executed on macro-server.

        :param value:
        """
        self.set_raw_value(ATTR_MACRO_PREFIX, value)
        self.set_macro_log_directory("{}_logs".format(value))
        self.set_macro_templates_directory("{}_templates".format(value))
        self.get_macro_count()

    @expose_method()
    def get_macro_count(self):
        """
        Macro output directory for highest postfix which is our macro count number.

        :return: int
        """
        macro_prefix = self.get_value(ATTR_MACRO_PREFIX)
        output_directory_path = self.get_value(ATTR_OUTPUT_DIRECTORY)
        next_index = get_next_file_index(
            output_directory_path, re.compile("{}_(\d+)\.log".format(macro_prefix))
        )
        self.set_attribute([ATTR_MACRO_COUNT, VALUE], next_index)
        return next_index

    def set_macro_log_directory(self, value=None):
        """
        Set macro base log directory.

        All macro log files will go into this directory.

        :param value:
        """
        if value is not None:
            log_directory = kamzik3.session.get_value(ATTR_LOG_DIRECTORY)
            if log_directory is None:
                raise DeviceError(
                    "Cannot set macro log directory. Attribute 'Log directory' is not set."
                )
            log_directory = os.path.join(log_directory, value)
        else:
            log_directory = self.get_value(ATTR_OUTPUT_DIRECTORY)

        self.logger.info("Setting macro log directory to: {}".format(log_directory))
        if not os.path.exists(log_directory):
            self.logger.info(
                "Directory {} does not exists, trying to create it.".format(
                    log_directory
                )
            )
            os.makedirs(log_directory)

        self.set_value(ATTR_OUTPUT_DIRECTORY, log_directory)

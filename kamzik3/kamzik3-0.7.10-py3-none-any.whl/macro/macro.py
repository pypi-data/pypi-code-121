import logging
import os
import re
import time
from threading import Thread

import numpy as np

import kamzik3
from kamzik3 import DeviceError, units, MacroException
from kamzik3.constants import *
from kamzik3.devices.attributeLogger import AttributeLoggerTriggered
from kamzik3.devices.device import Device
from kamzik3.macro.common import Common
from kamzik3.macro.common import StepGenerator
from kamzik3.macro.scan import Scan
from kamzik3.macro.step import Step
from kamzik3.snippets.snippetDataAccess import get_next_file_index
from kamzik3.snippets.snippetsDecorators import expose_method
from kamzik3.snippets.snippetsUnits import seconds_to_datetime, get_scaled_time_duration


class Macro(Common, Device):
    current_point_index = 0
    template_id = None

    def __init__(
        self,
        device_id,
        chain=None,
        repeat_count=0,
        wait_after=units.Quantity(0, "s"),
        retry_count=0,
        trigger_log=True,
        comment=None,
        exception=ABORT,
    ):
        self.logger = logging.getLogger("Macro.{}".format(device_id))
        self.comment = comment
        self.chain = chain
        Common.__init__(
            self,
            device_id,
            repeat_count,
            wait_after,
            retry_count,
            trigger_log,
            exception,
        )
        Device.__init__(self, device_id)
        self.macro_logger = None
        if self.chain is None:
            self.chain = []
        self.branch = []
        self.index = -1
        self.macro_body_thread = None
        self.connect()

    def _init_attributes(self):
        super()._init_attributes()
        self.create_attribute(
            ATTR_STATE, default_value=IDLE, readonly=True, default_type=np.uint8
        )
        self.create_attribute(
            ATTR_POINTS_COUNT, default_value=1, readonly=True, default_type=np.uint64
        )
        self.create_attribute(
            ATTR_POINT_INDEX, default_value=0, readonly=True, default_type=np.uint64
        )
        self.create_attribute(
            ATTR_PROGRESS,
            default_value=0,
            readonly=True,
            default_type=np.float16,
            unit="%",
            min_value=0,
            max_value=100,
            decimals=2,
        )
        self.create_attribute(
            ATTR_CHAIN_LINK, default_value=0, readonly=True, default_type=np.uint64
        )
        self.create_attribute(ATTR_CHAIN_LINK_OUTPUT, default_value="", readonly=True)
        self.create_attribute(ATTR_RUNNING_TIME, default_value=0, readonly=True)
        self.create_attribute(ATTR_ESTIMATED_TIME, default_value=0, readonly=True)
        self.create_attribute(ATTR_ESTIMATED_END, default_value=0, readonly=True)
        self.create_attribute(ATTR_REMAINING_TIME, default_value=0, readonly=True)
        self.create_attribute(ATTR_STARTED_AT, default_value=None, readonly=True)
        self.create_attribute(ATTR_OUTPUT_FILENAME, default_value=None, readonly=True)
        self.set_value(ATTR_DESCRIPTION, self.comment)

    def handle_configuration(self):
        start_at = time.time()

        def _finish_configuration(*_, **__):
            self._config_commands()
            self._config_attributes()
            self.set_status(STATUS_CONFIGURED)
            self.recount_steps()
            self.logger.info(
                "Device configuration took {} sec.".format(time.time() - start_at)
            )

        _finish_configuration()

    def command(self, command, callback=None, with_token=False, returning=True):
        raise DeviceError("Device does not accept any commands.")

    def add(self, link):
        if isinstance(link, list):
            for link_item in link:
                self.add(link_item)
            return
        assert isinstance(link, Common)
        if isinstance(link, Macro):
            self.chain += link.chain
        else:
            self.chain.append(link)
        self.recount_steps()

    def next(self):
        self.index += 1
        if self.index < len(self.chain):
            return self.chain[self.index]
        else:
            return None

    def prev(self):
        self.index -= 1
        if self.index >= 0:
            return self.chain[self.index]
        else:
            return None

    def reset(self):
        self.index = -1
        self.set_point_index(0)
        super().reset()

    def resolve_links_scanner(self):
        new_chain = []
        for link in self.chain:
            if link.scanner is not None and not link.resolved:
                scanner = kamzik3.session.get_device(link.scanner)
                new_link = scanner.get_scanner_macro(
                    scanner_input=link,
                    scanner_attributes=link.scanner_attributes,
                    parent_macro=self,
                )
                if isinstance(link, Scan) and hasattr(new_link, "chain"):
                    new_chain += new_link.chain
                else:
                    new_chain.append(new_link)
                link.resolved = True
            else:
                new_chain.append(link)
        self.chain = new_chain
        self.recount_steps()

    def before_macro_starts(self):
        pass

    def before_macro_stops(self):
        pass

    @expose_method()
    def start(self, threaded=True):
        if self.get_state() == BUSY:
            raise DeviceError("Macro is already running")
        self.resolve_links_scanner()
        self.logger.log(
            logging.MACRO_STATE,
            "{} started\n```{}```".format(
                self.device_id, self.macro_logger.preset_header
            ),
        )
        super().start()
        if self.macro_logger is not None:
            self.macro_logger.start()

        self.set_point_index(0)
        self.set_value(ATTR_STARTED_AT, seconds_to_datetime(self.started_at))
        self.set_value(ATTR_ESTIMATED_END, seconds_to_datetime(self.started_at))
        self.current_point_index = 0
        self.index = -1
        self.before_macro_starts()
        if threaded:
            self.macro_body_thread = Thread(target=self.body, args=[self.macro_clean])
            self.macro_body_thread.start()
        else:
            self.body(callback=self.macro_clean)

    def body(self, callback=None):
        try:
            # Repeat following macro steps
            for _ in range(self.repeat_count + 1):
                # Reset all links in chain
                for link in self.chain:
                    link.reset()
                # Get first link
                link = self.next()
                # Reset branch to empty list
                self.branch = []
                # Stay in Macro loop until macro is BUSY
                while self.get_state() == BUSY:
                    # Link is empty
                    if link is None:
                        if self.branch:
                            if self.branch[-1] in self.chain:
                                link = self.prev()
                            else:
                                link = self.branch.pop()
                                self.index -= 1
                        else:
                            link = self.prev()
                        continue
                    # Link is done and repeated
                    elif (
                        link.get_state() == DONE and link.repeated == link.repeat_count
                    ):
                        link.reset()
                        link = self.prev()
                        if link is None:
                            if self.repeated == self.repeat_count:
                                self.done()
                            else:
                                self.repeated += 1
                                break
                        continue
                    # Deal with Step type of Link
                    elif isinstance(link, Step):
                        if link.get_state() == DONE:
                            link.repeat()
                        else:
                            try:
                                link.start()
                            except MacroException as retry_reason:
                                link.retry(retry_reason)
                                continue
                    # Deal with StepGenerator type of Link
                    elif isinstance(link, StepGenerator):
                        if link.as_step:
                            step = link.start()
                            link = step
                            continue
                        # Get step from step generator
                        if link.get_state() == DONE:
                            step = link.repeat()
                        elif self.get_state() != BUSY:
                            continue
                        else:
                            try:
                                step = link.start()
                            except MacroException as retry_reason:
                                link.retry(retry_reason)
                                continue
                        if step is None:
                            if self.branch:
                                if link.repeated == link.repeat_count:
                                    link = self.branch.pop()
                            else:
                                link = self.chain[self.index]
                        else:
                            if link not in self.branch:
                                self.branch.append(link)
                            link = step
                        continue

                    # Set link index of chain
                    self.set_value(ATTR_CHAIN_LINK, self.index)
                    # Set output of link
                    self.set_attribute(
                        (ATTR_CHAIN_LINK_OUTPUT, VALUE),
                        [self.current_point_index + 1, self.index, link.get_output()],
                    )
                    # Set warning flag
                    if (
                        link.warning_message is not None
                        and self.macro_logger is not None
                    ):
                        self.macro_logger.write_line(
                            "# {};WARNING;{}".format(time.time(), link.warning_message)
                        )
                    # Set point index of macro
                    self.set_point_index(self.current_point_index + 1)
                    # Write into log file if trigger_log is set and we have logger associated
                    if link.trigger_log and self.macro_logger is not None:
                        self.macro_logger.trigger()

                    if link.repeated == link.repeat_count:
                        link = self.next()

                if self.in_statuses(IDLE_DEVICE_STATUSES):
                    return

                self.start_timer()
        except MacroException as e:
            self.error(e)
            raise e
        finally:
            self.logger.log(logging.MACRO_STATE, "{} done".format(self.device_id))
            if callable(callback):
                callback()

    @expose_method()
    def stop(self):
        if self.in_statuses(IDLE_DEVICE_STATUSES):
            raise DeviceError("Macro is not running")

        self.before_macro_stops()
        self.logger.log(logging.MACRO_STATE, "{} stopped".format(self.device_id))
        super().stop()

        for link in self.chain + self.branch:
            link.stop()

    def macro_clean(self):
        for link in self.chain:
            if isinstance(link, StepGenerator):
                link.return_back_callback()
            link.on_macro_done()
        self.before_macro_stops()

    def recount_steps(self):
        sub_steps_count = 0
        sub_points_count = 0
        for link in reversed(self.chain):
            if isinstance(link, StepGenerator) and sub_steps_count > 0:
                repeat_step = link.step_attributes.get("repeat_count", 0) + 1
                repeat_scan = link.repeat_count + 1
                total_steps = link.steps_count * sub_steps_count
                sub_steps_count = total_steps * repeat_scan

                total_points = (link.steps_count + 1) * (repeat_step + sub_points_count)
                sub_points_count = total_points * repeat_scan
            else:
                sub_steps_count += link.get_total_steps_count()
                sub_points_count += link.get_total_points_count()

        total_count = sub_points_count * (self.repeat_count + 1)
        self.points_count = total_count
        self.set_value(ATTR_POINTS_COUNT, self.points_count)

    def get_total_steps_count(self):
        return len(self.chain)

    def get_total_points_count(self):
        return self.points_count

    @expose_method()
    def get_chain_link_output(self):
        chain_link_output = []
        for _, chain_item in enumerate(self.chain):
            if isinstance(chain_item, Scan):
                chain_link_output.append(
                    (
                        chain_item.step_attributes["device_id"],
                        chain_item.step_attributes["attribute"],
                        chain_item.points_count,
                    )
                )
            else:
                chain_link_output.append(None)
        return chain_link_output

    def set_state(self, new_state):
        super().set_state(new_state)

        self.set_value(ATTR_STATE, new_state)
        if new_state in (IDLE, DONE, STOPPED):
            self.set_status(STATUS_IDLE)
        elif new_state in (BUSY, PAUSED):
            self.set_status(STATUS_BUSY)
        elif new_state == ERROR:
            self.set_status(STATUS_ERROR)

        if self.macro_logger is not None and new_state in (
            DONE,
            ERROR,
            IDLE,
            DONE,
            STOPPED,
        ):
            self.macro_logger.stop()

    def set_point_index(self, point_index):
        self.current_point_index = point_index
        self.set_value(ATTR_POINT_INDEX, point_index)
        progress = (100.0 / self[ATTR_POINTS_COUNT][VALUE]) * point_index
        self.set_value(ATTR_PROGRESS, progress)

        running_time = time.time() - self.started_at
        try:
            estimated_time = (100 / progress) * running_time
        except ZeroDivisionError:
            estimated_time = 1
        remaining_time = estimated_time - running_time
        self.set_value(ATTR_RUNNING_TIME, get_scaled_time_duration(running_time))
        self.set_value(ATTR_REMAINING_TIME, get_scaled_time_duration(remaining_time))
        self.set_value(
            ATTR_ESTIMATED_END, seconds_to_datetime(time.time() + remaining_time)
        )
        self.set_value(ATTR_ESTIMATED_TIME, get_scaled_time_duration(estimated_time))

    def setup_output_file(self, output_directory_path, macro_prefix):
        if not os.path.exists(output_directory_path):
            self.logger.info(
                "Output directory {} does not exists, trying to create it.".format(
                    output_directory_path
                )
            )
            os.makedirs(output_directory_path)
        next_index = get_next_file_index(
            output_directory_path, re.compile(r"{}_(\d+)\.log".format(macro_prefix))
        )
        output_filename = os.path.join(
            output_directory_path, "{}_{}.log".format(macro_prefix, next_index)
        )
        self.set_value(ATTR_OUTPUT_FILENAME, output_filename)
        self.macro_logger = AttributeLoggerTriggered(
            output_filename,
            device_id="{}_Log_{}".format(macro_prefix, next_index),
            config={"rotating": False},
        )
        return output_filename, next_index

    def add_output_attribute(self, device_id, attribute):
        if self.macro_logger is None:
            raise DeviceError("Macro logger is not set")

        self.macro_logger.add_logged_attribute(device_id, attribute)

    def get_output_header(self):
        lines = []
        for link in self.chain:
            lines += link.get_output_header()
            lines += ["-" * 32]
        return lines

    def disconnect(self):
        if self.chain is not None:
            for chain in self.chain:
                chain.remove()

        if self.macro_logger is not None:
            self.macro_logger.remove()

        return Device.disconnect(self)

    def remove(self):
        for step in self.chain:
            step.remove()
        Device.remove(self)
        self.macro_logger = None
        self.chain = None
        Common.remove(self)

    def error(self, error_message):
        error_message = str(error_message)
        self.error_at = time.time()
        self.running_time = self.error_at - self.started_at
        self.error_message = error_message
        self.set_value(ATTR_LAST_ERROR, error_message)
        self.logger.error(error_message)
        self.handle_command_error(self.common_id, error_message)
        self.set_state(ERROR)

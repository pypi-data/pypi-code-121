import logging
import time
from threading import Event

from kamzik3 import units, MacroException
from kamzik3.constants import *
from kamzik3.snippets.snippetsTimer import RecallableTimer
from kamzik3.snippets.snippetsYaml import YamlSerializable


class Common(YamlSerializable):
    state = IDLE
    repeated = 0
    error_message = None
    warning_message = None
    previous_running_time = 0
    running_time = 0
    started_at = 0
    done_at = 0
    stopped_at = 0
    reset_at = 0
    error_at = 0
    warning_at = 0
    steps_count = 0
    points_count = 1
    retry_timeout = 100  # 100 ms
    common_id = None
    logger = None
    resolved = False

    def __init__(
        self,
        common_id,
        repeat_count=0,
        wait_after=units.Quantity(0, "s"),
        retry_count=0,
        trigger_log=True,
        on_warning=ABORT,
        timeout=units.Quantity(0, "s"),
        scanner=None,
        scanner_attributes=None,
    ):
        assert repeat_count >= 0, "Repeat parameter should be >= 0"
        assert retry_count >= 0, "Retry parameter should be >= 0"
        assert wait_after >= 0, "Wait_after parameter should be >= 0"
        self.set_common_id(common_id)
        self.max_retry_count = retry_count
        self.retry_count = retry_count
        self.on_warning = on_warning
        self.wait_after = wait_after.to("s")
        self.trigger_log = trigger_log
        self.timeout = timeout.to("s")
        self.scanner = scanner
        self.scanner_attributes = scanner_attributes

        self.timer = None
        if self.wait_after > 0:
            self.timer = Event()
        self.timeout_timer = None
        if self.timeout > 0:
            self.timeout_timer = RecallableTimer(self.timeout.m, self.step_timeout)

        self.repeat_count = int(repeat_count)

    def set_common_id(self, common_id):
        self.common_id = common_id
        if not hasattr(self, "logger") or self.logger is None:
            self.logger = logging.getLogger("Macro.common.{}".format(self.common_id))

    def set_state(self, new_state):
        self.state = new_state

    def get_state(self):
        return self.state

    def step_timeout(self):
        self.warning("Step timeout")

    def reset(self):
        self.logger.debug("Reset")
        self.reset_at = time.time()
        self.error_message = None
        self.warning_message = None
        self.repeated = 0
        self.retry_count = self.max_retry_count
        self.set_state(IDLE)

    def start(self):
        self.logger.debug("Started")
        self.started_at = time.time()
        self.running_time = 0
        self.set_state(BUSY)
        if self.timeout_timer is not None:
            self.timeout_timer.start()

    def repeat(self):
        self.logger.debug("Repeated")
        self.started_at = time.time()
        self.running_time = 0
        self.repeated += 1
        self.set_state(BUSY)
        if self.timeout_timer is not None:
            self.timeout_timer.start()

    def retry(self, retry_reason):
        if self.retry_count == 0:
            raise retry_reason
        else:
            self.retry_count -= 1
            self.logger.error(
                "Retrying step due to error. Remaining tries {}. Error message: {}".format(
                    self.retry_count, retry_reason
                )
            )
            self.reset_at = time.time()
            self.error_message = None
            self.warning_message = None
            time.sleep(self.retry_timeout / 1e3)

    def stop(self):
        self.stopped_at = time.time()
        self.running_time = self.stopped_at - self.started_at
        if self.timer is not None:
            self.stop_timer()
        if self.timeout_timer is not None:
            self.timeout_timer.cancel()
        if self.logger:
            self.logger.debug("Stopped")
        self.set_state(STOPPED)

    def done(self):
        self.done_at = time.time()
        self.previous_running_time = self.running_time = self.done_at - self.started_at
        if self.logger:
            self.logger.debug("Done")
        if self.timeout_timer is not None:
            self.timeout_timer.cancel()
        self.set_state(DONE)

    def error(self, error_message):
        self.error_at = time.time()
        self.running_time = self.error_at - self.started_at
        self.error_message = error_message
        self.logger.error(error_message)
        self.set_state(ERROR)

    def warning(self, warning_message):
        self.warning_at = time.time()
        self.running_time = self.warning_at - self.started_at
        self.warning_message = warning_message
        self.logger.debug(warning_message)
        if self.timer is not None:
            self.stop_timer()
        self.set_state(WARNING)

    def stop_timer(self):
        if self.timer is not None:
            self.logger.debug("Timer for {}s stopped".format(self.wait_after))
            self.timer.set()
            return True
        return False

    def start_timer(self):
        if self.timer is not None:
            self.logger.debug("Waiting for {}s".format(self.wait_after))
            self.timer.clear()
            self.timer.wait(self.wait_after.m)
            return True
        return False

    def get_total_steps_count(self):
        return self.steps_count * (self.repeat_count + 1)

    def remove(self):
        self.logger = None

    def get_reset_step(self):
        return None

    def get_output(self):
        return None

    def on_macro_done(self):
        return None


class StepGenerator(Common):
    as_step = False
    step_index = 0
    first_step_at = 0

    def return_back_callback(self):
        raise NotImplementedError()

    def step_generator(self):
        raise NotImplementedError()

    def reset(self):
        self.steps = self.step_generator()
        Common.reset(self)

    def repeat(self):
        Common.repeat(self)
        self.steps = self.step_generator()
        return self.start()

    def stop(self):
        self.started_at = self.first_step_at
        if self.current_step is not None:
            self.current_step.stop()
        Common.stop(self)

    def done(self):
        self.started_at = self.first_step_at
        Common.done(self)

    def error(self, error_message):
        self.started_at = self.first_step_at
        Common.error(self, error_message)

    def before_first_step_executed(self):
        pass

    def before_step_executed(self):
        pass

    def start(self):
        Common.start(self)
        try:
            if self.current_step is not None:
                self.current_step.remove()
            else:
                self.before_first_step_executed()
            self.current_step = next(self.steps)
            self.before_step_executed()
            return self.current_step
        except StopIteration:
            self.done()
            return None
        except MacroException as e:
            self.error(e)
            raise e

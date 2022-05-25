from django.utils.timezone import now

from security.enums import LoggerName
from security.logging.common import SecurityLogger
from security.backends.signals import (
    command_started, command_output_updated, command_finished, command_error,
)


class CommandLogger(SecurityLogger):

    logger_name = LoggerName.COMMAND

    def __init__(self, name=None, input=None, is_executed_from_command_line=None, output=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.input = input
        self.is_executed_from_command_line = is_executed_from_command_line
        self.output = output

    def log_started(self, name, input, is_executed_from_command_line):
        self.start = now()
        self.name = name
        self.input = input
        self.is_executed_from_command_line = is_executed_from_command_line
        command_started.send(sender=CommandLogger, logger=self)

    def log_finished(self):
        self.stop = now()
        command_finished.send(sender=CommandLogger, logger=self)

    def log_output_updated(self, output):
        self.output = output
        command_output_updated.send(sender=CommandLogger, logger=self)

    def log_exception(self, ex_tb):
        self.stop = now()
        self.error_message = ex_tb,
        command_error.send(sender=CommandLogger, logger=self)

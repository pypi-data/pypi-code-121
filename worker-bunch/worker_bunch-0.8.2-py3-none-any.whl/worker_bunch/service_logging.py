import logging
import os
import sys
import logging.handlers


class LoggingConfKey:
    """Predefined keys to be reused in inherited worker classes (section: "worker_settings"). goal: consistent naming"""
    FILE = "file"
    LEVEL = "level"
    MAX_BYTES = "max_bytes"
    MAX_COUNT = "max_count"

    PRINT_CONSOLE = "print_console"
    SKIP_TIMES = "skip_times"

    MODULES_LEVELS = "module_levels"


LOGGING_DEFAULT_LOG_LEVEL = "info"
LOGGING_CHOICES = ["debug", "info", "warning", "error"]


LOGGING_JSONSCHEMA = {
    "type": "object",
    "properties": {
        LoggingConfKey.FILE: {"type": "string", "minLength": 3, "description": "Log file (path)"},
        LoggingConfKey.LEVEL: {"type": "string", "enum": LOGGING_CHOICES, "description": "Log level"},
        LoggingConfKey.MAX_BYTES: {"type": "integer", "minimum": 102400, "description": "Max bytes per log files."},
        LoggingConfKey.MAX_COUNT: {"type": "integer", "minimum": 1, "description": "Max count of rolled log files."},
        LoggingConfKey.PRINT_CONSOLE: {"type": "boolean", "description": "Print logs to console too."},
        LoggingConfKey.SKIP_TIMES: {"type": "boolean", "description": "Skip timestamps in log output and prints to console."},

        LoggingConfKey.MODULES_LEVELS: {
            "type": "object",
            "additionalProperties": {"type": "string", "enum": LOGGING_CHOICES},
            "description": "Dictionary of <module name as shown in log>:<log level>"
        }
    },
    "additionalProperties": False,
}


# noinspection SpellCheckingInspection
class ServiceLogging:

    @classmethod
    def configure(cls, config, file_cli, level_cli, print_console_cli, skip_times_cli):
        handlers = []

        if not file_cli:
            file_cli = config.get(LoggingConfKey.FILE)

        if not level_cli:
            level_cli = config.get(LoggingConfKey.LEVEL)
        level_cli = cls.parse_log_level(level_cli)

        if not print_console_cli:
            print_console_cli = config.get(LoggingConfKey.PRINT_CONSOLE, False)
        if not skip_times_cli:
            skip_times_cli = config.get(LoggingConfKey.SKIP_TIMES, False)

        format_with_ts = '%(asctime)s [%(levelname)8s] %(name)s: %(message)s'
        format_no_ts = '[%(levelname)8s] %(name)s: %(message)s'

        if file_cli:
            log_dir = os.path.dirname(file_cli)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

            max_bytes = config.get(LoggingConfKey.MAX_BYTES, 1048576)
            max_count = config.get(LoggingConfKey.MAX_COUNT, 5)
            handler = logging.handlers.RotatingFileHandler(
                file_cli,
                maxBytes=int(max_bytes),
                backupCount=int(max_count)
            )
            formatter = logging.Formatter(format_with_ts)
            handler.setFormatter(formatter)
            handlers.append(handler)

        if skip_times_cli:
            log_format = format_no_ts
        else:
            log_format = format_with_ts

        if print_console_cli or skip_times_cli:
            handlers.append(logging.StreamHandler(sys.stdout))

        logging.basicConfig(
            format=log_format,
            level=level_cli,
            handlers=handlers
        )

        module_levels = config.get(LoggingConfKey.MODULES_LEVELS, {})
        for logger_name, log_level in module_levels.items():
            log_level = cls.parse_log_level(log_level)
            logger = logging.getLogger(logger_name)
            logger.setLevel(log_level)

    @classmethod
    def parse_log_level(cls, value):
        value = value or LOGGING_DEFAULT_LOG_LEVEL

        if not isinstance(value, type(logging.INFO)):
            input_value = str(value).lower().strip() if value is not None else value
            if input_value == "debug":
                value = logging.DEBUG
            elif input_value == "info":
                value = logging.INFO
            elif input_value == "warning":
                value = logging.WARNING
            elif input_value == "error":
                value = logging.ERROR
            else:
                value = logging.INFO

        return value

    @classmethod
    def get_log_name(cls, instance_class, instance_name):
        class_name = instance_class.__class__.__name__

        # logname ist used for config handling, which ist all lower case
        if instance_name:
            instance_name = instance_name.lower()

        if instance_name and instance_name != class_name.lower() and instance_name != class_name.lower():
            log_name = f"{instance_class.__class__.__name__}({instance_name})"
        else:
            log_name = class_name
        return log_name

    @classmethod
    def get_full_log_name(cls, instance_class, instance_name):
        class_path = instance_class.__module__
        class_name = instance_class.__class__.__name__
        class_full = "{}.{}".format(class_path, class_name)

        # logname ist used for config handling, which ist all lower case
        if instance_name:
            instance_name = instance_name.lower()

        if instance_name and instance_name != class_name.lower() and instance_name != class_full.lower():
            log_name = f"{class_path}.{instance_class.__class__.__name__}({instance_name})"
        else:
            log_name = class_full
        return log_name

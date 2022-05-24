import os, datetime, inspect, sys, re, traceback, uuid, time, logging
from logging.handlers import TimedRotatingFileHandler

import platform

from numpy.core.numeric import full

PLATFORM = platform.system().lower()

from . import _colorations, _utils

from concurrent_log_handler import ConcurrentRotatingFileHandler

PROCESSES = {}
TIMINGS = []

base_time = datetime.datetime.now()

DEFAULT_FORMAT = "{$date} - {$level:7} - {$pid:5} - {$file:>15}.{$line:<4} - {$name:<14}: $message" # %(processName)s %(filename)s:%(lineno)s
DEFAUT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
class NoParsingFilter(logging.Filter):
    def __init__(self, name="", excludes={}, level=None):
        super().__init__(name)
        self.excludes = excludes
        self.level = level

    def filter(self, record):
        message = record.getMessage()

        for key, patterns in self.excludes.items():
            if self.level.upper() == key.upper() or key.upper() == "ALL":
                for pattern in patterns:
                    if len(re.findall(pattern, message)):
                        return False
        return True

class AlphaLogger:
    error_logger = None
    monitoring_logger = None

    def to_json(self):
        keys = ["level", "database_name", "excludes", "date_format","format_log", "date_str","root","pid","name","monitor"]
        return {x:self.__dict__[x] for x in keys if x in self.__dict__}

    def __init__(
        self,
        name: str,
        filename: str = None,
        root: str = None,
        cmd_output: bool = True,
        level: str = "INFO",
        format_log:str = DEFAULT_FORMAT,
        date_format:str = DEFAUT_DATE_FORMAT,
        colors=None,
        database=None,
        excludes=None,
        replaces=None,
        config={}
    ):
        self.date_str: str = ""
        self.database_name: str = database
        self.database = None
        self.excludes = excludes
        self.replaces = replaces
        self.config = config
        self.format_log = format_log
        self.date_format = date_format

        if "ALPHA_LOG_CMD_OUTPUT" in os.environ:
            cmd_output = "Y" in os.environ["ALPHA_LOG_CMD_OUTPUT"].upper()

        if filename is None:
            filename = name
        if root is None:
            """
            parentframe     = inspect.stack()[1]
            module          = inspect.getmodule(parentframe[0])
            root            = os.path.abspath(module.__file__).replace(module.__file__,'')"""
            root = _utils.get_alpha_logs_root()

        self.root = _utils.check_root(root)
        log_path = self.root + os.sep + filename + ".log"

        # Create logger
        self.logger = logging.getLogger(name)
        self.set_level(level)

        # File handler
        if config is not None and "timed" in config:
            if config is not None and len(config) != 0:
                handler = TimedRotatingFileHandler(
                    log_path, **config
                )
            else:
                handler = TimedRotatingFileHandler(
                    log_path, when="midnight", interval=1, backupCount=90
                )
        else:
            defaults = {"mode":"a","maxBytes":512 * 1024,"backupCount":10,
            "encoding":None, "debug":None, "delay":None, "use_gzip":None,
            "owner":None, "chmod":None, "umask":None, "newline":None, "terminator":None,
            "unicode_error_policy":None}
            config = {} if config is None else {x:y for x,y in config.items() if x in defaults}
            for x,y in defaults.items():
                if not x in config and y is not None:
                    config[x] = y
            handler = ConcurrentRotatingFileHandler(log_path, **config)

        # handler.suffix  = "%Y%m%d"

        self.logger.addHandler(handler)

        if cmd_output:
            handler = logging.StreamHandler(sys.stdout)
            if colors:
                handler.addFilter(_colorations.ColorFilter(colors))
            self.logger.addHandler(handler)

        if self.excludes and len(self.excludes):
            self.logger.addFilter(
                NoParsingFilter(excludes=self.excludes, level=self.level)
            )

        self.pid = os.getpid()
        self.name = name
        # self.cmd_output     = cmd_output if cmd_output is not None else True

        self.last_level = None
        self.last_message = None

    def _log(
        self,
        message: str,
        stack,
        stack_level: int,
        level: str = "INFO",
        monitor: str = None,
        save=False,
        ex: Exception = None,
    ):
        """
                frame       = inspect.stack()[1]
        module      = inspect.getmodule(frame[0])
        origin      = "Unknowned"
        if module is not None:
            origin  = os.path.basename(module.__file__)
        """
        if message is None and ex is not None:
            message = "Exception"
        if monitor:
            save = True

        if isinstance(message, Exception):
            message = traceback.format_exc()

        self.set_current_date()

        full_message = self.get_formatted_message(message, stack, stack_level, level)

        if self.replaces is not None and type(self.replaces) == dict:
            for regex, replacement in self.replaces.items():
                matchs = re.findall(regex,full_message)
                if len(matchs) != 0:
                    for match in matchs:
                        full_message = full_message.replace(match, replacement)

        if ex is not None:
            full_message += str(ex) + "\n" + traceback.format_exc()

        fct = getattr(self.logger, level.lower())
        fct(full_message)

        if monitor is not None and self.monitoring_logger is not None:
            fct_monitor = getattr(self.monitoring_logger, level.lower())
            fct_monitor(
                message=full_message.replace(message, f"[{monitor}] {message}")
            )

        self.last_level = level.upper()
        self.last_message = message

        if level.lower() in ["critical", "error", "warning"] and self.error_logger is not None and self.name != "error":
            fct_errors = getattr(self.error_logger, level.lower())
            fct_errors(full_message)

        """if len(TIMINGS) > TIMINGS_LIMIT:
            TIMINGS = TIMINGS[:TIMINGS_LIMIT]
        TIMINGS.insert(0,{
            "elasped": datetime.datetime.now() - base_time
        })
        base_time = datetime.datetime.now()"""

        if save:
            type_ = "exception" if ex is not None else "message"
            self.__log_in_db(full_message, origin="alpha", level=level, type_=type_)

    def set_level(self, level="INFO"):
        level = "INFO" if level is None else level
        self.level: str = level.upper()
        level_show = _utils.get_level(level)
        self.logger.setLevel(level_show)

    def get_formatted_message(self, message, stack, stack_level: int, level):
        msg = self.format_log

        parameters = re.findall("\{\$([a-zA-Z0-9]*):?[0-9<>]*\}", msg)

        parameters_values = []

        if stack_level >= len(stack):
            stack_level = len(stack) - 1
        caller = inspect.getframeinfo(stack[stack_level][0])

        structure = "$%s"
        keys = {
            "date": self.date_str,
            "pid": self.pid,
            "level": level.upper(),
            "name": self.name,
            "path": caller.filename,
            "file": caller.filename.split(os.sep)[-1].replace(".py", ""),
            "line": caller.lineno,
        }

        for parameter_name in parameters:
            if parameter_name in keys:
                msg = msg.replace(structure % parameter_name, "")
                parameters_values.append(keys[parameter_name])

        msg = msg.format(*parameters_values).replace(
            structure % "message", str(message)
        )
        return msg

    def info(
        self, message=None, monitor=None, level=1, save=False, ex: Exception = None
    ):
        self._log(
            message,
            stack=inspect.stack(),
            stack_level=level,
            level="info",
            monitor=monitor,
            save=save,
            ex=ex,
        )

    def warning(
        self, message=None, monitor=None, level=1, save=False, ex: Exception = None
    ):
        self._log(
            message,
            stack=inspect.stack(),
            stack_level=level,
            level="warning",
            monitor=monitor,
            save=save,
            ex=ex,
        )

    def error(
        self, message=None, monitor=None, level=1, save=False, ex: Exception = None
    ):
        self._log(
            message,
            stack=inspect.stack(),
            stack_level=level,
            level="error",
            monitor=monitor,
            save=save,
            ex=ex,
        )

    def debug(
        self, message=None, monitor=None, level=1, save=False, ex: Exception = None
    ):
        self._log(
            message,
            stack=inspect.stack(),
            stack_level=level,
            level="debug",
            monitor=monitor,
            save=save,
            ex=ex,
        )

    def critical(
        self, message=None, monitor=None, level=1, save=False, ex: Exception = None
    ):
        self._log(
            message,
            stack=inspect.stack(),
            stack_level=level,
            level="critical",
            monitor=monitor,
            save=save,
            ex=ex,
        )

    def set_current_date(self):
        current_date = datetime.datetime.now()
        self.date_str = current_date.strftime(self.date_format)

    def process_start(self, name, parameters):
        uuid_process = str(uuid.uuid4())
        PROCESSES[uuid_process] = {
            "uuid": uuid,
            "name": name,
            "parameters": parameters,
            "datetime": datetime.datetime.now(),
        }
        self.process_log(uuid_process, name, parameters, "START")
        return uuid_process

    def process_end(self, uuid_process, name, parameters, error=None):
        PROCESS_INFOS = None
        if uuid_process in PROCESSES:
            PROCESS_INFOS = PROCESSES[uuid_process]

        status = "INFOS"
        if PROCESS_INFOS is not None:
            if name != PROCESS_INFOS["name"]:
                status = "NAME"
            elif parameters != PROCESS_INFOS["parameters"]:
                status = "PARAM"
            name = PROCESS_INFOS["name"]
            parameters = PROCESS_INFOS["parameters"]
            status = "END"

        if error is not None:
            status = str(error)

        if uuid_process is not None:
            self.process_log(uuid_process, name, parameters, status)

    def trace_show(self):
        traceback.print_exc()

    def __log_in_db(self, message, origin="unspecified", type_="unspecified", level=None):
        from ...models.database.main_definitions import Logs

        # Connect to db
        stackraw = traceback.format_stack()
        stack = "".join(stackraw) if stackraw is not None else ""

        if self.database is not None:
            self.database.insert(
                Logs,
                values={
                    Logs.type_: type_,
                    Logs.origin: origin,
                    Logs.message: message,
                    Logs.stack: stack,
                },
            )

    def print_error(self, error_msg, raise_exception=True):
        """Display the last error catched"""
        if str(error_msg)[:3] == "-W-":
            print("#-# WARNING #-#: " + str(error_msg)[3:])
        else:
            error_msg = "#-# ERROR #-#: " + str(error_msg)
            error_msg += " -----> " + str(sys.exc_info()[0])
            self.error(error_msg)
            if raise_exception == True:
                raise Exception(0, "#-# ERROR #-#")

    def process_log(self, uuid_process, name, parameters, status):
        from ...models.database.main_definitions import Processes

        if type(parameters) != str:
            parameters = ";".join([str(x) for x in parameters])

        if self.database is not None:
            self.database.insert(
                Processes,
                values={
                    Processes.uuid: uuid_process,
                    Processes.name: name,
                    Processes.parameters: parameters,
                    Processes.status: status,
                },
            )

"""
@singleton
class AlphaLogManager:
    loggers: {AlphaLogger}  = {}

    def is_logger(self,name):
        return name in self.loggers
    
    def get_logger(self,name):
        if self.is_logger(name):
            return self.loggers[name]
        return None

    def set_logger(self,name,logger):
        self.loggers[name] = logger

log_manager = AlphaLogManager()"""

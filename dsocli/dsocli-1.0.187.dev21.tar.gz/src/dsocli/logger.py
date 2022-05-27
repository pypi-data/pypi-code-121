import logging
import coloredlogs
from .settings import *


FATAL = 0 ### logs only fatal errors (not handled)
ERROR = 1 ### logs only errors
WARNING = 2 ### logs also warnings
INFO = 3 ### logs also information
DETAIL = 4 ### logs also detailed information
DEBUG = 5 ### logs also debug information
EXCEPTION = 6 ### logs also unhandled exceptions
PACKAGE = 7 ### also sets built-in logger level to logging.INFO
FULL = 8 ### also sets built-in logger level to logging.DEBUG


FIELD_STYLES = dict(
    asctime=dict(color='green', faint=True, bold=BOLD_LOGS),
    levelname=dict(color='magenta', faint=True, bold=BOLD_LOGS),
)

LEVEL_STYLES = dict(
    fatal=dict(color='red', bold=BOLD_LOGS),
    error=dict(color='red', bold=BOLD_LOGS),
    warning=dict(color='yellow', bold=BOLD_LOGS),
    info=dict(color='white', bold=BOLD_LOGS),
    detail=dict(color='white', faint=True, bold=BOLD_LOGS),
    debug=dict(color='cyan', faint=True, bold=BOLD_LOGS),
)

### to control logging verbosity of external libraries
verbosity_map = {
    FATAL : logging.FATAL,
    ERROR : logging.ERROR,
    WARNING : logging.WARNING,
    INFO : logging.WARNING,
    DETAIL : logging.WARNING,
    DEBUG : logging.WARNING,
    EXCEPTION : logging.WARNING,
    PACKAGE : logging.INFO,
    FULL : logging.DEBUG,
}

level_name_map = {
    'FATAL': FATAL,
    'ERROR': ERROR,
    'WARNING': WARNING,
    'INFO': INFO,
    'DETAIL': DETAIL,
    'DEBUG': DEBUG,
    'EXCEPTION': EXCEPTION,
    'PACKAGE': PACKAGE,
    'FULL': FULL,
}

def get_user_data_dir(appname):
    from pathlib import Path
    import os
    if WIN_PLATFORM:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        )
        dir_,_ = winreg.QueryValueEx(key, "Local AppData")
        result = Path(dir_).resolve(strict=False)
    elif MAC_PLATFORM:
        result = Path('~/Library/Application Support/').expanduser()
    elif NIX_PLATFORM:
        result = Path(os.getenv('XDG_DATA_HOME', "~/.local/share")).expanduser()
    else:
        raise NotImplementedError
    os.makedirs(result.joinpath(appname, 'logs'), exist_ok=True)
    return result.joinpath(appname, 'logs')


def get_log_file_name():
    from datetime import datetime
    filename = datetime.now().strftime('%Y-%m-%d.log')
    return os.path.join(get_user_data_dir('dso'), filename) 


class LoggerWrapperClass():

    # logging.addLevelName(DETAIL, 'DETAIL')
    def __detail(self, message, *args, **kws):
        if self.isEnabledFor(DETAIL):
            # Yes, logger takes its '*args' as 'args'.
            self._log(DETAIL, message, args, **kws) 
    # logging.Logger.detail = self.__detail

    def get_log_format(self):
        log_format = ''
        if TIMESTAMP_LOGS: log_format += '%(asctime)s'
        if LABEL_LOG_LEVELS: log_format += ' [%(levelname)-5s]'
        log_format += ' %(message)s'
        return log_format

    def __init__(self, level):
        self.level = level
        logging.basicConfig(format=self.get_log_format(), datefmt=LOG_TIME_FORMAT, level=self.mapped_level, force=True)
        ### rename critical to fatal
        logging.addLevelName(logging.CRITICAL, 'FATAL')
        ### rename WARNING to WARN
        logging.addLevelName(logging.WARNING, 'WARN')
        ### add new level DETAIL 
        logging.addLevelName(level_name_map['DETAIL'], 'DETAIL')
        ### set formats and root level, and force recreate any exisitng handler

        self.logger = logging.getLogger('dso')
       
        ### set level of the logger to DEBUG to catch all
        self.logger.setLevel(logging.DEBUG)
        self.logger.detail = self.__detail

        #### Add file handler to capture all logs, regardless of verbosity level
        fh = logging.FileHandler(get_log_file_name())
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(self.get_log_format(), LOG_TIME_FORMAT))
        self.logger.addHandler(fh)
        ### also add it to the root to capture messages from other libraries as well
        self.logger.root.addHandler(fh)

        #### Add console handler
        if COLORED_LOGS:
            ### set level always to maximum (as the level is controlled by mapped_level), and attach it to root logger
            coloredlogs.install(logger=logging.root, 
                                level='DEBUG',
                                fmt=self.get_log_format(),
                                level_styles=LEVEL_STYLES,
                                field_styles=FIELD_STYLES,
                                )
        else:
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(logging.Formatter(self.get_log_format(), LOG_TIME_FORMAT))
            self.logger.addHandler(ch)
            ### also add it to the root to capture messages from other libraries as well
            self.logger.root.addHandler(ch)


    ### maps dso log verbosity to internal verbosity
    def _map_level(self, level):
        return verbosity_map[level]

    @property
    def mapped_level(self):
        return self._map_level(self.level)

    def set_verbosity(self,level):
        self.level = level
        logging.root.setLevel(self.mapped_level)
        # for handler in self.logger.handlers:
        #     if isinstance(handler, type(logging.StreamHandler())):
        #         handler.setLevel(self.mapped_level)

    def increase_verbosity(self):
        changed = self.level < FULL
        if changed:
            self.set_verbosity(self.level + 1)
        return changed

    def decrease_verbosity(self):
        changed = self.level > FATAL
        if changed:
            self.set_verbosity(self.level - 1)
        return changed

    def fatal(self, msg, force=True):
        self.logger.propagate = force or self.level >= FATAL
        self.logger.fatal(msg)

    def error(self, msg, force=True):
        self.logger.propagate = force or self.level >= ERROR
        self.logger.error(msg)

    def warn(self, msg, force=False):
        self.logger.propagate = force or self.level >= WARNING
        self.logger.warning(msg)

    def info(self, msg, force=False):
        self.logger.propagate = force or self.level >= INFO
        self.logger.info(msg)

    ### FIXME
    def detail(self, msg, force=False):
        self.logger.propagate = force or self.level >= DETAIL
        # self.logger.log(DETAIL, msg)
        # self.logger.log(logging.INFO, msg)
        self.logger.detail(self.logger, msg)

    def debug(self, msg, force=False):
        self.logger.propagate = force or self.level >= DEBUG
        self.logger.debug(msg)

Logger = LoggerWrapperClass(level_name_map[DEFAULT_LOG_LEVEL])


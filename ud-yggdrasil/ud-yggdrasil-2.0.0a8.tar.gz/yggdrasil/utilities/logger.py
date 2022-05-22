import logging


class CustomFormatter(logging.Formatter):
    """
    Custom logging formatter:
    - Info messages are shown in cyan
    - Debug messages are shown in white
    - Warning messages are shown in yellow
    - Error messages are shown in red
    - Critical messages are shown in white & red background
    Each message shows time, name of the module, criticality leven and line number.
    """
    grey = "\x1b[0;37m"
    cyan = "\x1b[0;36m"
    yellow = "\x1b[0;33m"
    red = "\x1b[1;31m"
    bold_red = "\x1b[41m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: cyan + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

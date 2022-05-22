import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from .platform import get_log_folder

logger = logging.getLogger('online-choir')


class StreamToLogger:
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, output_logger, level=logging.DEBUG):
        self.logger = output_logger
        self.log_level = level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass


def setup_logging(log_level, log_file=None, capture_stderr=True):
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(threadName)s:%(message)s')
    logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    if log_file:
        logger.info(f"Logging output to {log_file}")
        file_handler = RotatingFileHandler(log_file, maxBytes=10 * 2**20, backupCount=5)
        file_handler.setFormatter(formatter)
        logging.root.addHandler(file_handler)

        if capture_stderr:
            # send stderr to logger (only if writing to a file)
            stderr_logger = logging.getLogger('STDERR')
            sl = StreamToLogger(stderr_logger, logging.ERROR)
            sys.stderr = sl


def parse_args_and_set_logger(parser, program: Optional[str] = None):
    parser.add_argument('--log-level', choices=('DEBUG', 'INFO', 'WARNING', 'ERROR'), default='INFO')
    parser.add_argument('--log-file')
    parser.add_argument('--console', action="store_true", help="Do not redirect stderr to log file")
    parsed_args = parser.parse_args()
    log_file = parsed_args.log_file
    if log_file is None and program:
        # enable logging in default location
        if parsed_args.console:
            log_file = f"{program}.log"
        else:
            log_file = get_log_folder() / f"{program}.log"
    setup_logging(parsed_args.log_level, log_file, not parsed_args.console)
    return parsed_args

from logging.handlers import TimedRotatingFileHandler
from logging import Formatter
import logging


class Log:

    def __init__(self):

        # get named logger
        self.logger = logging.getLogger(__name__)

        # create handler
        handler = TimedRotatingFileHandler(
            filename='log.log', when='D', interval=1, backupCount=10, encoding='utf-8', delay=False)

        # create formatter and add to handler
        formatter = Formatter(
            fmt='%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # add the handler to named logger
        self.logger.addHandler(handler)

        # set the logging level
        self.logger.setLevel(logging.INFO)

        # --------------------------------------

        # log something

    def log(self, message):

        print(f'{message}')
        self.logger.info(message)

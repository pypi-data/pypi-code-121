import logging


class Logger:
    @staticmethod
    def get_logger(caller_class_name):
        logger = logging.getLogger(caller_class_name)
        logging.basicConfig(
            format="%(name)s %(levelname)s: %(asctime)s %(message)s",
            datefmt="%d/%m/%Y %I:%M:%S %p",
        )
        return logger

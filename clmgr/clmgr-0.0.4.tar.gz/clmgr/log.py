"""Log functions"""
import logging


def setup_custom_logger(name: str):
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)8s] - %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger
